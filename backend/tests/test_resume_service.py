from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.core.config import Settings
from app.core.errors import BadRequestError, NotFoundError
from app.db.models.resume import Resume, ResumeVersion
from app.modules.resume.service import ResumeServiceImpl
from app.modules.resume.storage import LocalResumeStorage


def _minimal_pdf() -> bytes:
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 44>>stream\n"
        b"BT /F1 12 Tf 100 700 Td (Jane Doe) Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\n"
        b"startxref\n0\n%%EOF"
    )


@pytest.fixture
def mock_repository() -> AsyncMock:
    repo = AsyncMock()
    return repo


@pytest.fixture
def service(mock_repository: AsyncMock, resume_storage: LocalResumeStorage, resume_settings: Settings) -> ResumeServiceImpl:
    return ResumeServiceImpl(repository=mock_repository, storage=resume_storage)


@pytest.mark.asyncio
async def test_upload_resume_creates_first_version(
    service: ResumeServiceImpl,
    mock_repository: AsyncMock,
) -> None:
    user_id = str(uuid.uuid4())
    resume_id = uuid.uuid4()
    version_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    resume = Resume(id=resume_id, user_id=uuid.UUID(user_id), title="Test", created_at=now, updated_at=now)
    version = ResumeVersion(
        id=version_id,
        resume_id=resume_id,
        version_number=1,
        original_filename="resume.pdf",
        stored_filename="uploads/resume.pdf",
        mime_type="application/pdf",
        file_size_bytes=100,
        created_at=now,
    )
    resume.current_version = version

    mock_repository.create_resume.return_value = resume
    mock_repository.create_version.return_value = version
    mock_repository.get_resume_for_user.return_value = resume
    mock_repository.count_versions.return_value = 1

    result = await service.upload_resume(
        user_id=user_id,
        filename="resume.pdf",
        content_type="application/pdf",
        content=_minimal_pdf(),
        title="My Resume",
    )

    assert result.id == str(resume_id)
    assert result.version_count == 1
    mock_repository.create_resume.assert_awaited_once()
    mock_repository.create_version.assert_awaited_once()
    mock_repository.set_current_version.assert_awaited_once()


@pytest.mark.asyncio
async def test_upload_rejects_invalid_file_type(service: ResumeServiceImpl) -> None:
    with pytest.raises(BadRequestError, match="Unsupported file type"):
        await service.upload_resume(
            user_id=str(uuid.uuid4()),
            filename="notes.txt",
            content_type="text/plain",
            content=b"hello",
        )


@pytest.mark.asyncio
async def test_get_resume_not_found(service: ResumeServiceImpl, mock_repository: AsyncMock) -> None:
    mock_repository.get_resume_for_user.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_resume(user_id=str(uuid.uuid4()), resume_id=str(uuid.uuid4()))


@pytest.mark.asyncio
async def test_delete_resume_removes_files(
    service: ResumeServiceImpl,
    mock_repository: AsyncMock,
    resume_storage: LocalResumeStorage,
    resume_settings: Settings,
) -> None:
    user_id = str(uuid.uuid4())
    resume_id = uuid.uuid4()
    version_id = uuid.uuid4()
    now = datetime.now(timezone.utc)

    file_path = resume_storage.build_path(
        user_id=user_id,
        resume_id=str(resume_id),
        version_id=str(version_id),
        extension=".pdf",
    )
    file_path.write_bytes(b"test")

    resume = Resume(id=resume_id, user_id=uuid.UUID(user_id), created_at=now, updated_at=now)
    version = ResumeVersion(
        id=version_id,
        resume_id=resume_id,
        version_number=1,
        original_filename="resume.pdf",
        stored_filename=str(file_path),
        mime_type="application/pdf",
        file_size_bytes=4,
        created_at=now,
    )

    mock_repository.get_resume_for_user.return_value = resume
    mock_repository.list_versions.return_value = [version]

    await service.delete_resume(user_id=user_id, resume_id=str(resume_id))

    assert not file_path.exists()
    mock_repository.delete_resume.assert_awaited_once()
