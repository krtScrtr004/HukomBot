// eslint-disable-next-line react-refresh/only-export-components
import {
	createContext,
	useCallback,
	useContext,
	useEffect,
	useMemo,
	useReducer,
	useRef,
	useState,
	type ReactNode,
} from 'react';
import { useNavigate, useBlocker } from 'react-router-dom';
import { ApiError, isAuthError, isNotFoundError } from '@/services/apiClient';
import { getCurrentUser } from '@/services/authService';
import {
	deleteSession as deleteSessionApi,
	getVersion,
	listSessions,
	listVersions,
	runCaseAnalysis,
} from '@/services/caseAnalysisService';
import type {
	CaseAnalysisPipelineCaseFactsPayload,
	CaseAnalysisSessionPreviewResponse,
	CaseAnalysisVersionPreviewResponse,
	CaseAnalysisVersionResponse,
	EditableCaseFact,
	PendingChangesCounts,
	UserResponse,
} from '@/types/workspace';
import {
	CASE_FACT_MAX_COUNT,
	CASE_FACT_MAX_LENGTH,
	CASE_FACT_MIN_LENGTH,
	SESSIONS_PAGE_SIZE,
	VERSIONS_PAGE_SIZE,
} from '@/types/workspace';
import { useToast } from '@/components/workspace/shared/ToastProvider';

// Safety guard to avoid infinite pagination loops on sessions list
const MAX_SESSION_OFFSET = 1000; // stop after offset reaches this value

export type ToastVariant = 'success' | 'error' | 'info';

type WorkspaceMode = 'view' | 'edit';

interface PaginationState {
	limit: number;
	offset: number;
	hasMore: boolean;
}

interface LoadingState {
	auth: boolean;
	initializing: boolean;
	sessions: boolean;
	sessionsMore: boolean;
	versions: boolean;
	versionsMore: boolean;
	analysis: boolean;
	generating: boolean;
	deleting: boolean;
}

interface WorkspaceState {
	user: UserResponse | null;
	loading: LoadingState;
	sessions: CaseAnalysisSessionPreviewResponse[];
	sessionsPagination: PaginationState;
	sessionQuery: string | null;
	selectedSessionId: string | null;
	versions: CaseAnalysisVersionPreviewResponse[];
	versionsPagination: PaginationState;
	selectedVersionNumber: number | null;
	currentAnalysis: CaseAnalysisVersionResponse | null;

	mode: WorkspaceMode;
	editState: EditableCaseFact[];
	errors: {
		sessions: string | null;
		versions: string | null;
		analysis: string | null;
	};
}

const initialState: WorkspaceState = {
	user: null,
	loading: {
		auth: true,
		initializing: false,
		sessions: false,
		sessionsMore: false,
		versions: false,
		versionsMore: false,
		analysis: false,
		generating: false,
		deleting: false,
	},
	sessions: [],
	sessionsPagination: {
		limit: SESSIONS_PAGE_SIZE,
		offset: 0,
		hasMore: false,
	},
	sessionQuery: null,
	selectedSessionId: null,
	versions: [],
	versionsPagination: {
		limit: VERSIONS_PAGE_SIZE,
		offset: 0,
		hasMore: false,
	},
	selectedVersionNumber: null,
	currentAnalysis: null,

	mode: 'view',
	editState: [],
	errors: { sessions: null, versions: null, analysis: null },
};

