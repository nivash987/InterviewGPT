from __future__ import annotations

from fastapi import Depends

from app.modules.agents.service import AgentsService


def get_agents_service() -> AgentsService:
    raise NotImplementedError("Agents service wiring not implemented yet")


AgentsServiceDep = Depends(get_agents_service)

