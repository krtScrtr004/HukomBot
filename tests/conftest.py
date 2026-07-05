import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.app.main import app

from backend.app.api.v1.dependency import lifespan


@pytest_asyncio.fixture
async def client():
    async with lifespan(app):
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://127.0.0.1:8000/",
            follow_redirects=True,
        ) as client:
            yield client
