from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

from .doctor import diagnose
from .errors import SwhouseError
from .io import load_yaml
from .metrics import generate_metrics, write_metrics
from .model import Outcome, Profile, require_outcome, require_profile
from .policy import evaluate_close, evaluate_route
from .store import Store, utc_now


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="swhouse", description="Software House AI runtime")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="project root (default: cwd)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    doctor = subparsers.add_parser("doctor", help="inspect legacy and v2 invariants without modifying state")
    doctor.add_argument("--baseline", type=Path, help="allow listed known diagnostics")
    subparsers.add_parser("status", help="show open v2 cycle state")

    start = subparsers.add_parser("start", help="open a v2 cycle")
    start.add_argument("problem")
    start.add_argument("--profile", required=True, choices=[item.value for item in Profile])
    start.add_argument("--criterion", action="append", default=[])
    start.add_argument("--risk", action="append", default=[], metavar="KEY=VALUE")

    set_change = subparsers.add_parser("set-change", help="set change/artifact reference")
    set_change.add_argument("reference")
    set_change.add_argument("--cycle")

    rollback = subparsers.add_parser("set-rollback", help="record a rollback strategy")
    rollback.add_argument("strategy")
    rollback.add_argument("--verified", action="store_true")
    rollback.add_argument("--cycle")

    approve = subparsers.add_parser("approve", help="record explicit Owner approval")
    approve.add_argument("owner")
    approve.add_argument("--cycle")

    challenge = subparsers.add_parser("record-challenge", help="record diff/artifact challenge evidence")
    challenge.add_argument("mode", choices=("logical", "adversarial", "ux"))
    challenge.add_argument(
        "--reviewer-context",
        required=True,
        choices=("same-model", "fresh-context", "different-model", "human", "tool"),
    )
    challenge.add_argument("--artifact", required=True)
    challenge.add_argument("--findings", type=int, default=0)
    challenge.add_argument("--cycle")

    resolve = subparsers.add_parser("resolve", help="record rejection/defer rationale")
    resolve.add_argument("reason")
    resolve.add_argument("--reopen-trigger")
    resolve.add_argument("--cycle")

    prepare_revert = subparsers.add_parser("prepare-revert", help="open a REVERT cycle for a Git commit")
    prepare_revert.add_argument("target")
    prepare_revert.add_argument("--reason", required=True)

    apply_revert = subparsers.add_parser("apply-revert", help="dry-run or apply the prepared Git revert")
    apply_revert.add_argument("--cycle")
    apply_revert.add_argument("--apply", action="store_true")

    criterion = subparsers.add_parser("criterion", help="update an acceptance criterion")
    criterion.add_argument("criterion_id")
    criterion.add_argument("status", choices=("pending", "met", "not_met"))
    criterion.add_argument("--cycle")

    run_check = subparsers.add_parser("run-check", help="execute and record an evidence-producing check")
    run_check.add_argument("check_id")
    run_check.add_argument("--cycle")
    run_check.add_argument("--optional", action="store_true")
    run_check.add_argument("check_command", nargs=argparse.REMAINDER)

    close = subparsers.add_parser("close", help="evaluate close policy and optionally archive")
    close.add_argument("--cycle")
    close.add_argument("--outcome", default="ACCEPTED", choices=[item.value for item in Outcome])
    close.add_argument("--apply", action="store_true", help="archive when policy allows")

    subparsers.add_parser("metrics", help="derive v2 metrics from archived cycles")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return dispatch(args)
    except SwhouseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def dispatch(args: argparse.Namespace) -> int:
    store = Store(args.root)
    if args.command == "doctor":
        return command_doctor(store, args.baseline)
    if args.command == "status":
        return command_status(store)
    if args.command == "start":
        return command_start(store, args)
    if args.command == "set-change":
        return command_set_change(store, args)
    if args.command == "set-rollback":
        return command_set_rollback(store, args)
    if args.command == "approve":
        return command_approve(store, args)
    if args.command == "record-challenge":
        return command_record_challenge(store, args)
    if args.command == "resolve":
        return command_resolve(store, args)
    if args.command == "prepare-revert":
        return command_prepare_revert(store, args)
    if args.command == "apply-revert":
        return command_apply_revert(store, args)
    if args.command == "criterion":
        return command_criterion(store, args)
    if args.command == "run-check":
        return command_run_check(store, args)
    if args.command == "close":
        return command_close(store, args)
    if args.command == "metrics":
        return command_metrics(store)
    raise AssertionError(f"Unhandled command: {args.command}")


