import subprocess  # nosec B404 - arguments are fixed and shell=False
from pathlib import Path

from app.models import CodeChange

STATUS = {"A": "ADDED", "M": "MODIFIED", "D": "DELETED", "R": "RENAMED"}


def collect_git_changes(repo: Path, base_ref: str = "HEAD~1") -> list[CodeChange]:
    """Collect path-level Git changes without asking a model to invent metadata."""
    result = subprocess.run(  # noqa: S603
        ["git", "diff", "--name-status", base_ref, "HEAD", "--"],
        cwd=repo.resolve(),
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
        shell=False,
    )
    if result.returncode != 0:
        return []
    changes: list[CodeChange] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0][0]
        path = parts[-1]
        changes.append(CodeChange(path=path, change_type=STATUS.get(status, "MODIFIED")))
    return changes
