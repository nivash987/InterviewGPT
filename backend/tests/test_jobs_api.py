import uuid

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


def _application_payload(**overrides: object) -> dict:
    base = {
        "company_name": "Acme Corp",
        "role_title": "Software Engineer",
        "status": "applied",
        "location": "Remote",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_jobs_status(client: AsyncClient) -> None:
    response = await client.get("/api/jobs/status")
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_jobs_crud_flow(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    create = await client.post("/api/jobs", headers=auth_headers, json=_application_payload())
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["ok"] is True
    application = body["data"]
    application_id = application["id"]
    assert application["company_name"] == "Acme Corp"
    assert application["status"] == "applied"

    listing = await client.get("/api/jobs", headers=auth_headers)
    assert listing.status_code == 200
    items = listing.json()["data"]["items"]
    assert any(item["id"] == application_id for item in items)

    detail = await client.get(f"/api/jobs/{application_id}", headers=auth_headers)
    assert detail.status_code == 200
    detail_data = detail.json()["data"]
    assert len(detail_data["status_history"]) >= 1

    status_update = await client.post(
        f"/api/jobs/{application_id}/status",
        headers=auth_headers,
        json={"status": "screening", "note": "Recruiter call"},
    )
    assert status_update.status_code == 200
    assert status_update.json()["data"]["status"] == "screening"

    timeline = await client.get(f"/api/jobs/{application_id}/timeline", headers=auth_headers)
    assert timeline.status_code == 200
    assert len(timeline.json()["data"]["events"]) >= 2

    note = await client.post(
        f"/api/jobs/{application_id}/notes",
        headers=auth_headers,
        json={"title": "Phone screen", "content": "Positive feedback"},
    )
    assert note.status_code == 201
    note_id = note.json()["data"]["id"]

    reminder = await client.post(
        f"/api/jobs/{application_id}/reminders",
        headers=auth_headers,
        json={"title": "Follow up", "remind_at": "2026-06-10T10:00:00Z"},
    )
    assert reminder.status_code == 201

    analytics = await client.get("/api/jobs/analytics/summary", headers=auth_headers)
    assert analytics.status_code == 200
    summary = analytics.json()["data"]
    assert summary["total_applications"] >= 1

    deleted_note = await client.delete(
        f"/api/jobs/{application_id}/notes/{note_id}",
        headers=auth_headers,
    )
    assert deleted_note.status_code == 200

    deleted = await client.delete(f"/api/jobs/{application_id}", headers=auth_headers)
    assert deleted.status_code == 200

    gone = await client.get(f"/api/jobs/{application_id}", headers=auth_headers)
    assert gone.status_code == 404


@pytest.mark.asyncio
async def test_jobs_requires_auth(client: AsyncClient) -> None:
    response = await client.get("/api/jobs")
    assert response.status_code == 401