def command_doctor(store: Store, baseline_path: Path | None = None) -> int:
    diagnostics = diagnose(store)
    allowed: set[tuple[str, str | None]] = set()
    if baseline_path:
        resolved = baseline_path if baseline_path.is_absolute() else store.project_root / baseline_path
        baseline = load_yaml(resolved)
        for item in baseline.get("allowed") or []:
            allowed.add((str(item.get("code")), normalize_path(item.get("path"))))
    for item in diagnostics:
        location = f" [{item.path.relative_to(store.project_root)}]" if item.path else ""
        key = (
            item.code,
            normalize_path(item.path.relative_to(store.project_root)) if item.path else None,
        )
        prefix = "KNOWN" if key in allowed else item.severity.upper()
        print(f"{prefix:7} {item.code}: {item.message}{location}")
    return 1 if any(
        item.severity == "error"
        and (
            item.code,
            normalize_path(item.path.relative_to(store.project_root)) if item.path else None,
        )
        not in allowed
        for item in diagnostics
    ) else 0


def command_status(store: Store) -> int:
    paths = store.open_paths()
    if not paths:
        print("No v2 cycle is open.")
        return 0
    for path in paths:
        from .io import load_yaml

        cycle = load_yaml(path)
        required = [item for item in cycle.get("checks") or [] if item.get("required", True)]
        passed = sum(1 for item in required if item.get("status") == "passed")
        print(
            f"{cycle.get('id')} {cycle.get('profile')} {cycle.get('status')} "
            f"mode={cycle.get('governance_mode', 'legacy')} | "
            f"criteria={len(cycle.get('acceptance_criteria') or [])} | checks={passed}/{len(required)} | "
            f"{cycle.get('problem')}"
        )
    return 0


def command_start(store: Store, args: argparse.Namespace) -> int:
    profile = require_profile(args.profile)
    risk = parse_key_values(args.risk)
    route = evaluate_route(profile, risk)
    if not route.allowed:
        print_evaluation(route)
        return 1
    cycle_id = store.next_cycle_id()
    configured_checks = checks_for_profile(store.validation(), profile)
    governance_mode = str(store.config().get("mode", "shadow"))
    cycle = {
        "schema_version": 2,
        "id": cycle_id,
        "status": "open",
        "governance_mode": governance_mode,
        "profile": profile.value,
        "problem": args.problem,
        "opened_at": utc_now(),
        "scope": {"in": [], "out": []},
        "acceptance_criteria": [
            {"id": f"AC-{index:02d}", "text": text, "status": "pending"}
            for index, text in enumerate(args.criterion, start=1)
        ],
        "risk": risk,
        "change": {"ref": None},
        "checks": configured_checks,
        "challenges": [],
        "findings": [],
        "pending_human": [],
        "rollback": {"strategy": None, "verified": False},
        "approval": {"owner": None},
        "resolution": {"reason": None, "reopen_trigger": None},
    }
    path = store.create_cycle(cycle)
    print(f"Opened cycle {cycle_id}: {path.relative_to(store.project_root)}")
    return 0


