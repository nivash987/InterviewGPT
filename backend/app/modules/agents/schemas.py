from __future__ import annotations

from pydantic import BaseModel


class AgentLogEvent(BaseModel):
    id: str
    agent_name: str
    event_type: str

