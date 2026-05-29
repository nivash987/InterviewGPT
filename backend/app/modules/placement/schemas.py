from __future__ import annotations

from pydantic import BaseModel


class PlacementScorePublic(BaseModel):
    id: str
    score: float

