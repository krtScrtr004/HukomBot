from typing import Any, List, Optional
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    message: List[str] = Field(default_factory=list)
    data: Optional[Any] = None
    error: List[str] = Field(default_factory=list)