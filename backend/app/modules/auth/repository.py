from __future__ import annotations

import hashlib
import secrets
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.user import (
    EmailVerificationToken,
    PasswordResetToken,
    Permission,
    RefreshToken,
    Role,
    User,
    UserRole,
)
from app.modules.auth.schemas import UserCredentials


class AuthRepository(ABC):
    """Auth persistence port (users, sessions, refresh tokens, etc.)."""

    @abstractmethod
    async def get_user_by_email(self, *, email: str) -> UserCredentials | None: ...

    @abstractmethod
    async def get_user_by_id(self, *, user_id: str) -> UserCredentials | None: ...

    @abstractmethod
    async def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str | None,
        role_name: str = "user",
    ) -> UserCredentials: ...

    @abstractmethod
    async def update_password(self, *, user_id: str, password_hash: str) -> None: ...

    @abstractmethod
    async def mark_email_verified(self, *, user_id: str) -> None: ...

    @abstractmethod
    async def update_last_login(self, *, user_id: str) -> None: ...

    @abstractmethod
    async def store_refresh_token(self, *, user_id: str, jti: str, expires_at: datetime) -> None: ...

    @abstractmethod
    async def get_refresh_token(self, *, jti: str) -> RefreshToken | None: ...

    @abstractmethod
    async def revoke_refresh_token(self, *, jti: str) -> None: ...

    @abstractmethod
    async def revoke_all_refresh_tokens(self, *, user_id: str) -> None: ...

    @abstractmethod
    async def create_email_verification_token(self, *, user_id: str, expires_at: datetime) -> str: ...

    @abstractmethod
    async def consume_email_verification_token(self, *, raw_token: str) -> str | None: ...

    @abstractmethod
    async def create_password_reset_token(self, *, user_id: str, expires_at: datetime) -> str: ...

    @abstractmethod
    async def consume_password_reset_token(self, *, raw_token: str) -> str | None: ...


def _hash_opaque_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def _to_credentials(user: User) -> UserCredentials:
    roles = [role.name for role in user.roles]
    permissions: set[str] = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.code)
    return UserCredentials(
        id=str(user.id),
        email=str(user.email),
        password_hash=user.password_hash,
        full_name=user.full_name,
        is_active=user.is_active,
        email_verified_at=user.email_verified_at,
        roles=roles,
        permissions=sorted(permissions),
    )


class SqlAlchemyAuthRepository(AuthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _load_user_by_email(self, email: str) -> User | None:
        stmt = (
            select(User)
            .where(User.email == email)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def _load_user_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, *, email: str) -> UserCredentials | None:
        user = await self._load_user_by_email(email)
        return _to_credentials(user) if user else None

    async def get_user_by_id(self, *, user_id: str) -> UserCredentials | None:
        user = await self._load_user_by_id(uuid.UUID(user_id))
        return _to_credentials(user) if user else None

    async def create_user(
        self,
        *,
        email: str,
        password_hash: str,
        full_name: str | None,
        role_name: str = "user",
    ) -> UserCredentials:
        role_stmt = select(Role).where(Role.name == role_name)
        role_result = await self._session.execute(role_stmt)
        role = role_result.scalar_one()

        user = User(email=email, password_hash=password_hash, full_name=full_name)
        self._session.add(user)
        await self._session.flush()

        self._session.add(UserRole(user_id=user.id, role_id=role.id))
        await self._session.flush()

        loaded = await self._load_user_by_id(user.id)
        assert loaded is not None
        return _to_credentials(loaded)

    async def update_password(self, *, user_id: str, password_hash: str) -> None:
        stmt = update(User).where(User.id == uuid.UUID(user_id)).values(password_hash=password_hash)
        await self._session.execute(stmt)

    async def mark_email_verified(self, *, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        stmt = update(User).where(User.id == uuid.UUID(user_id)).values(email_verified_at=now)
        await self._session.execute(stmt)

    async def update_last_login(self, *, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        stmt = update(User).where(User.id == uuid.UUID(user_id)).values(last_login_at=now)
        await self._session.execute(stmt)

    async def store_refresh_token(self, *, user_id: str, jti: str, expires_at: datetime) -> None:
        token = RefreshToken(user_id=uuid.UUID(user_id), jti=jti, expires_at=expires_at)
        self._session.add(token)

    async def get_refresh_token(self, *, jti: str) -> RefreshToken | None:
        stmt = select(RefreshToken).where(RefreshToken.jti == jti)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, *, jti: str) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.jti == jti, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self._session.execute(stmt)

    async def revoke_all_refresh_tokens(self, *, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == uuid.UUID(user_id), RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self._session.execute(stmt)

    async def create_email_verification_token(self, *, user_id: str, expires_at: datetime) -> str:
        raw_token = secrets.token_urlsafe(32)
        token = EmailVerificationToken(
            user_id=uuid.UUID(user_id),
            token_hash=_hash_opaque_token(raw_token),
            expires_at=expires_at,
        )
        self._session.add(token)
        return raw_token

    async def consume_email_verification_token(self, *, raw_token: str) -> str | None:
        token_hash = _hash_opaque_token(raw_token)
        now = datetime.now(timezone.utc)
        stmt = select(EmailVerificationToken).where(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.expires_at > now,
        )
        result = await self._session.execute(stmt)
        token = result.scalar_one_or_none()
        if token is None:
            return None
        token.used_at = now
        return str(token.user_id)

    async def create_password_reset_token(self, *, user_id: str, expires_at: datetime) -> str:
        raw_token = secrets.token_urlsafe(32)
        token = PasswordResetToken(
            user_id=uuid.UUID(user_id),
            token_hash=_hash_opaque_token(raw_token),
            expires_at=expires_at,
        )
        self._session.add(token)
        return raw_token

    async def consume_password_reset_token(self, *, raw_token: str) -> str | None:
        token_hash = _hash_opaque_token(raw_token)
        now = datetime.now(timezone.utc)
        stmt = select(PasswordResetToken).where(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        result = await self._session.execute(stmt)
        token = result.scalar_one_or_none()
        if token is None:
            return None
        token.used_at = now
        return str(token.user_id)
