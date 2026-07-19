import httpx
from urllib.parse import urlencode
from fastapi.responses import RedirectResponse

from backend.app.core.settings import settings

from backend.app.schema.auth_schema import GoogleOAuthTokenResponse

class GoogleOAuthService:
    def redirect_to_authorization(self):
        params = {
            "client_id": settings.OAUTH_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
        }

        google_url = settings.GOOGLE_AUTH_URL + "?" + urlencode(params)
        return RedirectResponse(google_url)

    async def request_tokens(self, authorization_code: str):
        async with httpx.AsyncClient() as client:
            url = settings.GOOGLE_TOKEN_URL
            body = {
                "code": authorization_code,
                "client_id": settings.OAUTH_CLIENT_ID,
                "client_secret": settings.OAUTH_CLIENT_SECRET,
                "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                "grant_type": "authorization_code",
            }

            response = await client.post(url=url, data=body)
            if not response or response.status_code != 200:
                raise Exception("An error occured while authentication")

        token_response = GoogleOAuthTokenResponse.model_validate(response.json())
        return token_response