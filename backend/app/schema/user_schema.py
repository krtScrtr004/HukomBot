from __future__ import annotations

from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, model_validator, EmailStr, Field

from backend.app.model.user_model import UserBase
from backend.app.enum.oauth_provider import OAuthProvider
from backend.app.schema.mixin import PaginatableMixin


class UserCreate(UserBase):
    id: UUID = Field(default_factory=uuid4)
    
    model_config = {"arbitrary_types_allowed": True}


class UserUpdate(BaseModel):
    id: UUID
    first_name: str|None = Field(default=None, min_length=1, max_length=255)
    last_name: str|None = Field(default=None, min_length=1, max_length=255)
    profile_picture: str|None = Field(default=None)


class UserSearch(PaginatableMixin, BaseModel):
    first_name: str|None = Field(default=None, min_length=1, max_length=255)
    last_name: str|None = Field(default=None, min_length=1, max_length=255)
    email: EmailStr|None = Field(default=None)
    provider: OAuthProvider|None = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}

    @model_validator(mode="after")
    def at_least_one_required(self) -> UserSearch:
        if not any(self.first_name, self.last_name, self.email, self.provider):
            raise ValueError(
                "At least one of 'first_name', 'last_name', 'email', or 'provider' must be provided"
            )
        return self
