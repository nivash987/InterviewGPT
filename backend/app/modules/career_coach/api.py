from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import PrincipalDep
from app.core.responses import ApiResponse, EmptyData
from app.core.security import Principal
from app.modules.career_coach.deps import CareerCoachServiceDep
from app.modules.career_coach.schemas import (
    CareerCoachDashboard,
    CareerRoadmapPublic,
    LearningRecommendation,
    ProgressEntryPublic,
    ProgressUpdateRequest,
    ReadinessScorePublic,
    SkillGapAnalysis,
    UserGoalCreate,
    UserGoalPublic,
    UserSkillPublic,
    UserSkillUpsert,
    WeaknessItem,
)
from app.modules.career_coach.service import CareerCoachService

router = APIRouter()


@router.get("/status", response_model=ApiResponse[EmptyData])
async def status() -> ApiResponse[EmptyData]:
    return ApiResponse(data=EmptyData())


@router.get("/dashboard", response_model=ApiResponse[CareerCoachDashboard])
async def dashboard(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[CareerCoachDashboard]:
    result = await svc.get_dashboard(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.post("/goals", response_model=ApiResponse[UserGoalPublic], status_code=201)
async def set_goal(
    payload: UserGoalCreate,
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[UserGoalPublic]:
    result = await svc.set_goal(user_id=principal.user_id, payload=payload)
    return ApiResponse(data=result)


@router.get("/goals", response_model=ApiResponse[UserGoalPublic | None])
async def get_goal(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[UserGoalPublic | None]:
    result = await svc.get_goal(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/skills", response_model=ApiResponse[list[UserSkillPublic]])
async def list_skills(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[list[UserSkillPublic]]:
    result = await svc.list_skills(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.put("/skills", response_model=ApiResponse[UserSkillPublic])
async def upsert_skill(
    payload: UserSkillUpsert,
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[UserSkillPublic]:
    result = await svc.upsert_skill(user_id=principal.user_id, payload=payload)
    return ApiResponse(data=result)


@router.post("/skills/sync-ats", response_model=ApiResponse[list[UserSkillPublic]])
async def sync_skills_from_ats(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[list[UserSkillPublic]]:
    result = await svc.sync_skills_from_ats(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.post("/roadmap/generate", response_model=ApiResponse[CareerRoadmapPublic], status_code=201)
async def generate_roadmap(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[CareerRoadmapPublic]:
    result = await svc.generate_roadmap(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/roadmap", response_model=ApiResponse[CareerRoadmapPublic])
async def get_roadmap(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[CareerRoadmapPublic]:
    result = await svc.get_roadmap(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/skill-gaps", response_model=ApiResponse[SkillGapAnalysis])
async def skill_gaps(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[SkillGapAnalysis]:
    result = await svc.get_skill_gaps(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.post("/readiness/compute", response_model=ApiResponse[ReadinessScorePublic])
async def compute_readiness(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[ReadinessScorePublic]:
    result = await svc.compute_readiness(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/readiness", response_model=ApiResponse[ReadinessScorePublic])
async def get_readiness(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[ReadinessScorePublic]:
    result = await svc.get_readiness(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.patch("/progress/{milestone_id}", response_model=ApiResponse[ProgressEntryPublic])
async def update_progress(
    milestone_id: str,
    payload: ProgressUpdateRequest,
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[ProgressEntryPublic]:
    result = await svc.update_progress(
        user_id=principal.user_id,
        milestone_id=milestone_id,
        payload=payload,
    )
    return ApiResponse(data=result)


@router.get("/recommendations", response_model=ApiResponse[list[LearningRecommendation]])
async def recommendations(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[list[LearningRecommendation]]:
    result = await svc.get_recommendations(user_id=principal.user_id)
    return ApiResponse(data=result)


@router.get("/weaknesses", response_model=ApiResponse[list[WeaknessItem]])
async def weaknesses(
    principal: Principal = PrincipalDep,
    svc: CareerCoachService = CareerCoachServiceDep,
) -> ApiResponse[list[WeaknessItem]]:
    result = await svc.get_weaknesses(user_id=principal.user_id)
    return ApiResponse(data=result)
