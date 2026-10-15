"""External proof contract for the Playwright guardian.

The guardian is deliberately not part of the platform authority.  It is a
strict witness: Playwright collects the visible DOM and the runtime readback,
then this small contract decides whether one transition is proven, blocked, or
still unknown.  A browser assertion never upgrades a native platform claim.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class GuardianStatus(str, Enum):
    PASS = "pass"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class GuardianStep:
    """What must be observed before one transition may be called proven."""

    step_id: str
    action: str
    expected_dom: Mapping[str, str] = field(default_factory=dict)
    expected_core: Mapping[str, Any] = field(default_factory=dict)
    required_audit_suffix: tuple[str, ...] = ()
    target_id: str | None = None
    requires_fresh_target: bool = True
    requires_native: bool = False


@dataclass(frozen=True)
class GuardianObservation:
    """The two readbacks collected by the Playwright witness."""

    step_id: str
    action: str
    dom: Mapping[str, str]
    core: Mapping[str, Any]
    audit_types: tuple[str, ...]
    target_id: str | None = None
    scan_id: str | None = None
    frame_hash: str | None = None
    native_proven: bool = False


@dataclass(frozen=True)
class GuardianVerdict:
    status: GuardianStatus
    step_id: str
    reasons: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.status is GuardianStatus.PASS


def _audit_suffix_matches(actual: tuple[str, ...], required: tuple[str, ...]) -> bool:
    if not required:
        return True
    return len(actual) >= len(required) and actual[-len(required) :] == required


class PlaywrightGuardian:
    """Fail-closed verifier for one visible Playwright transition at a time."""

    def __init__(self) -> None:
        self.verdicts: list[GuardianVerdict] = []

    def verify(self, step: GuardianStep, observation: GuardianObservation) -> GuardianVerdict:
        blocked: list[str] = []
        unknown: list[str] = []

        if observation.step_id != step.step_id:
            blocked.append(f"step mismatch: expected {step.step_id}, got {observation.step_id}")
        if observation.action != step.action:
            blocked.append(f"action mismatch: expected {step.action}, got {observation.action}")

        for key, expected in step.expected_dom.items():
            actual = observation.dom.get(key)
            if actual != expected:
                blocked.append(f"dom mismatch for {key}: expected {expected!r}, got {actual!r}")

        for key, expected in step.expected_core.items():
            actual = observation.core.get(key)
            if actual != expected:
                blocked.append(f"core mismatch for {key}: expected {expected!r}, got {actual!r}")

        if step.target_id is not None and observation.target_id != step.target_id:
            blocked.append(
                f"target mismatch: expected {step.target_id!r}, got {observation.target_id!r}"
            )
        if not _audit_suffix_matches(observation.audit_types, step.required_audit_suffix):
            blocked.append(
                "audit suffix mismatch: "
                f"expected {step.required_audit_suffix!r}, got {observation.audit_types!r}"
            )

        if step.requires_fresh_target:
            if not observation.scan_id:
                unknown.append("missing fresh scan_id")
            if not observation.frame_hash:
                unknown.append("missing frame_hash")
        if step.requires_native and not observation.native_proven:
            unknown.append("native platform witness is still missing")

        if blocked:
            verdict = GuardianVerdict(GuardianStatus.BLOCKED, step.step_id, tuple(blocked + unknown))
        elif unknown:
            verdict = GuardianVerdict(GuardianStatus.UNKNOWN, step.step_id, tuple(unknown))
        else:
            verdict = GuardianVerdict(GuardianStatus.PASS, step.step_id)
        self.verdicts.append(verdict)
        return verdict

