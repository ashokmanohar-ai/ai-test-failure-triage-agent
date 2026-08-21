import re

from app.models import DiagnosticFinding, FailureCategory, FailureEvidence


def _finding(
    rule: str,
    category: FailureCategory,
    score: float,
    evidence: list[str],
    explanation: str,
    *,
    subcategory: str | None = None,
    counter: list[str] | None = None,
) -> DiagnosticFinding:
    return DiagnosticFinding(
        rule_id=rule,
        category=category,
        subcategory=subcategory,
        score=score,
        evidence=evidence,
        counter_evidence=counter or [],
        explanation=explanation,
    )


def authentication_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    status = [n for n in value.network_failures if n.status_code in {401, 403}]
    text = " ".join(
        [value.failure.error_message, *(e.message for e in value.console_errors)]
    ).casefold()
    signals = [f"{n.method} {n.url} returned {n.status_code}" for n in status]
    if "expired token" in text or "storage state" in text or "redirected to login" in text:
        signals.append("Authentication/session-expiry text is present")
    return (
        [
            _finding(
                "AUTH-001",
                FailureCategory.AUTHENTICATION,
                min(0.98, 0.72 + 0.1 * len(signals)),
                signals,
                "The failure contains explicit authentication or session evidence",
                subcategory="SESSION_EXPIRED",
            )
        ]
        if signals
        else []
    )


def environment_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    down = [h for h in value.environment_health if h.status == "DOWN"]
    degraded = [h for h in value.environment_health if h.status == "DEGRADED"]
    if down:
        return [
            _finding(
                "ENV-001",
                FailureCategory.ENVIRONMENT,
                0.97,
                [f"Health check {h.name} is DOWN" for h in down],
                "A configured service health check failed",
                subcategory="SERVICE_UNAVAILABLE",
            )
        ]
    if degraded:
        return [
            _finding(
                "ENV-002",
                FailureCategory.ENVIRONMENT,
                0.72,
                [f"Health check {h.name} is DEGRADED" for h in degraded],
                "One or more environment components are degraded",
            )
        ]
    return []


def network_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    backend = [n for n in value.network_failures if n.status_code and n.status_code >= 500]
    connection = [n for n in value.network_failures if n.failure_reason]
    if backend:
        score = 0.94 if any(n.status_code == 500 for n in backend) else 0.9
        evidence = [f"{n.method} {n.url} returned HTTP {n.status_code}" for n in backend]
        return [
            _finding(
                "NET-5XX",
                FailureCategory.API_BACKEND,
                score,
                evidence,
                "A backend request failed immediately around the test failure",
                subcategory="HTTP_5XX",
            )
        ]
    if connection:
        evidence = [f"{n.method} {n.url}: {n.failure_reason}" for n in connection]
        return [
            _finding(
                "NET-CONNECTION",
                FailureCategory.NETWORK,
                0.88,
                evidence,
                "Transport-level failures were recorded",
            )
        ]
    return []


def browser_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    text = value.failure.error_message.casefold()
    patterns = (
        "browser has been closed",
        "browser launch",
        "context closed",
        "page crashed",
        "target closed",
    )
    return (
        [
            _finding(
                "BROWSER-001",
                FailureCategory.BROWSER,
                0.9,
                ["Browser lifecycle error recorded"],
                "The browser, page, or context terminated unexpectedly",
            )
        ]
        if any(p in text for p in patterns)
        else []
    )


def locator_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    text = value.failure.error_message.casefold()
    locator = any(
        p in text
        for p in ("locator", "selector", "strict mode violation", "element is not attached")
    )
    zero = any(p in text for p in ("resolved to 0", "element(s) not found", "waiting for locator"))
    if not locator:
        return []
    changes = [
        c.path
        for c in value.recent_changes
        if any(token in c.path.casefold() for token in ("page", "component", "view", "ui", "test"))
    ]
    healthy = bool(value.environment_health) and all(
        h.status == "UP" for h in value.environment_health
    )
    score = 0.66 + (0.12 if zero else 0) + (0.1 if changes else 0) + (0.06 if healthy else 0)
    evidence = ["Playwright reported a locator/action failure"]
    if zero:
        evidence.append("Locator resolved to zero matching elements")
    if changes:
        evidence.append(f"Related UI/test files changed: {', '.join(changes[:3])}")
    counter = [] if healthy else ["Application health was not confirmed"]
    return [
        _finding(
            "LOCATOR-001",
            FailureCategory.AUTOMATION_DEFECT,
            min(score, 0.96),
            evidence,
            "A test locator likely no longer matches the rendered UI",
            subcategory="LOCATOR_CHANGED",
            counter=counter,
        )
    ]


