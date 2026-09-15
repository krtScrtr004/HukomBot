from __future__ import annotations
from datetime import datetime
from pydantic import BaseModel, Field, model_validator
from backend.hukom_bot.enum.date_range import DateRange
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
    
    
class DateRangeableMixin(BaseModel):
    date_range: DateRange | None = Field(default=None)
    date_start: datetime | None = Field(default=None)
    date_end: str | None = Field(default=None)
    
    model_config = {"arbitrary_types_allowed": True}
    
    @model_validator(mode="after")
    def validate_dates(self) -> DateRangeableMixin:
        if self.date_range is not None:
            self.date_start = None
            self.date_end = None
            return self

        if self.date_end is not None:
            start = self.date_start if self.date_start is not None else datetime.now()
            if self.date_end <= start:
                raise ValueError("date_end must be later than date_start")

        return self

