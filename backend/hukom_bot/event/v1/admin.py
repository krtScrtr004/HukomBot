from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.service.pubsub_service import PubsubService
from backend.hukom_bot.orchistrator.admin_orchistrator import AdminOrchistrator
from backend.hukom_bot.schema.response_schema import SuccessResponse
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    require_role,
    get_pubsub_service, 
    get_admin_orchistrator
)

admin_sse_router = APIRouter()


async def admin_dashboard_event_stream(
    request: Request, 
    orchistrator: AdminOrchistrator,
    service: PubsubService
):
    await service.subscribe(settings.ADMIN_DASHBOARD_CH)

    try:
        while True:
            # Detect client disconnect
            if await request.is_disconnected():
                break

            message = await service.get_message(
                ignore_subscribe_messages=True, timeout=15.0
            )

            # No progress event within timeout — send a comment as heartbeat
            # so proxies/browsers don't time out the connection
            if message is None:
                yield ": heartbeat\n\n"
                continue

            data = await orchistrator.get_dashboard_data()                        
            yield f"data:{data}"
    finally:
        await service.unsubscribe(settings.ADMIN_DASHBOARD_CH)
        await service.close()


@admin_sse_router.get("/dashboard")
async def admin_dashboard_update(
    request: Request,
    orchistrator: Annotated[AdminOrchistrator, Depends(get_admin_orchistrator)],
    service: Annotated[PubsubService, Depends(get_pubsub_service)],
    _us: Annotated[User, Depends(verify_user)],
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    return StreamingResponse(
        admin_dashboard_event_stream(
            request=request, orchistrator=orchistrator, service=service
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
