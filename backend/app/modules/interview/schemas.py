from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

DifficultyLevel = Literal["easy", "medium", "hard"]
QuestionCountOption = Literal[5, 10, 15, 20]
SessionStatus = Literal["in_progress", "completed"]


class StartInterviewRequest(BaseModel):
    resume_id: str
    role: str = Field(min_length=1, max_length=128)
    difficulty: DifficultyLevel = "medium"
    question_count: QuestionCountOption = 10


class SubmitAnswerRequest(BaseModel):
    question_id: str
    answer: str = Field(min_length=1, max_length=10000)


class InterviewAnswerPublic(BaseModel):
    id: str
    question_id: str
    answer: str
    score: int
    feedback: str


class InterviewQuestionPublic(BaseModel):
    id: str
    question: str
    category: str
    difficulty: str
    expected_keywords: list[str]
    sort_order: int
    answer: InterviewAnswerPublic | None = None


class InterviewSessionPublic(BaseModel):
    id: str
    resume_id: str
    role: str
    difficulty: str
    question_count: int
    total_score: int | None
    status: SessionStatus
    started_at: datetime
    completed_at: datetime | None
    questions: list[InterviewQuestionPublic] = Field(default_factory=list)


class StartInterviewResponse(BaseModel):
    session: InterviewSessionPublic
    current_question_index: int


class SubmitAnswerResponse(BaseModel):
    answer: InterviewAnswerPublic
    session_progress: SessionProgress


class SessionProgress(BaseModel):
    answered_count: int
    total_questions: int
    is_complete: bool


class FinishInterviewResponse(BaseModel):
    session: InterviewSessionPublic
    summary: InterviewSummary


class InterviewSummary(BaseModel):
    total_score: int
    questions_answered: int
    total_questions: int
    average_per_category: dict[str, float]
    strengths: list[str]
    improvements: list[str]
    category_breakdown: list[CategoryScore]


class CategoryScore(BaseModel):
    category: str
    average_score: float
    question_count: int


class InterviewHistoryItem(BaseModel):
    id: str
    resume_id: str
    resume_title: str | None
    role: str
    difficulty: str
    question_count: int
    total_score: int | None
    status: SessionStatus
    started_at: datetime
    completed_at: datetime | None


class InterviewHistoryResponse(BaseModel):
    items: list[InterviewHistoryItem]
    total: int


class InterviewAnalytics(BaseModel):
    score_trend: list[ScoreTrendPoint]
    weak_topics: list[TopicInsight]
    strong_topics: list[TopicInsight]


class ScoreTrendPoint(BaseModel):
    session_id: str
    role: str
    total_score: int
    completed_at: datetime | None


class TopicInsight(BaseModel):
    category: str
    average_score: float
    question_count: int


class InterviewDetailResponse(BaseModel):
    session: InterviewSessionPublic
    summary: InterviewSummary | None
    analytics: InterviewAnalytics | None
