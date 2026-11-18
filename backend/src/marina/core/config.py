"""Application Configuration for MARINA INTELLIGENCE."""

from typing import List
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    PROJECT_NAME: str = "MARINA INTELLIGENCE"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    # Database Configuration
    # Defaults to PostgreSQL with psycopg driver; SQLite fallback available for local/testing
    DATABASE_URL: str = Field(
        default="postgresql+psycopg://marina:marina_secret@localhost:5432/marina_intelligence",
        description="Async database connection string",
    )

    # Secret Key for integrity checks or future auth
    SECRET_KEY: str = "marina-intelligence-insecure-dev-key-change-in-production-2026"

    # Default Target Focus Context
    DEFAULT_CLUB_CODE: str = "CFC"
    DEFAULT_CLUB_NAME: str = "Chennaiyin FC"
    DEFAULT_SEASON_CODE: str = "2026–27"
    DEFAULT_COMPETITION_CODE: str = "ISL"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_database_url(self) -> str:
        """Converts async database URL to a sync-compatible URL for Alembic migrations."""
        url = self.DATABASE_URL
        if url.startswith("postgresql+psycopg://"):
            return url.replace("postgresql+psycopg://", "postgresql+psycopg://")
        if url.startswith("postgresql+asyncpg://"):
            return url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
        if url.startswith("sqlite+aiosqlite:///"):
            return url.replace("sqlite+aiosqlite:///", "sqlite:///")
        return url


settings = Settings()
