import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError, isAuthError } from '@/services/apiClient';
import { uploadDocument } from '@/services/documentService';
import type { LegalDocumentType } from '@/types/workspace';
import { useToast } from '@/contexts/ToastProvider';

interface UploadDocumentModalProps {
	open: boolean;
	onClose: () => void;
}

const LEGAL_DOCUMENT_TYPES: { value: LegalDocumentType; label: string }[] = [
	{ value: 'contract', label: 'Contract' },
	{ value: 'non_disclosure_agreement', label: 'Non-Disclosure Agreement' },
	{ value: 'service_agreement', label: 'Service Agreement' },
	{ value: 'employment_contract', label: 'Employment Contract' },
	{ value: 'lease_agreement', label: 'Lease Agreement' },
	{ value: 'partnership_agreement', label: 'Partnership Agreement' },
	{ value: 'memorandum_of_agreement', label: 'Memorandum of Agreement' },
	{
		value: 'memorandum_of_understanding',
		label: 'Memorandum of Understanding',
	},
	{ value: 'addendum_amendment', label: 'Addendum/Amendment' },
	{ value: 'franchise_agreement', label: 'Franchise Agreement' },
	{ value: 'indemnity_agreement', label: 'Indemnity Agreement' },
	{ value: 'articles_of_incorporation', label: 'Articles of Incorporation' },
	{ value: 'bylaws', label: 'Bylaws' },
	{ value: 'board_resolution', label: 'Board Resolution' },
	{ value: 'shareholder_agreement', label: 'Shareholder Agreement' },
	{ value: 'minutes_of_meeting', label: 'Minutes of Meeting' },
	{ value: 'secretary_certificate', label: "Secretary's Certificate" },
	{ value: 'general_information_sheet', label: 'General Information Sheet' },
	{ value: 'complaint', label: 'Complaint' },
	{ value: 'affidavit', label: 'Affidavit' },
	{ value: 'subpoena', label: 'Subpoena' },
	{ value: 'court_order', label: 'Court Order' },
	{ value: 'judgment', label: 'Judgment' },
	{ value: 'supreme_court_decision', label: 'Supreme Court Decision' },
	{ value: 'court_of_appeals_decision', label: 'Court of Appeals Decision' },
	{ value: 'motion', label: 'Motion' },
	{ value: 'summons', label: 'Summons' },
	{ value: 'pleading', label: 'Pleading' },
	{ value: 'brief_memorandum', label: 'Brief/Memorandum' },
	{ value: 'last_will_and_testament', label: 'Last Will and Testament' },
	{ value: 'deed_of_sale', label: 'Deed of Sale' },
	{ value: 'power_of_attorney', label: 'Power of Attorney' },
	{ value: 'trust_deed', label: 'Trust Deed' },
	{ value: 'birth_certificate', label: 'Birth Certificate' },
	{ value: 'marriage_contract', label: 'Marriage Contract' },
	{ value: 'deed_of_donation', label: 'Deed of Donation' },
	{ value: 'prenuptial_agreement', label: 'Prenuptial Agreement' },
	{ value: 'permit', label: 'Permit' },
	{ value: 'license', label: 'License' },
	{ value: 'government_issued_id', label: 'Government Issued ID' },
	{ value: 'tax_declaration', label: 'Tax Declaration' },
	{ value: 'tax_clearance', label: 'Tax Clearance' },
	{
		value: 'certificate_of_registration',
		label: 'Certificate of Registration',
	},
	{ value: 'constitution', label: 'Constitution' },
	{ value: 'republic_act', label: 'Republic Act' },
	{ value: 'revenue_regulation', label: 'Revenue Regulation' },
	{
		value: 'revenue_memorandum_circular',
		label: 'Revenue Memorandum Circular',
	},
	{ value: 'executive_order', label: 'Executive Order' },
	{ value: 'municipal_ordinance', label: 'Municipal Ordinance' },
	{ value: 'promissory_note', label: 'Promissory Note' },
	{ value: 'deed_of_mortgage', label: 'Deed of Mortgage' },
	{ value: 'loan_agreement', label: 'Loan Agreement' },
	{ value: 'invoice', label: 'Invoice' },
	{ value: 'receipt', label: 'Receipt' },
	{
		value: 'audited_financial_statement',
		label: 'Audited Financial Statement',
	},
	{ value: 'patent', label: 'Patent' },
	{ value: 'trademark_registration', label: 'Trademark Registration' },
	{ value: 'copyright_registration', label: 'Copyright Registration' },
	{ value: 'ip_assignment', label: 'IP Assignment' },
	{ value: 'certification', label: 'Certification' },
	{ value: 'waiver', label: 'Waiver' },
	{ value: 'notice', label: 'Notice' },
	{ value: 'other', label: 'Other' },
];

function isPdf(file: File) {
	return (
		file.type === 'application/pdf' ||
		file.name.toLowerCase().endsWith('.pdf')
	);
}

