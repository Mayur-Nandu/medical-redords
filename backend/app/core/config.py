from __future__ import annotations

from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration sourced from environment variables and .env.

    Defaults are safe for local development. Production should override via env vars.
    """

    project_name: str = "Medical History API"
    version: str = "0.1.0"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    # Security
    secret_key: str = Field(default="change-me", min_length=16)
    log_level: str = "INFO"

    # CORS
    # Provide JSON list in env: ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:5173"]
    allowed_origins: List[str] = []

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (SQLite by default for local dev; override with Postgres in prod)
    database_url: str = Field(default="sqlite+pysqlite:///./data/app.db")

    # Auth
    access_token_expire_minutes: int = 60
    jwt_algorithm: str = "HS256"

    # PHI encryption (base64-encoded 32-byte key recommended)
    phi_encryption_key: str = Field(default="cGxlYXNlLXJvdGF0ZS10aGlzLWtleS1pbi1wcm9k")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

