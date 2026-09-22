import type { ReactNode } from 'react';
import Sidebar from '@/components/ui/Sidebar';

interface WorkspaceLayoutProps {
	header: ReactNode;
	sidebar: ReactNode;
	workspace: ReactNode;
	versionPanel: ReactNode;
	sidebarOpen?: boolean;
	versionPanelOpen?: boolean;
	onSidebarClose?: () => void;
	onVersionPanelClose?: () => void;
	className?: string;
}

export default function WorkspaceLayout({
	header,
	sidebar,
	workspace,
	versionPanel,
	sidebarOpen = false,
	versionPanelOpen = false,
	onSidebarClose,
	onVersionPanelClose,
	className,
}: WorkspaceLayoutProps) {
	return (
		<div
			className={`h-dvh flex flex-col bg-background text-text-primary font-sans transition-colors duration-fast ${className ?? ''}`}
		>
			{header}

			<div className="flex flex-1 min-h-0 relative">
				{/* Desktop / tablet sidebar */}
				<Sidebar
					ariaLabel="Session explorer"
					mobileOpen={sidebarOpen}
					onMobileClose={onSidebarClose}
				>
					{sidebar}
				</Sidebar>

				<main className="min-h-0 min-w-0 flex-1 flex flex-col overflow-hidden">
					{workspace}
				</main>

				{/* Desktop version panel */}
				<aside
					className="hidden lg:flex flex-col shrink-0 border-l border-border bg-surface w-(--version-panel-width)"
					aria-label="Version explorer"
				>
					{versionPanel}
				</aside>

				{/* Mobile / tablet version panel drawer */}
				{versionPanelOpen && (
					<>
						<div
							className="fixed inset-0 z-(--z-modal-backdrop) bg-black/40 lg:hidden"
							onClick={onVersionPanelClose}
							aria-hidden="true"
						/>
						<aside
							className="fixed inset-y-0 right-0 z-(--z-dialog) w-(--version-panel-width) flex flex-col border-l border-border bg-surface-overlay backdrop-blur-md lg:hidden"
							aria-label="Version explorer"
							role="dialog"
							aria-modal="true"
						>
							{versionPanel}
						</aside>
					</>
				)}
			</div>
		</div>
	);
}
