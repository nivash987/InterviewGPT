from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


SAMPLE_RESUME_TEXT = """
Jane Doe
jane.doe@example.com
+1 (555) 123-4567

Professional Summary
Software engineer with experience in Python and web development.

Skills
Python, FastAPI, PostgreSQL, React, Docker, Git, REST API

Experience
Software Engineer - Acme Corp
- Built REST APIs with Python and FastAPI

Education
B.S. Computer Science - State University
"""


def _resume_pdf_with_text() -> bytes:
    """PDF with embedded text for ATS testing."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 500>>stream\n"
        b"BT /F1 10 Tf 50 750 Td (Jane Doe jane.doe@example.com Skills Python FastAPI PostgreSQL React Git REST API) Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\n"
        b"startxref\n0\n%%EOF"
    )


async def _upload_resume(client: AsyncClient, auth_headers: dict[str, str]) -> str:
    files = {"file": ("resume.pdf", io.BytesIO(_resume_pdf_with_text()), "application/pdf")}
    response = await client.post(
        "/api/resumes/upload",
        headers=auth_headers,
        files=files,
        data={"title": "ATS Test Resume"},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


@pytest.mark.asyncio
async def test_ats_analyze_and_get(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resume_id = await _upload_resume(client, auth_headers)

    analyze = await client.post(f"/api/ats/analyze/{resume_id}", headers=auth_headers)
    assert analyze.status_code == 200, analyze.text
    body = analyze.json()
    assert body["ok"] is True
    data = body["data"]
    assert 0 <= data["ats_score"] <= 100
    assert 0 <= data["completeness_score"] <= 100
    assert "skills_found" in data
    assert "recommended_roles" in data
    assert "section_scores" in data

    latest = await client.get(f"/api/ats/{resume_id}", headers=auth_headers)
    assert latest.status_code == 200
    assert latest.json()["data"]["ats_score"] == data["ats_score"]


@pytest.mark.asyncio
async def test_ats_history(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resume_id = await _upload_resume(client, auth_headers)
    await client.post(f"/api/ats/analyze/{resume_id}", headers=auth_headers)

    history = await client.get("/api/ats/history", headers=auth_headers)
    assert history.status_code == 200
    items = history.json()["data"]["items"]
    assert len(items) >= 1
    assert items[0]["resume_id"] == resume_id


@pytest.mark.asyncio
async def test_ats_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/ats/history")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_ats_get_without_analysis_returns_404(
    client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    resume_id = await _upload_resume(client, auth_headers)
    response = await client.get(f"/api/ats/{resume_id}", headers=auth_headers)
    assert response.status_code == 404
