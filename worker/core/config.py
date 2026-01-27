"""Worker configuration using Pydantic settings."""

from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Worker settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Worker
    worker_name: str = "langgraph-worker"
    debug: bool = False

    # Database (same as app - uses asyncpg format)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/app_db"

    # Checkpointer
    checkpointer_pool_size: int = 5

    @cached_property
    def psycopg_database_url(self) -> str:
        """Convert asyncpg database URL to psycopg format.

        LangGraph uses psycopg3 (postgresql://) while FastAPI uses asyncpg
        (postgresql+asyncpg://). This property transforms the URL.
        """
        url = self.database_url
        # Remove the +asyncpg driver suffix
        if url.startswith("postgresql+asyncpg://"):
            url = url.replace("postgresql+asyncpg://", "postgresql://")
        return url


settings = WorkerSettings()
