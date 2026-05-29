from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import PrincipalDep
from app.core.responses import ApiResponse, EmptyData
from app.core.security import Principal
from app.modules.users.deps import UsersServiceDep
from app.modules.users.schemas import UserPublic
from app.modules.users.service import UsersService

router = APIRouter()


@router.get("/status", response_model=ApiResponse[EmptyData])
async def status() -> ApiResponse[EmptyData]:
    return ApiResponse(data=EmptyData())


@router.get("/me", response_model=ApiResponse[UserPublic])
async def get_me(
    principal: Principal = PrincipalDep,
    svc: UsersService = UsersServiceDep,
) -> ApiResponse[UserPublic]:
    user = await svc.get_me(principal_user_id=principal.user_id)
    return ApiResponse(data=user)
