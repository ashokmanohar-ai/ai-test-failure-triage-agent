from app.diagnostics import run_diagnostics
from app.llm.provider import TriageModelProvider
from app.models import FailureEvidence, TriageResult
from app.normalization.evidence import normalize_evidence
from app.triage.confidence import calculate_confidence, confidence_band
from app.triage.validation import validate_claims


class FailureTriageAgent:
    """Evidence-first orchestration: sanitize, diagnose, model, validate, calibrate."""

    def __init__(self, provider: TriageModelProvider) -> None:
        self.provider = provider

    async def triage(self, evidence: FailureEvidence) -> TriageResult:
        normalized = normalize_evidence(evidence)
        normalized.deterministic_findings = run_diagnostics(normalized)
        evidence.deterministic_findings = list(normalized.deterministic_findings)
        result = await self.provider.analyze(normalized)
        result.unsupported_claims = validate_claims(result, normalized)
        if result.unsupported_claims:
            result.evidence_against.extend(result.unsupported_claims)
            result.requires_human_review = True
        score, components = calculate_confidence(result, normalized)
        result.confidence = score
        result.confidence_band = confidence_band(score)  # type: ignore[assignment]
        result.deterministic_score = components["deterministic"]
        result.historical_score = components["historical"]
        result.agreement_score = components["agreement"]
        result.model_score = components["model"]
        result.requires_human_review = result.confidence_band != "HIGH" or bool(
            result.unsupported_claims
        )
        return result
