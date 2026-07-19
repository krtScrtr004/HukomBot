from datetime import datetime
from pydantic import BaseModel, Field

class GoogleOAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str|None = Field(default=None)
    id_token: str
    scope: str
    token_type: str
    expires_in: datetime