from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any

import yaml

from .errors import InvalidStateError


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InvalidStateError(f"Required file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise InvalidStateError(f"Invalid YAML in {path}: {exc}") from exc

    if value is None:
        return {}
    if not isinstance(value, dict):
        raise InvalidStateError(f"Expected a YAML mapping in {path}")
    return value


def write_yaml_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = yaml.safe_dump(
        value,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    )
    fd, temporary_name = tempfile.mkstemp(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_markdown_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise InvalidStateError(f"Missing YAML frontmatter in {path}")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as exc:
        raise InvalidStateError(f"Unterminated YAML frontmatter in {path}") from exc
    try:
        value = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        raise InvalidStateError(f"Invalid YAML frontmatter in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InvalidStateError(f"Expected frontmatter mapping in {path}")
    return value
