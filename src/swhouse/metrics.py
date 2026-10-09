from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Any

from .io import load_yaml
from .store import Store, utc_now


def generate_metrics(store: Store) -> dict[str, Any]:
    cycles = [load_yaml(path) for path in sorted(store.archive_v2_dir.glob("*.yaml"))]
    by_profile: dict[str, list[float]] = {}
    outcomes: dict[str, int] = {}
    outcomes_by_mode: dict[str, dict[str, int]] = {}
    verification_values: list[float] = []

    for cycle in cycles:
        outcome = str(cycle.get("outcome", "UNKNOWN"))
        outcomes[outcome] = outcomes.get(outcome, 0) + 1
        mode = str(cycle.get("governance_mode", "unknown"))
        mode_outcomes = outcomes_by_mode.setdefault(mode, {})
        mode_outcomes[outcome] = mode_outcomes.get(outcome, 0) + 1
        profile = str(cycle.get("profile", "UNKNOWN"))
        duration = _duration_hours(cycle.get("opened_at"), cycle.get("closed_at"))
        if duration is not None:
            by_profile.setdefault(profile, []).append(duration)

        required = [check for check in cycle.get("checks") or [] if check.get("required", True)]
        if required:
            complete = sum(
                1
                for check in required
                if check.get("status") == "passed"
                and check.get("exit_code") == 0
                and check.get("evidence")
                and _evidence_exists(store, check.get("evidence"))
            )
            verification_values.append(complete / len(required))

    return {
        "schema_version": 2,
        "generated_at": utc_now(),
        "source": "cycles/archive-v2",
        "cycles_closed": len(cycles),
        "outcomes": outcomes,
        "outcomes_by_governance_mode": outcomes_by_mode,
        "median_lead_time_hours_by_profile": {
            profile: round(median(values), 3) for profile, values in sorted(by_profile.items())
        },
        "verification_completeness": (
            round(sum(verification_values) / len(verification_values), 4)
            if verification_values
            else None
        ),
    }


def write_metrics(store: Store, metrics: dict[str, Any]) -> Path:
    destination = store.root / "metrics" / "generated.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destination


def _duration_hours(opened: Any, closed: Any) -> float | None:
    if not opened or not closed:
        return None
    try:
        start = datetime.fromisoformat(str(opened))
        end = datetime.fromisoformat(str(closed))
    except ValueError:
        return None
    return (end - start).total_seconds() / 3600


def _evidence_exists(store: Store, reference: Any) -> bool:
    candidate = (store.project_root / str(reference)).resolve()
    try:
        candidate.relative_to(store.project_root)
    except ValueError:
        return False
    return candidate.is_file()
