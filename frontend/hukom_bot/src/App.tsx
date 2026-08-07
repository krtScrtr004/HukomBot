import { Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import Login from '@/pages/Login';
import Workspace from '@/pages/Workspace';


export default function App() {
	return (
		<ThemeProvider>
			<Routes>
				<Route path="/login" element={<Login />} />
				<Route path="/workspace" element={<Workspace />} />
				<Route path="/" element={<Navigate to="/workspace" replace />} />
			</Routes>
		</ThemeProvider>
	);
}