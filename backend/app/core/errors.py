from __future__ import annotations

import traceback
from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from app.core.logging import get_logger
from app.core.responses import ErrorDetail, ErrorResponse


@dataclass(frozen=True)
class AppError(Exception):
    code: str
    message: str
    http_status: int = status.HTTP_400_BAD_REQUEST
    field: str | None = None
    meta: dict[str, Any] | None = None


class NotFoundError(AppError):
    def __init__(self, message: str = "Not found", *, code: str = "not_found") -> None:
        super().__init__(code=code, message=message, http_status=status.HTTP_404_NOT_FOUND)


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", *, code: str = "unauthorized") -> None:
        super().__init__(code=code, message=message, http_status=status.HTTP_401_UNAUTHORIZED)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", *, code: str = "forbidden") -> None:
        super().__init__(code=code, message=message, http_status=status.HTTP_403_FORBIDDEN)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", *, code: str = "conflict") -> None:
        super().__init__(code=code, message=message, http_status=status.HTTP_409_CONFLICT)


def _request_id(request: Request) -> str | None:
    return request.state.request_id if hasattr(request.state, "request_id") else None


def install_exception_handlers(app: FastAPI, *, debug: bool) -> None:
    log = get_logger(__name__)

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(code=exc.code, message=exc.message, field=exc.field, meta=exc.meta),
            request_id=_request_id(request),
        )
        log.info(
            "app_error",
            extra={
                "code": exc.code,
                "http_status": exc.http_status,
                "request_id": body.request_id,
                "path": str(request.url.path),
                "method": request.method,
            },
        )
        return JSONResponse(status_code=exc.http_status, content=body.model_dump(mode="json"))

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        body = ErrorResponse(
            error=ErrorDetail(code="validation_error", message="Request validation failed", meta={"errors": exc.errors()}),
            request_id=_request_id(request),
        )
        log.info(
            "validation_error",
            extra={"request_id": body.request_id, "path": str(request.url.path), "method": request.method},
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=body.model_dump(mode="json"))

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = _request_id(request)
        meta: dict[str, Any] | None = None
        if debug:
            meta = {"traceback": traceback.format_exc()}
        body = ErrorResponse(
            error=ErrorDetail(code="internal_error", message="Internal server error", meta=meta),
            request_id=request_id,
        )
        log.error(
            "unhandled_error",
            extra={
                "request_id": request_id,
                "path": str(request.url.path),
                "method": request.method,
                "exception": repr(exc),
                "traceback": traceback.format_exc(),
            },
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=body.model_dump(mode="json"))

