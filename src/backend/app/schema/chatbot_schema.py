from __future__ import annotations

from uuid import UUID
from typing import List, Optional, Dict
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    model_serializer,
    SerializerFunctionWrapHandler,
)

from backend.app.schema.mixin import ResponseMixin
from backend.app.model.case_analysis_model import CaseAnalysisVersion, CaseFactVersion

# API Response ===================================================

class ChatPipelineResponse(ResponseMixin, BaseModel):
    conversation_id: UUID = Field(default=None)
    answer: str

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)

        result["data"] = {
            "conversation_id": result.pop("conversation_id"),
            "answer": result.pop("answer"),
        }

        return result


class GetCaseAnalysisResponse(ResponseMixin, BaseModel):
    case_analysis_session_id: UUID
    case_analysis: List[CaseAnalysisFactResponse]
    
    model_config = {"arbitrary_types_allowed": True}

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)

        result["data"] = {
            "case_analysis_session_id": result.pop("case_analysis_session_id"),
            "case_analysis": result.pop("case_analysis"),
        }

        return result


class CaseAnalysisFactResponse(BaseModel):
    case_analysis: CaseAnalysisVersion
    case_facts: List[CaseFactVersion]

    model_config = {"arbitrary_types_allowed": True}


# API Schemas ========================================

CASE_FACT_MIN_LEN = 8
CASE_FACT_MAX_LEN = 500


class CaseAnalysisPipelineCaseFactsPayload(BaseModel):
    conversation_id: Optional[UUID] = Field(default=None)
    new_case_facts: Optional[List[str]] = Field(
        default=None, min_length=1, max_length=10
    )
    updated_case_facts: Optional[Dict[UUID, str]] = Field(
        default=None, min_length=1, max_length=10
    )
    deleted_case_facts: Optional[List[UUID]] = Field(
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
    def has_conversation_id_update_delete_list(self):
        if (
            self.updated_case_facts or self.deleted_case_facts
        ) and not self.conversation_id:
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
