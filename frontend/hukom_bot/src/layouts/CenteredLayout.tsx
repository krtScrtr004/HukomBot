import type LayoutProp from '@/layouts/types/LayoutProp';

function CenteredLayout({ children, className }: LayoutProp) {
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

export default CenteredLayout;
