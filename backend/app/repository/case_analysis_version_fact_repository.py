from psycopg import errors
from psycopg import AsyncConnection

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisVersionFact
from backend.app.schema.case_analysis_schema import CaseAnalysisVersionFactCreate


class CaseAnalysisVersionFactRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create_many(
        self,
        case_analysis_version_facts: list[CaseAnalysisVersionFactCreate],
        connection: AsyncConnection = None,
    ) -> list[CaseAnalysisVersionFact]:
        if not case_analysis_version_facts:
            return []

        if connection is not None:
            return await self._create_many_implement(
                connection, case_analysis_version_facts
            )

        async with self._database.connection() as conn:
            try:
                result = await self._create_many_implement(
                    conn, case_analysis_version_facts
                )
                await conn.commit()
                return result
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def _create_many_implement(
        self,
        conn: AsyncConnection,
        case_analysis_version_facts: list[CaseAnalysisVersionFactCreate],
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