import { useCallback, useEffect, useRef, useState } from 'react';
import { ApiError, isAuthError } from '@/services/apiClient';
import { uploadDocument } from '@/services/documentService';
import type { LegalDocumentType } from '@/types/workspace';
import { useToast } from '@/contexts/ToastProvider';

interface UploadDocumentModalProps {
	open: boolean;
	onClose: () => void;
}

// Define the legal document types and their labels
const LEGAL_DOCUMENT_TYPES: { value: LegalDocumentType; label: string }[] = [
	{ value: 'contract', label: 'Contract' },
	{
		value: 'non_disclosure_agreement',
		label: 'Non-Disclosure Agreement',
	},
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
	{
		value: 'articles_of_incorporation',
		label: 'Articles of Incorporation',
	},
	{ value: 'bylaws', label: 'Bylaws' },
	{ value: 'board_resolution', label: 'Board Resolution' },
	{ value: 'shareholder_agreement', label: 'Shareholder Agreement' },
	{ value: 'minutes_of_meeting', label: 'Minutes of Meeting' },
	{ value: 'secretary_certificate', label: "Secretary's Certificate" },
	{
		value: 'general_information_sheet',
		label: 'General Information Sheet',
	},
	{ value: 'complaint', label: 'Complaint' },
	{ value: 'affidavit', label: 'Affidavit' },
	{ value: 'subpoena', label: 'Subpoena' },
	{ value: 'court_order', label: 'Court Order' },
	{ value: 'judgment', label: 'Judgment' },
	{
		value: 'supreme_court_decision',
		label: 'Supreme Court Decision',
	},
	{
		value: 'court_of_appeals_decision',
		label: 'Court of Appeals Decision',
	},
	{ value: 'motion', label: 'Motion' },
	{ value: 'summons', label: 'Summons' },
	{ value: 'pleading', label: 'Pleading' },
	{ value: 'brief_memorandum', label: 'Brief/Memorandum' },
	{
		value: 'last_will_and_testament',
		label: 'Last Will and Testament',
	},
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
	{
		value: 'trademark_registration',
		label: 'Trademark Registration',
	},
	{
		value: 'copyright_registration',
		label: 'Copyright Registration',
	},
	{ value: 'ip_assignment', label: 'IP Assignment' },
	{ value: 'certification', label: 'Certification' },
	{ value: 'waiver', label: 'Waiver' },
	{ value: 'notice', label: 'Notice' },
	{ value: 'other', label: 'Other' },
];

