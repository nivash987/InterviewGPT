from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

PROFICIENCY_LEVELS = ("beginner", "intermediate", "advanced", "expert")
MILESTONE_STATUSES = ("pending", "in_progress", "completed", "skipped")


class UserGoalCreate(BaseModel):
    target_role: str = Field(min_length=1, max_length=128)
    target_timeline_months: int | None = Field(default=None, ge=1, le=60)
    description: str | None = Field(default=None, max_length=2000)


class UserGoalPublic(BaseModel):
    id: str
    target_role: str
    target_timeline_months: int | None
    description: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserSkillUpsert(BaseModel):
    skill_name: str = Field(min_length=1, max_length=128)
    proficiency_level: str = Field(default="beginner")
    source: str = Field(default="manual")


class UserSkillPublic(BaseModel):
    id: str
    skill_name: str
    proficiency_level: str
    source: str
    created_at: datetime
    updated_at: datetime


class RoadmapMilestone(BaseModel):
    id: str
    title: str
    description: str
    order: int
    estimated_weeks: int
    skills: list[str] = Field(default_factory=list)
    status: str = "pending"


class CareerRoadmapPublic(BaseModel):
    id: str
    goal_id: str | None
    title: str
    target_role: str
    milestones: list[RoadmapMilestone]
    status: str
    progress_percent: int
    created_at: datetime
    updated_at: datetime


class ProgressUpdateRequest(BaseModel):
    status: str
    notes: str | None = None


class ProgressEntryPublic(BaseModel):
    id: str
    roadmap_id: str
    milestone_id: str
    status: str
    notes: str | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SkillGapItem(BaseModel):
    skill_name: str
    priority: str
    reason: str


class SkillGapAnalysis(BaseModel):
    target_role: str
    required_skills: list[str]
    user_skills: list[str]
    missing_skills: list[SkillGapItem]
    coverage_percent: int


class LearningRecommendation(BaseModel):
    title: str
    description: str
    skill: str
    resource_type: str
    priority: str


class WeaknessItem(BaseModel):
    area: str
    severity: str
    description: str
    suggested_action: str


class ReadinessScorePublic(BaseModel):
    id: str
    overall_score: int
    category_scores: dict[str, int]
    weak_areas: list[WeaknessItem]
    missing_skills: list[str]
    recommendations: list[LearningRecommendation]
    computed_at: datetime


class CareerCoachDashboard(BaseModel):
    readiness_score: int | None
    readiness_trend: str | None
    missing_skills: list[str]
    roadmap_progress_percent: int | None
    weak_areas: list[WeaknessItem]
    recommendations: list[LearningRecommendation]
    active_goal: UserGoalPublic | None
    skill_coverage_percent: int | None
