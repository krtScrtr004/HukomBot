from __future__ import annotations
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    model_serializer,
    SerializerFunctionWrapHandler,
)

from backend.app.schema.base_schema import BaseResponse
from backend.app.enum.upload_status import UploadStatus


class DocumentCreate(BaseModel):
    original_file_name: str = Field(min_length=1, max_length=300)
    upload_file_name: UUID = Field(default=uuid4())
    file_type: Optional[str] = Field(default=None, min_length=1, max_length=20)
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class DocumentUpdate(BaseModel):
    id: UUID
    original_file_name: Optional[str] = Field(default=None, min_length=1, max_length=300)
    upload_file_name: Optional[UUID] = Field(default=None)
    file_type: Optional[str] = Field(default=None, min_length=1, max_length=20)
    upload_status: Optional[UploadStatus] = Field(default=None)
    upload_error: Optional[str] = Field(default=None, max_length=500)

    model_config = {"from_attributes": True}


class DocumentSearch(BaseModel):
    original_file_name: Optional[str] = Field(default=None, min_length=1, max_length=300)
    file_type: Optional[str] = Field(default=None, min_length=1, max_length=20)
    limit: int = Field(default=10, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def at_least_one_required(self) -> DocumentSearch:
        if self.original_file_name is None and self.file_type is None:
            raise ValueError("At least one of 'title' or 'file_type' must be provided")
        return self


class DocumentUploadResponse(BaseResponse):
    document_id: UUID
    status: UploadStatus = Field(default=UploadStatus.PENDING)

    model_config = {"arbitrary_types_allowed": True, "use_enum_values": True}

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)

        result["data"] = {
            "document_id": result.pop("document_id"),
            "status": result.pop("status"),
        }

        return result
