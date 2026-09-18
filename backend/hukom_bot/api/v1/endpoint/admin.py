import logging
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.orchistrator.admin_orchistrator import AdminOrchistrator
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from backend.hukom_bot.schema.response_schema import SuccessResponse
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    rate_limit,
    require_role,
    get_admin_orchistrator,
)

admin_api_router = APIRouter()

logger = logging.getLogger(__name__)


@admin_api_router.get("/dashboard")
async def get_dashboard_data(
    query: Annotated[DateRangeableMixin, Query()],
    orchistrator: Annotated[AdminOrchistrator, Depends(get_admin_orchistrator)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN))

):
    result = await orchistrator.get_dashboard_data(date_range=query)

    return SuccessResponse(message="Dashboard data retrived successfully", data=result)

@admin_api_router.get("/users")
async def get_dashboard_data(
    orchistrator: Annotated[AdminOrchistrator, Depends(get_admin_orchistrator)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN))

):
    result = await orchistrator.get_user_analytics()

    return SuccessResponse(message="Dashboard data retrived successfully", data=result)
