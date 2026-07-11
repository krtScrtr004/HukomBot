from psycopg import errors

from backend.app.database.database import Database
from backend.app.model.case_analysis_model import CaseAnalysisVersion
from backend.app.schema.case_analysis_schema import CaseAnalysisVersionCreate


class CaseAnalysisVersionRepository:
    def __init__(self, db: Database):
        self.__database = db
        
    async def create(self, case_analysis_version: CaseAnalysisVersionCreate) -> CaseAnalysisVersion:
        async with self.__database.connection() as conn:
            try:
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
                    
                await conn.commit()
                
                return CaseAnalysisVersion(
                    id=case_analysis_version.id,
                    case_analysis_session_id=case_analysis_version.case_analysis_session_id,
                    version_number=case_analysis_version.version_number,
                    answer=case_analysis_version.answer,
                    created_at=case_analysis_version.created_at
                )
            except (errors.IntegrityError, errors.OperationalError) as ex:
                await conn.rollback()
                raise
