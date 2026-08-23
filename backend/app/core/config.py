from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

class Settings(BaseSettings):
    app_name: str
    environment: str

    database_url: str
    database_ssl: bool = True

    redis_url: str

    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60

    cors_origins: str

    worker_id: str | None = None
    worker_count: int = Field(default=3, ge=1, le=20)
    max_concurrency: int = Field(default=10, ge=1)

    poll_interval_seconds: float = 0.5
    heartbeat_interval_seconds: float = 5.0
    lease_timeout_seconds: int = 120

    scheduler_interval_seconds: float = 1.0
    scheduler_lock_ttl_seconds: int = 5

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]

    @property
    def normalized_database_url(self) -> str:
        url = self.database_url

        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url[len("postgresql://"):]

        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://"):]

        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()