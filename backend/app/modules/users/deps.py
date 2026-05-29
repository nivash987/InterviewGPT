from __future__ import annotations

from fastapi import Depends

from app.modules.users.service import UsersService


def get_users_service() -> UsersService:
    raise NotImplementedError("Users service wiring not implemented yet")


UsersServiceDep = Depends(get_users_service)

