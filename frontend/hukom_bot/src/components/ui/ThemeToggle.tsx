import { useTheme } from '@/contexts/ThemeContext';

export default function ThemeToggle() {
	const { theme, toggleTheme } = useTheme();

	return (
		<>
			<button
				className="w-10 h-10 absolute top-5 right-5 rounded-full bg-background border border-primary flex items-center justify-center text-text-primary cursor-pointer transition-colors hover:bg-primary hover:text-background"
				onClick={toggleTheme}
			>
				<i
					className={theme === 'light' ? 'bi bi-moon' : 'bi bi-sun'}
				></i>
			</button>
		</>
	);
}
