import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import Logo from '@/components/ui/Logo';
import Sidebar from '@/components/ui/Sidebar';
import ThemeToggle from '@/components/ui/ThemeToggle';
import { useAuth } from '@/contexts/AuthContext';
import { logout } from '@/services/authService';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
	`flex items-center gap-3 rounded-sm px-3 py-2.5 text-sm font-medium transition-colors ${
		isActive
			? 'bg-primary text-primary-foreground shadow-sm'
			: 'text-text-secondary hover:bg-hover hover:text-text-primary'
	}`;

export default function AdminLayout() {
	const { user } = useAuth();
	const navigate = useNavigate();
	const [sidebarOpen, setSidebarOpen] = useState(false);

	const handleSignOut = async () => {
		await logout();
		navigate('/login');
	};

	return (
		<div className="flex h-dvh bg-background text-text-primary">
			<Sidebar
				ariaLabel="Admin navigation"
				mobileOpen={sidebarOpen}
				onMobileClose={() => setSidebarOpen(false)}
			>
				<AdminSidebarContent
					user={user}
					onSignOut={handleSignOut}
					onNavigate={() => setSidebarOpen(false)}
				/>
			</Sidebar>
			
			<div className="flex min-h-0 min-w-0 overflow-y-auto flex-1 flex-col">
				<header
					className="flex min-h-(--header-height) items-center justify-between gap-4 border-b border-border bg-surface/80 px-4 py-3 backdrop-blur md:px-8"
					role="banner"
				>
					<div className="flex items-center gap-3">
						<button
							type="button"
							onClick={() => setSidebarOpen(true)}
							className="rounded-sm p-2 text-text-secondary hover:bg-hover lg:hidden"
							aria-label="Open admin navigation"
						>
							<i
								className="bi bi-list text-xl"
								aria-hidden="true"
							/>
						</button>

						<div>
							<p className="text-xs font-semibold uppercase tracking-[0.18em] text-primary">
								HukomBot control center
							</p>
							<p className="mt-1 text-sm text-text-secondary">
								Monitor your legal knowledge operations
							</p>
						</div>
					</div>

					<div className="hidden items-center gap-2 text-xs text-text-muted sm:flex">
						<i
							className="bi bi-circle-fill text-[8px] text-success"
							aria-hidden="true"
						/>
						Live system status
					</div>
				</header>

				<main className="min-h-fit flex-1 p-4 md:p-8">
					<Outlet />
				</main>
			</div>
		</div>
	);
}

interface AdminSidebarContentProps {
	user: ReturnType<typeof useAuth>['user'];
	onSignOut: () => Promise<void>;
	onNavigate?: () => void;
}

function AdminSidebarContent({
	user,
	onSignOut,
	onNavigate,
}: AdminSidebarContentProps) {
	return (
		<div className="flex h-full flex-col">
			<section className="shrink-0 border-b border-border p-3">
				<div className="flex items-center justify-between gap-2">
					<Logo className="h-16 w-auto" />
				</div>
			</section>

			<section className="flex-1 overflow-y-auto p-2 scrollbar-thin">
				<nav className="space-y-1" aria-label="Admin navigation">
					{[
						['/admin', 'Dashboard', 'bi-grid-1x2-fill'],
						['/admin/users', 'Users', 'bi-people-fill'],
						[
							'/admin/files',
							'Uploaded Files',
							'bi-file-earmark-text-fill',
						],
					].map(([to, label, icon]) => (
						<NavLink
							key={to}
							to={to}
							end={to === '/admin'}
							onClick={onNavigate}
							className={navLinkClass}
						>
							<i className={`bi ${icon}`} aria-hidden="true" />
							{label}
						</NavLink>
					))}
					<span className="flex items-center gap-3 rounded-sm px-3 py-2.5 text-sm font-medium text-text-muted">
						<i
							className="bi bi-bar-chart-fill"
							aria-hidden="true"
						/>
						Analytics
					</span>
					<span className="flex items-center gap-3 rounded-sm px-3 py-2.5 text-sm font-medium text-text-muted">
						<i className="bi bi-gear-fill" aria-hidden="true" />
						Settings
					</span>
				</nav>
			</section>

			<footer className="mt-auto flex shrink-0 items-center justify-between gap-2 border-t border-border bg-sidebar p-3">
				<div className="flex min-w-0 items-center gap-2.5">
					<span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-neutral-700 text-xs font-semibold text-white">
						{user
							? `${user.first_name[0]}${user.last_name[0]}`
							: '?'}
					</span>
					<div className="min-w-0">
						<p className="truncate text-sm font-semibold">
							{user ? user.first_name : 'User'}
						</p>
						
						<p className="text-xs text-text-secondary">
							Administrator
						</p>
					</div>
				</div>

				<div className="flex items-center">
					<ThemeToggle className="rounded-sm hover:bg-hover" />
					<button
						type="button"
						onClick={() => void onSignOut()}
						className="rounded-sm p-2 text-text-secondary hover:bg-danger/10 hover:text-danger"
						aria-label="Sign out"
					>
						<i
							className="bi bi-box-arrow-right"
							aria-hidden="true"
						/>
					</button>
				</div>
			</footer>
		</div>
	);
}
