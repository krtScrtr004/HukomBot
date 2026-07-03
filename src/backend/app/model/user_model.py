from __future__ import annotations
from pydantic import BaseModel, EmailStr
from backend.app.enum.oauth_provider import OAuthProvider
from uuid import UUID
from typing import Optional
from datetime import datetime


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
    
    model_config = {"from_attributes": True}