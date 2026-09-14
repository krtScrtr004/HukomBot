import { apiFetch } from '@/services/apiClient';
import type {
	CaseAnalysisAnswerFormat,
	CaseAnalysisCreateResponse,
	CaseAnalysisPipelineCaseFactsPayload,
	CaseAnalysisSessionPreviewResponse,
	CaseAnalysisVersionDetailResponse,
	CaseAnalysisVersionPreviewResponse,
	SessionListParams,
	PaginationParams,
} from '@/types/workspace';

function buildQuery(params: Record<string, string | number | null | undefined>): string {
	const search = new URLSearchParams();
	for (const [key, value] of Object.entries(params)) {
		if (value !== undefined && value !== null && value !== '') {
			search.set(key, String(value));
		}
	}
	const qs = search.toString();
	return qs ? `?${qs}` : '';
}

export async function listSessions(
	params: SessionListParams = {},
): Promise<CaseAnalysisSessionPreviewResponse[]> {
	const query = buildQuery({
		limit: params.limit ?? 10,
		offset: params.offset ?? 0,
		query: params.query?.trim(),
	});
	return apiFetch<CaseAnalysisSessionPreviewResponse[]>(
		`/case-analyses${query}`,
	);
}

export async function listVersions(
	sessionId: string,
	params: PaginationParams = {},
): Promise<CaseAnalysisVersionPreviewResponse[]> {
	const query = buildQuery({
		limit: params.limit ?? 10,
		offset: params.offset ?? 0,
	});
	return apiFetch<CaseAnalysisVersionPreviewResponse[]>(
		`/case-analyses/${sessionId}/versions${query}`,
	);
}

export async function getVersion(
	sessionId: string,
	versionNumber: number,
): Promise<CaseAnalysisVersionDetailResponse> {
	return apiFetch<CaseAnalysisVersionDetailResponse>(
		`/case-analyses/${sessionId}/versions/${versionNumber}`,
	);
}

export async function runCaseAnalysis(
	payload: CaseAnalysisPipelineCaseFactsPayload,
	answerFormat: CaseAnalysisAnswerFormat = 'html',
): Promise<CaseAnalysisCreateResponse> {
	return apiFetch<CaseAnalysisCreateResponse>('/case-analyses', {
		method: 'POST',
		body: payload,
		headers: {
			'X-Answer-Format': answerFormat,
		},
	});
}

export async function deleteSession(
	sessionId: string,
): Promise<{ case_analysis_session_id: string }> {
	return apiFetch<{ case_analysis_session_id: string }>(
		`/case-analyses/${sessionId}`,
		{ method: 'DELETE' },
	);
}
