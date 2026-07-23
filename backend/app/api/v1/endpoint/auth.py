import jwt
import base64
import hashlib
import secrets
from typing import Annotated
from urllib.parse import urlencode
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import RedirectResponse
from backend.app.schema.auth_schema import JWTPayload
from backend.app.service.auth_service import AuthService
from backend.app.service.jwt_service import JWTService
from backend.app.service.google_service import GoogleService
from backend.app.exception.oauth_exception import OAuthException
from backend.app.api.v1.dependency import (
    get_auth_service,
    get_jwt_service,
    get_google_service,
)

auth_api_router = APIRouter()


@auth_api_router.get("/google/login")
def google_login(
    request: Request,
    service: Annotated[GoogleService, Depends(get_google_service)],
):
    state = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).decode().rstrip("=")
    nonce = secrets.token_urlsafe(32)

    request.session["oauth_state"] = state
    request.session["oauth_code_verfier"] = code_verifier
    request.session["oauth_nonce"] = nonce

    return service.redirect_to_authorization(
        state=state, code_challenge=code_challenge, nonce=nonce
    )


@auth_api_router.get("/google/login/callback")
async def google_login_callback(
    request: Request,
    code: Annotated[str, Query()],
    state: Annotated[str, Query()],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    google_service: Annotated[GoogleService, Depends(get_google_service)],
):
    try:
        session_state = request.session.get("oauth_state")
        if not session_state or session_state != state:
            raise OAuthException(details=["Invalid OAuth state"], status_code=401)

        code_verifier = request.session.get("oauth_code_verfier")
        if not code_verifier:
            raise OAuthException(
                details=["Invalid OAuth code verifier"], status_code=401
            )

        nonce = request.session.get("oauth_nonce")
        if not nonce:
            raise OAuthException(details=["Invalid OAuth nonce"], status_code=401)

        tokens = await google_service.request_tokens(
            authorization_code=code, code_verifier=code_verifier
        )

        google_user = await google_service.retrieve_user(tokens.id_token, nonce)

        user = await auth_service.authenticate_user(google_user)

        token = jwt_service.encode(payload=JWTPayload(provider_id=user.provider_id))

        # TODO: Update the redirect url here
        redirect = RedirectResponse("http://127.0.0.1:8000/redoc")
        # Set jwt on cookie
        redirect.set_cookie(key="token", value=token, httponly=True)

        return redirect
    except jwt.ExpiredSignatureError:
        params = urlencode({"error_code": "TOKEN_EXPIRED"})
        return RedirectResponse(
            url=request.url_for(f"login_page?{params}"), status_code=303
        )
    except (
        jwt.InvalidTokenError,
        jwt.InvalidAlgorithmError,
        jwt.InvalidAudienceError,
        jwt.InvalidIssuerError,
    ):
        params = urlencode({"error_code": "INVALID_TOKEN"})
        return RedirectResponse(
            url=request.url_for(f"login_page?{params}"), status_code=303
        )
    except OAuthException as ex:
        params = urlencode({"error_code": ex.code})
        return RedirectResponse(
            url=request.url_for(f"login_page?{params}"), status_code=303
        )
    finally:
        request.session.pop("oauth_state")
        request.session.pop("oauth_code_verfier")
        request.session.pop("oauth_nonce")
