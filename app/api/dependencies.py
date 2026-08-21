from functools import lru_cache
from pathlib import Path

from app.config import get_settings
from app.llm import create_provider
from app.persistence import FailureRepository
from app.triage import FailureTriageAgent


@lru_cache
def repository() -> FailureRepository:
    settings = get_settings()
    path = Path(settings.database_url.removeprefix("sqlite:///"))
    return FailureRepository(path)


def agent() -> FailureTriageAgent:
    return FailureTriageAgent(create_provider(get_settings()))
