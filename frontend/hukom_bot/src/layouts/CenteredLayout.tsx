import type LayoutProp from '@/layouts/types/LayoutProp';

export default function CenteredLayout({ children, className }: LayoutProp) {
	return (
		<>
			<div
				className={`h-dvh flex items-center justify-center transition-colors duration-fast ${className ?? ''}`}
			>
				{children}
			</div>
		</>
	);
}