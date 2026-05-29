from __future__ import annotations

from pydantic import BaseModel


class VisionSessionPublic(BaseModel):
    id: str
    provider: str | None = None

