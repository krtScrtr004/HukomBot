import type { CaseAnalysisVersionPreviewResponse } from '@/types/workspace';

interface VersionListItemProps {
	version: CaseAnalysisVersionPreviewResponse;
	isSelected: boolean;
	onSelect: (versionNumber: number) => void;
}

export default function VersionListItem({
	version,
	isSelected,
	onSelect,
}: VersionListItemProps) {
	const formattedDate = new Date(version.created_at).toLocaleString(
		undefined,
		{
			month: 'short',
			day: 'numeric',
			year: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
		},
	);

	return (
		<button
			type="button"
			onClick={() => onSelect(version.version_number)}
			className={`w-full text-left p-3 rounded-sm transition-colors duration-fast focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
				isSelected
					? 'bg-sidebar-active border border-border-strong'
					: 'hover:bg-hover border border-transparent'
			}`}
			aria-selected={isSelected}
			role="option"
		>
			<p className="text-sm font-medium text-text-primary truncate">
				{version.title}
			</p>
			<div className="flex items-center gap-2 mt-1 text-xs text-text-secondary">
				<span>Version {version.version_number}</span>
				<span aria-hidden="true">·</span>
				<time dateTime={version.created_at}>{formattedDate}</time>
			</div>
		</button>
	);
}
