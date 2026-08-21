from app.models import FailureCategory, FailureEvidence, TriageResult
from app.triage.recommendations import recommendations_for


class MockProvider:
    """Deterministic provider for orchestration tests; not a real AI-quality claim."""

    name = "mock"

    def __init__(self, model_name: str = "mock-evidence-v1") -> None:
        self.model_name = model_name

    async def analyze(self, evidence: FailureEvidence) -> TriageResult:
        findings = sorted(
            evidence.deterministic_findings, key=lambda item: item.score, reverse=True
        )
        best = findings[0] if findings else None
        category = best.category if best and best.score >= 0.5 else FailureCategory.UNKNOWN
        evidence_for = (
            list(best.evidence) if best else ["No decisive deterministic evidence was supplied"]
        )
        evidence_against = (
            list(best.counter_evidence)
            if best
            else ["Network, health, history and change context are insufficient"]
        )
        score = best.score if best else 0.35
        root_cause = (
            best.explanation
            if best
            else "The available evidence does not support a reliable root-cause hypothesis."
        )
        return TriageResult(
            failure_id=evidence.failure.failure_id,
            primary_classification=category,
            secondary_classifications=[f.category for f in findings[1:3] if f.category != category],
            subcategory=best.subcategory if best else None,
            confidence=score,
            confidence_band="LOW",
            failure_symptom=evidence.failure.error_message[:500],
            probable_technical_cause=best.explanation
            if best
            else "Undetermined from supplied evidence",
            probable_root_cause=root_cause,
            evidence_for=evidence_for,
            evidence_against=evidence_against,
            recommended_actions=recommendations_for(
                category, best.subcategory if best else None, evidence
            ),
            requires_human_review=True,
            model_provider=self.name,
            model_name=self.model_name,
            model_score=score,
        )
