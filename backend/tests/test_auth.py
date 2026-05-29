from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_status(client: AsyncClient) -> None:
    response = await client.get("/api/auth/status")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
