from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Test Failure Triage Agent"
    environment: str = "development"
    model_provider: Literal["mock", "azure_openai", "openai"] = "mock"
    model_name: str = "mock-evidence-v1"
    database_url: str = "sqlite:///./triage.db"
    artifact_root: Path = Field(default=Path("./artifacts"))
    report_root: Path = Field(default=Path("./reports"))
    max_upload_bytes: int = 25 * 1024 * 1024
    confidence_high: float = 0.85
    confidence_medium: float = 0.65
    pii_redaction: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()
