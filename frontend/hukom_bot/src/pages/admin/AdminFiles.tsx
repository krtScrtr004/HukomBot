import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { EVENT_BASE_URL_V1 } from '@/services/apiClient';
import { useAdmin } from '@/contexts/AdminContext';
import { deleteDocument, bulkDeleteDocuments } from '@/services/adminDocumentsService';
import ConfirmDialog from '@/components/workspace/shared/ConfirmDialog';
import { useToast } from '@/contexts/ToastProvider';
import { getAdminErrorMessage } from '@/utils/adminErrors';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import DocumentDetailModal from '@/components/admin/files/DocumentDetailModal';
import FileReviewActions from '@/components/admin/files/FileReviewActions';
import type { AdminDocumentAnalytics, AdminDocumentListItem } from '@/types/admin';
import { ADMIN_DOCUMENTS_PAGE_SIZE } from '@/types/admin';
import type { UploadStatus } from '@/types/workspace';

const STATUS_FILTERS: { label: string; value: UploadStatus | 'all'; icon: string }[] = [
	{ label: 'All Files', value: 'all', icon: 'bi-files' },
	{ label: 'Pending Review', value: 'pending', icon: 'bi-clock-history' },
	{ label: 'Processing', value: 'ongoing', icon: 'bi-gear-wide-connected' },
	{ label: 'Completed', value: 'completed', icon: 'bi-check-circle' },
	{ label: 'Failed', value: 'failed', icon: 'bi-x-circle' },
	{ label: 'Rejected', value: 'rejected', icon: 'bi-slash-circle' },
];

const VALID_STATUSES = new Set<UploadStatus>([
	'pending',
	'ongoing',
	'completed',
	'failed',
	'rejected',
]);

function formatUploader(row: AdminDocumentListItem): string {
	if (!row.uploader) return 'Unknown User';
	return `${row.uploader.first_name} ${row.uploader.last_name}`;
}

function emptyMessageForFilter(filter: UploadStatus | 'all'): string {
	if (filter === 'all') return 'No files match your search criteria';
	return `No ${filter} files found`;
}

function getFileIcon(filename: string) {
	const ext = filename.split('.').pop()?.toLowerCase();
	switch (ext) {
		case 'pdf':
			return 'bi-file-earmark-pdf text-danger';
		case 'doc':
		case 'docx':
			return 'bi-file-earmark-word text-info';
		case 'txt':
			return 'bi-file-earmark-text text-text-secondary';
		default:
			return 'bi-file-earmark-code text-primary';
	}
}

function parseDocumentAnalyticsEvent(eventData: string): AdminDocumentAnalytics | null {
	try {
		const parsed: unknown = JSON.parse(eventData.trim());
		if (!parsed || typeof parsed !== 'object') return null;
		const payload = parsed as { success?: unknown; data?: unknown };
		if ('success' in payload) {
			return payload.success === true && payload.data && typeof payload.data === 'object'
				? payload.data as AdminDocumentAnalytics
				: null;
		}
		return parsed as AdminDocumentAnalytics;
	} catch {
		return null;
	}
}

