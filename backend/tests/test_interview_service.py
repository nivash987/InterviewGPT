from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.interview.schemas import StartInterviewRequest, SubmitAnswerRequest
from app.modules.interview.service import InterviewServiceImpl


def _mock_session(*, status: str = "in_progress") -> MagicMock:
    session = MagicMock()
    session.id = uuid.uuid4()
    session.status = status
    session.questions = []
    return session


@pytest.mark.asyncio
async def test_start_interview_creates_session() -> None:
    interview_repo = AsyncMock()
    resume_repo = AsyncMock()
    ats_repo = AsyncMock()

    resume = MagicMock()
    version = MagicMock()
    version.raw_text = "Skills: Python, FastAPI"
    version.parsed_data = {
        "name": "Test",
        "email": None,
        "phone": None,
        "skills": ["Python", "FastAPI"],
        "projects": [],
        "experience": [],
        "education": [],
    }
    resume.current_version = version
    resume_repo.get_resume_for_user.return_value = resume
    ats_repo.get_latest_for_resume.return_value = None

    created_session = MagicMock()
    created_session.id = uuid.uuid4()
    created_session.resume_id = uuid.uuid4()
    created_session.role = "Backend Developer"
    created_session.difficulty = "medium"
    created_session.question_count = 5
    created_session.total_score = None
    created_session.status = "in_progress"
    created_session.started_at = datetime.now(UTC)
    created_session.completed_at = None
    created_session.questions = []
    interview_repo.create_session.return_value = created_session

    svc = InterviewServiceImpl(
        interview_repository=interview_repo,
        resume_repository=resume_repo,
        ats_repository=ats_repo,
    )

    resume_id = str(uuid.uuid4())
    result = await svc.start_interview(
        user_id=str(uuid.uuid4()),
        payload=StartInterviewRequest(
            resume_id=resume_id,
            role="Backend Developer",
            difficulty="medium",
            question_count=5,
        ),
    )

    assert result.session.role == "Backend Developer"
    interview_repo.create_session.assert_awaited_once()


@pytest.mark.asyncio
async def test_submit_answer_evaluates_and_saves() -> None:
    interview_repo = AsyncMock()
    resume_repo = AsyncMock()
    ats_repo = AsyncMock()

    question_id = uuid.uuid4()
    session_id = uuid.uuid4()

    question = MagicMock()
    question.id = question_id
    question.expected_keywords = ["python", "api"]
    question.answer = None

    session = MagicMock()
    session.id = session_id
    session.status = "in_progress"
    session.questions = [question]

    refreshed = MagicMock()
    refreshed.id = session_id
    refreshed.status = "in_progress"
    answered_q = MagicMock()
    answered_q.answer = MagicMock()
    refreshed.questions = [answered_q]

    interview_repo.get_session_for_user.side_effect = [session, refreshed]
    interview_repo.get_question_for_session.return_value = question
    interview_repo.save_answer.return_value = MagicMock(
        id=uuid.uuid4(),
        question_id=question_id,
        answer="I built Python REST APIs",
        score=75,
        feedback="Strong answer",
    )

    svc = InterviewServiceImpl(
        interview_repository=interview_repo,
        resume_repository=resume_repo,
        ats_repository=ats_repo,
    )

    result = await svc.submit_answer(
        user_id=str(uuid.uuid4()),
        session_id=str(session_id),
        payload=SubmitAnswerRequest(question_id=str(question_id), answer="I built Python REST APIs with FastAPI"),
    )

    assert result.answer.score >= 0
    interview_repo.save_answer.assert_awaited_once()
