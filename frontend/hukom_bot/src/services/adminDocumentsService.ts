import { apiFetch } from '@/services/apiClient';
import type {
	AdminDocumentListItem,
	AdminDocumentsQueryParams,
} from '@/types/admin';
import type { LegalDocumentType, UploadStatus } from '@/types/workspace';

/** GET /api/v1/documents/ with query params */
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
		`/api/v1/documents/${qs ? `?${qs}` : ''}`,
	);
}

/** PATCH /api/v1/documents/{document_id}/approve */
export async function approveDocument(
	documentId: string,
	documentType?: LegalDocumentType,
): Promise<{ document_id: string; status: UploadStatus }> {
	const body: { document_type?: LegalDocumentType } = {};
	if (documentType) body.document_type = documentType;
	return apiFetch<{ document_id: string; status: UploadStatus }>(
		`/api/v1/documents/${documentId}/approve`,
		{ method: 'PATCH', body },
	);
}

/** PATCH /api/v1/documents/{document_id} */
export async function rejectDocument(
	documentId: string,
	rejectionMessage: string,
): Promise<{ id: string }> {
	return apiFetch<{ id: string }>(`/api/v1/documents/${documentId}`, {
		method: 'PATCH',
		body: {
			upload_status: 'rejected',
			rejection_message: rejectionMessage,
		},
	});
}
