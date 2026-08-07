import Logo from '@/components/ui/Logo';
import ThemeToggle from '@/components/ui/ThemeToggle';
import { useWorkspace } from '@/contexts/WorkspaceContext';


interface HeaderProps {
	userName?: string;
	onToggleSidebar?: () => void;
	onToggleVersionPanel?: () => void;
	onSignOut?: () => void;
}

export default function Header({
	userName,
	onToggleSidebar,
	onToggleVersionPanel,
	onSignOut,
}: HeaderProps) {


	return (
		<header
			className="relative h-(--header-height) shrink-0 flex items-center justify-between gap-4 px-4 border-b border-border bg-surface"
			role="banner"
		>
			<section className="flex items-center gap-3 min-w-0">
				{/* Session list toggle button */}
				<button
					type="button"
					onClick={onToggleSidebar}
					className="lg:hidden p-2 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					aria-label="Toggle session explorer"
				>
					<i className="bi bi-list text-xl" aria-hidden="true" />
				</button>
				
				{/* Logo */}
				<Logo className="h-20" />
			</section>

			<section className="flex items-center gap-3 shrink-0">
				{/* User name */}
				{userName && (
					<span className="hidden sm:inline text-sm text-text-secondary truncate max-w-48">
						{userName}
					</span>
				)}

				{/* Analysis version list toggle button */}
				<button
					type="button"
					onClick={onToggleVersionPanel}
					className="lg:hidden p-2 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					aria-label="Toggle version panel"
				>
					<i
						className="bi bi-clock-history text-xl"
						aria-hidden="true"
					/>
				</button>

				{/* Theme toggle button */}
				<ThemeToggle className="right-10 rounded-sm hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary" />

				{/* Logout button */}
				<button
					type="button"
					onClick={onSignOut}
					className="p-2 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					aria-label="Sign out"
				>
					<i
						className="bi bi-box-arrow-right text-xl"
						aria-hidden="true"
					/>
				</button>
			</section>
		</header>
	);
}
