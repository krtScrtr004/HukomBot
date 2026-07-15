from typing import List
from psycopg import errors
from uuid import UUID
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisSession
from backend.app.schema.case_analysis_schema import CaseAnalysisSessionCreate


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
        self, conn: AsyncConnection, case_analysis_session: CaseAnalysisSessionCreate
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO case_analysis_sessions (id, created_at, updated_at) 
                VALUES (%(id)s, %(created_at)s, %(updated_at)s) 
                """,
                (case_analysis_session.model_dump()),
            )

            return CaseAnalysisSession(
                id=case_analysis_session.id,
                created_at=case_analysis_session.created_at,
                updated_at=case_analysis_session.updated_at,
            )
            
    async def is_existing_by_id(self, id: UUID) -> bool:
        async with self._database.connection() as conn:
            try:
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
                await conn.commit()
                return row is not None
            except errors.OperationalError as ex:
                raise