from __future__ import annotations
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, model_validator
from backend.hukom_bot.model.user_model import UserBase
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.oauth_provider import OAuthProvider
from backend.hukom_bot.schema.mixin import PaginatableMixin, OrderableMixin


class UserCreate(UserBase):
    id: UUID = Field(default_factory=uuid4)

    model_config = {"arbitrary_types_allowed": True}

class UserUpdateBase(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=255)
    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    role: UserRole | None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}


class UserUpdate(UserUpdateBase):
    id: UUID
    profile_picture: str | None = Field(default=None)


class UserSearch(PaginatableMixin):
    first_name: str | None = Field(default=None, min_length=1, max_length=255)
    last_name: str | None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr | None = Field(default=None)
    provider: OAuthProvider | None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def at_least_one_required(self) -> UserSearch:
        if not any(self.first_name, self.last_name, self.email, self.provider):
            raise ValueError(
                "At least one of 'first_name', 'last_name', 'email', or 'provider' must be provided"
            )
        return self


class UserGetAll(PaginatableMixin, OrderableMixin):
    column: list[str] = Field(default_factory=lambda: ["last_name", "first_name"])
    

class UserResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole
    profile_picture: str | None
