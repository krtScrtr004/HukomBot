import jwt

from typing import Annotated
from urllib.parse import urlencode
from fastapi import APIRouter, Request, Query, Depends

from fastapi.responses import RedirectResponse

from backend.app.schema.auth_schema import JWTPayload

from backend.app.service.auth_service import AuthService
from backend.app.service.jwt_service import JWTService
from backend.app.service.google_service import GoogleService

from backend.app.schema.auth_schema import LoginResponse
from backend.app.schema.response_schema import SuccessResponse

from backend.app.api.v1.dependency import (
    get_auth_service,
    get_jwt_service,
    get_google_service,
)

auth_api_router = APIRouter()


@auth_api_router.get("/google/login")
def google_login(
    service: Annotated[GoogleService, Depends(get_google_service)],
):
    return service.redirect_to_authorization()


@auth_api_router.get("/google/login/callback")
async def google_login_callback(
    request: Request,
    code: Annotated[str, Query()],
    jwt_service: Annotated[JWTService, Depends(get_jwt_service)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    google_service: Annotated[GoogleService, Depends(get_google_service)],
):
    try:
        tokens = await google_service.request_tokens(code)

        google_user = await google_service.retrieve_user(tokens.id_token)

        user = await auth_service.authenticate_user(google_user)

        token = jwt_service.encode(payload=JWTPayload(provider_id=user.provider_id))

        # TODO: Update the redirect url here
        redirect = RedirectResponse("http://127.0.0.1:8000/redoc")
        # Set jwt on cookie
        redirect.set_cookie(key="token", value=token, httponly=True)

        return redirect
    except jwt.ExpiredSignatureError:
        # TODO: Redirect user on fail
        params = urlencode({"error_code": "TOKEN_EXPIRED"})
        return RedirectResponse(
            url=request.url_for(f"login_page?{params}"), status_code=303
        )
    except (
        jwt.InvalidTokenError,
        jwt.InvalidAlgorithmError, 
        jwt.InvalidAudienceError,
        jwt.InvalidIssuerError
    ):
        params = urlencode({"error_code": "INVALID_TOKEN"})
        return RedirectResponse(
            url=request.url_for(f"login_page?{params}"), status_code=303
        )