from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query, Form, File, UploadFile
from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.user_schema import UserUpdateBase, UserSearch, UserGetAll
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.schema.response_schema import SuccessResponse
from backend.hukom_bot.service.pubsub_service import PubsubService
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.service.token_quota_service import TokenQuotaService
from backend.hukom_bot.orchistrator.user_orchistrator import UserOrchistrator
from backend.hukom_bot.util.user_caster import UserCaster
from backend.hukom_bot.api.v1.dependency import (
    verify_user,
    rate_limit,
    require_role,
    get_token_quota_service,
    get_user_service,
    get_user_orchistrator,
    get_pubsub_service,
)

user_api_router = APIRouter()


@user_api_router.get("/")
async def get_users(
    query: Annotated[UserSearch, Query()],
    service: Annotated[UserService, Depends(get_user_service)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    result = (
        await service.search(param=query)
        if query.query
        else await service.all(param=UserCaster.search_to_all(query))
    )

    return SuccessResponse(
        message="User fetched successfully",
        data=[UserCaster.base_to_response(u) for u in result],
    )


@user_api_router.get("/me")
async def get_me(
    user: Annotated[User, Depends(verify_user)],
    _=Depends(rate_limit(limit=60, window=60)),
):
    return SuccessResponse(
        message="User retrieved successfully",
        data=UserCaster.base_to_response(user),
    )


@user_api_router.get("/me/usage")
async def get_daily_token_usage(
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[TokenQuotaService, Depends(get_token_quota_service)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.STANDARD, UserRole.CONTRIBUTOR)),
):
    result = await service.retrieve_usage(user.id)

    return SuccessResponse(
        message="User token usage retrieved successfully", data=result
    )


@user_api_router.patch("/{user_id}")
async def update_user_info(
    *,
    user_id: Annotated[UUID, Path()],
    first_name: Annotated[str | None, Form()] = None,
    last_name: Annotated[str | None, Form()] = None,
    role: Annotated[UserRole | None, Form()] = None,
    profile_picture: Annotated[UploadFile | None, File()] = None,
    is_active: Annotated[bool | None, Form()] = None,
    user: Annotated[User, Depends(verify_user)],
    orchistrator: Annotated[UserOrchistrator, Depends(get_user_orchistrator)],
    service: Annotated[PubsubService, Depends(get_pubsub_service)],
    _=Depends(rate_limit(limit=10, window=60)),
):
    payload = UserUpdateBase(
        first_name=first_name,
        last_name=last_name,
        role=role,
        is_active=is_active
    )

    if payload.model_fields_set or profile_picture is not None:
        await orchistrator.update_pipeline(
            me=user, user_id=user_id, user=payload, profile_picture=profile_picture
        )

        await service.publish(
            channel=settings.ADMIN_DASHBOARD_CH, data="Admin dashboard data updated"
        )

    return SuccessResponse(
        message="User info successfully updated", data={"id": user_id}
    )


@user_api_router.delete("/{user_id}")
async def delete_user(
    user_id: Annotated[UUID, Path()],
    user_service: Annotated[UserService, Depends(get_user_service)],
    pubsub_service: Annotated[PubsubService, Depends(get_pubsub_service)],
    _us: Annotated[User, Depends(verify_user)],
    _rl=Depends(rate_limit(limit=60, window=60)),
    _rr=Depends(require_role(UserRole.ADMIN)),
):
    await user_service.delete(id=user_id)

    await pubsub_service.publish(
        channel=settings.ADMIN_DASHBOARD_CH, data="Admin dashboard data updated"
    )

    return SuccessResponse(
        message="User account deleted successfully",
        data={"id": user_id},
    )
