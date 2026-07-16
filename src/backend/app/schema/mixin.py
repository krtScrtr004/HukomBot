from typing import Any, List, Optional
from pydantic import Field


class PaginatableMixin:
    limit: int = Field(default=10, gt=0, lt=100)
    offset: int = Field(default=0, ge=0)