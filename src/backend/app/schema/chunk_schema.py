from uuid import UUID, uuid4
from typing import List, Optional
from pydantic import BaseModel, Field

from backend.app.schema.mixin import PaginatableMixin


class ChunkCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4())
    document_id: UUID
    chunk_number: int = Field(gt=0, lt=9999)
    chunk_text: str = Field(min_length=1, max_length=10000)
    section: Optional[str] = Field(default=None, min_length=2, max_length=25)
    embedding: Optional[List] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class ChunkSearchKeyword(PaginatableMixin, BaseModel):
    text: str = Field(min_length=1, max_length=10000)


class ChunkSearchVector(PaginatableMixin, BaseModel):
    embeddings: List
