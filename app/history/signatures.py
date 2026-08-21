import hashlib
from urllib.parse import urlsplit

from app.models import FailureEvidence
from app.normalization.errors import extract_locator, normalize_error


def _endpoint(value: str) -> str:
    parsed = urlsplit(value)
    return parsed.path or value.split("?")[0]


def build_signature(evidence: FailureEvidence) -> str:
    failure = evidence.failure
    locator = extract_locator(failure.error_message) or ""
    network = sorted(
        f"{event.method}:{_endpoint(event.url)}:{event.status_code or event.failure_reason or ''}"
        for event in evidence.network_failures
    )
    stable = "|".join(
        [
            failure.test_id,
            normalize_error(failure.error_message),
            locator,
            failure.browser or "",
            *network,
        ]
    )
    return hashlib.sha256(stable.encode()).hexdigest()[:24]
