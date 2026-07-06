from fastapi import APIRouter, UploadFile, Depends, BackgroundTasks, File

from backend.app.enum.upload_status import UploadStatus
from backend.app.schema.document_schema import DocumentUploadResponse
from backend.app.service.document_service import DocumentService

from backend.app.api.v1.dependency import get_document_service

document_api_router = APIRouter()

@document_api_router.post("/")
async def upload_document(
    *,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks,
    service: DocumentService = Depends(get_document_service)
):
    contents = await file.read()
    
    document = await service.create_pending_document(file.filename, contents)
    background_tasks.add_task(
        service.process_document_pdf_upload, document.id, file.filename, contents
    )
    return DocumentUploadResponse(message=["File is uploading"], document_id=document.id, status=UploadStatus.ONGOING)
