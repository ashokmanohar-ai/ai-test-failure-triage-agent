from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.dependencies import agent, repository
from app.collectors.playwright_results import collect_playwright_json
from app.config import get_settings
from app.models import FailureEvidence, PlaywrightImportRequest, TriageResult
from app.persistence import FailureRepository
from app.reporting import write_html
from app.security.paths import UnsafeArtifactPath, resolve_safe_path
from app.triage import FailureTriageAgent

router = APIRouter(prefix="/api/v1")


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "UP", "provider": get_settings().model_provider}


@router.get("/failures")
def list_failures(repo: FailureRepository = Depends(repository)) -> list[dict[str, object]]:
    return repo.list_failures()


@router.post("/failures", status_code=status.HTTP_201_CREATED)
def create_failure(
    evidence: FailureEvidence, repo: FailureRepository = Depends(repository)
) -> dict[str, str]:
    repo.save_evidence(evidence)
    return {"failure_id": evidence.failure.failure_id, "status": "accepted"}


@router.post("/import/playwright", status_code=status.HTTP_201_CREATED)
def import_playwright(
    request: PlaywrightImportRequest, repo: FailureRepository = Depends(repository)
) -> dict[str, object]:
    root = get_settings().artifact_root
    try:
        report_path = resolve_safe_path(root, request.report_path)
        records = collect_playwright_json(report_path, workspace_root=root)
    except (UnsafeArtifactPath, FileNotFoundError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    for evidence in records:
        repo.save_evidence(evidence)
    return {"imported": len(records), "failure_ids": [item.failure.failure_id for item in records]}


@router.get("/failures/{failure_id}")
def get_failure(failure_id: str, repo: FailureRepository = Depends(repository)) -> FailureEvidence:
    try:
        return repo.get_evidence(failure_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Failure not found") from exc


@router.post("/failures/{failure_id}/triage")
async def triage_failure(
    failure_id: str,
    repo: FailureRepository = Depends(repository),
    triage_agent: FailureTriageAgent = Depends(agent),
) -> TriageResult:
    try:
        evidence = repo.get_evidence(failure_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Failure not found") from exc
    result = await triage_agent.triage(evidence)
    repo.save_evidence(evidence)
    repo.save_triage(result)
    return result


@router.get("/failures/{failure_id}/timeline")
def timeline(
    failure_id: str, repo: FailureRepository = Depends(repository)
) -> list[dict[str, str]]:
    try:
        evidence = repo.get_evidence(failure_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Failure not found") from exc
    return [
        {"timestamp": item.timestamp.isoformat(), "source": item.source, "event": item.event}
        for item in sorted(evidence.timeline, key=lambda event: event.timestamp)
    ]


@router.get("/failures/{failure_id}/report")
def report(failure_id: str, repo: FailureRepository = Depends(repository)) -> Response:
    try:
        evidence = repo.get_evidence(failure_id)
        result = repo.get_triage(failure_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Failure not found") from exc
    if result is None:
        raise HTTPException(status_code=409, detail="Failure has not been triaged")
    report_path = write_html(
        result, evidence, Path(get_settings().report_root) / f"{failure_id}.html"
    )
    return Response(report_path.read_text(encoding="utf-8"), media_type="text/html")
