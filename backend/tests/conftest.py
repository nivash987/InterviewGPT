from __future__ import annotations

import asyncio
import sys
import uuid
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.db.models.resume import Resume, ResumeVersion
from app.main import create_app
from app.modules.resume.service import ResumeServiceImpl
from app.modules.resume.storage import LocalResumeStorage

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture
def app():
    get_settings.cache_clear()
    return create_app()


@pytest_asyncio.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict[str, str]:
    email = f"resume-test-{uuid.uuid4().hex}@example.com"
    password = "SecurePass123!"

    register = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "Resume Tester"},
    )
    assert register.status_code == 201, register.text

    login = await client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200, login.text
    token = login.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def resume_settings(tmp_path) -> Settings:
    return Settings(
        database_url="postgresql+psycopg://postgres:postgres@localhost:5432/interviewgpt",
        resume_upload_dir=str(tmp_path / "uploads"),
        resume_max_file_size_bytes=5 * 1024 * 1024,
    )


@pytest.fixture
def resume_storage(resume_settings: Settings) -> LocalResumeStorage:
    return LocalResumeStorage(resume_settings)
