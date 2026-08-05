from datetime import datetime
from backend.hukom_bot.model.case_analysis_model import CaseFact, CaseAnalysisVersion
from backend.hukom_bot.schema.case_analysis_schema import (
    CaseAnalysisVersionCreate, 
    CaseAnalysisVersionResponse,
    CaseAnalysisVersionPreviewResponse,
    CaseAnalysisSessionPreviewResponse
)


class CaseAnalysisVersionCaster:
    
    @staticmethod
    def base_to_response(
        case_analysis_version: CaseAnalysisVersion, case_facts: list[CaseFact] = []
    ) -> CaseAnalysisVersionResponse:
        return CaseAnalysisVersionResponse(
            id=case_analysis_version.id,
            title=case_analysis_version.title,
            version_number=case_analysis_version.version_number,
            answer=case_analysis_version.answer,
            answer_format=case_analysis_version.answer_format,
            created_at=case_analysis_version.created_at,
            case_facts=case_facts,
        )
        
    @staticmethod
    def base_to_session_preview_response(
        case_analysis_version: CaseAnalysisVersion,
        session_created_at: datetime,
        session_updated_at: datetime
    ) -> CaseAnalysisSessionPreviewResponse:
        return CaseAnalysisSessionPreviewResponse(
            case_analysis_session_id=case_analysis_version.case_analysis_session_id,
            latest_version_id=case_analysis_version.id,
            latest_version_number=case_analysis_version.version_number,
            latest_version_title=case_analysis_version.title,
            created_at=session_created_at,
            updated_at=session_updated_at
        )
    
    @staticmethod    
    def base_to_preview_response(
        case_analysis_version: CaseAnalysisVersion
    ) -> CaseAnalysisVersionPreviewResponse:
        return CaseAnalysisVersionPreviewResponse(
            id=case_analysis_version.id,
            title=case_analysis_version.title,
            version_number=case_analysis_version.version_number,
            created_at=case_analysis_version.created_at,
        )
        
    @staticmethod
    def create_to_base(
        case_analysis_version: CaseAnalysisVersionCreate
    ) -> CaseAnalysisVersion:
        return CaseAnalysisVersion(
            id=case_analysis_version.id,
            case_analysis_session_id=case_analysis_version.case_analysis_session_id,
            title=case_analysis_version.title,
            version_number=case_analysis_version.version_number,
            answer=case_analysis_version.answer,
            answer_format=case_analysis_version.answer_format,
            created_at=case_analysis_version.created_at
        ) 