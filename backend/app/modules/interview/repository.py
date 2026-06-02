from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.interview import InterviewAnswer, InterviewQuestion, InterviewSession
from app.db.models.resume import Resume
from app.modules.interview.generator import GeneratedQuestion
from app.modules.interview.schemas import (
    InterviewAnswerPublic,
    InterviewHistoryItem,
    InterviewQuestionPublic,
    InterviewSessionPublic,
)


class InterviewRepository(ABC):
    @abstractmethod
    async def create_session(
        self,
        *,
        user_id: str,
        resume_id: str,
        role: str,
        difficulty: str,
        question_count: int,
        questions: list[GeneratedQuestion],
    ) -> InterviewSession: ...

    @abstractmethod
    async def get_session_for_user(
        self,
        *,
        user_id: str,
        session_id: str,
    ) -> InterviewSession | None: ...

    @abstractmethod
    async def get_question_for_session(
        self,
        *,
        session_id: str,
        question_id: str,
    ) -> InterviewQuestion | None: ...

    @abstractmethod
    async def save_answer(
        self,
        *,
        question_id: str,
        answer: str,
        score: int,
        feedback: str,
    ) -> InterviewAnswer: ...

    @abstractmethod
    async def update_session_score(
        self,
        *,
        session_id: str,
        total_score: int,
        status: str,
    ) -> InterviewSession | None: ...

    @abstractmethod
    async def list_history_for_user(self, *, user_id: str) -> list[tuple[InterviewSession, str | None]]: ...

    @abstractmethod
    async def list_completed_sessions_for_user(self, *, user_id: str) -> list[InterviewSession]: ...


def _answer_to_public(answer: InterviewAnswer) -> InterviewAnswerPublic:
    return InterviewAnswerPublic(
        id=str(answer.id),
        question_id=str(answer.question_id),
        answer=answer.answer,
        score=answer.score,
        feedback=answer.feedback,
    )


def _question_to_public(question: InterviewQuestion) -> InterviewQuestionPublic:
    return InterviewQuestionPublic(
        id=str(question.id),
        question=question.question,
        category=question.category,
        difficulty=question.difficulty,
        expected_keywords=list(question.expected_keywords),
        sort_order=question.sort_order,
        answer=_answer_to_public(question.answer) if question.answer else None,
    )


def session_to_public(session: InterviewSession) -> InterviewSessionPublic:
    return InterviewSessionPublic(
        id=str(session.id),
        resume_id=str(session.resume_id),
        role=session.role,
        difficulty=session.difficulty,
        question_count=session.question_count,
        total_score=session.total_score,
        status=session.status,  # type: ignore[arg-type]
        started_at=session.started_at,
        completed_at=session.completed_at,
        questions=[_question_to_public(q) for q in session.questions],
    )


def history_item_from_row(session: InterviewSession, resume_title: str | None) -> InterviewHistoryItem:
    return InterviewHistoryItem(
        id=str(session.id),
        resume_id=str(session.resume_id),
        resume_title=resume_title,
        role=session.role,
        difficulty=session.difficulty,
        question_count=session.question_count,
        total_score=session.total_score,
        status=session.status,  # type: ignore[arg-type]
        started_at=session.started_at,
        completed_at=session.completed_at,
    )


class SqlAlchemyInterviewRepository(InterviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_session(
        self,
        *,
        user_id: str,
        resume_id: str,
        role: str,
        difficulty: str,
        question_count: int,
        questions: list[GeneratedQuestion],
    ) -> InterviewSession:
        interview_session = InterviewSession(
            user_id=uuid.UUID(user_id),
            resume_id=uuid.UUID(resume_id),
            role=role,
            difficulty=difficulty,
            question_count=question_count,
            status="in_progress",
        )
        self._session.add(interview_session)
        await self._session.flush()

        for index, generated in enumerate(questions):
            question = InterviewQuestion(
                session_id=interview_session.id,
                question=generated.question,
                category=generated.category,
                difficulty=generated.difficulty,
                expected_keywords=generated.expected_keywords,
                sort_order=index,
            )
            self._session.add(question)

        await self._session.flush()
        reloaded = await self._load_session(interview_session.id)
        assert reloaded is not None
        return reloaded

    async def _load_session(self, session_id: uuid.UUID) -> InterviewSession | None:
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.id == session_id)
            .options(
                selectinload(InterviewSession.questions).selectinload(InterviewQuestion.answer),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_session_for_user(
        self,
        *,
        user_id: str,
        session_id: str,
    ) -> InterviewSession | None:
        stmt = (
            select(InterviewSession)
            .where(
                InterviewSession.id == uuid.UUID(session_id),
                InterviewSession.user_id == uuid.UUID(user_id),
            )
            .options(
                selectinload(InterviewSession.questions).selectinload(InterviewQuestion.answer),
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_question_for_session(
        self,
        *,
        session_id: str,
        question_id: str,
    ) -> InterviewQuestion | None:
        stmt = (
            select(InterviewQuestion)
            .where(
                InterviewQuestion.id == uuid.UUID(question_id),
                InterviewQuestion.session_id == uuid.UUID(session_id),
            )
            .options(selectinload(InterviewQuestion.answer))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save_answer(
        self,
        *,
        question_id: str,
        answer: str,
        score: int,
        feedback: str,
    ) -> InterviewAnswer:
        existing_stmt = select(InterviewAnswer).where(
            InterviewAnswer.question_id == uuid.UUID(question_id)
        )
        existing_result = await self._session.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()

        if existing is not None:
            existing.answer = answer
            existing.score = score
            existing.feedback = feedback
            await self._session.flush()
            return existing

        record = InterviewAnswer(
            question_id=uuid.UUID(question_id),
            answer=answer,
            score=score,
            feedback=feedback,
        )
        self._session.add(record)
        await self._session.flush()
        return record

    async def update_session_score(
        self,
        *,
        session_id: str,
        total_score: int,
        status: str,
    ) -> InterviewSession | None:
        session = await self._load_session(uuid.UUID(session_id))
        if session is None:
            return None

        from datetime import UTC, datetime

        session.total_score = total_score
        session.status = status
        if status == "completed":
            session.completed_at = datetime.now(UTC)
        await self._session.flush()
        return session

    async def list_history_for_user(self, *, user_id: str) -> list[tuple[InterviewSession, str | None]]:
        stmt = (
            select(InterviewSession, Resume.title)
            .join(Resume, Resume.id == InterviewSession.resume_id)
            .where(InterviewSession.user_id == uuid.UUID(user_id))
            .order_by(InterviewSession.started_at.desc())
        )
        result = await self._session.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_completed_sessions_for_user(self, *, user_id: str) -> list[InterviewSession]:
        stmt = (
            select(InterviewSession)
            .where(
                InterviewSession.user_id == uuid.UUID(user_id),
                InterviewSession.status == "completed",
            )
            .options(
                selectinload(InterviewSession.questions).selectinload(InterviewQuestion.answer),
            )
            .order_by(InterviewSession.completed_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
