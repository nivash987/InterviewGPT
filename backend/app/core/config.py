from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


Environment = Literal["local", "dev", "staging", "prod", "test"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="APP_",
        env_file=(".env",),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    app_name: str = "InterviewGPT API"
    env: Environment = "local"
    debug: bool = False
    api_version: str = "0.1.0"
    api_prefix: str = "/api"
    enable_docs: bool = True

    # Logging
    log_level: str = "INFO"
    log_json: bool = False

    # CORS / security
    allowed_origins: str = ""
    cors_allow_credentials: bool = True
    trusted_hosts: str = "*"

    # Database (placeholder; used for engine wiring later)
    database_url: str = Field(default="", description="SQLAlchemy URL")

    # JWT (placeholder; auth implementation later)
    jwt_issuer: str = "interviewgpt"
    jwt_audience: str = "interviewgpt"
    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_seconds: int = 900

    # Outbound calls
    public_base_url: AnyUrl | None = None

    @property
    def allowed_origins_list(self) -> list[str]:
        if not self.allowed_origins:
            return []
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def trusted_hosts_list(self) -> list[str]:
        if not self.trusted_hosts:
            return []
        return [h.strip() for h in self.trusted_hosts.split(",") if h.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

