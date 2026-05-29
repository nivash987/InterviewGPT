from __future__ import annotations

import re
from dataclasses import dataclass

from app.modules.ats.schemas import (
    AtsAnalysisResult,
    KeywordCoverage,
    RecommendedRole,
    SectionScores,
)
from app.modules.resume.schemas import ParsedResumeData

SECTION_WEIGHTS: dict[str, float] = {
    "contact_information": 0.15,
    "summary": 0.10,
    "skills": 0.20,
    "experience": 0.25,
    "education": 0.15,
    "projects": 0.15,
}

SUMMARY_HEADERS = re.compile(
    r"^\s*(summary|professional\s+summary|objective|profile|about\s+me)\s*:?\s*$",
    re.I,
)

SECTION_HEADER_PATTERNS = [
    re.compile(r"^\s*(skills|technical\s+skills)\s*:?\s*$", re.I),
    re.compile(r"^\s*(experience|work\s+experience|employment)\s*:?\s*$", re.I),
    re.compile(r"^\s*(education|academic)\s*:?\s*$", re.I),
    re.compile(r"^\s*(projects|personal\s+projects)\s*:?\s*$", re.I),
    SUMMARY_HEADERS,
]


@dataclass(frozen=True)
class JobProfileData:
    role_name: str
    required_skills: list[str]
    preferred_skills: list[str]


def _normalize_skill(skill: str) -> str:
    return re.sub(r"\s+", " ", skill.strip().lower())


def _normalize_skills(skills: list[str]) -> set[str]:
    return {_normalize_skill(s) for s in skills if s.strip()}


def _score_contact(parsed: ParsedResumeData) -> int:
    score = 0
    if parsed.name:
        score += 34
    if parsed.email:
        score += 33
    if parsed.phone:
        score += 33
    return min(score, 100)


def _has_summary_section(raw_text: str) -> bool:
    for line in raw_text.splitlines():
        if SUMMARY_HEADERS.match(line.strip()):
            return True
    return False


def _score_summary(parsed: ParsedResumeData, raw_text: str) -> int:
    if _has_summary_section(raw_text):
        return 100
    header_lines = raw_text.splitlines()[:12]
    for line in header_lines:
        stripped = line.strip()
        if len(stripped) > 80 and not re.search(r"@|\d{3}[-.\s]?\d{3}", stripped):
            return 70
    return 0


def _score_skills(parsed: ParsedResumeData) -> int:
    count = len(parsed.skills)
    if count == 0:
        return 0
    if count <= 3:
        return 40
    if count <= 7:
        return 70
    if count <= 12:
        return 85
    return 100


def _score_experience(parsed: ParsedResumeData) -> int:
    count = len(parsed.experience)
    if count == 0:
        return 0
    if count == 1:
        desc_len = sum(len(e.description or "") for e in parsed.experience)
        return 60 if desc_len > 50 else 40
    desc_total = sum(len(e.description or "") for e in parsed.experience)
    if desc_total > 200:
        return 100
    return 80


def _score_education(parsed: ParsedResumeData) -> int:
    count = len(parsed.education)
    if count == 0:
        return 0
    if count == 1:
        return 80
    return 100


def _score_projects(parsed: ParsedResumeData) -> int:
    count = len(parsed.projects)
    if count == 0:
        return 0
    if count == 1:
        return 70
    return 100


def _compute_section_scores(parsed: ParsedResumeData, raw_text: str) -> SectionScores:
    return SectionScores(
        contact_information=_score_contact(parsed),
        summary=_score_summary(parsed, raw_text),
        skills=_score_skills(parsed),
        experience=_score_experience(parsed),
        education=_score_education(parsed),
        projects=_score_projects(parsed),
    )


def _compute_completeness(section_scores: SectionScores) -> int:
    weighted = (
        section_scores.contact_information * SECTION_WEIGHTS["contact_information"]
        + section_scores.summary * SECTION_WEIGHTS["summary"]
        + section_scores.skills * SECTION_WEIGHTS["skills"]
        + section_scores.experience * SECTION_WEIGHTS["experience"]
        + section_scores.education * SECTION_WEIGHTS["education"]
        + section_scores.projects * SECTION_WEIGHTS["projects"]
    )
    return round(weighted)


