from __future__ import annotations

from app.modules.interview.generator import DIFFICULTIES, QUESTION_COUNTS, generate_interview_questions


def test_generate_questions_count_and_difficulty() -> None:
    for count in QUESTION_COUNTS:
        questions = generate_interview_questions(
            role="Backend Developer",
            difficulty="medium",
            question_count=count,
            resume_skills=["Python", "FastAPI", "PostgreSQL"],
            ats_skills_found=["Docker"],
            ats_missing_skills=["Kubernetes"],
            experience_bullets=["Built REST APIs"],
        )
        assert len(questions) == count
        assert all(q.difficulty == "medium" for q in questions)
        assert all(q.question for q in questions)
        assert all(q.category for q in questions)


def test_generate_questions_uses_skills_and_gaps() -> None:
    questions = generate_interview_questions(
        role="Frontend Developer",
        difficulty="hard",
        question_count=10,
        resume_skills=["React", "TypeScript"],
        ats_skills_found=[],
        ats_missing_skills=["GraphQL"],
        experience_bullets=[],
    )
    categories = {q.category for q in questions}
    assert "Technical" in categories
    assert any("GraphQL" in q.question or "graphql" in " ".join(q.expected_keywords) for q in questions)


def test_invalid_difficulty_defaults_to_medium_pool() -> None:
    questions = generate_interview_questions(
        role="Data Engineer",
        difficulty="invalid",  # type: ignore[arg-type]
        question_count=5,
        resume_skills=["Python"],
        ats_skills_found=[],
        ats_missing_skills=[],
        experience_bullets=[],
    )
    assert len(questions) == 5
    assert all(q.difficulty == "medium" for q in questions)


def test_all_difficulties_supported() -> None:
    for difficulty in DIFFICULTIES:
        questions = generate_interview_questions(
            role="Software Engineer",
            difficulty=difficulty,
            question_count=5,
            resume_skills=["Git"],
            ats_skills_found=[],
            ats_missing_skills=[],
            experience_bullets=[],
        )
        assert len(questions) == 5
