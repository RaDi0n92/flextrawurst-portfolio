"""Deterministic in-memory bridge core used before any network transport."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .contracts import (
    ActionRequest,
    ActionResult,
    Agent,
    Binding,
    Lease,
    Target,
)
from .policy import evaluate_action


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    event_type: str
    request_id: str | None
    agent_id: str | None
    target_id: str | None
    details: dict[str, Any]


class InMemoryBridgeCore:
    """A side-effect-free request/policy/audit loopback.

    This class deliberately does not dispatch to a platform. An accepted
    result means only that the policy allows a later adapter to dispatch.
    """

    def __init__(self, *, visible_surface_id: str = "surface:windows:bridge") -> None:
        self.visible_surface_id = visible_surface_id
        self.agents: dict[str, Agent] = {}
        self.targets: dict[str, Target] = {}
        self.bindings: list[Binding] = []
        self.leases: dict[str, Lease] = {}
        self.emergency_stop = False
        self.audit: list[AuditEvent] = []

    def add_agent(self, agent: Agent) -> None:
        self.agents[agent.id] = agent

    def add_target(self, target: Target) -> None:
        self.targets[target.id] = target

    def add_binding(self, binding: Binding) -> None:
        self.bindings.append(binding)

    def add_lease(self, lease: Lease) -> None:
        self.leases[lease.id] = lease

    def set_emergency_stop(self, active: bool, *, reason: str = "operator") -> None:
        self.emergency_stop = active
        self._record(
            "emergency_stop.changed",
            request_id=None,
            agent_id=None,
            target_id=None,
            details={"active": active, "reason": reason},
        )

    def handle(self, request: ActionRequest, *, now_ms: int) -> ActionResult:
        self._record(
            "action.requested",
            request_id=request.request_id,
            agent_id=request.agent_id,
            target_id=request.target_id,
            details={"action": request.action.value, "capability": request.capability.value},
        )
        result = evaluate_action(
            request,
            agents=self.agents,
            targets=self.targets,
            bindings=self.bindings,
            leases=self.leases,
            now_ms=now_ms,
            emergency_stop=self.emergency_stop,
        )
        self._record(
            result.audit_event,
            request_id=request.request_id,
            agent_id=request.agent_id,
            target_id=request.target_id,
            details={"status": result.status.value, "reason": result.reason},
        )
        return result

    def record_adapter_event(
        self,
        event_type: str,
        *,
        request_id: str,
        agent_id: str,
        target_id: str,
        details: dict[str, Any],
    ) -> None:
        """Append an observed adapter transition to the same audit stream."""

        self._record(
            event_type,
            request_id=request_id,
            agent_id=agent_id,
            target_id=target_id,
            details=details,
        )

    def _record(
        self,
        event_type: str,
        *,
        request_id: str | None,
        agent_id: str | None,
        target_id: str | None,
        details: dict[str, Any],
    ) -> None:
        self.audit.append(
            AuditEvent(
                sequence=len(self.audit) + 1,
                event_type=event_type,
                request_id=request_id,
                agent_id=agent_id,
                target_id=target_id,
                details=details,
            )
        )
