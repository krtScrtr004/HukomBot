import type { MouseEvent } from 'react';
import type { CaseAnalysisSessionPreviewResponse } from '@/types/workspace';

interface SessionListItemProps {
	session: CaseAnalysisSessionPreviewResponse;
	isSelected: boolean;
	onSelect: (sessionId: string) => void;
	onDelete: (sessionId: string) => void;
}

function formatRelativeDate(dateStr: string): string {
	const date = new Date(dateStr);
	const now = new Date();
	const diffMs = now.getTime() - date.getTime();
	const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

	if (diffDays === 0) return 'Today';
	if (diffDays === 1) return 'Yesterday';
	if (diffDays < 7) return `${diffDays} days ago`;
	return date.toLocaleDateString(undefined, {
		month: 'short',
		day: 'numeric',
		year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
	});
}

export default function SessionListItem({
	session,
	isSelected,
	onSelect,
	onDelete,
}: SessionListItemProps) {
	const selectedClassName = isSelected
		? 'bg-sidebar-active border border-border-strong'
		: 'hover:bg-sidebar-hover border border-transparent';

	const selectButtonHandler = () =>
		onSelect(session.case_analysis_session_id);

	// Delete button handler
	const deleteButtonHandler = (e: MouseEvent<HTMLButtonElement>) => {
		e.stopPropagation();
		onDelete(session.case_analysis_session_id);
	};

	return (
		<div
			className={`"group relative rounded-sm transition-colors duration-fast ${selectedClassName}`}
		>
			{/* Info section */}
			<button
				type="button"
				onClick={selectButtonHandler}
				className="w-full text-left p-3 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm"
				aria-selected={isSelected}
				role="option"
			>
				{/* Title */}
				<p className="text-sm font-medium text-text-primary truncate pr-6">
					{session.latest_version_title}
				</p>

				<div className="flex items-center gap-2 mt-1 text-xs text-text-muted">
					{/* Version number */}
					<span>v{session.latest_version_number}</span>

					<span aria-hidden="true">·</span>

					{/* Date */}
					<time dateTime={session.updated_at}>
						{formatRelativeDate(session.updated_at)}
					</time>
				</div>
			</button>

			{/* Delete button */}
			<button
				type="button"
				onClick={deleteButtonHandler}
				className="absolute top-2 right-2 p-1 rounded-sm text-text-muted opacity-0 group-hover:opacity-100 hover:text-danger focus:opacity-100 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
				aria-label="Delete session"
			>
				<i className="bi bi-trash text-sm" aria-hidden="true" />
			</button>
		</div>
	);
}
