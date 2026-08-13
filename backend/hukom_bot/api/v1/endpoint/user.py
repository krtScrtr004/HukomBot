from typing import Annotated
from fastapi import APIRouter, Depends
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.util.user_caster import UserCaster
from backend.hukom_bot.schema.response_schema import SuccessResponse

from backend.hukom_bot.api.v1.dependency import verify_user, rate_limit

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