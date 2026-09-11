import { useEffect, useRef, useState } from 'react';
import { useAdmin } from '@/contexts/AdminContext';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import {
	type AdminUserListItem,
	ADMIN_USERS_PAGE_SIZE,
} from '@/types/admin';
import UserDetailPanel from '@/components/admin/users/UserDetailPanel';
import EditUserModal from '@/components/admin/users/EditUserModal';
import EmptyState from '@/components/workspace/shared/EmptyState';
import ErrorText from '@/components/ui/ErrorText';

const SORT_KEY_TO_COLUMNS: Record<string, string[]> = {
	name: ['last_name', 'first_name'],
	email: ['email'],
	role: ['role'],
	created_at: ['created_at'],
};

function columnsToSortKey(column: string[]): string | undefined {
	const joined = column.join(',');
	if (joined === 'last_name,first_name') return 'name';
	return column[0];
}

function formatProvider(provider: AdminUserListItem['provider']): string {
	return provider.charAt(0).toUpperCase() + provider.slice(1);
}

export default function AdminUsersPage() {
	const { state, dispatch, fetchUsers } = useAdmin();
	const { users, selectedUserId, editUserModal } = state;
	const [searchTerm, setSearchTerm] = useState('');
	const fetchRef = useRef(fetchUsers);
	fetchRef.current = fetchUsers;

	useEffect(() => {
		const timer = setTimeout(() => {
			dispatch({ type: 'SET_USERS_QUERY', payload: searchTerm.trim() });
			dispatch({ type: 'SET_USERS_OFFSET', payload: 0 });
		}, 300);
		return () => clearTimeout(timer);
	}, [searchTerm, dispatch]);

	useEffect(() => {
		void fetchRef.current();
	}, [
		users.query,
		users.offset,
		users.column,
		users.order,
	]);

	const selectedUser =
		users.items.find((u) => u.id === selectedUserId) ?? null;

	const tableColumns: DataTableColumn<AdminUserListItem>[] = [
		{
			key: 'name',
			header: 'Name',
			sortable: true,
			render: (row) => `${row.first_name} ${row.last_name}`,
		},
		{
			key: 'email',
			header: 'Email',
			sortable: true,
			render: (row) => row.email,
		},
		{
			key: 'role',
			header: 'Role',
			sortable: true,
			render: (row) => (
				<span className="capitalize">{row.role}</span>
			),
		},
		{
			key: 'provider',
			header: 'Auth Provider',
			render: (row) => formatProvider(row.provider),
		},
		{
			key: 'created_at',
			header: 'Date Registered',
			sortable: true,
			render: (row) =>
				new Date(row.created_at).toLocaleDateString(undefined, {
					year: 'numeric',
					month: 'short',
					day: 'numeric',
				}),
		},
	];

	const handleSortChange = (columnKey: string, order: 'ASC' | 'DESC') => {
		const apiColumns = SORT_KEY_TO_COLUMNS[columnKey] ?? [columnKey];
		dispatch({
			type: 'SET_USERS_SORT',
			payload: { column: apiColumns, order },
		});
		dispatch({ type: 'SET_USERS_OFFSET', payload: 0 });
	};

	if (users.forbidden) {
		return (
			<EmptyState
				icon="bi-shield-lock"
				title="Access denied"
				description="You do not have permission to view the users list."
			/>
		);
	}

	return (
		<div className="space-y-4">
			<h1 className="text-xl font-semibold text-text-primary">Users</h1>

			<input
				type="search"
				placeholder="Search users…"
				value={searchTerm}
				onChange={(e) => setSearchTerm(e.target.value)}
				className="w-full max-w-md border border-border rounded-sm px-3 py-2 text-sm bg-surface"
				aria-label="Search users"
			/>

			<DataTable
				columns={tableColumns}
				rows={users.items}
				rowKey={(row) => row.id}
				loading={users.loading}
				error={users.error}
				emptyMessage="No users found"
				sortColumn={columnsToSortKey(users.column)}
				sortOrder={users.order}
				onSortChange={handleSortChange}
				onRowClick={(row) =>
					dispatch({ type: 'SELECT_USER', payload: row.id })
				}
				onRetry={() => void fetchUsers()}
			/>

			<div className="flex items-center gap-3">
				<button
					type="button"
					disabled={users.offset === 0 || users.loading}
					onClick={() =>
						dispatch({
							type: 'SET_USERS_OFFSET',
							payload: Math.max(
								0,
								users.offset - ADMIN_USERS_PAGE_SIZE,
							),
						})
					}
					className="px-3 py-1.5 text-sm border border-border rounded-sm disabled:opacity-50 hover:bg-hover"
				>
					Previous
				</button>
				<span className="text-sm text-text-secondary">
					Showing {users.offset + 1}–
					{users.offset + users.items.length}
				</span>
				<button
					type="button"
					disabled={!users.hasMore || users.loading}
					onClick={() =>
						dispatch({
							type: 'SET_USERS_OFFSET',
							payload: users.offset + ADMIN_USERS_PAGE_SIZE,
						})
					}
					className="px-3 py-1.5 text-sm border border-border rounded-sm disabled:opacity-50 hover:bg-hover"
				>
					Next
				</button>
			</div>

			{users.error && users.items.length > 0 ? (
				<ErrorText error={users.error} onRetry={() => void fetchUsers()} />
			) : null}

			{selectedUser ? (
				<UserDetailPanel
					user={selectedUser}
					onClose={() =>
						dispatch({ type: 'SELECT_USER', payload: null })
					}
					onEdit={() =>
						dispatch({
							type: 'OPEN_EDIT_USER_MODAL',
							payload: selectedUser,
						})
					}
				/>
			) : null}

			<EditUserModal
				open={editUserModal.open}
				user={editUserModal.user}
				onClose={() => dispatch({ type: 'CLOSE_EDIT_USER_MODAL' })}
			/>
		</div>
	);
}
