from uuid import UUID
from psycopg import errors
from psycopg import AsyncConnection
from backend.hukom_bot.database.database import Database
from backend.hukom_bot.model.user_model import User
from backend.hukom_bot.schema.user_schema import *
from backend.hukom_bot.schema.admin_schema import MonthlyCount, UserRoleCount
from backend.hukom_bot.schema.mixin import DateRangeableMixin
from backend.hukom_bot.util.user_caster import UserCaster
from backend.hukom_bot.util.utility import build_date_range_where_clause


class UserRepository:
    def __init__(self, db: Database):
        self._database = db

    # CREATE ============================================================================

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

        return UserCaster.create_to_base(
            user=user,
            is_active=user_is_active,
            created_at=user_created_at,
            updated_at=user_updated_at,
        )

    # UPDATE ============================================================================

    async def update(
        self,
        user: UserUpdate,
        connection: AsyncConnection = None,
    ):
        if not user.model_dump(exclude={"id"}, exclude_none=True):
            return

        if connection is not None:
            await self._update_implement(connection, user)
            return

        async with self._database.connection() as conn:
            try:
                await self._update_implement(conn, user)
                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _update_implement(self, conn: AsyncConnection, user: UserUpdate):
        query, params = self._build_update_query(user)

        async with conn.cursor() as cur:
            await cur.execute(query, params)

    def _build_update_query(self, user: UserUpdate) -> tuple[str, tuple]:
        set_clauses = []
        values = {"id": user.id}

        if user.first_name:
            set_clauses.append("first_name = %(first_name)s")
            values["first_name"] = user.first_name
        if user.last_name:
            set_clauses.append("last_name = %(last_name)s")
            values["last_name"] = user.last_name
        if user.profile_picture:
            set_clauses.append("profile_picture = %(profile_picture)s")
            values["profile_picture"] = user.profile_picture
        if user.role:
            set_clauses.append("role = %(role)s")
            values["role"] = user.role.value
        if user.is_active is not None:
            set_clauses.append("is_active = %(is_active)s")
            values["is_active"] = user.is_active

        if not set_clauses:
            raise RuntimeError("No fields to update")

        query = f"""
            UPDATE users 
            SET {", ".join(set_clauses)}
            WHERE id = %(id)s
        """

        return query, values

    # READ =============================================================================

    async def get_by_id(self, id: UUID, connection: AsyncConnection = None):
        if not id:
            return None

        if connection is not None:
            return await self._get_by_id_implement(connection, id)

        async with self._database.connection() as conn:
            try:
                result = await self._get_by_id_implement(conn, id)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_by_id_implement(
        self, conn: AsyncConnection, id: UUID
    ) -> User | None:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT 
                    u.*,
                    (
                        SELECT COUNT(d.id)
                        FROM documents d
                        WHERE d.uploader_id = u.id
                    ) AS upload_count
                FROM users u
                WHERE id = %s
                LIMIT 1
                """,
                (id,),
            )

            row = await cur.fetchone()

        return User.model_validate(row) if row is not None else None

    async def get_by_many_id(
        self, param: UserGetByManyId, connection: AsyncConnection = None
    ):
        if not id:
            return None

        if connection is not None:
            return await self._get_by_many_id_implement(conn=connection, param=param)

        async with self._database.connection() as conn:
            try:
                result = await self._get_by_many_id_implement(conn=conn, param=param)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_by_many_id_implement(
        self, conn: AsyncConnection, param: UserGetByManyId
    ) -> list[User]:
        async with conn.cursor() as cur:
            placeholders = ", ".join(f"%(id_{i})s" for i, _ in enumerate(param.ids))
            params = {f"id_{i}": id for i, id in enumerate(param.ids)}
            params["limit"] = param.limit
            params["offset"] = param.offset

            await cur.execute(
                f"""
                SELECT 
                    u.*,
                    (
                        SELECT COUNT(d.id)
                        FROM documents d
                        WHERE d.uploader_id = u.id
                    ) AS upload_count
                FROM users u
                WHERE u.id IN ({placeholders})
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                params,
            )

            rows = await cur.fetchall()
        users = []
        for row in rows:
            users.append(User.model_validate(row))

        return users

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
                SELECT 
                    u.*,
                    (
                        SELECT COUNT(d.id)
                        FROM documents d
                        WHERE d.uploader_id = u.id
                    ) AS upload_count
                FROM users u
                WHERE u.provider_id = %s
                LIMIT 1
                """,
                (provider_id,),
            )

            row = await cur.fetchone()

        return User.model_validate(row) if row is not None else None

    async def get_most_upload_count(
        self, limit: int = 10, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._get_most_upload_count(connection, limit)

        async with self._database.connection() as conn:
            try:
                result = await self._get_most_upload_count(conn, limit)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_most_upload_count(self, conn: AsyncConnection, limit: int = 10):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT 
                    u.*,
                    (
                        SELECT COUNT(d.id)
                        FROM documents d
                        WHERE d.uploader_id = u.id
                    ) AS upload_count
                FROM users u
                ORDER BY 
                    upload_count DESC,
                    u.last_name ASC,
                    u.first_name ASC
                LIMIT %s
                """,
                (limit,),
            )

            rows = await cur.fetchall()
            users = [User(row) for row in rows]

            return users

    def _build_search_query(self, user: UserSearch) -> str:
        conditions: list[str] = []

        if user.is_active is not None:
            conditions.append("u.is_active = %(is_active)s")

        if user.role is not None:
            conditions.append("u.role = %(role)s")

        if user.oauth_provider is not None:
            conditions.append("u.provider = %(oauth_provider)s")

        if not conditions:
            return ""

        return "AND " + " AND ".join(conditions)

    async def search(
        self, user: UserSearch, connection: AsyncConnection = None
    ) -> list[User]:
        if connection is not None:
            return await self._search_implement(conn=connection, user=user)

        async with self._database.connection() as conn:
            try:
                result = await self._search_implement(conn=conn, user=user)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _search_implement(self, conn: AsyncConnection, user: UserSearch):
        column_order = ", ".join(f"{col} {user.order.value}" for col in user.column)
        search_query = self._build_search_query(user)

        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT * FROM (
                    WITH query AS (
                        SELECT plainto_tsquery('english',  %(query)s) AS q
                    )
                    SELECT 
                        u.*,
                        (
                            SELECT COUNT(d.id)
                            FROM documents d
                            WHERE d.uploader_id = u.id
                        ) AS upload_count,
                        ts_rank(u.search_vector, q.q) AS rank
                    FROM users u, query q
                    WHERE u.search_vector @@ q.q
                    {search_query}
                    ORDER BY rank DESC                    
                ) ORDER BY {column_order}
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                user.model_dump(),
            )

            rows = await cur.fetchall()

        users = []
        for row in rows:
            users.append(User.model_validate(row))

        return users

    async def all(
        self, param: UserGetAll, connection: AsyncConnection = None
    ) -> list[User]:
        if connection is not None:
            return await self._all_implement(connection, param)

        async with self._database.connection() as conn:
            try:
                result = await self._all_implement(conn, param)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _all_implement(
        self, conn: AsyncConnection, param: UserGetAll
    ) -> list[User]:
        column_order = ", ".join(f"{col} {param.order.value}" for col in param.column)
        search_query = self._build_search_query(param)

        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT 
                    u.*,
                    (
                        SELECT COUNT(d.id)
                        FROM documents d
                        WHERE d.uploader_id = u.id
                    ) AS upload_count
                FROM users u
                WHERE 1=1
                {search_query}
                ORDER BY {column_order}
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                param.model_dump(),
            )

            rows = await cur.fetchall()

        users = []
        for row in rows:
            users.append(User.model_validate(row))

        return users

    async def count_all(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._count_all_implement(
                conn=connection, date_range=date_range
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_all_implement(conn=conn, date_range=date_range)
        except errors.OperationalError:
            raise

    async def _count_all_implement(
        self, conn: AsyncConnection, date_range: DateRangeableMixin | None
    ) -> int:
        async with conn.cursor() as cur:
            date_range_query = (
                build_date_range_where_clause(
                    column_name="u.created_at",
                    date_rangeable=date_range,
                    include_where=True,
                )
                if date_range is not None
                else ""
            )

            await cur.execute(
                f"""
                SELECT COUNT(u.id) 
                FROM users u 
                {date_range_query}
                """,
            )

            row = await cur.fetchone()
            return row["count"]

    async def count_active(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        user = UserGetByActiveState(
            is_active=True, **date_range.model_dump() if date_range is not None else {}
        )

        if connection is not None:
            return await self._count_by_active_state_implement(
                conn=connection, user=user
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_by_active_state_implement(conn=conn, user=user)
        except errors.OperationalError:
            raise

    async def count_inactive(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        user = UserGetByActiveState(
            is_active=False, **date_range.model_dump() if date_range is not None else {}
        )

        if connection is not None:
            return await self._count_by_active_state_implement(
                conn=connection, user=user
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_by_active_state_implement(conn=conn, user=user)
        except errors.OperationalError:
            raise

    async def _count_by_active_state_implement(
        self, conn: AsyncConnection, user: UserGetByActiveState
    ) -> int:
        async with conn.cursor() as cur:
            dump = user.model_dump()

            date_range = DateRangeableMixin(**dump)
            date_range_query = (
                build_date_range_where_clause(
                    column_name="u.created_at", date_rangeable=date_range
                )
                if any(date_range.model_dump().values())
                else ""
            )

            await cur.execute(
                f"""
                SELECT COUNT(u.id) 
                FROM users u 
                WHERE u.is_active = %(is_active)s
                {date_range_query}
                """,
                dump,
            )

            row = await cur.fetchone()
            return row["count"]

    async def count_monthly_registration(
        self, year: int = datetime.now().year, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._count_monthly_registration_implement(
                conn=connection, year=year
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_monthly_registration_implement(
                    conn=conn, year=year
                )
        except errors.OperationalError:
            raise

    async def _count_monthly_registration_implement(
        self, conn: AsyncConnection, year: int
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                f"""
                SELECT 
                    lower(left(to_char(created_at, 'FMMonth'), 1)) || 
                        substring(to_char(created_at, 'FMMonth') from 2) AS month_name,
                    COUNT(*) AS total_count
                FROM users
                WHERE EXTRACT(YEAR FROM created_at) = %s
                GROUP BY 
                    date_trunc('month', created_at), 
                    to_char(created_at, 'FMMonth')
                ORDER BY 
                    date_trunc('month', created_at) ASC;
                """,
                (year,),
            )

            rows = await cur.fetchall()
            if not rows:
                return MonthlyCount()

            monthly_counts = {row["month_name"]: row["total_count"] for row in rows}

            return MonthlyCount(**monthly_counts)

    async def count_registration(
        self, interval_days: int = 360, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._count_registration_implement(
                conn=connection, interval_days=interval_days
            )

        try:
            async with self._database.connection() as conn:
                return await self._count_registration_implement(
                    conn=conn, interval_days=interval_days
                )
        except errors.OperationalError:
            raise

    async def _count_registration_implement(
        self, conn: AsyncConnection, interval_days: int
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT COUNT(*) FROM users
                WHERE created_at >= CURRENT_DATE - INTERVAL '%s days';
                """,
                (interval_days,),
            )

            row = await cur.fetchone()
            return row["count"]

    async def count_by_role(
        self, date_range: DateRangeableMixin = None, connection: AsyncConnection = None
    ):
        if connection is not None:
            return await self._count_by_role(conn=connection, date_range=date_range)

        try:
            async with self._database.connection() as conn:
                return await self._count_by_role(conn=conn, date_range=date_range)
        except errors.OperationalError:
            raise

    async def _count_by_role(
        self,
        conn: AsyncConnection,
        date_range: DateRangeableMixin | None,
    ):
        async with conn.cursor() as cur:
            date_range_query = (
                build_date_range_where_clause(
                    column_name="u.created_at",
                    date_rangeable=date_range,
                    include_where=True,
                )
                if date_range is not None
                else ""
            )

            await cur.execute(
                f"""
                SELECT role, COUNT(*)
                FROM users
                {date_range_query}
                GROUP BY role
                """,
            )

            rows = await cur.fetchall()
            if not rows:
                return UserRoleCount()

            role_counts = {row["role"]: row["count"] for row in rows}

            return UserRoleCount(**role_counts)

    # DELETE ============================================================================

    async def delete(self, id: UUID, connection: AsyncConnection = None):
        if connection is not None:
            await self._delete_implement(conn=connection, id=id)
            return

        async with self._database.connection() as conn:
            try:
                await self._delete_implement(conn=conn, id=id)
                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _delete_implement(self, conn: AsyncConnection, id: UUID):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM users
                WHERE id = %s
                """,
                (id,),
            )
