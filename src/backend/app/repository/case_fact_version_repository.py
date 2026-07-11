from typing import List
from psycopg import errors
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseFactVersion
from backend.app.schema.case_analysis_schema import CaseFactVersionCreate


class CaseFactVersionRepository:
    def __init__(self, db: Database):
        self.__database = db

    async def create(
        self,
        case_fact_version: CaseFactVersionCreate,
        connection: AsyncConnection = None,
    ) -> CaseFactVersion:
        if connection is not None:
            return await self.__create_implement(connection, case_fact_version)
        async with self.__database.connection() as conn:
            return await self.__create_implement(conn, case_fact_version)

    async def __create_implement(
        self,
        conn: AsyncConnection,
        case_fact_version: CaseFactVersionCreate,
    ) -> CaseFactVersion:
        try:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO case_fact_versions (
                        id,
                        case_fact_id, 
                        version_number,
                        fact,
                        is_deleted,
                        created_at
                    ) VALUES (
                        %(id)s,
                        %(case_fact_id)s, 
                        %(version_number)s,
                        %(fact)s,
                        %(is_deleted)s,
                        %(created_at)s
                    )
                    """,
                    (case_fact_version.model_dump()),
                )

            await conn.commit()
            return CaseFactVersion(
                id=case_fact_version.id,
                case_fact_id=case_fact_version.case_fact_id,
                version_number=case_fact_version.version_number,
                fact=case_fact_version.fact,
                is_deleted=case_fact_version.is_deleted,
                created_at=case_fact_version.created_at,
            )
        except (errors.IntegrityError, errors.OperationalError) as ex:
            await conn.rollback()
            raise

    async def create_many(
        self,
        case_fact_versions: List[CaseFactVersionCreate],
        connection: AsyncConnection = None,
    ) -> List[CaseFactVersion]:
        if not case_fact_versions:
            return []

        if connection is not None:
            return await self.__create_many_implement(connection, case_fact_versions)
        async with self.__database.connection() as conn:
            return await self.__create_many_implement(conn, case_fact_versions)

    async def __create_many_implement(
        self,
        conn: AsyncConnection,
        case_fact_versions: List[CaseFactVersionCreate],
    ) -> List[CaseFactVersion]:
        try:
            async with conn.cursor() as cur:
                await cur.executemany(
                    """
                    INSERT INTO case_fact_versions (
                        id,
                        case_fact_id, 
                        version_number,
                        fact,
                        is_deleted,
                        created_at
                    ) VALUES (
                        %(id)s,
                        %(case_fact_id)s, 
                        %(version_number)s,
                        %(fact)s,
                        %(is_deleted)s,
                        %(created_at)s
                    )
                    """,
                    [fact_version.model_dump() for fact_version in case_fact_versions],
                )

                # Retrieve the generated IDs
                updated = []
                for i, _ in enumerate(case_fact_versions):
                    updated.append(
                        CaseFactVersion(
                            id=case_fact_versions[i].id,
                            case_fact_id=case_fact_versions[i].case_fact_id,
                            version_number=case_fact_versions[i].version_number,
                            fact=case_fact_versions[i].fact,
                            is_deleted=case_fact_versions[i].is_deleted,
                            created_at=case_fact_versions[i].created_at,
                        )
                    )

            await conn.commit()
            return updated
        except (errors.IntegrityError, errors.OperationalError) as ex:
            await conn.rollback()
            raise
