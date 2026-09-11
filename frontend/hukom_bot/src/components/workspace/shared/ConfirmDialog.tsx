import { useEffect, useRef, type ReactNode } from 'react';
import { useFocusTrap } from '@/hooks/useFocusTrap';

export interface ConfirmDialogProps {
	open: boolean;
	title: string;
	message: ReactNode;
	confirmLabel?: string;
	cancelLabel?: string;
	variant?: 'danger' | 'default';
	onConfirm: () => void;
	onCancel: () => void;
}

export default function ConfirmDialog({
	open,
	title,
	message,
	confirmLabel = 'Confirm',
	cancelLabel = 'Cancel',
	variant = 'default',
	onConfirm,
	onCancel,
}: ConfirmDialogProps) {
	const cancelRef = useRef<HTMLButtonElement>(null);
	const dialogRef = useRef<HTMLDivElement>(null);
	useFocusTrap(dialogRef, open);

	// Focus the cancel button when the dialog opens
	useEffect(() => {
		if (open) {
			cancelRef.current?.focus();
		}
	}, [open]);

	// Close the dialog when the Escape key is pressed
	useEffect(() => {
		if (!open) {
			return;
		}
		
		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape') {
				onCancel();
			}
		};
		document.addEventListener('keydown', handleKey);
		return () => document.removeEventListener('keydown', handleKey);
	}, [open, onCancel]);

	if (!open) {
		return null;
	}

	const confirmClasses =
		variant === 'danger'
			? 'bg-danger text-danger-foreground hover:opacity-90'
			: 'bg-primary text-primary-foreground hover:opacity-90';

	return (
		<div
			className="fixed inset-0 z-(--z-dialog) flex items-center justify-center p-4"
			role="presentation"
		>
			<div
				className="absolute inset-0 bg-black/40"
				onClick={onCancel}
				aria-hidden="true"
			/>
			<div
				ref={dialogRef}
				role="dialog"
				aria-modal="true"
				aria-labelledby="confirm-dialog-title"
				aria-describedby="confirm-dialog-message"
				className="relative z-10 w-full max-w-md rounded-lg bg-surface border border-border shadow-lg p-6"
			>
				<h2
					id="confirm-dialog-title"
					className="text-lg font-semibold text-text-primary mb-2"
				>
					{title}
				</h2>
				<div
					id="confirm-dialog-message"
					className="text-sm text-text-secondary mb-6"
				>
					{message}
				</div>
				<div className="flex justify-end gap-3">
					<button
						ref={cancelRef}
						type="button"
						onClick={onCancel}
						className="px-4 py-2 rounded-sm text-sm font-medium text-text-primary border border-border hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
					>
						{cancelLabel}
					</button>
					<button
						type="button"
						onClick={onConfirm}
						className={`px-4 py-2 rounded-sm text-sm font-medium focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${confirmClasses}`}
					>
						{confirmLabel}
					</button>
				</div>
			</div>
		</div>
	);
}