type WorkspaceAction =
	| { type: 'SET_USER'; user: UserResponse | null }
	| { type: 'SET_LOADING'; key: keyof LoadingState; value: boolean }
	| {
			type: 'SET_SESSIONS';
			sessions: CaseAnalysisSessionPreviewResponse[];
			append?: boolean;
			hasMore: boolean;
			offset: number;
	  }
	| { type: 'SET_SESSION_QUERY'; query: string | null }
	| { type: 'SET_SELECTED_SESSION'; sessionId: string | null }
	| {
			type: 'SET_VERSIONS';
			versions: CaseAnalysisVersionPreviewResponse[];
			append?: boolean;
			hasMore: boolean;
			offset: number;
	  }
	| { type: 'SET_SELECTED_VERSION'; versionNumber: number | null }
	| {
			type: 'SET_CURRENT_ANALYSIS';
			analysis: CaseAnalysisVersionResponse | null;
	  }
	| { type: 'SET_MODE'; mode: WorkspaceMode }
	| { type: 'SET_EDIT_STATE'; editState: EditableCaseFact[] }
	| {
			type: 'SET_ERROR';
			key: keyof WorkspaceState['errors'];
			message: string | null;
	  }
	| { type: 'REMOVE_SESSION'; sessionId: string };

function workspaceReducer(
	state: WorkspaceState,
	action: WorkspaceAction,
): WorkspaceState {
	switch (action.type) {
		case 'SET_USER':
			return { ...state, user: action.user };
		case 'SET_LOADING':
			return {
				...state,
				loading: { ...state.loading, [action.key]: action.value },
			};
		case 'SET_SESSIONS':
			return {
				...state,
				sessions: action.append
					? [...state.sessions, ...action.sessions]
					: action.sessions,
				sessionsPagination: {
					...state.sessionsPagination,
					offset: action.offset,
					hasMore: action.hasMore,
				},
				errors: { ...state.errors, sessions: null },
			};
		case 'SET_SESSION_QUERY':
			return { ...state, sessionQuery: action.query };
		case 'SET_SELECTED_SESSION':
			return {
				...state,
				selectedSessionId: action.sessionId,
				versions: [],
				versionsPagination: {
					...state.versionsPagination,
					offset: 0,
					hasMore: false,
				},
				selectedVersionNumber: null,
				currentAnalysis: null,
				mode: 'view',
				editState: [],
			};
		case 'SET_VERSIONS':
			return {
				...state,
				versions: action.append
					? [...state.versions, ...action.versions]
					: action.versions,
				versionsPagination: {
					...state.versionsPagination,
					offset: action.offset,
					hasMore: action.hasMore,
				},
				errors: { ...state.errors, versions: null },
			};
		case 'SET_SELECTED_VERSION':
			return { ...state, selectedVersionNumber: action.versionNumber };
		case 'SET_CURRENT_ANALYSIS':
			return {
				...state,
				currentAnalysis: action.analysis,
				errors: { ...state.errors, analysis: null },
			};
		case 'SET_MODE':
			return { ...state, mode: action.mode };
		case 'SET_EDIT_STATE':
			return { ...state, editState: action.editState };
		case 'SET_ERROR':
			return {
				...state,
				errors: { ...state.errors, [action.key]: action.message },
			};
		case 'REMOVE_SESSION':
			return {
				...state,
				sessions: state.sessions.filter(
					(s) => s.case_analysis_session_id !== action.sessionId,
				),
			};
		default:
			return state;
	}
}

function computePendingChanges(
	editState: EditableCaseFact[],
): PendingChangesCounts {
	return editState.reduce(
		(acc, fact) => {
			if (fact.status === 'new') acc.newFacts += 1;
			if (fact.status === 'modified') acc.modifiedFacts += 1;
			if (fact.status === 'deleted') acc.deletedFacts += 1;
			return acc;
		},
		{ newFacts: 0, modifiedFacts: 0, deletedFacts: 0 },
	);
}

function buildEditStateFromAnalysis(
	analysis: CaseAnalysisVersionResponse,
): EditableCaseFact[] {
	return analysis.case_facts.map((cf) => ({
		tempId: cf.case_fact_id,
		case_fact_id: cf.case_fact_id,
		fact: cf.fact,
		originalFact: cf.fact,
		status: 'unchanged' as const,
	}));
}

