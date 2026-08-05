import {
	createContext,
	useState,
	useEffect,
	useCallback,
	useContext,
} from 'react';

type Theme = 'light' | 'dark';

// ThemeContext.tsx
const ThemeContext = createContext<{
	theme: Theme;
	toggleTheme: () => void;
} | null>(null);

function isValidTheme(value: string | null): value is Theme {
	return value === 'light' || value === 'dark';
}

export function ThemeProvider({ children }: { children: React.ReactNode }) {
	const [theme, setTheme] = useState<Theme>(() => {
		const stored = localStorage.getItem('theme');
		if (isValidTheme(stored)) {
			return stored;
		}
		return 'light';
	});

    // Update the document's data-theme attribute and localStorage whenever the theme changes
	useEffect(() => {
		document.documentElement.setAttribute('data-theme', theme);
		localStorage.setItem('theme', theme);
	}, [theme]);

	const toggleTheme = useCallback(() => {
		setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
	}, []);

	return (
		<ThemeContext.Provider value={{ theme, toggleTheme }}>
			{children}
		</ThemeContext.Provider>
	);
}

export function useTheme() {
	const ctx = useContext(ThemeContext);
	if (!ctx) {
		throw new Error('useTheme must be used within ThemeProvider');
	}
	return ctx;
}
