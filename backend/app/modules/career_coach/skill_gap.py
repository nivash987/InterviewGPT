from __future__ import annotations

from app.modules.career_coach.readiness_engine import compute_skill_coverage, get_required_skills_for_role, normalize_skill
from app.modules.career_coach.schemas import SkillGapAnalysis, SkillGapItem


def analyze_skill_gaps(
    *,
    target_role: str,
    user_skills: list[str],
    profile_required_skills: list[str] | None = None,
) -> SkillGapAnalysis:
    required = get_required_skills_for_role(target_role, profile_required_skills)
    coverage, missing = compute_skill_coverage(user_skills, required)

    gap_items: list[SkillGapItem] = []
    for idx, skill in enumerate(missing):
        priority = "high" if idx < 3 else "medium" if idx < 6 else "low"
        gap_items.append(
            SkillGapItem(
                skill_name=skill,
                priority=priority,
                reason=f"Required for {target_role} but not in your skill profile.",
            ),
        )

    return SkillGapAnalysis(
        target_role=target_role,
        required_skills=required,
        user_skills=[normalize_skill(s) for s in user_skills],
        missing_skills=gap_items,
        coverage_percent=coverage,
    )
