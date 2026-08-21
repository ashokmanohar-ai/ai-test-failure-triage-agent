import re
from collections.abc import Mapping
from typing import Any

SENSITIVE_KEYS = re.compile(
    r"^(authorization|proxy-authorization|cookie|set-cookie|x-api-key|api[-_]?key|password|token|secret)$",
    re.IGNORECASE,
)
BEARER_PATTERN = re.compile(r"(?i)\b(bearer|basic)\s+[a-z0-9._~+/=-]+")
KEY_VALUE_PATTERN = re.compile(r"(?i)\b(api[_-]?key|password|token|secret)\s*[:=]\s*[^\s,;]+")
EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d .()-]{7,}\d)(?!\w)")


def sanitize_text(value: str, *, redact_pii: bool = True) -> str:
    """Mask common secrets and optional PII before persistence or model use."""
    redacted = BEARER_PATTERN.sub("[REDACTED_AUTH]", value)
    redacted = KEY_VALUE_PATTERN.sub(lambda m: f"{m.group(1)}=[REDACTED]", redacted)
    if redact_pii:
        redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", redacted)
        redacted = PHONE_PATTERN.sub("[REDACTED_PHONE]", redacted)
    return redacted


def sanitize_mapping(value: Mapping[str, Any], *, redact_pii: bool = True) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, item in value.items():
        if SENSITIVE_KEYS.match(key):
            sanitized[key] = "[REDACTED]"
        elif isinstance(item, str):
            sanitized[key] = sanitize_text(item, redact_pii=redact_pii)
        elif isinstance(item, Mapping):
            sanitized[key] = sanitize_mapping(item, redact_pii=redact_pii)
        elif isinstance(item, list):
            sanitized[key] = [
                sanitize_mapping(v, redact_pii=redact_pii)
                if isinstance(v, Mapping)
                else sanitize_text(v, redact_pii=redact_pii)
                if isinstance(v, str)
                else v
                for v in item
            ]
        else:
            sanitized[key] = item
    return sanitized


def neutralize_prompt_injection(value: str) -> str:
    """Label untrusted instructions as evidence without deleting forensic content."""
    injection_markers = (
        "ignore previous instructions",
        "system prompt",
        "developer message",
        "reveal your prompt",
        "act as",
    )
    if any(marker in value.casefold() for marker in injection_markers):
        return f"[UNTRUSTED_INSTRUCTION_AS_DATA] {value}"
    return value
