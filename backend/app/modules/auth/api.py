from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import PrincipalDep
from app.core.responses import ApiResponse, EmptyData
from app.core.security import Principal
from app.modules.auth.deps import AuthServiceDep
from app.modules.auth.schemas import (
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPasswordRequest,
    ResendVerificationRequest,
    TokenPair,
    VerifyEmailRequest,
)
from app.modules.auth.service import AuthService

router = APIRouter()


@router.get("/status", response_model=ApiResponse[EmptyData])
async def status() -> ApiResponse[EmptyData]:
    return ApiResponse(data=EmptyData())


@router.post("/register", response_model=ApiResponse[RegisterResponse], status_code=201)
async def register(
    body: RegisterRequest,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[RegisterResponse]:
    result = await svc.register(email=body.email, password=body.password, full_name=body.full_name)
    return ApiResponse(data=result)


@router.post("/login", response_model=ApiResponse[TokenPair])
async def login(
    body: LoginRequest,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[TokenPair]:
    tokens = await svc.login(email=body.email, password=body.password)
    return ApiResponse(data=tokens)


@router.post("/refresh", response_model=ApiResponse[TokenPair])
async def refresh(
    body: RefreshRequest,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[TokenPair]:
    tokens = await svc.refresh(refresh_token=body.refresh_token)
    return ApiResponse(data=tokens)


@router.post("/logout", response_model=ApiResponse[MessageResponse])
async def logout(
    body: LogoutRequest,
    principal: Principal = PrincipalDep,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[MessageResponse]:
    result = await svc.logout(user_id=principal.user_id, refresh_token=body.refresh_token)
    return ApiResponse(data=result)


@router.post("/verify-email", response_model=ApiResponse[MessageResponse])
async def verify_email(
    body: VerifyEmailRequest,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[MessageResponse]:
    result = await svc.verify_email(token=body.token)
    return ApiResponse(data=result)


@router.post("/resend-verification", response_model=ApiResponse[MessageResponse])
async def resend_verification(
    body: ResendVerificationRequest,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[MessageResponse]:
    result = await svc.resend_verification(email=body.email)
    return ApiResponse(data=result)


@router.post("/forgot-password", response_model=ApiResponse[MessageResponse])
async def forgot_password(
    body: ForgotPasswordRequest,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[MessageResponse]:
    result = await svc.forgot_password(email=body.email)
    return ApiResponse(data=result)


@router.post("/reset-password", response_model=ApiResponse[MessageResponse])
async def reset_password(
    body: ResetPasswordRequest,
    svc: AuthService = AuthServiceDep,
) -> ApiResponse[MessageResponse]:
    result = await svc.reset_password(token=body.token, new_password=body.new_password)
    return ApiResponse(data=result)
