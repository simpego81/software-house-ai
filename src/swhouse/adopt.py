from __future__ import annotations

from pathlib import Path
from typing import Any

from .doctor import diagnose
from .errors import InvalidStateError
from .evidence import sha256_file
from .io import load_yaml, write_yaml_atomic
from .store import Store, utc_now

MANIFEST = "adoption.yaml"
BASELINE = "doctor-baseline.yaml"
DIRECTORIES = ("cycles/open", "cycles/archive-v2", "evidence", "metrics")


def _relative(store: Store, path: Path) -> str:
    return str(path.relative_to(store.root)).replace("\\", "/")


def adopt(store: Store, checks: list[dict[str, Any]], apply: bool) -> list[str]:
    """Add v2 state next to legacy state. Legacy files are never read for write or modified."""
    manifest_path = store.root / MANIFEST
    if manifest_path.exists():
        raise InvalidStateError(
            f"{MANIFEST} already exists: this instance was adopted. Use --rollback to undo it first."
        )
    config_path = store.root / "config.yaml"
    validation_path = store.root / "validation.yaml"
    for existing in (config_path, validation_path):
        if existing.exists():
            raise InvalidStateError(
                f"{existing.name} already exists and was not created by adopt; refusing to overwrite it"
            )

    lines: list[str] = []
    created_files: list[Path] = []
    created_dirs: list[Path] = []

    config = {
        "schema_version": 2,
        "mode": "shadow",
        "concurrent_cycles": False,
        "validation_file": "validation.yaml",
    }
    validation = {
        "schema_version": 2,
        "checks": [
            {
                "id": item["id"],
                "description": item.get("description", "Declared during adoption"),
                "command": item["command"],
                "profiles": ["SPRINT", "STANDARD", "GUARDED", "REVERT", "EXPERIMENT"],
                "required": True,
                "timeout_seconds": 300,
            }
            for item in checks
        ],
    }
    if not checks:
        lines.append(
            "WARNING no --check declared: validation.yaml will be empty and no cycle can close until "
            "you add a required check (e.g. --check tests='python -m pytest')"
        )

    diagnostics = diagnose(store)
    known = [item for item in diagnostics if item.severity in ("error", "warning")]
    baseline = {
        "version": 1,
        "generated_at": utc_now(),
        "note": "Pre-existing drift accepted at adoption. New drift is reported as an error.",
        "allowed": [
            {
                "code": item.code,
                **({"path": _relative_project(store, item.path)} if item.path else {}),
            }
            for item in known
            if item.severity == "error"
        ],
    }

    for directory in DIRECTORIES:
        target = store.root / directory
        if not target.exists():
            created_dirs.append(target)
            lines.append(f"CREATE dir  .swhouse/{directory}/")
    for target, label in ((config_path, "config.yaml"), (validation_path, "validation.yaml")):
        created_files.append(target)
        lines.append(f"CREATE file .swhouse/{label}")
    baseline_path = store.root / BASELINE
    created_files.append(baseline_path)
    lines.append(
        f"CREATE file .swhouse/{BASELINE} ({len(baseline['allowed'])} known error(s), "
        f"{sum(1 for item in known if item.severity == 'warning')} warning(s) stay visible)"
    )
    lines.append("UNCHANGED legacy cycles, memory, reputation, metrics/summary.yaml, instance.yaml")

    if not apply:
        return lines

    for directory in created_dirs:
        directory.mkdir(parents=True, exist_ok=True)
    write_yaml_atomic(config_path, config)
    write_yaml_atomic(validation_path, validation)
    write_yaml_atomic(baseline_path, baseline)
    manifest = {
        "version": 1,
        "adopted_at": utc_now(),
        "directories": [_relative(store, path) for path in created_dirs],
        "files": [{"path": _relative(store, path), "sha256": sha256_file(path)} for path in created_files],
    }
    write_yaml_atomic(manifest_path, manifest)
    lines.append(f"WROTE .swhouse/{MANIFEST}")
    return lines


def rollback_adoption(store: Store, apply: bool) -> list[str]:
    manifest_path = store.root / MANIFEST
    if not manifest_path.exists():
        raise InvalidStateError(f"No {MANIFEST}: nothing was adopted, nothing to roll back")
    manifest = load_yaml(manifest_path)
    lines: list[str] = []
    for item in manifest.get("files") or []:
        path = store.root / str(item["path"])
        if not path.exists():
            lines.append(f"SKIP   .swhouse/{item['path']} (already gone)")
        elif sha256_file(path) != item.get("sha256"):
            lines.append(f"KEEP   .swhouse/{item['path']} (edited since adoption; review and delete by hand)")
        else:
            lines.append(f"REMOVE .swhouse/{item['path']}")
            if apply:
                path.unlink()
    for directory in reversed(manifest.get("directories") or []):
        path = store.root / str(directory)
        if path.is_dir() and not any(path.iterdir()):
            lines.append(f"REMOVE .swhouse/{directory}/ (empty)")
            if apply:
                path.rmdir()
        elif path.is_dir():
            lines.append(f"KEEP   .swhouse/{directory}/ (contains v2 cycles or evidence; archive them if needed)")
    if apply:
        manifest_path.unlink()
        lines.append(f"REMOVE .swhouse/{MANIFEST}")
    else:
        lines.append("DRY RUN: pass --apply to remove")
    return lines


def _relative_project(store: Store, path: Path) -> str:
    return str(path.relative_to(store.project_root)).replace("\\", "/")
