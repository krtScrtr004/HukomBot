import { useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { useAdmin } from '@/contexts/AdminContext';
import type { AdminDocumentListItem } from '@/types/admin';
import DataTable, { type DataTableColumn } from '@/components/ui/DataTable';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import ErrorText from '@/components/ui/ErrorText';
import EmptyState from '@/components/workspace/shared/EmptyState';
import FileReviewActions from '@/components/admin/files/FileReviewActions';

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
		{ key: 'original_file_name', header: 'File Name', render: (row) => <span className="font-medium">{row.original_file_name}</span> },
		{ key: 'uploader', header: 'Uploaded By', render: (row) => <span className="text-text-secondary">{formatUploader(row)}</span> },
		{ key: 'created_at', header: 'Upload Date', render: (row) => new Date(row.created_at).toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' }) },
		{ key: 'upload_status', header: 'Status', render: () => <span className="rounded-full bg-warning/10 px-2.5 py-1 text-xs font-medium text-warning">Pending</span> },
		{ key: 'actions', header: 'Actions', render: (row) => <FileReviewActions document={row} /> },
	];

	return <section aria-label="Pending files" className="rounded-sm border border-border bg-surface p-5"><div className="flex flex-col justify-between gap-3 sm:flex-row sm:items-center"><div><h2 className="font-semibold">Pending Files</h2><p className="mt-1 text-xs text-text-secondary">Review the latest uploads awaiting approval</p></div><Link to="/admin/files?status=pending" className="text-sm font-medium text-primary hover:underline">View all <i className="bi bi-arrow-up-right" aria-hidden="true" /></Link></div><div className="mt-5 flex items-center gap-2 rounded-sm border border-border bg-background px-3 py-2 text-sm text-text-muted"><i className="bi bi-search" aria-hidden="true" /><span>Search pending files</span></div><div className="mt-4 overflow-x-auto">{pendingFiles.loading ? <LoadingSpinner label="Loading pending files" /> : pendingFiles.error ? <ErrorText error={pendingFiles.error} onRetry={() => void fetchPendingFiles()} /> : pendingFiles.items.length === 0 ? <EmptyState title="No pending files" /> : <DataTable columns={columns} rows={pendingFiles.items} rowKey={(row) => row.id} loading={false} error={null} emptyMessage="No pending files" />}</div><div className="mt-4 flex items-center justify-between border-t border-border pt-4 text-xs text-text-muted"><span>Showing 1-{Math.min(pendingFiles.items.length, 5)} of {pendingFiles.items.length} items</span><span className="flex gap-1"><button type="button" disabled className="rounded-sm border border-border px-2 py-1 opacity-50" aria-label="Previous page"><i className="bi bi-chevron-left" /></button><button type="button" disabled={pendingFiles.items.length < 5} className="rounded-sm border border-border px-2 py-1" aria-label="Next page"><i className="bi bi-chevron-right" /></button></span></div></section>;
}