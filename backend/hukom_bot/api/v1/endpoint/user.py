from typing import Annotated
from fastapi import APIRouter, Depends, Body
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.user_schema import UserUpdateBase
from backend.hukom_bot.util.user_caster import UserCaster
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.service.token_quota_service import TokenQuotaService
from backend.hukom_bot.schema.response_schema import SuccessResponse

from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    rate_limit,
    get_user_service,
    get_token_quota_service,
)

user_api_router = APIRouter()


@user_api_router.get("/me")
async def get_me(
    user: Annotated[User, Depends(verify_user)],
    _=Depends(rate_limit(limit=60, window=60)),
):
    return SuccessResponse(
        success=True,
        message="User fetched successfully",
        data=UserCaster.base_to_response(user),
    )


@user_api_router.get("/me/usage")
async def get_daily_token_usage(
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[TokenQuotaService, Depends(get_token_quota_service)],
    _=Depends(rate_limit(limit=60, window=60)),
):
    return await service.retrieve_usage(user.id)


@user_api_router.patch("/me")
async def update_user_info(
    payload: Annotated[UserUpdateBase, Body],
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[UserService, Depends(get_user_service)],
    _=Depends(rate_limit(limit=10, window=60)),
):
    # Use authenticated user's own id
    await service.update(
        user=UserCaster.update_base_to_update(id=user.id, user=payload)
    )

    return SuccessResponse(
        message="User info successfully updated", data={"id": user.id}
    )
