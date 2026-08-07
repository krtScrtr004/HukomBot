interface LoadingSpinnerProps {
	label?: string;
	size?: 'sm' | 'md' | 'lg';
	className?: string;
}

const sizeClasses = {
	sm: 'w-4 h-4 border-2',
	md: 'w-6 h-6 border-2',
	lg: 'w-10 h-10 border-3',
};

export default function LoadingSpinner({
	label = 'Loading',
	size = 'md',
	className = '',
}: LoadingSpinnerProps) {
	return (
		<div
			className={`flex flex-col items-center justify-center gap-2 ${className}`}
			role="status"
			aria-label={label}
		>
			<div
				className={`${sizeClasses[size]} rounded-full border-border border-t-primary animate-spin`}
				aria-hidden="true"
			/>
			{label && (
				<span className="text-sm text-text-secondary sr-only">
					{label}
				</span>
			)}
		</div>
	);
}
