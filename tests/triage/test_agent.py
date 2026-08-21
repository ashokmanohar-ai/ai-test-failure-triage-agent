import pytest

from app.llm.mock import MockProvider
from app.models import CodeChange, FailureCategory, HealthCheck
from app.triage import FailureTriageAgent


@pytest.mark.asyncio
async def test_agent_runs_rules_before_provider(evidence):
    evidence.failure.error_message = "locator('Checkout') resolved to 0 elements"
    evidence.environment_health = [HealthCheck(name="app", status="UP")]
    evidence.recent_changes = [CodeChange(path="src/components/Checkout.tsx")]
    result = await FailureTriageAgent(MockProvider()).triage(evidence)
    assert result.primary_classification == FailureCategory.AUTOMATION_DEFECT
    assert result.deterministic_score > 0
    assert 0 <= result.agreement_score <= 1
    assert result == type(result).model_validate_json(result.model_dump_json())
    assert result.requires_human_review


@pytest.mark.asyncio
async def test_unknown_is_valid(evidence):
    result = await FailureTriageAgent(MockProvider()).triage(evidence)
    assert result.primary_classification == FailureCategory.UNKNOWN
    assert result.confidence < 0.65
