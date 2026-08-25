import { apiFetch } from "@/services/apiClient";
import type { UploadDocumentPayload, UploadDocumentResponse } from "@/types/workspace";

function createFormData(params: UploadDocumentPayload): FormData {
    const fd = new FormData();
    fd.append("file", params.file);
    if (params.document_type) {
        fd.append("document_type", params.document_type);
    }

    return fd;
}

export async function uploadDocument(
    params: UploadDocumentPayload
): Promise<UploadDocumentResponse> {
    return apiFetch<UploadDocumentResponse>('/api/v1/documents', {
        method: 'POST',
        body: createFormData(params)
    });
}