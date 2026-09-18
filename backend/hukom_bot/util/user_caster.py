from uuid import UUID
from datetime import datetime
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.user_schema import *


class UserCaster:

    @staticmethod
    def create_to_base(
        user: UserCreate, is_active: bool, created_at: datetime, updated_at: datetime
    ) -> User:
        return User(
            id=user.id,
            provider_id=user.provider_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            profile_picture=user.profile_picture,
            role=user.role,
            provider=user.provider,
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at,
        )

    @staticmethod
    def update_payload_to_update(id: UUID, user: UserUpdateBase) -> UserUpdate:
        return UserUpdate(
            id=id,
            first_name=user.first_name,
            last_name=user.last_name,
            profile_picture=user.profile_picture,
            role=user.role
        )

    @staticmethod
    def base_to_response(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            role=user.role,
            profile_picture=user.profile_picture,
            provider=user.provider,
            created_at=user.created_at
        )
        
    @staticmethod
    def search_to_all(user: UserSearch) -> UserGetAll:
        return UserGetAll(
            is_active=user.is_active,
            role=user.role,
            oauth_provider=user.oauth_provider,
            column=user.column,
            order=user.order,
            limit=user.limit,
            offset=user.offset
        )