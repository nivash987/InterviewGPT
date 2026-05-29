from __future__ import annotations

import uuid
from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.user import Role, User
from app.modules.users.schemas import UserPublic


class UsersRepository(ABC):
    @abstractmethod
    async def get_public(self, *, user_id: str) -> UserPublic | None: ...


def _to_public(user: User) -> UserPublic:
    roles = [role.name for role in user.roles]
    permissions: set[str] = set()
    for role in user.roles:
        for perm in role.permissions:
            permissions.add(perm.code)
    return UserPublic(
        id=str(user.id),
        email=str(user.email),
        full_name=user.full_name,
        is_email_verified=user.email_verified_at is not None,
        is_active=user.is_active,
        roles=roles,
        permissions=sorted(permissions),
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


class SqlAlchemyUsersRepository(UsersRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_public(self, *, user_id: str) -> UserPublic | None:
        stmt = (
            select(User)
            .where(User.id == uuid.UUID(user_id))
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        result = await self._session.execute(stmt)
        user = result.scalar_one_or_none()
        return _to_public(user) if user else None
