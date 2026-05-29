from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.resume import Resume, ResumeVersion
from app.modules.resume.schemas import ParsedResumeData, ResumePublic, ResumeVersionPublic


class ResumeRepository(ABC):
    @abstractmethod
    async def create_resume(
        self,
        *,
        user_id: str,
        title: str | None,
    ) -> Resume: ...

    @abstractmethod
    async def create_version(
        self,
        *,
        resume_id: str,
        version_number: int,
        original_filename: str,
        stored_filename: str,
        mime_type: str,
        file_size_bytes: int,
        raw_text: str | None,
        parsed_data: dict | None,
    ) -> ResumeVersion: ...

    @abstractmethod
    async def set_current_version(self, *, resume_id: str, version_id: str) -> None: ...

    @abstractmethod
    async def get_resume_for_user(self, *, resume_id: str, user_id: str) -> Resume | None: ...

    @abstractmethod
    async def list_resumes_for_user(self, *, user_id: str) -> list[Resume]: ...

    @abstractmethod
    async def list_versions(self, *, resume_id: str) -> list[ResumeVersion]: ...

    @abstractmethod
    async def get_next_version_number(self, *, resume_id: str) -> int: ...

    @abstractmethod
    async def delete_resume(self, *, resume: Resume) -> None: ...

    @abstractmethod
    async def count_versions(self, *, resume_id: str) -> int: ...


def _version_to_public(version: ResumeVersion) -> ResumeVersionPublic:
    parsed: ParsedResumeData | None = None
    if version.parsed_data:
        parsed = ParsedResumeData.model_validate(version.parsed_data)
    return ResumeVersionPublic(
        id=str(version.id),
        resume_id=str(version.resume_id),
        version_number=version.version_number,
        original_filename=version.original_filename,
        mime_type=version.mime_type,
        file_size_bytes=version.file_size_bytes,
        parsed_data=parsed,
        created_at=version.created_at,
    )


def resume_to_public(resume: Resume, *, version_count: int) -> ResumePublic:
    current: ResumeVersionPublic | None = None
    if resume.current_version is not None:
        current = _version_to_public(resume.current_version)
    return ResumePublic(
        id=str(resume.id),
        title=resume.title,
        current_version=current,
        version_count=version_count,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


class SqlAlchemyResumeRepository(ResumeRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_resume(self, *, user_id: str, title: str | None) -> Resume:
        resume = Resume(user_id=uuid.UUID(user_id), title=title)
        self._session.add(resume)
        await self._session.flush()
        return resume

    async def create_version(
        self,
        *,
        resume_id: str,
        version_number: int,
        original_filename: str,
        stored_filename: str,
        mime_type: str,
        file_size_bytes: int,
        raw_text: str | None,
        parsed_data: dict | None,
    ) -> ResumeVersion:
        version = ResumeVersion(
            resume_id=uuid.UUID(resume_id),
            version_number=version_number,
            original_filename=original_filename,
            stored_filename=stored_filename,
            mime_type=mime_type,
            file_size_bytes=file_size_bytes,
            raw_text=raw_text,
            parsed_data=parsed_data,
        )
        self._session.add(version)
        await self._session.flush()
        return version

    async def set_current_version(self, *, resume_id: str, version_id: str) -> None:
        stmt = select(Resume).where(Resume.id == uuid.UUID(resume_id))
        result = await self._session.execute(stmt)
        resume = result.scalar_one()
        resume.current_version_id = uuid.UUID(version_id)
        resume.updated_at = datetime.now(timezone.utc)
        await self._session.flush()

    async def get_resume_for_user(self, *, resume_id: str, user_id: str) -> Resume | None:
        stmt = (
            select(Resume)
            .where(Resume.id == uuid.UUID(resume_id), Resume.user_id == uuid.UUID(user_id))
            .options(selectinload(Resume.current_version))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_resumes_for_user(self, *, user_id: str) -> list[Resume]:
        stmt = (
            select(Resume)
            .where(Resume.user_id == uuid.UUID(user_id))
            .options(selectinload(Resume.current_version))
            .order_by(Resume.updated_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def list_versions(self, *, resume_id: str) -> list[ResumeVersion]:
        stmt = (
            select(ResumeVersion)
            .where(ResumeVersion.resume_id == uuid.UUID(resume_id))
            .order_by(ResumeVersion.version_number.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_next_version_number(self, *, resume_id: str) -> int:
        stmt = select(func.coalesce(func.max(ResumeVersion.version_number), 0)).where(
            ResumeVersion.resume_id == uuid.UUID(resume_id),
        )
        result = await self._session.execute(stmt)
        current_max = result.scalar_one()
        return int(current_max) + 1

    async def delete_resume(self, *, resume: Resume) -> None:
        await self._session.delete(resume)
        await self._session.flush()

    async def count_versions(self, *, resume_id: str) -> int:
        stmt = select(func.count()).select_from(ResumeVersion).where(
            ResumeVersion.resume_id == uuid.UUID(resume_id),
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
