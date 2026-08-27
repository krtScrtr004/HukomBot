from uuid import UUID
from typing import Annotated
from fastapi import (
    APIRouter,
    UploadFile,
    Path,
    Form,
    Body,
    Depends,
    BackgroundTasks,
    File,
)
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.legal_document_type import LegalDocumentType
from backend.hukom_bot.enum.upload_status import UploadStatus
from backend.hukom_bot.schema.document_schema import (
    DocumentUpdatePayload,
    ApproveDocumentUploadPayload,
    DocumentUpdateBase,
)
from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.orchistrator.document_orchistrator import DocumentOrchistrator
from backend.hukom_bot.schema.response_schema import SuccessResponse
from backend.hukom_bot.util.document_caster import DocumentCaster
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    rate_limit,
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
    _=Depends(rate_limit(limit=5, window=60)),
):
    result = await orchistrator.create_pending(
        user_id=user.id, file=file, document_type=document_type
    )
    return SuccessResponse(message=result.message, data=result.data)


@document_api_router.patch("/{document_id}/approve")
async def approve_document(
    document_id: Annotated[UUID, Path()],
    payload: Annotated[ApproveDocumentUploadPayload, Body()],
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
    _=Depends(rate_limit(limit=10, window=60)),
):
    result = await orchistrator.approve_document_upload(document_id, payload)
    document = result.data["document"]

    file = service.get_file_from_storage(document.upload_file_name, document.file_type)
    background_tasks.add_task(orchistrator.process_document_pdf_upload, document, file)

    return SuccessResponse(message=result.message, data=result.data["response"])


@document_api_router.patch("/{document_id}/")
async def update_document(
    document_id: Annotated[UUID, Path()],
    payload: Annotated[DocumentUpdatePayload, Body()],
    # user: Annotated[User, Depends(verify_user)],
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
    # _=Depends(rate_limit(limit=10, window=60))
):
    await orchistrator.update_pipeline(
        document=DocumentCaster.update_payload_to_update(
            id=document_id, document=payload
        )
    )
    return SuccessResponse(
        message="Document info updated successfully", data={"id": document_id}
    )


@document_api_router.get("/{document_id}/upload-status")
async def get_document_upload_status(
    document_id: UUID,
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[DocumentService, Depends(get_document_service)],
    _=Depends(rate_limit(limit=60, window=60)),
):
    status = await service.get_upload_status(document_id)
    return SuccessResponse(
        message=f"Document upload status is {status.value}", data=status
    )
