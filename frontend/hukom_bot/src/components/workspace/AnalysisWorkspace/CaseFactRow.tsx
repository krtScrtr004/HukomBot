import type { EditableCaseFact, FactStatus } from '@/types/workspace';
import { CASE_FACT_MAX_LENGTH } from '@/types/workspace';
import FactRowActionButton from './FactRowActionButton';
import FactTextArea from '../shared/FactTextArea';
import CharacterCounter from '@/components/ui/CharacterCounter';
import ErrorText from '@/components/ui/ErrorText';

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
		return 'border-warning bg-warning/5';
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
		if (readOnly) {
			return null;
		}

		if (isDeleted) {
			// Delete fact button
			return (
				<FactRowActionButton
					text="Restore"
					iconClassName="bi-arrow-counterclockwise"
					className="text-text-link"
					onClick={() => onRestore?.(fact.tempId)}
				/>
			);
		}

		return (
			<>
				{/* Undo changes button */}
				{(isModified || isNew) && (
					<FactRowActionButton
						text="Undo"
						iconClassName="bi-arrow-return-left"
						className="text-text-link"
						onClick={() => onUndo?.(fact.tempId)}
					/>
				)}

				{/* Delete fact button */}
				<FactRowActionButton
					text="Delete"
					iconClassName="bi-trash3"
					className="text-danger"
					onClick={() => onDelete?.(fact.tempId)}
				/>
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
					<FactTextArea
						id=""
						value={fact.fact}
						disabled={isDeleted}
						maxLength={CASE_FACT_MAX_LENGTH}
						rows={2}
						className="min-h-20 max-h-40"
						hasError={!!error}
						onChange={(e) =>
							onChange?.(fact.tempId, e.target.value)
						}
					/>
				)}
			</div>

			{!readOnly && (
				<div className="flex items-center justify-between mt-1">
					{/* Errors */}
					{error && <ErrorText text={error} />}

					{/* Character counter */}
					<CharacterCounter
						text={fact.fact}
						maxLength={CASE_FACT_MAX_LENGTH}
					/>
				</div>
			)}

			<div className="flex items-center gap-2 mt-2">
				{renderActions()}
			</div>
		</div>
	);
}
