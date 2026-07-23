from pydantic import BaseModel, Field, model_serializer, SerializerFunctionWrapHandler
from uuid import UUID, uuid4
from datetime import datetime

from backend.app.model.user_model import User
from backend.app.enum.upload_status import UploadStatus
from backend.app.enum.legal_document_type import LegalDocumentType


class Document(BaseModel):
    id: UUID
    original_file_name: str
    upload_file_name: UUID = Field(default=uuid4())
    document_type: LegalDocumentType
    file_type: str|None = Field(default=None)
    upload_status: UploadStatus = Field(default=UploadStatus.PENDING)
    upload_error: str|None = Field(default=None)
    digest: bytes
    uploader_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    
    # Navigation Property
    uploader: User|None = Field(default=None)
    
    model_config = {"arbitrary_types_allowed": True}
    
    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)
        result.pop("uploader")
        return result
        
