"""Fail-closed policy evaluation without transport or platform side effects."""

from __future__ import annotations

from collections.abc import Iterable, Mapping

from .contracts import (
    ActionKind,
    ActionRequest,
    ActionResult,
    Agent,
    Binding,
    Capability,
    DecisionStatus,
    Lease,
    Target,
)


def _deny(request: ActionRequest, reason: str, event: str = "action.denied") -> ActionResult:
    return ActionResult(
        request_id=request.request_id,
        status=DecisionStatus.DENIED,
        reason=reason,
        audit_event=event,
        target_id=request.target_id,
    )


def evaluate_action(
    request: ActionRequest,
    *,
    agents: Mapping[str, Agent],
    targets: Mapping[str, Target],
    bindings: Iterable[Binding],
    leases: Mapping[str, Lease],
    now_ms: int,
    emergency_stop: bool = False,
) -> ActionResult:
    """Evaluate one request; never dispatches it.

    The evaluator intentionally knows only contracts and policy. Actual
    Windows/Linux dispatch belongs to later adapters and must consume an
    accepted result plus a separate observed-result event.
    """

    if emergency_stop:
        return _deny(request, "emergency_stop_active", "action.denied.emergency_stop")

    if not request.agent_id or request.agent_id not in agents:
        return _deny(request, "unknown_agent")
    if not request.target_id or request.target_id not in targets:
        return _deny(request, "unknown_target")
    if not request.surface_id:
        return _deny(request, "missing_visible_surface")

    binding = next(
        (
            candidate
            for candidate in bindings
            if candidate.agent_id == request.agent_id
            and candidate.target_id == request.target_id
            and candidate.surface_id == request.surface_id
        ),
        None,
    )
    if binding is None:
        return _deny(request, "agent_target_not_bound")
    if request.capability not in binding.capabilities:
        return _deny(request, "capability_not_granted")

    if request.action == ActionKind.INSPECT and request.capability != Capability.OBSERVE:
        return _deny(request, "inspect_requires_observe_capability")

    if request.capability in {Capability.INPUT, Capability.TERMINAL}:
        if not request.lease_id:
            return _deny(request, "lease_required")
        lease = leases.get(request.lease_id)
        if lease is None:
            return _deny(request, "unknown_lease")
        if (
            lease.agent_id != request.agent_id
            or lease.target_id != request.target_id
            or lease.capability != request.capability
        ):
            return _deny(request, "lease_scope_mismatch")
        if lease.expires_at_ms <= now_ms:
            return _deny(request, "lease_expired")

    return ActionResult(
        request_id=request.request_id,
        status=DecisionStatus.ACCEPTED,
        reason="policy_allows_dispatch",
        audit_event="action.accepted",
        target_id=request.target_id,
    )
