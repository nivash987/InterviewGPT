from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt

from app.core.config import Settings
from app.core.errors import UnauthorizedError


@dataclass(frozen=True)
class TokenPayload:
    sub: str
    email: str | None
    token_type: str
    roles: tuple[str, ...]
    permissions: tuple[str, ...]
    jti: str | None
    exp: datetime
    iat: datetime


class JWTService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_access_token(
        self,
        *,
        user_id: str,
        email: str | None,
        roles: tuple[str, ...],
        permissions: tuple[str, ...],
    ) -> str:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(seconds=self._settings.access_token_expire_seconds)
        payload = {
            "sub": user_id,
            "email": email,
            "type": "access",
            "roles": list(roles),
            "permissions": list(permissions),
            "iss": self._settings.jwt_issuer,
            "aud": self._settings.jwt_audience,
            "iat": now,
            "exp": expires,
        }
        return jwt.encode(payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)

    def create_refresh_token(self, *, user_id: str) -> tuple[str, str, datetime]:
        now = datetime.now(timezone.utc)
        jti = uuid4().hex
        expires = now + timedelta(seconds=self._settings.refresh_token_expire_seconds)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "jti": jti,
            "iss": self._settings.jwt_issuer,
            "aud": self._settings.jwt_audience,
            "iat": now,
            "exp": expires,
        }
        token = jwt.encode(payload, self._settings.jwt_secret, algorithm=self._settings.jwt_algorithm)
        return token, jti, expires

    def decode_token(self, token: str) -> TokenPayload:
        try:
            raw: dict[str, Any] = jwt.decode(
                token,
                self._settings.jwt_secret,
                algorithms=[self._settings.jwt_algorithm],
                audience=self._settings.jwt_audience,
                issuer=self._settings.jwt_issuer,
            )
        except jwt.ExpiredSignatureError as exc:
            raise UnauthorizedError("Token has expired", code="token_expired") from exc
        except jwt.InvalidTokenError as exc:
            raise UnauthorizedError("Invalid token", code="invalid_token") from exc

        exp = datetime.fromtimestamp(raw["exp"], tz=timezone.utc)
        iat = datetime.fromtimestamp(raw["iat"], tz=timezone.utc)
        return TokenPayload(
            sub=str(raw["sub"]),
            email=raw.get("email"),
            token_type=str(raw.get("type", "")),
            roles=tuple(raw.get("roles") or []),
            permissions=tuple(raw.get("permissions") or []),
            jti=raw.get("jti"),
            exp=exp,
            iat=iat,
        )
