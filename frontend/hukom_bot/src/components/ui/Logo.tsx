import logoLight from '@/assets/logo/logo_full_light.svg';
import logoDark from '@/assets/logo/logo_full_dark.svg';

import { useTheme } from '@/contexts/ThemeContext';

interface LogoProp {
	className?: string;
}

export default function Logo({ className = 'h-30' }: LogoProp) {
	const { theme } = useTheme();
	return (
		<img
			src={theme === 'dark' ? logoDark : logoLight}
			className={className}
			alt="HukomBot Logo"
			title="HukomBot Logo"
			aria-label="HukomBot Logo"
		/>
	);
}
