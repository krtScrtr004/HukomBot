from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from frontend.app import lookup

login_page_router = APIRouter()


@login_page_router.get("/")
def login_page():
    google_redirect_url = "http://127.0.0.1:8000/api/v1/auth/google/login"
    
    template = lookup.get_template("/page/login.html")
    return HTMLResponse(
        template.render(google_redirect_url=google_redirect_url)
    )
