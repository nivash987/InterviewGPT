from app.modules.career_coach.readiness_engine import (
    ReadinessInputs,
    compute_readiness,
    compute_skill_coverage,
    get_required_skills_for_role,
)
from app.modules.career_coach.skill_gap import analyze_skill_gaps


def test_get_required_skills_for_role_default() -> None:
    skills = get_required_skills_for_role("Software Engineer")
    assert "python" in skills
    assert "algorithms" in skills


def test_compute_skill_coverage() -> None:
    coverage, missing = compute_skill_coverage(
        ["python", "sql"],
        ["python", "sql", "docker"],
    )
    assert coverage == 66 or coverage == 67
    assert "docker" in missing


def test_compute_readiness_high_when_strong() -> None:
    required = get_required_skills_for_role("Software Engineer")
    result = compute_readiness(
        ReadinessInputs(
            target_role="Software Engineer",
            user_skills=required,
            required_skills=required,
            ats_score=90,
            interview_avg_score=85.0,
            interview_count=3,
            job_advanced_count=2,
            job_total_count=4,
            roadmap_progress=80,
        ),
    )
    assert result.overall_score >= 75
    assert len(result.recommendations) >= 0


def test_analyze_skill_gaps() -> None:
    analysis = analyze_skill_gaps(
        target_role="Frontend Developer",
        user_skills=["javascript", "html"],
    )
    assert analysis.coverage_percent < 100
    assert len(analysis.missing_skills) > 0
    assert analysis.missing_skills[0].priority == "high"
