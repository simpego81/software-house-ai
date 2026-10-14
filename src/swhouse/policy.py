from __future__ import annotations

from datetime import date
from typing import Any, Iterable

from .model import (
    BLAST_RADIUS_VALUES,
    Evaluation,
    GUARDED_RISK_FLAGS,
    KNOWN_RISK_KEYS,
    Outcome,
    PENDING_RESOLVED,
    Profile,
    require_profile,
)

INDEPENDENT_CONTEXTS = ("fresh-context", "different-model", "human", "tool")


def guarded_triggers(risk: dict[str, Any]) -> list[str]:
    triggers = [flag for flag in GUARDED_RISK_FLAGS if risk.get(flag) is True]
    if risk.get("blast_radius") == "high":
        triggers.append("blast_radius=high")
    if risk.get("native_verification_available") is False:
        triggers.append("native_verification_available=false")
    if risk.get("reversible") is False:
        triggers.append("reversible=false")
    return triggers


def recommend_profile(risk: dict[str, Any]) -> tuple[Profile, list[str]]:
    """Deterministic minimum profile for a declared risk. Never recommends DIRECT/REVERT/EXPERIMENT."""
    triggers = guarded_triggers(risk)
    if triggers:
        return Profile.GUARDED, triggers
    sprint = evaluate_route(Profile.SPRINT, risk)
    if sprint.allowed:
        return Profile.SPRINT, []
    return Profile.STANDARD, [finding.message for finding in sprint.blockers]


def evaluate_route(profile: Profile, risk: dict[str, Any]) -> Evaluation:
    result = Evaluation()

    unknown = sorted(set(risk) - KNOWN_RISK_KEYS)
    if unknown:
        result.add(
            "RISK_UNKNOWN_KEY",
            "Unknown risk key(s) would be ignored by the router: "
            + ", ".join(unknown)
            + ". Known keys: "
            + ", ".join(sorted(KNOWN_RISK_KEYS)),
        )
    for flag in (*GUARDED_RISK_FLAGS, "reversible", "native_verification_available"):
        if flag in risk and risk[flag] is not None and not isinstance(risk[flag], bool):
            result.add("RISK_FLAG_TYPE", f"Risk flag {flag} must be true or false, got {risk[flag]!r}")
    if "blast_radius" in risk and risk["blast_radius"] not in BLAST_RADIUS_VALUES:
        result.add(
            "RISK_BLAST_RADIUS",
            f"blast_radius must be one of {', '.join(BLAST_RADIUS_VALUES)}, got {risk['blast_radius']!r}",
        )

    triggers = guarded_triggers(risk)

    if profile is Profile.DIRECT:
        result.add("DIRECT_NOT_A_CYCLE", "DIRECT work must not open a formal cycle")
    elif profile in (Profile.SPRINT, Profile.STANDARD) and triggers:
        result.add(
            "GUARDED_REQUIRED",
            "Risk requires GUARDED profile: " + ", ".join(triggers),
        )

    if profile is Profile.SPRINT:
        if risk.get("blast_radius") not in (None, "low"):
            result.add("SPRINT_BLAST_RADIUS", "SPRINT requires low blast radius")
        if risk.get("reversible") is not True:
            result.add("SPRINT_REVERSIBILITY", "SPRINT requires reversible=true")
        if risk.get("native_verification_available") is not True:
            result.add(
                "SPRINT_VERIFICATION",
                "SPRINT requires native_verification_available=true",
            )

    if profile is Profile.REVERT and not risk.get("known_good_baseline"):
        result.add("REVERT_BASELINE", "REVERT requires a known good baseline")

    if profile is Profile.EXPERIMENT:
        if not risk.get("bounded_blast_radius"):
            result.add("EXPERIMENT_BOUNDARY", "EXPERIMENT requires bounded_blast_radius=true")
        if not risk.get("stop_condition"):
            result.add("EXPERIMENT_STOP", "EXPERIMENT requires a stop condition")

    return result


def _pending_state(item: dict[str, Any], today: date) -> str:
    status = item.get("status", "pending")
    if status in PENDING_RESOLVED:
        return "resolved"
    if status == "waived":
        expires = item.get("expires")
        try:
            expiry = date.fromisoformat(str(expires))
        except ValueError:
            return "waiver_invalid"
        if not item.get("ref"):
            return "waiver_invalid"
        return "waiver_active" if expiry >= today else "waiver_expired"
    return "unresolved"


