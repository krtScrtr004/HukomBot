from typing import Annotated
from fastapi import APIRouter, Depends

from backend.app.service.chatbot_service import ChatbotService
from backend.app.schema.chatbot_schema import CaseAnalysisCaseFactsPayload

from backend.app.api.v1.dependency import get_chatbot_service

chatbot_api_router = APIRouter()


@chatbot_api_router.post("/case-analysis/")
async def run_case_analysis_pipeline(
    payload: CaseAnalysisCaseFactsPayload,
    service: Annotated[ChatbotService, Depends(get_chatbot_service)],
):
    return await service.run_case_analysis_pipeline(payload)
