from __future__ import annotations

from abc import ABC, abstractmethod

from app.modules.users.schemas import UserPublic


class UsersService(ABC):
    @abstractmethod
    async def get_me(self, *, principal_user_id: str) -> UserPublic: ...

