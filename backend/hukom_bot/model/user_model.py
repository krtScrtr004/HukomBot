from __future__ import annotations

from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr

from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.oauth_provider import OAuthProvider


class UserBase(BaseModel):
    provider_id: str
    provider: OAuthProvider
    first_name: str
    last_name: str
    email: EmailStr 
    profile_picture: str|None = None
    role: UserRole
    
    model_config = {"arbitrary_types_allowed": True}


class User(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}