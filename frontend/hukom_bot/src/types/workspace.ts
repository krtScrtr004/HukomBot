export type CaseAnalysisAnswerFormat = 'plaintext' | 'html' | 'markdown';

export type UserRole = 'standard' | 'contributor' | 'admin';

export interface UserResponse {
	id: string;
	first_name: string;
	last_name: string;
	email: string;
	role: UserRole;
}

export interface CaseFactResponse {
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