function buildReanalyzePayload(
	sessionId: string,
	editState: EditableCaseFact[],
): CaseAnalysisPipelineCaseFactsPayload | null {
	const new_case_facts = editState
		.filter((f) => f.status === 'new')
		.map((f) => f.fact.trim());
	const updated_case_facts: Record<string, string> = {};
	const deleted_case_facts: string[] = [];

	for (const fact of editState) {
		if (fact.status === 'modified' && fact.case_fact_id) {
			updated_case_facts[fact.case_fact_id] = fact.fact.trim();
		}
		if (fact.status === 'deleted' && fact.case_fact_id) {
			deleted_case_facts.push(fact.case_fact_id);
		}
	}

	const payload: CaseAnalysisPipelineCaseFactsPayload = {
		case_analysis_session_id: sessionId,
	};

	if (new_case_facts.length > 0) payload.new_case_facts = new_case_facts;
	if (Object.keys(updated_case_facts).length > 0)
		payload.updated_case_facts = updated_case_facts;
	if (deleted_case_facts.length > 0)
		payload.deleted_case_facts = deleted_case_facts;

	const hasChanges =
		(payload.new_case_facts?.length ?? 0) > 0 ||
		Object.keys(payload.updated_case_facts ?? {}).length > 0 ||
		(payload.deleted_case_facts?.length ?? 0) > 0;

	return hasChanges ? payload : null;
}

export function validateCaseFact(text: string): string | null {
	const trimmed = text.trim();
	if (trimmed.length < CASE_FACT_MIN_LENGTH) {
		return `Must be at least ${CASE_FACT_MIN_LENGTH} characters.`;
	}
	if (trimmed.length > CASE_FACT_MAX_LENGTH) {
		return `Must be at most ${CASE_FACT_MAX_LENGTH} characters.`;
	}
	return null;
}

interface PendingNavigation {
	type: 'session' | 'version' | 'newAnalysis' | 'exitEdit' | 'discard';
	payload?: unknown;
	onProceed?: () => void;
}

interface WorkspaceContextValue {
	state: WorkspaceState;
	isDirty: boolean;
	pendingChanges: PendingChangesCounts;
	isLatestVersionSelected: boolean;
	confirmDialog: {
		open: boolean;
		title: string;
		message: string;
		confirmLabel: string;
		cancelLabel: string;
		variant: 'danger' | 'default';
		onConfirm: () => void;
		onCancel: () => void;
	} | null;
	newAnalysisModalOpen: boolean;
	setNewAnalysisModalOpen: (open: boolean) => void;

	requestNewAnalysis: () => void;
	initialize: () => Promise<void>;
	refreshSessions: () => Promise<void>;
	loadMoreSessions: () => Promise<void>;
	searchSessions: (query: string | null) => Promise<void>;
	selectSession: (sessionId: string) => Promise<void>;
	loadMoreVersions: () => Promise<void>;
	selectVersion: (versionNumber: number) => Promise<void>;
	enterEditMode: () => void;
	exitEditMode: () => void;
	addEditFact: () => void;
	updateEditFact: (tempId: string, fact: string) => void;
	deleteEditFact: (tempId: string) => void;
	restoreEditFact: (tempId: string) => void;
	undoEditFact: (tempId: string) => void;
	discardAllChanges: () => void;
	submitReanalysis: () => Promise<void>;
	submitNewAnalysis: (facts: string[]) => Promise<void>;
	deleteSelectedSession: () => Promise<void>;
	requestDeleteSession: (sessionId: string) => void;
	handleApiError: (error: unknown, context: string) => void;
}

