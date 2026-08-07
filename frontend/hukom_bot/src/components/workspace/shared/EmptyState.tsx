interface EmptyStateProps {
	icon?: string;
	title: string;
	description?: string;
	action?: React.ReactNode;
}

export default function EmptyState({
	icon = 'bi-inbox',
	title,
	description,
	action,
}: EmptyStateProps) {
	return (
		<div className="flex flex-col items-center justify-center gap-3 p-8 text-center h-full min-h-48">
			<i
				className={`bi ${icon} text-4xl text-text-muted`}
				aria-hidden="true"
			/>
			<h3 className="text-lg font-semibold text-text-primary">{title}</h3>
			{description && (
				<p className="text-sm text-text-secondary max-w-sm">
					{description}
				</p>
			)}
			{action}
		</div>
	);
}
