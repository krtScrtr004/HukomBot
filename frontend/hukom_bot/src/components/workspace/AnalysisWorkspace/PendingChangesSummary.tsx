import { useWorkspace } from '@/contexts/WorkspaceContext';

export default function PendingChangesSummary() {
	const {
		pendingChanges,
		isDirty,
		discardAllChanges,
		submitReanalysis,
		state,
	} = useWorkspace();

	const total =
		pendingChanges.newFacts +
		pendingChanges.modifiedFacts +
		pendingChanges.deletedFacts;

	return (
		<aside
			className="shrink-0 w-full lg:w-64 border border-border rounded-md bg-surface p-4 flex flex-col gap-4"
			aria-label="Pending changes summary"
		>
			<section>
				<h3 className="text-sm font-semibold text-text-primary flex items-center gap-2">
						<i className="bi bi-hourglass-split"></i>
						Pending Changes

					{isDirty && (
						<span className="px-2 py-0.5 rounded-full text-xs bg-warning/15 text-warning">
							Unsaved
						</span>
					)}
				</h3>

				{/* Modification stats */}
				<ul className="mt-3 space-y-1 text-sm text-text-secondary">
					<li>New Facts: {pendingChanges.newFacts}</li>
					<li>Modified Facts: {pendingChanges.modifiedFacts}</li>
					<li>Deleted Facts: {pendingChanges.deletedFacts}</li>
				</ul>
			</section>

			<hr className="border-border-muted" />

			<section className="flex flex-col gap-2">
				<button
					type="button"
					onClick={discardAllChanges}
					disabled={!isDirty || state.loading.generating}
					className="w-full px-4 py-2 rounded-sm text-sm font-medium border border-border text-text-primary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Discard Changes
				</button>

				<button
					type="button"
					onClick={() => void submitReanalysis()}
					disabled={total === 0 || state.loading.generating}
					className="w-full px-4 py-2 rounded-sm text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50 disabled:cursor-not-allowed"
				>
					{state.loading.generating ? 'Reanalyzing…' : 'Reanalyze'}
				</button>
			</section>
		</aside>
	);
}
