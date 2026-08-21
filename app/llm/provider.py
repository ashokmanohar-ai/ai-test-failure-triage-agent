from typing import Protocol

from app.config import Settings
from app.models import FailureEvidence, TriageResult


class TriageModelProvider(Protocol):
    name: str
    model_name: str

    async def analyze(self, evidence: FailureEvidence) -> TriageResult: ...


def create_provider(settings: Settings) -> TriageModelProvider:
    if settings.model_provider == "mock":
        from app.llm.mock import MockProvider

        return MockProvider(model_name=settings.model_name)
    if settings.model_provider == "azure_openai":
        from app.llm.remote import AzureOpenAIProvider

        return AzureOpenAIProvider.from_environment(settings.model_name)
    from app.llm.remote import OpenAICompatibleProvider

    return OpenAICompatibleProvider.from_environment(settings.model_name)
