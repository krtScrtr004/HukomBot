from pydantic import BaseModel, Field
from backend.hukom_bot.enum.utils import OrderEnum


class PaginatableMixin(BaseModel):
    limit: int = Field(default=10, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)


class SearchableMixin(BaseModel):
    query: str | None = Field(default=None, min_length=1, max_length=100)


class OrderableMixin(BaseModel):
    column: list[str] = Field(min_length=1, exclude=True)
    order: OrderEnum = Field(default_factory=lambda: OrderEnum.ASC, exclude=True)

    model_config = {"arbitrary_types_allowed": True}
