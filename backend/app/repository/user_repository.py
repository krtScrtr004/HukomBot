from psycopg import errors
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.user_model import User
from backend.app.schema.user_schema import UserCreate, UserSearch


class UserRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create(
        self,
        user: UserCreate,
        connection: AsyncConnection = None,
    ) -> User:
        if connection is not None:
            return await self._create_implement(connection, user)

        async with self._database.connection() as conn:
            try:
                result = await self._create_implement(conn, user)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _create_implement(
        self,
        conn: AsyncConnection,
        user: UserCreate,
    ) -> User:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO users (
                    id,
                    provider_id,
                    first_name,
                    last_name,
                    email,
                    provider,
                    profile_picture, 
                    role
                ) VALUES (
                    %(id)s,
                    %(provider_id)s,
                    %(first_name)s,
                    %(last_name)s,
                    %(email)s,
                    %(provider)s,
                    %(profile_picture)s,
                    %(role)s
                ) RETURNING is_active, created_at, updated_at
            """,
                user.model_dump(),
            )

            row = await cur.fetchone()
            user_is_active = row["is_active"]
            user_created_at = row["created_at"]
            user_updated_at = row["updated_at"]

        return User(
            id=user.id,
            provider_id=user.provider_id,
            first_name=user.first_name,
            last_name=user.last_name,
            email=user.email,
            profile_picture=user.profile_picture,
            role=user.role,
            provider=user.provider,
            is_active=user_is_active,
            created_at=user_created_at,
            updated_at=user_updated_at
        )

    async def get_by_provider_id(
        self, provider_id: str, connection: AsyncConnection = None
    ):
        if not provider_id:
            return None
        
        if connection is not None:
            return await self._get_by_provider_id_implement(connection, provider_id)
        
        async with self._database.connection() as conn:
            try:
                result = await self._get_by_provider_id_implement(conn, provider_id)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_by_provider_id_implement(
        self, conn: AsyncConnection, provider_id: str
    ) -> User | None:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT *
                FROM users
                WHERE provider_id = %s
                LIMIT 1
                """,
                (provider_id,),
            )

            row = await cur.fetchone()

        return User.model_validate(row) if row is not None else None

    async def search(
        self, user: UserSearch, connection: AsyncConnection = None
    ) -> list[User]:
        if connection is not None:
            return await self._search_implement(connection, user)

        async with self._database.connection() as conn:
            try:
                result = await self._search_implement(conn, user)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _search_implement(self, conn: AsyncConnection, user: UserSearch):
        search_comps = [
            user.first_name,
            user.last_name,
            user.email,
            user.provider.value,
        ]
        terms = " ".join([item for item in search_comps if item])

        async with conn.cursor() as cur:
            await cur.execute(
                """
                WITH query AS (
                    SELECT plainto_tsquery('english',  %s) AS q
                )
                SELECT 
                    u.*,
                    ts_rank(u.search_vector, q.q) AS rank
                FROM users u, query q
                WHERE u.search_vector @@ q.q
                ORDER BY rank DESC
                LIMIT %s
                OFFSET %s
                """,
                (terms, user.limit, user.offset),
            )

            rows = await cur.fetchall()

        users = []
        for row in rows:
            users.append(User.model_validate(row))

        return users
