from psycopg import errors
from uuid import UUID
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisVersion
from backend.app.schema.case_analysis_schema import (
    CaseAnalysisVersionCreate,
    CaseAnalysisGetByVersionNumber,
)
from backend.app.util.case_analysis_version_caster import CaseAnalysisVersionCaster


class CaseAnalysisVersionRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create(
        self,
        case_analysis_version: CaseAnalysisVersionCreate,
        connection: AsyncConnection = None,
    ) -> CaseAnalysisVersion:
        if connection is not None:
            return await self._create_implement(connection, case_analysis_version)

        async with self._database.connection() as conn:
            try:
                result = await self._create_implement(conn, case_analysis_version)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _create_implement(
        self, conn: AsyncConnection, case_analysis_version: CaseAnalysisVersionCreate
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO case_analysis_versions (
                    id,
                    case_analysis_session_id,
                    version_number,
                    answer,
                    created_at
                ) VALUES (
                    %(id)s,
                    %(case_analysis_session_id)s,
                    %(version_number)s,
                    %(answer)s,
                    %(created_at)s
                )
                """,
                (case_analysis_version.model_dump()),
            )

        return CaseAnalysisVersionCaster.create_to_base(case_analysis_version)

    async def get_latest_by_session_id(
        self,
        case_analysis_session_id: UUID,
        connection: AsyncConnection = None,
    ):
        if connection is not None:
            return await self._get_latest_by_session_id_implement(
                connection, case_analysis_session_id
            )

        async with self._database.connection() as conn:
            try:
                result = await self._get_latest_by_session_id_implement(
                    conn, case_analysis_session_id
                )
                await conn.commit()
                return result
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                await conn.rollback()
                raise

    async def _get_latest_by_session_id_implement(
        self, conn: AsyncConnection, case_analysis_session_id: UUID
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                SELECT cav.*
                FROM case_analysis_versions cav
                INNER JOIN case_analysis_sessions cas
                    ON cav.case_analysis_session_id = cas.id
                WHERE cas.id = %s
                ORDER BY cav.created_at DESC
                LIMIT 1
                """,
                (case_analysis_session_id,),
            )

            row = await cur.fetchone()
        return CaseAnalysisVersion.model_validate(row) if row is not None else None

    async def get_by_version_number(
        self,
        param: CaseAnalysisGetByVersionNumber,
        connection: AsyncConnection = None,
    ):
        if connection is not None:
            return await self._get_by_version_number_implement(connection, param)

        async with self._database.connection() as conn:
            try:
                result = await self._get_by_version_number_implement(conn, param)
                await conn.commit()
                return result
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                await conn.rollback()
                raise

    async def _get_by_version_number_implement(
        self, conn: AsyncConnection, param: CaseAnalysisGetByVersionNumber
    ):
        async with conn.cursor() as cur:
            session_id_query = ""
            if param.case_analysis_session_id is not None:
                session_id_query = (
                    "case_analysis_session_id = %(case_analysis_session_id)s AND"
                )

            await cur.execute(
                f"""
                SELECT *
                FROM case_analysis_versions
                WHERE {session_id_query} version_number = %(version_number)s
                LIMIT 1
                """,
                param.model_dump(),
            )

            row = await cur.fetchone()
        return CaseAnalysisVersion.model_validate(row) if row is not None else None
