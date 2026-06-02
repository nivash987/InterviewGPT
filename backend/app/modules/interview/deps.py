from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.di.container import get_session_dep
from app.modules.ats.repository import AtsRepository, SqlAlchemyAtsRepository
from app.modules.interview.repository import InterviewRepository, SqlAlchemyInterviewRepository
from app.modules.interview.service import InterviewService, InterviewServiceImpl
from app.modules.resume.repository import ResumeRepository, SqlAlchemyResumeRepository


def get_interview_repository(session: AsyncSession = Depends(get_session_dep)) -> InterviewRepository:
    return SqlAlchemyInterviewRepository(session)


def get_interview_resume_repository(session: AsyncSession = Depends(get_session_dep)) -> ResumeRepository:
    return SqlAlchemyResumeRepository(session)


def get_interview_ats_repository(session: AsyncSession = Depends(get_session_dep)) -> AtsRepository:
    return SqlAlchemyAtsRepository(session)


def get_interview_service(
    interview_repository: InterviewRepository = Depends(get_interview_repository),
    resume_repository: ResumeRepository = Depends(get_interview_resume_repository),
    ats_repository: AtsRepository = Depends(get_interview_ats_repository),
) -> InterviewService:
    return InterviewServiceImpl(
        interview_repository=interview_repository,
        resume_repository=resume_repository,
        ats_repository=ats_repository,
    )


InterviewServiceDep = Depends(get_interview_service)