def _detect_formatting_score(raw_text: str) -> int:
    if not raw_text.strip():
        return 0
    headers_found = sum(
        1 for pattern in SECTION_HEADER_PATTERNS if any(pattern.match(ln.strip()) for ln in raw_text.splitlines())
    )
    return min(headers_found * 20, 100)


def _content_length_score(raw_text: str) -> int:
    length = len(raw_text.strip())
    if length < 200:
        return 20
    if length < 500:
        return 60
    if length <= 5000:
        return 100
    if length <= 8000:
        return 80
    return 60


def _extract_skills_from_text(raw_text: str, taxonomy_skills: list[str]) -> list[str]:
    normalized_text = _normalize_skill(raw_text)
    found: list[str] = []
    for skill in taxonomy_skills:
        norm = _normalize_skill(skill)
        if len(norm) < 2:
            continue
        pattern = r"(?<![a-z0-9])" + re.escape(norm) + r"(?![a-z0-9])"
        if re.search(pattern, normalized_text):
            found.append(skill)
    return list(dict.fromkeys(found))


def _merge_resume_skills(parsed: ParsedResumeData, taxonomy_matches: list[str]) -> list[str]:
    parsed_normalized = {_normalize_skill(s): s for s in parsed.skills}
    merged: dict[str, str] = {}
    for skill in taxonomy_matches:
        merged[_normalize_skill(skill)] = skill
    for norm, original in parsed_normalized.items():
        if norm not in merged:
            merged[norm] = original
    return list(merged.values())


def _compute_keyword_coverage(found_skills: list[str], taxonomy_skills: list[str]) -> KeywordCoverage:
    if not taxonomy_skills:
        return KeywordCoverage(matched_keywords=0, total_keywords=0, coverage_percent=0.0)
    found_set = _normalize_skills(found_skills)
    taxonomy_set = _normalize_skills(taxonomy_skills)
    matched = len(found_set & taxonomy_set)
    total = len(taxonomy_set)
    percent = round((matched / total) * 100, 1) if total else 0.0
    return KeywordCoverage(
        matched_keywords=matched,
        total_keywords=total,
        coverage_percent=percent,
    )


def _recommend_roles(
    found_skills: list[str],
    job_profiles: list[JobProfileData],
) -> list[RecommendedRole]:
    found_set = _normalize_skills(found_skills)
    recommendations: list[RecommendedRole] = []

    for profile in job_profiles:
        required = profile.required_skills
        preferred = profile.preferred_skills
        required_norm = _normalize_skills(required)
        preferred_norm = _normalize_skills(preferred)

        matched_required = [s for s in required if _normalize_skill(s) in found_set]
        matched_preferred = [s for s in preferred if _normalize_skill(s) in found_set]
        missing_required = [s for s in required if _normalize_skill(s) not in found_set]

        max_score = len(required_norm) * 2 + len(preferred_norm)
        if max_score == 0:
            continue
        raw_score = len(matched_required) * 2 + len(matched_preferred)
        match_score = round((raw_score / max_score) * 100)

        if match_score >= 30:
            recommendations.append(
                RecommendedRole(
                    role_name=profile.role_name,
                    match_score=match_score,
                    matched_required=matched_required,
                    matched_preferred=matched_preferred,
                    missing_required=missing_required,
                ),
            )

    recommendations.sort(key=lambda r: r.match_score, reverse=True)
    return recommendations[:5]


def _detect_missing_skills(
    found_skills: list[str],
    recommended_roles: list[RecommendedRole],
    job_profiles: list[JobProfileData],
) -> list[str]:
    found_set = _normalize_skills(found_skills)
    missing: list[str] = []

    if recommended_roles:
        top_role = recommended_roles[0].role_name
        for profile in job_profiles:
            if profile.role_name == top_role:
                for skill in profile.required_skills:
                    if _normalize_skill(skill) not in found_set:
                        missing.append(skill)
                break
    elif job_profiles:
        all_required: set[str] = set()
        for profile in job_profiles:
            all_required.update(_normalize_skills(profile.required_skills))
        common_missing = sorted(all_required - found_set)
        missing = common_missing[:10]

    return list(dict.fromkeys(missing))[:15]


