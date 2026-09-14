import type { ReactNode } from 'react';

interface SidebarProps {
	children: ReactNode;
	ariaLabel: string;
	mobileOpen?: boolean;
	onMobileClose?: () => void;
	className?: string;
}

export default function Sidebar({
	children,
	ariaLabel,
	mobileOpen = false,
	onMobileClose,
	className = '',
}: SidebarProps) {
	return (
		<>
			<aside
				className={`hidden h-full w-(--sidebar-width) shrink-0 flex-col border-r border-border bg-sidebar lg:flex ${className}`}
				aria-label={ariaLabel}
			>
				{children}
			</aside>

			{mobileOpen && (
				<>
					<div
						className="fixed inset-0 z-(--z-modal-backdrop) bg-black/40 lg:hidden"
						onClick={onMobileClose}
						aria-hidden="true"
					/>
					<aside
						className={`fixed inset-y-0 left-0 z-(--z-dialog) flex w-(--sidebar-width) flex-col border-r border-border bg-surface-overlay backdrop-blur-md lg:hidden ${className}`}
						aria-label={ariaLabel}
						role="dialog"
						aria-modal="true"
					>
						{children}
					</aside>
				</>
			)}
		</>
	);
}