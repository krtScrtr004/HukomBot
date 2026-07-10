from typing import List
from psycopg import errors
from uuid import UUID

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisSession
from backend.app.schema.case_analysis_schema import CaseAnalysisSessionCreate


class CaseAnalysisSessionRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create(
        self, case_analysis_session: CaseAnalysisSessionCreate
    ) -> CaseAnalysisSession:
        async with self._database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO case_analysis_sessions (created_at, updated_at) 
                        VALUES (%(created_at)s, %(updated_at)s) 
                        RETURNING id
                        """,
                        (case_analysis_session.model_dump()),
                    )

                    case_analysis_session_id = (await cur.fetchone())["id"]
                await conn.commit()

                return CaseAnalysisSession(
                    id=case_analysis_session_id,
                    created_at=case_analysis_session.created_at,
                    updated_at=case_analysis_session.updated_at,
                )
            except (
                errors.ForeignKeyViolation,
                errors.IntegrityError,
                errors.OperationalError,
            ) as ex:
                await conn.rollback()
                raise

    async def get_by_id(self, id: UUID) -> CaseAnalysisSession | None:
        async with self._database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT *
                        FROM case_analysis_sessions
                        WHERE id = %s
                        LIMIT 1
                        """,
                        (id,),
                    )

                    row = await cur.fetchone()

                await conn.commit()
                return (
                    CaseAnalysisSession.model_validate(row) if row is not None else None
                )
            except errors.OperationalError as ex:
                raise

    async def delete(self, id: UUID):
        async with self._database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        DELETE FROM case_analysis_sessions
                        WHERE id = %s
                        """,
                        (id,),
                    )

                await conn.commit()
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise