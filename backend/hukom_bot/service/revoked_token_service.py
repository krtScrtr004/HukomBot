from uuid import UUID
from psycopg import AsyncConnection
from backend.hukom_bot.schema.auth_schema import RevokedToken
from backend.hukom_bot.repository.revoked_token_repository import RevokedTokenRepository


class RevokedTokenService:
    def __init__(self, revoked_token_repo: RevokedTokenRepository):
        self._revoked_token_repo = revoked_token_repo

    async def add_revoked_token(
        self, revoked_token: RevokedToken, connection: AsyncConnection = None
    ) -> RevokedToken:
        return await self._revoked_token_repo.add(
            revoked_token=revoked_token, connection=connection
        )

    async def is_revoked(self, jti: UUID, connection: AsyncConnection = None) -> bool:
        return await self._revoked_token_repo.is_revoked(jti=jti, connection=connection)

    async def delete_expired_tokens(
        self, limit: int = 100, connection: AsyncConnection = None
    ) -> None:
        await self._revoked_token_repo.delete_expired(
            limit=limit, connection=connection
        )
