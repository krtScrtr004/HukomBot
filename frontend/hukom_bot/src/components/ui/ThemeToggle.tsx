import { useTheme } from '@/contexts/ThemeContext';

interface ThemeToggleProps {
	className?: string;
}

export default function ThemeToggle({ className }: ThemeToggleProps) {
	const { theme, toggleTheme } = useTheme();

	return (
		<>
			<button
				className={`w-10 h-10 flex items-center justify-center text-text-primary cursor-pointer transition-colors  ${className}`}
				onClick={toggleTheme}
			>
				<i
					className={theme === 'light' ? 'bi bi-moon' : 'bi bi-sun'}
				></i>
			</button>
		</>
	);
}
