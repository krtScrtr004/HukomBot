from typing import List
from psycopg import errors

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisVersionFact
from backend.app.schema.case_analysis_schema import CaseAnalysisVersionFactCreate


class CaseAnalysisVersionFactRepository:
    def __init__(self, db: Database):
        self._database = db

    async def create(
        self, case_analysis_version_fact: CaseAnalysisVersionFactCreate
    ) -> CaseAnalysisVersionFact:
        async with self._database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO case_analysis_version_facts (case_analysis_version_id, case_fact_version_id) 
                        VALUES (%(case_analysis_version_id)s, %(case_fact_version_id)s)
                        """,
                        (case_analysis_version_fact.model_dump()),
                    )
                await conn.commit()

                return CaseAnalysisVersionFact(
                    case_analysis_version_id=case_analysis_version_fact.case_analysis_version_id,
                    case_fact_version_id=case_analysis_version_fact.case_fact_version_id,
                )
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def create_many(
        self, case_analysis_version_facts: List[CaseAnalysisVersionFactCreate]
    ) -> List[CaseAnalysisVersionFact]:
        if not case_analysis_version_facts:
            return []

        async with self._database.connection() as conn:
            try:
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
                            case_analysis_version_id=case_analysis_version_facts[i].case_analysis_version_id,
                            case_fact_version_id=case_analysis_version_facts[i].case_fact_version_id,
                        )
                    )
                
                await conn.commit()
                return updated
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise
