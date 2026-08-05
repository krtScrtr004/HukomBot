from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel, Field, model_validator, field_validator, Field

from backend.hukom_bot.enum.case_analysis_answer_format import CaseAnalysisAnswerFormat
from backend.hukom_bot.schema.case_analysis_schema import CaseAnalysisVersionResponse

# API Schemas ========================================

CASE_FACT_MIN_LEN = 8
CASE_FACT_MAX_LEN = 500


class CaseAnalysiPipelineCaseFactsHeader(BaseModel):
    answer_format: CaseAnalysisAnswerFormat = Field(
        default_factory=CaseAnalysisAnswerFormat.PLAINTEXT, alias="X-Answer-Format"
    )

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("answer_format", mode="before")
    @classmethod
    def lower_value(cls, value: str) -> str:
        if isinstance(value, str):
            return value.lower()
        return value


class CaseAnalysisPipelineCaseFactsPayload(BaseModel):
    case_analysis_session_id: UUID = Field(default=None)
    new_case_facts: list[str] | None = Field(default=None, min_length=1, max_length=10)
    updated_case_facts: dict[UUID, str] | None = Field(
        default=None, min_length=1, max_length=10
    )
    deleted_case_facts: list[UUID] | None = Field(
        default=None, min_length=1, max_length=10
    )

    @model_validator(mode="after")
    def atleast_one_list_required(self) -> CaseAnalysisPipelineCaseFactsPayload:
        if (
            not self.new_case_facts
            and not self.updated_case_facts
            and not self.deleted_case_facts
        ):
            raise ValueError("At least one list must have value")
        return self

    @model_validator(mode="after")
    def has_case_analysis_session_id_update_delete_list(self):
        if (
            self.updated_case_facts or self.deleted_case_facts
        ) and not self.case_analysis_session_id:
            raise ValueError(
                "Conversation id must be provided when editing / deleting a case fact"
            )
        return self

    @model_validator(mode="after")
    def is_allowed_case_fact(self) -> CaseAnalysisPipelineCaseFactsPayload:
        if self.new_case_facts is not None:
            for case_fact in self.new_case_facts:
                if (
                    len(case_fact) < CASE_FACT_MIN_LEN
                    or len(case_fact) > CASE_FACT_MAX_LEN
                ):
                    raise ValueError(
                        f"Each case fact must be between {CASE_FACT_MIN_LEN} and {CASE_FACT_MAX_LEN} only"
                    )

        if self.updated_case_facts is not None:
            for fact in self.updated_case_facts.values():
                if len(fact) < CASE_FACT_MIN_LEN or len(fact) > CASE_FACT_MAX_LEN:
                    raise ValueError(
                        f"Each case fact must be between {CASE_FACT_MIN_LEN} and {CASE_FACT_MAX_LEN} only"
                    )

        return self


# API Response ===================================================


class PostCaseAnalysisResponse(BaseModel):
    case_analysis_session_id: UUID = Field(default=None)
    case_analysis: CaseAnalysisVersionResponse


class GetCaseAnalysisResponse(BaseModel):
    case_analysis_session_id: UUID
    case_analysis: CaseAnalysisVersionResponse
