from typing import Optional
from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field, model_serializer, SerializerFunctionWrapHandler

from backend.app.schema.base_schema import BaseResponse


class ChunkCreate(BaseModel):
    document_id: UUID
    chunk_number: int = Field(gt=0, lt=9999)
    chunk_text: str = Field(min_length=1, max_length=1000)
    section: Optional[str] = Field(default=None, min_length=2, max_length=25)
    embedding: Optional[List] = Field(default=None)


class ChunkSearchKeyword(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)


class ChunkSearchVector(BaseModel):
    embeddings: List
    limit: int = Field(default=10, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)


class ChatPipelineResponse(BaseResponse):
    answer: str = Field(default=None)

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)

        result["data"] = {
            "answer": result.pop("answer"),
        }

        return result
