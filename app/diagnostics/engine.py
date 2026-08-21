from collections.abc import Callable

from app.diagnostics.rules import (
    assertion_findings,
    authentication_findings,
    browser_findings,
    environment_findings,
    flaky_findings,
    locator_findings,
    network_findings,
    test_data_findings,
    timeout_findings,
)
from app.models import DiagnosticFinding, FailureEvidence

Rule = Callable[[FailureEvidence], list[DiagnosticFinding]]

RULES: tuple[Rule, ...] = (
    authentication_findings,
    environment_findings,
    network_findings,
    browser_findings,
    locator_findings,
    timeout_findings,
    assertion_findings,
    test_data_findings,
    flaky_findings,
)


def run_diagnostics(evidence: FailureEvidence) -> list[DiagnosticFinding]:
    findings = [finding for rule in RULES for finding in rule(evidence)]
    return sorted(findings, key=lambda item: item.score, reverse=True)
