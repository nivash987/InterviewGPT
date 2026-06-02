from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import PrincipalDep
from app.core.responses import ApiResponse
from app.core.security import Principal
from app.modules.interview.deps import InterviewServiceDep
from app.modules.interview.schemas import (
    FinishInterviewResponse,
    InterviewDetailResponse,
    InterviewHistoryResponse,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from app.modules.interview.service import InterviewService

router = APIRouter()


@router.post("/start", response_model=ApiResponse[StartInterviewResponse])
async def start_interview(
    payload: StartInterviewRequest,
    principal: Principal = PrincipalDep,
    svc: InterviewService = InterviewServiceDep,
) -> ApiResponse[StartInterviewResponse]:
    result = await svc.start_interview(user_id=principal.user_id, payload=payload)
    return ApiResponse(data=result)


@router.post("/{session_id}/answer", response_model=ApiResponse[SubmitAnswerResponse])
async def submit_answer(
    session_id: str,
    payload: SubmitAnswerRequest,
    principal: Principal = PrincipalDep,
    svc: InterviewService = InterviewServiceDep,
) -> ApiResponse[SubmitAnswerResponse]:
    result = await svc.submit_answer(
        user_id=principal.user_id,
        session_id=session_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.post("/{session_id}/finish", response_model=ApiResponse[FinishInterviewResponse])
async def finish_interview(
    session_id: str,
    principal: Principal = PrincipalDep,
    svc: InterviewService = InterviewServiceDep,
) -> ApiResponse[FinishInterviewResponse]:
    result = await svc.finish_interview(user_id=principal.user_id, session_id=session_id)
    return ApiResponse(data=result)


@router.get("/history", response_model=ApiResponse[InterviewHistoryResponse])
async def get_interview_history(
    principal: Principal = PrincipalDep,
    svc: InterviewService = InterviewServiceDep,
) -> ApiResponse[InterviewHistoryResponse]:
    result = await svc.get_history(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/{session_id}", response_model=ApiResponse[InterviewDetailResponse])
async def get_interview_session(
    session_id: str,
    principal: Principal = PrincipalDep,
    svc: InterviewService = InterviewServiceDep,
) -> ApiResponse[InterviewDetailResponse]:
    result = await svc.get_session(user_id=principal.user_id, session_id=session_id)
    return ApiResponse(data=result)
