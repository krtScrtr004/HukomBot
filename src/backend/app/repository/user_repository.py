from backend.app.database.database import Database
from backend.app.model.user_model import User
from backend.app.schema.user_schema import UserCreate, UserSearch
from psycopg import errors
from typing import List
from psycopg import AsyncConnection


class UserRepositry:
    def __init__(self, db: Database):
        self.__database = db

    async def create(
        self,
        user: UserCreate,
        connection: AsyncConnection = None,
    ) -> User:
        if connection is not None:
            return await self.__create_implement(connection, user)
        async with self.__database.connection() as conn:
            return await self.__create_implement(conn, user)

    async def __create_implement(
        self,
        conn: AsyncConnection,
        user: UserCreate,
    ) -> User:
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO user (
                        id,
                        email, 
                        display_name, 
                        avatar_url, 
                        provider, 
                        provider_id, 
                        access_token, 
                        refresh_token, 
                        token_expires_at
                    ) VALUES (
                        %(id)s,
                        %(email)s,
                        %(display_name)s,
                        %(avatar_url)s,
                        %(provider)s,
                        %(provider_id)s,
                        %(access_token)s,
                        %(refresh_token)s,
                        %(token_expires_at)s
                    ) RETURNING is_active, last_login_at, created_at, updated_at
                """,
                    user.model_dump(),
                )

                row = await cur.fetchone()
                user_is_active = row["is_active"]
                user_last_login_at = row["last_login_at"]
                user_created_at = row["created_at"]
                user_updated_at = row["updated_at"]

            await conn.commit()
            return User(
                id=user.id,
                email=user.email,
                display_name=user.display_name,
                avatar_url=user.avatar_url,
                provider=user.provider,
                provider_id=user.provider_id,
                access_token=user.access_token,
                refresh_token=user.refresh_token,
                token_expires_at=user.token_expires_at,
                is_active=user_is_active,
                last_login_at=user_last_login_at,
                created_at=user_created_at,
                updated_at=user_updated_at,
            )
        except (errors.IntegrityError, errors.OperationalError) as ex:
            await conn.rollback()
            raise
        
    async def search(self, user: UserSearch) -> List[User]:
        async with self.__database.connection() as conn:
            try:
                search_comps = [user.display_name, user.email, user.provider.value]
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
                        (terms, user.limit, user.offset)
                    )
                    
                    rows = await cur.fetchall()
                    
                    users = []
                    for row in rows:
                        users.append(User.model_validate(row))
                    
                    return users
            except errors.OperationalError as ex:
                raise
            
