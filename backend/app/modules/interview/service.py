from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict

from app.core.errors import BadRequestError, NotFoundError
from app.modules.ats.repository import AtsRepository
from app.modules.interview.evaluator import compute_session_score, evaluate_answer
from app.modules.interview.generator import DIFFICULTIES, QUESTION_COUNTS, generate_interview_questions
from app.modules.interview.repository import (
    InterviewRepository,
    history_item_from_row,
    session_to_public,
    _answer_to_public,
)
from app.modules.interview.schemas import (
    CategoryScore,
    FinishInterviewResponse,
    InterviewAnalytics,
    InterviewDetailResponse,
    InterviewHistoryResponse,
    InterviewSummary,
    ScoreTrendPoint,
    SessionProgress,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    TopicInsight,
)
from app.modules.resume.parser import parse_resume_text
from app.modules.resume.repository import ResumeRepository
from app.modules.resume.schemas import ParsedResumeData


class InterviewService(ABC):
    @abstractmethod
    async def start_interview(self, *, user_id: str, payload: StartInterviewRequest) -> StartInterviewResponse: ...

    @abstractmethod
    async def submit_answer(
        self,
        *,
        user_id: str,
        session_id: str,
        payload: SubmitAnswerRequest,
    ) -> SubmitAnswerResponse: ...

    @abstractmethod
    async def finish_interview(self, *, user_id: str, session_id: str) -> FinishInterviewResponse: ...

    @abstractmethod
    async def get_history(self, *, user_id: str) -> InterviewHistoryResponse: ...

    @abstractmethod
    async def get_session(self, *, user_id: str, session_id: str) -> InterviewDetailResponse: ...


