import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import Login from '@/pages/Login';


export default function App() {
	return (
		<ThemeProvider>
			<Routes>
				<Route path="/login" element={<Login />}></Route>
			</Routes>
		</ThemeProvider>
	);
}