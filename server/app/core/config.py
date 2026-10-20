from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: Literal["development", "test", "production"] = "development"
    app_name: str = "AutoCut AI"
    debug: bool = False
    api_prefix: str = "/api/v1"
    database_url: str = "postgresql+asyncpg://localhost/autocut"
    redis_url: str = "redis://localhost:6379/0"
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=10, ge=0, le=100)
    db_pool_recycle: int = Field(default=1800, ge=60)
    cors_origins: list[str] = []
    auth_issuer: str = ""
    auth_audience: str = ""
    auth_jwks_url: str = ""
    auth_algorithms: list[str] = ["EdDSA", "RS256", "ES256"]
    media_storage_root: Path = Path("./var/media")
    storage_backend: Literal["local", "r2"] = "local"
    r2_endpoint_url: str = ""
    r2_bucket: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    database_schema: str = "public"
    celery_queue: str = "autocut-main"
    max_upload_size_mb: int = Field(default=1024, ge=1)
    max_project_duration_seconds: int = Field(default=3600, ge=1)
    max_concurrent_renders: int = Field(default=2, ge=1)
    max_projects_per_user: int = Field(default=100, ge=1)
    max_storage_bytes: int = Field(default=50 * 1024**3, ge=1)
    max_timeline_items: int = Field(default=500, ge=1)
    ffmpeg_binary: str = "ffmpeg"
    ffprobe_binary: str = "ffprobe"
    mlt_render_binary: str = "melt"
    process_timeout_seconds: int = Field(default=1800, ge=1)
    job_lease_seconds: int = Field(default=90, ge=10)
    max_job_retries: int = Field(default=3, ge=0, le=10)
    default_preview_preset: str = "preview"
    log_level: str = "INFO"
    cache_ttl_seconds: int = Field(default=60, ge=1)
    expensive_requests_per_minute: int = Field(default=20, ge=1)
    decode_check: bool = True
    upload_session_ttl_seconds: int = Field(default=86400, ge=60)
    upload_chunk_size_bytes: int = Field(default=1024 * 1024, ge=65536)
    request_max_bytes: int = Field(default=1024 * 1024, ge=1024)
    max_outbox_attempts: int = Field(default=10, ge=1, le=100)

    @field_validator("database_schema")
    @classmethod
    def valid_database_schema(cls, value: str) -> str:
        import re

        if not re.fullmatch(r"[a-z][a-z0-9_]{0,62}", value):
            raise ValueError("DATABASE_SCHEMA must be a PostgreSQL identifier")
        return value

    @field_validator("database_url")
    @classmethod
    def postgres_only(cls, value: str) -> str:
        if not value.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL must use postgresql+asyncpg")
        return value

    @model_validator(mode="after")
    def secure(self) -> "Settings":
        if set(self.auth_algorithms) - {"EdDSA", "RS256", "ES256"}:
            raise ValueError("Only asymmetric JWT algorithms are permitted")
        if self.app_env == "production" and (
            self.debug or not self.auth_jwks_url.startswith("https://")
        ):
            raise ValueError("Production requires HTTPS JWKS and DEBUG=false")
        if self.app_env == "production" and (not self.auth_issuer or not self.auth_audience):
            raise ValueError("Production requires AUTH_ISSUER and AUTH_AUDIENCE")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
