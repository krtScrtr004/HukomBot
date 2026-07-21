from backend.app.model.case_analysis_model import CaseFact, CaseAnalysisVersion
from backend.app.schema.case_analysis_schema import CaseAnalysisVersionResponse


class CaseAnalysisVersionCaster:
    @staticmethod
    def base_to_response(
        case_analysis_version: CaseAnalysisVersion, case_facts: list[CaseFact] = []
    ) -> CaseAnalysisVersionResponse:
        CaseAnalysisVersionResponse(
            id=case_analysis_version.id,
            version_number=case_analysis_version.version_number,
            answer=case_analysis_version.answer,
            created_at=case_analysis_version.created_at,
            case_facts=case_facts,
        ),
