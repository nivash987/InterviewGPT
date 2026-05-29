from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import PrincipalDep, require_permissions
from app.core.responses import ApiResponse
from app.core.security import Principal

router = APIRouter()


class AdminStatusResponse(BaseModel):
    message: str
    admin_user_id: str


@router.get(
    "/status",
    response_model=ApiResponse[AdminStatusResponse],
    dependencies=[Depends(require_permissions("admin:access"))],
)
async def admin_status(principal: Principal = PrincipalDep) -> ApiResponse[AdminStatusResponse]:
    return ApiResponse(
        data=AdminStatusResponse(
            message="Admin access granted",
            admin_user_id=principal.user_id,
        )
    )