class InterviewServiceImpl(InterviewService):
    def __init__(
        self,
        *,
        interview_repository: InterviewRepository,
        resume_repository: ResumeRepository,
        ats_repository: AtsRepository,
    ) -> None:
        self._interview_repository = interview_repository
        self._resume_repository = resume_repository
        self._ats_repository = ats_repository

    async def _load_context(
        self,
        *,
        user_id: str,
        resume_id: str,
        role: str,
    ) -> tuple[ParsedResumeData, list[str], list[str]]:
        resume = await self._resume_repository.get_resume_for_user(resume_id=resume_id, user_id=user_id)
        if resume is None:
            raise NotFoundError("Resume not found")

        version = resume.current_version
        if version is None:
            raise BadRequestError("Resume has no uploaded version")

        raw_text = version.raw_text or ""
        if version.parsed_data:
            parsed = ParsedResumeData.model_validate(version.parsed_data)
        elif raw_text.strip():
            parsed = parse_resume_text(raw_text)
        else:
            raise BadRequestError("Resume has no extractable content for interview generation")

        ats_skills_found: list[str] = []
        ats_missing_skills: list[str] = []
        analysis = await self._ats_repository.get_latest_for_resume(user_id=user_id, resume_id=resume_id)
        if analysis is not None:
            ats_skills_found = list(analysis.skills_found)
            ats_missing_skills = list(analysis.missing_skills)
            if not role.strip():
                roles = analysis.recommended_roles
                if roles and isinstance(roles, list) and len(roles) > 0:
                    first = roles[0]
                    if isinstance(first, dict) and first.get("role_name"):
                        role = str(first["role_name"])

        return parsed, ats_skills_found, ats_missing_skills

    def _experience_bullets(self, parsed: ParsedResumeData) -> list[str]:
        bullets: list[str] = []
        for entry in parsed.experience:
            if entry.description:
                bullets.append(entry.description)
            if entry.title:
                bullets.append(entry.title)
        return bullets

    async def start_interview(self, *, user_id: str, payload: StartInterviewRequest) -> StartInterviewResponse:
        if payload.difficulty not in DIFFICULTIES:
            raise BadRequestError(f"Difficulty must be one of: {', '.join(DIFFICULTIES)}")
        if payload.question_count not in QUESTION_COUNTS:
            raise BadRequestError(f"Question count must be one of: {', '.join(map(str, QUESTION_COUNTS))}")

        parsed, ats_found, ats_missing = await self._load_context(
            user_id=user_id,
            resume_id=payload.resume_id,
            role=payload.role,
        )

        questions = generate_interview_questions(
            role=payload.role,
            difficulty=payload.difficulty,
            question_count=payload.question_count,
            resume_skills=parsed.skills,
            ats_skills_found=ats_found,
            ats_missing_skills=ats_missing,
            experience_bullets=self._experience_bullets(parsed),
        )

        session = await self._interview_repository.create_session(
            user_id=user_id,
            resume_id=payload.resume_id,
            role=payload.role,
            difficulty=payload.difficulty,
            question_count=payload.question_count,
            questions=questions,
        )

        public = session_to_public(session)
        answered = sum(1 for q in public.questions if q.answer is not None)
        return StartInterviewResponse(
            session=public,
            current_question_index=answered,
        )

    def _session_progress(self, session) -> SessionProgress:
        total = len(session.questions)
        answered = sum(1 for q in session.questions if q.answer is not None)
        return SessionProgress(
            answered_count=answered,
            total_questions=total,
            is_complete=answered >= total and total > 0,
        )

    async def submit_answer(
        self,
        *,
        user_id: str,
        session_id: str,
        payload: SubmitAnswerRequest,
    ) -> SubmitAnswerResponse:
        session = await self._interview_repository.get_session_for_user(
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            raise NotFoundError("Interview session not found")
        if session.status == "completed":
            raise BadRequestError("Interview session is already completed")

        question = await self._interview_repository.get_question_for_session(
            session_id=session_id,
            question_id=payload.question_id,
        )
        if question is None:
            raise NotFoundError("Question not found in this session")

        evaluation = evaluate_answer(
            answer=payload.answer,
            expected_keywords=list(question.expected_keywords),
        )

        record = await self._interview_repository.save_answer(
            question_id=payload.question_id,
            answer=payload.answer.strip(),
            score=evaluation.score,
            feedback=evaluation.feedback,
        )

        refreshed = await self._interview_repository.get_session_for_user(
            user_id=user_id,
            session_id=session_id,
        )
        assert refreshed is not None

        return SubmitAnswerResponse(
            answer=_answer_to_public(record),
            session_progress=self._session_progress(refreshed),
        )

    def _build_summary(self, session) -> InterviewSummary:
        category_scores: dict[str, list[int]] = defaultdict(list)
        question_scores: list[int] = []

        for question in session.questions:
            if question.answer is None:
                continue
            category_scores[question.category].append(question.answer.score)
            question_scores.append(question.answer.score)

        total_score = compute_session_score(question_scores)
        category_breakdown = [
            CategoryScore(
                category=category,
                average_score=round(sum(scores) / len(scores), 1),
                question_count=len(scores),
            )
            for category, scores in sorted(category_scores.items())
        ]
        average_per_category = {c.category: c.average_score for c in category_breakdown}

        strengths: list[str] = []
        improvements: list[str] = []
        for item in category_breakdown:
            if item.average_score >= 75:
                strengths.append(f"Strong performance in {item.category} ({item.average_score:.0f}%)")
            elif item.average_score < 55:
                improvements.append(f"Review {item.category} topics (avg {item.average_score:.0f}%)")

        if total_score >= 80 and not strengths:
            strengths.append("Consistent high-quality answers across the interview")
        if total_score < 60 and not improvements:
            improvements.append("Provide more specific examples and technical depth in answers")

        return InterviewSummary(
            total_score=total_score,
            questions_answered=len(question_scores),
            total_questions=len(session.questions),
            average_per_category=average_per_category,
            strengths=strengths or ["Completed the full mock interview"],
            improvements=improvements or ["Keep practicing with harder difficulty levels"],
            category_breakdown=category_breakdown,
        )

    def _build_analytics(self, completed_sessions: list) -> InterviewAnalytics:
        score_trend: list[ScoreTrendPoint] = []
        category_totals: dict[str, list[int]] = defaultdict(list)

        for session in completed_sessions:
            if session.total_score is not None:
                score_trend.append(
                    ScoreTrendPoint(
                        session_id=str(session.id),
                        role=session.role,
                        total_score=session.total_score,
                        completed_at=session.completed_at,
                    )
                )
            for question in session.questions:
                if question.answer is not None:
                    category_totals[question.category].append(question.answer.score)

        topic_insights = [
            TopicInsight(
                category=category,
                average_score=round(sum(scores) / len(scores), 1),
                question_count=len(scores),
            )
            for category, scores in category_totals.items()
        ]
        topic_insights.sort(key=lambda t: t.average_score)

        weak = [t for t in topic_insights if t.average_score < 60][:5]
        strong = [t for t in reversed(topic_insights) if t.average_score >= 70][:5]

        return InterviewAnalytics(
            score_trend=score_trend[:20],
            weak_topics=weak,
            strong_topics=strong,
        )

    async def finish_interview(self, *, user_id: str, session_id: str) -> FinishInterviewResponse:
        session = await self._interview_repository.get_session_for_user(
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            raise NotFoundError("Interview session not found")

        summary = self._build_summary(session)
        updated = await self._interview_repository.update_session_score(
            session_id=session_id,
            total_score=summary.total_score,
            status="completed",
        )
        if updated is None:
            raise NotFoundError("Interview session not found")

        refreshed = await self._interview_repository.get_session_for_user(
            user_id=user_id,
            session_id=session_id,
        )
        assert refreshed is not None

        return FinishInterviewResponse(
            session=session_to_public(refreshed),
            summary=summary,
        )

    async def get_history(self, *, user_id: str) -> InterviewHistoryResponse:
        rows = await self._interview_repository.list_history_for_user(user_id=user_id)
        items = [history_item_from_row(session, title) for session, title in rows]
        return InterviewHistoryResponse(items=items, total=len(items))

    async def get_session(self, *, user_id: str, session_id: str) -> InterviewDetailResponse:
        session = await self._interview_repository.get_session_for_user(
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            raise NotFoundError("Interview session not found")

        summary = None
        analytics = None
        if session.status == "completed":
            summary = self._build_summary(session)
            completed = await self._interview_repository.list_completed_sessions_for_user(user_id=user_id)
            analytics = self._build_analytics(completed)

        return InterviewDetailResponse(
            session=session_to_public(session),
            summary=summary,
            analytics=analytics,
        )
