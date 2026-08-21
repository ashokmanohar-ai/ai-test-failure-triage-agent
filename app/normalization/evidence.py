from copy import deepcopy

from app.models import FailureEvidence
from app.normalization.timeline import build_timeline
from app.security.sanitization import neutralize_prompt_injection, sanitize_text


def normalize_evidence(evidence: FailureEvidence) -> FailureEvidence:
    """Return a sanitized deep copy suitable for diagnostics, storage and model input."""
    result = deepcopy(evidence)
    result.failure.error_message = sanitize_text(result.failure.error_message)
    if result.failure.stack_trace:
        result.failure.stack_trace = sanitize_text(result.failure.stack_trace)
    for event in result.console_errors:
        event.message = neutralize_prompt_injection(sanitize_text(event.message))
    for network in result.network_failures:
        network.url = sanitize_text(network.url, redact_pii=False)
        if network.failure_reason:
            network.failure_reason = sanitize_text(network.failure_reason)
    for health in result.environment_health:
        if health.detail:
            health.detail = sanitize_text(health.detail)
    result.timeline = build_timeline(result)
    return result
