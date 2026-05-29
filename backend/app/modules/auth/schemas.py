from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=256)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)


class AuthUserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None = None
    is_email_verified: bool
    roles: list[str] = Field(default_factory=list)


class RegisterResponse(BaseModel):
    user: AuthUserResponse
    tokens: TokenPair | None = None
    verification_token: str | None = Field(
        default=None,
        description="Returned in local/dev when email delivery is not configured.",
    )


class MessageResponse(BaseModel):
    message: str


class UserCredentials(BaseModel):
    id: str
    email: str
    password_hash: str | None
    full_name: str | None
    is_active: bool
    email_verified_at: datetime | None
    roles: list[str]
    permissions: list[str]
