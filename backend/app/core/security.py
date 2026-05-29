from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    """Authenticated identity placeholder.

    Actual auth (JWT, sessions, RBAC) will be implemented in the `auth` module.
    """

    user_id: str
    email: str | None = None
    roles: tuple[str, ...] = ()

