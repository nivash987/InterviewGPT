from __future__ import annotations

import random
from dataclasses import dataclass

DIFFICULTIES = ("easy", "medium", "hard")
QUESTION_COUNTS = (5, 10, 15, 20)

BEHAVIORAL_TEMPLATES: dict[str, list[tuple[str, list[str]]]] = {
    "easy": [
        (
            "Tell me about yourself and why you are interested in the {role} role.",
            ["background", "motivation", "role", "skills"],
        ),
        (
            "Describe a time you worked successfully in a team.",
            ["team", "collaboration", "communication", "outcome"],
        ),
    ],
    "medium": [
        (
            "Describe a challenging situation at work and how you resolved it.",
            ["challenge", "action", "result", "learning"],
        ),
        (
            "How do you prioritize tasks when facing multiple deadlines?",
            ["prioritization", "deadline", "planning", "communication"],
        ),
    ],
    "hard": [
        (
            "Tell me about a failure or setback. What did you learn and how did you apply it later?",
            ["failure", "reflection", "improvement", "accountability"],
        ),
        (
            "Describe a situation where you had to influence stakeholders without direct authority.",
            ["influence", "stakeholders", "negotiation", "outcome"],
        ),
    ],
}

ROLE_TEMPLATES: dict[str, list[tuple[str, list[str]]]] = {
    "easy": [
        (
            "What key responsibilities does a {role} typically have?",
            ["responsibilities", "role", "skills", "deliverables"],
        ),
    ],
    "medium": [
        (
            "How would you approach your first 90 days as a {role}?",
            ["onboarding", "goals", "learning", "stakeholders"],
        ),
    ],
    "hard": [
        (
            "What architectural or process decisions would you make as a senior {role}?",
            ["architecture", "trade-offs", "scalability", "leadership"],
        ),
    ],
}

SKILL_TEMPLATES: dict[str, list[tuple[str, list[str]]]] = {
    "easy": [
        ("What is {skill} and when would you use it?", ["definition", "use case", "benefits"]),
        ("Explain {skill} in simple terms for a non-technical audience.", ["explanation", "examples", "clarity"]),
    ],
    "medium": [
        (
            "Describe a project where you used {skill}. What challenges did you face?",
            ["project", "implementation", "challenge", "outcome"],
        ),
        (
            "How does {skill} fit into a modern {role} tech stack?",
            ["integration", "stack", "workflow", "best practices"],
        ),
    ],
    "hard": [
        (
            "Compare {skill} with common alternatives and explain trade-offs in production.",
            ["comparison", "trade-offs", "performance", "production"],
        ),
        (
            "How would you debug and optimize a performance issue related to {skill}?",
            ["debugging", "optimization", "monitoring", "root cause"],
        ),
    ],
}

ATS_GAP_TEMPLATES: dict[str, list[tuple[str, list[str]]]] = {
    "easy": [
        (
            "What is your experience level with {skill}? How are you building this skill?",
            ["experience", "learning", "practice", "goals"],
        ),
    ],
    "medium": [
        (
            "Your resume could be stronger in {skill}. How would you demonstrate competency in an interview?",
            ["competency", "examples", "projects", "certification"],
        ),
    ],
    "hard": [
        (
            "How would you ramp up on {skill} for a {role} position in the first month?",
            ["learning plan", "resources", "milestones", "delivery"],
        ),
    ],
}

EXPERIENCE_TEMPLATES: dict[str, list[tuple[str, list[str]]]] = {
    "easy": [
        (
            "Walk me through your most recent role and primary contributions.",
            ["role", "contributions", "technologies", "impact"],
        ),
    ],
    "medium": [
        (
            "Describe a technical decision you made in a past project and its impact.",
            ["decision", "rationale", "impact", "metrics"],
        ),
    ],
    "hard": [
        (
            "How have you handled production incidents or critical bugs in your experience?",
            ["incident", "response", "postmortem", "prevention"],
        ),
    ],
}


@dataclass(frozen=True)
class GeneratedQuestion:
    question: str
    category: str
    difficulty: str
    expected_keywords: list[str]


def _normalize_skill(skill: str) -> str:
    return skill.strip()


def _pick_templates(
    pool: dict[str, list[tuple[str, list[str]]]],
    difficulty: str,
) -> list[tuple[str, list[str]]]:
    return pool.get(difficulty, pool["medium"])


