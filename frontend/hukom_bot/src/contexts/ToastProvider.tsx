/* eslint-disable react-refresh/only-export-components */
import {
	createContext,
	useCallback,
	useContext,
	useMemo,
	useState,
} from 'react';

export type ToastVariant = 'success' | 'error' | 'info';

export interface ToastMessage {
	id: string;
	message: string;
	variant: ToastVariant;
}

interface ToastContextValue {
	toasts: ToastMessage[];
	showToast: (message: string, variant?: ToastVariant) => void;
	dismissToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

const TOAST_DURATION_MS = 4000;

export function ToastProvider({ children }: { children: React.ReactNode }) {
	const [toasts, setToasts] = useState<ToastMessage[]>([]);

	const dismissToast = useCallback((id: string) => {
		// Remove the toast with the given id from the state
		setToasts((prev) => prev.filter((t) => t.id !== id));
	}, []);

	const showToast = useCallback(
		(message: string, variant: ToastVariant = 'info') => {
			const id = crypto.randomUUID();
			setToasts((prev) => [...prev, { id, message, variant }]);
			setTimeout(() => dismissToast(id), TOAST_DURATION_MS);
		},
		[dismissToast],
	);

	const value = useMemo(
		() => ({ toasts, showToast, dismissToast }),
		[toasts, showToast, dismissToast],
	);

	return (
		<ToastContext.Provider value={value}>
			{children}
			<ToastContainer toasts={toasts} onDismiss={dismissToast} />
		</ToastContext.Provider>
	);
}

function ToastContainer({
	toasts,
	onDismiss,
}: {
	toasts: ToastMessage[];
	onDismiss: (id: string) => void;
}) {
	if (toasts.length === 0) {
		return null;
	}

	const variantClasses: Record<ToastVariant, string> = {
		success: 'border-success bg-surface text-text-primary',
		error: 'border-danger bg-surface text-text-primary',
		info: 'border-info bg-surface text-text-primary',
	};

	const iconClasses: Record<ToastVariant, string> = {
		success: 'bi-check-circle text-success',
		error: 'bi-exclamation-circle text-danger',
		info: 'bi-info-circle text-info',
	};

	return (
		<div
			className="fixed bottom-4 right-4 z-(--z-toast) flex flex-col gap-2 max-w-sm w-full pointer-events-none"
			aria-live="polite"
		>
			{toasts.map((toast) => (
				<div
					key={toast.id}
					role="status"
					className={`pointer-events-auto flex items-start gap-3 p-4 rounded-md border shadow-md ${variantClasses[toast.variant]}`}
				>
					<i
						className={`bi ${iconClasses[toast.variant]} text-lg shrink-0`}
						aria-hidden="true"
					/>
					
					<p className="text-sm flex-1">{toast.message}</p>

					<button
						type="button"
						onClick={() => onDismiss(toast.id)}
						className="shrink-0 p-1 rounded-sm text-text-muted hover:text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary"
						aria-label="Dismiss notification"
					>
						<i className="bi bi-x" aria-hidden="true" />
					</button>
				</div>
			))}
		</div>
	);
}

export function useToast() {
	const ctx = useContext(ToastContext);
	if (!ctx) {
		throw new Error('useToast must be used within ToastProvider');
	}
	return ctx;
}
