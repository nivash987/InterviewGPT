from __future__ import annotations

from fastapi import Depends

from app.modules.placement.service import PlacementService


def get_placement_service() -> PlacementService:
    raise NotImplementedError("Placement service wiring not implemented yet")


PlacementServiceDep = Depends(get_placement_service)

