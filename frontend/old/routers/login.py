from typing import Annotated
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse

from frontend.app import lookup

from backend.app.service.auth_service import AuthService
from backend.app.schema.auth_schema import LoginQueryParams
from backend.app.api.v1.dependency import get_auth_service

login_page_router = APIRouter()


@login_page_router.get("/")
async def login_page(
    request: Request,
    params: Annotated[LoginQueryParams, Query()],
    auth_service: AuthService = Depends(get_auth_service),
):
    # Redirect to dashboard/homepage if already authenticated
    redirect = await auth_service.redirect_authorized(request)
    if redirect:
        return redirect

    google_redirect_url = "http://127.0.0.1:8000/api/v1/auth/google/login"

    template = lookup.get_template("/pages/login.html")
    return HTMLResponse(
        template.render(
            google_redirect_url=google_redirect_url, error_code=params.error_code
        )
    )
