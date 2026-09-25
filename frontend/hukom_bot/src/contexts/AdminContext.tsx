import {
	createContext,
	useCallback,
	useContext,
	useReducer,
	useRef,
	type ReactNode,
} from 'react';
import { useNavigate } from 'react-router-dom';
import { ApiError, isAuthError } from '@/services/apiClient';
import { getDashboardData } from '@/services/adminDashboardService';
import { listUsers, getUserAnalytics } from '@/services/adminUsersService';
import { listDocuments, getDocumentAnalytics } from '@/services/adminDocumentsService';
import type {
	AdminDashboardData,
	AdminDashboardDateRange,
	AdminDocumentListItem,
	AdminDocumentAnalytics,
	AdminUserAnalytics,
	AdminUserListItem,
} from '@/types/admin';
import {
	ADMIN_USERS_PAGE_SIZE,
	ADMIN_DOCUMENTS_PAGE_SIZE,
	ADMIN_USERS_MAX_OFFSET,
	ADMIN_DOCUMENTS_MAX_OFFSET,
} from '@/types/admin';
import type { UploadStatus } from '@/types/workspace';
import { useToast } from '@/contexts/ToastProvider';
import { getAdminErrorMessage } from '@/utils/adminErrors';

interface AdminState {
	dashboard: {
		data: AdminDashboardData | null;
		loading: boolean;
		error: string | null;
	};
	pendingFiles: {
		items: AdminDocumentListItem[];
		loading: boolean;
		error: string | null;
	};
	userAnalytics: {
		data: AdminUserAnalytics | null;
		loading: boolean;
		error: string | null;
	};
	documentAnalytics: {
		data: AdminDocumentAnalytics | null;
		loading: boolean;
		error: string | null;
	};
	users: {
		items: AdminUserListItem[];
		query: string;
		column: string[];
		order: 'ASC' | 'DESC';
		statusFilter: 'all' | 'active' | 'inactive';
		roleFilter: 'all' | AdminUserListItem['role'];
		providerFilter: 'all' | AdminUserListItem['provider'];
		offset: number;
		hasMore: boolean;
		loading: boolean;
		loadingMore: boolean;
		error: string | null;
		forbidden: boolean;
	};
	selectedUserId: string | null;
	editUserModal: { open: boolean; user: AdminUserListItem | null };
	documents: {
		items: AdminDocumentListItem[];
		query: string;
		statusFilter: UploadStatus | 'all';
		uploaderIdFilter: string | null;
		column: string[];
		order: 'ASC' | 'DESC';
		offset: number;
		hasMore: boolean;
		loading: boolean;
		loadingMore: boolean;
		error: string | null;
	};
	approveDialog: { open: boolean; documentId: string | null };
	rejectDialog: { open: boolean; documentId: string | null };
}

