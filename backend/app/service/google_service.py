import logging

from httpx import AsyncClient
from urllib.parse import urlencode
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi.responses import RedirectResponse

from backend.app.core.settings import settings

from backend.app.schema.auth_schema import (
    GoogleOAuthTokenResponse,
    GoogleUserResource,
)

from backend.app.exception.oauth_exception import (
    GoogleEmailNotVerifiedException,
    OAuthException,
)

logger = logging.getLogger(__name__)

class GoogleService:
    def redirect_to_authorization(self):
        params = {
            "client_id": settings.OAUTH_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
        }

        try:
            google_url = settings.GOOGLE_AUTH_URL + "?" + urlencode(params)
            return RedirectResponse(google_url)
        except Exception as ex:
            raise OAuthException(
                message="Failed to redirect to Google's authentication failed",
                code="OAUTH_REDIRECT_FAIL",
                details=[str(ex)],
            )
            
    async def request_tokens(self, authorization_code: str):
        async with AsyncClient() as client:
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
                raise OAuthException(
                    message="Google authentication fail",
                    code="OAUTH_REQUEST_TOKEN_FAIL",
                    details=["Failed to retrieve tokens from Google"],
                )

        token_response = GoogleOAuthTokenResponse.model_validate(response.json())
        return token_response

    async def retrieve_user(self, id_token: str):
        resource = self._decode_id_token(id_token)
        if not resource.email_verified:
            raise GoogleEmailNotVerifiedException(
                details=[f"{resource.email} has not been verified by Google"]
            )
    
        return resource

    def _decode_id_token(self, token: str) -> GoogleUserResource:
        # Verify and decode token
        id_info = id_token.verify_oauth2_token(
            token, requests.Request(), settings.OAUTH_CLIENT_ID
        )
        return GoogleUserResource.model_validate(id_info)
