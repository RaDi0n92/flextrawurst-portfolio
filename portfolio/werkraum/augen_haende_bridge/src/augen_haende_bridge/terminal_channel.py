"""Fail-closed lifecycle contract for one owned terminal channel.

The channel is deliberately independent from terminal presentation.  A PTY
or ConPTY adapter supplies transport evidence; a native terminal adapter
supplies presentation/state readback.  Neither one may silently stand in for
the other.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import time
from typing import Mapping


TERMINAL_CHANNEL_PROOF_SEQUENCE = (
    "session_owned",
    "pty_connected",
    "vt_output_received",
    "rendered",
    "input_accepted",
    "input_delivered",
    "input_echoed",
    "state_observed",
    "audited",
)


class TerminalChannelStatus(str, Enum):
    READY = "ready"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"


@dataclass(frozen=True)
class TerminalChannelEvent:
    sequence: int
    state: str
    captured_at_ms: int
    evidence: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "state": self.state,
            "captured_at_ms": self.captured_at_ms,
            "evidence": dict(self.evidence),
        }


class TerminalChannel:
    """Require the real terminal proof chain in its exact order.

    This class records evidence only; it never starts a shell, sends input,
    or renders a terminal.  The adapters that own those capabilities remain
    explicit callers, which keeps transport and presentation separable.
    """

    def __init__(self, channel_id: str, target_id: str) -> None:
        if not channel_id or not target_id:
            raise ValueError("channel_id_and_target_id_required")
        self.channel_id = channel_id
        self.target_id = target_id
        self.status = TerminalChannelStatus.READY
        self.events: list[TerminalChannelEvent] = []
        self.last_error: str | None = None

    @property
    def current_state(self) -> str | None:
        return self.events[-1].state if self.events else None

    @property
    def next_state(self) -> str | None:
        if len(self.events) >= len(TERMINAL_CHANNEL_PROOF_SEQUENCE):
            return None
        return TERMINAL_CHANNEL_PROOF_SEQUENCE[len(self.events)]

    @property
    def proofs(self) -> tuple[str, ...]:
        return tuple(event.state for event in self.events)

    def _required_evidence(self, state: str, evidence: Mapping[str, object]) -> str | None:
        requirements = {
            "session_owned": ("owner",),
            "pty_connected": ("transport",),
            "vt_output_received": ("byte_count",),
            "rendered": ("render_source",),
            "input_accepted": ("request_id",),
            "input_delivered": ("delivery_method",),
            "input_echoed": ("marker",),
            "state_observed": ("capture_method",),
            "audited": ("audit_sequence",),
        }
        for key in requirements[state]:
            value = evidence.get(key)
            if value is None or value == "":
                return key
        if state == "vt_output_received":
            try:
                if int(evidence["byte_count"]) <= 0:
                    return "byte_count_positive"
            except (KeyError, TypeError, ValueError):
                return "byte_count_positive"
        return None

    def advance(
        self,
        state: str,
        evidence: Mapping[str, object] | None = None,
        *,
        captured_at_ms: int | None = None,
    ) -> TerminalChannelEvent:
        """Record exactly the next state or block the channel permanently."""

        details = dict(evidence or {})
        expected = self.next_state
        if self.status in {TerminalChannelStatus.BLOCKED, TerminalChannelStatus.COMPLETED}:
            raise RuntimeError(f"terminal_channel_not_open:{self.status.value}")
        if expected != state:
            self.block(f"expected:{expected}:received:{state}")
            raise RuntimeError(self.last_error or "terminal_channel_wrong_state")
        missing = self._required_evidence(state, details)
        if missing is not None:
            self.block(f"missing_evidence:{state}:{missing}")
            raise RuntimeError(self.last_error or "terminal_channel_missing_evidence")

        event = TerminalChannelEvent(
            sequence=len(self.events) + 1,
            state=state,
            captured_at_ms=captured_at_ms if captured_at_ms is not None else int(time.time() * 1000),
            evidence=details,
        )
        self.events.append(event)
        self.status = (
            TerminalChannelStatus.COMPLETED
            if self.next_state is None
            else TerminalChannelStatus.RUNNING
        )
        return event

    def block(self, reason: str) -> None:
        self.status = TerminalChannelStatus.BLOCKED
        self.last_error = reason

    def to_dict(self) -> dict[str, object]:
        return {
            "channel_id": self.channel_id,
            "target_id": self.target_id,
            "status": self.status.value,
            "current_state": self.current_state,
            "next_state": self.next_state,
            "proofs": list(self.proofs),
            "last_error": self.last_error,
            "events": [event.to_dict() for event in self.events],
        }
