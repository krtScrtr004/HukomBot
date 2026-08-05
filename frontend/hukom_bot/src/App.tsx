import { Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import Login from '@/pages/Login';


function App() {
	return (
		<ThemeProvider>
			<Routes>
				<Route path="/login" element={<Login />}></Route>
			</Routes>
		</ThemeProvider>
	);
}

export default App;
