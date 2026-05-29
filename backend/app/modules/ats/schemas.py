from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SectionScores(BaseModel):
    contact_information: int = 0
    summary: int = 0
    skills: int = 0
    experience: int = 0
    education: int = 0
    projects: int = 0


class KeywordCoverage(BaseModel):
    matched_keywords: int = 0
    total_keywords: int = 0
    coverage_percent: float = 0.0


class RecommendedRole(BaseModel):
    role_name: str
    match_score: int
    matched_required: list[str] = Field(default_factory=list)
    matched_preferred: list[str] = Field(default_factory=list)
    missing_required: list[str] = Field(default_factory=list)


class AtsAnalysisResult(BaseModel):
    ats_score: int
    completeness_score: int
    section_scores: SectionScores
    skills_found: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    keyword_coverage: KeywordCoverage
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
    recommended_roles: list[RecommendedRole] = Field(default_factory=list)


class AtsAnalysisPublic(BaseModel):
    id: str
    resume_id: str
    ats_score: int
    completeness_score: int
    section_scores: SectionScores
    skills_found: list[str]
    missing_skills: list[str]
    keyword_coverage: KeywordCoverage
    strengths: list[str]
    weaknesses: list[str]
    suggestions: list[str]
    recommended_roles: list[RecommendedRole]
    created_at: datetime


class AtsHistoryItem(BaseModel):
    id: str
    resume_id: str
    resume_title: str | None = None
    ats_score: int
    completeness_score: int
    created_at: datetime


class AtsHistoryResponse(BaseModel):
    items: list[AtsHistoryItem]
    total: int
