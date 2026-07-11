from uuid import UUID, uuid4
from typing import List, Optional
from pydantic import BaseModel, Field


class ChunkCreate(BaseModel):
    id: UUID = Field(default_factory=uuid4())
    document_id: UUID
    chunk_number: int = Field(gt=0, lt=9999)
    chunk_text: str = Field(min_length=1, max_length=10000)
    section: Optional[str] = Field(default=None, min_length=2, max_length=25)
    embedding: Optional[List] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class ChunkSearchKeyword(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    limit: int = Field(default=10, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)


class ChunkSearchVector(BaseModel):
    embeddings: List
    limit: int = Field(default=10, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)
