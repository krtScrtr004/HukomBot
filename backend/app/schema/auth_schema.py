from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class GoogleOAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str|None = Field(default=None)
    id_token: str
    scope: str
    token_type: str
    expires_in: datetime
    
class GoogleDecodedUserResource(BaseModel):
    sub: str
    first_name: str = Field(alias="given_name")
    last_name: str = Field(alias="family_name")
    email: EmailStr
    profile_picture: str = Field(alias="picture")
    email_verified: bool