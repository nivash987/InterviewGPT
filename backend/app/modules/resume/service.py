from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from app.core.errors import BadRequestError, NotFoundError
from app.modules.resume.parser import extract_text, parse_resume_text
from app.modules.resume.repository import ResumeRepository, _version_to_public, resume_to_public
from app.modules.resume.schemas import (
    ResumeHistoryResponse,
    ResumeListResponse,
    ResumePublic,
    ResumeVersionPublic,
)
from app.modules.resume.storage import LocalResumeStorage

MIME_BY_EXTENSION = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


class ResumeService(ABC):
    @abstractmethod
    async def upload_resume(
        self,
        *,
        user_id: str,
        filename: str,
        content_type: str | None,
        content: bytes,
        title: str | None = None,
    ) -> ResumePublic: ...

    @abstractmethod
    async def replace_resume(
        self,
        *,
        user_id: str,
        resume_id: str,
        filename: str,
        content_type: str | None,
        content: bytes,
    ) -> ResumePublic: ...

    @abstractmethod
    async def list_resumes(self, *, user_id: str) -> ResumeListResponse: ...

    @abstractmethod
    async def get_resume(self, *, user_id: str, resume_id: str) -> ResumePublic: ...

    @abstractmethod
    async def get_history(self, *, user_id: str, resume_id: str) -> ResumeHistoryResponse: ...

    @abstractmethod
    async def delete_resume(self, *, user_id: str, resume_id: str) -> None: ...


class ResumeServiceImpl(ResumeService):
    def __init__(
        self,
        *,
        repository: ResumeRepository,
        storage: LocalResumeStorage,
    ) -> None:
        self._repository = repository
        self._storage = storage

    def _resolve_mime(self, extension: str, content_type: str | None) -> str:
        if content_type and content_type in MIME_BY_EXTENSION.values():
            return content_type
        return MIME_BY_EXTENSION[extension]

    async def _process_upload(
        self,
        *,
        user_id: str,
        resume_id: str,
        filename: str,
        content_type: str | None,
        content: bytes,
        version_number: int,
    ) -> ResumeVersionPublic:
        try:
            extension = self._storage.validate(
                filename=filename,
                content_type=content_type,
                size_bytes=len(content),
            )
        except ValueError as exc:
            raise BadRequestError(str(exc)) from exc

        mime_type = self._resolve_mime(extension, content_type)
        version_id = self._storage.new_version_id()
        file_path = self._storage.build_path(
            user_id=user_id,
            resume_id=resume_id,
            version_id=version_id,
            extension=extension,
        )

        try:
            raw_text = extract_text(content=content, mime_type=mime_type)
            parsed = parse_resume_text(raw_text)
            parsed_dict = parsed.model_dump()
        except Exception:
            raw_text = None
            parsed_dict = None

        self._storage.save(path=file_path, content=content)

        version = await self._repository.create_version(
            resume_id=resume_id,
            version_number=version_number,
            original_filename=filename,
            stored_filename=str(file_path),
            mime_type=mime_type,
            file_size_bytes=len(content),
            raw_text=raw_text,
            parsed_data=parsed_dict,
        )
        await self._repository.set_current_version(resume_id=resume_id, version_id=str(version.id))
        return _version_to_public(version)

    async def upload_resume(
        self,
        *,
        user_id: str,
        filename: str,
        content_type: str | None,
        content: bytes,
        title: str | None = None,
    ) -> ResumePublic:
        resume = await self._repository.create_resume(user_id=user_id, title=title or Path(filename).stem)
        resume_id = str(resume.id)

        await self._process_upload(
            user_id=user_id,
            resume_id=resume_id,
            filename=filename,
            content_type=content_type,
            content=content,
            version_number=1,
        )

        loaded = await self._repository.get_resume_for_user(resume_id=resume_id, user_id=user_id)
        if loaded is None:
            raise NotFoundError("Resume not found after upload")
        count = await self._repository.count_versions(resume_id=resume_id)
        return resume_to_public(loaded, version_count=count)

    async def replace_resume(
        self,
        *,
        user_id: str,
        resume_id: str,
        filename: str,
        content_type: str | None,
        content: bytes,
    ) -> ResumePublic:
        resume = await self._require_owned_resume(user_id=user_id, resume_id=resume_id)
        version_number = await self._repository.get_next_version_number(resume_id=resume_id)

        await self._process_upload(
            user_id=user_id,
            resume_id=resume_id,
            filename=filename,
            content_type=content_type,
            content=content,
            version_number=version_number,
        )

        loaded = await self._repository.get_resume_for_user(resume_id=resume_id, user_id=user_id)
        if loaded is None:
            raise NotFoundError("Resume not found after replace")
        count = await self._repository.count_versions(resume_id=resume_id)
        return resume_to_public(loaded, version_count=count)

    async def list_resumes(self, *, user_id: str) -> ResumeListResponse:
        resumes = await self._repository.list_resumes_for_user(user_id=user_id)
        items: list[ResumePublic] = []
        for resume in resumes:
            count = await self._repository.count_versions(resume_id=str(resume.id))
            items.append(resume_to_public(resume, version_count=count))
        return ResumeListResponse(items=items, total=len(items))

    async def get_resume(self, *, user_id: str, resume_id: str) -> ResumePublic:
        resume = await self._require_owned_resume(user_id=user_id, resume_id=resume_id)
        count = await self._repository.count_versions(resume_id=resume_id)
        return resume_to_public(resume, version_count=count)

    async def get_history(self, *, user_id: str, resume_id: str) -> ResumeHistoryResponse:
        await self._require_owned_resume(user_id=user_id, resume_id=resume_id)
        versions = await self._repository.list_versions(resume_id=resume_id)
        return ResumeHistoryResponse(
            resume_id=resume_id,
            versions=[_version_to_public(v) for v in versions],
        )

    async def delete_resume(self, *, user_id: str, resume_id: str) -> None:
        resume = await self._require_owned_resume(user_id=user_id, resume_id=resume_id)
        versions = await self._repository.list_versions(resume_id=resume_id)
        for version in versions:
            self._storage.delete_file(Path(version.stored_filename))
        self._storage.delete_resume_directory(user_id=user_id, resume_id=resume_id)
        await self._repository.delete_resume(resume=resume)

    async def _require_owned_resume(self, *, user_id: str, resume_id: str):
        resume = await self._repository.get_resume_for_user(resume_id=resume_id, user_id=user_id)
        if resume is None:
            raise NotFoundError("Resume not found")
        return resume
