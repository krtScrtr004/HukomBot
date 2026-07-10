from typing import List
from psycopg import errors

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseFactVersion
from backend.app.schema.case_analysis_schema import CaseFactVersionCreate


class CaseFactVersionRepository:
    def __init__(self, db: Database):
        self._database = db
        
    async def create(self, case_fact_version: CaseFactVersionCreate) -> CaseFactVersion:
        async with self._database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.execute(
                        """
                        INSERT INTO case_fact_versions (
                            case_fact_id, 
                            version_number,
                            fact,
                            is_deleted,
                            created_at
                        ) VALUES (
                            %(case_fact_id)s, 
                            %(version_number)s,
                            %(fact)s,
                            %(is_deleted)s,
                            %(created_at)s
                        )
                        RETURNING id
                        """,
                        (case_fact_version.model_dump()),
                    )
                    
                    row = (await cur.fetchone())["id"]
                await conn.commit()
                
                return CaseFactVersion(
                    id=row,
                    case_fact_id=case_fact_version.case_fact_id,
                    version_number=case_fact_version.version_number,
                    fact=case_fact_version.fact,
                    is_deleted=case_fact_version.is_deleted,
                    created_at=case_fact_version.created_at
                )
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise

    async def create_many(self, case_fact_versions: List[CaseFactVersionCreate]) -> List[CaseFactVersion]:
        async with self._database.connection() as conn:
            try:
                async with conn.cursor() as cur:
                    await cur.executemany(
                        """
                        INSERT INTO case_fact_versions (
                            case_fact_id, 
                            version_number,
                            fact,
                            is_deleted,
                            created_at
                        ) VALUES (
                            %(case_fact_id)s, 
                            %(version_number)s,
                            %(fact)s,
                            %(is_deleted)s,
                            %(created_at)s
                        )
                        RETURNING id
                        """,
                        [fact_version.model_dump() for fact_version in case_fact_versions],
                        returning=True
                    )
                    
                    # Retrieve the generated IDs
                    updated = []
                    counter = 0
                    while True:
                        id = (await cur.fetchone())["id"]
                        if id:
                            updated.append(
                                CaseFactVersion(
                                    id=id,
                                    case_fact_id=case_fact_versions[counter].case_fact_id,
                                    version_number=case_fact_versions[counter].version_number,
                                    fact=case_fact_versions[counter].fact,
                                    is_deleted=case_fact_versions[counter].is_deleted,
                                    created_at=case_fact_versions[counter].created_at
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