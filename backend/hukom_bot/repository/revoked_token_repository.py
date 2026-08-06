from uuid import UUID
from psycopg import errors
from psycopg import AsyncConnection

from backend.hukom_bot.database.database import Database
from backend.hukom_bot.schema.auth_schema import RevokedToken


class RevokedTokenRepository:
    def __init__(self, db: Database):
        self._database = db

    async def add(
        self, revoked_token: RevokedToken, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._add_implement(connection, revoked_token)

        async with self._database.connection() as conn:
            try:
                result = await self._add_implement(conn, revoked_token)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _add_implement(self, conn: AsyncConnection, revoked_token: RevokedToken):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO revoked_tokens (
                    jti,
                    expired_at
                ) VALUES (
                    %(jti)s,
                    %(expired_at)s
                )
            """,
                revoked_token.model_dump(),
            )

    async def is_revoked(self, jti: UUID, connection: AsyncConnection = None) -> bool:
        if connection is not None:
            return await self._is_revoked_implement(connection, jti)

        async with self._database.connection() as conn:
            try:
                result = await self._is_revoked_implement(conn, jti)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _is_revoked_implement(self, conn: AsyncConnection, jti: UUID) -> bool:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT EXISTS (
                    SELECT 1 FROM revoked_tokens WHERE jti = %(jti)s
                )
            """,
                {"jti": jti},
            )
            result = await cur.fetchone()
            return result[0] if result else False

    async def delete_expired(
        self, limit: int = 100, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._delete_expired_implement(connection, limit)

        async with self._database.connection() as conn:
            try:
                result = await self._delete_expired_implement(conn, limit)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _delete_expired_implement(self, conn: AsyncConnection, limit: int):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM revoked_tokens
                WHERE expired_at <= NOW()
                LIMIT %s
            """,
                (limit,),
            )
