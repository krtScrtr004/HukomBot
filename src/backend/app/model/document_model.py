from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from datetime import datetime

from backend.app.enum.upload_status import UploadStatus


class Document(BaseModel):
    id: UUID
    title: str
    file_type: Optional[str] = None
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: str = Field(default=None)
    created_at: datetime
    
    model_config = {"arbitrary_types_allowed": True}
