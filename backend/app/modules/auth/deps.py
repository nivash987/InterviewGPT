from __future__ import annotations

from fastapi import Depends

from app.modules.auth.service import AuthService


def get_auth_service() -> AuthService:
    raise NotImplementedError("Auth service wiring not implemented yet")


AuthServiceDep = Depends(get_auth_service)

