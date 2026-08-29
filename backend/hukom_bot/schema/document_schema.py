from __future__ import annotations

from pathlib import Path
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator
from backend.hukom_bot.schema.user_schema import UserResponse
from backend.hukom_bot.schema.mixin import PaginatableMixin, OrderableMixin
from backend.hukom_bot.enum.upload_status import UploadStatus
from backend.hukom_bot.enum.legal_document_type import LegalDocumentType


class DocumentCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    original_file_name: str = Field(min_length=1, max_length=300)
    upload_file_name: UUID = Field(default_factory=uuid4)
    document_type: LegalDocumentType
    file_type: str = Field(min_length=1, max_length=20)
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: str | None = Field(default=None, max_length=500)
    digest: bytes
    uploader_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class DocumentUpdateBase(BaseModel):
    original_file_name: str | None = Field(default=None, min_length=1, max_length=300)
    document_type: LegalDocumentType | None = Field(default=None)
    upload_status: UploadStatus | None = Field(default=None)

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class DocumentUpdate(DocumentUpdateBase):
    id: UUID
    upload_file_name: UUID | None = Field(default=None)
    file_type: str | None = Field(default=None, min_length=1, max_length=20)
    upload_error: str | None = Field(default=None, max_length=500)


class DocumentUpdatePayload(DocumentUpdateBase):
    pass


class DocumentSearch(PaginatableMixin, OrderableMixin):
    query: str | None = Field(default=None, min_length=3, max_length=256)
    upload_status: UploadStatus | None = Field(default=None)

    column: list[str] = Field(default_factory=lambda: ["original_file_name"])

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class DocumentGetAll(PaginatableMixin, OrderableMixin):
    upload_status: UploadStatus | None = Field(default=None)
    column: list[str] = Field(default_factory=lambda: ["original_file_name"])

    model_config = {"arbitrary_types_allowed": True}


class DocumentMetadata(BaseModel):
    file_path: Path
    original_file_name: str
    upload_file_name: UUID
    document_type: LegalDocumentType
    suffix: str
    digest: bytes

    model_config = {"arbitrary_types_allowed": True}


# API Schemas ========================================


class ApproveDocumentUploadPayload(BaseModel):
    document_type: LegalDocumentType | None = Field(default=None)


# API Response ======================================================


class DocumentResponse(BaseModel):
    id: UUID
    original_file_name: str
    upload_file_name: UUID
    document_type: LegalDocumentType
    file_type: str
    upload_status: UploadStatus
    upload_error: str | None
    uploader: UserResponse
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True}


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    status: UploadStatus = Field(default=UploadStatus.PENDING)

    model_config = {"arbitrary_types_allowed": True, "use_enum_values": True}


class DocumentUploadStatusResponse(BaseModel):
    status_value: UploadStatus

    model_config = {"arbitrary_types_allowed": True, "use_enum_values": True}
