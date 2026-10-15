"""Platform-neutral input safety gate before any adapter dispatch."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import ActionRequest, Capability, DecisionStatus
from .loopback import InMemoryBridgeCore


@dataclass(frozen=True)
class TargetBounds:
    target_id: str
    left: int
    top: int
    right: int
    bottom: int

    def __post_init__(self) -> None:
        if self.right <= self.left or self.bottom <= self.top:
            raise ValueError("target bounds must have positive width and height")

    def contains(self, x: int, y: int) -> bool:
        return self.left <= x < self.right and self.top <= y < self.bottom


@dataclass(frozen=True)
class InputDecision:
    request_id: str
    target_id: str
    allowed: bool
    reason: str
    x: int
    y: int


class InputArbitrator:
    """Checks ownership and coordinates but never sends real input."""

    def __init__(self, core: InMemoryBridgeCore) -> None:
        self.core = core
        self.bounds: dict[str, TargetBounds] = {}
        self.human_override_active = False
        self.human_override_target: str | None = None

    def set_bounds(self, bounds: TargetBounds) -> None:
        self.bounds[bounds.target_id] = bounds

    def set_human_override(self, target_id: str | None) -> None:
        """Pause AI input globally or only for one target."""
        self.human_override_active = True
        self.human_override_target = target_id

    def clear_human_override(self) -> None:
        self.human_override_active = False
        self.human_override_target = None

    def trigger_emergency_stop(self, *, reason: str = "local_kill_switch") -> None:
        self.core.set_emergency_stop(True, reason=reason)

    def authorize(self, request: ActionRequest, *, x: int, y: int, now_ms: int) -> InputDecision:
        if request.capability != Capability.INPUT:
            return self._deny(request, x, y, "input_capability_required")
        if self.core.emergency_stop:
            return self._deny(request, x, y, "emergency_stop_active")
        if self.human_override_active and (
            self.human_override_target is None or self.human_override_target == request.target_id
        ):
            return self._deny(request, x, y, "human_override_active")

        target_bounds = self.bounds.get(request.target_id)
        if target_bounds is None:
            return self._deny(request, x, y, "target_bounds_unknown")
        if not target_bounds.contains(x, y):
            return self._deny(request, x, y, "outside_target_cage")

        policy_result = self.core.handle(request, now_ms=now_ms)
        if policy_result.status != DecisionStatus.ACCEPTED:
            return self._deny(request, x, y, policy_result.reason)

        return InputDecision(
            request_id=request.request_id,
            target_id=request.target_id,
            allowed=True,
            reason="ready_for_adapter_dispatch",
            x=x,
            y=y,
        )

    @staticmethod
    def _deny(request: ActionRequest, x: int, y: int, reason: str) -> InputDecision:
        return InputDecision(
            request_id=request.request_id,
            target_id=request.target_id,
            allowed=False,
            reason=reason,
            x=x,
            y=y,
        )
