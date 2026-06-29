from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from uuid import UUID
from typing import Optional
from datetime import datetime


class Document(BaseModel):
    id: UUID
    title: str
    file_type: Optional[str] = None
    created_at: datetime


class DocumentCreate(Document):
    title: str
    file_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class DocumentSearch(Document):
    title: Optional[str] = None
    file_type: Optional[str] = None
    limit: int = 10
    offset: int = 0

    @model_validator(mode="after")
    def at_least_one_required(self) -> DocumentSearch:
        if self.title is None and self.file_type is None:
            raise ValueError("At least one of 'title' or 'file_type' must be provided")
        return self
