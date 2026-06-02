from __future__ import annotations

import io

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


def _resume_pdf_with_text() -> bytes:
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 500>>stream\n"
        b"BT /F1 10 Tf 50 750 Td (Jane Doe Skills Python FastAPI PostgreSQL React Git REST API) Tj ET\n"
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
        data={"title": "Interview Test Resume"},
    )
    assert response.status_code == 201, response.text
    return response.json()["data"]["id"]


@pytest.mark.asyncio
async def test_interview_full_flow(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    resume_id = await _upload_resume(client, auth_headers)

    await client.post(f"/api/ats/analyze/{resume_id}", headers=auth_headers)

    start = await client.post(
        "/api/interviews/start",
        headers=auth_headers,
        json={
            "resume_id": resume_id,
            "role": "Backend Developer",
            "difficulty": "medium",
            "question_count": 5,
        },
    )
    assert start.status_code == 200, start.text
    session = start.json()["data"]["session"]
    session_id = session["id"]
    questions = session["questions"]
    assert len(questions) == 5
    assert session["status"] == "in_progress"

    for question in questions:
        answer_resp = await client.post(
            f"/api/interviews/{session_id}/answer",
            headers=auth_headers,
            json={
                "question_id": question["id"],
                "answer": (
                    f"I have hands-on experience with {question['category']} work. "
                    "For example, in a recent project I used Python, FastAPI, and PostgreSQL "
                    "to deliver REST APIs with measurable impact on team velocity."
                ),
            },
        )
        assert answer_resp.status_code == 200, answer_resp.text
        assert 0 <= answer_resp.json()["data"]["answer"]["score"] <= 100

    finish = await client.post(f"/api/interviews/{session_id}/finish", headers=auth_headers)
    assert finish.status_code == 200, finish.text
    finish_data = finish.json()["data"]
    assert finish_data["session"]["status"] == "completed"
    assert finish_data["summary"]["total_score"] >= 0
    assert finish_data["summary"]["questions_answered"] == 5

    detail = await client.get(f"/api/interviews/{session_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["summary"] is not None
    assert detail.json()["data"]["analytics"] is not None

    history = await client.get("/api/interviews/history", headers=auth_headers)
    assert history.status_code == 200
    items = history.json()["data"]["items"]
    assert any(item["id"] == session_id for item in items)


@pytest.mark.asyncio
async def test_interview_start_validation(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    response = await client.post(
        "/api/interviews/start",
        headers=auth_headers,
        json={
            "resume_id": "00000000-0000-0000-0000-000000000000",
            "role": "Engineer",
            "difficulty": "easy",
            "question_count": 5,
        },
    )
    assert response.status_code == 404