def _generate_skill_questions(
    skills: list[str],
    *,
    role: str,
    difficulty: str,
    limit: int,
) -> list[GeneratedQuestion]:
    if not skills or limit <= 0:
        return []

    templates = _pick_templates(SKILL_TEMPLATES, difficulty)
    questions: list[GeneratedQuestion] = []
    shuffled = list(skills)
    random.shuffle(shuffled)

    for skill in shuffled:
        if len(questions) >= limit:
            break
        template, keywords = random.choice(templates)
        normalized = _normalize_skill(skill)
        questions.append(
            GeneratedQuestion(
                question=template.format(skill=normalized, role=role),
                category="Technical",
                difficulty=difficulty,
                expected_keywords=[normalized.lower(), *[k.lower() for k in keywords]],
            )
        )
    return questions


def _generate_ats_gap_questions(
    missing_skills: list[str],
    *,
    role: str,
    difficulty: str,
    limit: int,
) -> list[GeneratedQuestion]:
    if not missing_skills or limit <= 0:
        return []

    templates = _pick_templates(ATS_GAP_TEMPLATES, difficulty)
    questions: list[GeneratedQuestion] = []
    shuffled = list(missing_skills)
    random.shuffle(shuffled)

    for skill in shuffled:
        if len(questions) >= limit:
            break
        template, keywords = random.choice(templates)
        normalized = _normalize_skill(skill)
        questions.append(
            GeneratedQuestion(
                question=template.format(skill=normalized, role=role),
                category="Skill Gap",
                difficulty=difficulty,
                expected_keywords=[normalized.lower(), *[k.lower() for k in keywords]],
            )
        )
    return questions


def _generate_category_questions(
    pool: dict[str, list[tuple[str, list[str]]]],
    *,
    role: str,
    difficulty: str,
    category: str,
    count: int,
) -> list[GeneratedQuestion]:
    if count <= 0:
        return []

    templates = _pick_templates(pool, difficulty)
    questions: list[GeneratedQuestion] = []
    for _ in range(count):
        template, keywords = random.choice(templates)
        questions.append(
            GeneratedQuestion(
                question=template.format(role=role),
                category=category,
                difficulty=difficulty,
                expected_keywords=[k.lower() for k in keywords],
            )
        )
    return questions


def generate_interview_questions(
    *,
    role: str,
    difficulty: str,
    question_count: int,
    resume_skills: list[str],
    ats_skills_found: list[str],
    ats_missing_skills: list[str],
    experience_bullets: list[str],
) -> list[GeneratedQuestion]:
    """Rule-based question generation from resume, ATS, and role context."""
    difficulty = difficulty.lower()
    if difficulty not in DIFFICULTIES:
        difficulty = "medium"
    if question_count not in QUESTION_COUNTS:
        question_count = 10

    merged_skills = list(
        dict.fromkeys(
            [_normalize_skill(s) for s in resume_skills + ats_skills_found if s and s.strip()]
        )
    )
    missing = [_normalize_skill(s) for s in ats_missing_skills if s and s.strip()]

    technical_slots = max(1, int(question_count * 0.45))
    behavioral_slots = max(1, int(question_count * 0.20))
    role_slots = max(1, int(question_count * 0.15))
    gap_slots = max(0, int(question_count * 0.10)) if missing else 0
    experience_slots = max(0, question_count - technical_slots - behavioral_slots - role_slots - gap_slots)

    questions: list[GeneratedQuestion] = []
    questions.extend(
        _generate_skill_questions(
            merged_skills,
            role=role,
            difficulty=difficulty,
            limit=technical_slots,
        )
    )
    questions.extend(
        _generate_ats_gap_questions(
            missing,
            role=role,
            difficulty=difficulty,
            limit=gap_slots,
        )
    )
    questions.extend(
        _generate_category_questions(
            BEHAVIORAL_TEMPLATES,
            role=role,
            difficulty=difficulty,
            category="Behavioral",
            count=behavioral_slots,
        )
    )
    questions.extend(
        _generate_category_questions(
            ROLE_TEMPLATES,
            role=role,
            difficulty=difficulty,
            category="Role Fit",
            count=role_slots,
        )
    )
    if experience_bullets or experience_slots > 0:
        questions.extend(
            _generate_category_questions(
                EXPERIENCE_TEMPLATES,
                role=role,
                difficulty=difficulty,
                category="Experience",
                count=experience_slots,
            )
        )

    # Fill remaining with technical from merged skills or generic fallbacks
    while len(questions) < question_count:
        if merged_skills:
            extra = _generate_skill_questions(
                merged_skills,
                role=role,
                difficulty=difficulty,
                limit=1,
            )
            if extra:
                questions.append(extra[0])
                continue
        questions.append(
            GeneratedQuestion(
                question=f"Why are you a good fit for the {role} position?",
                category="Role Fit",
                difficulty=difficulty,
                expected_keywords=["fit", "skills", "experience", "motivation", role.lower()],
            )
        )

    random.shuffle(questions)
    return questions[:question_count]
