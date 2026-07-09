from typing import Any, List, Optional
from pydantic import BaseModel, Field

class BaseResponse(BaseModel):
    messages: List[str] = Field(default_factory=list)
    data: Optional[Any] = None
    errors: List[str] = Field(default_factory=list)