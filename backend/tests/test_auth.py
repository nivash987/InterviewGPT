from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_status(client: AsyncClient) -> None:
    response = await client.get("/api/auth/status")
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True


@pytest.mark.asyncio
async def test_register_then_login(client: AsyncClient) -> None:
    email = f"user-{uuid.uuid4().hex}@example.com"
    password = "SecurePass123!"

    register = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert register.status_code == 201, register.text

    login = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text
    tokens = login.json()["data"]
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"
