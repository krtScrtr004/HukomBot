import Logo from '@/components/ui/Logo';
import ThemeToggle from '@/components/ui/ThemeToggle';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import type { CaseAnalysisAnswerFormat as AnswerFormat } from '@/types/workspace';

interface HeaderProps {
	userName?: string;
	onToggleSidebar?: () => void;
	onToggleVersionPanel?: () => void;
	onSignOut?: () => void;
}

export default function Header({
	userName,
	onToggleSidebar,
	onToggleVersionPanel,
	onSignOut,
}: HeaderProps) {
	const {
		state: { answerFormat },
		setAnswerFormat,
	} = useWorkspace();

	return (
		<header
			className="h-(--header-height) shrink-0 flex items-center justify-between gap-4 px-4 border-b border-border bg-surface"
			role="banner"
		>
			<div className="flex items-center gap-3 min-w-0">
				<button
					type="button"
					onClick={onToggleSidebar}
					className="lg:hidden p-2 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					aria-label="Toggle session explorer"
				>
					<i className="bi bi-list text-xl" aria-hidden="true" />
				</button>
				<Logo />
			</div>

			<div className="flex items-center gap-3 shrink-0">
				{userName && (
					<span className="hidden sm:inline text-sm text-text-secondary truncate max-w-48">
						{userName}
					</span>
				)}
				<button
					type="button"
					onClick={onToggleVersionPanel}
					className="lg:hidden p-2 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					aria-label="Toggle version panel"
				>
					<i
						className="bi bi-clock-history text-xl"
						aria-hidden="true"
					/>
				</button>

				{/* Answer Format Selector */}
				<select
					value={answerFormat}
					onChange={(e) =>
						setAnswerFormat(e.target.value as AnswerFormat)
					}
					className="rounded-sm border border-border bg-surface text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					aria-label="Select answer format"
				>
					<option value="plaintext">Plaintext</option>
					<option value="markdown">Markdown</option>
					<option value="html">HTML</option>
				</select>

				<ThemeToggle />
				<button
					type="button"
					onClick={onSignOut}
					className="p-2 rounded-sm text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					aria-label="Sign out"
				>
					<i
						className="bi bi-box-arrow-right text-xl"
						aria-hidden="true"
					/>
				</button>
			</div>
		</header>
	);
}
