import type { EditableCaseFact, FactStatus } from '@/types/workspace';
import { CASE_FACT_MAX_LENGTH } from '@/types/workspace';

interface CaseFactRowProps {
	fact: EditableCaseFact;
	readOnly?: boolean;
	onChange?: (tempId: string, value: string) => void;
	onDelete?: (tempId: string) => void;
	onRestore?: (tempId: string) => void;
	onUndo?: (tempId: string) => void;
	error?: string | null;
}

const STATUS_BADGE_MAP: Record<
	FactStatus,
	{ label: string; className: string } | null
> = {
	unchanged: null,
	modified: { label: 'Edited', className: 'bg-warning/15 text-warning' },
	new: { label: 'New', className: 'bg-info/15 text-info' },
	deleted: { label: 'Deleted', className: 'bg-danger/15 text-danger' },
};

function getRowClassName(status: FactStatus): string {
	if (status === 'modified') {
		(" return 'border-warning bg-warning/5';");
	}
	if (status === 'new') {
		return 'border-info bg-info/5';
	}
	if (status === 'deleted') {
		return 'border-border-muted bg-surface-muted opacity-75';
	}
	return 'border-border bg-surface';
}

export default function CaseFactRow({
	fact,
	readOnly = false,
	onChange,
	onDelete,
	onRestore,
	onUndo,
	error,
}: CaseFactRowProps) {
	const badge = STATUS_BADGE_MAP[fact.status];
	const isDeleted = fact.status === 'deleted';
	const isModified = fact.status === 'modified';
	const isNew = fact.status === 'new';

	const renderActions = () => {
		if (readOnly) return null;

		if (isDeleted) {
			return (
				<button
					type="button"
					onClick={() => onRestore?.(fact.tempId)}
					className="text-xs text-text-link hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm"
				>
					<span className="mr-2">
						<i className="bi bi-arrow-counterclockwise" />
					</span>
					Restore
				</button>
			);
		}

		return (
			<>
				{(isModified || isNew) && (
					<button
						type="button"
						onClick={() => onUndo?.(fact.tempId)}
						className="text-xs text-text-link hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm"
					>
						<span className="mr-2">
							<i className="bi bi-arrow-return-left" />
						</span>
						Undo
					</button>
				)}
				<button
					type="button"
					onClick={() => onDelete?.(fact.tempId)}
					className="text-xs text-danger hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm"
				>
					<span className="mr-2">
						<i className="bi bi-trash3" />
					</span>
					Delete
				</button>
			</>
		);
	};

	return (
		<div
			className={`rounded-sm border p-3 transition-colors duration-fast ${getRowClassName(fact.status)}`}
		>
			<div className="flex items-start gap-2">
				{badge && (
					<span
						className={`shrink-0 px-2 py-0.5 rounded-full text-xs font-medium ${badge.className}`}
					>
						{badge.label}
					</span>
				)}
				{readOnly ? (
					<p
						className={`flex-1 text-sm text-text-primary ${isDeleted ? 'line-through' : ''}`}
					>
						{fact.fact}
					</p>
				) : (
					<textarea
						value={fact.fact}
						onChange={(e) =>
							onChange?.(fact.tempId, e.target.value)
						}
						disabled={isDeleted}
						maxLength={CASE_FACT_MAX_LENGTH}
						rows={5}
						className={`bg-surface-elevated flex-1 w-full min-h-20 max-h-50 text-sm rounded-sm border border-border bg-surface px-3 py-2 text-text-secondary resize-y focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-60 ${isDeleted ? 'line-through' : ''}`}
						aria-label="Case fact"
						aria-invalid={!!error}
					/>
				)}
			</div>

			{error && (
				<p className="mt-1 text-xs text-danger" role="alert">
					{error}
				</p>
			)}

			<div className="flex items-center gap-2 mt-2">
				{renderActions()}
			</div>
		</div>
	);
}
