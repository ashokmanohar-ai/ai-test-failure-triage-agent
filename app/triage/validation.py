import re
from urllib.parse import urlsplit

from app.models import FailureEvidence, TriageResult

UNSAFE_ACTION = re.compile(
    r"(?i)(rm\s+-rf|git\s+push\s+--force|disable\s+all\s+tests|curl.+\|\s*(?:sh|bash))"
)
ENDPOINT = re.compile(r"(?<!\w)/(?:api/)?[a-z0-9_./{}-]+", re.I)


def validate_claims(result: TriageResult, evidence: FailureEvidence) -> list[str]:
    known = {urlsplit(item.url).path for item in evidence.network_failures}
    unsupported: list[str] = []
    for claim in [result.probable_root_cause, *result.evidence_for]:
        for endpoint in ENDPOINT.findall(claim):
            normalized = endpoint.rstrip(".,)")
            if normalized.startswith(("/api/", "/v1/")) and normalized not in known:
                unsupported.append(
                    f"UNSUPPORTED_TRIAGE_CLAIM: endpoint {normalized} not present in network evidence"
                )
    for action in result.recommended_actions:
        if UNSAFE_ACTION.search(action):
            unsupported.append("UNSAFE_RECOMMENDATION_BLOCKED")
    return sorted(set(unsupported))
