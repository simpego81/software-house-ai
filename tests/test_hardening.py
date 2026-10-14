from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

import yaml

from swhouse.cli import main
from swhouse.model import Outcome, Profile
from swhouse.policy import evaluate_close, evaluate_route, recommend_profile
from swhouse.store import Store

SPRINT_RISK = ["--risk", "reversible=true", "--risk", "native_verification_available=true", "--risk", "blast_radius=low"]


def sprint_cycle() -> dict:
    return {
        "profile": "SPRINT",
        "risk": {"reversible": True, "native_verification_available": True, "blast_radius": "low"},
        "acceptance_criteria": [{"id": "AC-01", "status": "met"}],
        "change": {"ref": "commit:abc"},
        "checks": [
            {"id": "tests", "required": True, "status": "passed", "exit_code": 0, "evidence": "e.log"}
        ],
        "pending_human": [],
        "findings": [],
    }


class RouteHardeningTests(unittest.TestCase):
    def test_typo_in_risk_key_is_rejected_instead_of_ignored(self) -> None:
        result = evaluate_route(Profile.SPRINT, {"attack_surfce": True, "reversible": True})
        self.assertIn("RISK_UNKNOWN_KEY", {item.code for item in result.findings})
        self.assertFalse(result.allowed)

    def test_blast_radius_is_validated(self) -> None:
        result = evaluate_route(Profile.STANDARD, {"blast_radius": "hgih"})
        self.assertIn("RISK_BLAST_RADIUS", {item.code for item in result.findings})

    def test_recommend_profile_is_deterministic(self) -> None:
        self.assertEqual(recommend_profile({"attack_surface": True})[0], Profile.GUARDED)
        self.assertEqual(
            recommend_profile(
                {"reversible": True, "native_verification_available": True, "blast_radius": "low"}
            )[0],
            Profile.SPRINT,
        )
        self.assertEqual(
            recommend_profile({"reversible": True, "native_verification_available": True, "blast_radius": "medium"})[0],
            Profile.STANDARD,
        )


class ContractTests(unittest.TestCase):
    def test_check_missing_from_cycle_blocks_even_if_other_check_passes(self) -> None:
        result = evaluate_close(sprint_cycle(), Outcome.ACCEPTED, configured_required=["lint"])
        self.assertIn("CONTRACT_CHECK_MISSING", {item.code for item in result.findings})
        self.assertFalse(result.allowed)

    def test_check_downgraded_to_optional_blocks(self) -> None:
        cycle = sprint_cycle()
        cycle["checks"][0]["required"] = False
        result = evaluate_close(cycle, Outcome.ACCEPTED, configured_required=["tests"])
        self.assertIn("CONTRACT_CHECK_DOWNGRADED", {item.code for item in result.findings})

    def test_enforced_mode_rejects_empty_contract(self) -> None:
        result = evaluate_close(sprint_cycle(), Outcome.ACCEPTED, configured_required=[], strict=True)
        self.assertIn("CONTRACT_EMPTY", {item.code for item in result.findings})
        self.assertFalse(result.allowed)

    def test_shadow_mode_tolerates_empty_contract(self) -> None:
        self.assertTrue(evaluate_close(sprint_cycle(), Outcome.ACCEPTED, configured_required=[]).allowed)


class GuardedTests(unittest.TestCase):
    def guarded(self) -> dict:
        cycle = sprint_cycle()
        cycle["profile"] = "GUARDED"
        cycle["risk"] = {"irreversible": True, "native_verification_available": True}
        cycle["rollback"] = {"strategy": "restore snapshot"}
        cycle["challenges"] = [
            {"status": "completed", "artifact": "r", "reviewer_context": "same-model"}
        ]
        cycle["approval"] = {"owner": "owner"}
        return cycle

    def test_self_asserted_owner_approval_blocks_in_enforced_mode(self) -> None:
        shadow = evaluate_close(self.guarded(), Outcome.ACCEPTED, strict=False)
        enforced = evaluate_close(self.guarded(), Outcome.ACCEPTED, strict=True)
        self.assertIn("OWNER_APPROVAL_UNVERIFIED", {item.code for item in shadow.findings})
        self.assertTrue(shadow.allowed or "GUARDED_REQUIRED" not in {i.code for i in shadow.blockers})
        self.assertIn("OWNER_APPROVAL_UNVERIFIED", {item.code for item in enforced.blockers})

    def test_same_model_challenge_blocks_guarded_only_when_required(self) -> None:
        lax = evaluate_close(self.guarded(), Outcome.ACCEPTED, require_independent_guarded=False)
        strict = evaluate_close(self.guarded(), Outcome.ACCEPTED, require_independent_guarded=True)
        self.assertNotIn("CHALLENGE_NOT_INDEPENDENT", {item.code for item in lax.blockers})
        self.assertIn("CHALLENGE_NOT_INDEPENDENT", {item.code for item in strict.blockers})


