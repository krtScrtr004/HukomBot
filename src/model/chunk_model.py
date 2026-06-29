from __future__ import annotations
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
    embedding: list
    
class ChunkCreate(Chunk):
    document_id: UUID
    chunk_number: int
    chunk_text: str
    section: Optional[str] = None
    embedding: list
    
class ChunkSearchKeyword(Chunk):
    chunk_text: str
    limit: int = 10
    offset: int = 0
    
class ChunkSearchVector(Chunk):
    embeddings: List
    limit: int = 10
    offset: int = 0