def evaluate_close(
    cycle: dict[str, Any],
    requested: Outcome = Outcome.ACCEPTED,
    configured_required: Iterable[str] | None = None,
    require_independent_guarded: bool = False,
    strict: bool = False,
    today: date | None = None,
) -> Evaluation:
    """Evaluate close policy.

    `configured_required` is the list of required check ids declared by the project's
    validation file for this profile. When given, those checks cannot be dropped or
    replaced by editing the cycle record: the validation file is the contract.
    `strict` (enforced governance) additionally demands a non-empty contract and an
    externally referenced Owner approval for GUARDED cycles.
    """
    result = Evaluation()
    today = today or date.today()
    profile = require_profile(cycle.get("profile"))

    route = evaluate_route(profile, cycle.get("risk") or {})
    result.findings.extend(route.findings)

    if requested in (Outcome.REJECTED, Outcome.DEFERRED):
        if not cycle.get("resolution", {}).get("reason"):
            result.add("RESOLUTION_REASON", f"{requested.value} requires resolution.reason")
        if requested is Outcome.DEFERRED and not cycle.get("resolution", {}).get("reopen_trigger"):
            result.add("REOPEN_TRIGGER", "DEFERRED requires resolution.reopen_trigger")
        return result

    if requested is Outcome.PROVISIONAL:
        if not any(_pending_state(item, today) == "unresolved" for item in cycle.get("pending_human") or []):
            result.add(
                "PROVISIONAL_REASON",
                "PROVISIONAL requires at least one unresolved pending_human entry",
            )
        return result

    if requested is Outcome.REVERTED and profile is not Profile.REVERT:
        result.add("REVERT_PROFILE", "REVERTED outcome requires REVERT profile")

    criteria = cycle.get("acceptance_criteria") or []
    if not criteria:
        result.add("ACCEPTANCE_CRITERIA", "At least one acceptance criterion is required")
    for criterion in criteria:
        if criterion.get("status") != "met":
            result.add(
                "CRITERION_NOT_MET",
                f"Acceptance criterion {criterion.get('id', '<unnamed>')} is not met",
            )

    change = cycle.get("change") or {}
    if not change.get("ref"):
        result.add("CHANGE_REF", "A change/artifact reference is required")

    checks = cycle.get("checks") or []
    by_id = {check.get("id"): check for check in checks}
    contract_ids = list(configured_required) if configured_required is not None else []
    if strict and configured_required is not None and not contract_ids:
        result.add(
            "CONTRACT_EMPTY",
            "Enforced governance needs at least one required check declared in .swhouse/validation.yaml "
            "for this profile; an ad-hoc command is not a validation contract",
        )
    for check_id in contract_ids:
        if check_id not in by_id:
            result.add(
                "CONTRACT_CHECK_MISSING",
                f"Check {check_id} is required by the validation file but absent from the cycle",
            )
        elif not by_id[check_id].get("required", True):
            result.add(
                "CONTRACT_CHECK_DOWNGRADED",
                f"Check {check_id} is required by the validation file but marked optional in the cycle",
            )
    required_checks = [
        check for check in checks if check.get("required", True) or check.get("id") in contract_ids
    ]
    if not required_checks:
        result.add(
            "REQUIRED_CHECK",
            "At least one required executable check is required; declare it in .swhouse/validation.yaml",
        )
    for check in required_checks:
        check_id = check.get("id", "<unnamed>")
        if check.get("status") != "passed":
            result.add("CHECK_NOT_PASSED", f"Required check {check_id} did not pass")
        if check.get("exit_code") != 0:
            result.add("CHECK_EXIT_CODE", f"Required check {check_id} has no successful exit code")
        if not check.get("evidence"):
            result.add("CHECK_EVIDENCE", f"Required check {check_id} has no evidence reference")

    for item in cycle.get("pending_human") or []:
        state = _pending_state(item, today)
        label = item.get("id", "<unnamed>")
        if state == "unresolved":
            result.add("PENDING_HUMAN", f"Unresolved human verification {label} blocks acceptance")
        elif state == "waiver_invalid":
            result.add(
                "WAIVER_INVALID",
                f"Waiver for {label} needs an ISO expiry date and a reference to the Owner decision",
            )
        elif state == "waiver_expired":
            result.add("WAIVER_EXPIRED", f"Waiver for {label} expired on {item.get('expires')}")
        elif state == "waiver_active":
            result.add(
                "WAIVER_ACTIVE",
                f"Human verification {label} is waived until {item.get('expires')}",
                severity="warning",
            )

    for finding in cycle.get("findings") or []:
        if finding.get("severity") in ("high", "critical") and finding.get("status") == "open":
            result.add(
                "BLOCKING_FINDING",
                f"Blocking finding {finding.get('id', '<unnamed>')} remains open",
            )

    if profile in (Profile.STANDARD, Profile.GUARDED):
        challenges = cycle.get("challenges") or []
        completed = [item for item in challenges if item.get("status") == "completed"]
        if not completed:
            result.add("CHALLENGE_REQUIRED", f"{profile.value} requires a completed challenge")
        for challenge in completed:
            if not challenge.get("artifact"):
                result.add("CHALLENGE_ARTIFACT", "Completed challenge requires an artifact reference")
        independent = [item for item in completed if item.get("reviewer_context") in INDEPENDENT_CONTEXTS]
        if completed and not independent:
            severity = "error" if profile is Profile.GUARDED and require_independent_guarded else "warning"
            result.add(
                "CHALLENGE_NOT_INDEPENDENT",
                "No challenge came from a different model, a human or a tool; "
                "same-model and fresh-context reviews share the author's blind spots",
                severity=severity,
            )
        if not (cycle.get("rollback") or {}).get("strategy"):
            result.add("ROLLBACK_STRATEGY", f"{profile.value} requires rollback.strategy")

    if profile is Profile.GUARDED:
        approval = cycle.get("approval") or {}
        if not approval.get("owner"):
            result.add("OWNER_APPROVAL", "GUARDED acceptance requires approval.owner")
        elif not approval.get("ref"):
            result.add(
                "OWNER_APPROVAL_UNVERIFIED",
                "Owner approval has no external reference (commit, PR, message id); "
                "the runtime cannot tell it apart from an agent's own assertion",
                severity="error" if strict else "warning",
            )

    if requested is Outcome.REVERTED and not (cycle.get("rollback") or {}).get("verified"):
        result.add("REVERT_NOT_VERIFIED", "REVERTED requires rollback.verified=true")

    return result
