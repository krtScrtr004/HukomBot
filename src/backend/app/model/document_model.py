from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

from backend.app.enum.upload_status import UploadStatus


class Document(BaseModel):
    id: UUID
    title: str = Field(min_length=1, max_length=300)
    file_type: Optional[str] = Field(default=None, min_length=1, max_length=20)
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = {"arbitrary_types_allowed": True}
