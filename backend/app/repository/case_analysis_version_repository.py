from psycopg import errors
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisVersion
from backend.app.schema.case_analysis_schema import (
    CaseAnalysisGetByUserId,
    CaseAnalysisGetBySessionId,
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
                    title,
                    version_number,
                    answer,
                    answer_format,
                    created_at
                ) VALUES (
                    %(id)s,
                    %(case_analysis_session_id)s,
                    %(title)s,
                    %(version_number)s,
                    %(answer)s,
                    %(answer_format)s,
                    %(created_at)s
                )
                """,
                (case_analysis_version.model_dump()),
            )

        return CaseAnalysisVersionCaster.create_to_base(case_analysis_version)

    async def get_latest_by_session_id(
        self,
        param: CaseAnalysisGetBySessionId,
        connection: AsyncConnection = None,
    ):
        if connection is not None:
            return await self._get_latest_by_session_id_implement(
                conn=connection, param=param
            )

        async with self._database.connection() as conn:
            try:
                result = await self._get_latest_by_session_id_implement(
                    conn=conn, param=param
                )
                await conn.commit()
                return result
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                await conn.rollback()
                raise

    async def _get_latest_by_session_id_implement(
        self, 
        conn: AsyncConnection, 
        param: CaseAnalysisGetBySessionId,
    ):
        async with conn.cursor() as cur:
            user_query = ""
            if param.user_id:
                user_query = "AND cas.user_id = %(user_id)s"

            await cur.execute(
                f"""
                SELECT cav.*
                FROM case_analysis_versions cav
                INNER JOIN case_analysis_sessions cas
                    ON cav.case_analysis_session_id = cas.id
                {user_query}
                WHERE cas.id = %(case_analysis_session_id)s
                ORDER BY cav.created_at DESC
                LIMIT 1
                """,
                param.model_dump(),
            )

            row = await cur.fetchone()
        return CaseAnalysisVersion.model_validate(row) if row is not None else None

    async def get_by_session_id(
        self,
        param: CaseAnalysisGetBySessionId,
        connection: AsyncConnection = None,
    ):
        if connection is not None:
            return await self._get_by_session_id_implement(connection, param)

        async with self._database.connection() as conn:
            try:
                result = await self._get_by_session_id_implement(conn, param)
                await conn.commit()
                return result
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                await conn.rollback()
                raise

    async def _get_by_session_id_implement(
        self, conn: AsyncConnection, param: CaseAnalysisGetBySessionId
    ):
        async with conn.cursor() as cur:
            user_query = ""
            if param.user_id:
                user_query = """
                    INNER JOIN case_analysis_sessions cas
                        ON cav.case_analysis_session_id = cas.id
                        AND cas.user_id = %(user_id)s
                    """
                
            await cur.execute(
                f"""
                SELECT *
                FROM case_analysis_versions cav
                {user_query}
                WHERE cav.case_analysis_session_id = %(case_analysis_session_id)s
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                param.model_dump(),
            )

            rows = await cur.fetchall()

        versions = []
        for row in rows:
            versions.append(CaseAnalysisVersion.model_validate(row))

        return versions

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
            user_query = ""
            if param.user_id:
                user_query = """
                    INNER JOIN case_analysis_sessions cas
                        ON cav.case_analysis_session_id = cas.id
                        AND cas.user_id = %(user_id)s
                    """
                    
            session_query = ""
            if param.case_analysis_session_id:
                session_query = (
                    "cav.case_analysis_session_id = %(case_analysis_session_id)s AND"
                )                

            await cur.execute(
                f"""
                SELECT *
                FROM case_analysis_versions cav
                {user_query}
                WHERE {session_query} 
                    cav.version_number = %(version_number)s
                LIMIT 1
                """,
                param.model_dump(),
            )

            row = await cur.fetchone()
        return CaseAnalysisVersion.model_validate(row) if row is not None else None

    async def get_latest_by_user_id(
        self, param: CaseAnalysisGetByUserId, connection: AsyncConnection = None
    ) -> list[CaseAnalysisVersion]:
        if connection is not None:
            return await self._get_latest_by_user_id_implement(connection, param)

        async with self._database.connection() as conn:
            try:
                result = await self._get_latest_by_user_id_implement(conn, param)
                await conn.commit()
                return result
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                await conn.rollback()
                raise

    async def _get_latest_by_user_id_implement(
        self, conn: AsyncConnection, param: CaseAnalysisGetByUserId
    ):
        async with conn.cursor() as cur:
            await cur.execute("""
                SELECT DISTINCT ON (cav.case_analysis_session_id)
                    cav.*
                FROM case_analysis_versions cav
                JOIN case_analysis_sessions cas
                    ON cas.id = cav.case_analysis_session_id
                WHERE cas.user_id = %(user_id)s
                ORDER BY
                    cav.case_analysis_session_id,
                    cav.version_number desc
                LIMIT %(limit)s
                OFFSET %(offset)s
                """,
                param.model_dump()
            )
            
            rows = await cur.fetchall()
            
        latest_analyses = []
        for row in rows:
            latest_analyses.append(
                CaseAnalysisVersion.model_validate(row)
            )
            
        return latest_analyses