from typing import List
from psycopg import errors

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseFact
from backend.app.schema.case_analysis_schema import CaseFactCreate


class CaseFactRepository:
    def __init__(self, db: Database):
        self.__database = db

    async def create(self, case_fact: CaseFactCreate) -> CaseFact:
        async with self.__database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO case_facts (id, case_analysis_session_id, created_at)
                        VALUES (%(id), %(case_analysis_session_id)s, %(created_at)s)
                        """,
                        (case_fact.model_dump()),
                    )

                await conn.commit()

                return CaseFact(
                    id=case_fact.id,
                    case_analysis_session_id=case_fact.case_analysis_session_id,
                    created_at=case_fact.created_at,
                )
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def create_many(self, case_facts: List[CaseFactCreate]) -> List[CaseFact]:
        async with self.__database.connection() as conn:
            try:
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

                await conn.commit()
                return updated
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise
