from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def evidence_problem(project_root: Path, check: dict[str, Any]) -> tuple[str, str] | None:
    """Return (code, message) when a check's evidence cannot be trusted, else None.

    The digest detects edits made after the check ran. It does not stop an actor who
    can rewrite both the log and the cycle record; that needs an external CI log.
    """
    reference = check.get("evidence")
    if not reference:
        return None
    label = check.get("id", "<unnamed>")
    candidate = (project_root / str(reference)).resolve()
    try:
        candidate.relative_to(project_root)
    except ValueError:
        return ("EVIDENCE_OUTSIDE_PROJECT", f"Evidence for {label} resolves outside the project")
    if not candidate.is_file():
        return ("EVIDENCE_NOT_FOUND", f"Evidence for {label} does not exist: {reference}")
    recorded = check.get("evidence_sha256")
    if recorded and sha256_file(candidate) != recorded:
        return ("EVIDENCE_MODIFIED", f"Evidence for {label} changed after it was recorded: {reference}")
    return None