def command_set_change(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    cycle.setdefault("change", {})["ref"] = args.reference
    store.save_open(path, cycle)
    print(f"Cycle {cycle['id']} change ref: {args.reference}")
    return 0


def command_set_rollback(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    rollback = cycle.setdefault("rollback", {})
    rollback["strategy"] = args.strategy
    if args.verified:
        rollback["verified"] = True
    store.save_open(path, cycle)
    print(f"Cycle {cycle['id']} rollback strategy recorded")
    return 0


def command_approve(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    cycle.setdefault("approval", {})["owner"] = args.owner
    store.save_open(path, cycle)
    print(f"Cycle {cycle['id']} approved by Owner {args.owner}")
    return 0


def command_record_challenge(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    independent = args.reviewer_context in ("fresh-context", "different-model", "human", "tool")
    cycle.setdefault("challenges", []).append(
        {
            "mode": args.mode,
            "reviewer_context": args.reviewer_context,
            "independent": independent,
            "artifact": args.artifact,
            "findings": args.findings,
            "status": "completed",
            "recorded_at": utc_now(),
        }
    )
    store.save_open(path, cycle)
    label = "independent" if independent else "not independent"
    print(f"Cycle {cycle['id']} {args.mode} challenge recorded ({label})")
    return 0


def command_resolve(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    resolution = cycle.setdefault("resolution", {})
    resolution["reason"] = args.reason
    resolution["reopen_trigger"] = args.reopen_trigger
    store.save_open(path, cycle)
    print(f"Cycle {cycle['id']} resolution recorded")
    return 0


def command_prepare_revert(store: Store, args: argparse.Namespace) -> int:
    if args.target.startswith("-") or not re.fullmatch(r"[A-Za-z0-9._/@{}^~:+-]+", args.target):
        raise SwhouseError(f"Unsafe Git revision: {args.target!r}")
    target = git_output(store, "rev-parse", "--verify", f"{args.target}^{{commit}}")
    parents = git_output(store, "rev-list", "--parents", "-n", "1", target).split()
    if len(parents) > 2:
        raise SwhouseError("Merge commits require an explicit mainline and are not supported yet")
    if git_run(store, "merge-base", "--is-ancestor", target, "HEAD").returncode != 0:
        raise SwhouseError(f"Revert target is not an ancestor of HEAD: {target}")

    profile = Profile.REVERT
    cycle_id = store.next_cycle_id()
    cycle = {
        "schema_version": 2,
        "id": cycle_id,
        "status": "open",
        "governance_mode": str(store.config().get("mode", "shadow")),
        "profile": profile.value,
        "problem": f"Revert {target}: {args.reason}",
        "opened_at": utc_now(),
        "scope": {"in": [f"git:{target}"], "out": ["root-cause fix"]},
        "acceptance_criteria": [
            {"id": "AC-01", "text": "Known-good behavior is restored and verified", "status": "pending"}
        ],
        "risk": {
            "known_good_baseline": True,
            "reversible": True,
            "native_verification_available": True,
            "blast_radius": "recovery",
        },
        "change": {"ref": f"revert-target:{target}"},
        "checks": checks_for_profile(store.validation(), profile),
        "challenges": [],
        "findings": [],
        "pending_human": [],
        "rollback": {"strategy": None, "verified": False},
        "approval": {"owner": None},
        "resolution": {"reason": None, "reopen_trigger": None},
        "revert": {"target": target, "reason": args.reason, "status": "planned"},
    }
    path = store.create_cycle(cycle)
    print(f"Prepared REVERT cycle {cycle_id} for {target}: {path.relative_to(store.project_root)}")
    return 0


def command_apply_revert(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    if require_profile(cycle.get("profile")) is not Profile.REVERT:
        raise SwhouseError("apply-revert requires an open REVERT cycle")
    target = str((cycle.get("revert") or {}).get("target", ""))
    if not target:
        raise SwhouseError("REVERT cycle has no target")
    dirty = product_dirty_paths(store)
    if dirty:
        raise SwhouseError("Product working tree is not clean: " + ", ".join(dirty[:5]))
    if not args.apply:
        print(f"WOULD_RUN: git revert --no-edit {target}")
        return 0

    result = git_run(store, "revert", "--no-edit", target)
    evidence_dir = store.evidence_dir / str(cycle["id"])
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / "revert-apply.log"
    evidence_path.write_text(
        "$ git revert --no-edit "
        + target
        + "\n\nSTDOUT\n"
        + redact_sensitive(result.stdout)
        + "\nSTDERR\n"
        + redact_sensitive(result.stderr),
        encoding="utf-8",
    )
    revert = cycle.setdefault("revert", {})
    revert["applied_at"] = utc_now()
    revert["evidence"] = str(evidence_path.relative_to(store.project_root)).replace("\\", "/")
    if result.returncode == 0:
        revert_commit = git_output(store, "rev-parse", "HEAD")
        revert["status"] = "applied"
        revert["commit"] = revert_commit
        cycle.setdefault("change", {})["ref"] = f"revert-commit:{revert_commit}"
        cycle.setdefault("rollback", {})["strategy"] = f"revert the revert commit {revert_commit}"
        print(f"APPLIED: revert commit {revert_commit}")
    else:
        revert["status"] = "conflict"
        cycle.setdefault("findings", []).append(
            {
                "id": "REVERT-CONFLICT",
                "severity": "critical",
                "status": "open",
                "evidence": revert["evidence"],
            }
        )
        print(f"CONFLICT: Git revert failed; evidence: {revert['evidence']}")
    store.save_open(path, cycle)
    return result.returncode


def command_criterion(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    for criterion in cycle.get("acceptance_criteria") or []:
        if criterion.get("id") == args.criterion_id:
            criterion["status"] = args.status
            store.save_open(path, cycle)
            print(f"Cycle {cycle['id']} {args.criterion_id}: {args.status}")
            return 0
    raise SwhouseError(f"Criterion not found: {args.criterion_id}")


def command_run_check(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    command = list(args.check_command)
    if command and command[0] == "--":
        command = command[1:]
    existing = next(
        (item for item in cycle.get("checks") or [] if item.get("id") == args.check_id),
        None,
    )
    configured_command = list(existing.get("command") or []) if existing else []
    if not command:
        command = configured_command
    elif configured_command and command != configured_command:
        raise SwhouseError(
            f"Check {args.check_id} is configured as {configured_command!r}; refusing command substitution"
        )
    if not command:
        raise SwhouseError("run-check requires a configured command or arguments after --")

    timeout = int(existing.get("timeout_seconds", 300)) if existing else 300
    try:
        result = subprocess.run(
            command,
            cwd=store.project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        result = subprocess.CompletedProcess(
            command,
            124,
            stdout=_text_output(exc.stdout),
            stderr=f"Check timed out after {timeout} seconds\n" + _text_output(exc.stderr),
        )
    except OSError as exc:
        result = subprocess.CompletedProcess(command, 127, stdout="", stderr=f"Execution failed: {exc}\n")
    evidence_dir = store.evidence_dir / str(cycle["id"])
    evidence_dir.mkdir(parents=True, exist_ok=True)
    evidence_path = evidence_dir / f"{safe_name(args.check_id)}.log"
    redacted_command = [redact_sensitive(argument) for argument in command]
    evidence_path.write_text(
        "$ "
        + " ".join(redacted_command)
        + "\n\nSTDOUT\n"
        + redact_sensitive(result.stdout)
        + "\nSTDERR\n"
        + redact_sensitive(result.stderr),
        encoding="utf-8",
    )
    record = {
        "id": args.check_id,
        "command": redacted_command,
        "required": existing.get("required", True) if existing else not args.optional,
        "status": "passed" if result.returncode == 0 else "failed",
        "exit_code": result.returncode,
        "executed_at": utc_now(),
        "evidence": str(evidence_path.relative_to(store.project_root)).replace("\\", "/"),
    }
    checks = cycle.setdefault("checks", [])
    checks[:] = [item for item in checks if item.get("id") != args.check_id]
    checks.append(record)
    store.save_open(path, cycle)
    print(f"{record['status'].upper()} {args.check_id} (exit {result.returncode}) -> {record['evidence']}")
    return result.returncode


def command_close(store: Store, args: argparse.Namespace) -> int:
    path, cycle = store.get_open(args.cycle)
    outcome = require_outcome(args.outcome)
    evaluation = evaluate_close(cycle, outcome)
    for check in cycle.get("checks") or []:
        if not check.get("required", True) or not check.get("evidence"):
            continue
        evidence = (store.project_root / str(check["evidence"])).resolve()
        try:
            evidence.relative_to(store.project_root)
        except ValueError:
            evaluation.add(
                "EVIDENCE_OUTSIDE_PROJECT",
                f"Evidence for {check.get('id', '<unnamed>')} resolves outside the project",
            )
            continue
        if not evidence.is_file():
            evaluation.add(
                "EVIDENCE_NOT_FOUND",
                f"Evidence for {check.get('id', '<unnamed>')} does not exist: {check['evidence']}",
            )
    print_evaluation(evaluation)
    if not evaluation.allowed:
        print("WOULD_BLOCK: close policy is not satisfied")
        return 1
    if not args.apply:
        mode = cycle.get("governance_mode", "shadow").upper()
        print(f"WOULD_ALLOW: {mode} {outcome.value} (dry run; pass --apply to archive)")
        return 0
    cycle["status"] = "closed"
    cycle["outcome"] = outcome.value
    cycle["closed_at"] = utc_now()
    destination = store.archive(path, cycle)
    mode = cycle.get("governance_mode", "shadow")
    print(f"Archived {mode} cycle {cycle['id']}: {destination.relative_to(store.project_root)}")
    return 0


def command_metrics(store: Store) -> int:
    metrics = generate_metrics(store)
    destination = write_metrics(store, metrics)
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    print(f"Written: {destination.relative_to(store.project_root)}")
    return 0


def parse_key_values(values: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for value in values:
        if "=" not in value:
            raise SwhouseError(f"Expected KEY=VALUE, got: {value}")
        key, raw = value.split("=", 1)
        normalized = raw.strip().lower()
        if normalized in ("true", "yes"):
            parsed: Any = True
        elif normalized in ("false", "no"):
            parsed = False
        elif normalized in ("none", "null"):
            parsed = None
        else:
            parsed = raw
        result[key.strip()] = parsed
    return result


def checks_for_profile(validation: dict[str, Any], profile: Profile) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    for definition in validation.get("checks") or []:
        profiles = [str(value).upper() for value in definition.get("profiles") or []]
        if profiles and profile.value not in profiles:
            continue
        checks.append(
            {
                "id": str(definition["id"]),
                "command": [str(value) for value in definition.get("command") or []],
                "required": bool(definition.get("required", True)),
                "timeout_seconds": int(definition.get("timeout_seconds", 300)),
                "status": "pending",
                "exit_code": None,
                "executed_at": None,
                "evidence": None,
            }
        )
    return checks


def print_evaluation(evaluation: Any) -> None:
    if not evaluation.findings:
        print("POLICY_OK")
        return
    for finding in evaluation.findings:
        print(f"{finding.severity.upper():7} {finding.code}: {finding.message}")


def safe_name(value: str) -> str:
    normalized = "".join(character if character.isalnum() or character in "-_" else "-" for character in value)
    return normalized.strip("-") or "check"


def normalize_path(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).replace("\\", "/")


_ASSIGNMENT_SECRET = re.compile(
    r"(?i)(\b(?:api[_-]?key|access[_-]?token|token|password|passwd|secret)\s*[=:]\s*)([^\s&;]+)"
)
_BEARER_SECRET = re.compile(r"(?i)(\bBearer\s+)([A-Za-z0-9._~+/=-]+)")


def redact_sensitive(value: str) -> str:
    redacted = _ASSIGNMENT_SECRET.sub(r"\1[REDACTED]", value)
    return _BEARER_SECRET.sub(r"\1[REDACTED]", redacted)


def _text_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def git_run(store: Store, *arguments: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", *arguments],
            cwd=store.project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            check=False,
        )
    except OSError as exc:
        raise SwhouseError(f"Unable to execute Git: {exc}") from exc


def git_output(store: Store, *arguments: str) -> str:
    result = git_run(store, *arguments)
    if result.returncode != 0:
        raise SwhouseError(f"Git command failed: git {' '.join(arguments)}\n{result.stderr.strip()}")
    return result.stdout.strip()


def product_dirty_paths(store: Store) -> list[str]:
    result = git_run(store, "status", "--porcelain", "--untracked-files=all")
    if result.returncode != 0:
        raise SwhouseError(f"Unable to inspect Git working tree: {result.stderr.strip()}")
    dirty: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:].replace("\\", "/") if len(line) > 3 else line
        if path.startswith(".swhouse/"):
            continue
        dirty.append(path)
    return dirty


if __name__ == "__main__":
    raise SystemExit(main())
