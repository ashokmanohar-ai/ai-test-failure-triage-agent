import asyncio
import json
from pathlib import Path

from pydantic import BaseModel, Field

from app.models import FailureCategory, FailureEvidence, TriageEvaluationCase
from app.triage import FailureTriageAgent


class CategoryMetrics(BaseModel):
    precision: float
    recall: float
    f1: float
    support: int


class CalibrationBin(BaseModel):
    minimum: float
    maximum: float
    count: int
    accuracy: float


class EvaluationReport(BaseModel):
    total: int
    correct: int
    overall_accuracy: float
    by_category: dict[str, CategoryMetrics]
    confusion_matrix: dict[str, dict[str, int]]
    calibration: list[CalibrationBin]
    high_confidence_accuracy: float
    unknown_precision: float
    root_cause_fact_recall: float
    quality_gate_passed: bool
    gate_failures: list[str] = Field(default_factory=list)


async def run_evaluation(
    agent: FailureTriageAgent, dataset_path: Path, root: Path, gates: dict[str, float] | None = None
) -> EvaluationReport:
    cases = [
        TriageEvaluationCase.model_validate(item)
        for item in json.loads(dataset_path.read_text(encoding="utf-8"))
    ]
    predictions: list[tuple[TriageEvaluationCase, FailureCategory, float, str]] = []
    for case in cases:
        evidence = FailureEvidence.model_validate_json(
            (root / case.evidence_fixture).read_text(encoding="utf-8")
        )
        result = await agent.triage(evidence)
        predictions.append(
            (
                case,
                result.primary_classification,
                result.confidence,
                result.probable_root_cause.casefold(),
            )
        )

    labels = sorted(
        {case.expected_primary_classification for case, _, _, _ in predictions}
        | {prediction for _, prediction, _, _ in predictions}
    )
    matrix: dict[str, dict[str, int]] = {
        str(label): {str(other): 0 for other in labels} for label in labels
    }
    correct = 0
    root_expected = 0
    root_matched = 0
    for case, prediction, _, root_cause in predictions:
        matrix[str(case.expected_primary_classification)][str(prediction)] += 1
        correct += prediction == case.expected_primary_classification
        for fact in case.expected_root_cause_facts:
            root_expected += 1
            root_matched += fact.casefold() in root_cause

    by_category: dict[str, CategoryMetrics] = {}
    for label in labels:
        key = str(label)
        tp = matrix[key][key]
        fp = sum(matrix[actual][key] for actual in matrix if actual != key)
        fn = sum(matrix[key][predicted] for predicted in matrix[key] if predicted != key)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        by_category[key] = CategoryMetrics(
            precision=precision,
            recall=recall,
            f1=2 * precision * recall / (precision + recall) if precision + recall else 0.0,
            support=tp + fn,
        )

    bins: list[CalibrationBin] = []
    for low, high in ((0.5, 0.59), (0.6, 0.69), (0.7, 0.79), (0.8, 0.89), (0.9, 1.0)):
        rows = [row for row in predictions if low <= row[2] <= high]
        accuracy = (
            sum(row[1] == row[0].expected_primary_classification for row in rows) / len(rows)
            if rows
            else 0.0
        )
        bins.append(CalibrationBin(minimum=low, maximum=high, count=len(rows), accuracy=accuracy))
    high_confidence_rows = [row for row in predictions if row[2] >= 0.85]
    high_accuracy = (
        sum(row[1] == row[0].expected_primary_classification for row in high_confidence_rows)
        / len(high_confidence_rows)
        if high_confidence_rows
        else 1.0
    )
    accuracy = correct / len(cases) if cases else 0.0
    unknown = by_category.get(
        "UNKNOWN", CategoryMetrics(precision=0, recall=0, f1=0, support=0)
    ).precision
    root_recall = root_matched / root_expected if root_expected else 1.0
    requested = gates or {
        "overall_accuracy": 0.88,
        "high_confidence_accuracy": 0.95,
        "unknown_precision": 0.80,
    }
    observed = {
        "overall_accuracy": accuracy,
        "high_confidence_accuracy": high_accuracy,
        "unknown_precision": unknown,
    }
    failures = [
        f"{name}: {observed[name]:.3f} < {minimum:.3f}"
        for name, minimum in requested.items()
        if observed.get(name, 0.0) < minimum
    ]
    return EvaluationReport(
        total=len(cases),
        correct=correct,
        overall_accuracy=accuracy,
        by_category=by_category,
        confusion_matrix=matrix,
        calibration=bins,
        high_confidence_accuracy=high_accuracy,
        unknown_precision=unknown,
        root_cause_fact_recall=root_recall,
        quality_gate_passed=not failures,
        gate_failures=failures,
    )


def run_evaluation_sync(
    agent: FailureTriageAgent, dataset_path: Path, root: Path, gates: dict[str, float] | None = None
) -> EvaluationReport:
    return asyncio.run(run_evaluation(agent, dataset_path, root, gates))
