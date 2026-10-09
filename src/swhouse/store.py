from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import InvalidStateError
from .io import load_yaml, write_yaml_atomic


CYCLE_FILE_RE = re.compile(r"^(?:cycle-)?(?P<id>\d{3,})\.ya?ml$")


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class Store:
    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.root = self.project_root / ".swhouse"
        if not self.root.is_dir():
            raise InvalidStateError(f"No .swhouse directory under {self.project_root}")

    @property
    def open_dir(self) -> Path:
        return self.root / "cycles" / "open"

    @property
    def archive_v2_dir(self) -> Path:
        return self.root / "cycles" / "archive-v2"

    @property
    def evidence_dir(self) -> Path:
        return self.root / "evidence"

    def config(self) -> dict[str, Any]:
        path = self.root / "config.yaml"
        return load_yaml(path) if path.exists() else {}

    def validation(self) -> dict[str, Any]:
        configured = self.config().get("validation_file", "validation.yaml")
        path = self.root / str(configured)
        return load_yaml(path) if path.exists() else {}

    def open_paths(self) -> list[Path]:
        if not self.open_dir.exists():
            return []
        return sorted(path for path in self.open_dir.glob("*.yaml") if path.is_file())

    def get_open(self, cycle_id: str | None = None) -> tuple[Path, dict[str, Any]]:
        paths = self.open_paths()
        if cycle_id:
            normalized = normalize_cycle_id(cycle_id)
            matches = [path for path in paths if normalize_cycle_id(path.stem) == normalized]
            if not matches:
                raise InvalidStateError(f"Open cycle {normalized} not found")
            path = matches[0]
        elif len(paths) == 1:
            path = paths[0]
        elif not paths:
            raise InvalidStateError("No v2 cycle is open")
        else:
            raise InvalidStateError("Multiple cycles are open; specify --cycle")
        return path, load_yaml(path)

    def next_cycle_id(self) -> str:
        identifiers: list[int] = []
        for directory in (self.open_dir, self.archive_v2_dir):
            if directory.exists():
                for path in directory.glob("*.yaml"):
                    match = CYCLE_FILE_RE.match(path.name)
                    if match:
                        identifiers.append(int(match.group("id")))

        legacy_archive = self.root / "cycles" / "archive"
        if legacy_archive.exists():
            for path in legacy_archive.glob("cycle-*.md"):
                match = re.search(r"cycle-(\d+)", path.stem)
                if match:
                    identifiers.append(int(match.group(1)))

        return f"{max(identifiers, default=0) + 1:03d}"

    def create_cycle(self, cycle: dict[str, Any]) -> Path:
        if self.open_paths():
            config = self.config()
            if not config.get("concurrent_cycles", False):
                raise InvalidStateError("A v2 cycle is already open and concurrency is disabled")
        path = self.open_dir / f"{cycle['id']}.yaml"
        if path.exists():
            raise InvalidStateError(f"Cycle already exists: {cycle['id']}")
        write_yaml_atomic(path, cycle)
        return path

    def save_open(self, path: Path, cycle: dict[str, Any]) -> None:
        if path.parent.resolve() != self.open_dir.resolve():
            raise InvalidStateError("Refusing to update a cycle outside cycles/open")
        write_yaml_atomic(path, cycle)

    def archive(self, path: Path, cycle: dict[str, Any]) -> Path:
        destination = self.archive_v2_dir / path.name
        if destination.exists():
            raise InvalidStateError(f"Archive destination already exists: {destination}")
        write_yaml_atomic(destination, cycle)
        path.unlink()
        return destination


def normalize_cycle_id(value: str) -> str:
    match = re.search(r"(\d+)", value)
    if not match:
        raise InvalidStateError(f"Invalid cycle id: {value!r}")
    return f"{int(match.group(1)):03d}"
