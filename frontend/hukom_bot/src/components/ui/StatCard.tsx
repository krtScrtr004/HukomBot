interface StatCardProps {
	label: string;
	value: number;
	icon?: string;
	className?: string;
}

export default function StatCard({
	label,
	value,
	icon,
	className = '',
}: StatCardProps) {
	return (
		<div
			className={`flex items-center gap-3 p-4 bg-surface rounded-sm border border-border shadow-sm ${className}`}
		>
			{icon && (
				<i
					className={`bi ${icon} text-2xl text-text-secondary`}
					aria-hidden="true"
				/>
			)}
			<div className="flex flex-col">
				<span className="text-text-secondary text-sm uppercase">
					{label}
				</span>
				<span className="text-text-primary font-bold text-xl">
					{value}
				</span>
			</div>
		</div>
	);
}
