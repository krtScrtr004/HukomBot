import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAdmin } from '@/contexts/AdminContext';
import type { AdminDocumentListItem } from '@/types/admin';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import ErrorText from '@/components/ui/ErrorText';
import EmptyState from '@/components/workspace/shared/EmptyState';

function formatUploader(row: AdminDocumentListItem): string {
	if (!row.uploader) return 'Unknown';
	return `${row.uploader.first_name} ${row.uploader.last_name}`;
}

export default function PendingFilesList() {
	const { state, fetchPendingFiles } = useAdmin();
	const { pendingFiles } = state;
	const initRef = useRef(false);

	useEffect(() => {
		if (initRef.current) return;
		initRef.current = true;
		void fetchPendingFiles();
	}, [fetchPendingFiles]);

	const columns: DataTableColumn<AdminDocumentListItem>[] = [
		{
			key: 'original_file_name',
			header: 'File Name',
			render: (row) => row.original_file_name,
		},
		{
			key: 'uploader',
			header: 'Uploaded By',
			render: (row) => formatUploader(row),
		},
		{
			key: 'created_at',
			header: 'Upload Date',
			render: (row) =>
				new Date(row.created_at).toLocaleDateString(undefined, {
					year: 'numeric',
					month: 'short',
					day: 'numeric',
				}),
		},
	];

	return (
		<section aria-label="Pending files preview">
			<h2 className="text-lg font-semibold text-text-primary mb-3">
				Pending Files
			</h2>
			{pendingFiles.loading ? (
				<LoadingSpinner label="Loading pending files" />
			) : pendingFiles.error ? (
				<ErrorText
					error={pendingFiles.error}
					onRetry={() => void fetchPendingFiles()}
				/>
			) : pendingFiles.items.length === 0 ? (
				<EmptyState title="No pending files" />
			) : (
				<DataTable
					columns={columns}
					rows={pendingFiles.items}
					rowKey={(row) => row.id}
					loading={false}
					error={null}
					emptyMessage="No pending files"
				/>
			)}
			<div className="mt-3">
				<Link
					to="/admin/files?status=pending"
					className="text-sm text-primary hover:underline"
				>
					View all pending
				</Link>
			</div>
		</section>
	);
}