export default function UploadDocumentModal({
	open,
	onClose,
}: UploadDocumentModalProps) {
	const [selectedFile, setSelectedFile] = useState<File | null>(null);
	const [documentType, setDocumentType] = useState<LegalDocumentType | ''>(
		'',
	);
	const [previewUrl, setPreviewUrl] = useState<string | null>(null);
	const [error, setError] = useState<string | null>(null);
	const [uploading, setUploading] = useState(false);
	const fileInputRef = useRef<HTMLInputElement>(null);
	const previewUrlRef = useRef<string | null>(null);
	const { showToast } = useToast();

	const revokePreviewUrl = useCallback(() => {
		if (previewUrlRef.current) {
			URL.revokeObjectURL(previewUrlRef.current);
			previewUrlRef.current = null;
		}
	}, []);

	const resetState = useCallback(() => {
		revokePreviewUrl();
		setSelectedFile(null);
		setDocumentType('');
		setPreviewUrl(null);
		setError(null);
		setUploading(false);
		if (fileInputRef.current) fileInputRef.current.value = '';
	}, [revokePreviewUrl]);

	useEffect(() => {
		const resetTimer = window.setTimeout(resetState, 0);
		return () => window.clearTimeout(resetTimer);
	}, [open, resetState]);

	useEffect(() => {
		if (!open) return;
		const handleKey = (event: KeyboardEvent) => {
			if (event.key === 'Escape' && !uploading) onClose();
		};
		document.addEventListener('keydown', handleKey);
		return () => document.removeEventListener('keydown', handleKey);
	}, [open, onClose, uploading]);

	useEffect(() => () => revokePreviewUrl(), [revokePreviewUrl]);

	if (!open) return null;

	const handleFileSelected = (file: File | null) => {
		if (!file) return;
		if (!isPdf(file)) {
			setError('Please select a PDF file.');
			setSelectedFile(null);
			setPreviewUrl(null);
			revokePreviewUrl();
			if (fileInputRef.current) fileInputRef.current.value = '';
			return;
		}
		const objectUrl = URL.createObjectURL(file);
		revokePreviewUrl();
		previewUrlRef.current = objectUrl;
		setSelectedFile(file);
		setPreviewUrl(objectUrl);
		setError(null);
	};

	const handleSubmit = async () => {
		if (!selectedFile) return setError('Please select a PDF file.');
		if (!documentType) return setError('Please select a document type.');
		setUploading(true);
		setError(null);
		try {
			const result = await uploadDocument({
				file: selectedFile,
				document_type: documentType,
			});
			onClose();
			showToast(
				result.status === 'pending'
					? 'Uploaded document is pending for approval.'
					: result.status === 'ongoing'
						? 'Uploaded document is being processed.'
						: 'Document uploaded successfully.',
				'success',
			);
		} catch (err) {
			if (isAuthError(err)) {
				window.location.href = '/login';
				return;
			}
			const message =
				err instanceof ApiError
					? err.message
					: 'Document upload failed. Please retry.';
			setError(message);
			showToast(message, 'error');
		} finally {
			setUploading(false);
		}
	};

	return (
		<div className="fixed inset-0 z-(--z-dialog) flex items-center justify-center p-4">
			<section
				className="absolute inset-0 bg-black/40"
				onClick={() => !uploading && onClose()}
				aria-hidden="true"
			/>
			<section
				role="dialog"
				aria-modal="true"
				aria-labelledby="upload-document-title"
				className="relative z-10 flex max-h-[90vh] w-150 max-w-lg flex-col rounded-lg border border-border bg-surface shadow-lg"
			>
				<header className="shrink-0 border-b border-border p-4">
					<h2
						id="upload-document-title"
						className="text-lg font-semibold text-text-primary"
					>
						Upload Document
					</h2>
					<p className="mt-1 text-sm text-text-muted">
						Select a PDF document and assign its legal document
						type.
					</p>
				</header>

				<section className="flex-1 space-y-4 overflow-y-auto p-6 scrollbar-thin">
					<div className="space-y-3">
						<p className="text-sm font-medium text-text-primary">
							PDF file
						</p>
						<input
							ref={fileInputRef}
							type="file"
							accept=".pdf,application/pdf"
							disabled={uploading}
							className="hidden"
							onChange={(event) =>
								handleFileSelected(
									event.target.files?.[0] ?? null,
								)
							}
						/>
						<button
							type="button"
							onClick={() => fileInputRef.current?.click()}
							disabled={uploading}
							className="flex w-full items-center justify-center gap-2 rounded-sm border border-dashed border-border px-4 py-8 text-sm text-text-secondary hover:bg-hover disabled:opacity-50"
						>
							<i
								className="bi bi-cloud-arrow-up text-xl"
								aria-hidden="true"
							/>
							{selectedFile
								? selectedFile.name
								: 'Choose a PDF file'}
						</button>
						{previewUrl && (
							<iframe
								title="PDF preview"
								src={previewUrl}
								className="h-48 w-full rounded-sm border border-border"
							/>
						)}
					</div>
					<label
						className="block space-y-2 text-sm font-medium text-text-primary"
						htmlFor="document-type"
					>
						Document type
						<select
							id="document-type"
							value={documentType}
							disabled={uploading}
							onChange={(event) =>
								setDocumentType(
									event.target.value as LegalDocumentType,
								)
							}
							className="mt-1 w-full rounded-sm border border-border bg-background px-3 py-2 text-sm font-normal"
						>
							<option value="">Select a type</option>
							{LEGAL_DOCUMENT_TYPES.map((type) => (
								<option key={type.value} value={type.value}>
									{type.label}
								</option>
							))}
						</select>
					</label>
					{error && (
						<p role="alert" className="text-sm text-danger">
							{error}
						</p>
					)}
				</section>
				<footer className="flex shrink-0 justify-end gap-2 border-t border-border p-4">
					<button
						type="button"
						onClick={onClose}
						disabled={uploading}
						className="rounded-sm border border-border px-4 py-2 text-sm text-text-secondary hover:bg-hover disabled:opacity-50"
					>
						Cancel
					</button>
					<button
						type="button"
						onClick={() => void handleSubmit()}
						disabled={uploading}
						className="rounded-sm bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:opacity-90 disabled:opacity-50"
					>
						{uploading ? 'Uploading...' : 'Upload document'}
					</button>
				</footer>
			</section>
		</div>
	);
}
