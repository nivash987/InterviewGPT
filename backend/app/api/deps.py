from __future__ import annotations

from fastapi import Depends, Request

from app.core.security import Principal


def get_request_id(request: Request) -> str | None:
    return request.state.request_id if hasattr(request.state, "request_id") else None


def get_principal() -> Principal:
    """Authentication dependency placeholder.

    Later this will extract/verify JWT or session and return the authenticated principal.
    """

    raise NotImplementedError("Auth not implemented yet")


PrincipalDep = Depends(get_principal)

