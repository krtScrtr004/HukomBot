// src/App.tsx
import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ToastProvider } from '@/contexts/ToastProvider';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import Login from '@/pages/login';
import Workspace from '@/pages/Workspace';
import type { JSX } from 'react/jsx-runtime';
import { AdminProvider } from '@/contexts/AdminContext';
import AdminLayout from '@/layouts/AdminLayout';
import AdminDashboardPage from '@/pages/admin/AdminDashboard';
import AdminUsersPage from '@/pages/admin/AdminUsers';
import AdminFilesPage from '@/pages/admin/AdminFiles';

function RequireAuth({
	children,
	allowedRoles,
}: {
	children: JSX.Element;
	allowedRoles: string[];
}) {
	const { user, loading } = useAuth();
	if (loading) {
		return <LoadingSpinner label="Checking authentication" size="lg" />;
	}
	if (!user) {
		return <Navigate to="/login" replace />;
	}
	if (!allowedRoles.includes(user.role)) {
		// Wrong role – redirect to workspace as spec requires.
		return <Navigate to="/workspace" replace />;
	}
	return children;
}

export default function App() {
	return (
		<ThemeProvider>
			<ToastProvider>
				<AuthProvider>
					<Routes>
						{/* Login */}
						<Route path="/login" element={<Login />} />

						{/* Workspace */}
						<Route
							path="/workspace"
							element={
								<RequireAuth
									allowedRoles={['standard', 'contributor']}
								>
									<Workspace />
								</RequireAuth>
							}
						/>

						{/* Default redirect to workspace */}
						<Route
							path="/"
							element={<Navigate to="/workspace" replace />}
						/>

						{/* Admin routes */}
						<Route
							path="/admin/*"
							element={
								<RequireAuth allowedRoles={['admin']}>
									<AdminProvider>
										<AdminLayout />
									</AdminProvider>
								</RequireAuth>
							}
						>
							<Route index element={<AdminDashboardPage />} />
							<Route path="users" element={<AdminUsersPage />} />
							<Route path="files" element={<AdminFilesPage />} />
						</Route>
					</Routes>
				</AuthProvider>
			</ToastProvider>
		</ThemeProvider>
	);
}
