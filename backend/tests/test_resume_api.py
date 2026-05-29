import io
import uuid

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


def _minimal_pdf() -> bytes:
    """Minimal valid PDF for upload tests."""
    return (
        b"%PDF-1.4\n"
        b"1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        b"2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        b"3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R>>endobj\n"
        b"4 0 obj<</Length 44>>stream\n"
        b"BT /F1 12 Tf 100 700 Td (Jane Doe) Tj ET\n"
        b"endstream\nendobj\n"
        b"xref\n0 5\n0000000000 65535 f \n"
        b"trailer<</Size 5/Root 1 0 R>>\n"
        b"startxref\n0\n%%EOF"
    )


@pytest.mark.asyncio
async def test_resumes_status(client: AsyncClient) -> None:
    response = await client.get("/api/resumes/status")
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_upload_list_get_delete_resume(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    pdf_content = _minimal_pdf()
    files = {"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

    upload = await client.post(
        "/api/resumes/upload",
        headers=auth_headers,
        files=files,
        data={"title": "My Resume"},
    )
    assert upload.status_code == 201, upload.text
    body = upload.json()
    assert body["ok"] is True
    resume = body["data"]
    resume_id = resume["id"]
    assert resume["title"] == "My Resume"
    assert resume["current_version"] is not None
    assert resume["version_count"] == 1

    listing = await client.get("/api/resumes", headers=auth_headers)
    assert listing.status_code == 200
    items = listing.json()["data"]["items"]
    assert any(item["id"] == resume_id for item in items)

    detail = await client.get(f"/api/resumes/{resume_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["data"]["id"] == resume_id

    history = await client.get(f"/api/resumes/{resume_id}/history", headers=auth_headers)
    assert history.status_code == 200
    versions = history.json()["data"]["versions"]
    assert len(versions) == 1

    deleted = await client.delete(f"/api/resumes/{resume_id}", headers=auth_headers)
    assert deleted.status_code == 200

    gone = await client.get(f"/api/resumes/{resume_id}", headers=auth_headers)
    assert gone.status_code == 404


@pytest.mark.asyncio
async def test_replace_resume_creates_new_version(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    pdf_content = _minimal_pdf()
    files = {"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

    upload = await client.post("/api/resumes/upload", headers=auth_headers, files=files)
    assert upload.status_code == 201
    resume_id = upload.json()["data"]["id"]

    replace_files = {"file": ("resume-v2.pdf", io.BytesIO(pdf_content), "application/pdf")}
    replaced = await client.put(
        f"/api/resumes/{resume_id}/replace",
        headers=auth_headers,
        files=replace_files,
    )
    assert replaced.status_code == 200, replaced.text
    assert replaced.json()["data"]["version_count"] == 2

    history = await client.get(f"/api/resumes/{resume_id}/history", headers=auth_headers)
    assert len(history.json()["data"]["versions"]) == 2


@pytest.mark.asyncio
async def test_resume_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/resumes")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resume_ownership_enforced(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    pdf_content = _minimal_pdf()
    files = {"file": ("resume.pdf", io.BytesIO(pdf_content), "application/pdf")}

    upload = await client.post("/api/resumes/upload", headers=auth_headers, files=files)
    resume_id = upload.json()["data"]["id"]

    other_email = f"other-{__import__('uuid').uuid4().hex}@example.com"
    await client.post(
        "/api/auth/register",
        json={"email": other_email, "password": "SecurePass123!", "full_name": "Other"},
    )
    other_login = await client.post(
        "/api/auth/login",
        json={"email": other_email, "password": "SecurePass123!"},
    )
    other_token = other_login.json()["data"]["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    forbidden = await client.get(f"/api/resumes/{resume_id}", headers=other_headers)
    assert forbidden.status_code == 404


@pytest.mark.asyncio
async def test_upload_rejects_invalid_file_type(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    files = {"file": ("notes.txt", io.BytesIO(b"hello"), "text/plain")}
    response = await client.post("/api/resumes/upload", headers=auth_headers, files=files)
    assert response.status_code == 400
