from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.di.container import get_session_dep
from app.modules.career_coach.repository import CareerCoachRepository, SqlAlchemyCareerCoachRepository
from app.modules.career_coach.service import CareerCoachService, CareerCoachServiceImpl


def get_career_coach_repository(session: AsyncSession = Depends(get_session_dep)) -> CareerCoachRepository:
    return SqlAlchemyCareerCoachRepository(session)


def get_career_coach_service(
    repository: CareerCoachRepository = Depends(get_career_coach_repository),
) -> CareerCoachService:
    return CareerCoachServiceImpl(repository=repository)


CareerCoachServiceDep = Depends(get_career_coach_service)
