from uuid import UUID
from psycopg import errors
from psycopg import AsyncConnection

from backend.hukom_bot.database.database import Database
from backend.hukom_bot.model.case_analysis_model import CaseFact
from backend.hukom_bot.schema.case_analysis_schema import CaseFactCreate


class CaseFactRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create_many(
        self,
        case_facts: list[CaseFactCreate],
        connection: AsyncConnection = None,
    ) -> list[CaseFact]:
        if not case_facts:
            return []

        if connection is not None:
            return await self._create_many_implement(connection, case_facts)
        
        async with self._database.connection() as conn:
            try:
                result = await self._create_many_implement(conn, case_facts)
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _create_many_implement(
        self,
        conn: AsyncConnection,
        case_facts: list[CaseFactCreate],
    ) -> list[CaseFact]:
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
    
    async def delete_many(self, ids: list[UUID], connection: AsyncConnection = None):
        if not ids:
            return

        if connection is not None:
            await self._delete_many_implement(connection, ids)
        else:
            async with self._database.connection() as conn:
                try:
                    await self._delete_many_implement(conn, ids)
                    await conn.commit()
                except errors.OperationalError as ex:
                    await conn.rollback()
                    raise

    async def _delete_many_implement(self, conn: AsyncConnection, ids: list[UUID]):
        async with conn.cursor() as cur:
            placeholders = ", ".join(["%s"] * len(ids))
            await cur.execute(
                f"""
                DELETE FROM case_facts
                WHERE id IN ({placeholders})
                """,
                ids,
            )