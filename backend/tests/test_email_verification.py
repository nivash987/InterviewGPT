from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

from app.core.config import Settings, get_settings
from app.core.jwt import JWTService
from app.di.container import get_session_dep
from app.modules.auth.deps import get_auth_service
from app.modules.auth.repository import SqlAlchemyAuthRepository
from app.modules.auth.service import AuthServiceImpl
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class MockEmailSender:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send_verification_email(self, *, to: str, verification_link: str) -> None:
        self.sent.append((to, verification_link))


@pytest.fixture
def verification_settings(monkeypatch) -> Settings:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_REQUIRE_EMAIL_VERIFICATION", "true")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DEBUG", "true")
    monkeypatch.setenv("APP_FRONTEND_URL", "http://localhost:3000")
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture
def mock_email_sender() -> MockEmailSender:
    return MockEmailSender()


def _auth_service_override(
    verification_settings: Settings,
    mock_email_sender: MockEmailSender,
):
    async def override_auth_service(session: AsyncSession = Depends(get_session_dep)):
        return AuthServiceImpl(
            repository=SqlAlchemyAuthRepository(session),
            jwt_service=JWTService(verification_settings),
            settings=verification_settings,
            email_sender=mock_email_sender,
        )

    return override_auth_service


@pytest.mark.asyncio
async def test_register_auto_verifies_and_issues_tokens(
    app,
    client: AsyncClient,
    verification_settings: Settings,
    mock_email_sender: MockEmailSender,
) -> None:
    app.dependency_overrides[get_auth_service] = _auth_service_override(
        verification_settings, mock_email_sender
    )

    email = f"verify-{uuid.uuid4().hex}@example.com"
    password = "SecurePass123!"

    register = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password, "full_name": "Verify User"},
    )
    assert register.status_code == 201, register.text
    body = register.json()["data"]
    assert body["user"]["is_email_verified"] is True
    assert body["tokens"] is not None
    assert body["verification_token"] is None
    assert len(mock_email_sender.sent) == 0

    login = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_verify_email_endpoint_still_works(
    app,
    client: AsyncClient,
    verification_settings: Settings,
    mock_email_sender: MockEmailSender,
) -> None:
    from sqlalchemy import update

    from app.db.models.user import User
    from app.di.container import sessionmaker_provider

    app.dependency_overrides[get_auth_service] = _auth_service_override(
        verification_settings, mock_email_sender
    )

    email = f"manual-{uuid.uuid4().hex}@example.com"
    password = "SecurePass123!"

    register = await client.post(
        "/api/auth/register",
        json={"email": email, "password": password},
    )
    assert register.status_code == 201, register.text

    sm = sessionmaker_provider()
    async with sm() as session:
        await session.execute(update(User).where(User.email == email).values(email_verified_at=None))
        await session.commit()

    resend = await client.post("/api/auth/resend-verification", json={"email": email})
    assert resend.status_code == 200, resend.text
    assert len(mock_email_sender.sent) == 1

    token = mock_email_sender.sent[0][1].split("token=", 1)[1]
    verify = await client.post("/api/auth/verify-email", json={"token": token})
    assert verify.status_code == 200, verify.text

    login = await client.post("/api/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_resend_verification_skips_already_verified_user(
    app,
    client: AsyncClient,
    verification_settings: Settings,
    mock_email_sender: MockEmailSender,
) -> None:
    app.dependency_overrides[get_auth_service] = _auth_service_override(
        verification_settings, mock_email_sender
    )

    email = f"resend-{uuid.uuid4().hex}@example.com"

    await client.post(
        "/api/auth/register",
        json={"email": email, "password": "SecurePass123!"},
    )

    resend = await client.post("/api/auth/resend-verification", json={"email": email})
    assert resend.status_code == 200, resend.text
    assert len(mock_email_sender.sent) == 0

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_debug_verification_endpoint_shows_verified_user(
    app,
    client: AsyncClient,
    verification_settings: Settings,
    mock_email_sender: MockEmailSender,
) -> None:
    app.dependency_overrides[get_auth_service] = _auth_service_override(
        verification_settings, mock_email_sender
    )

    email = f"debug-{uuid.uuid4().hex}@example.com"
    await client.post("/api/auth/register", json={"email": email, "password": "SecurePass123!"})

    debug = await client.get(f"/api/auth/debug-verification/{email}")
    assert debug.status_code == 200, debug.text
    data = debug.json()["data"]
    assert data["email"] == email
    assert data["is_email_verified"] is True
    assert data["verification_url"] is None

    app.dependency_overrides.clear()