class PendingHumanTests(unittest.TestCase):
    def with_pending(self, **item) -> dict:
        cycle = sprint_cycle()
        cycle["pending_human"] = [{"id": "H-1", **item}]
        return cycle

    def test_pending_blocks(self) -> None:
        result = evaluate_close(self.with_pending(status="pending"))
        self.assertIn("PENDING_HUMAN", {item.code for item in result.blockers})

    def test_converted_and_verified_resolve(self) -> None:
        for status in ("verified", "converted"):
            self.assertTrue(evaluate_close(self.with_pending(status=status)).allowed, status)

    def test_waiver_requires_expiry_and_reference(self) -> None:
        result = evaluate_close(self.with_pending(status="waived"))
        self.assertIn("WAIVER_INVALID", {item.code for item in result.blockers})

    def test_waiver_expires(self) -> None:
        cycle = self.with_pending(status="waived", expires="2026-01-01", ref="owner:msg-1")
        result = evaluate_close(cycle, today=date(2026, 6, 1))
        self.assertIn("WAIVER_EXPIRED", {item.code for item in result.blockers})
        active = evaluate_close(cycle, today=date(2025, 12, 1))
        self.assertTrue(active.allowed)
        self.assertIn("WAIVER_ACTIVE", {item.code for item in active.findings})


class RuntimeHardeningTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        house = self.root / ".swhouse"
        house.mkdir()
        (house / "cycles").mkdir()
        (house / "instance.yaml").write_text('framework_version: "0.6.0"\n', encoding="utf-8")
        (house / "metrics").mkdir()
        (house / "metrics" / "summary.yaml").write_text("version: 1\n", encoding="utf-8")
        self.house = house
        self.write_config("enforced", [{"id": "tests", "command": [sys.executable, "-c", "pass"]}])

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_config(self, mode: str, checks: list[dict]) -> None:
        (self.house / "config.yaml").write_text(
            yaml.safe_dump({"schema_version": 2, "mode": mode, "validation_file": "validation.yaml"}),
            encoding="utf-8",
        )
        full = [
            {"required": True, "profiles": ["SPRINT"], "timeout_seconds": 30, **item} for item in checks
        ]
        (self.house / "validation.yaml").write_text(
            yaml.safe_dump({"schema_version": 2, "checks": full}), encoding="utf-8"
        )

    def args(self, *values: str) -> list[str]:
        return ["--root", str(self.root), *values]

    def start_sprint(self) -> None:
        self.assertEqual(
            main(self.args("start", "probe", "--profile", "SPRINT", "--criterion", "x", *SPRINT_RISK)), 0
        )
        self.assertEqual(main(self.args("set-change", "commit:fake")), 0)
        self.assertEqual(main(self.args("criterion", "AC-01", "met")), 0)

    def test_editing_cycle_yaml_cannot_drop_configured_check(self) -> None:
        self.start_sprint()
        store = Store(self.root)
        path, cycle = store.get_open()
        cycle["checks"] = [
            {
                "id": "other",
                "required": True,
                "status": "passed",
                "exit_code": 0,
                "evidence": ".swhouse/evidence/001/other.log",
            }
        ]
        evidence = self.house / "evidence" / "001"
        evidence.mkdir(parents=True)
        (evidence / "other.log").write_text("ok", encoding="utf-8")
        store.save_open(path, cycle)
        self.assertEqual(main(self.args("close")), 1)

    def test_evidence_tampering_after_run_blocks_close(self) -> None:
        self.start_sprint()
        self.assertEqual(main(self.args("run-check", "tests")), 0)
        log = next((self.house / "evidence").rglob("tests.log"))
        log.write_text("forged\n", encoding="utf-8")
        self.assertEqual(main(self.args("close")), 1)

    def test_clean_run_still_closes(self) -> None:
        self.start_sprint()
        self.assertEqual(main(self.args("run-check", "tests")), 0)
        self.assertEqual(main(self.args("close", "--apply")), 0)

    def test_optional_flag_after_check_id_is_not_executed_as_command(self) -> None:
        self.start_sprint()
        self.assertEqual(main(self.args("run-check", "adhoc", "--optional", "--", sys.executable, "-c", "pass")), 0)
        _, cycle = Store(self.root).get_open()
        adhoc = next(item for item in cycle["checks"] if item["id"] == "adhoc")
        self.assertFalse(adhoc["required"])

    def test_pending_human_cli_roundtrip(self) -> None:
        self.start_sprint()
        self.assertEqual(main(self.args("run-check", "tests")), 0)
        self.assertEqual(main(self.args("add-pending", "H-1", "reopen after standby", "--owner", "ops")), 0)
        self.assertEqual(main(self.args("close")), 1)
        self.assertEqual(main(self.args("resolve-pending", "H-1", "waived")), 2)
        self.assertEqual(
            main(self.args("resolve-pending", "H-1", "converted", "--ref", "test:standby")), 0
        )
        self.assertEqual(main(self.args("close")), 0)

    def test_open_legacy_cycle_blocks_v2_start(self) -> None:
        (self.house / "cycles" / "current.md").write_text("---\ncycle: 1\nstatus: open\n---\n", encoding="utf-8")
        self.assertEqual(
            main(self.args("start", "probe", "--profile", "SPRINT", "--criterion", "x", *SPRINT_RISK)), 2
        )
        (self.house / "cycles" / "current.md").unlink()
        self.assertEqual(
            main(self.args("start", "probe", "--profile", "SPRINT", "--criterion", "x", *SPRINT_RISK)), 0
        )

    def test_route_command_rejects_unknown_key(self) -> None:
        self.assertEqual(main(self.args("route", "--risk", "attack_surfce=true")), 1)
        self.assertEqual(main(self.args("route", "--risk", "attack_surface=true")), 0)


class AdoptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        house = self.root / ".swhouse"
        (house / "cycles" / "archive").mkdir(parents=True)
        (house / "metrics").mkdir()
        (house / "instance.yaml").write_text('framework_version: "0.5.0"\n', encoding="utf-8")
        (house / "metrics" / "summary.yaml").write_text("version: 1\ntotal_cycles: 2\n", encoding="utf-8")
        (house / "cycles" / "archive" / "cycle-001.md").write_text(
            "# Cycle 001\n\n**Status:** closed\n**Track:** S\n", encoding="utf-8"
        )
        (house / "cycles" / "archive" / "cycle-003.md").write_text(
            "# Cycle 003\n\n**Status:** IN PROGRESS\n", encoding="utf-8"
        )
        self.house = house

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def snapshot(self) -> dict[str, bytes]:
        return {
            str(path.relative_to(self.house)): path.read_bytes()
            for path in sorted(self.house.rglob("*"))
            if path.is_file()
        }

    def args(self, *values: str) -> list[str]:
        return ["--root", str(self.root), *values]

    def test_header_format_is_read_without_frontmatter_errors(self) -> None:
        from swhouse.doctor import diagnose

        codes = [item.code for item in diagnose(Store(self.root))]
        self.assertNotIn("FRONTMATTER", codes)
        self.assertIn("ARCHIVED_NOT_CLOSED", codes)
        self.assertIn("CYCLE_NUMBER_GAP", codes)

    def test_dry_run_writes_nothing(self) -> None:
        before = self.snapshot()
        self.assertEqual(main(self.args("adopt", "--check", "tests=python -m pytest")), 0)
        self.assertEqual(before, self.snapshot())

    def test_adopt_then_rollback_restores_exact_legacy_state(self) -> None:
        before = self.snapshot()
        self.assertEqual(main(self.args("adopt", "--apply", "--check", "tests=python -m pytest")), 0)
        self.assertTrue((self.house / "config.yaml").exists())
        self.assertEqual(main(self.args("doctor")), 0)
        self.assertEqual(main(self.args("adopt", "--rollback", "--apply")), 0)
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.house / "cycles" / "open").exists())

    def test_adopt_refuses_to_overwrite_existing_config(self) -> None:
        (self.house / "config.yaml").write_text("schema_version: 2\n", encoding="utf-8")
        self.assertEqual(main(self.args("adopt", "--apply")), 2)
        self.assertEqual((self.house / "config.yaml").read_text(encoding="utf-8"), "schema_version: 2\n")

    def test_rollback_keeps_files_edited_after_adoption(self) -> None:
        self.assertEqual(main(self.args("adopt", "--apply", "--check", "tests=python -m pytest")), 0)
        validation = self.house / "validation.yaml"
        validation.write_text(validation.read_text(encoding="utf-8") + "# edited\n", encoding="utf-8")
        self.assertEqual(main(self.args("adopt", "--rollback", "--apply")), 0)
        self.assertTrue(validation.exists())

    def test_new_drift_after_adoption_is_an_error_but_baseline_is_not(self) -> None:
        self.assertEqual(main(self.args("adopt", "--apply", "--check", "tests=python -m pytest")), 0)
        self.assertEqual(main(self.args("doctor")), 0)
        (self.house / "cycles" / "archive" / "cycle-004.md").write_text(
            "# Cycle 004\n\n**Status:** open\n", encoding="utf-8"
        )
        self.assertEqual(main(self.args("doctor")), 1)


if __name__ == "__main__":
    unittest.main()
