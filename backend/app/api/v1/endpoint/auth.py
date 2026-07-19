from typing import Annotated
from fastapi import APIRouter, Request, Query, Depends
from backend.app.service.auth_service import AuthService
from backend.app.service.google_service import GoogleService
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
    google_service: Annotated[GoogleService, Depends(get_google_service)]
): 
    tokens = await google_service.request_tokens(code)
    
    google_user = await google_service.retrieve_user(tokens.id_token)
    
    return await auth_service.authenticate_google_user(google_user)