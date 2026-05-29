from __future__ import annotations

from pydantic import BaseModel


class CodingSessionPublic(BaseModel):
    id: str
    language: str

