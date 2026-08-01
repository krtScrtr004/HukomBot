from uuid import UUID
from typing import Annotated
from fastapi import APIRouter, Depends, Path, Header, Query, Body
from backend.app.model.user_model import User
from backend.app.service.case_analysis_service import CaseAnalysisService
from backend.app.orchistrator.case_analysis_orchistrator import CaseAnalysisOrchistrator
from backend.app.schema.case_analysis_schema import (
    CaseAnalysisGetBySessionId,
    CaseAnalysisGetByUserId,
    CaseAnalysisGetByVersionNumber,
)
from backend.app.schema.chatbot_schema import (
    CaseAnalysiPipelineCaseFactsHeader,
    CaseAnalysisPipelineCaseFactsPayload,
    GetCaseAnalysisResponse,
)
from backend.app.schema.mixin import PaginatableMixin
from backend.app.schema.response_schema import SuccessResponse
from backend.app.api.v1.dependency import (
    verify_user,
    get_case_analysis_service,
    get_case_analysis_orchestrator,
)


from backend.app.util.case_analysis_version_caster import CaseAnalysisVersionCaster

case_analysis_api_router = APIRouter()


@case_analysis_api_router.post("/")
async def run_case_analysis_pipeline(
    header: Annotated[CaseAnalysiPipelineCaseFactsHeader, Header()],
    payload: Annotated[CaseAnalysisPipelineCaseFactsPayload, Body()],
    user: Annotated[User, Depends(verify_user)],
    orchistrator: Annotated[
        CaseAnalysisOrchistrator, Depends(get_case_analysis_orchestrator)
    ],
):
    answer_format = header.answer_format
    result = await orchistrator.run_pipeline(
        user_id=user.id, payload=payload, answer_format=answer_format
    )
    return SuccessResponse(message=result.message, data=result.data)


@case_analysis_api_router.get("/")
async def get_latest_session_analyses(
    params: Annotated[PaginatableMixin, Query()],
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    result = await service.get_latest_session_analyses_preview(
        CaseAnalysisGetByUserId(
            user_id=user.id, limit=params.limit, offset=params.offset
        )
    )
    return SuccessResponse(message="User analyses fetched successfully", data=result)


@case_analysis_api_router.get("/{case_analysis_session_id}/versions")
async def get_case_analysis_versions(
    case_analysis_session_id: UUID,
    params: Annotated[PaginatableMixin, Query()],
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    results = await service.get_analysis_versions_by_session_id(
        CaseAnalysisGetBySessionId(
            case_analysis_session_id=case_analysis_session_id,
            user_id=user.id,
            limit=params.limit,
            offset=params.offset,
        )
    )

    return SuccessResponse(
        message="Case analysis versions fetched successfully",
        data=[
            CaseAnalysisVersionCaster.base_to_preview_response(res) for res in results
        ],
    )


@case_analysis_api_router.get("/{case_analysis_session_id}/versions/{version_number}")
async def get_case_analysis_version(
    case_analysis_session_id: UUID,
    version_number: Annotated[int, Path(ge=1)],
    user: Annotated[User, Depends(verify_user)],
    service: Annotated[CaseAnalysisService, Depends(get_case_analysis_service)],
):
    result = await service.get_by_version(
        CaseAnalysisGetByVersionNumber(
            case_analysis_session_id=case_analysis_session_id,
            user_id=user.id,
            version_number=version_number,
        )
    )
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
