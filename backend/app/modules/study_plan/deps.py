from __future__ import annotations

from fastapi import Depends

from app.modules.study_plan.service import StudyPlanService


def get_study_plan_service() -> StudyPlanService:
    raise NotImplementedError("Study plan service wiring not implemented yet")


StudyPlanServiceDep = Depends(get_study_plan_service)

