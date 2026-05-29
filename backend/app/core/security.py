from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Principal:
    """Authenticated identity extracted from a verified JWT access token."""

    user_id: str
    email: str | None = None
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()

    def has_role(self, role: str) -> bool:
        return role in self.roles

    def has_any_role(self, *roles: str) -> bool:
        return any(role in self.roles for role in roles)

    def has_permission(self, permission: str) -> bool:
        return permission in self.permissions

    def has_any_permission(self, *permissions: str) -> bool:
        return any(perm in self.permissions for perm in permissions)

