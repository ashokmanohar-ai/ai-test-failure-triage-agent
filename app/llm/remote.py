import json
import os
from dataclasses import dataclass
from typing import Any, Self

import httpx

from app.models import FailureEvidence, TriageResult


def _prompt(evidence: FailureEvidence) -> str:
    prompt_path = os.getenv("TRIAGE_PROMPT_PATH", "prompts/triage-agent/v1.md")
    with open(prompt_path, encoding="utf-8") as handle:
        instructions = handle.read()
    return f"{instructions}\n\nUNTRUSTED EVIDENCE JSON:\n{evidence.model_dump_json()}"


@dataclass
class OpenAICompatibleProvider:
    api_key: str
    base_url: str
    model_name: str
    name: str = "openai"

    @classmethod
    def from_environment(cls, model_name: str) -> Self:
        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY is required for the openai provider")
        return cls(
            api_key=key,
            base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            model_name=model_name,
        )

    async def analyze(self, evidence: FailureEvidence) -> TriageResult:
        body = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": _prompt(evidence)}],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url.rstrip('/')}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json=body,
            )
            response.raise_for_status()
        payload: dict[str, Any] = response.json()
        raw = payload["choices"][0]["message"]["content"]
        for attempt in range(2):
            try:
                result = TriageResult.model_validate_json(raw)
                result.model_provider = self.name
                result.model_name = self.model_name
                return result
            except (ValueError, KeyError) as exc:
                if attempt:
                    raise RuntimeError("TRIAGE_MODEL_OUTPUT_INVALID") from exc
                raw = json.dumps(
                    {
                        "failure_id": evidence.failure.failure_id,
                        "primary_classification": "UNKNOWN",
                        "secondary_classifications": [],
                        "confidence": 0.2,
                        "confidence_band": "LOW",
                        "failure_symptom": evidence.failure.error_message,
                        "probable_technical_cause": "Invalid model output",
                        "probable_root_cause": "Invalid model output",
                        "evidence_for": [],
                        "evidence_against": ["Provider returned malformed structured output"],
                        "recommended_actions": ["Inspect provider output and evidence manually"],
                        "requires_human_review": True,
                    }
                )
        raise RuntimeError("TRIAGE_MODEL_OUTPUT_INVALID")


@dataclass
class AzureOpenAIProvider(OpenAICompatibleProvider):
    api_version: str = "2024-10-21"
    name: str = "azure_openai"

    @classmethod
    def from_environment(cls, model_name: str) -> Self:
        key = os.getenv("AZURE_OPENAI_API_KEY")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", model_name)
        if not key or not endpoint:
            raise RuntimeError("AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT are required")
        return cls(
            api_key=key,
            base_url=endpoint,
            model_name=deployment,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        )

    async def analyze(self, evidence: FailureEvidence) -> TriageResult:
        body = {
            "messages": [{"role": "user", "content": _prompt(evidence)}],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }
        url = f"{self.base_url.rstrip('/')}/openai/deployments/{self.model_name}/chat/completions?api-version={self.api_version}"
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(url, headers={"api-key": self.api_key}, json=body)
            response.raise_for_status()
        raw = response.json()["choices"][0]["message"]["content"]
        try:
            result = TriageResult.model_validate_json(raw)
        except ValueError as exc:
            raise RuntimeError("TRIAGE_MODEL_OUTPUT_INVALID") from exc
        result.model_provider = self.name
        result.model_name = self.model_name
        return result