const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
	const [state, dispatch] = useReducer(workspaceReducer, initialState);
	const navigate = useNavigate();
	const { showToast } = useToast();
	const initRef = useRef(false);
	const pendingNavRef = useRef<PendingNavigation | null>(null);
	const [confirmDialog, setConfirmDialog] =
		useState<WorkspaceContextValue['confirmDialog']>(null);
	const [newAnalysisModalOpen, setNewAnalysisModalOpenRaw] = useState(false);
	const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

	const isDirty = useMemo(
		() => state.editState.some((f) => f.status !== 'unchanged'),
		[state.editState],
	);

	const pendingChanges = useMemo(
		() => computePendingChanges(state.editState),
		[state.editState],
	);

	const isLatestVersionSelected = useMemo(() => {
		if (state.versions.length === 0 || state.selectedVersionNumber === null)
			return false;
		const latest = state.versions[0];
		return latest?.version_number === state.selectedVersionNumber;
	}, [state.versions, state.selectedVersionNumber]);

	const handleAuthError = useCallback(() => {
		navigate('/login');
	}, [navigate]);

	const handleApiError = useCallback(
		(error: unknown, context: string) => {
			if (isAuthError(error)) {
				handleAuthError();
				return;
			}
			if (error instanceof ApiError) {
				if (error.code === 'LLM_SERVICE_ERROR') {
					showToast(
						'Analysis generation failed, please retry.',
						'error',
					);
					return;
				}
				if (isNotFoundError(error)) {
					showToast('The requested resource was not found.', 'error');
					return;
				}
				if (error.code === 'VALIDATION_ERROR') {
					showToast(error.message, 'error');
					return;
				}
			}
			showToast(
				`Something went wrong${context ? ` while ${context}` : ''}. Please try again.`,
				'error',
			);
		},
		[handleAuthError, showToast],
	);

	const fetchSessions = useCallback(
		async (offset: number, query: string | null, append: boolean) => {
			const loadingKey = append ? 'sessionsMore' : 'sessions';
			dispatch({ type: 'SET_LOADING', key: loadingKey, value: true });
			try {
				const sessions = await listSessions({
					limit: SESSIONS_PAGE_SIZE,
					offset,
					query: query ?? undefined,
				});
				dispatch({
					type: 'SET_SESSIONS',
					sessions,
					append,
					hasMore: sessions.length === SESSIONS_PAGE_SIZE,
					offset: offset + sessions.length,
				});
				return sessions;
			} catch (error) {
				if (isAuthError(error)) {
					handleAuthError();
					return [];
				}
				dispatch({
					type: 'SET_ERROR',
					key: 'sessions',
					message: 'Failed to load sessions.',
				});
				handleApiError(error, 'loading sessions');
				return [];
			} finally {
				dispatch({
					type: 'SET_LOADING',
					key: loadingKey,
					value: false,
				});
			}
		},
		[handleApiError, handleAuthError],
	);

	const loadVersionsForSession = useCallback(
		async (sessionId: string, offset = 0, append = false) => {
			const loadingKey = append ? 'versionsMore' : 'versions';
			dispatch({ type: 'SET_LOADING', key: loadingKey, value: true });
			try {
				const versions = await listVersions(sessionId, {
					limit: VERSIONS_PAGE_SIZE,
					offset,
				});
				dispatch({
					type: 'SET_VERSIONS',
					versions,
					append,
					hasMore: versions.length === VERSIONS_PAGE_SIZE,
					offset: offset + versions.length,
				});
				return versions;
			} catch (error) {
				if (isAuthError(error)) {
					handleAuthError();
					return [];
				}
				dispatch({
					type: 'SET_ERROR',
					key: 'versions',
					message: 'Failed to load versions.',
				});
				handleApiError(error, 'loading versions');
				return [];
			} finally {
				dispatch({
					type: 'SET_LOADING',
					key: loadingKey,
					value: false,
				});
			}
		},
		[handleApiError, handleAuthError],
	);

	const loadAnalysis = useCallback(
		async (sessionId: string, versionNumber: number) => {
			dispatch({ type: 'SET_LOADING', key: 'analysis', value: true });
			try {
				const detail = await getVersion(sessionId, versionNumber);
				dispatch({
					type: 'SET_CURRENT_ANALYSIS',
					analysis: detail.case_analysis,
				});
			} catch (error) {
				if (isAuthError(error)) {
					handleAuthError();
					return;
				}
				dispatch({
					type: 'SET_ERROR',
					key: 'analysis',
					message: 'Failed to load analysis.',
				});
				handleApiError(error, 'loading analysis');
			} finally {
				dispatch({
					type: 'SET_LOADING',
					key: 'analysis',
					value: false,
				});
			}
		},
		[handleApiError, handleAuthError],
	);

	const selectSessionInternal = useCallback(
		async (sessionId: string) => {
			dispatch({ type: 'SET_SELECTED_SESSION', sessionId });
			const versions = await loadVersionsForSession(sessionId);
			if (versions.length > 0) {
				const latest = versions[0];
				dispatch({
					type: 'SET_SELECTED_VERSION',
					versionNumber: latest.version_number,
				});
				await loadAnalysis(sessionId, latest.version_number);
			}
		},
		[loadAnalysis, loadVersionsForSession],
	);

	const initialize = useCallback(async () => {
		dispatch({ type: 'SET_LOADING', key: 'initializing', value: true });
		try {
			const user = await getCurrentUser();
			dispatch({ type: 'SET_USER', user });
			const sessions = await fetchSessions(0, null, false);
			if (sessions.length > 0) {
				await selectSessionInternal(
					sessions[0].case_analysis_session_id,
				);
			}
		} catch (error) {
			if (isAuthError(error)) {
				handleAuthError();
			} else {
				handleApiError(error, 'initializing workspace');
			}
		} finally {
			dispatch({ type: 'SET_LOADING', key: 'auth', value: false });
			dispatch({
				type: 'SET_LOADING',
				key: 'initializing',
				value: false,
			});
		}
	}, [fetchSessions, handleApiError, handleAuthError, selectSessionInternal]);

	useEffect(() => {
		if (!initRef.current) {
			initRef.current = true;
			void initialize();
		}
	}, [initialize]);

	const confirmIfDirty = useCallback(
		(nav: PendingNavigation, onProceed: () => void) => {
			if (!isDirty) {
				onProceed();
				return;
			}
			pendingNavRef.current = { ...nav, onProceed };
			setConfirmDialog({
				open: true,
				title: 'Unsaved changes',
				message:
					'You have unsaved changes. If you leave now, your pending modifications will be lost.',
				confirmLabel: 'Discard Changes',
				cancelLabel: 'Continue Editing',
				variant: 'danger',
				onConfirm: () => {
					dispatch({ type: 'SET_MODE', mode: 'view' });
					dispatch({ type: 'SET_EDIT_STATE', editState: [] });
					setConfirmDialog(null);
					pendingNavRef.current?.onProceed?.();
					pendingNavRef.current = null;
				},
				onCancel: () => {
					setConfirmDialog(null);
					pendingNavRef.current = null;
				},
			});
		},
		[isDirty],
	);

	const selectSession = useCallback(
		async (sessionId: string) => {
			if (sessionId === state.selectedSessionId) return;
			confirmIfDirty({ type: 'session', payload: sessionId }, () => {
				void selectSessionInternal(sessionId);
			});
		},
		[confirmIfDirty, selectSessionInternal, state.selectedSessionId],
	);

	const selectVersion = useCallback(
		async (versionNumber: number) => {
			if (
				versionNumber === state.selectedVersionNumber ||
				!state.selectedSessionId
			)
				return;

			const proceed = () => {
				dispatch({ type: 'SET_MODE', mode: 'view' });
				dispatch({ type: 'SET_EDIT_STATE', editState: [] });
				dispatch({ type: 'SET_SELECTED_VERSION', versionNumber });
				void loadAnalysis(state.selectedSessionId!, versionNumber);
			};

			if (state.mode === 'edit' || isDirty) {
				confirmIfDirty(
					{ type: 'version', payload: versionNumber },
					proceed,
				);
			} else {
				proceed();
			}
		},
		[
			confirmIfDirty,
			isDirty,
			loadAnalysis,
			state.mode,
			state.selectedSessionId,
			state.selectedVersionNumber,
		],
	);

	const refreshSessions = useCallback(async () => {
		dispatch({ type: 'SET_SESSION_QUERY', query: state.sessionQuery });
		await fetchSessions(0, state.sessionQuery, false);
	}, [fetchSessions, state.sessionQuery]);

	const loadMoreSessions = useCallback(async () => {
		if (!state.sessionsPagination.hasMore || state.loading.sessionsMore)
			return;
		// Prevent runaway pagination if backend keeps returning full pages
		if (state.sessionsPagination.offset >= MAX_SESSION_OFFSET) {
			dispatch({
				type: 'SET_SESSIONS',
				sessions: [],
				append: true,
				hasMore: false,
				offset: state.sessionsPagination.offset,
			});
			return;
		}
		await fetchSessions(
			state.sessionsPagination.offset,
			state.sessionQuery,
			true,
		);
	}, [
		fetchSessions,
		state.loading.sessionsMore,
		state.sessionQuery,
		state.sessionsPagination.hasMore,
		state.sessionsPagination.offset,
	]);

	const searchSessions = useCallback(
		async (query: string | null) => {
			dispatch({ type: 'SET_SESSION_QUERY', query });
			await fetchSessions(0, query, false);
		},
		[fetchSessions],
	);

	const loadMoreVersions = useCallback(async () => {
		if (
			!state.selectedSessionId ||
			!state.versionsPagination.hasMore ||
			state.loading.versionsMore
		)
			return;
		await loadVersionsForSession(
			state.selectedSessionId,
			state.versionsPagination.offset,
			true,
		);
	}, [
		loadVersionsForSession,
		state.loading.versionsMore,
		state.selectedSessionId,
		state.versionsPagination.hasMore,
		state.versionsPagination.offset,
	]);

	const enterEditMode = useCallback(() => {
		if (!state.currentAnalysis || !isLatestVersionSelected) return;
		dispatch({ type: 'SET_MODE', mode: 'edit' });
		dispatch({
			type: 'SET_EDIT_STATE',
			editState: buildEditStateFromAnalysis(state.currentAnalysis),
		});
	}, [isLatestVersionSelected, state.currentAnalysis]);

	const exitEditMode = useCallback(() => {
		const proceed = () => {
			dispatch({ type: 'SET_MODE', mode: 'view' });
			dispatch({ type: 'SET_EDIT_STATE', editState: [] });
		};
		if (isDirty) {
			confirmIfDirty({ type: 'exitEdit' }, proceed);
		} else {
			proceed();
		}
	}, [confirmIfDirty, isDirty]);

	const addEditFact = useCallback(() => {
		const activeCount = state.editState.filter(
			(f) => f.status !== 'deleted',
		).length;
		if (activeCount >= CASE_FACT_MAX_COUNT) return;
		const newFact: EditableCaseFact = {
			tempId: crypto.randomUUID(),
			case_fact_id: null,
			fact: '',
			originalFact: '',
			status: 'new',
		};
		dispatch({
			type: 'SET_EDIT_STATE',
			editState: [...state.editState, newFact],
		});
	}, [state.editState]);

	const updateEditFact = useCallback(
		(tempId: string, fact: string) => {
			dispatch({
				type: 'SET_EDIT_STATE',
				editState: state.editState.map((f) => {
					if (f.tempId !== tempId) return f;
					if (f.status === 'new') return { ...f, fact };
					if (f.status === 'deleted') return f;
					const isModified = fact !== f.originalFact;
					return {
						...f,
						fact,
						status: isModified ? 'modified' : 'unchanged',
					};
				}),
			});
		},
		[state.editState],
	);

	const deleteEditFact = useCallback(
		(tempId: string) => {
			dispatch({
				type: 'SET_EDIT_STATE',
				editState: state.editState
					.map((f) => {
						if (f.tempId !== tempId) return f;
						if (f.status === 'new') return null;
						return { ...f, status: 'deleted' as const };
					})
					.filter(Boolean) as EditableCaseFact[],
			});
		},
		[state.editState],
	);

	const restoreEditFact = useCallback(
		(tempId: string) => {
			dispatch({
				type: 'SET_EDIT_STATE',
				editState: state.editState.map((f) => {
					if (f.tempId !== tempId || f.status !== 'deleted') return f;
					const isModified = f.fact !== f.originalFact;
					return {
						...f,
						status: isModified ? 'modified' : 'unchanged',
					};
				}),
			});
		},
		[state.editState],
	);

	const undoEditFact = useCallback(
		(tempId: string) => {
			dispatch({
				type: 'SET_EDIT_STATE',
				editState: state.editState
					.map((f) => {
						if (f.tempId !== tempId) return f;
						if (f.status === 'new') return null;
						return {
							...f,
							fact: f.originalFact,
							status: 'unchanged' as const,
						};
					})
					.filter(Boolean) as EditableCaseFact[],
			});
		},
		[state.editState],
	);

	const discardAllChanges = useCallback(() => {
		if (!state.currentAnalysis) return;
		dispatch({
			type: 'SET_EDIT_STATE',
			editState: buildEditStateFromAnalysis(state.currentAnalysis),
		});
		showToast('Changes discarded.', 'info');
	}, [showToast, state.currentAnalysis]);

	const submitReanalysis = useCallback(async () => {
		if (!state.selectedSessionId || !isDirty) return;
		const payload = buildReanalyzePayload(
			state.selectedSessionId,
			state.editState,
		);
		if (!payload) return;

		dispatch({ type: 'SET_LOADING', key: 'generating', value: true });
		try {
			const result = await runCaseAnalysis(payload);
			showToast('Analysis completed.', 'success');
			dispatch({ type: 'SET_MODE', mode: 'view' });
			dispatch({ type: 'SET_EDIT_STATE', editState: [] });
			await fetchSessions(0, state.sessionQuery, false);
			const versions = await loadVersionsForSession(
				state.selectedSessionId,
			);
			if (versions.length > 0) {
				const newest = result.case_analysis.version_number;
				dispatch({
					type: 'SET_SELECTED_VERSION',
					versionNumber: newest,
				});
				dispatch({
					type: 'SET_CURRENT_ANALYSIS',
					analysis: result.case_analysis,
				});
			}
		} catch (error) {
			handleApiError(error, 'generating analysis');
		} finally {
			dispatch({ type: 'SET_LOADING', key: 'generating', value: false });
		}
	}, [
		fetchSessions,
		handleApiError,
		isDirty,
		loadVersionsForSession,
		showToast,
		state.editState,
		state.selectedSessionId,
		state.sessionQuery,
	]);

	const submitNewAnalysis = useCallback(
		async (facts: string[]) => {
			dispatch({ type: 'SET_LOADING', key: 'generating', value: true });
			try {
				const result = await runCaseAnalysis({ new_case_facts: facts });
				showToast('Analysis completed.', 'success');
				setNewAnalysisModalOpenRaw(false);
				await fetchSessions(0, state.sessionQuery, false);
				await selectSessionInternal(result.case_analysis_session_id);
			} catch (error) {
				handleApiError(error, 'creating analysis');
				throw error;
			} finally {
				dispatch({
					type: 'SET_LOADING',
					key: 'generating',
					value: false,
				});
			}
		},
		[
			fetchSessions,
			handleApiError,
			selectSessionInternal,
			showToast,
			state.sessionQuery,
		],
	);

	const requestNewAnalysis = useCallback(() => {
		confirmIfDirty({ type: 'newAnalysis' }, () => {
			setNewAnalysisModalOpenRaw(true);
		});
	}, [confirmIfDirty]);

	const setNewAnalysisModalOpen = useCallback(
		(open: boolean) => {
			if (open) {
				requestNewAnalysis();
			} else {
				setNewAnalysisModalOpenRaw(false);
			}
		},
		[requestNewAnalysis],
	);

	const deleteSelectedSession = useCallback(async () => {
		const sessionId = sessionToDelete ?? state.selectedSessionId;
		if (!sessionId) return;

		dispatch({ type: 'SET_LOADING', key: 'deleting', value: true });
		try {
			await deleteSessionApi(sessionId);
			showToast('Session deleted.', 'success');
			const wasSelected = state.selectedSessionId === sessionId;
			const remaining = state.sessions.filter(
				(s) => s.case_analysis_session_id !== sessionId,
			);
			dispatch({ type: 'REMOVE_SESSION', sessionId });
			setSessionToDelete(null);
			setConfirmDialog(null);

			if (wasSelected) {
				if (remaining.length > 0) {
					await selectSessionInternal(
						remaining[0].case_analysis_session_id,
					);
				} else {
					dispatch({ type: 'SET_SELECTED_SESSION', sessionId: null });
				}
			}
		} catch (error) {
			handleApiError(error, 'deleting session');
		} finally {
			dispatch({ type: 'SET_LOADING', key: 'deleting', value: false });
		}
	}, [
		handleApiError,
		selectSessionInternal,
		sessionToDelete,
		showToast,
		state.selectedSessionId,
		state.sessions,
	]);

	const requestDeleteSession = useCallback(
		(sessionId: string) => {
			setSessionToDelete(sessionId);
			setConfirmDialog({
				open: true,
				title: 'Delete session',
				message:
					'Are you sure you want to delete this analysis session? This action cannot be undone.',
				confirmLabel: 'Delete',
				cancelLabel: 'Cancel',
				variant: 'danger',
				onConfirm: () => {
					void deleteSelectedSession();
				},
				onCancel: () => {
					setSessionToDelete(null);
					setConfirmDialog(null);
				},
			});
		},
		[deleteSelectedSession],
	);

	useEffect(() => {
		if (!isDirty) return;
		const handler = (e: BeforeUnloadEvent) => {
			e.preventDefault();
		};
		window.addEventListener('beforeunload', handler);
		return () => window.removeEventListener('beforeunload', handler);
	}, [isDirty]);

	const blocker = useBlocker(
		({ currentLocation, nextLocation }) =>
			isDirty && currentLocation.pathname !== nextLocation.pathname,
	);

	useEffect(() => {
		if (blocker.state !== 'blocked') return;
		pendingNavRef.current = {
			type: 'discard',
			onProceed: () => blocker.proceed?.(),
		};
		setConfirmDialog({
			open: true,
			title: 'Unsaved changes',
			message:
				'You have unsaved changes. If you leave now, your pending modifications will be lost.',
			confirmLabel: 'Discard Changes',
			cancelLabel: 'Continue Editing',
			variant: 'danger',
			onConfirm: () => {
				dispatch({ type: 'SET_MODE', mode: 'view' });
				dispatch({ type: 'SET_EDIT_STATE', editState: [] });
				setConfirmDialog(null);
				blocker.proceed?.();
				pendingNavRef.current = null;
			},
			onCancel: () => {
				setConfirmDialog(null);
				blocker.reset?.();
				pendingNavRef.current = null;
			},
		});
	}, [blocker]);

	const value: WorkspaceContextValue = {
		state,
		isDirty,
		pendingChanges,
		isLatestVersionSelected,
		confirmDialog,
		newAnalysisModalOpen,
		setNewAnalysisModalOpen,
		requestNewAnalysis,
		initialize,
		refreshSessions,
		loadMoreSessions,
		searchSessions,
		selectSession,
		loadMoreVersions,
		selectVersion,
		enterEditMode,
		exitEditMode,
		addEditFact,
		updateEditFact,
		deleteEditFact,
		restoreEditFact,
		undoEditFact,
		discardAllChanges,
		submitReanalysis,
		submitNewAnalysis,
		deleteSelectedSession,
		requestDeleteSession,
		handleApiError,
	};

	return (
		<WorkspaceContext.Provider value={value}>
			{children}
		</WorkspaceContext.Provider>
	);
}

export function useWorkspace() {
	const ctx = useContext(WorkspaceContext);
	if (!ctx) {
		throw new Error('useWorkspace must be used within WorkspaceProvider');
	}
	return ctx;
}
