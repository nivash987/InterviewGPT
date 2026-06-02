from __future__ import annotations

from app.modules.career_coach.readiness_engine import get_required_skills_for_role
from app.modules.career_coach.schemas import RoadmapMilestone


def build_roadmap_milestones(target_role: str, missing_skills: list[str]) -> list[dict]:
    required = get_required_skills_for_role(target_role)
    gap_skills = missing_skills[:6] if missing_skills else required[:4]

    milestones: list[dict] = [
        {
            "id": "m1",
            "title": "Foundation & fundamentals",
            "description": "Strengthen core concepts and programming fundamentals for your target role.",
            "order": 1,
            "estimated_weeks": 3,
            "skills": gap_skills[:2] or required[:2],
            "status": "pending",
        },
        {
            "id": "m2",
            "title": "Core technical skills",
            "description": "Master role-specific technologies and tools through structured practice.",
            "order": 2,
            "estimated_weeks": 4,
            "skills": gap_skills[2:4] or required[2:4],
            "status": "pending",
        },
        {
            "id": "m3",
            "title": "Projects & portfolio",
            "description": "Build 2–3 portfolio projects demonstrating applied skills.",
            "order": 3,
            "estimated_weeks": 4,
            "skills": ["portfolio", "projects"],
            "status": "pending",
        },
        {
            "id": "m4",
            "title": "Interview preparation",
            "description": "Practice mock interviews, coding challenges, and behavioral questions.",
            "order": 4,
            "estimated_weeks": 3,
            "skills": ["mock interviews", "algorithms", "system design"],
            "status": "pending",
        },
        {
            "id": "m5",
            "title": "Applications & placement",
            "description": "Apply to roles, track applications, and refine based on feedback.",
            "order": 5,
            "estimated_weeks": 4,
            "skills": ["job search", "networking"],
            "status": "pending",
        },
    ]
    return milestones


def milestones_to_public(raw: list) -> list[RoadmapMilestone]:
    return [RoadmapMilestone.model_validate(m) for m in raw]
