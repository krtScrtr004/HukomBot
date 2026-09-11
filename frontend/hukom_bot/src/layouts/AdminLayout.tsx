import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import Logo from '@/components/ui/Logo';
import ThemeToggle from '@/components/ui/ThemeToggle';
import { useAuth } from '@/contexts/AuthContext';
import { logout } from '@/services/authService';

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
	`px-3 py-1.5 rounded-sm text-sm font-medium transition-colors ${
		isActive
			? 'bg-primary text-primary-foreground'
			: 'text-text-secondary hover:bg-hover hover:text-text-primary'
	}`;

export default function AdminLayout() {
	const { user } = useAuth();
	const navigate = useNavigate();

	const handleSignOut = async () => {
		await logout();
		navigate('/login');
	};

	return (
		<div className="flex flex-col min-h-screen bg-background text-text-primary">
			<header
				className="shrink-0 flex items-center justify-between gap-4 px-4 border-b border-border bg-surface h-(--header-height)"
				role="banner"
			>
				<section className="flex items-center gap-6 min-w-0">
					<Logo className="h-16" />
					<nav
						className="flex items-center gap-1"
						aria-label="Admin navigation"
					>
						<NavLink to="/admin" end className={navLinkClass}>
							Dashboard
						</NavLink>
						<NavLink to="/admin/users" className={navLinkClass}>
							Users
						</NavLink>
						<NavLink to="/admin/files" className={navLinkClass}>
							Uploaded Files
						</NavLink>
					</nav>
				</section>

				<section className="flex items-center gap-3 shrink-0">
					{user && (
						<span className="hidden sm:inline text-sm text-text-secondary">
							{user.first_name} {user.last_name}
						</span>
					)}
					<ThemeToggle className="rounded-sm hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary" />
					<button
						type="button"
						onClick={() => void handleSignOut()}
						className="px-3 py-1.5 rounded-sm text-sm text-text-secondary border border-border hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					>
						Sign out
					</button>
				</section>
			</header>

			<main className="flex-1 p-4 md:p-6">
				<Outlet />
			</main>
		</div>
	);
}
