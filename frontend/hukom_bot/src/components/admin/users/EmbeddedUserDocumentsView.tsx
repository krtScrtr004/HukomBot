import { useCallback, useEffect, useState } from 'react';
import { listDocuments, getDocumentInfo, deleteDocument } from '@/services/adminDocumentsService';
import type { AdminDocumentListItem } from '@/types/admin';
import type { UploadStatus } from '@/types/workspace';
import { useToast } from '@/contexts/ToastProvider';
import { getAdminErrorMessage } from '@/utils/adminErrors';
import StatusBadge from '@/components/ui/StatusBadge';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import DocumentDetailModal from '@/components/admin/files/DocumentDetailModal';
import ConfirmDialog from '@/components/workspace/shared/ConfirmDialog';

interface EmbeddedUserDocumentsViewProps {
	uploaderId: string;
}

export default function EmbeddedUserDocumentsView({ uploaderId }: EmbeddedUserDocumentsViewProps) {
	const { showToast } = useToast();
	const [documents, setDocuments] = useState<AdminDocumentListItem[]>([]);
	const [isInitialLoad, setIsInitialLoad] = useState(true);
	const [loading, setLoading] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const [searchTerm, setSearchTerm] = useState('');
	const [debouncedQuery, setDebouncedQuery] = useState('');
	const [statusFilter, setStatusFilter] = useState<UploadStatus | 'all'>('all');
	const [offset, setOffset] = useState(0);
	const [hasMore, setHasMore] = useState(false);

	const [deleteTarget, setDeleteTarget] = useState<AdminDocumentListItem | null>(null);
	const [deleting, setDeleting] = useState(false);
	const [selectedDocDetail, setSelectedDocDetail] = useState<AdminDocumentListItem | null>(null);
	const [fetchingDetail, setFetchingDetail] = useState(false);

	const PAGE_SIZE = 10;

	useEffect(() => {
		const timer = setTimeout(() => {
			setDebouncedQuery(searchTerm.trim());
			setOffset(0);
		}, 300);
		return () => clearTimeout(timer);
	}, [searchTerm]);

	const fetchUserDocs = useCallback(async () => {
		if (!uploaderId) return;
		if (documents.length === 0) {
			setLoading(true);
		}
		setError(null);
		try {
			const data = await listDocuments({
				uploader_id: uploaderId,
				query: debouncedQuery || undefined,
				upload_status: statusFilter !== 'all' ? statusFilter : undefined,
				limit: PAGE_SIZE,
				offset,
				column: ['created_at'],
				order: 'DESC',
			});
			setDocuments(data);
			setHasMore(data.length === PAGE_SIZE);
		} catch (err) {
			setError(getAdminErrorMessage(err));
		} finally {
			setLoading(false);
			setIsInitialLoad(false);
		}
	}, [uploaderId, debouncedQuery, statusFilter, offset, documents.length]);

	useEffect(() => {
		void fetchUserDocs();
	}, [fetchUserDocs]);

	const handleRowClick = async (docRow: AdminDocumentListItem) => {
		setFetchingDetail(true);
		try {
			const detail = await getDocumentInfo(docRow.id);
			setSelectedDocDetail(detail);
		} catch {
			setSelectedDocDetail(docRow);
		} finally {
			setFetchingDetail(false);
		}
	};

	const handleDeleteConfirm = async () => {
		if (!deleteTarget) return;
		setDeleting(true);
		try {
			await deleteDocument(deleteTarget.id);
			showToast('Document deleted successfully', 'success');
			setDeleteTarget(null);
			void fetchUserDocs();
		} catch (err) {
			showToast(getAdminErrorMessage(err), 'error');
		} finally {
			setDeleting(false);
		}
	};

	const STATUS_FILTERS: { label: string; value: UploadStatus | 'all'; icon: string }[] = [
		{ label: 'All', value: 'all', icon: 'bi-files' },
		{ label: 'Pending', value: 'pending', icon: 'bi-clock-history' },
		{ label: 'Ongoing', value: 'ongoing', icon: 'bi-gear-wide-connected' },
		{ label: 'Completed', value: 'completed', icon: 'bi-check-circle' },
		{ label: 'Failed', value: 'failed', icon: 'bi-x-circle' },
		{ label: 'Rejected', value: 'rejected', icon: 'bi-slash-circle' },
	];

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

	const columns: DataTableColumn<AdminDocumentListItem>[] = [
		{
			key: 'original_file_name',
			header: 'File Name',
			render: (row) => (
				<div className="flex items-center gap-2.5 min-w-40">
					<i className={`bi ${getFileIcon(row.original_file_name)} text-lg shrink-0`} />
					<div className="flex flex-col min-w-0">
						<span
							className="font-medium text-text-primary group-hover:text-primary transition-colors truncate max-w-xs"
							title={row.original_file_name}
						>
							{row.original_file_name}
						</span>
						<span className="text-[11px] text-text-muted capitalize">
							Type: {row.document_type || 'Unspecified'}
						</span>
					</div>
				</div>
			),
		},
		{
			key: 'created_at',
			header: 'Upload Date',
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
			render: (row) => <StatusBadge status={row.upload_status} />,
		},
		{
			key: 'actions',
			header: 'Actions',
			render: (row) => (
				<button
					type="button"
					onClick={(e) => {
						e.stopPropagation();
						setDeleteTarget(row);
					}}
					className="p-1 rounded text-text-secondary hover:text-danger hover:bg-danger/10 transition-colors"
					title="Delete file"
					aria-label={`Delete ${row.original_file_name}`}
				>
					<i className="bi bi-trash" />
				</button>
			),
		},
	];

	return (
		<div className="flex flex-col h-full space-y-3 overflow-hidden">
			{/* Search & Filter Toolbar */}
			<div className="space-y-2 shrink-0">
				<div className="relative">
					<i className="bi bi-search absolute left-3 top-1/2 -translate-y-1/2 text-text-muted text-xs" />
					<input
						type="search"
						placeholder="Search user's documents by filename…"
						value={searchTerm}
						onChange={(e) => setSearchTerm(e.target.value)}
						className="w-full pl-8 pr-3 py-1.5 border border-border rounded-md text-xs bg-background text-text-primary focus:outline-none focus:ring-1 focus:ring-primary"
						aria-label="Search user documents"
					/>
				</div>

				<div className="flex flex-wrap gap-1.5" role="group" aria-label="Filter documents by status">
					{STATUS_FILTERS.map((f) => (
						<button
							key={f.value}
							type="button"
							onClick={() => {
								setStatusFilter(f.value);
								setOffset(0);
							}}
							className={`px-2 py-0.5 text-[11px] font-medium rounded border flex items-center gap-1 transition-colors ${
								statusFilter === f.value
									? 'bg-primary text-primary-foreground border-primary shadow-xs'
									: 'border-border bg-surface text-text-secondary hover:bg-hover'
							}`}
						>
							<i className={`bi ${f.icon} text-[10px]`} />
							{f.label}
						</button>
					))}
				</div>
			</div>

			{/* Table Content */}
			<div className="flex-1 overflow-y-auto scrollbar-thin">
				{fetchingDetail && (
					<div className="text-xs text-text-muted flex items-center gap-2 py-1">
						<i className="bi bi-arrow-repeat animate-spin" /> Fetching document details…
					</div>
				)}
				<DataTable
					columns={columns}
					rows={documents}
					rowKey={(row) => row.id}
					loading={loading && isInitialLoad}
					error={error}
					emptyMessage="No uploaded documents match criteria."
					onRowClick={(row) => void handleRowClick(row)}
					onRetry={() => void fetchUserDocs()}
				/>
			</div>

			{/* Pagination Footer */}
			<div className="pt-2 border-t border-border shrink-0 flex justify-between items-center text-xs text-text-secondary">
				<span className="font-medium">
					Showing {documents.length > 0 ? offset + 1 : 0}–{offset + documents.length} documents
				</span>

				<div className="flex items-center gap-2">
					<button
						type="button"
						disabled={offset === 0 || loading}
						onClick={() => setOffset((prev) => Math.max(0, prev - PAGE_SIZE))}
						className="px-2.5 py-1 border border-border rounded-md text-xs font-medium disabled:opacity-40 hover:bg-hover transition-colors flex items-center gap-1"
					>
						<i className="bi bi-chevron-left" /> Prev
					</button>
					<button
						type="button"
						disabled={!hasMore || loading}
						onClick={() => setOffset((prev) => prev + PAGE_SIZE)}
						className="px-2.5 py-1 border border-border rounded-md text-xs font-medium disabled:opacity-40 hover:bg-hover transition-colors flex items-center gap-1"
					>
						Next <i className="bi bi-chevron-right" />
					</button>
				</div>
			</div>

			{/* Document Detail & Delete Dialogs */}
			<DocumentDetailModal
				open={!!selectedDocDetail}
				document={selectedDocDetail}
				onClose={() => {
					setSelectedDocDetail(null);
				}}
			/>

			<ConfirmDialog
				open={!!deleteTarget}
				title="Delete Document"
				message={`Are you sure you want to permanently delete "${deleteTarget?.original_file_name}"? This action cannot be undone.`}
				confirmLabel={deleting ? 'Deleting…' : 'Delete Document'}
				variant="danger"
				onConfirm={() => void handleDeleteConfirm()}
				onCancel={() => !deleting && setDeleteTarget(null)}
			/>
		</div>
	);
}