type AdminAction =
	| { type: 'SET_DASHBOARD_LOADING'; payload: boolean }
	| { type: 'SET_DASHBOARD_DATA'; payload: AdminDashboardData | null }
	| { type: 'SET_DASHBOARD_ERROR'; payload: string | null }
	| { type: 'DISPATCH_DASHBOARD_UPDATE'; payload: AdminDashboardData }
	| { type: 'SET_USER_ANALYTICS_LOADING'; payload: boolean }
	| { type: 'SET_USER_ANALYTICS_DATA'; payload: AdminUserAnalytics | null }
	| { type: 'SET_USER_ANALYTICS_ERROR'; payload: string | null }
	| { type: 'DISPATCH_USER_ANALYTICS_UPDATE'; payload: AdminUserAnalytics }
	| { type: 'SET_DOCUMENT_ANALYTICS_LOADING'; payload: boolean }
	| { type: 'SET_DOCUMENT_ANALYTICS_DATA'; payload: AdminDocumentAnalytics | null }
	| { type: 'SET_DOCUMENT_ANALYTICS_ERROR'; payload: string | null }
	| { type: 'DISPATCH_DOCUMENT_ANALYTICS_UPDATE'; payload: AdminDocumentAnalytics }
	| { type: 'SET_PENDING_LOADING'; payload: boolean }
	| { type: 'SET_PENDING_FILES'; payload: AdminDocumentListItem[] }
	| { type: 'SET_PENDING_ERROR'; payload: string | null }
	| { type: 'SET_USERS_LOADING'; payload: boolean }
	| { type: 'SET_USERS_LOADING_MORE'; payload: boolean }
	| { type: 'SET_USERS_DATA'; payload: AdminUserListItem[] }
	| { type: 'SET_USERS_HAS_MORE'; payload: boolean }
	| { type: 'SET_USERS_ERROR'; payload: string | null }
	| { type: 'SET_USERS_FORBIDDEN'; payload: boolean }
	| { type: 'SET_USERS_OFFSET'; payload: number }
	| { type: 'SET_USERS_QUERY'; payload: string }
	| { type: 'SET_USERS_STATUS_FILTER'; payload: 'all' | 'active' | 'inactive' }
	| { type: 'SET_USERS_ROLE_FILTER'; payload: 'all' | AdminUserListItem['role'] }
	| { type: 'SET_USERS_PROVIDER_FILTER'; payload: 'all' | AdminUserListItem['provider'] }
	| {
			type: 'SET_USERS_SORT';
			payload: { column: string[]; order: 'ASC' | 'DESC' };
	  }
	| { type: 'PATCH_USER'; payload: AdminUserListItem }
	| { type: 'SELECT_USER'; payload: string | null }
	| { type: 'OPEN_EDIT_USER_MODAL'; payload: AdminUserListItem }
	| { type: 'CLOSE_EDIT_USER_MODAL' }
	| { type: 'SET_DOCS_LOADING'; payload: boolean }
	| { type: 'SET_DOCS_LOADING_MORE'; payload: boolean }
	| { type: 'SET_DOCS_HAS_MORE'; payload: boolean }
	| { type: 'SET_DOCS_DATA'; payload: AdminDocumentListItem[] }
	| { type: 'SET_DOCS_ERROR'; payload: string | null }
	| { type: 'SET_DOCS_OFFSET'; payload: number }
	| { type: 'SET_DOCS_QUERY'; payload: string }
	| { type: 'SET_DOCS_STATUS_FILTER'; payload: UploadStatus | 'all' }
	| {
			type: 'SET_DOCS_SORT';
			payload: { column: string[]; order: 'ASC' | 'DESC' };
	  }
	| { type: 'SET_DOCS_UPLOADER_FILTER'; payload: string | null }
	| { type: 'PATCH_DOCUMENT'; payload: AdminDocumentListItem }
	| { type: 'OPEN_APPROVE_DIALOG'; payload: string }
	| { type: 'CLOSE_APPROVE_DIALOG' }
	| { type: 'OPEN_REJECT_DIALOG'; payload: string }
	| { type: 'CLOSE_REJECT_DIALOG' };

interface AdminContextValue {
	state: AdminState;
	dispatch: React.Dispatch<AdminAction>;
	fetchDashboard: (dateRange?: AdminDashboardDateRange) => Promise<void>;
	fetchPendingFiles: () => Promise<void>;
	fetchUsers: () => Promise<void>;
	fetchUserAnalytics: () => Promise<void>;
	fetchDocumentAnalytics: () => Promise<void>;
	fetchDocuments: () => Promise<void>;
	patchUser: (user: AdminUserListItem) => void;
	patchDocument: (document: AdminDocumentListItem) => void;
	handleAdminApiError: (error: unknown, context: string) => void;
}

export const AdminContext = createContext<AdminContextValue | undefined>(undefined);

const initialState: AdminState = {
	dashboard: { data: null, loading: false, error: null },
	pendingFiles: { items: [], loading: false, error: null },
	userAnalytics: { data: null, loading: false, error: null },
	documentAnalytics: { data: null, loading: false, error: null },
	users: {
		items: [],
		query: '',
		column: ['last_name', 'first_name'],
		order: 'ASC',
		statusFilter: 'all',
		roleFilter: 'all',
		providerFilter: 'all',
		offset: 0,
		hasMore: false,
		loading: false,
		loadingMore: false,
		error: null,
		forbidden: false,
	},
	selectedUserId: null,
	editUserModal: { open: false, user: null },
	documents: {
		items: [],
		query: '',
		statusFilter: 'all',
		uploaderIdFilter: null,
		column: ['created_at'],
		order: 'DESC',
		offset: 0,
		hasMore: false,
		loading: false,
		loadingMore: false,
		error: null,
	},
	approveDialog: { open: false, documentId: null },
	rejectDialog: { open: false, documentId: null },
};

