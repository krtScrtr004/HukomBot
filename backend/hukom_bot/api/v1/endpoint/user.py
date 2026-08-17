from typing import Annotated
from fastapi import APIRouter, Depends
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.util.user_caster import UserCaster
from backend.hukom_bot.service.token_quota_service import TokenQuotaService
from backend.hukom_bot.schema.response_schema import SuccessResponse

from backend.hukom_bot.api.v1.dependency import verify_user, rate_limit, get_token_quota_service

user_api_router = APIRouter()

@user_api_router.get("/me")
async def get_me(
    user: Annotated[User, Depends(verify_user)],
    _=Depends(rate_limit(limit=60, window=60))
):
    return SuccessResponse(
        success=True,
        message="User fetched successfully",
        data=UserCaster.base_to_response(user),
    )
    
@user_api_router.get("/me/usage")
async def get_daily_token_usage(
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[TokenQuotaService, Depends(get_token_quota_service)]
):
    return await service.retrieve_usage(user.id)