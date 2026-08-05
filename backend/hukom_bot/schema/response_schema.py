from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")

class SuccessResponse(BaseModel, Generic[T]):
    success: bool = Field(True, literal=True)
    message: Optional[str] = Field(default=None)
    data: T


class ErrorDetail(BaseModel):
    field: Optional[str] = Field(None)
    issue: str = Field


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=[])


class ErrorResponse(BaseModel):
    success: bool = Field(False, literal=True)
    error: ErrorPayload
