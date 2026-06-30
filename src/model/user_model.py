from __future__ import annotations
from pydantic import BaseModel, Field, model_validator, EmailStr
from enum import Enum
from uuid import UUID
from typing import Optional
from datetime import datetime


class OAuthProvider(str, Enum):
    GOOGLE = "google"
    FACEBOOK = "facebook"
    APPLE = "apple"


class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    provider: OAuthProvider
    provider_id: str


class User(UserBase):
    id: UUID
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None


class UserUpdate(BaseModel):
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    last_login_at: Optional[datetime] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserSearch(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    provider: Optional[OAuthProvider] = None
    limit: int = 10
    offset: int = 0
    
    model_config = {"arbitrary_types_allowed": True}
    
    @model_validator(mode="after")
    def at_least_one_required(self) -> UserSearch:
        if not any(self.display_name, self.email, self.provider):
            raise ValueError("At least one of 'display_name', 'email', or 'provider' must be provided")
        return self