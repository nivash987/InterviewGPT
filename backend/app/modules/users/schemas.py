from __future__ import annotations

from pydantic import BaseModel


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: str | None = None

