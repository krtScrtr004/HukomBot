import logging

from httpx import AsyncClient
from urllib.parse import urlencode
from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi.responses import RedirectResponse

from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.schema.auth_schema import (
    GoogleOAuthTokenResponse,
    AuthUser,
)
from backend.hukom_bot.exception.oauth_exception import (
    GoogleEmailNotVerifiedException,
    OAuthException,
)

logger = logging.getLogger(__name__)


class GoogleService:
    def redirect_to_authorization(self, state: str, code_challenge: str, nonce: str):
        if not state:
            raise OAuthException(
                details=["Invalid state to redirect to Google authentication"]
            )
            
        if not code_challenge:
            raise OAuthException(
                details=["Invalid code challenge to redirect to Google authentication"]
            )
            
        if not nonce:
            raise OAuthException(
                details=["Invalid nonce to redirect to Google authentication"]
            )

        params = {
            "client_id": settings.OAUTH_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "nonce": nonce
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

    async def request_tokens(self, authorization_code: str, code_verifier: str):
        if not authorization_code:
            raise OAuthException(
                details=["Invalid authorization code on Google login callback"]
            )
        
        if not code_verifier:
            raise OAuthException(
                details=["Invalid code verifier on Google login callback"]
            )

        try:
            async with AsyncClient() as client:
                url = settings.GOOGLE_TOKEN_URL
                body = {
                    "code": authorization_code,
                    "client_id": settings.OAUTH_CLIENT_ID,
                    "client_secret": settings.OAUTH_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_OAUTH_REDIRECT_URI,
                    "grant_type": "authorization_code",
                    "code_verifier": code_verifier
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
        except Exception as ex:
            logger.exception("An error occured while requesting for OAuth tokens: %s", str(ex))
            raise

    def retrieve_user(self, id_token: str, session_nonce: str):
        resource = self._verify_id_token(id_token, session_nonce)
        if not resource.email_verified:
            raise GoogleEmailNotVerifiedException(
                details=[f"{resource.email} has not been verified by Google"]
            )

        return resource

    def _verify_id_token(self, token: str, session_nonce: str) -> AuthUser:
        # Verify and decode token
        id_info = id_token.verify_oauth2_token(
            token, requests.Request(), settings.OAUTH_CLIENT_ID
        )
        nonce = id_info["nonce"]
        if not nonce or session_nonce != nonce:
            raise OAuthException(details=["Invalid nonce from Google's ID Token"])
        return AuthUser.model_validate(id_info)
