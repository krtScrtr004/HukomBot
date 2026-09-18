from __future__ import annotations
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, model_validator
from backend.hukom_bot.model.user_model import UserBase
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.oauth_provider import OAuthProvider
from backend.hukom_bot.schema.mixin import (
    SearchableMixin,
    PaginatableMixin,
    OrderableMixin,
    DateRangeableMixin,
)


class UserCreate(UserBase):
    id: UUID = Field(default_factory=uuid4)

    model_config = {"arbitrary_types_allowed": True}


class UserUpdateBase(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=255)
    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = Field(default=None)
    is_active: bool | None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class UserUpdate(UserUpdateBase):
    id: UUID
    profile_picture: str | None = Field(default=None)


class UserSearch(PaginatableMixin, OrderableMixin):
    query: str | None = Field(default=None, min_length=3, max_length=256)
    is_active: bool | None = Field(default=None)
    role: UserRole | None = Field(default=None)
    oauth_provider: OAuthProvider | None = Field(default=None)
    column: list[str] = Field(default_factory=lambda: ["last_name", "first_name"])

    model_config = {"arbitrary_types_allowed": True}


class UserGetByManyId(PaginatableMixin):
    ids: list[UUID]


class UserGetByActiveState(PaginatableMixin, DateRangeableMixin):
    is_active: bool = Field(default=True)


class UserGetAll(PaginatableMixin, OrderableMixin):
    column: list[str] = Field(default_factory=lambda: ["last_name", "first_name"])


class UserGetQueryParams(SearchableMixin, PaginatableMixin):
    pass


class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    profile_picture: str | None
    provider: OAuthProvider
    created_at: datetime

    model_config = {"arbitrary_types_allowed": True}
