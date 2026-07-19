from __future__ import annotations
from pydantic import BaseModel, EmailStr
from backend.app.enum.oauth_provider import OAuthProvider
from uuid import UUID
from datetime import datetime


class UserBase(BaseModel):
    provider_id: str
    provider: OAuthProvider
    first_name: str
    last_name: str
    email: EmailStr 
    profile_picture: str|None = None


class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}