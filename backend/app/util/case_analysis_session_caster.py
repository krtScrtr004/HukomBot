from backend.app.model.case_analysis_model import CaseAnalysisSession
from backend.app.schema.case_analysis_schema import CaseAnalysisSessionCreate


class CaseAnalysisSessionCaster:
    
    @staticmethod
    def create_to_base(
        case_analysis_session: CaseAnalysisSessionCreate,
    ) -> CaseAnalysisSession:
        return CaseAnalysisSession(
            id=case_analysis_session.id,
            user_id=case_analysis_session.user_id,
            created_at=case_analysis_session.created_at,
            updated_at=case_analysis_session.updated_at,
        )
