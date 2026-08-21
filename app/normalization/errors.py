import re

UUID = re.compile(
    r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I
)
ISO_TIMESTAMP = re.compile(r"\b\d{4}-\d{2}-\d{2}[T ][0-9:.+-]+Z?\b")
LONG_ID = re.compile(r"\b(order|user|account|request|trace|job)([-_])\d{4,}\b", re.I)
HEX_ADDRESS = re.compile(r"0x[0-9a-f]+", re.I)
WHITESPACE = re.compile(r"\s+")


def normalize_error(message: str) -> str:
    """Remove volatile identifiers while retaining semantically useful values."""
    value = UUID.sub("<uuid>", message)
    value = ISO_TIMESTAMP.sub("<timestamp>", value)
    value = LONG_ID.sub(r"\1\2<id>", value)
    value = HEX_ADDRESS.sub("<address>", value)
    return WHITESPACE.sub(" ", value).strip().casefold()


def extract_locator(message: str) -> str | None:
    patterns = (
        r"locator\((['\"])(.+?)\1\)",
        r"getByRole\((.+?)\)",
        r"waiting for (?:selector|locator) ['\"](.+?)['\"]",
    )
    for pattern in patterns:
        match = re.search(pattern, message, re.I)
        if match:
            return match.group(match.lastindex or 1)[:500]
    return None
