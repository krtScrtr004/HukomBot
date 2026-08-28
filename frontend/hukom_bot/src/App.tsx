import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { ToastProvider } from '@/contexts/ToastProvider';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import Login from '@/pages/Login';
import Workspace from '@/pages/Workspace';
import type { JSX } from 'react/jsx-runtime';

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
		return <Navigate to="/login" replace />;
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

						{/* Default <Workspace> */}
						<Route
							path="/"
							element={<Navigate to="/workspace" replace />}
						/>
					</Routes>
				</AuthProvider>
			</ToastProvider>
		</ThemeProvider>
	);
}
