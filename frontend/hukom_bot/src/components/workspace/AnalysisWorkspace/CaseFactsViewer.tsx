import type { CaseFactResponse } from '@/types/workspace';
import EmptyState from '@/components/workspace/shared/EmptyState';

interface CaseFactsViewerProps {
	caseFacts: CaseFactResponse[];
}

export default function CaseFactsViewer({ caseFacts }: CaseFactsViewerProps) {
	if (caseFacts.length === 0) {
		return (
			<EmptyState
				title="No case facts"
				description="This analysis version has no associated case facts."
			/>
		);
	}

	const factListItems = caseFacts.map((fact, index) => (
		<li
			key={fact.case_fact_id}
			className="flex gap-3 p-3 rounded-sm bg-surface-muted border border-border-muted text-sm text-text-primary"
		>
			<span
				className="shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-surface text-xs font-medium text-text-muted"
				aria-hidden="true"
			>
				{index + 1}
			</span>

			<span>{fact.fact}</span>
		</li>
	));

	return (
		<div className="flex flex-col gap-2">
			<h3 className="text-sm font-semibold text-text-primary">
				<span className="mr-2">
					<i className="bi bi-list-ul" />
				</span>
				Case Facts
			</h3>

			{/* Case facts list */}
			<ol
				className="flex flex-col gap-2 max-h-64 overflow-y-auto scrollbar-thin"
				aria-label="Case facts"
			>
				{factListItems}
			</ol>
		</div>
	);
}
