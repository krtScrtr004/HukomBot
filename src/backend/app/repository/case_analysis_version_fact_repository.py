from typing import List
from uuid import UUID
from psycopg import errors
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisVersionFact
from backend.app.schema.case_analysis_schema import CaseAnalysisVersionFactCreate


class CaseAnalysisVersionFactRepository:
    def __init__(self, db: Database):
        self.__database = db

    async def create(
        self,
        case_analysis_version_fact: CaseAnalysisVersionFactCreate,
        connection: AsyncConnection = None,
    ) -> CaseAnalysisVersionFact:
        if connection is not None:
            return await self.__create_implement(connection, case_analysis_version_fact)

        async with self.__database.connection() as conn:
            try:
                result = await self.__create_implement(conn, case_analysis_version_fact)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def __create_implement(
        self,
        conn: AsyncConnection,
        case_analysis_version_fact: CaseAnalysisVersionFactCreate,
    ):
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO case_analysis_version_facts (case_analysis_version_id, case_fact_version_id) 
                VALUES (%(case_analysis_version_id)s, %(case_fact_version_id)s)
                """,
                (case_analysis_version_fact.model_dump()),
            )

        return CaseAnalysisVersionFact(
            case_analysis_version_id=case_analysis_version_fact.case_analysis_version_id,
            case_fact_version_id=case_analysis_version_fact.case_fact_version_id,
        )

    async def create_many(
        self,
        case_analysis_version_facts: List[CaseAnalysisVersionFactCreate],
        connection: AsyncConnection = None,
    ) -> List[CaseAnalysisVersionFact]:
        if not case_analysis_version_facts:
            return []

        if connection is not None:
            return await self.__create_many_implement(
                connection, case_analysis_version_facts
            )

        async with self.__database.connection() as conn:
            try:
                result = await self.__create_many_implement(
                    conn, case_analysis_version_facts
                )
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def __create_many_implement(
        self,
        conn: AsyncConnection,
        case_analysis_version_facts: List[CaseAnalysisVersionFactCreate],
    ):
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO case_analysis_version_facts (case_analysis_version_id, case_fact_version_id) 
                VALUES (%(case_analysis_version_id)s, %(case_fact_version_id)s)
                """,
                [
                    analysis_version_fact.model_dump()
                    for analysis_version_fact in case_analysis_version_facts
                ],
            )

        # Retrieve the generated IDs
        updated = []
        for i, _ in enumerate(case_analysis_version_facts):
            updated.append(
                CaseAnalysisVersionFact(
                    case_analysis_version_id=case_analysis_version_facts[
                        i
                    ].case_analysis_version_id,
                    case_fact_version_id=case_analysis_version_facts[
                        i
                    ].case_fact_version_id,
                )
            )

        return updated

    async def delete_many_by_case_fact_version_id(
        self, case_fact_version_ids: List[UUID], connection: AsyncConnection = None
    ):
        if not case_fact_version_ids:
            return

        if connection is not None:
            await self.__delete_many_by_case_fact_version_id_implement(
                connection, case_fact_version_ids
            )
        else:
            async with self.__database.connection() as conn:
                try:
                    await self.__delete_many_by_case_fact_version_id_implement(
                        conn, case_fact_version_ids
                    )
                    await conn.commit()
                except errors.OperationalError as ex:
                    await conn.rollback()
                    raise

    async def __delete_many_by_case_fact_version_id_implement(
        self, conn: AsyncConnection, case_fact_version_ids: List[UUID]
    ):
        async with conn.cursor() as cur:
            placeholders = ", ".join(["%s"] * len(case_fact_version_ids))
            await cur.execute(
                f"""
                DELETE FROM case_analysis_version_facts
                WHERE case_fact_version_id IN ({placeholders})
                """,
                case_fact_version_ids,
            )
