from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.di.container import get_session_dep
from app.modules.users.repository import SqlAlchemyUsersRepository, UsersRepository
from app.modules.users.service import UsersService, UsersServiceImpl


def get_users_repository(session: AsyncSession = Depends(get_session_dep)) -> UsersRepository:
    return SqlAlchemyUsersRepository(session)


def get_users_service(repository: UsersRepository = Depends(get_users_repository)) -> UsersService:
    return UsersServiceImpl(repository=repository)


UsersServiceDep = Depends(get_users_service)
