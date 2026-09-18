import type { AdminDocumentListItem } from '@/types/admin';
import StatusBadge from '@/components/ui/StatusBadge';
import FileReviewActions from '@/components/admin/files/FileReviewActions';

interface DocumentCardProps {
	document: AdminDocumentListItem;
	onSelect: (doc: AdminDocumentListItem) => void;
}

function getFileFormatBadge(filename: string) {
	const ext = filename.split('.').pop()?.toUpperCase() || 'FILE';
	switch (ext) {
		case 'PDF':
			return { label: 'PDF', bg: 'bg-danger/10 text-danger border-danger/20', icon: 'bi-file-earmark-pdf-fill' };
		case 'DOC':
		case 'DOCX':
			return { label: 'DOCX', bg: 'bg-info/10 text-info border-info/20', icon: 'bi-file-earmark-word-fill' };
		case 'TXT':
			return { label: 'TXT', bg: 'bg-secondary/10 text-text-secondary border-border', icon: 'bi-file-earmark-text-fill' };
		default:
			return { label: ext, bg: 'bg-primary/10 text-primary border-primary/20', icon: 'bi-file-earmark-code-fill' };
	}
}

function formatUploaderName(row: AdminDocumentListItem): string {
	if (!row.uploader) return 'Unknown User';
	return `${row.uploader.first_name} ${row.uploader.last_name}`;
}

export default function DocumentCard({ document: doc, onSelect }: DocumentCardProps) {
	const format = getFileFormatBadge(doc.original_file_name);
	const uploaderName = formatUploaderName(doc);
	const initials = doc.uploader
		? `${doc.uploader.first_name?.charAt(0) || ''}${doc.uploader.last_name?.charAt(0) || ''}`.toUpperCase()
		: 'U';

	return (
		<div
			onClick={() => onSelect(doc)}
			className="group relative flex flex-col justify-between rounded-lg border border-border bg-surface p-4 shadow-xs transition-all hover:border-primary/50 hover:shadow-md cursor-pointer"
		>
			<div>
				{/* Top Card Header: Format badge & Status */}
				<div className="flex items-center justify-between gap-2 border-b border-border/50 pb-3">
					<span
						className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-bold border uppercase tracking-wider ${format.bg}`}
					>
						<i className={`bi ${format.icon}`} />
						{format.label}
					</span>
					<StatusBadge status={doc.upload_status} />
				</div>

				{/* File Name & Main Info */}
				<div className="mt-3.5 flex items-start gap-3">
					<div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-surface-muted border border-border text-primary group-hover:bg-primary/10 transition-colors">
						<i className={`bi ${format.icon} text-xl`} />
					</div>
					<div className="min-w-0 flex-1">
						<h3
							className="font-semibold text-text-primary text-sm line-clamp-2 leading-snug group-hover:text-primary transition-colors"
							title={doc.original_file_name}
						>
							{doc.original_file_name}
						</h3>
						<span className="mt-1 inline-block text-[11px] font-medium text-text-muted capitalize">
							{doc.document_type || 'Unspecified Category'}
						</span>
					</div>
				</div>

				{/* Rejection Message if rejected */}
				{doc.upload_status === 'rejected' && doc.rejection_message ? (
					<p className="mt-2.5 rounded-md bg-danger/5 border border-danger/20 p-2 text-xs text-danger line-clamp-2">
						<i className="bi bi-exclamation-circle mr-1" />
						{doc.rejection_message}
					</p>
				) : null}
			</div>

			{/* Card Footer: Uploader & Action Buttons */}
			<div className="mt-4 pt-3 border-t border-border/60 flex items-center justify-between text-xs gap-2">
				<div className="flex items-center gap-2 min-w-0">
					<div className="h-6 w-6 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-[10px] font-bold text-primary shrink-0">
						{initials}
					</div>
					<span className="text-text-secondary text-xs truncate max-w-[110px]" title={uploaderName}>
						{uploaderName}
					</span>
				</div>

				<div className="flex items-center gap-1.5 shrink-0" onClick={(e) => e.stopPropagation()}>
					<FileReviewActions document={doc} />
					<button
						type="button"
						onClick={() => onSelect(doc)}
						className="p-1.5 rounded-md text-text-secondary hover:text-primary hover:bg-hover transition-colors"
						title="Inspect document"
					>
						<i className="bi bi-eye text-base" />
					</button>
				</div>
			</div>
		</div>
	);
}

