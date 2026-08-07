import { useMemo, useState } from 'react';
import { useWorkspace, validateCaseFact } from '@/contexts/WorkspaceContext';
import CaseFactRow from '@/components/workspace/AnalysisWorkspace/CaseFactRow';
import PendingChangesSummary from '@/components/workspace/AnalysisWorkspace/PendingChangesSummary';
import { CASE_FACT_MAX_COUNT } from '@/types/workspace';

export default function EditReanalyzeWorkspace() {
	const {
		state,
		exitEditMode,
		addEditFact,
		updateEditFact,
		deleteEditFact,
		restoreEditFact,
		undoEditFact,
	} = useWorkspace();

	const [errors, setErrors] = useState<Record<string, string | null>>({});

	const activeCount = useMemo(
		() => state.editState.filter((f) => f.status !== 'deleted').length,
		[state.editState],
	);

	const handleChange = (tempId: string, value: string) => {
		updateEditFact(tempId, value);
		setErrors((prev) => ({ ...prev, [tempId]: validateCaseFact(value) }));
	};

	return (
		<div className="flex flex-col lg:flex-row gap-6 h-full">
			<div className="flex-1 min-w-0 flex flex-col gap-4">
				<div className="flex items-center justify-between gap-4">
					<h2 className="text-lg font-semibold text-text-primary">
						Review &amp; Reanalyze
					</h2>
					<button
						type="button"
						onClick={exitEditMode}
						className="text-sm text-text-secondary hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm"
					>
						Close
					</button>
				</div>

				<div className="flex flex-col gap-3 overflow-y-auto flex-1">
					{state.editState.map((fact) => (
						<CaseFactRow
							key={fact.tempId}
							fact={fact}
							onChange={handleChange}
							onDelete={deleteEditFact}
							onRestore={restoreEditFact}
							onUndo={undoEditFact}
							error={errors[fact.tempId]}
						/>
					))}
				</div>

				<button
					type="button"
					onClick={addEditFact}
					disabled={activeCount >= CASE_FACT_MAX_COUNT}
					className="self-start flex items-center gap-2 px-4 py-2 rounded-sm text-sm font-medium border border-dashed border-border text-text-secondary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
				>
					<i className="bi bi-plus-lg" aria-hidden="true" />
					Add Fact
				</button>
			</div>

			<PendingChangesSummary />
		</div>
	);
}