function adminReducer(state: AdminState, action: AdminAction): AdminState {
	switch (action.type) {
		case 'SET_DASHBOARD_LOADING':
			return {
				...state,
				dashboard: { ...state.dashboard, loading: action.payload },
			};
		case 'SET_DASHBOARD_DATA':
			return {
				...state,
				dashboard: { ...state.dashboard, data: action.payload },
			};
		case 'SET_DASHBOARD_ERROR':
			return {
				...state,
				dashboard: { ...state.dashboard, error: action.payload },
			};
		case 'DISPATCH_DASHBOARD_UPDATE':
			return {
				...state,
				dashboard: { ...state.dashboard, data: action.payload },
			};
		case 'SET_USER_ANALYTICS_LOADING':
			return {
				...state,
				userAnalytics: { ...state.userAnalytics, loading: action.payload },
			};
		case 'SET_USER_ANALYTICS_DATA':
			return {
				...state,
				userAnalytics: { ...state.userAnalytics, data: action.payload },
			};
		case 'SET_USER_ANALYTICS_ERROR':
			return {
				...state,
				userAnalytics: { ...state.userAnalytics, error: action.payload },
			};
		case 'DISPATCH_USER_ANALYTICS_UPDATE':
			return {
				...state,
				userAnalytics: { ...state.userAnalytics, data: action.payload },
			};
		case 'SET_DOCUMENT_ANALYTICS_LOADING':
			return { ...state, documentAnalytics: { ...state.documentAnalytics, loading: action.payload } };
		case 'SET_DOCUMENT_ANALYTICS_DATA':
			return { ...state, documentAnalytics: { ...state.documentAnalytics, data: action.payload } };
		case 'SET_DOCUMENT_ANALYTICS_ERROR':
			return { ...state, documentAnalytics: { ...state.documentAnalytics, error: action.payload } };
		case 'DISPATCH_DOCUMENT_ANALYTICS_UPDATE':
			return { ...state, documentAnalytics: { ...state.documentAnalytics, data: action.payload } };
		case 'SET_PENDING_LOADING':
			return {
				...state,
				pendingFiles: { ...state.pendingFiles, loading: action.payload },
			};
		case 'SET_PENDING_FILES':
			return {
				...state,
				pendingFiles: { ...state.pendingFiles, items: action.payload },
			};
		case 'SET_PENDING_ERROR':
			return {
				...state,
				pendingFiles: { ...state.pendingFiles, error: action.payload },
			};
		case 'SET_USERS_LOADING':
			return {
				...state,
				users: { ...state.users, loading: action.payload },
			};
		case 'SET_USERS_LOADING_MORE':
			return {
				...state,
				users: { ...state.users, loadingMore: action.payload },
			};
		case 'SET_USERS_DATA':
			return {
				...state,
				users: { ...state.users, items: action.payload },
			};
		case 'SET_USERS_HAS_MORE':
			return {
				...state,
				users: { ...state.users, hasMore: action.payload },
			};
		case 'SET_USERS_ERROR':
			return {
				...state,
				users: { ...state.users, error: action.payload },
			};
		case 'SET_USERS_FORBIDDEN':
			return {
				...state,
				users: { ...state.users, forbidden: action.payload },
			};
		case 'SET_USERS_OFFSET':
			return {
				...state,
				users: { ...state.users, offset: action.payload },
			};
		case 'SET_USERS_QUERY':
			return {
				...state,
				users: { ...state.users, query: action.payload },
			};
		case 'SET_USERS_STATUS_FILTER':
			return { ...state, users: { ...state.users, statusFilter: action.payload } };
		case 'SET_USERS_ROLE_FILTER':
			return { ...state, users: { ...state.users, roleFilter: action.payload } };
		case 'SET_USERS_PROVIDER_FILTER':
			return { ...state, users: { ...state.users, providerFilter: action.payload } };
		case 'SET_USERS_SORT':
			return {
				...state,
				users: {
					...state.users,
					column: action.payload.column,
					order: action.payload.order,
				},
			};
		case 'PATCH_USER':
			return {
				...state,
				users: {
					...state.users,
					items: state.users.items.map((u) =>
						u.id === action.payload.id ? action.payload : u,
					),
				},
			};
		case 'SELECT_USER':
			return { ...state, selectedUserId: action.payload };
		case 'OPEN_EDIT_USER_MODAL':
			return {
				...state,
				editUserModal: { open: true, user: action.payload },
			};
		case 'CLOSE_EDIT_USER_MODAL':
			return {
				...state,
				editUserModal: { open: false, user: null },
			};
		case 'SET_DOCS_LOADING':
			return {
				...state,
				documents: { ...state.documents, loading: action.payload },
			};
		case 'SET_DOCS_LOADING_MORE':
			return {
				...state,
				documents: { ...state.documents, loadingMore: action.payload },
			};
		case 'SET_DOCS_HAS_MORE':
			return {
				...state,
				documents: { ...state.documents, hasMore: action.payload },
			};
		case 'SET_DOCS_DATA':
			return {
				...state,
				documents: { ...state.documents, items: action.payload },
			};
		case 'SET_DOCS_ERROR':
			return {
				...state,
				documents: { ...state.documents, error: action.payload },
			};
		case 'SET_DOCS_OFFSET':
			return {
				...state,
				documents: { ...state.documents, offset: action.payload },
			};
		case 'SET_DOCS_QUERY':
			return {
				...state,
				documents: { ...state.documents, query: action.payload },
			};
		case 'SET_DOCS_STATUS_FILTER':
			return {
				...state,
				documents: {
					...state.documents,
					statusFilter: action.payload,
				},
			};
		case 'SET_DOCS_SORT':
			return {
				...state,
				documents: {
					...state.documents,
					column: action.payload.column,
					order: action.payload.order,
				},
			};
		case 'SET_DOCS_UPLOADER_FILTER':
			return {
				...state,
				documents: {
					...state.documents,
					uploaderIdFilter: action.payload,
				},
			};
		case 'PATCH_DOCUMENT':
			return {
				...state,
				documents: {
					...state.documents,
					items: state.documents.items.map((d) =>
						d.id === action.payload.id ? action.payload : d,
					),
				},
				pendingFiles: {
					...state.pendingFiles,
					items: state.pendingFiles.items.map((d) =>
						d.id === action.payload.id ? action.payload : d,
					),
				},
			};
		case 'OPEN_APPROVE_DIALOG':
			return {
				...state,
				approveDialog: { open: true, documentId: action.payload },
			};
		case 'CLOSE_APPROVE_DIALOG':
			return {
				...state,
				approveDialog: { open: false, documentId: null },
			};
		case 'OPEN_REJECT_DIALOG':
			return {
				...state,
				rejectDialog: { open: true, documentId: action.payload },
			};
		case 'CLOSE_REJECT_DIALOG':
			return {
				...state,
				rejectDialog: { open: false, documentId: null },
			};
		default:
			return state;
	}
}

