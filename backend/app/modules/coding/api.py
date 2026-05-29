from __future__ import annotations

from fastapi import APIRouter

from app.core.responses import ApiResponse, EmptyData

router = APIRouter()


@router.get("/status", response_model=ApiResponse[EmptyData])
async def status() -> ApiResponse[EmptyData]:
    return ApiResponse(data=EmptyData())

