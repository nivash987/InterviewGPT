from __future__ import annotations

from abc import ABC, abstractmethod

from app.modules.users.schemas import UserPublic


class UsersRepository(ABC):
    @abstractmethod
    async def get_public(self, *, user_id: str) -> UserPublic | None: ...

