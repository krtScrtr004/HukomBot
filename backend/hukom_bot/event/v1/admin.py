from typing import Annotated
from functools import partial
from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import StreamingResponse
from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.service.pubsub_service import PubsubService
from backend.hukom_bot.orchistrator.admin_orchistrator import AdminOrchistrator
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    require_role,
    get_pubsub_service,
    get_admin_orchistrator,
)
from backend.hukom_bot.util.sse_handler import sse_handler

admin_sse_router = APIRouter()


@admin_sse_router.get("/dashboard")
async def admin_dashboard_update(
    request: Request,
    query: Annotated[DateRangeableMixin, Query()],
    orchistrator: Annotated[AdminOrchistrator, Depends(get_admin_orchistrator)],
    service: Annotated[PubsubService, Depends(get_pubsub_service)],
    _us: Annotated[User, Depends(verify_user)],
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    data_handler = partial(orchistrator.get_dashboard_data, date_range=query)

    return StreamingResponse(
        sse_handler(
            request=request,
            channel_name=settings.ADMIN_DASHBOARD_CH,
            data_builder=data_handler,
            pubsub_service=service,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

@admin_sse_router.get("/users")
async def admin_user_analytics_update(
    request: Request,
    orchistrator: Annotated[AdminOrchistrator, Depends(get_admin_orchistrator)],
    service: Annotated[PubsubService, Depends(get_pubsub_service)],
    _us: Annotated[User, Depends(verify_user)],
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    return StreamingResponse(
        sse_handler(
            request=request,
            channel_name=settings.ADMIN_USER_ANALYTICS_CH,
            data_builder=orchistrator.get_user_analytics,
            pubsub_service=service,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )