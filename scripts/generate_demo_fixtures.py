"""Generate sanitized, deterministic evaluation fixtures; no execution evidence is claimed."""

import json
from datetime import UTC, datetime
from pathlib import Path

from app.models import (
    CodeChange,
    FailureEvidence,
    FailureRecord,
    HealthCheck,
    HistoricalFailure,
    NetworkFailure,
)

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "evidence"
DATASET = ROOT / "datasets" / "triage" / "cases.json"


def base(identifier: str, message: str, *, retry: int = 0) -> FailureEvidence:
    return FailureEvidence(
        failure=FailureRecord(
            failure_id=f"FAIL-{identifier}",
            test_id=f"test-{identifier}",
            test_name=f"Controlled scenario {identifier}",
            suite="controlled-failures",
            error_message=message,
            duration_ms=5000,
            retry_count=retry,
            browser="chromium",
            environment="local",
            timestamp=datetime(2026, 8, 21, 10, 32, tzinfo=UTC),
        )
    )


def scenarios() -> list[tuple[str, FailureEvidence, str, list[str]]]:
    values: list[tuple[str, FailureEvidence, str, list[str]]] = []
    for index in range(1, 16):
        item = base(
            f"AUTO-{index:02}", "locator('button:has-text(Checkout)') resolved to 0 elements"
        )
        item.environment_health = [HealthCheck(name="app", status="UP")]
        item.recent_changes = [CodeChange(path=f"src/components/CheckoutButton{index}.tsx")]
        values.append((f"automation-{index:02}", item, "AUTOMATION_DEFECT", ["locator"]))
    for index in range(1, 16):
        item = base(f"PROD-{index:02}", f"Expected total {100 + index}, received {90 + index}")
        item.recent_changes = [CodeChange(path=f"src/domain/pricing{index}.py")]
        values.append(
            (
                f"product-{index:02}",
                item,
                "PRODUCT_DEFECT",
                ["assertion detected changed product behaviour"],
            )
        )
    for index in range(1, 11):
        item = base(f"API-{index:02}", "Checkout UI did not show confirmation")
        item.network_failures = [
            NetworkFailure(
                method="POST",
                url=f"http://demo/api/orders/{index}",
                status_code=500,
                correlation_id=f"req-{index:04}",
            )
        ]
        values.append((f"api-{index:02}", item, "API_BACKEND", ["backend request failed"]))
    for index in range(1, 11):
        item = base(f"ENV-{index:02}", "Application was unreachable")
        item.environment_health = [HealthCheck(name=f"application-{index}", status="DOWN")]
        values.append((f"environment-{index:02}", item, "ENVIRONMENT", ["health check failed"]))
    for index in range(1, 11):
        item = base(
            f"DATA-{index:02}", f"Invalid account state: account expired for fixture {index}"
        )
        values.append((f"test-data-{index:02}", item, "TEST_DATA", ["data precondition"]))
    for index in range(1, 11):
        item = base(f"FLAKE-{index:02}", "Intermittent render failure", retry=1)
        item.historical_failures = [
            HistoricalFailure(
                signature=f"sig-{index}-{n}",
                classification="FLAKY_TEST",
                root_cause="timing" if n % 2 else "render",
                occurrence_count=2,
                similarity=0.9,
                retry_recovered=True,
                same_commit=True,
                same_environment=True,
            )
            for n in range(2)
        ]  # type: ignore[list-item]
        values.append((f"flaky-{index:02}", item, "FLAKY_TEST", ["instability signals"]))
    for index in range(1, 6):
        item = base(f"AUTH-{index:02}", "Stored auth state expired token; redirected to login")
        item.network_failures = [
            NetworkFailure(method="GET", url="http://demo/api/session", status_code=401)
        ]
        values.append(
            (f"auth-{index:02}", item, "AUTHENTICATION", ["authentication or session evidence"])
        )
    for index in range(1, 6):
        item = base(f"UNKNOWN-{index:02}", f"Unexpected value in scenario {index}")
        values.append((f"unknown-{index:02}", item, "UNKNOWN", ["does not support"]))
    return values


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    DATASET.parent.mkdir(parents=True, exist_ok=True)
    cases = []
    for identifier, evidence, expected, facts in scenarios():
        relative = f"fixtures/evidence/{identifier}.json"
        (ROOT / relative).write_text(evidence.model_dump_json(indent=2), encoding="utf-8")
        cases.append(
            {
                "id": identifier,
                "evidence_fixture": relative,
                "expected_primary_classification": expected,
                "accepted_secondary": [],
                "expected_root_cause_facts": facts,
                "tags": [expected.casefold()],
            }
        )
    DATASET.write_text(json.dumps(cases, indent=2), encoding="utf-8")
    print(f"Generated {len(cases)} controlled evaluation cases")


if __name__ == "__main__":
    main()
