from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from frontend.app import lookup

login_page_router = APIRouter()


@login_page_router.get("/")
def login_page():
    template = lookup.get_template("/page/login.html")
    return HTMLResponse(template.render())
