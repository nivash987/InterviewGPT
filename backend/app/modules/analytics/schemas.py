from __future__ import annotations

from pydantic import BaseModel


class AnalyticsEvent(BaseModel):
    id: str
    event_name: str

