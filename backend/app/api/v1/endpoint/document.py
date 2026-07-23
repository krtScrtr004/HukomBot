from uuid import UUID
from typing import Annotated
from fastapi import (
    APIRouter,
    UploadFile,
    Form,
    Depends,
    BackgroundTasks,
    File,
)
from backend.app.model.user_model import User
from backend.app.enum.legal_document_type import LegalDocumentType
from backend.app.schema.document_schema import ApproveDocumentUploadPayload
from backend.app.service.document_service import DocumentService
from backend.app.orchistrator.document_orchistrator import DocumentOrchistrator
from backend.app.schema.response_schema import SuccessResponse
from backend.app.api.v1.dependency import (
    verify_user,
    get_document_service,
    get_document_orchestrator,
)

document_api_router = APIRouter()


@document_api_router.post("/")
async def upload_document(
    file: Annotated[UploadFile, File(...)],
    document_type: Annotated[LegalDocumentType, Form(...)],
    user: Annotated[User, Depends(verify_user)],
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
):
    result = await orchistrator.create_pending(file, document_type)
    return SuccessResponse(message=result.message, data=result.data)


@document_api_router.post("/{document_id}/approve")
async def approve_document(
    document_id: UUID,
    payload: ApproveDocumentUploadPayload,
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
):
    result = await orchistrator.approve_document_upload(document_id, payload)
    document = result.data["document"]

    file = service.get_file_from_storage(document.upload_file_name, document.file_type)
    background_tasks.add_task(orchistrator.process_document_pdf_upload, document, file)

    return SuccessResponse(message=result.message, data=result.data["response"])


@document_api_router.get("/{document_id}/upload-status")
async def get_document_upload_status(
    document_id: UUID,
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
):
    status = await service.get_upload_status(document_id)
    return SuccessResponse(
        message=f"Document upload status is {status.value}",
        data=status
    )