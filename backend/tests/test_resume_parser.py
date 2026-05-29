from __future__ import annotations

import pytest

from app.modules.resume.parser import parse_resume_text
from app.modules.resume.storage import validate_resume_file


SAMPLE_RESUME = """
Jane Doe
jane.doe@example.com
+1 (555) 123-4567

Skills
Python, FastAPI, PostgreSQL, React

Experience
Senior Software Engineer - Acme Corp
- Built APIs serving 1M requests/day
- Led migration to async Python stack

Software Engineer - Startup Inc
- Developed MVP in 3 months

Projects
InterviewGPT
- AI-powered interview preparation platform

Education
B.S. Computer Science - State University
2018 - 2022
"""


@pytest.mark.parametrize(
    ("filename", "content_type", "size", "expected_ext"),
    [
        ("resume.pdf", "application/pdf", 1024, ".pdf"),
        ("resume.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 2048, ".docx"),
    ],
)
def test_validate_resume_file_accepts_allowed_types(
    filename: str,
    content_type: str,
    size: int,
    expected_ext: str,
) -> None:
    ext = validate_resume_file(
        filename=filename,
        content_type=content_type,
        size_bytes=size,
        max_size_bytes=5 * 1024 * 1024,
    )
    assert ext == expected_ext


def test_validate_resume_file_rejects_unsupported_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        validate_resume_file(
            filename="resume.txt",
            content_type="text/plain",
            size_bytes=100,
            max_size_bytes=5 * 1024 * 1024,
        )


def test_validate_resume_file_rejects_oversized_file() -> None:
    with pytest.raises(ValueError, match="exceeds maximum size"):
        validate_resume_file(
            filename="resume.pdf",
            content_type="application/pdf",
            size_bytes=10 * 1024 * 1024,
            max_size_bytes=5 * 1024 * 1024,
        )


def test_parse_resume_text_extracts_contact_and_sections() -> None:
    parsed = parse_resume_text(SAMPLE_RESUME)

    assert parsed.name == "Jane Doe"
    assert parsed.email == "jane.doe@example.com"
    assert parsed.phone is not None
    assert "Python" in parsed.skills
    assert len(parsed.experience) >= 1
    assert len(parsed.projects) >= 1
    assert len(parsed.education) >= 1
