from pydantic import BaseModel, HttpUrl, Field


class AdminDashboardData(BaseModel):
    active_user_count: int = Field(default=0, min=0)
    documents_count: int = Field(default=0, min=0)
    pending_document_count: int = Field(default=0, min=0)
    ongoing_document_count: int = Field(default=0, min=0)
    completed_document_count: int = Field(default=0, min=0)
    failed_document_count: int = Field(default=0, min=0)
    rejected_document_count: int = Field(default=0, min=0)
    chunks_count: int = Field(default=0, min=0)


class CloudinaryUploadResponse(BaseModel):
    public_id: str
    secure_url: HttpUrl
