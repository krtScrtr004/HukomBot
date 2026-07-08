from typing import Annotated
from fastapi import APIRouter, UploadFile, Form, Depends, BackgroundTasks, File

from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType
from backend.app.schema.document_schema import DocumentUploadResponse
from backend.app.service.document_service import DocumentService

from backend.app.api.v1.dependency import get_document_service

document_api_router = APIRouter()


@document_api_router.post("/")
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    document_type: Annotated[LegalDocumentType, Form(...)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    background_tasks: BackgroundTasks,
):
    contents = await file.read()

    document = await service.create_pending_document(
        file_name=file.filename, document_type=document_type, contents=contents
    )
    background_tasks.add_task(
        service.process_document_pdf_upload, document.id, file.filename, contents
    )
    return DocumentUploadResponse(
        message=["File is pending"],
        document_id=document.id,
        status=UploadStatus.PENDING,
    )
