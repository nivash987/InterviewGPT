from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from app.core.errors import BadRequestError, NotFoundError
from app.db.models.job_application import JobApplication
from app.modules.jobs.schemas import (
    InterviewNoteCreate,
    JobApplicationCreate,
    StatusUpdateRequest,
)
from app.modules.jobs.service import JobsServiceImpl


@pytest.fixture
def mock_repository() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def service(mock_repository: AsyncMock) -> JobsServiceImpl:
    return JobsServiceImpl(repository=mock_repository)


@pytest.mark.asyncio
async def test_create_application_validates_status(service: JobsServiceImpl) -> None:
    with pytest.raises(BadRequestError):
        await service.create_application(
            user_id=str(uuid.uuid4()),
            payload=JobApplicationCreate(company_name="Acme", role_title="Engineer", status="invalid"),
        )


@pytest.mark.asyncio
async def test_create_application_returns_public(
    service: JobsServiceImpl,
    mock_repository: AsyncMock,
) -> None:
    user_id = str(uuid.uuid4())
    app_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    application = JobApplication(
        id=app_id,
        user_id=uuid.UUID(user_id),
        company_name="Acme",
        role_title="Engineer",
        status="applied",
        created_at=now,
        updated_at=now,
    )
    mock_repository.create_application.return_value = application

    result = await service.create_application(
        user_id=user_id,
        payload=JobApplicationCreate(company_name="Acme", role_title="Engineer"),
    )

    assert result.company_name == "Acme"
    assert result.status == "applied"
    mock_repository.create_application.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_application_not_found(service: JobsServiceImpl, mock_repository: AsyncMock) -> None:
    mock_repository.get_application_detail_for_user.return_value = None
    with pytest.raises(NotFoundError):
        await service.get_application(user_id=str(uuid.uuid4()), application_id=str(uuid.uuid4()))


@pytest.mark.asyncio
async def test_update_status_appends_history(
    service: JobsServiceImpl,
    mock_repository: AsyncMock,
) -> None:
    user_id = str(uuid.uuid4())
    app_id = uuid.uuid4()
    now = datetime.now(timezone.utc)
    application = JobApplication(
        id=app_id,
        user_id=uuid.UUID(user_id),
        company_name="Acme",
        role_title="Engineer",
        status="applied",
        created_at=now,
        updated_at=now,
    )
    mock_repository.get_application_for_user.return_value = application
    mock_repository.update_application.return_value = application

    result = await service.update_status(
        user_id=user_id,
        application_id=str(app_id),
        payload=StatusUpdateRequest(status="screening", note="Phone screen"),
    )

    assert result.status == "screening"
    mock_repository.append_status_history.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_analytics_computes_success_rate(
    service: JobsServiceImpl,
    mock_repository: AsyncMock,
) -> None:
    mock_repository.count_by_status_for_user.return_value = {
        "applied": 2,
        "offer": 1,
        "rejected": 1,
    }

    result = await service.get_analytics(user_id=str(uuid.uuid4()))

    assert result.total_applications == 4
    assert result.offers_received == 1
    assert result.rejections == 1
    assert result.success_rate == 50.0


@pytest.mark.asyncio
async def test_add_note_requires_application(
    service: JobsServiceImpl,
    mock_repository: AsyncMock,
) -> None:
    mock_repository.get_application_for_user.return_value = None
    with pytest.raises(NotFoundError):
        await service.add_note(
            user_id=str(uuid.uuid4()),
            application_id=str(uuid.uuid4()),
            payload=InterviewNoteCreate(title="Round 1", content="Went well"),
        )
