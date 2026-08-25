import type { ReactNode } from 'react';

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
				<aside
					className="hidden md:flex flex-col shrink-0 border-r border-border bg-sidebar w-[var(--sidebar-width)]"
					aria-label="Session explorer"
				>
					{sidebar}
				</aside>

				{/* Mobile sidebar drawer */}
				{sidebarOpen && (
					<>
						<div
							className="fixed inset-0 z-[var(--z-modal-backdrop)] bg-black/40 md:hidden"
							onClick={onSidebarClose}
							aria-hidden="true"
						/>
						<aside
							className="fixed inset-y-0 left-0 z-[var(--z-dialog)] w-[var(--sidebar-width)] flex flex-col border-r border-border bg-surface-overlay backdrop-blur-md md:hidden"
							aria-label="Session explorer"
							role="dialog"
							aria-modal="true"
						>
							{sidebar}
						</aside>
					</>
				)}

				<main className="flex-1 min-w-0 flex flex-col overflow-hidden">
					{workspace}
				</main>

				{/* Desktop version panel */}
				<aside
					className="hidden lg:flex flex-col shrink-0 border-l border-border bg-surface w-[var(--version-panel-width)]"
					aria-label="Version explorer"
				>
					{versionPanel}
				</aside>

				{/* Mobile / tablet version panel drawer */}
				{versionPanelOpen && (
					<>
						<div
							className="fixed inset-0 z-[var(--z-modal-backdrop)] bg-black/40 lg:hidden"
							onClick={onVersionPanelClose}
							aria-hidden="true"
						/>
						<aside
							className="fixed inset-y-0 right-0 z-[var(--z-dialog)] w-[var(--version-panel-width)] flex flex-col border-l border-border bg-surface-overlay backdrop-blur-md lg:hidden"
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
