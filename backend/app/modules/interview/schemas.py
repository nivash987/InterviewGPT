from __future__ import annotations

from pydantic import BaseModel


class InterviewPublic(BaseModel):
    id: str
    title: str | None = None

