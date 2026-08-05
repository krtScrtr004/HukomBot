from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field

from backend.hukom_bot.schema.mixin import PaginatableMixin
from backend.hukom_bot.enum.case_analysis_answer_format import CaseAnalysisAnswerFormat


class CaseAnalysisGetBySessionId(PaginatableMixin):
    case_analysis_session_id: UUID
    user_id: UUID | None = Field(default=None)


class CaseAnalysisGetByVersionNumber(PaginatableMixin):
    version_number: int
    case_analysis_session_id: UUID | None = Field(default=None)
    user_id: UUID | None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class CaseAnalysisGetByUserId(PaginatableMixin):
    user_id: UUID


class CaseAnalysisGeneratedAnswer(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    answer: str


# Case Analysis Session ======================================


class CaseAnalysisSessionCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}


class CaseAnalysisSessionPreviewResponse(BaseModel):
    case_analysis_session_id: UUID
    latest_version_id: UUID
    latest_version_title: str
    latest_version_number: int
    created_at: datetime
    updated_at: datetime


# Case Fact ==================================================


class CaseFactCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
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
    version_number: int | None = Field(default=None)
    fact: str | None = Field(default=None)
    is_deleted: bool | None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class CaseFactVersionGetManyBySessionIds(PaginatableMixin):
    case_analysis_session_ids: list[UUID]
    user_id: UUID | None = Field(default=None)


class CaseFactVersionResponse(BaseModel):
    case_fact_id: UUID
    case_fact_version_id: UUID
    version_number: int
    fact: str


# Case Analysis Version =========================================


class CaseAnalysisVersionCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    case_analysis_session_id: UUID
    title: str
    version_number: int = Field(default=1)
    answer: str = Field(min_length=1)
    answer_format: CaseAnalysisAnswerFormat
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = {"arbitrary_types_allowed": True}


class CaseAnalysisVersionPreviewResponse(BaseModel):
    id: UUID
    title: str
    version_number: int = Field(gt=0)
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True}


class CaseAnalysisVersionResponse(CaseAnalysisVersionPreviewResponse):
    answer: str = Field(min_length=0)
    answer_format: CaseAnalysisAnswerFormat

    case_facts: list[CaseFactVersionResponse] = Field(default_factory=[])


# Case Analysis Version Fact =========================================


class CaseAnalysisVersionFactCreate(BaseModel):
    case_analysis_version_id: UUID
    case_fact_version_id: UUID

    model_config = {"arbitrary_types_allowed": True}
