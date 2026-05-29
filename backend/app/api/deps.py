from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, Request, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.errors import ForbiddenError, UnauthorizedError
from app.core.jwt import JWTService
from app.core.security import Principal
from app.modules.auth.deps import _jwt_service

_bearer_scheme = HTTPBearer(auto_error=False)


def get_request_id(request: Request) -> str | None:
    return request.state.request_id if hasattr(request.state, "request_id") else None


async def get_principal(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
    jwt_service: JWTService = Depends(_jwt_service),
) -> Principal:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing or invalid authorization header", code="missing_token")

    payload = jwt_service.decode_token(credentials.credentials)
    if payload.token_type != "access":
        raise UnauthorizedError("Invalid access token", code="invalid_token")

    return Principal(
        user_id=payload.sub,
        email=payload.email,
        roles=payload.roles,
        permissions=payload.permissions,
    )


PrincipalDep = Depends(get_principal)


async def get_optional_principal(
    credentials: HTTPAuthorizationCredentials | None = Security(_bearer_scheme),
    jwt_service: JWTService = Depends(_jwt_service),
) -> Principal | None:
    if credentials is None or credentials.scheme.lower() != "bearer":
        return None
    try:
        payload = jwt_service.decode_token(credentials.credentials)
        if payload.token_type != "access":
            return None
        return Principal(
            user_id=payload.sub,
            email=payload.email,
            roles=payload.roles,
            permissions=payload.permissions,
        )
    except UnauthorizedError:
        return None


OptionalPrincipalDep = Depends(get_optional_principal)


def require_roles(*roles: str) -> Callable[..., Any]:
    async def _dependency(principal: Principal = PrincipalDep) -> Principal:
        if not principal.has_any_role(*roles):
            raise ForbiddenError("Insufficient role privileges", code="forbidden_role")
        return principal

    return _dependency


def require_permissions(*permissions: str) -> Callable[..., Any]:
    async def _dependency(principal: Principal = PrincipalDep) -> Principal:
        if not principal.has_any_permission(*permissions):
            raise ForbiddenError("Insufficient permissions", code="forbidden_permission")
        return principal

    return _dependency
