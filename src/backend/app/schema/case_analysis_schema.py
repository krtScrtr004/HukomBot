from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

from backend.app.schema.mixin import PaginatableMixin


class CaseAnalysisGetByVersionNumber(PaginatableMixin, BaseModel):
    version_number: int
    case_analysis_session_id: Optional[UUID] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


# Case Analysis Session ======================================


class CaseAnalysisSessionCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}


# Case Fact ==================================================


class CaseFactCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    case_analysis_session_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}


# Case Fact Version ==========================================


class CaseFactVersionCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    case_fact_id: UUID
    version_number: int = Field(default=1)
    fact: str
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}


class CaseFactVersionUpdate(BaseModel):
    id: UUID
    version_number: Optional[int] = Field(default=None)
    fact: Optional[str] = Field(default=None)
    is_deleted: Optional[bool] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class CaseFactVersionGetBySessionId(PaginatableMixin, BaseModel):
    case_analysis_session_id: UUID

    model_config = {"arbitrary_types_allowed": True}


# Case Analysis Version =========================================


class CaseAnalysisVersionCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    case_analysis_session_id: UUID
    version_number: int = Field(default=1)
    answer: str
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}


class CaseAnalysisVersionFactCreate(BaseModel):
    case_analysis_version_id: UUID
    case_fact_version_id: UUID

    model_config = {"arbitrary_types_allowed": True}
