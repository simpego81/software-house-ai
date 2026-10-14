from __future__ import annotations

from statistics import median
from typing import Any

from .errors import InvalidStateError
from .store import utc_now

VERDICTS = ("accept", "conditional", "reject")

# Failure criteria fixed before the pilot starts. Change them only before collecting data.
THRESHOLDS = {
    "false_blocks": 2,
    "escaped_defects": 1,
    "manual_edit_cycles": 2,
}
MIN_SAMPLE = 5


def observations(cycle: dict[str, Any]) -> dict[str, Any]:
    return cycle.setdefault("observations", {})


def record_judgement(cycle: dict[str, Any], verdict: str, by: str, reason: str | None) -> None:
    if verdict not in VERDICTS:
        raise InvalidStateError(f"verdict must be one of {', '.join(VERDICTS)}")
    block = observations(cycle)
    if block.get("close_attempts"):
        raise InvalidStateError(
            "The close policy was already evaluated for this cycle; a judgement recorded now would not be blind"
        )
    if block.get("judgement"):
        raise InvalidStateError("A judgement is already recorded for this cycle and cannot be changed")
    block["judgement"] = {"verdict": verdict, "by": by, "reason": reason, "recorded_at": utc_now()}


def record_skip(cycle: dict[str, Any]) -> None:
    block = observations(cycle)
    if not block.get("judgement"):
        block["judgement"] = {"verdict": "skipped", "recorded_at": utc_now()}


def record_session(cycle: dict[str, Any], minutes: int) -> None:
    if minutes < 0:
        raise InvalidStateError("minutes must not be negative")
    effort = observations(cycle).setdefault("effort", {"sessions": 0, "minutes": 0})
    effort["sessions"] += 1
    effort["minutes"] += minutes


def record_friction(cycle: dict[str, Any], text: str) -> None:
    observations(cycle).setdefault("friction", []).append({"at": utc_now(), "text": text})


def record_defect(cycle: dict[str, Any], text: str) -> None:
    observations(cycle).setdefault("escaped_defects", []).append({"at": utc_now(), "text": text})


def record_check_run(cycle: dict[str, Any], passed: bool) -> None:
    block = observations(cycle)
    block["check_runs"] = block.get("check_runs", 0) + 1
    if not passed:
        block["check_failures"] = block.get("check_failures", 0) + 1


def record_close_attempt(cycle: dict[str, Any], allowed: bool, blockers: list[str]) -> None:
    observations(cycle).setdefault("close_attempts", []).append(
        {"at": utc_now(), "allowed": allowed, "blockers": blockers}
    )


def record_manual_edit(cycle: dict[str, Any]) -> None:
    observations(cycle).setdefault("manual_edits", []).append({"detected_at": utc_now()})


def _v2_verdict(cycle: dict[str, Any]) -> str | None:
    if cycle.get("status") == "closed":
        outcome = cycle.get("outcome")
        if outcome == "ACCEPTED":
            return "accept"
        return "conditional" if outcome == "PROVISIONAL" else "reject"
    attempts = observations(cycle).get("close_attempts") or []
    if not attempts:
        return None
    return "accept" if attempts[-1]["allowed"] else "reject"


def aggregate(cycles: list[dict[str, Any]], baseline_minutes: float | None = None) -> dict[str, Any]:
    judged = agree = false_blocks = false_passes = other_disagreements = 0
    unjudged = skipped = 0
    minutes: list[float] = []
    sessions: list[float] = []
    escaped = manual_edit_cycles = failed_then_passed = 0
    friction = 0
    by_context: dict[str, dict[str, int]] = {}
    pending: dict[str, int] = {}

    for cycle in cycles:
        block = cycle.get("observations") or {}
        judgement = block.get("judgement") or {}
        verdict = judgement.get("verdict")
        v2 = _v2_verdict(cycle)
        if verdict == "skipped":
            skipped += 1
        elif verdict in VERDICTS:
            if v2 is None:
                unjudged += 1
            else:
                judged += 1
                if verdict == v2:
                    agree += 1
                elif verdict == "accept":
                    false_blocks += 1
                elif v2 == "accept":
                    false_passes += 1
                else:
                    other_disagreements += 1
        else:
            unjudged += 1

        effort = block.get("effort")
        if effort:
            minutes.append(effort.get("minutes", 0))
            sessions.append(effort.get("sessions", 0))
        escaped += len(block.get("escaped_defects") or [])
        friction += len(block.get("friction") or [])
        if block.get("manual_edits"):
            manual_edit_cycles += 1
        if block.get("check_failures") and cycle.get("status") == "closed":
            failed_then_passed += 1
        for challenge in cycle.get("challenges") or []:
            bucket = by_context.setdefault(str(challenge.get("reviewer_context")), {"challenges": 0, "findings": 0})
            bucket["challenges"] += 1
            bucket["findings"] += int(challenge.get("findings") or 0)
        for item in cycle.get("pending_human") or []:
            status = str(item.get("status", "pending"))
            pending[status] = pending.get(status, 0) + 1

    median_minutes = round(median(minutes), 1) if minutes else None
    values = {
        "false_blocks": false_blocks,
        "escaped_defects": escaped,
        "manual_edit_cycles": manual_edit_cycles,
    }
    criteria = {
        name: {"value": values[name], "threshold": limit, "tripped": values[name] >= limit}
        for name, limit in THRESHOLDS.items()
    }
    if baseline_minutes is not None and median_minutes is not None:
        criteria["median_minutes_vs_baseline"] = {
            "value": median_minutes,
            "threshold": baseline_minutes,
            "tripped": median_minutes > baseline_minutes,
        }
    return {
        "sample_size": len(cycles),
        "sufficient_sample": len(cycles) >= MIN_SAMPLE,
        "judgement_vs_v2": {
            "compared": judged,
            "agree": agree,
            "false_blocks": false_blocks,
            "false_passes": false_passes,
            "other_disagreements": other_disagreements,
            "not_judged": unjudged,
            "judgement_skipped": skipped,
        },
        "effort": {
            "cycles_with_effort": len(minutes),
            "median_minutes": median_minutes,
            "median_sessions": median(sessions) if sessions else None,
        },
        "cycles_where_a_check_failed_before_passing": failed_then_passed,
        "cycles_with_manual_edits_detected": manual_edit_cycles,
        "escaped_defects": escaped,
        "friction_notes": friction,
        "challenge_findings_by_reviewer_context": by_context,
        "pending_human_by_status": pending,
        "failure_criteria": criteria,
        "any_criterion_tripped": any(item["tripped"] for item in criteria.values()),
    }
