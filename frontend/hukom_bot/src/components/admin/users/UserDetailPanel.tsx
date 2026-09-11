import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { listDocuments } from '@/services/adminDocumentsService';
import type { AdminDocumentListItem, AdminUserListItem } from '@/types/admin';
import StatusBadge from '@/components/ui/StatusBadge';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import ErrorText from '@/components/ui/ErrorText';
import EmptyState from '@/components/workspace/shared/EmptyState';
import { getAdminErrorMessage } from '@/utils/adminErrors';
import { useFocusTrap } from '@/hooks/useFocusTrap';

interface UserDetailPanelProps {
	user: AdminUserListItem;
	onClose: () => void;
	onEdit: () => void;
}

type Tab = 'details' | 'files';

function getInitials(user: AdminUserListItem): string {
	const first = user.first_name.trim().charAt(0) || '';
	const last = user.last_name.trim().charAt(0) || '';
	return `${first}${last}`.toUpperCase() || '?';
}

function formatProvider(provider: AdminUserListItem['provider']): string {
	return provider.charAt(0).toUpperCase() + provider.slice(1);
}

export default function UserDetailPanel({
	user,
	onClose,
	onEdit,
}: UserDetailPanelProps) {
	const [activeTab, setActiveTab] = useState<Tab>('details');
	const [files, setFiles] = useState<AdminDocumentListItem[]>([]);
	const [filesLoading, setFilesLoading] = useState(false);
	const [filesError, setFilesError] = useState<string | null>(null);
	const [avatarBroken, setAvatarBroken] = useState(false);
	const panelRef = useRef<HTMLElement>(null);
	useFocusTrap(panelRef, true);

	useEffect(() => {
		setAvatarBroken(false);
		setActiveTab('details');
	}, [user.id]);

	useEffect(() => {
		if (activeTab !== 'files') return;
		const fetchFiles = async () => {
			setFilesLoading(true);
			setFilesError(null);
			try {
				const data = await listDocuments({
					uploader_id: user.id,
					limit: 5,
					column: ['created_at'],
					order: 'DESC',
				});
				setFiles(data);
			} catch (error) {
				setFilesError(getAdminErrorMessage(error));
			} finally {
				setFilesLoading(false);
			}
		};
		void fetchFiles();
	}, [activeTab, user.id]);

	useEffect(() => {
		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape') onClose();
		};
		document.addEventListener('keydown', handleKey);
		return () => document.removeEventListener('keydown', handleKey);
	}, [onClose]);

	const showAvatar =
		user.profile_picture && !avatarBroken ? user.profile_picture : null;

	return (
		<div className="fixed inset-0 z-(--z-dialog) flex justify-end">
			<div
				className="absolute inset-0 bg-black/40"
				onClick={onClose}
				aria-hidden="true"
			/>
			<aside
				ref={panelRef}
				role="dialog"
				aria-modal="true"
				aria-labelledby="user-detail-title"
				className="relative z-10 w-full max-w-md h-full bg-surface border-l border-border shadow-lg flex flex-col overflow-hidden"
			>
				<header className="flex items-center justify-between p-4 border-b border-border shrink-0">
					<h2
						id="user-detail-title"
						className="text-lg font-semibold text-text-primary"
					>
						User Details
					</h2>
					<button
						type="button"
						onClick={onClose}
						className="p-1 rounded-sm text-text-muted hover:text-text-primary"
						aria-label="Close user details"
					>
						<i className="bi bi-x-lg" aria-hidden="true" />
					</button>
				</header>

				<div className="p-4 border-b border-border shrink-0">
					<div className="flex items-center gap-4">
						{showAvatar ? (
							<img
								src={showAvatar}
								alt=""
								className="w-16 h-16 rounded-full object-cover border border-border"
								onError={() => setAvatarBroken(true)}
							/>
						) : (
							<div
								className="w-16 h-16 rounded-full bg-primary/10 text-primary flex items-center justify-center text-lg font-semibold"
								aria-hidden="true"
							>
								{getInitials(user)}
							</div>
						)}
						<div>
							<p className="font-semibold text-text-primary">
								{user.first_name} {user.last_name}
							</p>
							<p className="text-sm text-text-secondary">
								{user.email}
							</p>
							<span className="inline-block mt-1 px-2 py-0.5 text-xs rounded bg-primary/10 text-primary capitalize">
								{user.role}
							</span>
						</div>
					</div>
					<button
						type="button"
						onClick={onEdit}
						className="mt-4 w-full px-4 py-2 text-sm rounded-sm border border-border hover:bg-hover"
					>
						Edit
					</button>
				</div>

				<div
					className="flex border-b border-border shrink-0"
					role="tablist"
				>
					<button
						type="button"
						role="tab"
						aria-selected={activeTab === 'details'}
						onClick={() => setActiveTab('details')}
						className={`flex-1 px-4 py-2 text-sm ${activeTab === 'details' ? 'border-b-2 border-primary text-primary font-medium' : 'text-text-secondary'}`}
					>
						Details
					</button>
					<button
						type="button"
						role="tab"
						aria-selected={activeTab === 'files'}
						onClick={() => setActiveTab('files')}
						className={`flex-1 px-4 py-2 text-sm ${activeTab === 'files' ? 'border-b-2 border-primary text-primary font-medium' : 'text-text-secondary'}`}
					>
						Uploaded Files
					</button>
				</div>

				<div className="flex-1 overflow-y-auto p-4">
					{activeTab === 'details' ? (
						<dl className="space-y-3 text-sm">
							<div>
								<dt className="text-text-muted">Email</dt>
								<dd className="text-text-primary">{user.email}</dd>
							</div>
							<div>
								<dt className="text-text-muted">Role</dt>
								<dd className="text-text-primary capitalize">
									{user.role}
								</dd>
							</div>
							<div>
								<dt className="text-text-muted">Auth Provider</dt>
								<dd className="text-text-primary">
									{formatProvider(user.provider)}
								</dd>
							</div>
							<div>
								<dt className="text-text-muted">Date Registered</dt>
								<dd className="text-text-primary">
									{new Date(user.created_at).toLocaleDateString(
										undefined,
										{
											year: 'numeric',
											month: 'long',
											day: 'numeric',
										},
									)}
								</dd>
							</div>
						</dl>
					) : filesLoading ? (
						<LoadingSpinner label="Loading uploaded files" />
					) : filesError ? (
						<ErrorText error={filesError} />
					) : files.length === 0 ? (
						<EmptyState title="This user hasn't uploaded any files" />
					) : (
						<div className="space-y-3">
							<ul className="space-y-2">
								{files.map((file) => (
									<li
										key={file.id}
										className="p-3 rounded-sm border border-border text-sm"
									>
										<p className="font-medium text-text-primary truncate">
											{file.original_file_name}
										</p>
										<div className="flex items-center justify-between mt-1 gap-2">
											<span className="text-text-muted text-xs">
												{new Date(
													file.created_at,
												).toLocaleDateString()}
											</span>
											<StatusBadge
												status={file.upload_status}
											/>
										</div>
									</li>
								))}
							</ul>
							{files.length === 5 ? (
								<p className="text-xs text-text-muted">
									Showing 5 most recent
								</p>
							) : null}
							<Link
								to={`/admin/files?uploader_id=${user.id}`}
								className="text-sm text-primary hover:underline"
							>
								View all in Uploaded Files
							</Link>
						</div>
					)}
				</div>
			</aside>
		</div>
	);
}
