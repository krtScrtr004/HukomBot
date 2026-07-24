from backend.app.model.case_analysis_model import CaseFactVersion
from backend.app.schema.case_analysis_schema import CaseFactVersionCreate


class CaseFactVersionCaster:

    @staticmethod
    def create_to_base(case_fact_version: CaseFactVersionCreate) -> CaseFactVersion:
        return CaseFactVersion(
            id=case_fact_version.id,
            case_fact_id=case_fact_version.case_fact_id,
            version_number=case_fact_version.version_number,
            fact=case_fact_version.fact,
            is_deleted=case_fact_version.is_deleted,
            created_at=case_fact_version.created_at,
        )
