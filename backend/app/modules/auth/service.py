from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone

from app.core.config import Settings
from app.core.email import EmailSender, create_email_sender
from app.core.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError
from app.core.jwt import JWTService
from app.core.logging import get_logger
from app.core.password import hash_password, verify_password
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import (
    AuthUserResponse,
    DebugVerificationResponse,
    MessageResponse,
    RegisterResponse,
    TokenPair,
    UserCredentials,
)

log = get_logger(__name__)


class AuthService(ABC):
    @abstractmethod
    async def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None,
    ) -> RegisterResponse: ...

    @abstractmethod
    async def login(self, *, email: str, password: str) -> TokenPair: ...

    @abstractmethod
    async def refresh(self, *, refresh_token: str) -> TokenPair: ...

    @abstractmethod
    async def logout(self, *, user_id: str, refresh_token: str | None) -> MessageResponse: ...

    @abstractmethod
    async def verify_email(self, *, token: str) -> MessageResponse: ...

    @abstractmethod
    async def resend_verification(self, *, email: str) -> MessageResponse: ...

    @abstractmethod
    async def debug_verification(self, *, email: str) -> DebugVerificationResponse: ...

    @abstractmethod
    async def forgot_password(self, *, email: str) -> MessageResponse: ...

    @abstractmethod
    async def reset_password(self, *, token: str, new_password: str) -> MessageResponse: ...


def _auth_user(user: UserCredentials) -> AuthUserResponse:
    return AuthUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_email_verified=user.email_verified_at is not None,
        roles=user.roles,
    )


