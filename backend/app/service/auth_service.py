import logging
from uuid import UUID

from backend.app.database.database import Database
from backend.app.enum.user_role import UserRole
from backend.app.enum.oauth_provider import OAuthProvider

from backend.app.model.user_model import User

from backend.app.schema.user_schema import UserCreate
from backend.app.schema.auth_schema import AuthUser

from backend.app.repository.user_repository import UserRepository

from backend.app.service.jwt_service import JWTService
from backend.app.exception.app_exception import UnauthorizedException

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self, db: Database, user_repo: UserRepository, jwt_service: JWTService
    ):
        self._db = db
        self._user_repo = user_repo
        self._jwt_service = jwt_service

    def authenticate_request(self, request_id: UUID, scheme: str, token: str):
        def raiseUnauthorized(details: list[str]):
            raise UnauthorizedException(
                message="You are not authorized to perform this action",
                code="INVALID_TOKEN",
                details=details,
            )

        if scheme != "Bearer":
            raiseUnauthorized(
                details=[
                    f"Incorrect authorization scheme/type in request with id: {request_id}"
                ]
            )

        decoded = self._jwt_service.verify(token)
        provider_id = decoded.get("provider_id")
        if not decoded or not provider_id:
            raiseUnauthorized(
                details=[f"Invalid token provided in request with id: {request_id}"]
            )

        return provider_id

    async def authenticate_user(self, user: AuthUser) -> User:
        async with self._db.connection() as conn:
            try:
                user = await self._user_repo.get_by_provider_id(user.provider_id, conn)
                if not user:
                    # Create user record if account is not yet connected
                    await self._user_repo.create(
                        UserCreate(
                            provider_id=user.provider_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email,
                            role=UserRole.STANDARD,
                            profile_picture=user.profile_picture,
                            provider=OAuthProvider.GOOGLE,
                        )
                    )

                    logger.info(
                        "New account with provider id: %s has successgully connected to the app",
                        user.provider_id,
                    )

                await conn.commit()

                return user
            except Exception as ex:
                logger.exception(str(ex))
                await conn.rollback()
