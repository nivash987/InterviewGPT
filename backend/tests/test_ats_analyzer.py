from __future__ import annotations

import pytest

from app.modules.ats.analyzer import JobProfileData, analyze_resume
from app.modules.resume.parser import parse_resume_text

SAMPLE_RESUME = """
Jane Doe
jane.doe@example.com
+1 (555) 123-4567

Professional Summary
Experienced software engineer with 5 years building scalable web applications.

Skills
Python, FastAPI, PostgreSQL, React, Docker, Git, REST API

Experience
Senior Software Engineer - Acme Corp
- Built APIs serving 1M requests/day using Python and FastAPI
- Led migration to async Python stack with PostgreSQL

Software Engineer - Startup Inc
- Developed MVP in 3 months using React and Node.js

Projects
InterviewGPT
- AI-powered interview preparation platform built with Next.js and FastAPI

Education
B.S. Computer Science - State University
2018 - 2022
"""

DEFAULT_JOB_PROFILES = [
    JobProfileData(
        role_name="Backend Developer",
        required_skills=["Python", "SQL", "REST API", "Git"],
        preferred_skills=["FastAPI", "Docker", "PostgreSQL"],
    ),
    JobProfileData(
        role_name="Full Stack Developer",
        required_skills=["JavaScript", "Python", "React", "SQL"],
        preferred_skills=["TypeScript", "Next.js", "FastAPI"],
    ),
]

TAXONOMY_SKILLS = [
    "Python", "FastAPI", "PostgreSQL", "React", "Docker", "Git",
    "REST API", "JavaScript", "TypeScript", "Next.js", "SQL", "Node.js",
]


def test_analyze_resume_returns_valid_scores() -> None:
    parsed = parse_resume_text(SAMPLE_RESUME)
    result = analyze_resume(
        parsed=parsed,
        raw_text=SAMPLE_RESUME,
        taxonomy_skills=TAXONOMY_SKILLS,
        job_profiles=DEFAULT_JOB_PROFILES,
    )

    assert 0 <= result.ats_score <= 100
    assert 0 <= result.completeness_score <= 100
    assert result.section_scores.contact_information >= 80
    assert result.section_scores.skills >= 70
    assert result.section_scores.experience >= 60
    assert len(result.skills_found) >= 4


def test_analyze_resume_extracts_skills() -> None:
    parsed = parse_resume_text(SAMPLE_RESUME)
    result = analyze_resume(
        parsed=parsed,
        raw_text=SAMPLE_RESUME,
        taxonomy_skills=TAXONOMY_SKILLS,
        job_profiles=DEFAULT_JOB_PROFILES,
    )

    found_lower = {s.lower() for s in result.skills_found}
    assert "python" in found_lower
    assert "fastapi" in found_lower or "postgresql" in found_lower


def test_analyze_resume_recommends_roles() -> None:
    parsed = parse_resume_text(SAMPLE_RESUME)
    result = analyze_resume(
        parsed=parsed,
        raw_text=SAMPLE_RESUME,
        taxonomy_skills=TAXONOMY_SKILLS,
        job_profiles=DEFAULT_JOB_PROFILES,
    )

    assert len(result.recommended_roles) >= 1
    assert result.recommended_roles[0].match_score >= 30
    assert result.recommended_roles[0].role_name in {"Backend Developer", "Full Stack Developer"}


def test_analyze_resume_detects_missing_skills() -> None:
    parsed = parse_resume_text(SAMPLE_RESUME)
    result = analyze_resume(
        parsed=parsed,
        raw_text=SAMPLE_RESUME,
        taxonomy_skills=TAXONOMY_SKILLS,
        job_profiles=DEFAULT_JOB_PROFILES,
    )

    assert isinstance(result.missing_skills, list)


def test_analyze_resume_generates_feedback() -> None:
    parsed = parse_resume_text(SAMPLE_RESUME)
    result = analyze_resume(
        parsed=parsed,
        raw_text=SAMPLE_RESUME,
        taxonomy_skills=TAXONOMY_SKILLS,
        job_profiles=DEFAULT_JOB_PROFILES,
    )

    assert len(result.strengths) >= 1
    assert isinstance(result.weaknesses, list)
    assert len(result.suggestions) >= 1


def test_analyze_empty_resume_scores_low() -> None:
    parsed = parse_resume_text("")
    result = analyze_resume(
        parsed=parsed,
        raw_text="",
        taxonomy_skills=TAXONOMY_SKILLS,
        job_profiles=DEFAULT_JOB_PROFILES,
    )

    assert result.ats_score < 30
    assert result.completeness_score < 20
    assert result.section_scores.contact_information == 0


def test_keyword_coverage_calculated() -> None:
    parsed = parse_resume_text(SAMPLE_RESUME)
    result = analyze_resume(
        parsed=parsed,
        raw_text=SAMPLE_RESUME,
        taxonomy_skills=TAXONOMY_SKILLS,
        job_profiles=DEFAULT_JOB_PROFILES,
    )

    assert result.keyword_coverage.total_keywords == len(TAXONOMY_SKILLS)
    assert result.keyword_coverage.matched_keywords >= 4
    assert result.keyword_coverage.coverage_percent > 0
