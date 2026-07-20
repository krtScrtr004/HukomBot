from typing import Annotated
from fastapi import APIRouter, Request, Query, Depends

from backend.app.service.auth_service import AuthService
from backend.app.service.jwt_service import JWTService
from backend.app.service.google_service import GoogleService

from backend.app.schema.auth_schema import LoginResponse
from backend.app.schema.response_schema import SuccessResponse

from backend.app.api.v1.dependency import get_auth_service, get_google_service

auth_api_router = APIRouter()


@auth_api_router.get("/google/login")
def google_login(
    service: Annotated[GoogleService, Depends(get_google_service)],
):
    return service.redirect_to_authorization()


@auth_api_router.get("/google/login/callback")
async def google_login_callback(
    code: Annotated[str, Query()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    google_service: Annotated[GoogleService, Depends(get_google_service)],
):
    tokens = await google_service.request_tokens(code)

    google_user = await google_service.retrieve_user(tokens.id_token)

    user = await auth_service.authenticate_user(google_user)
    jwt = auth_service.build_jwt_from_user(user)

    return SuccessResponse(
        message="Google user successfully authenticated", data=LoginResponse(token=jwt)
    )
