from app.models import FailureCategory, TriageResult
from app.triage.validation import validate_claims


def test_nonexistent_endpoint_is_flagged(evidence):
    result = TriageResult(
        failure_id="FAIL-TEST",
        primary_classification=FailureCategory.API_BACKEND,
        confidence=0.9,
        confidence_band="HIGH",
        failure_symptom="failure",
        probable_technical_cause="HTTP failure",
        probable_root_cause="POST /api/invented returned 500",
        evidence_for=["POST /api/invented returned 500"],
        evidence_against=[],
        recommended_actions=["Inspect logs"],
        requires_human_review=True,
    )
    assert any("UNSUPPORTED_TRIAGE_CLAIM" in item for item in validate_claims(result, evidence))


def test_unsafe_recommendation_is_blocked(evidence):
    result = TriageResult(
        failure_id="FAIL-TEST",
        primary_classification=FailureCategory.UNKNOWN,
        confidence=0.2,
        confidence_band="LOW",
        failure_symptom="failure",
        probable_technical_cause="unknown",
        probable_root_cause="unknown",
        evidence_for=[],
        evidence_against=[],
        recommended_actions=["rm -rf /tmp/app"],
        requires_human_review=True,
    )
    assert "UNSAFE_RECOMMENDATION_BLOCKED" in validate_claims(result, evidence)
