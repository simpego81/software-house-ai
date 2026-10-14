from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .errors import InvalidStateError
from .io import parse_markdown_frontmatter

CLOSED_WORDS = ("closed", "decided", "accepted", "deferred", "rejected", "escalated")
OPEN_WORDS = ("open", "in progress", "in_progress", "draft")

_STATUS_LINE = re.compile(r"(?im)^\*{0,2}status:?\*{0,2}:?\s*\*{0,2}\s*(?P<value>[^\r\n]+)")
_TRACK_LINE = re.compile(r"(?im)^\*{0,2}track:?\*{0,2}:?\s*\*{0,2}\s*(?P<value>[^\r\n]+)")
_STEP_HEADING = re.compile(r"(?m)^#{2,3}\s+Step\s+(?P<n>\d+)")
_DECISION = re.compile(
    r"(?i)\b(?:final\s+)?decision\W{0,4}(?P<value>accepted with conditions|accepted|rejected|deferred|escalated)"
)


@dataclass(frozen=True)
class LegacyCycle:
    path: Path
    number: int | None
    format: str
    status: str | None
    track: str | None
    steps: int
    decision: str | None
    final_status: str | None = None

    @property
    def stale_header(self) -> bool:
        """Header says open but a later status line in the same file says closed."""
        if not self.is_open or self.final_status is None:
            return False
        return self.final_status.strip().lower().strip("* ").startswith(CLOSED_WORDS)

    @property
    def is_closed(self) -> bool:
        if self.status is None:
            return False
        normalized = self.status.strip().lower().strip("* ")
        return normalized.startswith(CLOSED_WORDS)

    @property
    def is_open(self) -> bool:
        if self.status is None:
            return False
        normalized = self.status.strip().lower().strip("* ")
        return normalized.startswith(OPEN_WORDS)

    @property
    def track_code(self) -> str | None:
        if not self.track:
            return None
        match = re.match(r"\s*\*{0,2}\s*(SA|S|M|F)\b", self.track, re.IGNORECASE)
        return match.group(1).upper() if match else None


def _clean(value: str) -> str:
    return value.strip().strip("*").strip()


def read_legacy_cycle(path: Path) -> LegacyCycle:
    text = path.read_text(encoding="utf-8", errors="replace")
    number_match = re.search(r"cycle-(\d+)", path.stem)
    number = int(number_match.group(1)) if number_match else None
    steps = len(_STEP_HEADING.findall(text))
    decision_match = _DECISION.search(text)
    decision = decision_match.group("value").upper() if decision_match else None

    try:
        frontmatter = parse_markdown_frontmatter(path)
    except InvalidStateError:
        frontmatter = None

    if frontmatter is not None:
        status = str(frontmatter.get("status")) if frontmatter.get("status") is not None else None
        track = str(frontmatter.get("track")) if frontmatter.get("track") is not None else None
        if track is None:
            header_track = _TRACK_LINE.search(text)
            track = _clean(header_track.group("value")) if header_track else None
        return LegacyCycle(path, number, "frontmatter", status, track, steps, decision)

    status_match = _STATUS_LINE.search(text[:2000])
    track_match = _TRACK_LINE.search(text[:2000])
    declared = [_clean(item.group("value")) for item in _STATUS_LINE.finditer(text)]
    final_status = declared[-1] if declared else None
    return LegacyCycle(
        path,
        number,
        "header" if status_match else "unknown",
        _clean(status_match.group("value")) if status_match else None,
        _clean(track_match.group("value")) if track_match else None,
        steps,
        decision,
        final_status,
    )


def missing_numbers(numbers: list[int]) -> list[int]:
    if not numbers:
        return []
    present = set(numbers)
    return [value for value in range(1, max(numbers) + 1) if value not in present]
