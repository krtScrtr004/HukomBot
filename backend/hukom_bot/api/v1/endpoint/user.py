from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Form, File, UploadFile
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.user_schema import UserUpdateBase
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.schema.response_schema import SuccessResponse
from backend.hukom_bot.service.token_quota_service import TokenQuotaService
from backend.hukom_bot.orchistrator.user_orchistrator import UserOrchistrator
from backend.hukom_bot.util.user_caster import UserCaster
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    rate_limit,
    get_token_quota_service,
    get_user_orchistrator,
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
    result = await service.retrieve_usage(user.id)

    return SuccessResponse(message="User token usage retrive successfully", data=result)


@user_api_router.patch("/{user_id}")
async def update_user_info(
    *,
    user_id: Annotated[UUID, Path()],
    first_name: Annotated[str | None, Form()] = None,
    last_name: Annotated[str | None, Form()] = None,
    role: Annotated[UserRole | None, Form()] = None,
    profile_picture: Annotated[UploadFile | None, File()] = None,
    user: Annotated[User, Depends(verify_user)],
    orchistrator: Annotated[UserOrchistrator, Depends(get_user_orchistrator)],
    _=Depends(rate_limit(limit=10, window=60)),
):
    payload = UserUpdateBase(
        first_name=first_name,
        last_name=last_name,
        role=role,
    )

    if payload.model_fields_set or profile_picture is not None:
        await orchistrator.update_pipeline(
            me=user, user_id=user_id, user=payload, profile_picture=profile_picture
        )

    return SuccessResponse(
        message="User info successfully updated", data={"id": user_id}
    )
