from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Path

from backend.app.service.chatbot_service import ChatbotService
from backend.app.schema.chatbot_schema import CaseAnalysisPipelineCaseFactsPayload

from backend.app.api.v1.dependency import get_chatbot_service

chatbot_api_router = APIRouter()


@chatbot_api_router.post("/case-analysis/")
async def run_case_analysis_pipeline(
    payload: CaseAnalysisPipelineCaseFactsPayload,
    service: Annotated[ChatbotService, Depends(get_chatbot_service)],
):
    return await service.run_case_analysis_pipeline(payload)


@chatbot_api_router.post(
    "/case-analysis/{case_analysis_session_id}/version/{version_number}"
)
async def get_case_analysis_version(
    case_analysis_session_id: UUID,
    version_number: Annotated[int, Path(ge=1)],
    service: Annotated[ChatbotService, Depends(get_chatbot_service)],
):
    return await service.get_case_analysis_version(
        case_analysis_session_id, version_number
    )