function isPdf(file: File): boolean {
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

	// Revoke the object URL when the component unmounts or when a new file is selected
	const revokePreviewUrl = useCallback(() => {
		if (previewUrlRef.current) {
			URL.revokeObjectURL(previewUrlRef.current);
			previewUrlRef.current = null;
		}
	}, []);

	// Reset the state when the modal is closed or when the component unmounts
	const resetState = useCallback(() => {
		revokePreviewUrl();
		setSelectedFile(null);
		setDocumentType('');
		setPreviewUrl(null);
		setError(null);
		setUploading(false);
		if (fileInputRef.current) {
			fileInputRef.current.value = '';
		}
	}, [revokePreviewUrl]);

	// Reset the state when the modal is closed
	useEffect(() => {
		const resetTimer = window.setTimeout(() => {
			resetState();
		}, 0);

		return () => window.clearTimeout(resetTimer);
	}, [open, resetState]);

	// Handle the Escape key to close the modal when it's open and not uploading
	useEffect(() => {
		if (!open) {
			return;
		}

		const handleKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape' && !uploading) {
				onClose();
			}
		};
		document.addEventListener('keydown', handleKey);
		return () => document.removeEventListener('keydown', handleKey);
	}, [open, onClose, uploading]);

	// Revoke the object URL when the component unmounts
	useEffect(() => {
		return () => {
			revokePreviewUrl();
		};
	}, [revokePreviewUrl]);

	if (!open) {
		return null;
	}

	const handleFileSelected = (file: File | null) => {
		if (!file) {
			return;
		}

		// Check if the selected file is a PDF
		if (!isPdf(file)) {
			setError('Please select a PDF file.');
			setSelectedFile(null);
			setPreviewUrl(null);
			revokePreviewUrl();
			if (fileInputRef.current) {
				fileInputRef.current.value = '';
			}
			return;
		}

		// Create an object URL for the selected file and set it as the preview URL
		const objectUrl = URL.createObjectURL(file);
		revokePreviewUrl();
		previewUrlRef.current = objectUrl;
		setSelectedFile(file);
		setPreviewUrl(objectUrl);
		setError(null);
	};

	// Handle the form submission to upload the document
	const handleSubmit = async () => {
		if (!selectedFile) {
			setError('Please select a PDF file.');
			return;
		}

		if (!documentType) {
			setError('Please select a document type.');
			return;
		}

		setUploading(true);
		setError(null);

		try {
			// Upload the document
			await uploadDocument({
				file: selectedFile,
				document_type: documentType,
			});
			onClose();

			showToast('Uploaded document is pending for approval.', 'success');
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
				className="relative z-10 w-150 max-w-lg rounded-lg bg-surface border border-border shadow-lg flex flex-col max-h-[90vh]"
			>
				{/* Heading */}
				<section className="p-4 border-b border-border shrink-0">
					<h2
						id="upload-document-title"
						className="text-lg font-semibold text-text-primary"
					>
						Upload Document
					</h2>

					<p className="text-sm text-text-muted mt-1">
						Select a PDF document and assign its legal document
						type.
					</p>
				</section>

				<section className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
					{/* File upload selection */}
					<div className="space-y-3">
						<label className="text-sm font-medium text-text-primary">
							<p className="mb-2">PDF file</p>
						</label>

						{/* Hidden file input */}
						<input
							ref={fileInputRef}
							type="file"
							accept=".pdf,application/pdf"
							disabled={uploading}
							className="hidden"
							onChange={(e) =>
								handleFileSelected(e.target.files?.[0] ?? null)
							}
						/>

						{/* Button toggler */}
						<button
							type="button"
							onClick={() => fileInputRef.current?.click()}
							disabled={uploading}
							className="w-full min-h-24 rounded-sm border border-dashed border-border bg-surface-muted px-4 py-3 text-left hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
						>
							<span className="flex items-center gap-3">
								<i
									className="bi bi-file-earmark-pdf text-xl text-danger"
									aria-hidden="true"
								/>
								<span className="min-w-0">
									<span className="block text-sm font-medium text-text-primary truncate">
										{selectedFile
											? selectedFile.name
											: 'Choose a PDF file'}
									</span>

									<span className="block text-xs text-text-muted mt-1">
										PDF files only
									</span>
								</span>
							</span>
						</button>
					</div>

					{/* Document type selection */}
					<div className="space-y-3">
						<label
							htmlFor="document-type"
							className="text-sm font-medium text-text-primary"
						>
							<p className="mb-2">Document type</p>
						</label>

						<select
							id="document-type"
							value={documentType}
							disabled={uploading}
							onChange={(e) =>
								setDocumentType(
									e.target.value as LegalDocumentType | '',
								)
							}
							className="w-full h-(--input-height) rounded-sm border border-border bg-background px-3 text-sm text-text-primary focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
						>
							<option value="">Select document type</option>
							{LEGAL_DOCUMENT_TYPES.sort(
								(a, b) => a.label.localeCompare(b.label), // Sort by label in ascending order
							).map((type) => (
								<option key={type.value} value={type.value}>
									{type.label}
								</option>
							))}
						</select>
					</div>

					{/*  File preview, if selected */}
					{previewUrl && (
						<div className="space-y-2">
							<h3 className="text-sm font-medium text-text-primary">
								Preview
							</h3>
							<iframe
								src={previewUrl}
								className="w-full h-64 border border-border rounded-sm"
								title="Document preview"
							/>
						</div>
					)}

					{error && (
						<p className="text-sm text-danger" role="alert">
							{error}
						</p>
					)}
				</section>

				{/* Action buttons */}
				<section className="p-4 border-t border-border flex justify-end gap-3 shrink-0">
					<button
						type="button"
						onClick={onClose}
						disabled={uploading}
						className="px-4 py-2 rounded-sm text-sm font-medium border border-border text-text-primary hover:bg-hover focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
					>
						Cancel
					</button>

					<button
						type="button"
						onClick={() => void handleSubmit()}
						disabled={uploading}
						className="px-4 py-2 rounded-sm text-sm font-medium bg-primary text-primary-foreground hover:opacity-90 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary disabled:opacity-50"
					>
						{uploading ? 'Uploading...' : 'Upload'}
					</button>
				</section>

				{/* Uploading overlay */}
				{uploading && (
					<div className="absolute inset-0 bg-surface-overlay/80 flex items-center justify-center rounded-lg">
						<div className="flex flex-col items-center gap-3">
							<div className="w-10 h-10 border-3 border-border border-t-primary rounded-full animate-spin" />
							<p className="text-sm text-text-secondary">
								Uploading document...
							</p>
						</div>
					</div>
				)}
			</section>
		</div>
	);
}
