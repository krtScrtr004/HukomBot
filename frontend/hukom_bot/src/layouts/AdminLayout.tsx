import { useState } from 'react';
import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import Logo from '@/components/ui/Logo';
import Sidebar from '@/components/ui/Sidebar';
import ThemeToggle from '@/components/ui/ThemeToggle';
import Header from '@/components/workspace/Header';
import UploadDocumentModal from '@/components/UploadDocumentModal';
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
	const [uploadModalOpen, setUploadModalOpen] = useState(false);

	const handleSignOut = async () => {
		await logout();
		navigate('/login');
	};

	return (
		<div className="flex h-dvh flex-col bg-background text-text-primary">
			<Header
				userRole={user?.role}
				onToggleSidebar={() => setSidebarOpen(true)}
				onUploadClick={() => setUploadModalOpen(true)}
			/>

			<div className="relative flex min-h-0 min-w-0 flex-1">
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

				<main className="min-h-0 min-w-0 flex-1 overflow-y-auto p-4 md:p-8">
					<Outlet />
				</main>
			</div>

			<UploadDocumentModal
				open={uploadModalOpen}
				onClose={() => setUploadModalOpen(false)}
			/>
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
		<div className="flex h-full flex-col pt-3">
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
