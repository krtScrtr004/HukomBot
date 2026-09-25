import { apiFetch } from '@/services/apiClient';
import type {
	AdminDocumentListItem,
	AdminDocumentsQueryParams,
	AdminDocumentAnalytics,
} from '@/types/admin';
import type { LegalDocumentType, UploadStatus } from '@/types/workspace';

export async function getDocumentAnalytics(): Promise<AdminDocumentAnalytics> {
	return apiFetch<AdminDocumentAnalytics>('/admin/documents');
}

/** GET /documents/ with query params */
export async function listDocuments(
	params: AdminDocumentsQueryParams,
): Promise<AdminDocumentListItem[]> {
	const query = new URLSearchParams();
	if (params.query) query.set('query', params.query);
	if (params.upload_status) query.set('upload_status', params.upload_status);
	if (params.uploader_id) query.set('uploader_id', params.uploader_id);
	if (params.limit !== undefined) query.set('limit', String(params.limit));
	if (params.offset !== undefined) query.set('offset', String(params.offset));
	if (params.column?.length) query.set('column', params.column.join(','));
	if (params.order) query.set('order', params.order);
	const qs = query.toString();
	return apiFetch<AdminDocumentListItem[]>(
		`/documents/${qs ? `?${qs}` : ''}`,
	);
}

/** PATCH /documents/{document_id}/approve */
export async function approveDocument(
	documentId: string,
	documentType?: LegalDocumentType,
): Promise<{ document_id: string; status: UploadStatus }> {
	const body: { document_type?: LegalDocumentType } = {};
	if (documentType) body.document_type = documentType;
	return apiFetch<{ document_id: string; status: UploadStatus }>(
		`/documents/${documentId}/approve`,
		{ method: 'PATCH', body },
	);
}

/** PATCH /documents/{document_id} */
export async function rejectDocument(
	documentId: string,
	rejectionMessage: string,
): Promise<{ id: string }> {
	return apiFetch<{ id: string }>(`/documents/${documentId}`, {
		method: 'PATCH',
		body: {
			upload_status: 'rejected',
			rejection_message: rejectionMessage,
		},
	});
}

/** DELETE /documents/{document_id} */
export async function deleteDocument(
	documentId: string,
): Promise<{ id: string }> {
	return apiFetch<{ id: string }>(`/documents/${documentId}`, {
		method: 'DELETE',
	});
}

/** POST /documents/bulk-delete */
export async function bulkDeleteDocuments(
	ids: string[],
): Promise<{ ids: string[] }> {
	return apiFetch<{ ids: string[] }>('/documents/bulk-delete', {
		method: 'POST',
		body: ids,
	});
}

/** GET /documents/{document_id} */
export async function getDocumentInfo(
	documentId: string,
): Promise<AdminDocumentListItem> {
	return apiFetch<AdminDocumentListItem>(`/documents/${documentId}`);
}



