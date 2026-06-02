from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.di.container import get_session_dep
from app.modules.jobs.repository import JobsRepository, SqlAlchemyJobsRepository
from app.modules.jobs.service import JobsService, JobsServiceImpl


def get_jobs_repository(session: AsyncSession = Depends(get_session_dep)) -> JobsRepository:
    return SqlAlchemyJobsRepository(session)


def get_jobs_service(
    repository: JobsRepository = Depends(get_jobs_repository),
) -> JobsService:
    return JobsServiceImpl(repository=repository)


JobsServiceDep = Depends(get_jobs_service)