export function AdminProvider({ children }: { children: ReactNode }) {
	const [state, dispatch] = useReducer(adminReducer, initialState);
	const navigate = useNavigate();
	const { showToast } = useToast();
	const stateRef = useRef(state);
	stateRef.current = state;
	const initGuard = useRef(false);
	if (!initGuard.current) {
		initGuard.current = true;
	}

	const handleAdminApiError = useCallback(
		(error: unknown, context: string) => {
			if (isAuthError(error)) {
				navigate('/login');
				return;
			}
			void context;
			showToast(getAdminErrorMessage(error), 'error');
		},
		[navigate, showToast],
	);

	const fetchDashboard = useCallback(async (dateRange: AdminDashboardDateRange = 'last_30_days') => {
		dispatch({ type: 'SET_DASHBOARD_LOADING', payload: true });
		try {
			const data = await getDashboardData(dateRange);
			dispatch({ type: 'SET_DASHBOARD_DATA', payload: data });
			dispatch({ type: 'SET_DASHBOARD_ERROR', payload: null });
		} catch (error) {
			dispatch({
				type: 'SET_DASHBOARD_ERROR',
				payload: getAdminErrorMessage(error),
			});
		} finally {
			dispatch({ type: 'SET_DASHBOARD_LOADING', payload: false });
		}
	}, []);

	const fetchPendingFiles = useCallback(async () => {
		dispatch({ type: 'SET_PENDING_LOADING', payload: true });
		try {
			const data = await listDocuments({
				upload_status: 'pending',
				limit: 5,
				column: ['created_at'],
				order: 'DESC',
			});
			dispatch({ type: 'SET_PENDING_FILES', payload: data });
			dispatch({ type: 'SET_PENDING_ERROR', payload: null });
		} catch (error) {
			dispatch({
				type: 'SET_PENDING_ERROR',
				payload: getAdminErrorMessage(error),
			});
		} finally {
			dispatch({ type: 'SET_PENDING_LOADING', payload: false });
		}
	}, []);

	const fetchUsers = useCallback(async () => {
		const { users } = stateRef.current;
		const loadingMore = users.offset > 0;
		dispatch({
			type: loadingMore ? 'SET_USERS_LOADING_MORE' : 'SET_USERS_LOADING',
			payload: true,
		});
		dispatch({ type: 'SET_USERS_FORBIDDEN', payload: false });
		try {
			const data = await listUsers({
				query: users.query || undefined,
				is_active: users.statusFilter === 'all' ? undefined : users.statusFilter === 'active',
				role: users.roleFilter === 'all' ? undefined : users.roleFilter,
				oauth_provider: users.providerFilter === 'all' ? undefined : users.providerFilter,
				limit: ADMIN_USERS_PAGE_SIZE,
				offset: users.offset,
				column: users.column,
				order: users.order,
			});
			dispatch({ type: 'SET_USERS_DATA', payload: data });
			dispatch({ type: 'SET_USERS_ERROR', payload: null });
			dispatch({
				type: 'SET_USERS_HAS_MORE',
				payload:
					data.length === ADMIN_USERS_PAGE_SIZE &&
					users.offset + ADMIN_USERS_PAGE_SIZE <=
						ADMIN_USERS_MAX_OFFSET,
			});
		} catch (error) {
			if (error instanceof ApiError && error.code === 'FORBIDDEN') {
				dispatch({ type: 'SET_USERS_FORBIDDEN', payload: true });
			}
			dispatch({
				type: 'SET_USERS_ERROR',
				payload: getAdminErrorMessage(error),
			});
		} finally {
			dispatch({
				type: loadingMore ? 'SET_USERS_LOADING_MORE' : 'SET_USERS_LOADING',
				payload: false,
			});
		}
	}, []);

	const fetchDocuments = useCallback(async () => {
		const { documents } = stateRef.current;
		const loadingMore = documents.offset > 0;
		dispatch({
			type: loadingMore ? 'SET_DOCS_LOADING_MORE' : 'SET_DOCS_LOADING',
			payload: true,
		});
		try {
			const data = await listDocuments({
				limit: ADMIN_DOCUMENTS_PAGE_SIZE,
				offset: documents.offset,
				query: documents.query || undefined,
				upload_status:
					documents.statusFilter !== 'all'
						? documents.statusFilter
						: undefined,
				uploader_id: documents.uploaderIdFilter || undefined,
				column: documents.column,
				order: documents.order,
			});
			dispatch({ type: 'SET_DOCS_DATA', payload: data });
			dispatch({ type: 'SET_DOCS_ERROR', payload: null });
			dispatch({
				type: 'SET_DOCS_HAS_MORE',
				payload:
					data.length === ADMIN_DOCUMENTS_PAGE_SIZE &&
					documents.offset + ADMIN_DOCUMENTS_PAGE_SIZE <=
						ADMIN_DOCUMENTS_MAX_OFFSET,
			});
		} catch (error) {
			dispatch({
				type: 'SET_DOCS_ERROR',
				payload: getAdminErrorMessage(error),
			});
		} finally {
			dispatch({
				type: loadingMore ? 'SET_DOCS_LOADING_MORE' : 'SET_DOCS_LOADING',
				payload: false,
			});
		}
	}, []);

	const fetchUserAnalytics = useCallback(async () => {
		dispatch({ type: 'SET_USER_ANALYTICS_LOADING', payload: true });
		try {
			const data = await getUserAnalytics();
			dispatch({ type: 'SET_USER_ANALYTICS_DATA', payload: data });
			dispatch({ type: 'SET_USER_ANALYTICS_ERROR', payload: null });
		} catch (error) {
			dispatch({
				type: 'SET_USER_ANALYTICS_ERROR',
				payload: getAdminErrorMessage(error),
			});
		} finally {
			dispatch({ type: 'SET_USER_ANALYTICS_LOADING', payload: false });
		}
	}, []);

	const fetchDocumentAnalytics = useCallback(async () => {
		dispatch({ type: 'SET_DOCUMENT_ANALYTICS_LOADING', payload: true });
		try {
			const data = await getDocumentAnalytics();
			dispatch({ type: 'SET_DOCUMENT_ANALYTICS_DATA', payload: data });
			dispatch({ type: 'SET_DOCUMENT_ANALYTICS_ERROR', payload: null });
		} catch (error) {
			dispatch({ type: 'SET_DOCUMENT_ANALYTICS_ERROR', payload: getAdminErrorMessage(error) });
		} finally {
			dispatch({ type: 'SET_DOCUMENT_ANALYTICS_LOADING', payload: false });
		}
	}, []);

	const patchUser = useCallback((user: AdminUserListItem) => {
		dispatch({ type: 'PATCH_USER', payload: user });
	}, []);

	const patchDocument = useCallback((document: AdminDocumentListItem) => {
		dispatch({ type: 'PATCH_DOCUMENT', payload: document });
	}, []);

	return (
		<AdminContext.Provider
			value={{
				state,
				dispatch,
				fetchDashboard,
				fetchPendingFiles,
				fetchUsers,
				fetchUserAnalytics,
				fetchDocumentAnalytics,
				fetchDocuments,
				patchUser,
				patchDocument,
				handleAdminApiError,
			}}
		>
			{children}
		</AdminContext.Provider>
	);
}

export function useAdmin() {
	const ctx = useContext(AdminContext);
	if (!ctx) throw new Error('useAdmin must be used within AdminProvider');
	return ctx;
}
