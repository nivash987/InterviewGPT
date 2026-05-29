from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str
    field: str | None = None
    meta: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    ok: Literal[False] = False
    error: ErrorDetail
    request_id: str | None = None
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApiResponse(BaseModel, Generic[T]):
    ok: Literal[True] = True
    data: T
    request_id: str | None = None
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EmptyData(BaseModel):
    """Use when returning a success response with no payload."""

