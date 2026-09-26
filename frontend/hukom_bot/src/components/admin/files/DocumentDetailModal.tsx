import { useContext, useEffect, useRef, useState } from 'react';
import type { AdminDocumentListItem } from '@/types/admin';
import type { LegalDocumentType } from '@/types/workspace';
import {
	approveDocument,
	rejectDocument,
	deleteDocument,
} from '@/services/adminDocumentsService';
import { AdminContext } from '@/contexts/AdminContext';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/contexts/ToastProvider';
import { getAdminErrorMessage } from '@/utils/adminErrors';
import { LEGAL_DOCUMENT_TYPES } from '@/constants/legalDocumentTypes';
import StatusBadge from '@/components/ui/StatusBadge';
import CharacterCounter from '@/components/ui/CharacterCounter';
import ErrorText from '@/components/ui/ErrorText';
import ConfirmDialog from '@/components/workspace/shared/ConfirmDialog';
import { useFocusTrap } from '@/hooks/useFocusTrap';

interface DocumentDetailModalProps {
	open: boolean;
	document: AdminDocumentListItem | null;
	readOnly?: boolean;
	onClose: () => void;
}

const MAX_REJECTION_LENGTH = 500;

export default function DocumentDetailModal({
	open,
	document: doc,
	readOnly = false,
	onClose,
}: DocumentDetailModalProps) {
	const adminCtx = useContext(AdminContext);
	const { user: currentUser } = useAuth();
	const { showToast } = useToast();
	const [documentType, setDocumentType] =
		useState<LegalDocumentType>('contract');
	const [rejectionMessage, setRejectionMessage] = useState('');
	const [rejectionError, setRejectionError] = useState<string | null>(null);
	const [submitting, setSubmitting] = useState(false);
	const [showRejectInput, setShowRejectInput] = useState(false);
	const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);

	const isAdmin = !readOnly && currentUser?.role === 'admin';

	const dialogRef = useRef<HTMLDivElement>(null);
	useFocusTrap(dialogRef, open);

	useEffect(() => {
		if (open && doc) {
			setDocumentType(doc.document_type || 'statute');
			setRejectionMessage(doc.rejection_message || '');
			setRejectionError(null);
			setShowRejectInput(false);
			setConfirmDeleteOpen(false);
		}
	}, [open, doc]);

	useEffect(() => {
		if (!open) return;
		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape' && !submitting) onClose();
		};
		window.addEventListener('keydown', handleKey);
		return () => window.removeEventListener('keydown', handleKey);
	}, [open, onClose, submitting]);

	if (!open || !doc) return null;

	const handleApprove = async () => {
		setSubmitting(true);
		try {
			await approveDocument(doc.id, documentType);
			adminCtx?.patchDocument({
				...doc,
				document_type: documentType,
				upload_status: 'ongoing',
			});
			showToast(
				'Document approved successfully. Ingestion process is ongoing.',
				'success',
			);
			onClose();
		} catch (error) {
			showToast(getAdminErrorMessage(error), 'error');
		} finally {
			setSubmitting(false);
		}
	};

	const handleReject = async () => {
		const trimmed = rejectionMessage.trim();
		if (!trimmed) {
			setRejectionError('A rejection reason is required.');
			return;
		}
		setRejectionError(null);
		setSubmitting(true);
		try {
			await rejectDocument(doc.id, trimmed);
			adminCtx?.patchDocument({
				...doc,
				upload_status: 'rejected',
				rejection_message: trimmed,
			});
			showToast('Document rejected', 'success');
			onClose();
		} catch (error) {
			showToast(getAdminErrorMessage(error), 'error');
		} finally {
			setSubmitting(false);
		}
	};

	const handleDelete = async () => {
		setSubmitting(true);
		try {
			await deleteDocument(doc.id);
			showToast('Document deleted successfully', 'success');
			setConfirmDeleteOpen(false);
			onClose();
			adminCtx?.fetchDocuments();
			adminCtx?.fetchDocumentAnalytics();
		} catch (error) {
			showToast(getAdminErrorMessage(error), 'error');
		} finally {
			setSubmitting(false);
		}
	};

	const uploaderName = doc.uploader
		? `${doc.uploader.first_name} ${doc.uploader.last_name}`
		: 'Unknown User';

	return (
		<div className="fixed inset-0 z-(--z-dialog) flex items-center justify-center p-4">
			{/* Overlay */}
			<div
				className="absolute inset-0 bg-black/40"
				onClick={() => !submitting && onClose()}
				aria-hidden="true"
			/>

			{/* Dialog Container */}
			<div
				ref={dialogRef}
				role="dialog"
				aria-modal="true"
				aria-labelledby="doc-detail-title"
				className="relative z-10 w-150 rounded-sm bg-surface border border-border shadow-lg flex flex-col max-h-[90vh] overflow-hidden"
			>
				{/* Modal Header */}
				<header className="p-4 border-b border-border shrink-0 flex items-center justify-between bg-surface">
					<div className="flex items-center gap-3 min-w-0">
						<div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary shrink-0">
							<i className="bi bi-file-earmark-text text-xl" />
						</div>
						<div className="min-w-0">
							<h2
								id="doc-detail-title"
								className="text-base font-semibold text-text-primary truncate"
								title={doc.original_file_name}
							>
								{doc.original_file_name}
							</h2>
							<p className="text-xs text-text-muted">
								Document Details & Metadata
							</p>
						</div>
					</div>
					<button
						type="button"
						onClick={onClose}
						disabled={submitting}
						className="p-1 rounded-sm text-text-secondary hover:bg-hover focus:outline-none disabled:opacity-50"
						aria-label="Close modal"
					>
						<i className="bi bi-x text-xl" />
					</button>
				</header>

				{/* Modal Content Body */}
				<div className="flex-1 overflow-y-auto p-6 space-y-5 scrollbar-thin">
					{/* Status Overview Card */}
					<div className="rounded-lg border border-border bg-surface-muted p-4 space-y-3">
						<div className="flex items-center justify-between">
							<span className="text-xs text-text-muted font-medium">
								Processing Status
							</span>
							<StatusBadge status={doc.upload_status} />
						</div>

						<div className="grid grid-cols-2 gap-2 pt-2 border-t border-border/60 text-xs">
							<div>
								<span className="text-text-muted block">
									Upload Date
								</span>
								<span className="font-medium text-text-primary">
									{new Date(
										doc.created_at,
									).toLocaleDateString(undefined, {
										year: 'numeric',
										month: 'long',
										day: 'numeric',
									})}
								</span>
							</div>
							<div>
								<span className="text-text-muted block">
									Uploader ID
								</span>
								<span className="font-mono text-text-primary truncate block">
									{doc.uploader?.id || 'N/A'}
								</span>
							</div>
						</div>
					</div>

					{/* Uploader Details Card */}
					<div className="rounded-lg border border-border bg-surface p-4 space-y-2">
						<h3 className="text-xs font-semibold text-text-secondary uppercase tracking-wider">
							Uploader Profile
						</h3>
						<div className="flex items-center gap-3 pt-1">
							<div className="h-9 w-9 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold text-sm shrink-0">
								{doc.uploader?.first_name?.charAt(0) || 'U'}
							</div>
							<div>
								<p className="text-sm font-medium text-text-primary">
									{uploaderName}
								</p>
								<p className="text-xs text-text-muted font-mono">
									{doc.uploader?.email || 'No email provided'}
								</p>
							</div>
						</div>
					</div>

					{/* Document Category Field */}
					<div className="space-y-1">
						<label
							htmlFor="doc-type-select"
							className="block text-sm font-medium text-text-primary"
						>
							Legal Document Category
						</label>

						<select
							id="doc-type-select"
							value={documentType}
							disabled={
								!isAdmin ||
								submitting ||
								doc.upload_status === 'rejected'
							}
							onChange={(e) =>
								setDocumentType(
									e.target.value as LegalDocumentType,
								)
							}
							className="w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-60 disabled:cursor-not-allowed"
						>
							{LEGAL_DOCUMENT_TYPES.sort((a, b) =>
								a.label.localeCompare(b.label),
							).map((opt) => (
								<option
									key={opt.value}
									value={opt.value}
									selected={doc.document_type === opt.value}
								>
									{opt.label}
								</option>
							))}
						</select>
					</div>

					{/* Rejection Message Section */}
					{doc.upload_status === 'rejected' &&
					doc.rejection_message ? (
						<div className="rounded-lg border border-danger/30 bg-danger/5 p-4 space-y-1">
							<span className="text-xs font-semibold text-danger flex items-center gap-1">
								<i className="bi bi-exclamation-triangle" />{' '}
								Rejection Reason
							</span>
							<p className="text-xs text-text-primary">
								{doc.rejection_message}
							</p>
						</div>
					) : null}

					{/* Inline Disapproval Reason Form for Pending files */}
					{isAdmin &&
					doc.upload_status === 'pending' &&
					showRejectInput ? (
						<div className="rounded-lg border border-danger/30 bg-danger/5 p-4 space-y-2">
							<label
								htmlFor="modal-reject-reason"
								className="block text-xs font-semibold text-danger"
							>
								Reason for Disapproval
							</label>

							<textarea
								id="modal-reject-reason"
								value={rejectionMessage}
								disabled={submitting}
								maxLength={MAX_REJECTION_LENGTH}
								rows={3}
								onChange={(e) => {
									setRejectionMessage(e.target.value);
									if (rejectionError) setRejectionError(null);
								}}
								placeholder="Describe why this document is being rejected…"
								className="w-full border border-border rounded-sm p-2 text-xs bg-surface text-text-primary focus:outline-none focus:ring-1 focus:ring-danger"
							/>

							<div className="flex justify-between items-center text-xs">
								{rejectionError ? (
									<ErrorText error={rejectionError} />
								) : (
									<span />
								)}
								<CharacterCounter
									text={rejectionMessage}
									maxLength={MAX_REJECTION_LENGTH}
								/>
							</div>

							<div className="flex justify-end gap-2 pt-1">
								<button
									type="button"
									onClick={() => setShowRejectInput(false)}
									disabled={submitting}
									className="px-3 py-1 rounded-sm text-xs border border-border hover:bg-hover"
								>
									Cancel
								</button>

								<button
									type="button"
									onClick={() => void handleReject()}
									disabled={submitting}
									className="px-3 py-1 rounded-sm text-xs bg-danger text-danger-foreground font-medium hover:opacity-90 disabled:opacity-50"
								>
									{submitting
										? 'Rejecting…'
										: 'Confirm Disapproval'}
								</button>
							</div>
						</div>
					) : null}
				</div>

				{/* Modal Footer */}
				<footer className="p-4 border-t border-border shrink-0 flex items-center justify-between bg-surface">
					<div className="flex items-center gap-2">
						<button
							type="button"
							onClick={onClose}
							disabled={submitting}
							className="px-4 py-2 rounded-sm text-sm border border-border text-text-primary hover:bg-hover transition-colors disabled:opacity-50"
						>
							Close
						</button>

						{isAdmin && (
							<button
								type="button"
								onClick={() => setConfirmDeleteOpen(true)}
								disabled={submitting}
								className="px-3 py-2 rounded-sm text-sm border border-danger/40 text-danger hover:bg-danger/10 transition-colors disabled:opacity-50 flex items-center gap-1.5"
							>
								<i className="bi bi-trash" /> Delete
							</button>
						)}
					</div>

					{isAdmin &&
					(doc.upload_status === 'pending' ||
						doc.upload_status === 'failed') &&
					!showRejectInput ? (
						<div className="flex items-center gap-2">
							{doc.upload_status === 'pending' && (
								<button
									type="button"
									onClick={() => setShowRejectInput(true)}
									disabled={submitting}
									className="px-3 py-2 rounded-sm text-sm border border-danger/40 text-danger hover:bg-danger/10 transition-colors disabled:opacity-50"
								>
									Disapprove
								</button>
							)}

							<button
								type="button"
								onClick={() => void handleApprove()}
								disabled={submitting}
								className="px-4 py-2 rounded-sm text-sm bg-primary text-primary-foreground font-medium hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-1.5"
							>
								{submitting && (
									<i className="bi bi-arrow-repeat animate-spin text-sm" />
								)}
								{submitting
									? doc.upload_status === 'failed'
										? 'Retrying…'
										: 'Approving…'
									: doc.upload_status === 'failed'
										? 'Retry Upload'
										: 'Approve File'}
							</button>
						</div>
					) : null}
				</footer>
			</div>

			<ConfirmDialog
				open={confirmDeleteOpen}
				title="Delete Document"
				message={`Are you sure you want to permanently delete "${doc.original_file_name}"? This action cannot be undone.`}
				confirmLabel={submitting ? 'Deleting…' : 'Delete Document'}
				variant="danger"
				onConfirm={() => void handleDelete()}
				onCancel={() => !submitting && setConfirmDeleteOpen(false)}
			/>
		</div>
	);
}
