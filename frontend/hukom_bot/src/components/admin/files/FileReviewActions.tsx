import { useState } from 'react';
import type { AdminDocumentListItem } from '@/types/admin';
import type { LegalDocumentType } from '@/types/workspace';
import {
	approveDocument,
	rejectDocument,
} from '@/services/adminDocumentsService';
import { useAdmin } from '@/contexts/AdminContext';
import { useToast } from '@/contexts/ToastProvider';
import { getAdminErrorMessage } from '@/utils/adminErrors';
import { LEGAL_DOCUMENT_TYPES } from '@/constants/legalDocumentTypes';
import ConfirmDialog from '@/components/workspace/shared/ConfirmDialog';
import FactTextArea from '@/components/workspace/shared/FactTextarea';
import CharacterCounter from '@/components/ui/CharacterCounter';
import ErrorText from '@/components/ui/ErrorText';

interface FileReviewActionsProps {
	document: AdminDocumentListItem;
}

const MAX_REJECTION_LENGTH = 500;

export default function FileReviewActions({
	document,
}: FileReviewActionsProps) {
	const { patchDocument } = useAdmin();
	const { showToast } = useToast();
	const [approveOpen, setApproveOpen] = useState(false);
	const [rejectOpen, setRejectOpen] = useState(false);
	const [documentType, setDocumentType] = useState<LegalDocumentType>(
		document.document_type,
	);
	const [rejectionMessage, setRejectionMessage] = useState('');
	const [rejectionError, setRejectionError] = useState<string | null>(null);
	const [submitting, setSubmitting] = useState(false);

	if (
		document.upload_status !== 'pending' &&
		document.upload_status !== 'failed'
	) {
		return null;
	}

	const handleApprove = async () => {
		setSubmitting(true);
		try {
			await approveDocument(document.id, documentType);
			patchDocument({
				...document,
				document_type: documentType,
				upload_status: 'ongoing',
			});
			showToast('File approved', 'success');
			setApproveOpen(false);
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
			await rejectDocument(document.id, trimmed);
			patchDocument({
				...document,
				upload_status: 'rejected',
				rejection_message: trimmed,
			});
			showToast('File rejected', 'success');
			setRejectOpen(false);
			setRejectionMessage('');
		} catch (error) {
			showToast(getAdminErrorMessage(error), 'error');
		} finally {
			setSubmitting(false);
		}
	};

	return (
		<>
			<div
				className="flex gap-2"
				onClick={(e) => e.stopPropagation()}
				onKeyDown={(e) => e.stopPropagation()}
			>
				{document.upload_status === 'failed' ? (
					<button
						type="button"
						className="px-2 py-1 text-xs rounded-sm bg-primary text-primary-foreground hover:opacity-90 flex items-center gap-1"
						onClick={() => {
							setDocumentType(document.document_type);
							setApproveOpen(true);
						}}
					>
						<i className="bi bi-arrow-clockwise" /> Retry
					</button>
				) : (
					<>
						<button
							type="button"
							className="px-2 py-1 text-xs rounded-sm bg-primary text-primary-foreground hover:opacity-90"
							onClick={() => {
								setDocumentType(document.document_type);
								setApproveOpen(true);
							}}
						>
							Approve
						</button>
						<button
							type="button"
							className="px-2 py-1 text-xs rounded-sm bg-danger text-danger-foreground hover:opacity-90"
							onClick={() => {
								setRejectionMessage('');
								setRejectionError(null);
								setRejectOpen(true);
							}}
						>
							Disapprove
						</button>
					</>
				)}
			</div>

			<ConfirmDialog
				open={approveOpen}
				title="Approve File"
				message={
					<div>
						<p className="mb-2">
							Confirm approval for{' '}
							<strong>{document.original_file_name}</strong>.
						</p>
						<label
							htmlFor={`approve-type-${document.id}`}
							className="block text-sm mb-1"
						>
							Document type (optional)
						</label>
						<select
							id={`approve-type-${document.id}`}
							value={documentType}
							onChange={(e) =>
								setDocumentType(
									e.target.value as LegalDocumentType,
								)
							}
							className="w-full border border-border rounded-sm px-2 py-1 text-sm bg-surface"
						>
							{LEGAL_DOCUMENT_TYPES.map((opt) => (
								<option key={opt.value} value={opt.value}>
									{opt.label}
								</option>
							))}
						</select>
					</div>
				}
				confirmLabel={submitting ? 'Approving…' : 'Approve'}
				onConfirm={() => void handleApprove()}
				onCancel={() => !submitting && setApproveOpen(false)}
			/>

			<ConfirmDialog
				open={rejectOpen}
				title="Disapprove File"
				message={
					<div>
						<p className="mb-2">
							Provide a reason for rejecting{' '}
							<strong>{document.original_file_name}</strong>.
						</p>
						<FactTextArea
							id={`reject-reason-${document.id}`}
							value={rejectionMessage}
							disabled={submitting}
							maxLength={MAX_REJECTION_LENGTH}
							rows={4}
							hasError={!!rejectionError}
							onChange={(e) => {
								setRejectionMessage(e.target.value);
								if (rejectionError) setRejectionError(null);
							}}
						/>
						<div className="flex justify-between items-start mt-1">
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
					</div>
				}
				confirmLabel={submitting ? 'Rejecting…' : 'Disapprove'}
				variant="danger"
				onConfirm={() => void handleReject()}
				onCancel={() => !submitting && setRejectOpen(false)}
			/>
		</>
	);
}
