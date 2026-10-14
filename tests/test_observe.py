from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

from swhouse.cli import main
from swhouse.observe import aggregate
from swhouse.store import Store

SPRINT = ["--risk", "reversible=true", "--risk", "native_verification_available=true", "--risk", "blast_radius=low"]


class ObserveTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        house = self.root / ".swhouse"
        (house / "cycles").mkdir(parents=True)
        (house / "metrics").mkdir()
        (house / "instance.yaml").write_text('framework_version: "0.6.0"\n', encoding="utf-8")
        (house / "metrics" / "summary.yaml").write_text("version: 1\n", encoding="utf-8")
        (house / "config.yaml").write_text(
            yaml.safe_dump({"schema_version": 2, "mode": "shadow", "validation_file": "validation.yaml"}),
            encoding="utf-8",
        )
        (house / "validation.yaml").write_text(
            yaml.safe_dump(
                {
                    "schema_version": 2,
                    "checks": [
                        {
                            "id": "tests",
                            "command": [sys.executable, "-c", "pass"],
                            "profiles": ["SPRINT"],
                            "required": True,
                            "timeout_seconds": 30,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.house = house

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def args(self, *values: str) -> list[str]:
        return ["--root", str(self.root), *values]

    def run_cycle(self, judge: str | None, green: bool = True) -> None:
        self.assertEqual(main(self.args("start", "task", "--profile", "SPRINT", "--criterion", "x", *SPRINT)), 0)
        if judge:
            self.assertEqual(main(self.args("observe", "judge", judge, "--by", "op")), 0)
        self.assertEqual(main(self.args("set-change", "commit:abc")), 0)
        self.assertEqual(main(self.args("criterion", "AC-01", "met" if green else "pending")), 0)
        self.assertEqual(main(self.args("run-check", "tests")), 0)
        self.assertEqual(main(self.args("close", "--apply")), 0 if green else 1)

    def test_judgement_must_precede_first_close(self) -> None:
        self.assertEqual(main(self.args("start", "t", "--profile", "SPRINT", "--criterion", "x", *SPRINT)), 0)
        main(self.args("close"))
        self.assertEqual(main(self.args("observe", "judge", "accept", "--by", "op")), 2)

    def test_judgement_cannot_be_changed(self) -> None:
        main(self.args("start", "t", "--profile", "SPRINT", "--criterion", "x", *SPRINT))
        self.assertEqual(main(self.args("observe", "judge", "accept", "--by", "op")), 0)
        self.assertEqual(main(self.args("observe", "judge", "reject", "--by", "op")), 2)

    def test_false_block_is_counted(self) -> None:
        main(self.args("start", "t", "--profile", "SPRINT", "--criterion", "x", *SPRINT))
        main(self.args("observe", "judge", "accept", "--by", "op"))
        main(self.args("set-change", "commit:abc"))
        self.assertEqual(main(self.args("close")), 1)
        cycles = [Store(self.root).get_open()[1]]
        report = aggregate(cycles)
        self.assertEqual(report["judgement_vs_v2"]["false_blocks"], 1)

    def test_agreement_on_clean_cycle(self) -> None:
        self.run_cycle("accept")
        archived = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in (self.house / "cycles" / "archive-v2").glob("*.yaml")]
        report = aggregate(archived)
        self.assertEqual(report["judgement_vs_v2"]["agree"], 1)
        self.assertEqual(report["judgement_vs_v2"]["false_blocks"], 0)

    def test_manual_edit_of_cycle_file_is_detected(self) -> None:
        main(self.args("start", "t", "--profile", "SPRINT", "--criterion", "x", *SPRINT))
        path = next((self.house / "cycles" / "open").glob("*.yaml"))
        path.write_text(path.read_text(encoding="utf-8").replace("problem: t", "problem: tampered"), encoding="utf-8")
        main(self.args("set-change", "commit:abc"))
        _, cycle = Store(self.root).get_open()
        self.assertEqual(len(cycle["observations"]["manual_edits"]), 1)

    def test_cli_edits_do_not_look_like_manual_edits(self) -> None:
        self.run_cycle("accept")
        archived = yaml.safe_load(next((self.house / "cycles" / "archive-v2").glob("*.yaml")).read_text(encoding="utf-8"))
        self.assertFalse((archived.get("observations") or {}).get("manual_edits"))

    def test_late_defect_is_recorded_on_archived_cycle(self) -> None:
        self.run_cycle("accept")
        self.assertEqual(main(self.args("observe", "defect", "regression found", "--cycle", "001")), 0)
        archived = yaml.safe_load(next((self.house / "cycles" / "archive-v2").glob("*.yaml")).read_text(encoding="utf-8"))
        self.assertEqual(len(archived["observations"]["escaped_defects"]), 1)

    def test_session_minutes_accumulate_and_report_writes_file(self) -> None:
        main(self.args("start", "t", "--profile", "SPRINT", "--criterion", "x", *SPRINT))
        main(self.args("observe", "session", "--minutes", "20"))
        main(self.args("observe", "session", "--minutes", "15"))
        _, cycle = Store(self.root).get_open()
        self.assertEqual(cycle["observations"]["effort"], {"sessions": 2, "minutes": 35})
        self.assertEqual(main(self.args("observe", "report", "--baseline-minutes", "30")), 0)
        data = json.loads((self.house / "metrics" / "observations.json").read_text(encoding="utf-8"))
        self.assertFalse(data["sufficient_sample"])
        self.assertTrue(data["failure_criteria"]["median_minutes_vs_baseline"]["tripped"])

    def test_thresholds_trip(self) -> None:
        cycles = [
            {"status": "open", "observations": {"judgement": {"verdict": "accept"}, "close_attempts": [{"allowed": False}]}}
            for _ in range(2)
        ]
        report = aggregate(cycles)
        self.assertTrue(report["failure_criteria"]["false_blocks"]["tripped"])
        self.assertTrue(report["any_criterion_tripped"])

    def test_provisional_is_not_counted_as_a_block(self) -> None:
        cycle = {"status": "closed", "outcome": "PROVISIONAL", "observations": {"judgement": {"verdict": "conditional"}}}
        report = aggregate([cycle])
        self.assertEqual(report["judgement_vs_v2"]["agree"], 1)

    def test_check_failure_then_pass_is_counted(self) -> None:
        cycle = {"status": "closed", "outcome": "ACCEPTED", "observations": {"check_failures": 1}}
        self.assertEqual(aggregate([cycle])["cycles_where_a_check_failed_before_passing"], 1)


if __name__ == "__main__":
    unittest.main()
