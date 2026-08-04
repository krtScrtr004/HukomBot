import { Routes, Route } from 'react-router-dom';
import Login from './pages/login';

function App() {
	return (
		<Routes>
			<Route path="/login" element={<Login />}></Route>
		</Routes>
	);
}

export default App;
