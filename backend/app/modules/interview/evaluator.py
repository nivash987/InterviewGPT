from __future__ import annotations

import re
from dataclasses import dataclass

MIN_ANSWER_LENGTH = 20
GOOD_ANSWER_LENGTH = 80
STRONG_ANSWER_LENGTH = 150


@dataclass(frozen=True)
class EvaluationResult:
    score: int
    feedback: str
    keywords_matched: list[str]
    keywords_missed: list[str]


def _tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9]+", text.lower())
    return set(tokens)


def _keyword_hits(answer: str, keywords: list[str]) -> tuple[list[str], list[str]]:
    if not keywords:
        return [], []

    answer_lower = answer.lower()
    matched: list[str] = []
    missed: list[str] = []

    for keyword in keywords:
        normalized = keyword.strip().lower()
        if not normalized:
            continue
        if normalized in answer_lower or normalized.replace(" ", "") in answer_lower.replace(" ", ""):
            matched.append(keyword)
        else:
            parts = normalized.split()
            if any(part in answer_lower for part in parts if len(part) > 2):
                matched.append(keyword)
            else:
                missed.append(keyword)

    return matched, missed


def _structure_bonus(answer: str) -> int:
    bonus = 0
    if re.search(r"\b(first|second|then|finally|because|therefore)\b", answer, re.I):
        bonus += 5
    if re.search(r"\b(for example|such as|specifically)\b", answer, re.I):
        bonus += 5
    if answer.count(".") >= 2 or answer.count("\n") >= 1:
        bonus += 5
    return min(bonus, 15)


def _length_score(answer: str) -> int:
    length = len(answer.strip())
    if length < MIN_ANSWER_LENGTH:
        return 10
    if length < GOOD_ANSWER_LENGTH:
        return 25
    if length < STRONG_ANSWER_LENGTH:
        return 35
    return 40


def evaluate_answer(*, answer: str, expected_keywords: list[str]) -> EvaluationResult:
    """Rule-based scoring: keyword coverage, length, and structure."""
    trimmed = answer.strip()
    if not trimmed:
        return EvaluationResult(
            score=0,
            feedback="No answer provided. Include specific examples and relevant technical terms.",
            keywords_matched=[],
            keywords_missed=list(expected_keywords),
        )

    matched, missed = _keyword_hits(trimmed, expected_keywords)
    keyword_total = len(expected_keywords) or 1
    keyword_ratio = len(matched) / keyword_total
    keyword_points = int(keyword_ratio * 45)

    length_points = _length_score(trimmed)
    structure_points = _structure_bonus(trimmed)

    raw_score = keyword_points + length_points + structure_points
    score = max(0, min(100, raw_score))

    if score >= 85:
        feedback = (
            "Excellent answer. You covered key concepts with good depth and structure. "
            f"Keywords addressed: {', '.join(matched) if matched else 'general relevance'}."
        )
    elif score >= 70:
        feedback = (
            "Strong answer with solid coverage. "
            + (
                f"Consider expanding on: {', '.join(missed)}."
                if missed
                else "Add more concrete metrics or outcomes to strengthen impact."
            )
        )
    elif score >= 50:
        feedback = (
            "Adequate answer but missing depth. "
            + (
                f"Try to mention: {', '.join(missed)}."
                if missed
                else "Provide a specific example from your experience."
            )
        )
    elif score >= 30:
        feedback = (
            "Answer is too brief or vague. Elaborate with a STAR-style example "
            f"and include terms like: {', '.join(missed[:5]) if missed else 'relevant skills and outcomes'}."
        )
    else:
        feedback = (
            "Weak answer. Provide a structured response with context, actions, and results. "
            f"Expected topics: {', '.join(expected_keywords[:6]) if expected_keywords else 'role-relevant details'}."
        )

    return EvaluationResult(
        score=score,
        feedback=feedback,
        keywords_matched=matched,
        keywords_missed=missed,
    )


def compute_session_score(question_scores: list[int]) -> int:
    if not question_scores:
        return 0
    return round(sum(question_scores) / len(question_scores))
