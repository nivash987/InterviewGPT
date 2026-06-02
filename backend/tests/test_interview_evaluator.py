from __future__ import annotations

from app.modules.interview.evaluator import compute_session_score, evaluate_answer


def test_evaluate_empty_answer() -> None:
    result = evaluate_answer(answer="   ", expected_keywords=["python", "api"])
    assert result.score == 0
    assert "No answer" in result.feedback


def test_evaluate_strong_answer() -> None:
    answer = (
        "In my recent project, I built REST APIs with Python and FastAPI. "
        "For example, we integrated PostgreSQL for persistence. "
        "First we designed the schema, then implemented endpoints, and finally "
        "added monitoring because performance mattered in production."
    )
    result = evaluate_answer(
        answer=answer,
        expected_keywords=["python", "fastapi", "postgresql", "rest", "api"],
    )
    assert result.score >= 70
    assert len(result.keywords_matched) >= 3


def test_evaluate_weak_short_answer() -> None:
    result = evaluate_answer(answer="I used it before.", expected_keywords=["kubernetes", "docker", "scaling"])
    assert result.score < 50
    assert len(result.keywords_missed) >= 1


def test_compute_session_score() -> None:
    assert compute_session_score([80, 60, 100]) == 80
    assert compute_session_score([]) == 0
