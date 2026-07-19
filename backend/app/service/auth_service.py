import logging

from backend.app.database.database import Database
from backend.app.enum.user_role import UserRole
from backend.app.enum.oauth_provider import OAuthProvider

from backend.app.schema.user_schema import UserCreate, UserResponse
from backend.app.schema.auth_schema import GoogleUserResource
from backend.app.schema.response_schema import SuccessResponse

from backend.app.repository.user_repository import UserRepository

from backend.app.exception.oauth_exception import OAuthException

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Database, user_repo: UserRepository):
        self._db = db
        self._user_repo = user_repo

    async def authenticate_google_user(self, google_user: GoogleUserResource):
        async with self._db.connection() as conn:
            try:
                user = await self._user_repo.get_by_provider_id(google_user.sub, conn)
                if not user:
                    # Create user record if account is not yet connected
                    await self._user_repo.create(
                        UserCreate(
                            provider_id=google_user.sub,
                            first_name=google_user.first_name,
                            last_name=google_user.last_name,
                            email=google_user.email,
                            role=UserRole.STANDARD,
                            profile_picture=google_user.profile_picture,
                            provider=OAuthProvider.GOOGLE,
                        )
                    )

                    logger.info(
                        "New google account with sub: %s has successgully connected to the app",
                        google_user.sub,
                    )

                await conn.commit()

                return SuccessResponse(
                    success=True,
                    message="Google user connected successfully",
                    data=UserResponse(
                        id=user.id,
                        first_name=user.first_name,
                        last_name=user.last_name,
                        email=user.email,
                        role=user.role,
                    ),
                )
            except Exception as ex:
                logger.exception(str(ex))
                await conn.rollback()
