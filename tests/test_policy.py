import unittest

from swhouse.model import Outcome, Profile
from swhouse.policy import evaluate_close, evaluate_route


class RoutePolicyTests(unittest.TestCase):
    def test_sprint_requires_reversible_native_low_risk_change(self) -> None:
        result = evaluate_route(
            Profile.SPRINT,
            {
                "reversible": True,
                "native_verification_available": True,
                "blast_radius": "low",
            },
        )
        self.assertTrue(result.allowed)

    def test_security_surface_escalates_to_guarded(self) -> None:
        result = evaluate_route(
            Profile.STANDARD,
            {"attack_surface": True, "native_verification_available": True},
        )
        self.assertFalse(result.allowed)
        self.assertIn("GUARDED_REQUIRED", {finding.code for finding in result.findings})


class ClosePolicyTests(unittest.TestCase):
    def complete_cycle(self) -> dict:
        return {
            "profile": "SPRINT",
            "risk": {
                "reversible": True,
                "native_verification_available": True,
                "blast_radius": "low",
            },
            "acceptance_criteria": [{"id": "AC-01", "status": "met"}],
            "change": {"ref": "commit:abc123"},
            "checks": [
                {
                    "id": "tests",
                    "required": True,
                    "status": "passed",
                    "exit_code": 0,
                    "evidence": ".swhouse/evidence/003/tests.log",
                }
            ],
            "pending_human": [],
            "findings": [],
        }

    def test_complete_sprint_can_close(self) -> None:
        self.assertTrue(evaluate_close(self.complete_cycle(), Outcome.ACCEPTED).allowed)

    def test_missing_evidence_blocks_close(self) -> None:
        cycle = self.complete_cycle()
        cycle["checks"][0]["evidence"] = None
        result = evaluate_close(cycle, Outcome.ACCEPTED)
        self.assertFalse(result.allowed)
        self.assertIn("CHECK_EVIDENCE", {finding.code for finding in result.findings})

    def test_deferred_requires_reopen_trigger(self) -> None:
        cycle = self.complete_cycle()
        cycle["resolution"] = {"reason": "target unavailable"}
        result = evaluate_close(cycle, Outcome.DEFERRED)
        self.assertIn("REOPEN_TRIGGER", {finding.code for finding in result.findings})

    def test_standard_requires_challenge_and_rollback(self) -> None:
        cycle = self.complete_cycle()
        cycle["profile"] = "STANDARD"
        cycle["rollback"] = {"strategy": "git revert"}
        result = evaluate_close(cycle, Outcome.ACCEPTED)
        self.assertIn("CHALLENGE_REQUIRED", {finding.code for finding in result.findings})
        cycle["challenges"] = [
            {
                "status": "completed",
                "artifact": "review.md",
                "reviewer_context": "same-model",
            }
        ]
        result = evaluate_close(cycle, Outcome.ACCEPTED)
        self.assertTrue(result.allowed)
        self.assertIn("CHALLENGE_NOT_INDEPENDENT", {finding.code for finding in result.findings})


if __name__ == "__main__":
    unittest.main()
