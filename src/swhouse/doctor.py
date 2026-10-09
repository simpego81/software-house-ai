from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import InvalidStateError
from .io import load_yaml, parse_markdown_frontmatter
from .store import Store


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    message: str
    path: Path | None = None


def diagnose(store: Store) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    instance_path = store.root / "instance.yaml"
    summary_path = store.root / "metrics" / "summary.yaml"

    for required in (instance_path, summary_path, store.root / "cycles"):
        if not required.exists():
            diagnostics.append(Diagnostic("error", "MISSING_REQUIRED", "Required path missing", required))

    if instance_path.exists():
        try:
            instance = load_yaml(instance_path)
            if not instance.get("framework_version"):
                diagnostics.append(
                    Diagnostic("error", "FRAMEWORK_VERSION", "framework_version is missing", instance_path)
                )
        except InvalidStateError as exc:
            diagnostics.append(Diagnostic("error", "INVALID_YAML", str(exc), instance_path))

    config_path = store.root / "config.yaml"
    if config_path.exists():
        try:
            config = load_yaml(config_path)
            if config.get("schema_version") != 2:
                diagnostics.append(
                    Diagnostic("error", "CONFIG_SCHEMA", "config.yaml must use schema_version 2", config_path)
                )
            if config.get("mode", "shadow") not in ("shadow", "enforced"):
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "CONFIG_MODE",
                        "config mode must be shadow or enforced",
                        config_path,
                    )
                )
            validation_path = store.root / str(config.get("validation_file", "validation.yaml"))
            if not validation_path.exists():
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "VALIDATION_MISSING",
                        "Configured validation matrix does not exist",
                        validation_path,
                    )
                )
            else:
                validation = load_yaml(validation_path)
                identifiers: set[str] = set()
                for check in validation.get("checks") or []:
                    identifier = str(check.get("id", ""))
                    if not identifier or identifier in identifiers:
                        diagnostics.append(
                            Diagnostic(
                                "error",
                                "VALIDATION_CHECK_ID",
                                "Validation check ids must be present and unique",
                                validation_path,
                            )
                        )
                    identifiers.add(identifier)
                    command = check.get("command")
                    if not isinstance(command, list) or not command:
                        diagnostics.append(
                            Diagnostic(
                                "error",
                                "VALIDATION_COMMAND",
                                f"Validation check {identifier or '<unnamed>'} needs a command array",
                                validation_path,
                            )
                        )
        except InvalidStateError as exc:
            diagnostics.append(Diagnostic("error", "INVALID_V2_CONFIG", str(exc), config_path))

    legacy_archives = sorted((store.root / "cycles" / "archive").glob("cycle-*.md"))
    summary = {}
    if summary_path.exists():
        try:
            summary = load_yaml(summary_path)
        except InvalidStateError as exc:
            diagnostics.append(Diagnostic("error", "INVALID_YAML", str(exc), summary_path))

    declared_total = summary.get("total_cycles")
    if isinstance(declared_total, int) and declared_total != len(legacy_archives):
        diagnostics.append(
            Diagnostic(
                "warning",
                "LEGACY_CYCLE_COUNT",
                f"summary total_cycles={declared_total}, legacy archive files={len(legacy_archives)}",
                summary_path,
            )
        )

    for path in legacy_archives:
        try:
            frontmatter = parse_markdown_frontmatter(path)
        except InvalidStateError as exc:
            diagnostics.append(Diagnostic("error", "FRONTMATTER", str(exc), path))
            continue
        if str(frontmatter.get("status", "")).lower() not in ("closed", "decided"):
            diagnostics.append(
                Diagnostic(
                    "error",
                    "ARCHIVED_NOT_CLOSED",
                    f"Archived cycle has status={frontmatter.get('status')!r}",
                    path,
                )
            )
        text = path.read_text(encoding="utf-8").lower()
        if "awaiting owner approval" in text and str(frontmatter.get("status", "")).lower() == "closed":
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "STALE_OWNER_APPROVAL",
                    "Closed archive still contains an awaiting Owner approval marker",
                    path,
                )
            )

    memory_summary = summary.get("memory_entries") or {}
    for category in ("decisions", "patterns", "errors", "knowledge"):
        directory = store.root / "memory" / category
        actual = len(list(directory.glob("*.md"))) if directory.exists() else 0
        declared = memory_summary.get(category)
        if isinstance(declared, int) and declared != actual:
            diagnostics.append(
                Diagnostic(
                    "warning",
                    "MEMORY_COUNT",
                    f"{category}: summary={declared}, files={actual}",
                    summary_path,
                )
            )

    for path in store.open_paths():
        try:
            cycle = load_yaml(path)
            if cycle.get("schema_version") != 2:
                diagnostics.append(
                    Diagnostic("error", "CYCLE_SCHEMA", "Open cycle is not schema_version 2", path)
                )
            if cycle.get("status") != "open":
                diagnostics.append(
                    Diagnostic("error", "OPEN_STATUS", "Cycle in open/ is not status=open", path)
                )
        except InvalidStateError as exc:
            diagnostics.append(Diagnostic("error", "INVALID_CYCLE", str(exc), path))

    if store.archive_v2_dir.exists():
        for path in sorted(store.archive_v2_dir.glob("*.yaml")):
            try:
                cycle = load_yaml(path)
            except InvalidStateError as exc:
                diagnostics.append(Diagnostic("error", "INVALID_V2_ARCHIVE", str(exc), path))
                continue
            if cycle.get("schema_version") != 2:
                diagnostics.append(
                    Diagnostic("error", "V2_ARCHIVE_SCHEMA", "Archived cycle is not schema_version 2", path)
                )
            if cycle.get("status") != "closed":
                diagnostics.append(
                    Diagnostic("error", "V2_ARCHIVE_STATUS", "Cycle in archive-v2/ is not closed", path)
                )
            if cycle.get("governance_mode") not in ("shadow", "enforced"):
                diagnostics.append(
                    Diagnostic(
                        "error",
                        "V2_GOVERNANCE_MODE",
                        "Archived cycle has no valid governance_mode",
                        path,
                    )
                )
            for check in cycle.get("checks") or []:
                if not check.get("required", True) or not check.get("evidence"):
                    continue
                evidence = (store.project_root / str(check["evidence"])).resolve()
                try:
                    evidence.relative_to(store.project_root)
                except ValueError:
                    diagnostics.append(
                        Diagnostic(
                            "error",
                            "V2_EVIDENCE_OUTSIDE_PROJECT",
                            f"Evidence for {check.get('id', '<unnamed>')} leaves the project",
                            path,
                        )
                    )
                    continue
                if not evidence.is_file():
                    diagnostics.append(
                        Diagnostic(
                            "error",
                            "V2_EVIDENCE_MISSING",
                            f"Evidence for {check.get('id', '<unnamed>')} is missing",
                            path,
                        )
                    )

    if not diagnostics:
        diagnostics.append(Diagnostic("ok", "HEALTHY", "No invariant violations found"))
    return diagnostics
