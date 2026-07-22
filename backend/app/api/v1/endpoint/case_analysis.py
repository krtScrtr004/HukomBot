from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Path

from backend.app.service.case_analysis_service import CaseAnalysisService
from backend.app.orchistrator.case_analysis_orchistrator import CaseAnalysisOrchistrator
from backend.app.schema.chatbot_schema import (
    CaseAnalysisPipelineCaseFactsPayload,
    GetCaseAnalysisResponse,
)
from backend.app.schema.response_schema import SuccessResponse

from backend.app.api.v1.dependency import (
    get_case_analysis_service,
    get_case_analysis_orchestrator,
)

case_analysis_api_router = APIRouter()


@case_analysis_api_router.post("/")
async def run_case_analysis_pipeline(
    payload: CaseAnalysisPipelineCaseFactsPayload,
    orchistrator: Annotated[
        CaseAnalysisOrchistrator, Depends(get_case_analysis_orchestrator)
    ],
):
    result = await orchistrator.run_pipeline(payload)
    return SuccessResponse(message=result.message, data=result.data)


@case_analysis_api_router.post("/{case_analysis_session_id}/version/{version_number}")
async def get_case_analysis_version(
    case_analysis_session_id: UUID,
    version_number: Annotated[int, Path(ge=1)],
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    result = await service.get_by_version(case_analysis_session_id, version_number)
    return SuccessResponse(
        message="Case analysis version fetched successfully",
        data=GetCaseAnalysisResponse(
            case_analysis_session_id=case_analysis_session_id, case_analysis=result
        ),
    )
