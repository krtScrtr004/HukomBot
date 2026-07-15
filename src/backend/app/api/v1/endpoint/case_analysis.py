from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Path

from backend.app.service.case_analysis_service import CaseAnalysisService
from backend.app.schema.chatbot_schema import CaseAnalysisPipelineCaseFactsPayload

from backend.app.api.v1.dependency import get_case_analysis_service

case_analysis_api_router = APIRouter()


@case_analysis_api_router.post("/")
async def run_case_analysis_pipeline(
    payload: CaseAnalysisPipelineCaseFactsPayload,
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    return await service.run_pipeline(payload)


@case_analysis_api_router.post(
    "/{case_analysis_session_id}/version/{version_number}"
)
async def get_case_analysis_version(
    case_analysis_session_id: UUID,
    version_number: Annotated[int, Path(ge=1)],
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    return await service.get_by_version(
        case_analysis_session_id, version_number
    )