def timeout_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    text = value.failure.error_message.casefold()
    if "timeout" not in text and value.failure.status != "TIMED_OUT":
        return []
    slow = [n for n in value.network_failures if n.duration_ms and n.duration_ms >= 5000]
    if slow:
        return [
            _finding(
                "TIMEOUT-PERF",
                FailureCategory.PERFORMANCE_TIMEOUT,
                0.87,
                [f"{n.method} {n.url} took {n.duration_ms}ms" for n in slow],
                "Slow backend responses correlate with the timeout",
                subcategory="API_TIMEOUT",
            )
        ]
    return [
        _finding(
            "TIMEOUT-UNKNOWN",
            FailureCategory.UNKNOWN,
            0.42,
            ["A timeout occurred without sufficient causal evidence"],
            "Timeout type requires additional trace/network evidence",
        )
    ]


def assertion_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    text = value.failure.error_message
    if not re.search(r"(?is)(expected.+(?:received|actual)|assertion)", text):
        return []
    product_change = [
        c
        for c in value.recent_changes
        if not any(t in c.path.casefold() for t in ("test", "spec", "fixture"))
    ]
    if product_change:
        return [
            _finding(
                "ASSERT-PRODUCT",
                FailureCategory.PRODUCT_DEFECT,
                0.76,
                [
                    "Expected/actual mismatch recorded",
                    f"Product files changed: {product_change[0].path}",
                ],
                "The assertion detected changed product behaviour",
                subcategory="BEHAVIOR_REGRESSION",
            )
        ]
    return [
        _finding(
            "ASSERT-AMBIGUOUS",
            FailureCategory.UNKNOWN,
            0.48,
            ["Expected/actual mismatch recorded"],
            "Evidence does not distinguish a product defect from an incorrect expectation",
            counter=["No requirements or change evidence supplied"],
        )
    ]


def test_data_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    text = " ".join(
        [value.failure.error_message, *(e.message for e in value.console_errors)]
    ).casefold()
    patterns = (
        "test data",
        "account expired",
        "record not found",
        "duplicate record",
        "inventory unavailable",
        "invalid account state",
    )
    matches = [p for p in patterns if p in text]
    return (
        [
            _finding(
                "DATA-001",
                FailureCategory.TEST_DATA,
                min(0.94, 0.7 + 0.05 * len(matches)),
                [f"Recorded data-state signal: {p}" for p in matches],
                "The failure is tied to a controlled data precondition",
                subcategory="INVALID_STATE",
            )
        ]
        if matches
        else []
    )


def flaky_findings(value: FailureEvidence) -> list[DiagnosticFinding]:
    history = value.historical_failures
    recoveries = sum(item.retry_recovered for item in history)
    alternation = len({item.root_cause for item in history}) > 1
    no_changes = not value.recent_changes
    same_context = any(item.same_commit and item.same_environment for item in history)
    indicator = min(
        1.0,
        0.28 * bool(value.failure.retry_count)
        + 0.24 * bool(recoveries)
        + 0.18 * alternation
        + 0.16 * no_changes
        + 0.14 * same_context,
    )
    if indicator < 0.5:
        return []
    return [
        _finding(
            "FLAKE-001",
            FailureCategory.FLAKY_TEST,
            indicator,
            [
                f"Flake indicator={indicator:.2f}",
                f"Historical retry recoveries={recoveries}",
                f"Same-context history={same_context}",
            ],
            "Multiple independent instability signals support a flaky-test candidate",
            subcategory="INTERMITTENT",
            counter=["Retry success alone is not proof of flakiness"],
        )
    ]
