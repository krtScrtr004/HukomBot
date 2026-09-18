import { useEffect, useRef, useState } from 'react';
import { useAdmin } from '@/contexts/AdminContext';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import {
	type AdminUserListItem,
	ADMIN_USERS_PAGE_SIZE,
} from '@/types/admin';
import AdminUsersChart from '@/components/admin/users/AdminUsersChart';
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

function getRoleBadgeColor(role: string): string {
	switch (role.toLowerCase()) {
		case 'admin':
			return 'bg-warning/15 text-warning border-warning/30';
		case 'contributor':
			return 'bg-info/15 text-info border-info/30';
		default:
			return 'bg-primary/10 text-primary border-primary/20';
	}
}

export default function AdminUsersPage() {
	const { state, dispatch, fetchUsers } = useAdmin();
	const { users, editUserModal } = state;
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

	const tableColumns: DataTableColumn<AdminUserListItem>[] = [
		{
			key: 'name',
			header: 'User',
			sortable: true,
			render: (row) => {
				const initials = `${row.first_name?.charAt(0) || ''}${row.last_name?.charAt(0) || ''}`.toUpperCase() || 'U';
				return (
					<div className="flex items-center gap-3 min-w-[180px]">
						<div className="relative h-9 w-9 rounded-full bg-surface-muted border border-border flex items-center justify-center overflow-hidden shrink-0">
							{row.profile_picture ? (
								<img
									src={row.profile_picture}
									alt={`${row.first_name} ${row.last_name}`}
									className="h-full w-full object-cover"
								/>
							) : (
								<span className="text-xs font-semibold text-text-secondary">{initials}</span>
							)}
						</div>
						<div className="flex flex-col min-w-0">
							<span className="font-medium text-text-primary group-hover:text-primary transition-colors whitespace-nowrap">
								{row.first_name} {row.last_name}
							</span>
							<span className="text-xs text-text-muted whitespace-nowrap">{row.email}</span>
						</div>
					</div>
				);
			},
		},
		{
			key: 'email',
			header: 'Email',
			sortable: true,
			render: (row) => (
				<span className="font-mono text-xs text-text-secondary whitespace-nowrap">{row.email}</span>
			),
		},
		{
			key: 'role',
			header: 'Role',
			sortable: true,
			render: (row) => (
				<span
					className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize whitespace-nowrap ${getRoleBadgeColor(
						row.role,
					)}`}
				>
					{row.role}
				</span>
			),
		},
		{
			key: 'provider',
			header: 'Auth Provider',
			render: (row) => (
				<span className="inline-flex items-center gap-1.5 text-xs text-text-secondary whitespace-nowrap">
					<i className={`bi ${row.provider === 'google' ? 'bi-google' : 'bi-shield-lock'} text-xs text-text-muted`} />
					{formatProvider(row.provider)}
				</span>
			),
		},
		{
			key: 'created_at',
			header: 'Date Registered',
			sortable: true,
			render: (row) => (
				<span className="text-xs text-text-secondary whitespace-nowrap">
					{new Date(row.created_at).toLocaleDateString(undefined, {
						year: 'numeric',
						month: 'short',
						day: 'numeric',
					})}
				</span>
			),
		},
		{
			key: 'actions',
			header: '',
			render: (row) => (
				<button
					type="button"
					onClick={(e) => {
						e.stopPropagation();
						dispatch({ type: 'OPEN_EDIT_USER_MODAL', payload: row });
					}}
					className="p-1.5 rounded-md text-text-secondary hover:text-primary hover:bg-hover transition-colors"
					title="Edit User"
					aria-label={`Edit ${row.first_name} ${row.last_name}`}
				>
					<i className="bi bi-pencil-square text-base" />
				</button>
			),
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
		<div className="space-y-6">
			{/* Page Header */}
			<header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
				<div>
					<div className="flex items-center gap-2">
						<h1 className="text-2xl font-bold tracking-tight text-text-primary">
							User Management
						</h1>
						<span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
							Admin Console
						</span>
					</div>
					<p className="text-sm text-text-secondary mt-1">
						Monitor user registrations, system activity, and edit account credentials.
					</p>
				</div>
			</header>

			{/* Interactive Charts & Stat Cards */}
			<AdminUsersChart />

			{/* Table & Controls Section */}
			<div className="rounded-lg border border-border bg-surface p-5 shadow-xs space-y-4">
				<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
					<div>
						<h2 className="text-lg font-semibold text-text-primary flex items-center gap-2">
							<i className="bi bi-table text-primary" /> Users Directory
						</h2>
						<p className="text-xs text-text-muted mt-0.5">
							Click any user row to view or edit profile details in a modal.
						</p>
					</div>

					<div className="relative w-full sm:w-72">
						<i className="bi bi-search absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-sm" />
						<input
							type="search"
							placeholder="Search by name or email…"
							value={searchTerm}
							onChange={(e) => setSearchTerm(e.target.value)}
							className="w-full pl-9 pr-3 py-2 border border-border rounded-md text-sm bg-background text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
							aria-label="Search users"
						/>
					</div>
				</div>

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
						dispatch({ type: 'OPEN_EDIT_USER_MODAL', payload: row })
					}
					onRetry={() => void fetchUsers()}
				/>

				{/* Pagination Controls */}
				<div className="flex items-center justify-between pt-2 border-t border-border">
					<span className="text-xs text-text-secondary font-medium">
						Showing {users.items.length > 0 ? users.offset + 1 : 0}–
						{users.offset + users.items.length} users
					</span>

					<div className="flex items-center gap-2">
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
							className="px-3 py-1.5 text-xs font-medium border border-border rounded-md disabled:opacity-40 hover:bg-hover transition-colors flex items-center gap-1"
						>
							<i className="bi bi-chevron-left" /> Previous
						</button>
						<button
							type="button"
							disabled={!users.hasMore || users.loading}
							onClick={() =>
								dispatch({
									type: 'SET_USERS_OFFSET',
									payload: users.offset + ADMIN_USERS_PAGE_SIZE,
								})
							}
							className="px-3 py-1.5 text-xs font-medium border border-border rounded-md disabled:opacity-40 hover:bg-hover transition-colors flex items-center gap-1"
						>
							Next <i className="bi bi-chevron-right" />
						</button>
					</div>
				</div>

				{users.error && users.items.length > 0 ? (
					<ErrorText error={users.error} onRetry={() => void fetchUsers()} />
				) : null}
			</div>

			{/* Edit User Modal */}
			<EditUserModal
				open={editUserModal.open}
				user={editUserModal.user}
				onClose={() => dispatch({ type: 'CLOSE_EDIT_USER_MODAL' })}
			/>
		</div>
	);
}
