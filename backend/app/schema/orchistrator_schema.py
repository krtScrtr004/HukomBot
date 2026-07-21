from typing import TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class OrchistratorResult(BaseModel):
    message: str
    data: T