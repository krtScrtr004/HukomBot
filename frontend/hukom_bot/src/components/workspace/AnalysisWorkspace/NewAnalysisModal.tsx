import { useEffect, useRef, useState } from 'react';
import { useWorkspace, validateCaseFact } from '@/contexts/WorkspaceContext';
import {
	CASE_FACT_MAX_COUNT,
	CASE_FACT_MAX_LENGTH,
	CASE_FACT_MIN_LENGTH,
} from '@/types/workspace';
import FactTextArea from '../shared/FactTextarea';
import CharacterCounter from '@/components/ui/CharacterCounter';
import ErrorText from '@/components/ui/ErrorText';

interface NewAnalysisModalProps {
	open: boolean;
	onClose: () => void;
}

export default function NewAnalysisModal({
	open,
	onClose,
}: NewAnalysisModalProps) {
	const { submitNewAnalysis, state } = useWorkspace();
	const [facts, setFacts] = useState<string[]>(['']);
	const [errors, setErrors] = useState<(string | null)[]>([null]);
	const [submitError, setSubmitError] = useState<string | null>(null);
	const firstInputRef = useRef<HTMLTextAreaElement>(null);

	useEffect(() => {
		if (!open) {
			return;
		}
		setTimeout(() => {
			setFacts(['']);
			setErrors([null]);
			setSubmitError(null);
			firstInputRef.current?.focus();
		}, 0);
	}, [open]);

	useEffect(() => {
		if (!open) {
			return;
		}

		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape' && !state.loading.generating) {
				onClose();
			}
		};
		document.addEventListener('keydown', handleKey);
		return () => document.removeEventListener('keydown', handleKey);
	}, [open, onClose, state.loading.generating]);

	if (!open) return null;

	const addFact = () => {
		if (facts.length >= CASE_FACT_MAX_COUNT) {
			return;
		}
		setFacts((prev) => [...prev, '']);
		setErrors((prev) => [...prev, null]);
	};

	const removeFact = (index: number) => {
		if (facts.length <= 1) {
			return;
		}
		setFacts((prev) => prev.filter((_, i) => i !== index));
		setErrors((prev) => prev.filter((_, i) => i !== index));
	};

	const updateFact = (index: number, value: string) => {
		setFacts((prev) => prev.map((f, i) => (i === index ? value : f)));
		setErrors((prev) =>
			prev.map((e, i) => (i === index ? validateCaseFact(value) : e)),
		);
	};

	const handleSubmit = async () => {
		const trimmed = facts.map((f) => f.trim()).filter(Boolean);
		if (trimmed.length === 0) {
			setSubmitError('Add at least one case fact.');
			return;
		}

		const validationErrors = trimmed.map((f) => validateCaseFact(f));
		if (validationErrors.some(Boolean)) {
			setErrors(facts.map((f) => validateCaseFact(f)));
			return;
		}

		setSubmitError(null);
		try {
			await submitNewAnalysis(trimmed);
		} catch {
			setSubmitError('Analysis generation failed. Please retry.');
		}
	};

	return (
		<div className="fixed inset-0 z-(--z-dialog) flex items-center justify-center p-4">
			<section
				className="absolute inset-0 bg-black/40"
				onClick={() => !state.loading.generating && onClose()}
				aria-hidden="true"
			/>

			<section
				role="dialog"
				aria-modal="true"
				aria-labelledby="new-analysis-title"
				className="relative z-10 w-150 max-w-lg rounded-lg bg-surface border border-border shadow-lg flex flex-col max-h-[90vh]"
			>
				{/* Heading */}
				<section className="p-4 border-b border-border shrink-0">
					<h2
						id="new-analysis-title"
						className="text-lg font-semibold text-text-primary"
					>
						New Analysis
					</h2>
					
					<p className="text-sm text-text-muted mt-1">
						Describe the facts of your legal case (
						{CASE_FACT_MIN_LENGTH}–{CASE_FACT_MAX_LENGTH} characters
						each).
					</p>
				</section>

				{/* Body */}
				<section className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
					{facts.map((fact, index) => (
						<div key={index} className="space-y-1">
							{/* Heading */}
							<div className="flex items-center justify-between">
								<label
									htmlFor={`new-fact-${index}`}
									className="text-sm font-medium text-text-primary"
								>
									Fact {index + 1}
								</label>

								{/* Remove fact button */}
								{facts.length > 1 && (
									<button
										type="button"
										onClick={() => removeFact(index)}
										disabled={state.loading.generating}
										className="text-xs text-danger hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm disabled:opacity-50"
									>
										Remove
									</button>
								)}
							</div>

							{/* Fact input form */}
							<FactTextArea
								id={`new-fact-${index}`}
								value={fact}
								disabled={state.loading.generating}
								maxLength={CASE_FACT_MAX_LENGTH}
								rows={2}
								ref={index === 0 ? firstInputRef : undefined}
								className="min-h-10 max-h-15"
								hasError={!!errors[index]}
								onChange={(e) =>
									updateFact(index, e.target.value)
								}
							/>
							
							<div className="flex items-center justify-between">
								{/* Error */}
								{errors[index] && (
									<ErrorText text={errors[index]} />
								)}

								{/* Character counter */}
								<CharacterCounter
									text={fact}
									maxLength={CASE_FACT_MAX_LENGTH}
								/>
							</div>
						</div>
					))}

					{/* Add fact button */}
					{facts.length < CASE_FACT_MAX_COUNT && (
						<button
							type="button"
							onClick={addFact}
							disabled={state.loading.generating}
							className="flex items-center gap-2 text-sm text-text-link hover:underline focus:outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-sm disabled:opacity-50"
						>
							<i className="bi bi-plus-lg" aria-hidden="true" />
							Add another fact
						</button>
					)}

					{submitError && (
						<p className="text-sm text-danger" role="alert">
							{submitError}
						</p>
					)}
				</section>

				{/* Footer */}
				<section className="p-4 border-t border-border flex justify-end gap-3 shrink-0">
					<button
						type="button"
						onClick={onClose}
						disabled={state.loading.generating}
						className="px-4 py-2 rounded-sm text-sm font-medium border border-border text-text-primary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
					>
						Cancel
					</button>

					<button
						type="button"
						onClick={() => void handleSubmit()}
						disabled={state.loading.generating}
						className="px-4 py-2 rounded-sm text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
					>
						{state.loading.generating ? 'Analyzing…' : 'Analyze'}
					</button>
				</section>

				{/* Gneration loading overlay */}
				{state.loading.generating && (
					<div className="absolute inset-0 bg-surface-overlay/80 flex items-center justify-center rounded-lg">
						<div className="flex flex-col items-center gap-3">
							<div className="w-10 h-10 border-3 border-border border-t-primary rounded-full animate-spin" />
							<p className="text-sm text-text-secondary">
								Generating analysis…
							</p>
						</div>
					</div>
				)}
			</section>
		</div>
	);
}
