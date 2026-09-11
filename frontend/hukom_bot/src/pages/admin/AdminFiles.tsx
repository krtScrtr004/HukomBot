import { useEffect, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useAdmin } from '@/contexts/AdminContext';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import StatusBadge from '@/components/ui/StatusBadge';
import FileReviewActions from '@/components/admin/files/FileReviewActions';
import type { AdminDocumentListItem } from '@/types/admin';
import {
	ADMIN_DOCUMENTS_PAGE_SIZE,
} from '@/types/admin';
import type { UploadStatus } from '@/types/workspace';

const STATUS_FILTERS: { label: string; value: UploadStatus | 'all' }[] = [
	{ label: 'All', value: 'all' },
	{ label: 'Pending', value: 'pending' },
	{ label: 'Ongoing', value: 'ongoing' },
	{ label: 'Completed', value: 'completed' },
	{ label: 'Failed', value: 'failed' },
	{ label: 'Rejected', value: 'rejected' },
];

const VALID_STATUSES = new Set<UploadStatus>([
	'pending',
	'ongoing',
	'completed',
	'failed',
	'rejected',
]);

function formatUploader(row: AdminDocumentListItem): string {
	if (!row.uploader) return 'Unknown';
	return `${row.uploader.first_name} ${row.uploader.last_name}`;
}

function emptyMessageForFilter(filter: UploadStatus | 'all'): string {
	if (filter === 'all') return 'No files match your search';
	return `No ${filter} files`;
}

export default function AdminFilesPage() {
	const { state, dispatch, fetchDocuments } = useAdmin();
	const { documents } = state;
	const [searchParams, setSearchParams] = useSearchParams();
	const initFromUrlRef = useRef(false);
	const fetchRef = useRef(fetchDocuments);
	fetchRef.current = fetchDocuments;

	useEffect(() => {
		if (initFromUrlRef.current) return;
		initFromUrlRef.current = true;

		const statusParam = searchParams.get('status');
		const uploaderParam = searchParams.get('uploader_id');

		if (
			statusParam &&
			VALID_STATUSES.has(statusParam as UploadStatus)
		) {
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

	useEffect(() => {
		void fetchRef.current();
	}, [
		documents.offset,
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

	// DocumentResponse has only created_at — no updated_at field in the API.
	const columns: DataTableColumn<AdminDocumentListItem>[] = [
		{
			key: 'original_file_name',
			header: 'File Name',
			sortable: true,
			render: (row) => row.original_file_name,
		},
		{
			key: 'uploader',
			header: 'Uploaded By',
			sortable: false,
			render: (row) => formatUploader(row),
		},
		{
			key: 'created_at',
			header: 'Upload Date',
			sortable: true,
			render: (row) =>
				new Date(row.created_at).toLocaleDateString(undefined, {
					year: 'numeric',
					month: 'short',
					day: 'numeric',
				}),
		},
		{
			key: 'upload_status',
			header: 'Status',
			sortable: true,
			render: (row) => (
				<div className="flex items-center gap-2">
					<StatusBadge status={row.upload_status} />
					{row.upload_status === 'rejected' &&
					row.rejection_message ? (
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
			header: 'Actions',
			render: (row) => <FileReviewActions document={row} />,
		},
	];

	return (
		<div className="space-y-4">
			<h1 className="text-xl font-semibold text-text-primary">
				Uploaded Files
			</h1>

			<div
				className="flex flex-wrap gap-2"
				role="group"
				aria-label="Filter by status"
			>
				{STATUS_FILTERS.map((filter) => (
					<button
						key={filter.value}
						type="button"
						onClick={() => handleStatusFilterChange(filter.value)}
						className={`px-3 py-1.5 text-sm rounded-sm border transition-colors ${
							documents.statusFilter === filter.value
								? 'bg-primary text-primary-foreground border-primary'
								: 'border-border text-text-secondary hover:bg-hover'
						}`}
					>
						{filter.label}
					</button>
				))}
			</div>

			{documents.uploaderIdFilter ? (
				<p className="text-sm text-text-secondary">
					Filtered by uploader ID: {documents.uploaderIdFilter}
				</p>
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
				onRetry={() => {
					dispatch({ type: 'SET_DOCS_OFFSET', payload: 0 });
					void fetchDocuments();
				}}
			/>

			<div className="flex items-center gap-3">
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
					className="px-3 py-1.5 text-sm border border-border rounded-sm disabled:opacity-50 hover:bg-hover"
				>
					Previous
				</button>
				<span className="text-sm text-text-secondary">
					Showing {documents.offset + 1}–
					{documents.offset + documents.items.length}
				</span>
				<button
					type="button"
					disabled={!documents.hasMore || documents.loading}
					onClick={() =>
						dispatch({
							type: 'SET_DOCS_OFFSET',
							payload:
								documents.offset + ADMIN_DOCUMENTS_PAGE_SIZE,
						})
					}
					className="px-3 py-1.5 text-sm border border-border rounded-sm disabled:opacity-50 hover:bg-hover"
				>
					Next
				</button>
			</div>
		</div>
	);
}
