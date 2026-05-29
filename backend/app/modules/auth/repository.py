from __future__ import annotations

from abc import ABC


class AuthRepository(ABC):
    """Auth persistence port (users, sessions, refresh tokens, etc.)."""

