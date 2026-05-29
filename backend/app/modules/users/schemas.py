from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class UserPublic(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    is_email_verified: bool = False
    is_active: bool = True
    roles: list[str] = Field(default_factory=list)
    permissions: list[str] = Field(default_factory=list)
    last_login_at: datetime | None = None
    created_at: datetime | None = None
