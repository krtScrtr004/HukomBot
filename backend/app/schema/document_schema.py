from __future__ import annotations

from pathlib import Path
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, model_validator

from backend.app.schema.mixin import PaginatableMixin
from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType


class DocumentCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    original_file_name: str = Field(min_length=1, max_length=300)
    upload_file_name: UUID = Field(default_factory=uuid4)
    document_type: LegalDocumentType
    file_type: str | None = Field(default=None, min_length=1, max_length=20)
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: str | None = Field(default=None, max_length=500)
    digest: bytes
    uploader_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class DocumentUpdate(BaseModel):
    id: UUID
    original_file_name: str | None = Field(default=None, min_length=1, max_length=300)
    upload_file_name: UUID | None = Field(default=None)
    document_type: LegalDocumentType | None = Field(default=None)
    file_type: str | None = Field(default=None, min_length=1, max_length=20)
    upload_status: UploadStatus | None = Field(default=None)
    upload_error: str | None = Field(default=None, max_length=500)

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}


class DocumentSearch(PaginatableMixin):
    original_file_name: str | None = Field(default=None, min_length=1, max_length=300)
    document_type: LegalDocumentType
    file_type: str | None = Field(default=None, min_length=1, max_length=20)

    model_config = {"from_attributes": True, "arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def at_least_one_required(self) -> DocumentSearch:
        if self.original_file_name is None and self.file_type is None:
            raise ValueError("At least one of 'title' or 'file_type' must be provided")
        return self


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


class DocumentUploadResponse(BaseModel):
    document_id: UUID
    status: UploadStatus = Field(default=UploadStatus.PENDING)

    model_config = {"arbitrary_types_allowed": True, "use_enum_values": True}


class DocumentUploadStatusResponse(BaseModel):
    status_value: UploadStatus

    model_config = {"arbitrary_types_allowed": True, "use_enum_values": True}
