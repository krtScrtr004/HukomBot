from __future__ import annotations
from typing import List
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    model_serializer,
    SerializerFunctionWrapHandler,
)

from backend.app.schema.base_schema import BaseResponse


class ChatPipelineResponse(BaseResponse):
    answer: str = Field(default=None)

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)

        result["data"] = {
            "answer": result.pop("answer"),
        }

        return result


# API Schemas ========================================


class CaseAnalysisCaseFacts(BaseModel):
    case_facts: List[str] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def is_allowed_case_fact(self) -> CaseAnalysisCaseFacts:
        MIN_LEN = 8
        MAX_LEN = 500

        for case_fact in self.case_facts:
            if not case_fact or len(case_fact) < MIN_LEN and len(case_fact) > MAX_LEN:
                raise ValueError(
                    f"Each case fact must be between {MIN_LEN} and {MAX_LEN} only"
                )
