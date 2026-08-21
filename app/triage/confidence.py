from dataclasses import dataclass

from app.models import FailureCategory, FailureEvidence, TriageResult


@dataclass(frozen=True)
class ConfidenceWeights:
    deterministic: float = 0.40
    historical: float = 0.25
    agreement: float = 0.20
    model: float = 0.15


def calculate_confidence(
    result: TriageResult,
    evidence: FailureEvidence,
    weights: ConfidenceWeights = ConfidenceWeights(),
) -> tuple[float, dict[str, float]]:
    matching = [
        f for f in evidence.deterministic_findings if f.category == result.primary_classification
    ]
    deterministic = max(
        (f.score for f in matching),
        default=0.2 if result.primary_classification == FailureCategory.UNKNOWN else 0.0,
    )
    history = max(
        (
            h.similarity
            for h in evidence.historical_failures
            if h.classification == result.primary_classification
        ),
        default=0.0,
    )
    competing = max(
        (
            f.score
            for f in evidence.deterministic_findings
            if f.category != result.primary_classification
        ),
        default=0.0,
    )
    agreement = min(1.0, max(0.0, deterministic - competing + 0.5))
    model = min(max(result.model_score or result.confidence, 0.0), 1.0)
    score = (
        deterministic * weights.deterministic
        + history * weights.historical
        + agreement * weights.agreement
        + model * weights.model
    )
    if result.primary_classification == FailureCategory.UNKNOWN:
        score = min(score, 0.64)
    components = {
        "deterministic": deterministic,
        "historical": history,
        "agreement": agreement,
        "model": model,
    }
    return round(min(max(score, 0.0), 1.0), 4), components


def confidence_band(score: float) -> str:
    if score >= 0.85:
        return "HIGH"
    if score >= 0.65:
        return "MEDIUM"
    return "LOW"
