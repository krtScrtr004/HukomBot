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
import { useToast } from '@/contexts/ToastProvider';

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

// Workspace state structure
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

// Initial state for the workspace
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

// Workspace actions for the reducer
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

/**
 * Reducer function to manage workspace state transitions.
 * @param {WorkspaceState} state - The current workspace state.
 * @param {WorkspaceAction} action - The action to dispatch.
 * @returns {WorkspaceState} - The updated workspace state.
 */
function workspaceReducer(
	state: WorkspaceState,
	action: WorkspaceAction,
): WorkspaceState {
	/* The reducer function handles state transitions based on dispatched actions.
	 * It takes the current state and the action type.
	 * Each case in the switch statement corresponds to a specific action that updates the state accordingly.
	 */
	switch (action.type) {
		case 'SET_USER':
			// Update the user information in the state
			return { ...state, user: action.user };
		case 'SET_LOADING':
			// Update the loading state for a specific key
			// The key is a property of the loading state (e.g., 'auth', 'sessions', etc.),
			// and the value is a boolean indicating whether that part of the state is currently loading.
			return {
				...state,
				loading: { ...state.loading, [action.key]: action.value },
			};
		case 'SET_SESSIONS':
			// Update the sessions list and pagination information in the state
			// If append is true, append the new sessions to the existing list; otherwise, replace the list.
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
			// Update the session query (for search feature) string in the state
			return { ...state, sessionQuery: action.query };
		case 'SET_SELECTED_SESSION':
			// Update the selected session ID in the state and reset related data (versions, analysis, etc.) when a new session is selected
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
			// Update the versions list and pagination information in the state
			// If append is true, append the new versions to the existing list; otherwise, replace the list.
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
			// Update the selected version number in the state
			return { ...state, selectedVersionNumber: action.versionNumber };
		case 'SET_CURRENT_ANALYSIS':
			// Update the current analysis data in the state and clear any existing analysis errors
			return {
				...state,
				currentAnalysis: action.analysis,
				errors: { ...state.errors, analysis: null },
			};
		case 'SET_MODE':
			// Update the workspace mode (view or edit) in the state
			return { ...state, mode: action.mode };
		case 'SET_EDIT_STATE':
			// Update the edit state (list of editable case facts) in the state
			return { ...state, editState: action.editState };
		case 'SET_ERROR':
			// Update the error message for a specific key in the state
			return {
				...state,
				errors: { ...state.errors, [action.key]: action.message },
			};
		case 'REMOVE_SESSION':
			// Remove a session from the sessions list in the state based on the provided session ID
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

/**
 * Computes the count of pending changes in the edit state.
 * @param {EditableCaseFact[]} editState - The list of editable case facts.
 * @returns {PendingChangesCounts} - The counts of new, modified, and deleted facts.
 */
function computePendingChanges(
	editState: EditableCaseFact[],
): PendingChangesCounts {
	return editState.reduce(
		(acc, fact) => {
			if (fact.status === 'new') {
				acc.newFacts += 1;
			}
			if (fact.status === 'modified') {
				acc.modifiedFacts += 1;
			}
			if (fact.status === 'deleted') {
				acc.deletedFacts += 1;
			}
			return acc;
		},
		{ newFacts: 0, modifiedFacts: 0, deletedFacts: 0 },
	);
}

/**
 * Builds the edit state from the analysis facts.
 * @param {CaseAnalysisVersionResponse} analysis - The analysis data.
 * @returns {EditableCaseFact[]} - The list of editable case facts.
 */
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

/**
 * Builds the reanalyze payload based on the edit state.
 * @param {string} sessionId - The ID of the session for which to build the reanalyze payload.
 * @param {EditableCaseFact[]} editState - The list of editable case facts.
 * @returns {CaseAnalysisPipelineCaseFactsPayload | null} - The reanalyze payload or null if no changes are present.
 */
function buildReanalyzePayload(
	sessionId: string,
	editState: EditableCaseFact[],
): CaseAnalysisPipelineCaseFactsPayload | null {
	const new_case_facts = editState
		.filter((f) => f.status === 'new')
		.map((f) => f.fact.trim());
	const updated_case_facts: Record<string, string> = {};
	const deleted_case_facts: string[] = [];

	// Build the updated and deleted case facts
	for (const fact of editState) {
		if (fact.status === 'modified' && fact.case_fact_id) {
			updated_case_facts[fact.case_fact_id] = fact.fact.trim();
		}
		if (fact.status === 'deleted' && fact.case_fact_id) {
			deleted_case_facts.push(fact.case_fact_id);
		}
	}

	// Build the payload for reanalysis based on the edit state
	const payload: CaseAnalysisPipelineCaseFactsPayload = {
		case_analysis_session_id: sessionId,
	};

	if (new_case_facts.length > 0) {
		payload.new_case_facts = new_case_facts;
	}
	if (Object.keys(updated_case_facts).length > 0) {
		payload.updated_case_facts = updated_case_facts;
	}
	if (deleted_case_facts.length > 0) {
		payload.deleted_case_facts = deleted_case_facts;
	}

	const hasChanges =
		(payload.new_case_facts?.length ?? 0) > 0 ||
		Object.keys(payload.updated_case_facts ?? {}).length > 0 ||
		(payload.deleted_case_facts?.length ?? 0) > 0;

	return hasChanges ? payload : null;
}

/**
 * Validates a case fact based on length constraints.
 * @param {string} text The case fact to validate.
 * @returns {string | null} An error message if the fact is invalid, or null if it's valid.
 */
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

// Interface for the workspace context value
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

// Create the workspace context
const WorkspaceContext = createContext<WorkspaceContextValue | null>(null);

/**
 * Provider component for the workspace context.
 * @param {ReactNode} children - The child components that will have access to the workspace context.
 * @returns
 */
export function WorkspaceProvider({ children }: { children: ReactNode }) {
	const [state, dispatch] = useReducer(workspaceReducer, initialState);

	const navigate = useNavigate();
	const { showToast } = useToast();

	const initRef = useRef(false); // Flag to ensure initialization runs only once
	const pendingNavRef = useRef<PendingNavigation | null>(null); // Ref to store pending navigation actions when there are unsaved changes

	const [confirmDialog, setConfirmDialog] =
		useState<WorkspaceContextValue['confirmDialog']>(null);
	const [newAnalysisModalOpen, setNewAnalysisModalOpenRaw] = useState(false);
	const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

	// Memoized value to determine if there are unsaved changes in the edit state
	const isDirty = useMemo(
		() => state.editState.some((f) => f.status !== 'unchanged'),
		[state.editState],
	);

	// Memoized value to compute pending changes counts based on the current edit state
	const pendingChanges = useMemo(
		() => computePendingChanges(state.editState),
		[state.editState],
	);

	// Memoized value to check if the latest version is selected based on the versions list and the selected version number
	const isLatestVersionSelected = useMemo(() => {
		if (
			state.versions.length === 0 ||
			state.selectedVersionNumber === null
		) {
			return false;
		}
		const latest = state.versions[0];
		return latest?.version_number === state.selectedVersionNumber;
	}, [state.versions, state.selectedVersionNumber]);

	// Callback to handle authentication errors by navigating to the login page
	const handleAuthError = useCallback(() => {
		navigate('/login');
	}, [navigate]);

	const handleApiError = useCallback(
		(error: unknown, context: string) => {
			// Return to login page if the error is an authentication error
			if (isAuthError(error)) {
				handleAuthError();
				return;
			}

			// Show specific error messages based on the type of API error encountered
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

	// Retrieve the list of sessions from the API
	const fetchSessions = useCallback(
		async (offset: number, query: string | null, append: boolean) => {
			const loadingKey = append ? 'sessionsMore' : 'sessions';
			// Set the loading state for sessions or sessionsMore based on whether we are appending or not
			dispatch({ type: 'SET_LOADING', key: loadingKey, value: true });

			try {
				// Fetch the list of sessions from the API with the specified limit, offset, and query parameters
				const sessions = await listSessions({
					limit: SESSIONS_PAGE_SIZE,
					offset,
					query: query ?? undefined,
				});

				// Update the state with the fetched sessions, pagination info, and whether there are more sessions to load
				dispatch({
					type: 'SET_SESSIONS',
					sessions,
					append,
					hasMore: sessions.length === SESSIONS_PAGE_SIZE,
					offset: offset + sessions.length,
				});

				return sessions;
			} catch (error) {
				// Handle authentication errors by navigating to the login page
				if (isAuthError(error)) {
					handleAuthError();
					return [];
				}

				// Set an error message in the state for sessions if the API call fails
				dispatch({
					type: 'SET_ERROR',
					key: 'sessions',
					message: 'Failed to load sessions.',
				});

				handleApiError(error, 'loading sessions');
				return [];
			} finally {
				// Reset the loading state for sessions or sessionsMore after the API call is complete
				dispatch({
					type: 'SET_LOADING',
					key: loadingKey,
					value: false,
				});
			}
		},
		[handleApiError, handleAuthError],
	);

	// Retrieve the list of versions for a specific session from the API
	const loadVersionsForSession = useCallback(
		async (sessionId: string, offset = 0, append = false) => {
			const loadingKey = append ? 'versionsMore' : 'versions';
			// Set the loading state for versions or versionsMore based on whether we are appending or not
			dispatch({ type: 'SET_LOADING', key: loadingKey, value: true });

			try {
				// Fetch the list of versions for the specified session from the API with the specified limit and offset
				const versions = await listVersions(sessionId, {
					limit: VERSIONS_PAGE_SIZE,
					offset,
				});

				// Update the state with the fetched versions, pagination info, and whether there are more versions to load
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

	// Load the analysis details for a specific session and version from the API
	const loadAnalysis = useCallback(
		async (sessionId: string, versionNumber: number) => {
			// Set the loading state for analysis to true before making the API call
			dispatch({ type: 'SET_LOADING', key: 'analysis', value: true });

			try {
				// Fetch the analysis details for the specified session and version from the API
				const detail = await getVersion(sessionId, versionNumber);

				// Update the state with the fetched analysis details
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

	// Select a session and load its versions and analysis details
	const selectSessionInternal = useCallback(
		async (sessionId: string) => {
			// Set the selected session ID in the state and reset related data (versions, analysis, etc.) when a new session is selected
			dispatch({ type: 'SET_SELECTED_SESSION', sessionId });
			const versions = await loadVersionsForSession(sessionId);

			// If there are versions available for the selected session, select the latest version and load its analysis details
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

	// Initialize the workspace context by fetching the current user and the list of sessions
	const initialize = useCallback(async () => {
		dispatch({ type: 'SET_LOADING', key: 'initializing', value: true });

		try {
			// Fetch the current user information from the API and update the state
			const user = await getCurrentUser();

			dispatch({ type: 'SET_USER', user });

			// Fetch the list of sessions from the API and select the first session if available
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

	// Use effect to initialize the workspace context when the component mounts
	useEffect(() => {
		if (!initRef.current) {
			initRef.current = true;
			void initialize();
		}
	}, [initialize]);

	// Callback to confirm navigation if there are unsaved changes in the edit state
	const confirmIfDirty = useCallback(
		(nav: PendingNavigation, onProceed: () => void) => {
			if (!isDirty) {
				onProceed();
				return;
			}

			// Store the pending navigation action and its associated callback in a ref to be used later when the user confirms or cancels the navigation
			pendingNavRef.current = { ...nav, onProceed };

			// Show a confirmation dialog to the user if there are unsaved changes in the edit state,
			// warning them that their pending modifications will be lost if they proceed with the navigation
			setConfirmDialog({
				open: true,
				title: 'Unsaved changes',
				message:
					'You have unsaved changes. If you leave now, your pending modifications will be lost.',
				confirmLabel: 'Discard Changes',
				cancelLabel: 'Continue Editing',
				variant: 'danger',
				onConfirm: () => {
					// If the user confirms, reset the workspace mode to 'view'
					// and reset the edit state to an empty array, discarding any unsaved changes.
					dispatch({ type: 'SET_MODE', mode: 'view' });
					dispatch({ type: 'SET_EDIT_STATE', editState: [] });
					setConfirmDialog(null);
					pendingNavRef.current?.onProceed?.(); // Call the onProceed callback to continue with the navigation action after discarding changes
					pendingNavRef.current = null; // Reset the pending navigation ref to null after handling the navigation action
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
			if (sessionId === state.selectedSessionId) {
				return;
			}

			confirmIfDirty({ type: 'session', payload: sessionId }, () => {
				// Set the selected session and load its versions and analysis details
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
			) {
				return;
			}

			// Set the selected version number in the state and reset the edit state to an empty array
			const proceed = () => {
				dispatch({ type: 'SET_MODE', mode: 'view' });
				dispatch({ type: 'SET_EDIT_STATE', editState: [] });
				dispatch({ type: 'SET_SELECTED_VERSION', versionNumber });
				void loadAnalysis(state.selectedSessionId!, versionNumber);
			};

			// If there are unsaved changes, show a confirmation dialog to the user before proceeding with the version selection.
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
		if (!state.sessionsPagination.hasMore || state.loading.sessionsMore) {
			return;
		}

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
		/**
		 * If there is no selected session,
		 * or if there are no more versions to load,
		 * or if the versions are already loading,
		 * return early and do not attempt to load more versions.
		 */
		if (
			!state.selectedSessionId ||
			!state.versionsPagination.hasMore ||
			state.loading.versionsMore
		) {
			return;
		}

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
		// Prevent entering edit mode if there is no current analysis or if the latest version is not selected
		if (!state.currentAnalysis || !isLatestVersionSelected) {
			return;
		}

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
		// Count the number of active (non-deleted) facts in the edit state
		const activeCount = state.editState.filter(
			(f) => f.status !== 'deleted',
		).length;

		if (activeCount >= CASE_FACT_MAX_COUNT) {
			return;
		}

		// Create a new editable case fact with a temporary ID and default values, and add it to the edit state
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
					// If the tempId does not match, return the fact unchanged
					if (f.tempId !== tempId) {
						return f;
					}

					// If the fact is new, update it with the new fact value
					if (f.status === 'new') {
						return { ...f, fact };
					}

					// If the fact is marked as deleted, return it unchanged
					if (f.status === 'deleted') {
						return f;
					}

					// If the fact is unchanged, check if it has been modified and update its status accordingly
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
						if (f.tempId !== tempId) {
							return f;
						}
						if (f.status === 'new') {
							return null;
						}
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
					// If the tempId does not match or the fact is not marked as deleted, return the fact unchanged
					if (f.tempId !== tempId || f.status !== 'deleted') {
						return f;
					}

					// If the fact is marked as deleted, restore it to its original state and update its status accordingly
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
						// If the tempId does not match, return the fact unchanged
						if (f.tempId !== tempId) {
							return f;
						}

						// If the fact is new, return null to remove it from the edit state
						if (f.status === 'new') {
							return null;
						}

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
		if (!state.currentAnalysis) {
			return;
		}

		dispatch({
			type: 'SET_EDIT_STATE',
			editState: buildEditStateFromAnalysis(state.currentAnalysis),
		});

		showToast('Changes discarded.', 'info');
	}, [showToast, state.currentAnalysis]);

	const submitReanalysis = useCallback(async () => {
		if (!state.selectedSessionId || !isDirty) {
			return;
		}

		const payload = buildReanalyzePayload(
			state.selectedSessionId,
			state.editState,
		);
		if (!payload) {
			return;
		}

		dispatch({ type: 'SET_LOADING', key: 'generating', value: true });
		try {
			// Run the case analysis with the constructed payload and handle the response
			const result = await runCaseAnalysis(payload);

			showToast('Analysis completed.', 'success');

			dispatch({ type: 'SET_MODE', mode: 'view' });
			dispatch({ type: 'SET_EDIT_STATE', editState: [] });

			// Fetch the updated list of sessions and versions for the selected session after the reanalysis is completed
			await fetchSessions(0, state.sessionQuery, false);
			const versions = await loadVersionsForSession(
				state.selectedSessionId,
			);
			if (versions.length > 0) {
				// Select the newest version from the list of versions
				// and update the state with the selected version number
				// and current analysis details
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
				// Run the case analysis with the provided new case facts and handle the response
				const result = await runCaseAnalysis({ new_case_facts: facts });

				showToast('Analysis completed.', 'success');
				setNewAnalysisModalOpenRaw(false);

				// Fetch the updated list of sessions and select the newly created session after the analysis is completed
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

	// Callback to request a new analysis, showing a confirmation dialog if there are unsaved changes
	const requestNewAnalysis = useCallback(() => {
		confirmIfDirty({ type: 'newAnalysis' }, () => {
			setNewAnalysisModalOpenRaw(true);
		});
	}, [confirmIfDirty]);

	// Callback to handle opening and closing the new analysis modal, and request a new analysis if the modal is opened
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
		if (!sessionId) {
			return;
		}

		dispatch({ type: 'SET_LOADING', key: 'deleting', value: true });
		try {
			// Call the API to delete the selected session and handle the response
			await deleteSessionApi(sessionId);

			showToast('Session deleted.', 'success');

			const wasSelected = state.selectedSessionId === sessionId;
			const remaining = state.sessions.filter(
				(s) => s.case_analysis_session_id !== sessionId,
			);

			dispatch({ type: 'REMOVE_SESSION', sessionId });

			setSessionToDelete(null);
			setConfirmDialog(null);

			// If the deleted session was the currently selected session,
			// select the next available session or clear the selection if there are no remaining sessions
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

	// Prevent the user from navigating away from the page if there are unsaved changes in the edit state
	useEffect(() => {
		if (!isDirty) {
			return;
		}

		const handler = (e: BeforeUnloadEvent) => {
			e.preventDefault();
		};
		window.addEventListener('beforeunload', handler);
		return () => window.removeEventListener('beforeunload', handler);
	}, [isDirty]);

	// Block navigation if there are unsaved changes in the edit state and the user attempts to navigate away from the current page
	const blocker = useBlocker(
		({ currentLocation, nextLocation }) =>
			isDirty && currentLocation.pathname !== nextLocation.pathname,
	);

	useEffect(() => {
		if (blocker.state !== 'blocked') {
			return;
		}

		// Store the pending navigation action in a ref to be used later when the user confirms or cancels the navigation
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
