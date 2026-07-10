from __future__ import annotations
from uuid import UUID
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, model_validator


class CaseAnalysisSession(BaseModel):
    id: UUID
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())


class CaseFact(BaseModel):
    id: UUID
    case_analysis_session_id: UUID
    created_at: datetime = Field(default=datetime.now())

    # Navigation prop
    case_analysis_session: Optional[CaseAnalysisSession] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True, "from_attributes": True}

    @model_validator(mode="after")
    def resolve_case_analysis_session_id(self) -> CaseFact:
        if (
            self.case_analysis_session is not None
            and self.case_analysis_session_id is None
        ):
            self.case_analysis_session_id = self.case_analysis_session.id
        return self


class CaseFactVersion(BaseModel):
    id: UUID
    case_fact_id: UUID
    version_number: int = Field(default=1)
    fact: str
    is_deleted: bool = Field(default=False)
    created_at: datetime = Field(default=datetime.now())

    # Navigation prop
    case_fact: Optional[CaseFact] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True, "from_attributes": True}

    @model_validator(mode="after")
    def resolve_case_fact_id(self) -> CaseFactVersion:
        if self.case_fact is not None and self.case_fact_id is None:
            self.case_fact_id = self.case_fact.id
        return self


class CaseAnalysisVersion(BaseModel):
    id: UUID
    case_analysis_session_id: UUID
    answer: str
    created_at: datetime = Field(default=datetime.now())

    # Navigation prop
    case_analysis_session: Optional[CaseAnalysisSession] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True, "from_attributes": True}

    @model_validator(mode="after")
    def resolve_case_analysis_session_id(self) -> CaseAnalysisVersion:
        if self.case_analysis_session is not None and self.case_analysis_session_id:
            self.case_analysis_session_id = self.case_analysis_session.id
        return self


class CaseAnalysisVersionFact(BaseModel):
    case_analysis_version_id: UUID
    case_fact_version_id: UUID

    # Navigation prop
    case_analysis_version: CaseAnalysisSession
    case_fact_version: CaseFactVersion

    model_config = {"arbitrary_types_allowed": True, "from_attributes": True}

    @model_validator(mode="after")
    def resolve_ids(self) -> CaseAnalysisVersionFact:
        if (
            self.case_analysis_version is not None
            and self.case_analysis_version_id is None
        ):
            self.case_analysis_version_id = self.case_fact_version.id

        if self.case_fact_version is not None and self.case_fact_version_id is None:
            self.case_fact_version_id = self.case_fact_version.id

        return self
