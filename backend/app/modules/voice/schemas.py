from __future__ import annotations

from pydantic import BaseModel


class VoiceSessionPublic(BaseModel):
    id: str
    provider: str | None = None

