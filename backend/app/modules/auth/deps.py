from __future__ import annotations

from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.jwt import JWTService
from app.di.container import get_session_dep, get_settings_dep
from app.modules.auth.repository import AuthRepository, SqlAlchemyAuthRepository
from app.modules.auth.service import AuthService, AuthServiceImpl


@lru_cache
def _jwt_service() -> JWTService:
    return JWTService(get_settings())


def get_auth_repository(session: AsyncSession = Depends(get_session_dep)) -> AuthRepository:
    return SqlAlchemyAuthRepository(session)


def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
    settings: Settings = Depends(get_settings_dep),
) -> AuthService:
    return AuthServiceImpl(repository=repository, jwt_service=_jwt_service(), settings=settings)


AuthServiceDep = Depends(get_auth_service)
