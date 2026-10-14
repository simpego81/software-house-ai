from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .errors import InvalidStateError


class Profile(str, Enum):
    DIRECT = "DIRECT"
    SPRINT = "SPRINT"
    STANDARD = "STANDARD"
    GUARDED = "GUARDED"
    REVERT = "REVERT"
    EXPERIMENT = "EXPERIMENT"


class Outcome(str, Enum):
    ACCEPTED = "ACCEPTED"
    PROVISIONAL = "PROVISIONAL"
    DEFERRED = "DEFERRED"
    REJECTED = "REJECTED"
    REVERTED = "REVERTED"


GUARDED_RISK_FLAGS = (
    "irreversible",
    "data_migration",
    "public_contract",
    "attack_surface",
    "cross_domain",
)

KNOWN_RISK_KEYS = frozenset(
    GUARDED_RISK_FLAGS
    + (
        "blast_radius",
        "reversible",
        "native_verification_available",
        "known_good_baseline",
        "bounded_blast_radius",
        "stop_condition",
    )
)

BLAST_RADIUS_VALUES = ("low", "medium", "high", "recovery")

PENDING_RESOLVED = ("verified", "converted")
PENDING_STATUSES = ("pending", "verified", "failed", "waived", "converted")


@dataclass(frozen=True)
class Finding:
    code: str
    message: str
    severity: str = "error"


@dataclass
class Evaluation:
    findings: list[Finding] = field(default_factory=list)

    @property
    def blockers(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "error"]

    @property
    def allowed(self) -> bool:
        return not self.blockers

    def add(self, code: str, message: str, severity: str = "error") -> None:
        self.findings.append(Finding(code, message, severity))


def require_profile(value: Any) -> Profile:
    try:
        return Profile(str(value).upper())
    except ValueError as exc:
        allowed = ", ".join(item.value for item in Profile)
        raise InvalidStateError(f"Unknown profile {value!r}; expected one of: {allowed}") from exc


def require_outcome(value: Any) -> Outcome:
    try:
        return Outcome(str(value).upper())
    except ValueError as exc:
        allowed = ", ".join(item.value for item in Outcome)
        raise InvalidStateError(f"Unknown outcome {value!r}; expected one of: {allowed}") from exc
