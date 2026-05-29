from __future__ import annotations

from abc import ABC, abstractmethod

from app.modules.auth.schemas import TokenPair


class AuthService(ABC):
    @abstractmethod
    async def login(self, *, email: str, password: str) -> TokenPair: ...

    @abstractmethod
    async def refresh(self, *, refresh_token: str) -> TokenPair: ...