function DocumentAnalytics({ data, loading }: { data: AdminDocumentAnalytics | null; loading: boolean }) {
	if (loading && !data) return <div className="rounded-sm border border-border bg-surface p-8 text-center text-sm text-text-muted">Loading document analytics...</div>;
	if (!data) return null;
	const statuses = Object.entries(data.status_count);
	const monthly = Object.entries(data.monthly_upload_count);
	const monthlyMax = Math.max(...monthly.map(([, value]) => value), 1);
	const types = Object.entries(data.type_count).filter(([, value]) => value > 0).sort(([, a], [, b]) => b - a).slice(0, 8);
	const typeMax = Math.max(...types.map(([, value]) => value), 1);
	return <section className="space-y-4" aria-label="Document analytics">
		<div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
			{[['Total documents', data.total_count, 'bi-file-earmark-text-fill', 'text-primary'], ['New uploads', data.new_upload_count, 'bi-cloud-arrow-up-fill', 'text-info'], ['Pending review', data.status_count.pending, 'bi-hourglass-split', 'text-warning'], ['Processing', data.status_count.ongoing, 'bi-arrow-repeat', 'text-info'], ['Completed', data.status_count.completed, 'bi-check-circle-fill', 'text-success']].map(([label, value, icon, tone]) => <article key={String(label)} className="flex items-center gap-4 rounded-sm border border-border bg-surface p-4 shadow-sm"><span className={`flex h-10 w-10 items-center justify-center rounded-sm bg-hover ${tone}`}><i className={`bi ${icon} text-lg`} /></span><div><p className="text-xs text-text-secondary">{label}</p><p className="mt-1 text-2xl font-semibold">{Number(value).toLocaleString()}</p></div></article>)}
		</div>
		<div className="grid gap-4 xl:grid-cols-[1.25fr_0.75fr]">
			<article className="rounded-sm border border-border bg-surface p-5"><h2 className="font-semibold">Upload activity</h2><p className="mt-1 text-xs text-text-secondary">Monthly document ingestion</p><div className="mt-6 flex h-40 items-end gap-2 border-b border-border">{monthly.map(([month, value]) => <div key={month} className="group flex min-w-0 flex-1 flex-col items-center gap-2"><div className="w-full rounded-t-sm bg-primary/70 group-hover:bg-primary" style={{ height: `${Math.max((value / monthlyMax) * 100, 3)}%` }} title={`${month}: ${value}`} /><span className="text-[10px] text-text-muted">{month.slice(0, 3)}</span></div>)}</div></article>
			<article className="rounded-sm border border-border bg-surface p-5"><h2 className="font-semibold">Status distribution</h2><p className="mt-1 text-xs text-text-secondary">Current document pipeline</p><div className="mt-5 space-y-3">{statuses.map(([status, value]) => <div key={status}><div className="mb-1 flex justify-between text-xs"><span className="capitalize text-text-secondary">{status}</span><strong>{value}</strong></div><div className="h-2 rounded-full bg-hover"><div className={`h-full rounded-full ${status === 'completed' ? 'bg-success' : status === 'pending' ? 'bg-warning' : status === 'failed' || status === 'rejected' ? 'bg-danger' : 'bg-info'}`} style={{ width: `${Math.max((value / Math.max(data.total_count, 1)) * 100, value ? 4 : 0)}%` }} /></div></div>)}</div></article>
		</div>
		<article className="rounded-sm border border-border bg-surface p-5"><h2 className="font-semibold">Documents by type</h2><p className="mt-1 text-xs text-text-secondary">Top legal document categories</p><div className="mt-5 grid gap-x-8 gap-y-3 md:grid-cols-2">{types.map(([type, value]) => <div key={type} className="grid grid-cols-[minmax(7rem,12rem)_1fr_2rem] items-center gap-3 text-xs"><span className="truncate capitalize text-text-secondary">{type.replaceAll('_', ' ')}</span><div className="h-2 rounded-full bg-hover"><div className="h-full rounded-full bg-primary" style={{ width: `${(value / typeMax) * 100}%` }} /></div><strong className="text-right">{value}</strong></div>)}</div></article>
		{data.most_upload_user.length > 0 && <article className="rounded-sm border border-border bg-surface p-5"><div className="flex items-center justify-between"><div><h2 className="font-semibold">Top uploaders</h2><p className="mt-1 text-xs text-text-secondary">Users with the most uploaded documents</p></div><i className="bi bi-trophy text-warning" aria-hidden="true" /></div><div className="mt-5 divide-y divide-border">{data.most_upload_user.slice(0, 10).map((user, index) => <div key={user.id} className="flex items-center gap-3 py-3 first:pt-0 last:pb-0"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">{index + 1}</span><div className="min-w-0 flex-1"><p className="truncate text-sm font-medium">{user.first_name} {user.last_name}</p><p className="truncate text-xs text-text-muted">{user.email}</p></div><strong className="text-sm">{user.upload_count.toLocaleString()}</strong><span className="text-xs text-text-muted">uploads</span></div>)}</div></article>}
	</section>;
}

export default function AdminFilesPage() {
	const { state, dispatch, fetchDocuments, fetchDocumentAnalytics } = useAdmin();
	const { documents, documentAnalytics } = state;
	const { showToast } = useToast();
	const [searchParams, setSearchParams] = useSearchParams();
	const [searchTerm, setSearchTerm] = useState('');
	const [selectedDocument, setSelectedDocument] = useState<AdminDocumentListItem | null>(null);

	// Selection state for bulk actions
	const [selectedIds, setSelectedIds] = useState<string[]>([]);
	const [singleDeleteTarget, setSingleDeleteTarget] = useState<AdminDocumentListItem | null>(null);
	const [bulkDeleteConfirmOpen, setBulkDeleteConfirmOpen] = useState(false);
	const [deleting, setDeleting] = useState(false);
	const [refreshing, setRefreshing] = useState(false);

	const initFromUrlRef = useRef(false);

	const handleManualRefresh = async () => {
		setRefreshing(true);
		try {
			await Promise.all([fetchDocuments(), fetchDocumentAnalytics()]);
		} finally {
			setRefreshing(false);
		}
	};

	useEffect(() => { void fetchDocumentAnalytics(); }, [fetchDocumentAnalytics]);

	useEffect(() => {
		let stream: EventSource | null = null;
		const open = () => {
			if (document.hidden || stream) return;
			stream = new EventSource(`${EVENT_BASE_URL_V1}/admin/documents`, { withCredentials: true });
			stream.onmessage = (event) => {
				const data = parseDocumentAnalyticsEvent(event.data);
				if (data) dispatch({ type: 'DISPATCH_DOCUMENT_ANALYTICS_UPDATE', payload: data });
			};
		};
		open();
		const onVisibility = () => { if (document.hidden) { stream?.close(); stream = null; } else open(); };
		document.addEventListener('visibilitychange', onVisibility);
		return () => { stream?.close(); document.removeEventListener('visibilitychange', onVisibility); };
	}, [dispatch]);

	useEffect(() => {
		if (initFromUrlRef.current) return;
		initFromUrlRef.current = true;

		const statusParam = searchParams.get('status');
		const uploaderParam = searchParams.get('uploader_id');

		if (statusParam && VALID_STATUSES.has(statusParam as UploadStatus)) {
			dispatch({
				type: 'SET_DOCS_STATUS_FILTER',
				payload: statusParam as UploadStatus,
			});
		}
		if (uploaderParam) {
			dispatch({
				type: 'SET_DOCS_UPLOADER_FILTER',
				payload: uploaderParam,
			});
		}
		dispatch({ type: 'SET_DOCS_OFFSET', payload: 0 });
	}, [searchParams, dispatch]);

	// Search Debounce Effect
	useEffect(() => {
		const timer = setTimeout(() => {
			dispatch({ type: 'SET_DOCS_QUERY', payload: searchTerm.trim() });
			dispatch({ type: 'SET_DOCS_OFFSET', payload: 0 });
		}, 300);
		return () => clearTimeout(timer);
	}, [searchTerm, dispatch]);

	useEffect(() => {
		void fetchDocuments();
		setSelectedIds([]);
	}, [
		fetchDocuments,
		documents.offset,
		documents.query,
		documents.statusFilter,
		documents.uploaderIdFilter,
		documents.column,
		documents.order,
	]);

	const handleStatusFilterChange = (value: UploadStatus | 'all') => {
		dispatch({ type: 'SET_DOCS_STATUS_FILTER', payload: value });
		dispatch({ type: 'SET_DOCS_OFFSET', payload: 0 });
		dispatch({ type: 'SET_DOCS_DATA', payload: [] });

		const next = new URLSearchParams(searchParams);
		if (value === 'all') {
			next.delete('status');
		} else {
			next.set('status', value);
		}
		setSearchParams(next, { replace: true });
	};

	const handleSortChange = (columnKey: string, order: 'ASC' | 'DESC') => {
		dispatch({
			type: 'SET_DOCS_SORT',
			payload: { column: [columnKey], order },
		});
		dispatch({ type: 'SET_DOCS_OFFSET', payload: 0 });
	};

	const handleSingleDelete = async () => {
		if (!singleDeleteTarget) return;
		setDeleting(true);
		try {
			await deleteDocument(singleDeleteTarget.id);
			showToast('Document deleted successfully', 'success');
			setSingleDeleteTarget(null);
			setSelectedIds((prev) => prev.filter((id) => id !== singleDeleteTarget.id));
			void fetchDocuments();
			void fetchDocumentAnalytics();
		} catch (error) {
			showToast(getAdminErrorMessage(error), 'error');
		} finally {
			setDeleting(false);
		}
	};

	const handleBulkDelete = async () => {
		if (selectedIds.length === 0) return;
		setDeleting(true);
		try {
			await bulkDeleteDocuments(selectedIds);
			showToast(`${selectedIds.length} document(s) deleted successfully`, 'success');
			setSelectedIds([]);
			setBulkDeleteConfirmOpen(false);
			void fetchDocuments();
			void fetchDocumentAnalytics();
		} catch (error) {
			showToast(getAdminErrorMessage(error), 'error');
		} finally {
			setDeleting(false);
		}
	};

	const allCurrentSelected =
		documents.items.length > 0 &&
		documents.items.every((item) => selectedIds.includes(item.id));

	const toggleSelectAll = () => {
		if (allCurrentSelected) {
			const currentIds = new Set(documents.items.map((i) => i.id));
			setSelectedIds((prev) => prev.filter((id) => !currentIds.has(id)));
		} else {
			const currentIds = documents.items.map((i) => i.id);
			setSelectedIds((prev) => Array.from(new Set([...prev, ...currentIds])));
		}
	};

	const toggleSelectRow = (id: string) => {
		setSelectedIds((prev) =>
			prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id],
		);
	};

	const columns: DataTableColumn<AdminDocumentListItem>[] = [
		{
			key: 'selection',
			header: '',
			render: (row) => (
				<input
					type="checkbox"
					checked={selectedIds.includes(row.id)}
					onChange={(e) => {
						e.stopPropagation();
						toggleSelectRow(row.id);
					}}
					onClick={(e) => e.stopPropagation()}
					className="h-4 w-4 rounded border-border accent-primary cursor-pointer"
					aria-label={`Select ${row.original_file_name}`}
				/>
			),
		},
		{
			key: 'original_file_name',
			header: 'File Name',
			sortable: true,
			render: (row) => (
				<div className="flex items-center gap-3 min-w-50">
					<div className="flex h-9 w-9 items-center justify-center rounded-lg bg-surface-muted border border-border shrink-0">
						<i className={`bi ${getFileIcon(row.original_file_name)} text-lg`} />
					</div>
					<div className="flex flex-col min-w-0">
						<span
							className="font-medium text-text-primary group-hover:text-primary transition-colors truncate max-w-xs sm:max-w-md"
							title={row.original_file_name}
						>
							{row.original_file_name}
						</span>
						<span className="text-[11px] text-text-muted capitalize whitespace-nowrap">
							Type: {row.document_type || 'Unspecified'}
						</span>
					</div>
				</div>
			),
		},
		{
			key: 'uploader',
			header: 'Uploaded By',
			sortable: false,
			render: (row) => {
				const name = formatUploader(row);
				const initials = row.uploader
					? `${row.uploader.first_name?.charAt(0) || ''}${row.uploader.last_name?.charAt(0) || ''}`.toUpperCase()
					: 'U';
				return (
					<div className="flex items-center gap-2 whitespace-nowrap">
						<div className="h-7 w-7 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-xs font-semibold text-primary shrink-0">
							{initials}
						</div>
						<span className="text-xs text-text-secondary font-medium">{name}</span>
					</div>
				);
			},
		},
		{
			key: 'created_at',
			header: 'Upload Date',
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
			key: 'upload_status',
			header: 'Status',
			sortable: true,
			render: (row) => (
				<div className="flex items-center gap-2 whitespace-nowrap">
					<StatusBadge status={row.upload_status} />
					{row.upload_status === 'rejected' && row.rejection_message ? (
						<span
							className="text-text-muted cursor-help"
							title={row.rejection_message}
							aria-label={`Rejection reason: ${row.rejection_message}`}
						>
							<i className="bi bi-info-circle" aria-hidden="true" />
						</span>
					) : null}
				</div>
			),
		},
		{
			key: 'actions',
			header: 'Review Actions',
			render: (row) => (
				<div className="flex items-center gap-2">
					<FileReviewActions document={row} />
					<button
						type="button"
						onClick={(e) => {
							e.stopPropagation();
							setSelectedDocument(row);
						}}
						className="p-1.5 rounded-md text-text-secondary hover:text-primary hover:bg-hover transition-colors"
						title="View Details"
						aria-label={`View details for ${row.original_file_name}`}
					>
						<i className="bi bi-eye text-base" />
					</button>
					<button
						type="button"
						onClick={(e) => {
							e.stopPropagation();
							setSingleDeleteTarget(row);
						}}
						className="p-1.5 rounded-md text-text-secondary hover:text-danger hover:bg-danger/10 transition-colors"
						title="Delete Document"
						aria-label={`Delete ${row.original_file_name}`}
					>
						<i className="bi bi-trash text-base" />
					</button>
				</div>
			),
		},
	];

	return (
		<div className="space-y-4">
			{/* Page Header */}
			<header className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-border pb-4">
				<div>
					<div className="flex items-center gap-2">
						<h1 className="text-2xl font-bold tracking-tight text-text-primary flex items-center gap-2">
							<i className="bi bi-folder-symlink text-primary" /> Knowledge Base Explorer
						</h1>
						<span className="rounded-full bg-primary/10 px-2.5 py-0.5 text-xs font-semibold text-primary">
							RAG Ingestion
						</span>
					</div>
					<p className="text-sm text-text-secondary mt-1">
						Browse uploaded legal documents, review pending files, and track chunking progress.
					</p>
				</div>
			</header>

			<DocumentAnalytics data={documentAnalytics.data} loading={documentAnalytics.loading} />

			<main className="space-y-4">
					<div className="rounded-lg border border-border bg-surface p-5 shadow-xs space-y-4">
						{/* Search Bar & Bulk Actions Toolbar */}
						<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
							<div className="relative flex-1">
								<i className="bi bi-search absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-sm" />
								<input
									type="search"
									placeholder="Search by filename or uploader…"
									value={searchTerm}
									onChange={(e) => setSearchTerm(e.target.value)}
									className="w-full pl-9 pr-3 py-2 border border-border rounded-md text-sm bg-background text-text-primary focus:outline-none focus:ring-2 focus:ring-primary"
									aria-label="Search uploaded documents"
								/>
							</div>

							<div className="flex items-center gap-2 shrink-0">
								<button
									type="button"
									onClick={() => void handleManualRefresh()}
									disabled={refreshing || documents.loading || documentAnalytics.loading}
									className="px-3 py-2 text-xs font-medium border border-border rounded-md bg-background text-text-secondary hover:text-text-primary hover:bg-hover transition-colors flex items-center gap-1.5"
									title="Refresh documents table and analytics stats"
								>
									<i
										className={`bi bi-arrow-clockwise text-sm ${
											refreshing || documents.loading || documentAnalytics.loading ? 'animate-spin' : ''
										}`}
									/>
									<span className="hidden sm:inline">Refresh</span>
								</button>

								{documents.items.length > 0 && (
									<button
										type="button"
										onClick={toggleSelectAll}
										className="px-3 py-2 text-xs font-medium border border-border rounded-md bg-background text-text-secondary hover:text-text-primary hover:bg-hover transition-colors flex items-center gap-1.5"
									>
										<i className={`bi ${allCurrentSelected ? 'bi-check-square-fill text-primary' : 'bi-square'}`} />
										<span>{allCurrentSelected ? 'Deselect Page' : 'Select Page'}</span>
									</button>
								)}

								{selectedIds.length > 0 && (
									<button
										type="button"
										onClick={() => setBulkDeleteConfirmOpen(true)}
										className="px-3 py-2 text-xs font-medium rounded-md bg-danger text-danger-foreground hover:opacity-90 transition-opacity flex items-center gap-1.5 shadow-xs"
									>
										<i className="bi bi-trash" />
										<span>Delete Selected ({selectedIds.length})</span>
									</button>
								)}
							</div>
						</div>

						{/* Status Filter Tab Pills */}
						<div
							className="flex flex-wrap gap-2 pt-2 border-t border-border"
							role="group"
							aria-label="Filter documents by status"
						>
							{STATUS_FILTERS.map((filter) => (
								<button
									key={filter.value}
									type="button"
									onClick={() => handleStatusFilterChange(filter.value)}
									className={`px-3 py-1.5 text-xs font-medium rounded-md border flex items-center gap-1.5 transition-colors ${
										documents.statusFilter === filter.value
											? 'bg-primary text-primary-foreground border-primary shadow-xs'
											: 'border-border text-text-secondary hover:bg-hover'
									}`}
								>
									<i className={`bi ${filter.icon} text-xs`} />
									{filter.label}
								</button>
							))}
						</div>

						{documents.uploaderIdFilter ? (
							<div className="flex items-center gap-2 text-xs text-text-secondary bg-surface-muted border border-border rounded-md px-3 py-1.5 w-fit">
								<i className="bi bi-funnel text-primary" />
								<span>Filtered by uploader: <strong>{documents.uploaderIdFilter}</strong></span>
								<button
									type="button"
									onClick={() => {
										dispatch({ type: 'SET_DOCS_UPLOADER_FILTER', payload: null });
										dispatch({ type: 'SET_DOCS_OFFSET', payload: 0 });
									}}
									className="ml-2 text-text-muted hover:text-text-primary"
								>
									<i className="bi bi-x-lg" />
								</button>
							</div>
						) : null}

						<DataTable
							columns={columns}
							rows={documents.items}
							rowKey={(row) => row.id}
							loading={documents.loading}
							error={documents.error}
							emptyMessage={emptyMessageForFilter(documents.statusFilter)}
							sortColumn={documents.column[0]}
							sortOrder={documents.order}
							onSortChange={handleSortChange}
							onRowClick={(row) => setSelectedDocument(row)}
							onRetry={() => void fetchDocuments()}
						/>

						{/* Pagination Controls */}
						<div className="flex items-center justify-between pt-3 border-t border-border">
							<span className="text-xs text-text-secondary font-medium">
								Showing {documents.items.length > 0 ? documents.offset + 1 : 0}–
								{documents.offset + documents.items.length} files
							</span>

							<div className="flex items-center gap-2">
								<button
									type="button"
									disabled={documents.offset === 0 || documents.loading}
									onClick={() =>
										dispatch({
											type: 'SET_DOCS_OFFSET',
											payload: Math.max(
												0,
												documents.offset - ADMIN_DOCUMENTS_PAGE_SIZE,
											),
										})
									}
									className="px-3 py-1.5 text-xs font-medium border border-border rounded-md disabled:opacity-40 hover:bg-hover transition-colors flex items-center gap-1"
								>
									<i className="bi bi-chevron-left" /> Previous
								</button>
								<button
									type="button"
									disabled={!documents.hasMore || documents.loading}
									onClick={() =>
										dispatch({
											type: 'SET_DOCS_OFFSET',
											payload: documents.offset + ADMIN_DOCUMENTS_PAGE_SIZE,
										})
									}
									className="px-3 py-1.5 text-xs font-medium border border-border rounded-md disabled:opacity-40 hover:bg-hover transition-colors flex items-center gap-1"
								>
									Next <i className="bi bi-chevron-right" />
								</button>
							</div>
						</div>
					</div>
				</main>

			{/* Document Detail & Review Modal */}
			<DocumentDetailModal
				open={!!selectedDocument}
				document={selectedDocument}
				onClose={() => setSelectedDocument(null)}
			/>

			{/* Single Document Delete Dialog */}
			<ConfirmDialog
				open={!!singleDeleteTarget}
				title="Delete Document"
				message={`Are you sure you want to permanently delete "${singleDeleteTarget?.original_file_name}"? This action cannot be undone.`}
				confirmLabel={deleting ? 'Deleting…' : 'Delete Document'}
				variant="danger"
				onConfirm={() => void handleSingleDelete()}
				onCancel={() => !deleting && setSingleDeleteTarget(null)}
			/>

			{/* Bulk Document Delete Dialog */}
			<ConfirmDialog
				open={bulkDeleteConfirmOpen}
				title="Bulk Delete Documents"
				message={`Are you sure you want to permanently delete ${selectedIds.length} selected document(s)? This action cannot be undone.`}
				confirmLabel={deleting ? 'Deleting…' : `Delete ${selectedIds.length} Document(s)`}
				variant="danger"
				onConfirm={() => void handleBulkDelete()}
				onCancel={() => !deleting && setBulkDeleteConfirmOpen(false)}
			/>
		</div>
	);
}
