from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings, get_settings
from app.db.session import create_engine, create_sessionmaker, get_db_session


@lru_cache
def settings_provider() -> Settings:
    return get_settings()


@lru_cache
def sessionmaker_provider() -> async_sessionmaker:
    settings = settings_provider()
    engine = create_engine(settings)
    return create_sessionmaker(engine)


def get_settings_dep() -> Settings:
    return settings_provider()


def get_sessionmaker_dep() -> async_sessionmaker:
    return sessionmaker_provider()


async def get_session_dep(
    sm: async_sessionmaker = Depends(get_sessionmaker_dep),
) -> AsyncSession:
    async for s in get_db_session(sm):
        return s
    raise RuntimeError("Failed to acquire DB session")

