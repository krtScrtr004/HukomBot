from uuid import UUID
from typing import List
from psycopg import errors
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseFact
from backend.app.schema.case_analysis_schema import CaseFactCreate


class CaseFactRepository:
    def __init__(self, db: Database):
        self.__database = db

    async def create_many(
        self,
        case_facts: List[CaseFactCreate],
        connection: AsyncConnection = None,
    ) -> List[CaseFact]:
        if not case_facts:
            return []

        if connection is not None:
            return await self.__create_many_implement(connection, case_facts)
        
        async with self.__database.connection() as conn:
            try:
                result = await self.__create_many_implement(conn, case_facts)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def __create_many_implement(
        self,
        conn: AsyncConnection,
        case_facts: List[CaseFactCreate],
    ) -> List[CaseFact]:
        async with conn.cursor() as cur:
            await cur.executemany(
                """
                INSERT INTO case_facts (id, case_analysis_session_id, created_at)
                VALUES (%(id)s, %(case_analysis_session_id)s, %(created_at)s)
                """,
                [fact.model_dump() for fact in case_facts],
            )

            # Retrieve the generated IDs
            updated = []
            for i, _ in enumerate(case_facts):
                updated.append(
                    CaseFact(
                        id=case_facts[i].id,
                        case_analysis_session_id=case_facts[
                            i
                        ].case_analysis_session_id,
                        created_at=case_facts[i].created_at,
                    )
                )

        return updated
    
    async def delete_many(self, ids: List[UUID], connection: AsyncConnection = None):
        if not ids:
            return

        if connection is not None:
            await self.__delete_many_implement(connection, ids)
        else:
            async with self.__database.connection() as conn:
                try:
                    await self.__delete_many_implement(conn, ids)
                    await conn.commit()
                except errors.OperationalError as ex:
                    await conn.rollback()
                    raise

    async def __delete_many_implement(self, conn: AsyncConnection, ids: List[UUID]):
        async with conn.cursor() as cur:
            placeholders = ", ".join(["%s"] * len(ids))
            await cur.execute(
                f"""
                DELETE FROM case_facts
                WHERE id IN ({placeholders})
                """,
                ids,
            )