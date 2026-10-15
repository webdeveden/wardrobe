from functools import lru_cache
from pathlib import Path

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_JWT_SECRET = "dev-secret-change-me"


class Settings(BaseSettings):
    """Environment-driven configuration. Values come from the process env, then `.env`."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    database_url: str = "postgresql://postgres:postgres@localhost:5432/wardrobe_catalog"
    jwt_secret: str = DEV_JWT_SECRET
    jwt_expires_days: int = 7
    frontend_origin: str = "http://localhost:5173"
    uploads_dir: Path = Path("uploads")

    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    chat_model: str = "openai/gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"

    @model_validator(mode="after")
    def _require_secret_in_production(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret == DEV_JWT_SECRET:
            raise ValueError("JWT_SECRET must be set in production")
        return self

    @property
    def sqlalchemy_url(self) -> str:
        """DATABASE_URL rewritten for the psycopg (v3) driver, which understands libpq params like sslmode."""
        for prefix in ("postgresql+psycopg://", "postgresql://", "postgres://"):
            if self.database_url.startswith(prefix):
                return "postgresql+psycopg://" + self.database_url[len(prefix):]
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
