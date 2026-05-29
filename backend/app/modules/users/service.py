from __future__ import annotations

from abc import ABC, abstractmethod

from app.core.errors import NotFoundError
from app.modules.users.repository import UsersRepository
from app.modules.users.schemas import UserPublic


class UsersService(ABC):
    @abstractmethod
    async def get_me(self, *, principal_user_id: str) -> UserPublic: ...


class UsersServiceImpl(UsersService):
    def __init__(self, *, repository: UsersRepository) -> None:
        self._repository = repository

    async def get_me(self, *, principal_user_id: str) -> UserPublic:
        user = await self._repository.get_public(user_id=principal_user_id)
        if user is None:
            raise NotFoundError("User not found")
        return user
