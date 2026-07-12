from typing import List
from psycopg import errors
from uuid import UUID
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisVersion
from backend.app.schema.case_analysis_schema import CaseAnalysisVersionCreate


class CaseAnalysisVersionRepository:
    def __init__(self, db: Database):
        self.__database = db

    async def create(
        self,
        case_analysis_version: CaseAnalysisVersionCreate,
        connection: AsyncConnection = None,
    ) -> CaseAnalysisVersion:
        if connection is not None:
            return await self.__create_implement(connection, case_analysis_version)

        async with self.__database.connection() as conn:
            try:
                result = await self.__create_implement(conn, case_analysis_version)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def __create_implement(
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

        return CaseAnalysisVersion(
            id=case_analysis_version.id,
            case_analysis_session_id=case_analysis_version.case_analysis_session_id,
            version_number=case_analysis_version.version_number,
            answer=case_analysis_version.answer,
            created_at=case_analysis_version.created_at,
        )

    async def create_many(
        self,
        case_analysis_versions: List[CaseAnalysisVersionCreate],
        connection: AsyncConnection = None,
    ) -> List[CaseAnalysisVersion]:
        if not case_analysis_versions:
            return []

        if connection is not None:
            return await self.__create_many_implement(
                connection, case_analysis_versions
            )

        async with self.__database.connection() as conn:
            try:
                result = await self.__create_many_implement(
                    conn, case_analysis_versions
                )
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def __create_many_implement(
        self,
        conn: AsyncConnection,
        case_analysis_versions: List[CaseAnalysisVersionCreate],
    ):
        async with conn.cursor() as cur:
            await cur.executemany(
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
                [
                    analysis_version.model_dump()
                    for analysis_version in case_analysis_versions
                ],
            )

        # Retrieve the generated IDs
        updated = []
        for i, _ in enumerate(case_analysis_versions):
            updated.append(
                CaseAnalysisVersion(
                    id=case_analysis_versions[i].id,
                    case_analysis_session_id=case_analysis_versions[
                        i
                    ].case_analysis_session_id,
                    version_number=case_analysis_versions[i].version_number,
                    answer=case_analysis_versions[i].answer,
                    created_at=case_analysis_versions[i].created_at,
                )
            )

        return updated

    async def get_id_by_session_id(
        self, case_analysis_session_id: UUID
    ) -> UUID|None:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT cav.id
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
                await conn.commit()
                return (
                    row["id"]
                    if row is not None and row["id"] is not None
                    else None
                )
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                raise

    async def get_latest_analysis_version_by_session_id(
        self, case_analysis_session_id: UUID
    ) -> int | None:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        SELECT cav.version_number
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
                await conn.commit()
                return (
                    row["version_number"]
                    if row is not None and row["version_number"] is not None
                    else None
                )
            except (errors.OperationalError, errors.IntegrityConstraintViolation) as ex:
                raise
