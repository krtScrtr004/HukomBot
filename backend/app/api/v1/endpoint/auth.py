from typing import Annotated
from fastapi import APIRouter, Request, Depends
from backend.app.service.google_oauth_service import GoogleOAuthService
from backend.app.api.v1.dependency import get_google_oauth_service

auth_api_router = APIRouter()


@auth_api_router.get("/google/login")
async def google_login(
    request: Request,
    service: Annotated[GoogleOAuthService, Depends(get_google_oauth_service)],
):
    return service.redirect_to_authorization()
