import jwt
import base64
import hashlib
import secrets
import logging
from typing import Annotated
from fastapi import APIRouter, Request, Query, Depends
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.response_schema import SuccessResponse
from backend.hukom_bot.schema.auth_schema import JWTPayload
from backend.hukom_bot.service.auth_service import AuthService
from backend.hukom_bot.service.jwt_service import JWTService
from backend.hukom_bot.service.google_service import GoogleService
from backend.hukom_bot.util.user_caster import UserCaster
from backend.hukom_bot.exception.oauth_exception import OAuthException
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    rate_limit,
    get_auth_service,
    get_jwt_service,
    get_google_service,
)
from backend.hukom_bot.exception.app_exception import RateLimitException

auth_api_router = APIRouter()

logger = logging.getLogger(__name__)


async def rate_limit_handler(
    request: Request,
    limit: int,
    window: int,
    auth_service: AuthService,
):
    try:
        await rate_limit(limit=limit, window=window)(request)
    except RateLimitException:
        return auth_service.redirect_unauthorized(request, "RATE_LIMIT_EXCEEDED")


@auth_api_router.get("/me")
async def get_authenticated_user(
    request: Request,
    user: Annotated[User, Depends(verify_user)],
    _=Depends(rate_limit(limit=60, window=60)),
):
    return SuccessResponse(
        success=True,
        message="User fetched successfully",
        data=UserCaster.base_to_response(user),
    )


@auth_api_router.get("/google/login")
async def google_login(
    request: Request,
    service: Annotated[GoogleService, Depends(get_google_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    rate_limit_response = await rate_limit_handler(
        request=request, limit=10, window=60, auth_service=auth_service
    )
    if rate_limit_response:
        return rate_limit_response

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
    rate_limit_response = await rate_limit_handler(
        request=request, limit=10, window=60, auth_service=auth_service
    )
    if rate_limit_response:
        return rate_limit_response

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

        google_user = google_service.retrieve_user(tokens.id_token, nonce)

        user = await auth_service.authenticate_user(google_user)

        token = jwt_service.encode(payload=JWTPayload(provider_id=user.provider_id))

        return auth_service.redirect_authorized(request, token)
    except Exception as ex:
        logger.exception(str(ex))

        jwt_errors = (
            jwt.InvalidTokenError,
            jwt.InvalidAlgorithmError,
            jwt.InvalidAudienceError,
            jwt.InvalidIssuerError,
        )

        error_code = "INTERNAL_SERVER_ERROR"
        if isinstance(ex, jwt_errors):
            error_code = "INVALID_TOKEN"
        elif isinstance(ex, jwt.ExpiredSignatureError):
            error_code = "TOKEN_EXPIRED"
        elif isinstance(ex, OAuthException):
            error_code = ex.code

        return auth_service.redirect_unauthorized(
            request=request, error_code=error_code
        )
    finally:
        request.session.pop("oauth_state", "")
        request.session.pop("oauth_code_verfier", "")
        request.session.pop("oauth_nonce", "")


@auth_api_router.get("/logout")
async def logout(
    request: Request,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    _: Annotated[User, Depends(verify_user)],
):
    rate_limit_response = await rate_limit_handler(
        request=request, limit=20, window=60, auth_service=auth_service
    )
    if rate_limit_response:
        return rate_limit_response

    return await auth_service.logout(request)
