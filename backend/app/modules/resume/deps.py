from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.di.container import get_session_dep
from app.modules.resume.repository import ResumeRepository, SqlAlchemyResumeRepository
from app.modules.resume.service import ResumeService, ResumeServiceImpl
from app.modules.resume.storage import LocalResumeStorage


def get_resume_repository(session: AsyncSession = Depends(get_session_dep)) -> ResumeRepository:
    return SqlAlchemyResumeRepository(session)


def get_resume_storage(settings: Settings = Depends(get_settings)) -> LocalResumeStorage:
    return LocalResumeStorage(settings)


def get_resume_service(
    repository: ResumeRepository = Depends(get_resume_repository),
    storage: LocalResumeStorage = Depends(get_resume_storage),
) -> ResumeService:
    return ResumeServiceImpl(repository=repository, storage=storage)


ResumeServiceDep = Depends(get_resume_service)
