from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import PrincipalDep
from app.core.responses import ApiResponse
from app.core.security import Principal
from app.modules.ats.deps import AtsServiceDep
from app.modules.ats.schemas import AtsAnalysisPublic, AtsAnalysisResult, AtsHistoryResponse
from app.modules.ats.service import AtsService

router = APIRouter()


@router.post("/analyze/{resume_id}", response_model=ApiResponse[AtsAnalysisResult])
async def analyze_resume(
    resume_id: str,
    principal: Principal = PrincipalDep,
    svc: AtsService = AtsServiceDep,
) -> ApiResponse[AtsAnalysisResult]:
    result = await svc.analyze_resume(user_id=principal.user_id, resume_id=resume_id)
    return ApiResponse(data=result)


@router.get("/history", response_model=ApiResponse[AtsHistoryResponse])
async def get_analysis_history(
    principal: Principal = PrincipalDep,
    svc: AtsService = AtsServiceDep,
) -> ApiResponse[AtsHistoryResponse]:
    result = await svc.get_history(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/{resume_id}", response_model=ApiResponse[AtsAnalysisPublic])
async def get_latest_analysis(
    resume_id: str,
    principal: Principal = PrincipalDep,
    svc: AtsService = AtsServiceDep,
) -> ApiResponse[AtsAnalysisPublic]:
    result = await svc.get_latest_analysis(user_id=principal.user_id, resume_id=resume_id)
    return ApiResponse(data=result)
