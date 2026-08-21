from app.models import FailureCategory, FailureEvidence

RECOMMENDATIONS: dict[FailureCategory, list[str]] = {
    FailureCategory.AUTOMATION_DEFECT: [
        "Inspect the failing page-object locator and captured trace.",
        "Confirm the UI behaviour with the product owner before changing automation.",
        "Apply any locator change through review and re-run affected tests.",
    ],
    FailureCategory.PRODUCT_DEFECT: [
        "Reproduce the behaviour against the approved requirement and stable data.",
        "Attach the assertion, screenshot, trace and relevant recent product changes to the defect.",
        "Route to the owning product team for review.",
    ],
    FailureCategory.API_BACKEND: [
        "Inspect the failed endpoint and correlation/request ID in backend logs.",
        "Confirm whether the failure reproduces outside the UI test.",
        "Re-run the UI test only after backend health is restored or the defect is fixed.",
    ],
    FailureCategory.ENVIRONMENT: [
        "Inspect the failed health check and platform telemetry.",
        "Restore the affected service or configuration before re-running tests.",
        "Keep the original test failure visible in CI.",
    ],
    FailureCategory.AUTHENTICATION: [
        "Validate storage state, token expiry and login redirects.",
        "Refresh credentials through the approved secret-management flow.",
        "Re-run the affected authentication path after review.",
    ],
    FailureCategory.TEST_DATA: [
        "Inspect the referenced account/record state in the target environment.",
        "Provision isolated valid data or repair the controlled fixture.",
        "Record the data dependency for future runs.",
    ],
    FailureCategory.FLAKY_TEST: [
        "Repeat under the same commit, data and environment while preserving artifacts.",
        "Compare signature variability and timing across recent runs.",
        "Quarantine or change waits only through the team's reviewed policy.",
    ],
    FailureCategory.NETWORK: [
        "Inspect DNS, proxy, TLS and transport evidence for the failed request.",
        "Correlate with infrastructure telemetry before assigning a product defect.",
    ],
    FailureCategory.BROWSER: [
        "Inspect browser process logs and resource availability.",
        "Reproduce with the same browser build and configuration.",
    ],
    FailureCategory.PERFORMANCE_TIMEOUT: [
        "Compare endpoint and rendering duration against the defined SLO.",
        "Inspect backend/trace timing before increasing any timeout.",
    ],
    FailureCategory.ASSERTION_DEFECT: [
        "Compare the assertion with the current approved requirement.",
        "Update expectations only through human review.",
    ],
    FailureCategory.CONFIGURATION: [
        "Compare runtime settings with the approved environment baseline.",
        "Correct configuration through the controlled deployment process.",
    ],
    FailureCategory.DEPENDENCY: [
        "Inspect the dependent service and its status history.",
        "Re-run after the dependency is healthy.",
    ],
    FailureCategory.UNKNOWN: [
        "Collect missing trace, network, health, history and change evidence.",
        "Escalate for human investigation; do not auto-route or modify tests.",
    ],
}


def recommendations_for(
    category: FailureCategory, subcategory: str | None, evidence: FailureEvidence
) -> list[str]:
    actions = list(RECOMMENDATIONS[category])
    correlation_ids = [
        item.correlation_id for item in evidence.network_failures if item.correlation_id
    ]
    if correlation_ids:
        actions.insert(0, f"Use correlation ID {correlation_ids[0]} to inspect service logs.")
    if subcategory == "LOCATOR_CHANGED":
        actions[0] = (
            "Inspect the failed accessible locator against the current rendered label/role."
        )
    return actions
