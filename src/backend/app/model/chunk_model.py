from __future__ import annotations
from uuid import UUID
from typing import Optional
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from backend.app.model.document_model import Document


class Chunk(BaseModel):
    id: UUID
    document_id: UUID
    chunk_number: int = Field(gt=0, lt=9999)
    chunk_text: str = Field(min_length=1, max_length=1000)
    section: Optional[str] = Field(default=None, min_length=2, max_length=25)
    embedding: List

    document: Optional[Document] = Field(default=None)  # Navigation prop

    model_config = {"arbitrary_types_allowed": True, "from_attributes": True}

    @model_validator(mode="after")
    def resolve_document_id(self) -> Chunk:
        """If a document nav prop is provided, use its id as document_id."""
        if self.document is not None and self.document_id is None:
            self.document_id = self.document.id
        return self
