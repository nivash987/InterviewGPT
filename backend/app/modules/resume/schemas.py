from __future__ import annotations

from pydantic import BaseModel


class ResumePublic(BaseModel):
    content_item_id: str
    title: str | None = None

