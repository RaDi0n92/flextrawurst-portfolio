"""Small, serializable domain contracts for the Greenfield bridge core."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class _ValueEnum(str, Enum):
    def __str__(self) -> str:
        return self.value


class Capability(_ValueEnum):
    OBSERVE = "observe"
    OVERLAY = "overlay"
    SAY = "say"
    INPUT = "input"
    TERMINAL = "terminal"


class ActionKind(_ValueEnum):
    INSPECT = "inspect"
    OVERLAY = "overlay"
    SAY = "say"
    CLICK = "click"
    TYPE = "type"
    HOTKEY = "hotkey"
    TERMINAL = "terminal"


class TargetKind(_ValueEnum):
    WINDOWS_WINDOW = "windows.window"
    WINDOWS_DESKTOP = "windows.desktop"
    LINUX_KDE_DESKTOP = "linux.kde.desktop"
    LINUX_WINDOW = "linux.window"
    LINUX_TERMINAL = "linux.terminal"


@dataclass(frozen=True)
class TargetScanItem:
    """One target discovered by a scanner snapshot.

    A native window handle is not sufficient identity. ``generation`` makes a
    reused handle a new target instead of silently retaining a stale binding.
    """

    target_id: str
    generation: str
    kind: TargetKind
    label: str
    host: str
    rect: tuple[int, int, int, int] | None = None
    visible: bool = True
    z_order: int | None = None
    virtual_desktop: str | None = None
    process_id: int | None = None
    process_path: str | None = None
    source: str = "unknown"
    availability: str = "unavailable"
    capabilities: frozenset[str] = frozenset()

    def to_dict(self) -> dict[str, object]:
        return {
            "target_id": self.target_id,
            "generation": self.generation,
            "kind": self.kind.value,
            "label": self.label,
            "host": self.host,
            "rect": list(self.rect) if self.rect is not None else None,
            "visible": self.visible,
            "z_order": self.z_order,
            "virtual_desktop": self.virtual_desktop,
            "process_id": self.process_id,
            "process_path": self.process_path,
            "source": self.source,
            "availability": self.availability,
            "capabilities": sorted(self.capabilities),
        }


@dataclass(frozen=True)
class TargetScanSnapshot:
    """A visual and structured witness produced by the window scanner."""

    scan_id: str
    captured_at_ms: int
    source: str
    frame_ref: str
    frame_hash: str
    default_target_id: str
    items: tuple[TargetScanItem, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "scan_id": self.scan_id,
            "captured_at_ms": self.captured_at_ms,
            "source": self.source,
            "frame_ref": self.frame_ref,
            "frame_hash": self.frame_hash,
            "default_target_id": self.default_target_id,
            "items": [item.to_dict() for item in self.items],
        }


class DecisionStatus(_ValueEnum):
    ACCEPTED = "accepted"
    DENIED = "denied"


@dataclass(frozen=True)
class Agent:
    id: str
    name: str


@dataclass(frozen=True)
class Target:
    id: str
    kind: TargetKind
    label: str
    host: str


@dataclass(frozen=True)
class Lease:
    id: str
    agent_id: str
    target_id: str
    capability: Capability
    expires_at_ms: int


@dataclass(frozen=True)
class Binding:
    """Binds an agent to a target while the visible bridge stays on Windows."""

    agent_id: str
    target_id: str
    surface_id: str = "surface:windows:bridge"
    capabilities: frozenset[Capability] = frozenset()


@dataclass(frozen=True)
class ActionRequest:
    request_id: str
    session_id: str
    agent_id: str
    surface_id: str
    target_id: str
    capability: Capability
    action: ActionKind
    lease_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "session_id": self.session_id,
            "agent_id": self.agent_id,
            "surface_id": self.surface_id,
            "target_id": self.target_id,
            "capability": self.capability.value,
            "action": self.action.value,
            "lease_id": self.lease_id,
            "payload": dict(self.payload),
        }


@dataclass(frozen=True)
class ActionResult:
    request_id: str
    status: DecisionStatus
    reason: str
    audit_event: str
    target_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "request_id": self.request_id,
            "status": self.status.value,
            "reason": self.reason,
            "audit_event": self.audit_event,
            "target_id": self.target_id,
        }
