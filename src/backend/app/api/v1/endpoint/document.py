from uuid import UUID
from typing import Optional, Annotated
from fastapi import (
    APIRouter,
    UploadFile,
    Form,
    Depends,
    BackgroundTasks,
    File,
)

from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType
from backend.app.schema.document_schema import ApproveDocumentUpload
from backend.app.service.document_service import DocumentService

from backend.app.api.v1.dependency import get_document_service

document_api_router = APIRouter()


@document_api_router.post("/")
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    document_type: Annotated[LegalDocumentType, Form(...)],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    return await service.create_pending_document(file, document_type)


@document_api_router.post("/{document_id}/approve")
async def approve_document(
    document_id: UUID,
    payload: ApproveDocumentUpload,
    background_tasks: BackgroundTasks,
    service: Annotated[DocumentService, Depends(get_document_service)],    
):
    return await service.approve_document_upload(document_id, payload, background_tasks)
    
