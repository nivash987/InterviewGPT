from __future__ import annotations

from dataclasses import dataclass

from app.modules.career_coach.schemas import LearningRecommendation, WeaknessItem

DEFAULT_ROLE_SKILLS: dict[str, list[str]] = {
    "software engineer": [
        "python",
        "javascript",
        "data structures",
        "algorithms",
        "sql",
        "git",
        "rest apis",
        "system design",
    ],
    "frontend developer": [
        "javascript",
        "typescript",
        "react",
        "html",
        "css",
        "git",
        "rest apis",
        "testing",
    ],
    "backend developer": [
        "python",
        "java",
        "sql",
        "rest apis",
        "docker",
        "git",
        "system design",
        "microservices",
    ],
    "data scientist": [
        "python",
        "sql",
        "machine learning",
        "statistics",
        "pandas",
        "data visualization",
        "git",
        "deep learning",
    ],
    "devops engineer": [
        "linux",
        "docker",
        "kubernetes",
        "ci/cd",
        "aws",
        "terraform",
        "git",
        "monitoring",
    ],
}


def normalize_skill(skill: str) -> str:
    return skill.strip().lower()


def get_required_skills_for_role(role: str, profile_skills: list[str] | None = None) -> list[str]:
    if profile_skills:
        return [normalize_skill(s) for s in profile_skills]
    key = role.strip().lower()
    for role_key, skills in DEFAULT_ROLE_SKILLS.items():
        if role_key in key or key in role_key:
            return skills
    return DEFAULT_ROLE_SKILLS["software engineer"]


@dataclass
class ReadinessInputs:
    target_role: str
    user_skills: list[str]
    required_skills: list[str]
    ats_score: int | None
    interview_avg_score: float | None
    interview_count: int
    job_advanced_count: int
    job_total_count: int
    roadmap_progress: int


@dataclass
class ReadinessResult:
    overall_score: int
    category_scores: dict[str, int]
    weak_areas: list[WeaknessItem]
    missing_skills: list[str]
    recommendations: list[LearningRecommendation]


def compute_skill_coverage(user_skills: list[str], required_skills: list[str]) -> tuple[int, list[str]]:
    if not required_skills:
        return 100, []
    normalized_user = {normalize_skill(s) for s in user_skills}
    missing = [s for s in required_skills if s not in normalized_user]
    coverage = int(round((len(required_skills) - len(missing)) / len(required_skills) * 100))
    return max(0, min(100, coverage)), missing


def compute_readiness(inputs: ReadinessInputs) -> ReadinessResult:
    coverage, missing = compute_skill_coverage(inputs.user_skills, inputs.required_skills)

    resume_score = inputs.ats_score if inputs.ats_score is not None else 50
    interview_score = 0
    if inputs.interview_avg_score is not None and inputs.interview_count > 0:
        interview_score = int(min(100, max(0, inputs.interview_avg_score)))

    job_score = 0
    if inputs.job_total_count > 0:
        job_score = int(min(100, (inputs.job_advanced_count / inputs.job_total_count) * 100))

    roadmap_score = max(0, min(100, inputs.roadmap_progress))

    category_scores = {
        "resume_ats": resume_score,
        "skills_match": coverage,
        "interview_prep": interview_score,
        "job_tracker": job_score,
        "roadmap_progress": roadmap_score,
    }

    weights = {
        "resume_ats": 0.25,
        "skills_match": 0.30,
        "interview_prep": 0.20,
        "job_tracker": 0.15,
        "roadmap_progress": 0.10,
    }
    overall = int(
        round(
            sum(category_scores[k] * weights[k] for k in weights),
        ),
    )
    overall = max(0, min(100, overall))

    weak_areas: list[WeaknessItem] = []
    if coverage < 70:
        weak_areas.append(
            WeaknessItem(
                area="Technical skills",
                severity="high" if coverage < 50 else "medium",
                description=f"Skill coverage for {inputs.target_role} is {coverage}%.",
                suggested_action="Focus on missing core skills via structured learning.",
            ),
        )
    if resume_score < 65:
        weak_areas.append(
            WeaknessItem(
                area="Resume & ATS",
                severity="medium",
                description=f"Resume/ATS readiness is at {resume_score}%.",
                suggested_action="Run ATS analysis and improve keywords and sections.",
            ),
        )
    if interview_score < 60 and inputs.interview_count > 0:
        weak_areas.append(
            WeaknessItem(
                area="Interview performance",
                severity="high" if interview_score < 40 else "medium",
                description=f"Average mock interview score is {interview_score}%.",
                suggested_action="Complete more mock interviews targeting weak topics.",
            ),
        )
    elif inputs.interview_count == 0:
        weak_areas.append(
            WeaknessItem(
                area="Interview practice",
                severity="medium",
                description="No completed mock interviews yet.",
                suggested_action="Start at least one mock interview for your target role.",
            ),
        )
    if job_score < 40 and inputs.job_total_count > 0:
        weak_areas.append(
            WeaknessItem(
                area="Job search momentum",
                severity="low",
                description="Few applications have progressed past initial stages.",
                suggested_action="Follow up on applications and schedule more interviews.",
            ),
        )
    if roadmap_score < 30:
        weak_areas.append(
            WeaknessItem(
                area="Career roadmap",
                severity="medium",
                description=f"Roadmap completion is {roadmap_score}%.",
                suggested_action="Complete the next milestone on your career roadmap.",
            ),
        )

    recommendations = build_learning_recommendations(missing, weak_areas)
    return ReadinessResult(
        overall_score=overall,
        category_scores=category_scores,
        weak_areas=weak_areas,
        missing_skills=missing,
        recommendations=recommendations,
    )


def build_learning_recommendations(
    missing_skills: list[str],
    weak_areas: list[WeaknessItem],
) -> list[LearningRecommendation]:
    recs: list[LearningRecommendation] = []
    for skill in missing_skills[:5]:
        recs.append(
            LearningRecommendation(
                title=f"Learn {skill.title()}",
                description=f"Build foundational knowledge in {skill} through courses and hands-on projects.",
                skill=skill,
                resource_type="course",
                priority="high",
            ),
        )
    for area in weak_areas:
        if area.area == "Interview practice":
            recs.append(
                LearningRecommendation(
                    title="Mock interview sprint",
                    description="Complete 3 mock interviews focused on behavioral and technical questions.",
                    skill="interviewing",
                    resource_type="practice",
                    priority="high",
                ),
            )
        elif area.area == "Resume & ATS":
            recs.append(
                LearningRecommendation(
                    title="Resume optimization workshop",
                    description="Improve ATS score with keyword alignment and section completeness.",
                    skill="resume",
                    resource_type="guide",
                    priority="medium",
                ),
            )
    return recs[:8]
