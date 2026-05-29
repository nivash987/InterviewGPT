from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.di.container import get_session_dep
from app.modules.ats.repository import AtsRepository, SqlAlchemyAtsRepository
from app.modules.ats.service import AtsService, AtsServiceImpl
from app.modules.resume.repository import ResumeRepository, SqlAlchemyResumeRepository


def get_ats_repository(session: AsyncSession = Depends(get_session_dep)) -> AtsRepository:
    return SqlAlchemyAtsRepository(session)


def get_ats_resume_repository(session: AsyncSession = Depends(get_session_dep)) -> ResumeRepository:
    return SqlAlchemyResumeRepository(session)


def get_ats_service(
    ats_repository: AtsRepository = Depends(get_ats_repository),
    resume_repository: ResumeRepository = Depends(get_ats_resume_repository),
) -> AtsService:
    return AtsServiceImpl(ats_repository=ats_repository, resume_repository=resume_repository)


AtsServiceDep = Depends(get_ats_service)
