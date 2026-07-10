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
                        INSERT INTO case_facts (case_analysis_session_id, created_at)
                        VALUES (%(case_analysis_session_id)s, %(created_at)s)
                        RETURNING id
                        """,
                        (case_fact.model_dump()),
                    )
                    
                    id = (await cur.fetchone())["id"]
                await conn.commit()
                
                return CaseFact(
                    id=id,
                    case_analysis_session_id=case_fact.case_analysis_session_id,
                    created_at=case_fact.created_at
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
                        INSERT INTO case_facts (case_analysis_session_id, created_at)
                        VALUES (%(case_analysis_session_id)s, %(created_at)s)
                        RETURNING id
                        """,
                        [fact.model_dump() for fact in case_facts],
                        returning=True
                    )
                                    
                    # Retrieve the generated IDs
                    updated = []
                    counter = 0
                    while True:
                        id = (await cur.fetchone())["id"]
                        if id:
                            updated.append(
                                CaseFact(
                                    id=id,
                                    case_analysis_session_id=case_facts[counter].case_analysis_session_id,
                                    created_at=case_facts[counter].created_at
                                )
                            )
                            counter += 1
                        if not cur.nextset():
                            break
                
                await conn.commit()
                return updated
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

