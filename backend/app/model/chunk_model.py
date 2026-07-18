from __future__ import annotations
from uuid import UUID
from typing import Optional
from typing import List, Optional
from pydantic import (
    BaseModel,
    Field,
    model_validator,
    model_serializer,
    SerializerFunctionWrapHandler,
)

from backend.app.model.document_model import Document


class Chunk(BaseModel):
    id: UUID
    document_id: UUID
    chunk_number: int
    chunk_text: str
    section: Optional[str] = Field(default=None)
    embedding: List

    # Navigation prop
    document: Optional[Document] = Field(default=None)

    model_config = {"arbitrary_types_allowed": True, "from_attributes": True}

    @model_validator(mode="after")
    def resolve_document_id(self) -> Chunk:
        """If a document nav prop is provided, use its id as document_id."""
        if self.document is not None and self.document_id is None:
            self.document_id = self.document.id
        return self

    @model_serializer(mode="wrap")
    def custom_serializer(self, handler: SerializerFunctionWrapHandler):
        result = handler(self)
        result.pop("document")
        return result
