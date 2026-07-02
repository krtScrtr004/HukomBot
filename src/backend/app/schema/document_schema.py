from __future__ import annotations
from typing import Optional
from datetime import datetime
from uuid import UUID
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
    title: str
    file_type: Optional[str] = None
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: str = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"from_attributes": True}


class DocumentSearch(BaseModel):
    title: Optional[str] = None
    file_type: Optional[str] = None
    limit: int = 10
    offset: int = 0

    @model_validator(mode="after")
    def at_least_one_required(self) -> DocumentSearch:
        if self.title is None and self.file_type is None:
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
