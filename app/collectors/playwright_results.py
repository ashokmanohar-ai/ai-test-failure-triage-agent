import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.models import ConsoleEvent, FailureEvidence, FailureRecord, NetworkFailure
from app.security.paths import resolve_safe_path


def _iter_specs(
    suites: list[dict[str, Any]], parents: tuple[str, ...] = ()
) -> list[tuple[tuple[str, ...], dict[str, Any]]]:
    found: list[tuple[tuple[str, ...], dict[str, Any]]] = []
    for suite in suites:
        title = str(suite.get("title", "suite"))
        current = (*parents, title)
        for spec in suite.get("specs", []):
            found.append((current, spec))
        found.extend(_iter_specs(suite.get("suites", []), current))
    return found


def collect_playwright_json(
    path: Path, *, workspace_root: Path | None = None
) -> list[FailureEvidence]:
    """Parse Playwright's structured JSON reporter output into normalized evidence."""
    safe_path = resolve_safe_path(workspace_root or path.parent, path)
    payload = json.loads(safe_path.read_text(encoding="utf-8"))
    output: list[FailureEvidence] = []
    for suite_path, spec in _iter_specs(payload.get("suites", [])):
        for test in spec.get("tests", []):
            project = str(test.get("projectName", "default"))
            results = test.get("results", [])
            final = results[-1] if results else {}
            status = str(final.get("status", "failed"))
            if status not in {"failed", "timedOut"}:
                continue
            errors = final.get("errors", [])
            error = errors[0] if errors else final.get("error", {})
            if isinstance(error, str):
                error = {"message": error}
            attachments = final.get("attachments", [])
            screenshots = [
                str(a["path"])
                for a in attachments
                if a.get("name") == "screenshot" and a.get("path")
            ]
            trace = next(
                (str(a["path"]) for a in attachments if a.get("name") == "trace" and a.get("path")),
                None,
            )
            metadata = final.get("metadata", {}) or {}
            network = [
                NetworkFailure.model_validate(item) for item in metadata.get("networkFailures", [])
            ]
            console = [
                ConsoleEvent.model_validate(item) for item in metadata.get("consoleErrors", [])
            ]
            output.append(
                FailureEvidence(
                    failure=FailureRecord(
                        failure_id=f"FAIL-{uuid4().hex[:12].upper()}",
                        test_id=str(spec.get("id", spec.get("title", "unknown"))),
                        test_name=str(spec.get("title", "unknown test")),
                        suite=" > ".join(suite_path),
                        status="TIMED_OUT" if status == "timedOut" else "FAILED",
                        error_message=str(error.get("message", "Unknown Playwright failure")),
                        stack_trace=error.get("stack"),
                        duration_ms=int(final.get("duration", 0)),
                        retry_count=int(final.get("retry", 0)),
                        browser=project,
                        project=project,
                        timestamp=datetime.now(UTC),
                    ),
                    screenshot_paths=screenshots,
                    trace_path=trace,
                    console_errors=console,
                    network_failures=network,
                    page_url=metadata.get("pageUrl"),
                    metadata={"source": "playwright-json", "report": str(safe_path)},
                )
            )
    return output
