from __future__ import annotations

from fastapi import Depends

from app.modules.coding.service import CodingService


def get_coding_service() -> CodingService:
    raise NotImplementedError("Coding service wiring not implemented yet")


CodingServiceDep = Depends(get_coding_service)

