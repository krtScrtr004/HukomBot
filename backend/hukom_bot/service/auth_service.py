import logging
from uuid import UUID
from datetime import datetime
from fastapi import Request, Response
from fastapi.responses import RedirectResponse

from backend.hukom_bot.service.redirect_service import redirect_service

from backend.hukom_bot.database.database import Database
from backend.hukom_bot.enum.user_role import UserRole
from backend.hukom_bot.enum.oauth_provider import OAuthProvider

from backend.hukom_bot.model.user_model import User

from backend.hukom_bot.schema.user_schema import UserCreate
from backend.hukom_bot.schema.auth_schema import AuthUser, JWTPayload, RevokedToken

from backend.hukom_bot.service.jwt_service import JWTService
from backend.hukom_bot.service.revoked_token_service import RevokedTokenService
from backend.hukom_bot.service.user_service import UserService
from backend.hukom_bot.exception.app_exception import UnauthorizedException

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        db: Database,
        user_service: UserService,
        revoked_token_service: RevokedTokenService,
        jwt_service: JWTService,
    ):
        self._db = db
        self._user_service = user_service
        self._revoked_token_service = revoked_token_service
        self._jwt_service = jwt_service

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

    async def authenticate_user(self, user: AuthUser) -> User:
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

                    await conn.commit()

                    logger.info(
                        "New account with provider id: %s has successgully connected to the app",
                        user.provider_id,
                    )

                return app_user
            except Exception as ex:
                logger.exception(str(ex))
                await conn.rollback()
                raise

    def redirect_authorized(self, request: Request, token: str) -> RedirectResponse | None:
        try:
            if not token:
                raise UnauthorizedException("Token not found")

            url = redirect_service.get_redirect_url("workspace")
            redirect = RedirectResponse(url=url)
            # Set jwt on cookie
            redirect.set_cookie(
                key="token",
                value=token,
                httponly=True,
                secure=True,  # REQUIRED when samesite="none" — cookie won't be sent otherwise
                samesite="none",  # REQUIRED for cross-domain — "lax" (the default) blocks this
                domain=None,
            )
            
            return redirect
        except Exception:
            return self.redirect_unauthorized(request)

    def redirect_unauthorized(
        self, request: Request, error_code: str = "INTERNAL_SERVER_ERROR"
    ) -> RedirectResponse:
        request.session.clear()
        url = redirect_service.get_redirect_url(
            "login", payload={"error_code": error_code}
        )
        redirect = RedirectResponse(url=url)
        redirect.delete_cookie(key="token", path="/", httponly=True)
        return redirect

    async def logout(self, request: Request, response: Response) -> str:
        # Rovoke the token
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
        response.delete_cookie(
            key="token",
            path="/",
            httponly=True,
            secure=True,      # Keep “True” in production; set to False only for local dev
            samesite="none",
        )
        
        return redirect_service.get_redirect_url("login")
