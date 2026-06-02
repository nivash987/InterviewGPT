import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_career_coach_status(client: AsyncClient) -> None:
    response = await client.get("/api/career-coach/status")
    assert response.status_code == 200
    assert response.json()["ok"] is True


@pytest.mark.asyncio
async def test_career_coach_flow(client: AsyncClient, auth_headers: dict[str, str]) -> None:
    goal = await client.post(
        "/api/career-coach/goals",
        headers=auth_headers,
        json={
            "target_role": "Software Engineer",
            "target_timeline_months": 6,
            "description": "Land a full-time SWE role",
        },
    )
    assert goal.status_code == 201, goal.text
    assert goal.json()["data"]["target_role"] == "Software Engineer"

    skill = await client.put(
        "/api/career-coach/skills",
        headers=auth_headers,
        json={"skill_name": "Python", "proficiency_level": "intermediate", "source": "manual"},
    )
    assert skill.status_code == 200

    roadmap = await client.post("/api/career-coach/roadmap/generate", headers=auth_headers)
    assert roadmap.status_code == 201, roadmap.text
    roadmap_data = roadmap.json()["data"]
    assert len(roadmap_data["milestones"]) >= 5
    milestone_id = roadmap_data["milestones"][0]["id"]

    progress = await client.patch(
        f"/api/career-coach/progress/{milestone_id}",
        headers=auth_headers,
        json={"status": "completed", "notes": "Done"},
    )
    assert progress.status_code == 200

    gaps = await client.get("/api/career-coach/skill-gaps", headers=auth_headers)
    assert gaps.status_code == 200
    assert "coverage_percent" in gaps.json()["data"]

    readiness = await client.post("/api/career-coach/readiness/compute", headers=auth_headers)
    assert readiness.status_code == 200
    score = readiness.json()["data"]
    assert 0 <= score["overall_score"] <= 100

    dashboard = await client.get("/api/career-coach/dashboard", headers=auth_headers)
    assert dashboard.status_code == 200
    dash = dashboard.json()["data"]
    assert dash["readiness_score"] is not None
    assert dash["active_goal"] is not None

    weaknesses = await client.get("/api/career-coach/weaknesses", headers=auth_headers)
    assert weaknesses.status_code == 200

    recs = await client.get("/api/career-coach/recommendations", headers=auth_headers)
    assert recs.status_code == 200
