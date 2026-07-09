from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime

from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType


class Document(BaseModel):
    id: UUID
    original_file_name: str = Field(min_length=1, max_length=300)
    upload_file_name: UUID = Field(default=uuid4())
    document_type: LegalDocumentType
    file_type: Optional[str] = Field(default=None, min_length=1, max_length=20)
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: Optional[str] = Field(default=None, max_length=500)
    digest: bytes
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {"arbitrary_types_allowed": True}
