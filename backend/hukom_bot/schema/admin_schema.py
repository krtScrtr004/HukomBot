from pydantic import BaseModel, Field


class DocumentStatusCount(BaseModel):
    pending: int = Field(default=0, min=0)
    ongoing: int = Field(default=0, min=0)
    completed: int = Field(default=0, min=0)
    failed: int = Field(default=0, min=0)
    rejected: int = Field(default=0, min=0)


class DocumentWeeklyCount(BaseModel):
    monday: int = Field(default=0, min=0)
    tuesday: int = Field(default=0, min=0)
    wednesday: int = Field(default=0, min=0)
    thursday: int = Field(default=0, min=0)
    friday: int = Field(default=0, min=0)
    saturday: int = Field(default=0, min=0)
    sunday: int = Field(default=0, min=0)


class AdminDashboardData(BaseModel):
    active_user_count: int = Field(default=0, min=0)
    documents_count: int = Field(default=0, min=0)
    document_status_count: DocumentStatusCount = Field(default=None)
    document_weekly_count: DocumentWeeklyCount = Field(default=None)
    chunks_count: int = Field(default=0, min=0)
    
    model_config = {"arbitrary_types_allowed": True}
