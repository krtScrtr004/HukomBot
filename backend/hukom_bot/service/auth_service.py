import logging
from uuid import UUID
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from backend.hukom_bot.core.settings import settings
from backend.hukom_bot.service.redirect_service import redirect_service
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.oauth_provider import OAuthProvider
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.user_schema import UserCreate
from backend.hukom_bot.schema.auth_schema import AuthUser, JWTPayload, RevokedToken
from backend.hukom_bot.service.jwt_service import JWTService
from backend.hukom_bot.service.pubsub_service import PubsubService
from backend.hukom_bot.service.revoked_token_service import RevokedTokenService
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.exception.app_exception import UnauthorizedException

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        db: Database,
        jwt_service: JWTService,
        pubsub_service: PubsubService,
        revoked_token_service: RevokedTokenService,
        user_service: UserService,
    ):
        self._db = db
        self._jwt_service = jwt_service
        self._pubsub_service = pubsub_service
        self._revoked_token_service = revoked_token_service
        self._user_service = user_service

    def _token_cookie_options(self) -> dict:
        return {
            "path": "/",
            "httponly": True,
            "secure": True if not settings.DEBUG else False,
            "samesite": "lax",
        }

    async def authenticate(self, request_id: UUID, token: str) -> User:
        decoded = self._jwt_service.verify(token)
        payload = JWTPayload.model_validate(decoded)

        # Check if the token has been revoked
        jti = payload.jti
        is_revoked = await self._revoked_token_service.is_revoked(jti)
        if is_revoked:
            raise UnauthorizedException(
                message="You are not authorized to perform this action",
                code="REVOKED_TOKEN",
                details=[f"Token with jti: {jti} has been revoked"],
            )

        provider_id = payload.provider_id
        if not decoded or not provider_id:
            raise UnauthorizedException(
                message="You are not authorized to perform this action",
                code="INVALID_TOKEN",
                details=[f"Invalid token provided in request with id: {request_id}"],
            )

        user = await self._user_service.get_by_provider_id(provider_id)
        return user

    async def authenticate_user(self, user: AuthUser) -> User | RedirectResponse:
        async with self._db.connection() as conn:
            try:
                app_user = await self._user_service.get_by_provider_id(
                    user.provider_id, conn
                )

                if not app_user:
                    # Create user record if account is not yet connected
                    app_user = await self._user_service.create(
                        UserCreate(
                            provider_id=user.provider_id,
                            first_name=user.first_name,
                            last_name=user.last_name,
                            email=user.email,
                            role=UserRole.STANDARD,
                            profile_picture=user.profile_picture,
                            provider=OAuthProvider.GOOGLE,
                        ),
                        connection=conn,
                    )

                    await self._pubsub_service.publish(
                        channel=settings.ADMIN_USER_ANALYTICS_CH,
                        data="Users analytics data updated",
                    )

                    await conn.commit()

                    # Notify admin dashboard about users count
                    await self._pubsub_service.publish(
                        channel=settings.ADMIN_DASHBOARD_CH,
                        data="Admin dashboard data updated",
                    )

                    logger.info(
                        "New account with provider id: %s has successfully connected to the app",
                        user.provider_id,
                    )
                elif not app_user.is_active:
                    raise UnauthorizedException(
                        message="Your account has been deactivated. Please contact the admins for more information"
                    )

                return app_user
            except UnauthorizedException:
                return self.redirect_unauthorized(error_code="ACCOUNT_DISABLED")
            except Exception as ex:
                await conn.rollback()
                raise

    def redirect_authorized(
        self, request: Request, token: str, user_role: UserRole
    ) -> RedirectResponse | None:
        try:
            if not token:
                raise UnauthorizedException("Token not found")

            url = redirect_service.get_redirect_url(
                "admin" if user_role == UserRole.ADMIN else "workspace"
            )
            redirect = RedirectResponse(url=url)
            redirect.set_cookie(
                key="token",
                value=token,
                **self._token_cookie_options(),
            )

            return redirect
        except Exception as ex:
            logger.exception(ex)

            return self.redirect_unauthorized(request)

    def redirect_unauthorized(
        self, request: Request = None, error_code: str = "INTERNAL_SERVER_ERROR"
    ) -> RedirectResponse:
        if request is not None:
            request.session.clear()

        url = redirect_service.get_redirect_url(
            "login", payload={"error_code": error_code}
        )
        redirect = RedirectResponse(url=url)
        redirect.delete_cookie(key="token", **self._token_cookie_options())
        return redirect

    async def logout(self, request: Request, response: Response) -> str:
        # Revoke the token
        token = request.cookies.get("token")
        if token:
            decoded = self._jwt_service.verify(token)
            payload = JWTPayload.model_validate(decoded)
            jti = payload.jti
            expiration_time = payload.exp
            await self._revoked_token_service.add_revoked_token(
                RevokedToken(
                    jti=jti, expires_at=datetime.fromtimestamp(expiration_time)
                )
            )

        # Clear session variables
        request.session.clear()

        # Clear cookies
        response.delete_cookie(key="token", **self._token_cookie_options())

        return redirect_service.get_redirect_url("login")
