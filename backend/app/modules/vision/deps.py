from __future__ import annotations

from fastapi import Depends

from app.modules.vision.service import VisionService


def get_vision_service() -> VisionService:
    raise NotImplementedError("Vision service wiring not implemented yet")


VisionServiceDep = Depends(get_vision_service)

