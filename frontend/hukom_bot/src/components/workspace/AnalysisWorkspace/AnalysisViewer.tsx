import EmptyState from '@/components/workspace/shared/EmptyState';
import { useWorkspace } from '@/contexts/WorkspaceContext';
import LoadingSpinner from '@/components/workspace/shared/LoadingSpinner';
import AnalysisContent from '@/components/workspace/AnalysisWorkspace/AnalysisContent';

export default function AnalysisViewer() {
	const { state, isLatestVersionSelected, enterEditMode, selectVersion } =
		useWorkspace();

	const analysis = state.currentAnalysis;

	// Show loading
	if (state.loading.analysis) {
		return <LoadingSpinner label="Loading analysis" className="py-16" />;
	}

	const buttonHandler = () => {
		if (state.selectedVersionNumber !== null && state.selectedSessionId) {
			void selectVersion(state.selectedVersionNumber);
		}
	};

	if (state.errors.analysis) {
		return (
			<EmptyState
				icon="bi-exclamation-triangle"
				title="Failed to load analysis"
				description={state.errors.analysis}
				action={
					<button
						type="button"
						className="flex items-center gap-2 px-4 py-2 mt-4 rounded-sm text-sm font-medium border border-border hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						aria-label="Retry loading analysis"
						onClick={buttonHandler}
					>
						<i
							className="bi bi-arrow-clockwise"
							aria-hidden="true"
						/>
						Retry
					</button>
				}
			/>
		);
	}

	if (!analysis) {
		return null;
	}

	const formattedDate = new Date(analysis.created_at).toLocaleString(
		undefined,
		{
			month: 'long',
			day: 'numeric',
			year: 'numeric',
			hour: 'numeric',
			minute: '2-digit',
		},
	);

	// Edit & Reanalyze Button
	const editNReanalyzeButtonElem =
		isLatestVersionSelected && state.mode === 'view' ? (
			<button
				type="button"
				onClick={enterEditMode}
				className="shrink-0 flex items-center gap-2 px-4 py-2 rounded-sm text-sm font-medium border border-border hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
			>
				<i className="bi bi-pencil" aria-hidden="true" />
				Edit &amp; Reanalyze
			</button>
		) : null;

	return (
		<div className="flex flex-col gap-4 fade-in">
			<section className="flex items-start justify-between gap-4">
				<div className="min-w-0">
					{/* Tile */}
					<h2 className="text-xl font-semibold text-text-primary">
						<span className="mr-2">
							<i className="bi bi-lightbulb" />
						</span>

						{analysis.title}
					</h2>

					{/* Version number and date */}
					<p className="text-sm text-text-muted mt-1">
						Version {analysis.version_number}
						<span aria-hidden="true"> · </span>
						<time dateTime={analysis.created_at}>
							{formattedDate}
						</time>
					</p>
				</div>

				{/* Edit & Reanalyze button, if latest analysis version */}
				{editNReanalyzeButtonElem}
			</section>

			{/* Answer */}
			<section className="rounded-md border border-border bg-surface-muted p-4 overflow-auto">
				<AnalysisContent answer={analysis.answer} />
			</section>
		</div>
	);
}
