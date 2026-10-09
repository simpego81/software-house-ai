from __future__ import annotations

from typing import Any

from .model import Evaluation, GUARDED_RISK_FLAGS, Outcome, Profile, require_profile


def evaluate_route(profile: Profile, risk: dict[str, Any]) -> Evaluation:
    result = Evaluation()
    guarded_triggers = [flag for flag in GUARDED_RISK_FLAGS if risk.get(flag) is True]
    if risk.get("blast_radius") == "high":
        guarded_triggers.append("blast_radius=high")
    if risk.get("native_verification_available") is False:
        guarded_triggers.append("native_verification_available=false")
    if risk.get("reversible") is False:
        guarded_triggers.append("reversible=false")

    if profile is Profile.DIRECT:
        result.add("DIRECT_NOT_A_CYCLE", "DIRECT work must not open a formal cycle")
    elif profile in (Profile.SPRINT, Profile.STANDARD) and guarded_triggers:
        result.add(
            "GUARDED_REQUIRED",
            "Risk requires GUARDED profile: " + ", ".join(guarded_triggers),
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


def evaluate_close(cycle: dict[str, Any], requested: Outcome = Outcome.ACCEPTED) -> Evaluation:
    result = Evaluation()
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
        if not cycle.get("pending_human"):
            result.add(
                "PROVISIONAL_REASON",
                "PROVISIONAL requires at least one pending_human entry",
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
    required_checks = [check for check in checks if check.get("required", True)]
    if not required_checks:
        result.add("REQUIRED_CHECK", "At least one required executable check is required")
    for check in required_checks:
        check_id = check.get("id", "<unnamed>")
        if check.get("status") != "passed":
            result.add("CHECK_NOT_PASSED", f"Required check {check_id} did not pass")
        if check.get("exit_code") != 0:
            result.add("CHECK_EXIT_CODE", f"Required check {check_id} has no successful exit code")
        if not check.get("evidence"):
            result.add("CHECK_EVIDENCE", f"Required check {check_id} has no evidence reference")

    if cycle.get("pending_human"):
        unresolved = [
            item for item in cycle["pending_human"] if item.get("status", "pending") != "verified"
        ]
        if unresolved:
            result.add("PENDING_HUMAN", "Unresolved human verification blocks acceptance")

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
            if challenge.get("reviewer_context") == "same-model":
                result.add(
                    "CHALLENGE_NOT_INDEPENDENT",
                    "Challenge used the same model/context and is not independent",
                    severity="warning",
                )
        if not (cycle.get("rollback") or {}).get("strategy"):
            result.add("ROLLBACK_STRATEGY", f"{profile.value} requires rollback.strategy")

    if profile is Profile.GUARDED and not (cycle.get("approval") or {}).get("owner"):
        result.add("OWNER_APPROVAL", "GUARDED acceptance requires approval.owner")

    if requested is Outcome.REVERTED and not (cycle.get("rollback") or {}).get("verified"):
        result.add("REVERT_NOT_VERIFIED", "REVERTED requires rollback.verified=true")

    return result
