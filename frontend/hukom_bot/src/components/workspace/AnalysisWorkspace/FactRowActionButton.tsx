import type { MouseEventHandler } from 'react';

interface FactRowActionButtonProp {
	text: string;
	iconClassName: string;
	className?: string;
	onClick?: MouseEventHandler<HTMLButtonElement>;
}

export default function FactRowActionButton({
	text,
	iconClassName,
	className = '',
	onClick = () => {},
}: FactRowActionButtonProp) {
	return (
		<button
			type="button"
			onClick={onClick}
			className={`text-xs hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm ${className}`}
		>
			<span className="mr-2">
				<i className={`bi ${iconClassName}`} />
			</span>
			{text}
		</button>
	);
}
