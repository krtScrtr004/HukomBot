from datetime import datetime
from backend.app.model.user_model import User
from backend.app.schema.user_schema import UserCreate


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
