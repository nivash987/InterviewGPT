from __future__ import annotations

from fastapi import FastAPI


def configure_openapi(app: FastAPI) -> None:
    # Reserved for later: add JWT auth scheme, request-id header, etc.
    # Keep as an explicit hook so OpenAPI customization stays centralized.
    return None

