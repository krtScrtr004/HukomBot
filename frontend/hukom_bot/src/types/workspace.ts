/***********************************************/

export type CaseAnalysisAnswerFormat = 'plaintext' | 'html' | 'markdown';

/***********************************************/

export type UploadStatus =
	| 'pending'
	| 'ongoing'
	| 'completed'
	| 'failed'
	| 'rejected';

export type LegalDocumentType =
	// Contracts & Agreements
	| 'contract'
	| 'non_disclosure_agreement'
	| 'service_agreement'
	| 'employment_contract'
	| 'lease_agreement'
	| 'partnership_agreement'
	| 'memorandum_of_agreement'
	| 'memorandum_of_understanding'
	| 'addendum_amendment'
	| 'franchise_agreement'
	| 'indemnity_agreement'

	// Corporate Documents
	| 'articles_of_incorporation'
	| 'bylaws'
	| 'board_resolution'
	| 'shareholder_agreement'
	| 'minutes_of_meeting'
	| 'secretary_certificate'
	| 'general_information_sheet'

	// Court & Litigation
	| 'complaint'
	| 'affidavit'
	| 'subpoena'
	| 'court_order'
	| 'judgment'
	| 'supreme_court_decision'
	| 'court_of_appeals_decision'
	| 'motion'
	| 'summons'
	| 'pleading'
	| 'brief_memorandum'

	// Personal & Estate
	| 'last_will_and_testament'
	| 'deed_of_sale'
	| 'power_of_attorney'
	| 'trust_deed'
	| 'birth_certificate'
	| 'marriage_contract'
	| 'deed_of_donation'
	| 'prenuptial_agreement'

	// Government & Regulatory
	| 'permit'
	| 'license'
	| 'government_issued_id'
	| 'tax_declaration'
	| 'tax_clearance'
	| 'certificate_of_registration'

	// Regulatory & Administrative
	| 'constitution'
	| 'republic_act'
	| 'revenue_regulation'
	| 'revenue_memorandum_circular'
	| 'executive_order'
	| 'municipal_ordinance'

	// Financial
	| 'promissory_note'
	| 'deed_of_mortgage'
	| 'loan_agreement'
	| 'invoice'
	| 'receipt'
	| 'audited_financial_statement'

	// Intellectual Property
	| 'patent'
	| 'trademark_registration'
	| 'copyright_registration'
	| 'ip_assignment'

	// Miscellaneous
	| 'certification'
	| 'waiver'
	| 'notice'
	| 'other';

/***********************************************/

export interface UploadDocumentPayload {
	file: File;
	document_type: LegalDocumentType;
}

export interface UploadDocumentResponse {
	id: string;
	status: UploadStatus;
}

export interface CaseFactResponse {
	id: string;
	case_fact_id: string;
	case_fact_version_id: string;
	version_number: number;
	fact: string;
}

export interface CaseAnalysisVersionResponse {
	id: string;
	title: string;
	version_number: number;
	answer: string;
	answer_format: CaseAnalysisAnswerFormat;
	created_at: string;
	case_facts: CaseFactResponse[];
}

export interface CaseAnalysisVersionPreviewResponse {
	id: string;
	title: string;
	version_number: number;
	created_at: string;
}

export interface CaseAnalysisSessionPreviewResponse {
	case_analysis_session_id: string;
	latest_version_id: string;
	latest_version_number: number;
	latest_version_title: string;
	created_at: string;
	updated_at: string;
}

export interface CaseAnalysisPipelineCaseFactsPayload {
	case_analysis_session_id?: string | null;
	new_case_facts?: string[];
	updated_case_facts?: Record<string, string>;
	deleted_case_facts?: string[];
}

export interface CaseAnalysisCreateResponse {
	case_analysis_session_id: string;
	case_analysis: CaseAnalysisVersionResponse;
}

export interface CaseAnalysisVersionDetailResponse {
	case_analysis_session_id: string;
	case_analysis: CaseAnalysisVersionResponse;
}

export interface PaginationParams {
	limit?: number;
	offset?: number;
}

export interface SessionListParams extends PaginationParams {
	query?: string | null;
}

export interface ApiErrorDetail {
	field: string | null;
	issue: string;
}

export interface ApiErrorBody {
	code: string;
	message: string;
	details: ApiErrorDetail[];
}

export type FactStatus = 'unchanged' | 'modified' | 'new' | 'deleted';

export interface EditableCaseFact {
	tempId: string;
	case_fact_id: string | null;
	fact: string;
	originalFact: string;
	status: FactStatus;
}

export interface PendingChangesCounts {
	newFacts: number;
	modifiedFacts: number;
	deletedFacts: number;
}

export const CASE_FACT_MIN_LENGTH = 8;
export const CASE_FACT_MAX_LENGTH = 500;
export const CASE_FACT_MAX_COUNT = 10;
export const SESSIONS_PAGE_SIZE = 10;
export const VERSIONS_PAGE_SIZE = 10;
