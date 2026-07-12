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

from backend.app.schema.base_schema import BaseResponse


class ChatPipelineResponse(BaseResponse):
    conversation_id: UUID = Field(default=None)
    answer: str

    @classmethod
    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)

        result["data"] = {
            "conversation_id": result.pop("conversation_id"),
            "answer": result.pop("answer"),
        }

        return result


# API Schemas ========================================

CASE_FACT_MIN_LEN = 8
CASE_FACT_MAX_LEN = 500


class CaseAnalysisCaseFactsPayload(BaseModel):
    conversation_id: Optional[UUID] = Field(default=None)
    new_case_facts: Optional[List[str]] = Field(
        default_factory=[], min_length=1, max_length=10
    )
    updated_case_facts: Optional[List[Dict[UUID, str]]] = Field(
        default_factory=[], min_length=1, max_length=10
    )
    deleted_case_facts: Optional[List[UUID]] = Field(
        default_factory=[], min_length=1, max_length=10
    )
    
    @classmethod
    @model_validator(mode="after")
    def atleast_one_list_required(self) -> CaseAnalysisCaseFactsPayload:
        if not self.new_case_facts and not self.updated_case_facts and not self.deleted_case_facts:
            return ValueError("At least one list must have value")
        return self
    
    @classmethod
    @model_validator(mode="after")
    def has_conversation_id_update_delete_list(self):
        if len(self.updated_case_facts) > 0 or len(self.deleted_case_facts) > 0 and not self.conversation_id:
            return ValueError("Conversation id must be provided when editing / deleting a case fact")
        return self

    @classmethod
    @model_validator(mode="after")
    def is_allowed_case_fact(self) -> CaseAnalysisCaseFactsPayload:
        for case_fact in self.new_case_facts:
            if len(case_fact) < CASE_FACT_MIN_LEN or len(case_fact) > CASE_FACT_MAX_LEN:
                raise ValueError(
                    f"Each case fact must be between {CASE_FACT_MIN_LEN} and {CASE_FACT_MAX_LEN} only"
                )

        for case_fact in self.updated_case_facts:
            fact = next(iter(case_fact.values()))
            if len(fact) < CASE_FACT_MIN_LEN or len(fact) > CASE_FACT_MAX_LEN:
                raise ValueError(
                    f"Each case fact must be between {CASE_FACT_MIN_LEN} and {CASE_FACT_MAX_LEN} only"
                )

        return self


class UpdateCaseFactsPayload(BaseModel):
    case_facts: List[Dict[UUID, str]] = Field(min_length=1, max_length=10)

    model_config = {"arbitrary_types_allowed": True}

    @classmethod
    @model_validator(mode="after")
    def is_allowed_case_fact(self) -> UpdateCaseFactsPayload:
        for case_fact in self.case_facts:
            fact = next(iter(case_fact.values()))
            if len(fact) < CASE_FACT_MIN_LEN or len(fact) > CASE_FACT_MAX_LEN:
                raise ValueError(
                    f"Each case fact must be between {CASE_FACT_MIN_LEN} and {CASE_FACT_MAX_LEN} only"
                )

        return self
