import { useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAdmin } from '@/contexts/AdminContext';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import DocumentCard from '@/components/admin/files/DocumentCard';
import AdminFilesSidebar from '@/components/admin/files/AdminFilesSidebar';
import DocumentDetailModal from '@/components/admin/files/DocumentDetailModal';
import FileReviewActions from '@/components/admin/files/FileReviewActions';
import UploadDocumentModal from '@/components/UploadDocumentModal';
import type { AdminDocumentListItem } from '@/types/admin';
import { ADMIN_DOCUMENTS_PAGE_SIZE } from '@/types/admin';
import type { UploadStatus } from '@/types/workspace';

type ViewMode = 'grid' | 'table';

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

export default function AdminFilesPage() {
	const { state, dispatch, fetchDocuments } = useAdmin();
	const { documents } = state;
	const [searchParams, setSearchParams] = useSearchParams();
	const [searchTerm, setSearchTerm] = useState('');
	const [viewMode, setViewMode] = useState<ViewMode>('grid');
	const [selectedDocument, setSelectedDocument] = useState<AdminDocumentListItem | null>(null);
	const [uploadModalOpen, setUploadModalOpen] = useState(false);

	const initFromUrlRef = useRef(false);
	const fetchRef = useRef(fetchDocuments);
	fetchRef.current = fetchDocuments;

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
		void fetchRef.current();
	}, [
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

	const columns: DataTableColumn<AdminDocumentListItem>[] = [
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
				</div>
			),
		},
	];

	return (
		<div className="space-y-6">
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

			{/* 2-Column Knowledge Base & Pipeline Split Layout */}
			<div className="grid gap-6 lg:grid-cols-3 items-start">
				{/* Main Documents Explorer (Left 2 Columns) */}
				<main className="lg:col-span-2 space-y-4">
					<div className="rounded-lg border border-border bg-surface p-5 shadow-xs space-y-4">
						{/* Search Bar & View Mode Switcher */}
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

							{/* View Mode Switcher (Grid vs Table) */}
							<div className="flex items-center gap-1 rounded-md border border-border bg-background p-1 self-end sm:self-auto shrink-0">
								<button
									type="button"
									onClick={() => setViewMode('grid')}
									className={`px-3 py-1.5 rounded-sm text-xs font-medium flex items-center gap-1.5 transition-colors ${
										viewMode === 'grid'
											? 'bg-surface text-primary shadow-xs border border-border'
											: 'text-text-secondary hover:text-text-primary'
									}`}
									title="Grid View"
								>
									<i className="bi bi-grid-fill" /> Grid
								</button>
								<button
									type="button"
									onClick={() => setViewMode('table')}
									className={`px-3 py-1.5 rounded-sm text-xs font-medium flex items-center gap-1.5 transition-colors ${
										viewMode === 'table'
											? 'bg-surface text-primary shadow-xs border border-border'
											: 'text-text-secondary hover:text-text-primary'
									}`}
									title="Table View"
								>
									<i className="bi bi-[#list-task]" /> Table
								</button>
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

						{/* Content Rendering: Grid Mode vs Table Mode */}
						{viewMode === 'grid' ? (
							documents.items.length > 0 ? (
								<div className="grid gap-4 sm:grid-cols-2 pt-2">
									{documents.items.map((doc) => (
										<DocumentCard
											key={doc.id}
											document={doc}
											onSelect={(item) => setSelectedDocument(item)}
										/>
									))}
								</div>
							) : (
								<div className="py-12 text-center text-text-muted text-sm border border-dashed border-border rounded-lg bg-surface-muted">
									<i className="bi bi-folder-x text-3xl text-text-muted block mb-2" />
									{emptyMessageForFilter(documents.statusFilter)}
								</div>
							)
						) : (
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
								onRetry={() => {
									dispatch({ type: 'SET_DOCS_OFFSET', payload: 0 });
									void fetchDocuments();
								}}
							/>
						)}

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

				{/* Sidebar Section (Right 1 Column) */}
				<AdminFilesSidebar />
			</div>

			{/* Document Detail & Review Modal */}
			<DocumentDetailModal
				open={!!selectedDocument}
				document={selectedDocument}
				onClose={() => setSelectedDocument(null)}
			/>

			{/* Upload Document Modal Shortcut */}
			<UploadDocumentModal
				open={uploadModalOpen}
				onClose={() => setUploadModalOpen(false)}
			/>
		</div>
	);
}
