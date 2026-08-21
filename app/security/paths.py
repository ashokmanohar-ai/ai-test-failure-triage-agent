from pathlib import Path


class UnsafeArtifactPath(ValueError):
    """Raised when an artifact escapes its configured workspace."""


def resolve_safe_path(root: Path, candidate: str | Path, *, must_exist: bool = True) -> Path:
    root_resolved = root.resolve()
    path = Path(candidate)
    resolved = (root_resolved / path).resolve() if not path.is_absolute() else path.resolve()
    if resolved != root_resolved and root_resolved not in resolved.parents:
        raise UnsafeArtifactPath(f"Artifact path escapes configured root: {candidate}")
    if must_exist and not resolved.exists():
        raise FileNotFoundError(resolved)
    return resolved
