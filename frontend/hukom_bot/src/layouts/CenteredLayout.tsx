import type LayoutProp from '@/layouts/types/LayoutProp';

function CenteredLayout({ children }: LayoutProp) {
	return (
		<>
			<div className="flex items-center justify-center">{children}</div>;
		</>
	);
}

export default CenteredLayout;
