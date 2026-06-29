from __future__ import annotations
from model.document_model import Document
from typing import Optional
from pydantic import BaseModel, model_validator
from uuid import UUID
from typing import List, Optional


class Chunk(BaseModel):
    id: UUID
    document_id: UUID
    chunk_number: int
    chunk_text: str
    section: Optional[str] = None
    embedding: List

    document: Optional[Document] = None  # Navigation prop

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def resolve_document_id(self) -> Chunk:
        """If a document nav prop is provided, use its id as document_id."""
        if self.document is not None and self.document_id is None:
            self.document_id = self.document.id
        return self


class ChunkCreate(BaseModel):
    document_id: UUID
    chunk_number: int
    chunk_text: str
    section: Optional[str] = None
    embedding: Optional[List] = None


class ChunkSearchKeyword(BaseModel):
    text: str
    limit: int = 10
    offset: int = 0


class ChunkSearchVector(BaseModel):
    embeddings: List
    limit: int = 10
    offset: int = 0
