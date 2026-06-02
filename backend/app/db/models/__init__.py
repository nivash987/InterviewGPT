from __future__ import annotations

from app.db.models.ats import AtsAnalysis, JobProfile, SkillTaxonomy
from app.db.models.career_coach import CareerRoadmap, ProgressTracking, ReadinessScore, UserGoal, UserSkill
from app.db.models.interview import InterviewAnswer, InterviewQuestion, InterviewSession
from app.db.models.job_application import (
    ApplicationStatusHistory,
    InterviewNote,
    JobApplication,
    Reminder,
)
from app.db.models.resume import Resume, ResumeVersion
from app.db.models.user import (
    EmailVerificationToken,
    PasswordResetToken,
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
    UserRole,
)

__all__ = [
    "ApplicationStatusHistory",
    "AtsAnalysis",
    "CareerRoadmap",
    "InterviewAnswer",
    "InterviewNote",
    "InterviewQuestion",
    "InterviewSession",
    "JobApplication",
    "EmailVerificationToken",
    "JobProfile",
    "PasswordResetToken",
    "Permission",
    "ProgressTracking",
    "ReadinessScore",
    "RefreshToken",
    "Reminder",
    "Resume",
    "ResumeVersion",
    "Role",
    "RolePermission",
    "SkillTaxonomy",
    "User",
    "UserGoal",
    "UserRole",
    "UserSkill",
]
