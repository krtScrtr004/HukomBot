from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class Document(BaseModel):
    id: UUID
    title: str
    file_type: Optional[str] = None
    created_at: datetime
