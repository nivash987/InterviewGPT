from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.errors import BadRequestError, NotFoundError
from app.modules.ats.analyzer import JobProfileData
from app.modules.ats.service import AtsServiceImpl
from app.modules.resume.schemas import ParsedResumeData

SAMPLE_PARSED = ParsedResumeData(
    name="Jane Doe",
    email="jane@example.com",
    phone="+1 555-1234",
    skills=["Python", "FastAPI", "React"],
    experience=[{"title": "Engineer", "description": "Built APIs"}],
    education=[{"title": "B.S. CS", "description": ""}],
    projects=[{"title": "App", "description": "Web app"}],
)

SAMPLE_RAW = "Jane Doe\njane@example.com\nSkills\nPython, FastAPI, React"


@pytest.fixture
def mock_resume() -> MagicMock:
    resume = MagicMock()
    version = MagicMock()
    version.raw_text = SAMPLE_RAW
    version.parsed_data = SAMPLE_PARSED.model_dump()
    resume.current_version = version
    return resume


@pytest.fixture
def service() -> tuple[AtsServiceImpl, AsyncMock, AsyncMock]:
    ats_repo = AsyncMock()
    resume_repo = AsyncMock()
    ats_repo.list_taxonomy_skills.return_value = ["Python", "FastAPI", "React", "Git", "SQL"]
    ats_repo.list_job_profiles.return_value = [
        JobProfileData(
            role_name="Backend Developer",
            required_skills=["Python", "SQL", "Git"],
            preferred_skills=["FastAPI"],
        ),
    ]
    svc = AtsServiceImpl(ats_repository=ats_repo, resume_repository=resume_repo)
    return svc, ats_repo, resume_repo


@pytest.mark.asyncio
async def test_analyze_resume_success(service: tuple, mock_resume: MagicMock) -> None:
    svc, ats_repo, resume_repo = service
    resume_repo.get_resume_for_user.return_value = mock_resume

    result = await svc.analyze_resume(user_id="user-1", resume_id="resume-1")

    assert 0 <= result.ats_score <= 100
    assert result.completeness_score > 0
    ats_repo.create_analysis.assert_called_once()


@pytest.mark.asyncio
async def test_analyze_resume_not_found(service: tuple) -> None:
    svc, _, resume_repo = service
    resume_repo.get_resume_for_user.return_value = None

    with pytest.raises(NotFoundError):
        await svc.analyze_resume(user_id="user-1", resume_id="missing")


@pytest.mark.asyncio
async def test_analyze_resume_no_text(service: tuple) -> None:
    svc, _, resume_repo = service
    resume = MagicMock()
    version = MagicMock()
    version.raw_text = ""
    resume.current_version = version
    resume_repo.get_resume_for_user.return_value = resume

    with pytest.raises(BadRequestError, match="no extractable text"):
        await svc.analyze_resume(user_id="user-1", resume_id="resume-1")


@pytest.mark.asyncio
async def test_get_latest_analysis_not_found(service: tuple) -> None:
    svc, ats_repo, resume_repo = service
    resume_repo.get_resume_for_user.return_value = MagicMock()
    ats_repo.get_latest_for_resume.return_value = None

    with pytest.raises(NotFoundError, match="No ATS analysis"):
        await svc.get_latest_analysis(user_id="user-1", resume_id="resume-1")


@pytest.mark.asyncio
async def test_get_history(service: tuple) -> None:
    svc, ats_repo, _ = service
    analysis = MagicMock()
    analysis.id = "a1"
    analysis.resume_id = "r1"
    analysis.ats_score = 85
    analysis.completeness_score = 90
    analysis.created_at = "2026-05-30T00:00:00Z"
    ats_repo.list_history_for_user.return_value = [(analysis, "My Resume")]

    result = await svc.get_history(user_id="user-1")

    assert result.total == 1
    assert result.items[0].resume_title == "My Resume"
