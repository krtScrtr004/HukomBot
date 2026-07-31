from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Path
from backend.app.model.user_model import User
from backend.app.service.case_analysis_service import CaseAnalysisService
from backend.app.orchistrator.case_analysis_orchistrator import CaseAnalysisOrchistrator
from backend.app.schema.chatbot_schema import (
    CaseAnalysisPipelineCaseFactsPayload,
    GetCaseAnalysisResponse,
)
from backend.app.schema.response_schema import SuccessResponse
from backend.app.api.v1.dependency import (
    verify_user,
    get_case_analysis_service,
    get_case_analysis_orchestrator,
)

case_analysis_api_router = APIRouter()


@case_analysis_api_router.post("/")
async def run_case_analysis_pipeline(
    payload: CaseAnalysisPipelineCaseFactsPayload,
    user: Annotated[User, Depends(verify_user)],
    orchistrator: Annotated[
        CaseAnalysisOrchistrator, Depends(get_case_analysis_orchestrator)
    ],
):
    result = await orchistrator.run_pipeline(user_id=user.id, payload=payload)
    return SuccessResponse(message=result.message, data=result.data)


@case_analysis_api_router.get("/{case_analysis_session_id}/version/{version_number}")
async def get_case_analysis_version(
    case_analysis_session_id: UUID,
    version_number: Annotated[int, Path(ge=1)],
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    result = await service.get_by_version(case_analysis_session_id, version_number)
    return SuccessResponse(
        message="Case analysis version fetched successfully",
        data=GetCaseAnalysisResponse(
            case_analysis_session_id=case_analysis_session_id, case_analysis=result
        ),
    )


@case_analysis_api_router.delete("/{case_analysis_session_id}")
async def delete_case_analysis(
    case_analysis_session_id: UUID,
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    await service.delete_session(id=case_analysis_session_id)
    return SuccessResponse(
        message="Case analysis session successfully deleted",
        data={"case_analysis_session_id": case_analysis_session_id},
    )