def _generate_strengths(section_scores: SectionScores, found_skills: list[str]) -> list[str]:
    strengths: list[str] = []
    if section_scores.contact_information >= 80:
        strengths.append("Complete contact information helps recruiters reach you easily.")
    if section_scores.skills >= 80:
        strengths.append(f"Strong skills section with {len(found_skills)} relevant skills identified.")
    if section_scores.experience >= 80:
        strengths.append("Work experience section is well-developed with detailed entries.")
    if section_scores.education >= 80:
        strengths.append("Education credentials are clearly documented.")
    if section_scores.projects >= 70:
        strengths.append("Projects section demonstrates practical application of skills.")
    if section_scores.summary >= 70:
        strengths.append("Professional summary provides a clear career narrative.")
    if not strengths:
        strengths.append("Resume contains foundational content that can be improved with targeted edits.")
    return strengths


def _generate_weaknesses(section_scores: SectionScores) -> list[str]:
    weaknesses: list[str] = []
    if section_scores.contact_information < 70:
        weaknesses.append("Contact information is incomplete — include name, email, and phone.")
    if section_scores.summary < 50:
        weaknesses.append("Missing or weak professional summary — add a 2–3 sentence overview.")
    if section_scores.skills < 60:
        weaknesses.append("Skills section needs more relevant technical and soft skills.")
    if section_scores.experience < 60:
        weaknesses.append("Experience section lacks sufficient detail or entries.")
    if section_scores.education < 60:
        weaknesses.append("Education section is missing or insufficient.")
    if section_scores.projects < 50:
        weaknesses.append("No projects listed — add personal or professional project work.")
    return weaknesses


def _generate_suggestions(
    section_scores: SectionScores,
    missing_skills: list[str],
    keyword_coverage: KeywordCoverage,
) -> list[str]:
    suggestions: list[str] = []
    if section_scores.summary < 70:
        suggestions.append("Add a Professional Summary section with your role, years of experience, and key strengths.")
    if section_scores.skills < 80:
        suggestions.append("Expand your skills list with industry-standard keywords matching your target roles.")
    if section_scores.experience < 80:
        suggestions.append("Use bullet points with action verbs and quantifiable results in experience entries.")
    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        suggestions.append(f"Consider adding these in-demand skills: {top_missing}.")
    if keyword_coverage.coverage_percent < 40:
        suggestions.append("Increase keyword density by aligning skills with common job descriptions in your field.")
    if section_scores.projects < 60:
        suggestions.append("Include 2–3 projects with technologies used and measurable outcomes.")
    if not suggestions:
        suggestions.append("Fine-tune formatting and ensure consistent section headers for ATS parsers.")
    return suggestions


def analyze_resume(
    *,
    parsed: ParsedResumeData,
    raw_text: str,
    taxonomy_skills: list[str],
    job_profiles: list[JobProfileData],
) -> AtsAnalysisResult:
    section_scores = _compute_section_scores(parsed, raw_text)
    completeness_score = _compute_completeness(section_scores)

    taxonomy_matches = _extract_skills_from_text(raw_text, taxonomy_skills)
    skills_found = _merge_resume_skills(parsed, taxonomy_matches)

    keyword_coverage = _compute_keyword_coverage(skills_found, taxonomy_skills)

    formatting_score = _detect_formatting_score(raw_text)
    length_score = _content_length_score(raw_text)

    ats_score = round(
        completeness_score * 0.60
        + keyword_coverage.coverage_percent * 0.20
        + formatting_score * 0.10
        + length_score * 0.10,
    )
    ats_score = max(0, min(100, ats_score))

    recommended_roles = _recommend_roles(skills_found, job_profiles)
    missing_skills = _detect_missing_skills(skills_found, recommended_roles, job_profiles)

    strengths = _generate_strengths(section_scores, skills_found)
    weaknesses = _generate_weaknesses(section_scores)
    suggestions = _generate_suggestions(section_scores, missing_skills, keyword_coverage)

    return AtsAnalysisResult(
        ats_score=ats_score,
        completeness_score=completeness_score,
        section_scores=section_scores,
        skills_found=skills_found,
        missing_skills=missing_skills,
        keyword_coverage=keyword_coverage,
        strengths=strengths,
        weaknesses=weaknesses,
        suggestions=suggestions,
        recommended_roles=recommended_roles,
    )
