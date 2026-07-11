from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

# Case Analysis Session ========================================


class CaseAnalysisSessionCreate(BaseModel):
    id: UUID
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())


class CaseFactCreate(BaseModel):
    id: UUID
    case_analysis_session_id: UUID
    created_at: datetime = Field(default=datetime.now())


class CaseFactVersionCreate(BaseModel):
    id: UUID
    case_fact_id: UUID
    version_number: int = Field(default=1)
    fact: str
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default=datetime.now())


class CaseAnalysisVersionCreate(BaseModel):
    id: UUID
    case_analysis_session_id: UUID
    version_number: int = Field(default=1)
    answer: str
    created_at: datetime = Field(default=datetime.now())


class CaseAnalysisVersionFactCreate(BaseModel):
    case_analysis_version_id: UUID
    case_fact_version_id: UUID
