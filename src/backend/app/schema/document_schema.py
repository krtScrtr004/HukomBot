from __future__ import annotations
from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
from fastapi import UploadFile


class DocumentCreate(BaseModel):
    title: str
    file_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes: True


class DocumentSearch(BaseModel):
    title: Optional[str] = None
    file_type: Optional[str] = None
    limit: int = 10
    offset: int = 0

    @model_validator(mode="after")
    def at_least_one_required(self) -> DocumentSearch:
        if self.title is None and self.file_type is None:
            raise ValueError("At least one of 'title' or 'file_type' must be provided")
        return self
    

class DocumentUpload(BaseModel):
    file: UploadFile
    
    model_config = {"arbitrary_types_allowed": True}
