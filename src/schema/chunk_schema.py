from typing import Optional
from pydantic import BaseModel
from uuid import UUID
from typing import List, Optional

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