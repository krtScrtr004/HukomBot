from psycopg import errors
from uuid import UUID
from psycopg import AsyncConnection

from backend.hukom_bot.database.database import Database
from backend.hukom_bot.model.case_analysis_model import CaseAnalysisSession
from backend.hukom_bot.schema.case_analysis_schema import (
    CaseAnalysisSessionCreate,
    CaseAnalysisGetByUserId,
    CaseAnalysisSessionPreviewSearch,
)
from backend.hukom_bot.util.case_analysis_session_caster import (
    CaseAnalysisSessionCaster,
)


class CaseAnalysisSessionRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create(
        self,
        case_analysis_session: CaseAnalysisSessionCreate,
        connection: AsyncConnection = None,
    ) -> CaseAnalysisSession:
        if connection is not None:
            return await self._create_implement(connection, case_analysis_session)

        async with self._database.connection() as conn:
            try:
                result = await self._create_implement(conn, case_analysis_session)
                await conn.commit()
                return result
            except (
                errors.ForeignKeyViolation,
                errors.IntegrityError,
                errors.OperationalError,
            ) as ex:
                await conn.rollback()
                raise

    async def _create_implement(
        self, conn: AsyncConnection, case_analysis_session: CaseAnalysisGetByUserId
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO case_analysis_sessions (id, user_id, created_at, updated_at) 
                VALUES (%(id)s, %(user_id)s, %(created_at)s, %(updated_at)s) 
                """,
                (case_analysis_session.model_dump()),
            )

            return CaseAnalysisSessionCaster.create_to_base(case_analysis_session)

    async def get_by_user_id(
        self, param: CaseAnalysisGetByUserId, connection: AsyncConnection = None
    ) -> list[CaseAnalysisSession]:
        if connection is not None:
            return await self._get_by_user_id_implement(conn=connection, param=param)

        async with self._database.connection() as conn:
            try:
                result = await self._get_by_user_id_implement(conn=conn, param=param)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _get_by_user_id_implement(
        self, conn: AsyncConnection, param: CaseAnalysisGetByUserId
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT *
                FROM case_analysis_sessions
                WHERE user_id = %(user_id)s
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                param.model_dump(),
            )

            rows = await cur.fetchall()

        sessions = []
        for row in rows:
            sessions.append(CaseAnalysisSession.model_validate(row))

        return sessions

    async def search(
        self,
        param: CaseAnalysisSessionPreviewSearch,
        connection: AsyncConnection = None,
    ):
        if connection is not None:
            return await self._search_implement(conn=connection, param=param)

        async with self._database.connection() as conn:
            try:
                result = await self._search_implement(conn=conn, param=param)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _search_implement(
        self, conn: AsyncConnection, param: CaseAnalysisSessionPreviewSearch
    ):
        async with conn.cursor() as cur:
            user_query = ""
            if param.user_id:
                user_query = " cas.user_id = %(user_id)s AND "
            
            await cur.execute(
                f"""
                WITH query AS (
                    SELECT plainto_tsquery('english', 'obligations and contracts') AS q
                )
                SELECT DISTINCT ON (cas.id)
                    cas.*,
                    ts_rank(cav.search_vector, query.q) AS rank
                FROM case_analysis_sessions cas
                JOIN case_analysis_versions cav
                    ON cav.case_analysis_session_id = cas.id
                CROSS JOIN query
                WHERE {user_query} 
                cav.search_vector @@ query.q
                OR EXISTS (
                    SELECT 1
                    FROM case_facts cf
                    JOIN case_fact_versions cfv ON cfv.case_fact_id = cf.id
                    WHERE cf.case_analysis_session_id = cas.id
                        AND cfv.fact ILIKE '%%' || %(query)s || '%%'
                )
                ORDER BY cas.id, rank DESC
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                param.model_dump(),
            )

            rows = await cur.fetchall()

            sessions = []
            for row in rows:
                sessions.append(CaseAnalysisSession.model_validate(row))

            return sessions

    async def is_existing_by_id(
        self, id: UUID, connection: AsyncConnection = None
    ) -> bool:
        if connection is not None:
            return await self._is_existing_by_id_implement(connection, id)

        async with self._database.connection() as conn:
            try:
                result = await self._is_existing_by_id_implement(conn, id)
                await conn.commit()
                return result
            except errors.OperationalError as ex:
                await conn.rollback()
                raise

    async def _is_existing_by_id_implement(self, conn: AsyncConnection, id: UUID):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT 1
                FROM case_analysis_sessions
                WHERE id = %s
                LIMIT 1
                """,
                (id,),
            )

            row = await cur.fetchone()
        return row is not None

    async def delete(self, id: UUID, connection: AsyncConnection = None):
        if connection is not None:
            await self._delete_implement(connection, id)
        else:
            async with self._database.connection() as conn:
                try:
                    await self._delete_implement(conn, id)
                    await conn.commit()
                except errors.OperationalError as ex:
                    await conn.rollback()
                    raise

    async def _delete_implement(self, conn: AsyncConnection, id: UUID):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                DELETE FROM case_analysis_sessions
                WHERE id = %s 
                """,
                (id,),
            )
