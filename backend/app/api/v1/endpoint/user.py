from typing import Annotated
from backend.app.model.user_model import User
from fastapi import APIRouter, Depends
from backend.app.util.user_caster import UserCaster
from backend.app.schema.response_schema import SuccessResponse

from backend.app.api.v1.dependency import verify_user

user_api_router = APIRouter()

@user_api_router.get("/me")
async def get_me(user: Annotated[User, Depends(verify_user)]):
    return SuccessResponse(
        success=True,
        message="User fetched successfully",
        data=UserCaster.base_to_response(user),
    )