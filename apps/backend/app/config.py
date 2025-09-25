from __future__ import annotations

from functools import lru_cache
from pydantic import BaseModel, Field
import os


class Settings(BaseModel):
    app_env: str = Field(default=os.getenv("APP_ENV", "development"))
    app_debug: bool = Field(default=os.getenv("APP_DEBUG", "false").lower() == "true")
    secret_key: str = Field(default=os.getenv("SECRET_KEY", "change-me"))
    allowed_origins: list[str] = Field(default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"])

    database_url: str = Field(default=os.getenv("DATABASE_URL", ""))

    keycloak_url: str = Field(default=os.getenv("KEYCLOAK_URL", "http://localhost:8080"))
    keycloak_realm: str = Field(default=os.getenv("KEYCLOAK_REALM", "medhist-dev"))
    keycloak_client_id: str = Field(default=os.getenv("KEYCLOAK_CLIENT_ID", "backend"))
    keycloak_client_secret: str = Field(default=os.getenv("KEYCLOAK_CLIENT_SECRET", "secret"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

