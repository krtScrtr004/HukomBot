from datetime import datetime
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.user_schema import UserCreate, UserResponse


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
    def base_to_response(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            role=user.role
        )