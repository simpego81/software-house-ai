from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from swhouse.cli import main, redact_sensitive
from swhouse.doctor import diagnose
from swhouse.store import Store


class RuntimeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.house = self.root / ".swhouse"
        (self.house / "cycles" / "archive").mkdir(parents=True)
        (self.house / "metrics").mkdir(parents=True)
        for category in ("decisions", "patterns", "errors", "knowledge"):
            (self.house / "memory" / category).mkdir(parents=True)
        self.write_yaml(
            self.house / "instance.yaml",
            {"framework_version": "0.5.0", "instance": {"operator": "test"}},
        )
        self.write_yaml(
            self.house / "metrics" / "summary.yaml",
            {
                "version": 1,
                "total_cycles": 2,
                "memory_entries": {
                    "decisions": 0,
                    "patterns": 0,
                    "errors": 0,
                    "knowledge": 0,
                },
            },
        )
        (self.house / "cycles" / "archive" / "cycle-001.md").write_text(
            "---\ncycle: 1\nstatus: open\n---\nlegacy\n",
            encoding="utf-8",
        )
        (self.house / "cycles" / "archive" / "cycle-002.md").write_text(
            "---\ncycle: 2\nstatus: closed\n---\nawaiting Owner approval\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_yaml(self, path: Path, value: dict) -> None:
        path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")

    def args(self, *values: str) -> list[str]:
        return ["--root", str(self.root), *values]

    def test_doctor_reports_known_legacy_inconsistencies(self) -> None:
        diagnostics = diagnose(Store(self.root))
        codes = {item.code for item in diagnostics}
        self.assertIn("ARCHIVED_NOT_CLOSED", codes)
        self.assertIn("STALE_OWNER_APPROVAL", codes)

    def test_doctor_rejects_v2_archive_with_missing_evidence(self) -> None:
        archive = self.house / "cycles" / "archive-v2"
        archive.mkdir(parents=True)
        self.write_yaml(
            archive / "003.yaml",
            {
                "schema_version": 2,
                "status": "closed",
                "governance_mode": "shadow",
                "checks": [
                    {
                        "id": "tests",
                        "required": True,
                        "evidence": ".swhouse/evidence/003/missing.log",
                    }
                ],
            },
        )
        codes = {item.code for item in diagnose(Store(self.root))}
        self.assertIn("V2_EVIDENCE_MISSING", codes)

    def test_doctor_baseline_allows_known_error(self) -> None:
        baseline = self.root / "baseline.yaml"
        self.write_yaml(
            baseline,
            {
                "version": 1,
                "allowed": [
                    {
                        "code": "ARCHIVED_NOT_CLOSED",
                        "path": ".swhouse/cycles/archive/cycle-001.md",
                    }
                ],
            },
        )
        self.assertEqual(main(self.args("doctor", "--baseline", str(baseline))), 0)

    def test_evidence_redacts_common_secret_formats(self) -> None:
        value = "API_KEY=abc123 Authorization: Bearer token.value password: hunter2"
        redacted = redact_sensitive(value)
        self.assertNotIn("abc123", redacted)
        self.assertNotIn("token.value", redacted)
        self.assertNotIn("hunter2", redacted)

    def test_configured_check_cannot_be_substituted(self) -> None:
        self.write_yaml(
            self.house / "config.yaml",
            {"schema_version": 2, "validation_file": "validation.yaml"},
        )
        self.write_yaml(
            self.house / "validation.yaml",
            {
                "schema_version": 2,
                "checks": [
                    {
                        "id": "tests",
                        "command": [sys.executable, "-c", "print('expected')"],
                        "profiles": ["SPRINT"],
                        "required": True,
                    }
                ],
            },
        )
        self.assertEqual(
            main(
                self.args(
                    "start",
                    "Configured verification",
                    "--profile",
                    "SPRINT",
                    "--criterion",
                    "Configured test runs",
                    "--risk",
                    "reversible=true",
                    "--risk",
                    "native_verification_available=true",
                    "--risk",
                    "blast_radius=low",
                )
            ),
            0,
        )
        self.assertEqual(
            main(self.args("run-check", "tests", "--", sys.executable, "-c", "print('fake')")),
            2,
        )
        self.assertEqual(main(self.args("run-check", "tests")), 0)

    def test_sprint_lifecycle_and_generated_metrics(self) -> None:
        self.assertEqual(
            main(
                self.args(
                    "start",
                    "Implement evidence runtime",
                    "--profile",
                    "SPRINT",
                    "--criterion",
                    "Runtime records successful checks",
                    "--risk",
                    "reversible=true",
                    "--risk",
                    "native_verification_available=true",
                    "--risk",
                    "blast_radius=low",
                )
            ),
            0,
        )
        self.assertEqual(main(self.args("set-change", "working-tree:test")), 0)
        self.assertEqual(main(self.args("criterion", "AC-01", "met")), 0)
        self.assertEqual(
            main(
                self.args(
                    "run-check",
                    "smoke",
                    "--",
                    sys.executable,
                    "-c",
                    "print('ok')",
                )
            ),
            0,
        )
        self.assertEqual(main(self.args("close")), 0)
        self.assertTrue((self.house / "cycles" / "open" / "003.yaml").exists())
        self.assertEqual(main(self.args("close", "--apply")), 0)
        self.assertFalse((self.house / "cycles" / "open" / "003.yaml").exists())
        self.assertTrue((self.house / "cycles" / "archive-v2" / "003.yaml").exists())
        self.assertEqual(main(self.args("metrics")), 0)
        metrics = json.loads((self.house / "metrics" / "generated.json").read_text(encoding="utf-8"))
        self.assertEqual(metrics["cycles_closed"], 1)
        self.assertEqual(metrics["verification_completeness"], 1.0)

    def test_close_rejects_missing_evidence_file(self) -> None:
        self.assertEqual(
            main(
                self.args(
                    "start",
                    "Reject fake evidence",
                    "--profile",
                    "SPRINT",
                    "--criterion",
                    "Evidence exists",
                    "--risk",
                    "reversible=true",
                    "--risk",
                    "native_verification_available=true",
                    "--risk",
                    "blast_radius=low",
                )
            ),
            0,
        )
        path, cycle = Store(self.root).get_open()
        cycle["acceptance_criteria"][0]["status"] = "met"
        cycle["change"]["ref"] = "working-tree:test"
        cycle["checks"] = [
            {
                "id": "fake",
                "required": True,
                "status": "passed",
                "exit_code": 0,
                "evidence": ".swhouse/evidence/003/does-not-exist.log",
            }
        ]
        Store(self.root).save_open(path, cycle)
        self.assertEqual(main(self.args("close")), 1)

    def test_missing_check_executable_is_recorded_as_failure(self) -> None:
        self.assertEqual(
            main(
                self.args(
                    "start",
                    "Record execution failure",
                    "--profile",
                    "SPRINT",
                    "--criterion",
                    "Failure is visible",
                    "--risk",
                    "reversible=true",
                    "--risk",
                    "native_verification_available=true",
                    "--risk",
                    "blast_radius=low",
                )
            ),
            0,
        )
        self.assertEqual(
            main(self.args("run-check", "missing", "--", "definitely-not-a-real-executable")),
            127,
        )
        _, cycle = Store(self.root).get_open()
        self.assertEqual(cycle["checks"][0]["status"], "failed")
        self.assertEqual(cycle["checks"][0]["exit_code"], 127)

    def test_prepare_and_apply_revert(self) -> None:
        self.git("init")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Runtime Test")
        product = self.root / "product.txt"
        product.write_text("good\n", encoding="utf-8")
        self.git("add", "product.txt")
        self.git("commit", "-m", "good baseline")
        product.write_text("regression\n", encoding="utf-8")
        self.git("add", "product.txt")
        self.git("commit", "-m", "introduce regression")
        bad_commit = self.git("rev-parse", "HEAD").stdout.strip()

        self.assertEqual(
            main(self.args("prepare-revert", bad_commit, "--reason", "test regression")),
            0,
        )
        self.assertEqual(main(self.args("apply-revert")), 0)
        self.assertEqual(product.read_text(encoding="utf-8"), "regression\n")
        dirty = self.root / "uncommitted.txt"
        dirty.write_text("do not overwrite\n", encoding="utf-8")
        self.assertEqual(main(self.args("apply-revert", "--apply")), 2)
        dirty.unlink()
        self.assertEqual(main(self.args("apply-revert", "--apply")), 0)
        self.assertEqual(product.read_text(encoding="utf-8"), "good\n")
        _, cycle = Store(self.root).get_open()
        self.assertEqual(cycle["revert"]["status"], "applied")
        self.assertTrue(cycle["change"]["ref"].startswith("revert-commit:"))

    def git(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *arguments],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
