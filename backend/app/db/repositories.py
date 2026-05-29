from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

TEntity = TypeVar("TEntity")
TId = TypeVar("TId")


class Repository(ABC, Generic[TEntity, TId]):
    """Repository port (interface).

    Concrete implementations will live in each module's infrastructure layer later.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @abstractmethod
    async def get(self, entity_id: TId) -> TEntity | None: ...

    @abstractmethod
    async def add(self, entity: TEntity) -> None: ...