class AuthServiceImpl(AuthService):
    def __init__(
        self,
        *,
        repository: AuthRepository,
        jwt_service: JWTService,
        settings: Settings,
        email_sender: EmailSender | None = None,
    ) -> None:
        self._repository = repository
        self._jwt = jwt_service
        self._settings = settings
        self._email_sender = email_sender or create_email_sender(settings)

    async def _issue_tokens(self, user: UserCredentials) -> TokenPair:
        access_token = self._jwt.create_access_token(
            user_id=user.id,
            email=user.email,
            roles=tuple(user.roles),
            permissions=tuple(user.permissions),
        )
        refresh_token, jti, expires_at = self._jwt.create_refresh_token(user_id=user.id)
        await self._repository.store_refresh_token(user_id=user.id, jti=jti, expires_at=expires_at)
        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    def _ensure_active(self, user: UserCredentials) -> None:
        if not user.is_active:
            raise ForbiddenError("Account is deactivated", code="account_inactive")

    def _ensure_email_verified_if_required(self, user: UserCredentials) -> None:
        if self._settings.require_email_verification and user.email_verified_at is None:
            raise ForbiddenError("Email address is not verified", code="email_not_verified")

    def _verification_link(self, token: str) -> str:
        base = str(self._settings.frontend_url) if self._settings.frontend_url else "http://localhost:3000"
        return f"{base.rstrip('/')}/verify-email?token={token}"

    async def _create_and_send_verification_token(self, *, user: UserCredentials) -> str:
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=self._settings.email_verification_expire_seconds
        )
        invalidated = await self._repository.invalidate_email_verification_tokens(user_id=user.id)
        if invalidated:
            log.info(
                "verification_tokens_invalidated",
                extra={"user_id": user.id, "email": user.email, "count": invalidated},
            )

        verification_token = await self._repository.create_email_verification_token(
            user_id=user.id,
            expires_at=expires_at,
        )
        log.info(
            "verification_token_created",
            extra={
                "user_id": user.id,
                "email": user.email,
                "expires_at": expires_at.isoformat(),
            },
        )

        verification_link = self._verification_link(verification_token)
        try:
            await self._email_sender.send_verification_email(to=user.email, verification_link=verification_link)
            log.info(
                "verification_email_sent",
                extra={"user_id": user.id, "email": user.email, "verification_link": verification_link},
            )
        except Exception as exc:
            log.error(
                "verification_email_send_failed",
                extra={
                    "user_id": user.id,
                    "email": user.email,
                    "verification_link": verification_link,
                    "error": repr(exc),
                },
            )

        return verification_token

    async def register(
        self,
        *,
        email: str,
        password: str,
        full_name: str | None,
    ) -> RegisterResponse:
        existing = await self._repository.get_user_by_email(email=email)
        if existing is not None:
            raise ConflictError("Email already registered", code="email_taken")

        user = await self._repository.create_user(
            email=email,
            password_hash=hash_password(password),
            full_name=full_name,
        )

        await self._repository.mark_email_verified(user_id=user.id)
        user = await self._repository.get_user_by_id(user_id=user.id)
        assert user is not None
        log.info("user_auto_verified_on_register", extra={"user_id": user.id, "email": user.email})

        tokens = await self._issue_tokens(user)

        return RegisterResponse(
            user=_auth_user(user),
            tokens=tokens,
            verification_token=None,
        )

    async def login(self, *, email: str, password: str) -> TokenPair:
        user = await self._repository.get_user_by_email(email=email)
        if user is None or user.password_hash is None:
            raise UnauthorizedError("Invalid email or password", code="invalid_credentials")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedError("Invalid email or password", code="invalid_credentials")

        self._ensure_active(user)
        self._ensure_email_verified_if_required(user)

        await self._repository.update_last_login(user_id=user.id)
        return await self._issue_tokens(user)

    async def refresh(self, *, refresh_token: str) -> TokenPair:
        payload = self._jwt.decode_token(refresh_token)
        if payload.token_type != "refresh" or payload.jti is None:
            raise UnauthorizedError("Invalid refresh token", code="invalid_token")

        stored = await self._repository.get_refresh_token(jti=payload.jti)
        now = datetime.now(timezone.utc)
        if stored is None or stored.revoked_at is not None or stored.expires_at <= now:
            raise UnauthorizedError("Refresh token is invalid or expired", code="invalid_token")

        user = await self._repository.get_user_by_id(user_id=payload.sub)
        if user is None:
            raise UnauthorizedError("User not found", code="invalid_token")

        self._ensure_active(user)
        self._ensure_email_verified_if_required(user)

        await self._repository.revoke_refresh_token(jti=payload.jti)
        return await self._issue_tokens(user)

    async def logout(self, *, user_id: str, refresh_token: str | None) -> MessageResponse:
        if refresh_token:
            try:
                payload = self._jwt.decode_token(refresh_token)
                if payload.token_type == "refresh" and payload.jti:
                    await self._repository.revoke_refresh_token(jti=payload.jti)
            except UnauthorizedError:
                pass
        else:
            await self._repository.revoke_all_refresh_tokens(user_id=user_id)
        return MessageResponse(message="Logged out successfully")

    async def verify_email(self, *, token: str) -> MessageResponse:
        log.info("verification_token_submitted")
        user_id = await self._repository.consume_email_verification_token(raw_token=token)
        if user_id is None:
            log.warning("verification_token_invalid_or_expired")
            raise UnauthorizedError("Invalid or expired verification token", code="invalid_token")

        await self._repository.mark_email_verified(user_id=user_id)
        log.info("user_email_verified", extra={"user_id": user_id})
        return MessageResponse(message="Email verified successfully")

    async def resend_verification(self, *, email: str) -> MessageResponse:
        user = await self._repository.get_user_by_email(email=email)
        if user is None:
            return MessageResponse(message="If the account exists, a verification email has been sent")

        if user.email_verified_at is not None:
            return MessageResponse(message="If the account exists, a verification email has been sent")

        await self._create_and_send_verification_token(user=user)
        return MessageResponse(message="If the account exists, a verification email has been sent")

    async def debug_verification(self, *, email: str) -> DebugVerificationResponse:
        user = await self._repository.get_user_by_email(email=email)
        if user is None:
            raise NotFoundError("User not found", code="user_not_found")

        is_verified = user.email_verified_at is not None
        active_token = await self._repository.get_active_email_verification_token(user_id=user.id)
        verification_url: str | None = None
        token_expires_at = active_token.expires_at if active_token else None

        if not is_verified:
            debug_token = await self._create_and_send_verification_token(user=user)
            verification_url = self._verification_link(debug_token)
            token_expires_at = datetime.now(timezone.utc) + timedelta(
                seconds=self._settings.email_verification_expire_seconds
            )

        return DebugVerificationResponse(
            user_id=user.id,
            email=user.email,
            is_email_verified=is_verified,
            verification_token_exists=active_token is not None or verification_url is not None,
            token_expires_at=token_expires_at,
            verification_url=verification_url,
        )

    async def forgot_password(self, *, email: str) -> MessageResponse:
        user = await self._repository.get_user_by_email(email=email)
        if user is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=self._settings.password_reset_expire_seconds)
            reset_token = await self._repository.create_password_reset_token(user_id=user.id, expires_at=expires_at)
            self._log_password_reset_email(user.email, reset_token)
        return MessageResponse(message="If the account exists, a password reset email has been sent")

    async def reset_password(self, *, token: str, new_password: str) -> MessageResponse:
        user_id = await self._repository.consume_password_reset_token(raw_token=token)
        if user_id is None:
            raise UnauthorizedError("Invalid or expired reset token", code="invalid_token")

        await self._repository.update_password(user_id=user_id, password_hash=hash_password(new_password))
        await self._repository.revoke_all_refresh_tokens(user_id=user_id)
        return MessageResponse(message="Password reset successfully")

    def _log_password_reset_email(self, email: str, token: str) -> None:
        link = self._reset_link(token)
        log.info("password_reset_sent", extra={"email": email, "reset_link": link})

    def _reset_link(self, token: str) -> str:
        base = str(self._settings.frontend_url) if self._settings.frontend_url else "http://localhost:3000"
        return f"{base.rstrip('/')}/reset-password?token={token}"
