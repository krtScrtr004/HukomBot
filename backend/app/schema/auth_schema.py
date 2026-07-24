import time
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, EmailStr, AliasChoices

from backend.app.core.settings import settings


class AuthUser(BaseModel):
    provider_id: str = Field(validation_alias=AliasChoices("sub"))
    first_name: str = Field(alias="given_name")
    last_name: str = Field(alias="family_name")
    email: EmailStr
    profile_picture: str = Field(alias="picture")
    email_verified: bool


class JWTPayload(BaseModel):
    provider_id: str
    iss: str = Field(default=settings.JWT_ISS)
    aud: str = Field(default=settings.JWT_AUD)
    iat: int = Field(default_factory=lambda: int(time.time()))
    exp: int = Field(
        default_factory=lambda: int(
            (datetime.now() + timedelta(minutes=settings.JWT_EXP_IN_MIN)).timestamp()
        )
    )


class LoginQueryParams(BaseModel):
    error_code: str | None = Field(default=None, min_length=1, max_length=100)


class LoginResponse(BaseModel):
    token: str
    token_type: str


class GoogleOAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = Field(default=None)
    id_token: str
    scope: str
    token_type: str
    expires_in: datetime
