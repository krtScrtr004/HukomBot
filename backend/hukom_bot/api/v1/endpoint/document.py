from uuid import UUID
from typing import Annotated
from fastapi import (
    APIRouter,
    UploadFile,
    Path,
    Query,
    Form,
    Body,
    Depends,
    BackgroundTasks,
    File,
)
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.legal_document_type import LegalDocumentType
from backend.hukom_bot.schema.document_schema import (
    DocumentSearch,
    DocumentUpdatePayload,
    ApproveDocumentUploadPayload,
)
from backend.hukom_bot.service.document_service import DocumentService
from backend.hukom_bot.orchistrator.document_orchistrator import DocumentOrchistrator
from backend.hukom_bot.schema.response_schema import SuccessResponse
from backend.hukom_bot.exception.app_exception import NotFoundException
from backend.hukom_bot.util.document_caster import DocumentCaster
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    rate_limit,
    get_document_service,
    get_document_orchestrator,
    require_role,
)

document_api_router = APIRouter()


@document_api_router.get("/")
async def get_documents(
    query: Annotated[DocumentSearch, Query()],
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    result = await orchistrator.search_pipeline(param=query)

    return SuccessResponse(message="Documents retrieved successfully", data=result)


@document_api_router.get("/{document_id}")
async def get_document_info(
    document_id: UUID,
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    document = await orchistrator.get_by_id(id=document_id)
    if not document:
        raise NotFoundException(
            message="Document not found",
            details=[f"Document's info with an id: {document_id} is not found"],
        )

    return SuccessResponse(message=f"Document retrieved successfully", data=document)


@document_api_router.get("/{document_id}/upload-status")
async def get_document_upload_status(
    document_id: UUID,
    service: Annotated[DocumentService, Depends(get_document_service)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    status = await service.get_upload_status(document_id)

    return SuccessResponse(
        message=f"Document upload status is {status.value}", data=status
    )


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


@document_api_router.patch("/{document_id}")
async def update_document(
    document_id: Annotated[UUID, Path()],
    payload: Annotated[DocumentUpdatePayload, Body()],
    user: Annotated[User, Depends(verify_user)],
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
    _rl=Depends(rate_limit(limit=10, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    await orchistrator.update_pipeline(
        document=DocumentCaster.update_payload_to_update(
            id=document_id, document=payload
        )
    )
    return SuccessResponse(
        message="Document info updated successfully", data={"id": document_id}
    )


@document_api_router.patch("/{document_id}/approve")
async def approve_document(
    document_id: Annotated[UUID, Path()],
    payload: Annotated[ApproveDocumentUploadPayload, Body()],
    background_tasks: BackgroundTasks,
    service: Annotated[DocumentService, Depends(get_document_service)],
    orchistrator: Annotated[DocumentOrchistrator, Depends(get_document_orchestrator)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=10, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    result = await orchistrator.approve_document_upload(document_id, payload)
    document = result.data["document"]

    file = service.get_file_from_storage(document.upload_file_name, document.file_type)
    background_tasks.add_task(orchistrator.process_document_pdf_upload, document, file)

    return SuccessResponse(message=result.message, data=result.data["response"])
