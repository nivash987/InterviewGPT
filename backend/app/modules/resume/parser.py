from __future__ import annotations

import io
import re
from typing import Any

from docx import Document
from pypdf import PdfReader

from app.modules.resume.schemas import (
    ParsedEducation,
    ParsedExperience,
    ParsedProject,
    ParsedResumeData,
)

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}(?:[-.\s]?\d{1,4})?"
)

SECTION_HEADERS = {
    "skills": re.compile(r"^\s*(skills|technical\s+skills|core\s+competencies)\s*:?\s*$", re.I),
    "experience": re.compile(r"^\s*(experience|work\s+experience|employment|professional\s+experience)\s*:?\s*$", re.I),
    "education": re.compile(r"^\s*(education|academic\s+background)\s*:?\s*$", re.I),
    "projects": re.compile(r"^\s*(projects|personal\s+projects|key\s+projects)\s*:?\s*$", re.I),
}


def extract_text_from_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            parts.append(text)
    return "\n".join(parts)


def extract_text_from_docx(content: bytes) -> str:
    document = Document(io.BytesIO(content))
    return "\n".join(paragraph.text for paragraph in document.paragraphs if paragraph.text.strip())


def extract_text(*, content: bytes, mime_type: str) -> str:
    if mime_type == "application/pdf":
        return extract_text_from_pdf(content)
    if mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(content)
    raise ValueError(f"Unsupported MIME type for text extraction: {mime_type}")


def _split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {
        "header": [],
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
    }
    current = "header"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        matched = False
        for key, pattern in SECTION_HEADERS.items():
            if pattern.match(stripped):
                current = key
                matched = True
                break
        if not matched:
            sections[current].append(stripped)

    return sections


def _extract_name(header_lines: list[str], email: str | None, phone: str | None) -> str | None:
    for line in header_lines[:8]:
        lower = line.lower()
        if email and email.lower() in lower:
            continue
        if phone and phone in line:
            continue
        if EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line):
            continue
        if len(line) < 80 and not line.startswith(("-", "•", "*")):
            return line.strip()
    return header_lines[0].strip() if header_lines else None


def _parse_skills(lines: list[str]) -> list[str]:
    skills: list[str] = []
    for line in lines:
        parts = re.split(r"[,;|•·]", line)
        for part in parts:
            skill = part.strip(" -•*")
            if skill and len(skill) < 64:
                skills.append(skill)
    return list(dict.fromkeys(skills))


def _parse_bullet_entries(lines: list[str]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None

    for line in lines:
        if line.startswith(("-", "•", "*")) or re.match(r"^\d+\.", line):
            if current:
                entries.append(current)
            current = {"title": re.sub(r"^[-•*\d.]+\s*", "", line).strip(), "description": ""}
        elif current is not None:
            desc = current.get("description", "")
            current["description"] = f"{desc} {line}".strip() if desc else line
        else:
            if entries:
                last = entries[-1]
                desc = last.get("description", "")
                last["description"] = f"{desc} {line}".strip() if desc else line
            else:
                entries.append({"title": line, "description": ""})

    if current:
        entries.append(current)

    return entries


def parse_resume_text(text: str) -> ParsedResumeData:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.strip() for ln in normalized.split("\n") if ln.strip()]

    email_match = EMAIL_PATTERN.search(normalized)
    email = email_match.group(0) if email_match else None

    phone_match = PHONE_PATTERN.search(normalized)
    phone = phone_match.group(0).strip() if phone_match else None

    sections = _split_sections(lines)
    name = _extract_name(sections["header"], email, phone)

    experience_entries = _parse_bullet_entries(sections["experience"])
    project_entries = _parse_bullet_entries(sections["projects"])
    education_entries = _parse_bullet_entries(sections["education"])

    if not experience_entries and sections["experience"]:
        experience_entries = [{"title": ln, "description": ""} for ln in sections["experience"][:20]]
    if not project_entries and sections["projects"]:
        project_entries = [{"title": ln, "description": ""} for ln in sections["projects"][:20]]
    if not education_entries and sections["education"]:
        education_entries = [{"title": ln, "description": ""} for ln in sections["education"][:10]]

    return ParsedResumeData(
        name=name,
        email=email,
        phone=phone,
        skills=_parse_skills(sections["skills"]),
        projects=[ParsedProject(**e) for e in project_entries],
        experience=[ParsedExperience(**e) for e in experience_entries],
        education=[ParsedEducation(**e) for e in education_entries],
    )
