"""Read-only target selection and frame-coupled binding evidence.

This module records what a later native adapter selected; it does not move a
window, send input, create a lease, or dispatch an action.  A binding is valid
only for the exact target generation and paired frame that created it.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .contracts import Capability, TargetScanItem, TargetScanSnapshot


class BindingError(ValueError):
    """A requested read-only binding cannot be created safely."""


class BindingStatus(str, Enum):
    MATCHED = "matched"
    STALE = "stale"


@dataclass(frozen=True)
class ReadOnlyTargetBinding:
    binding_id: str
    agent_id: str
    surface_id: str
    target_id: str
    target_generation: str
    scan_id: str
    frame_ref: str
    frame_hash: str
    capabilities: frozenset[Capability]


@dataclass(frozen=True)
class BindingReadback:
    binding_id: str
    status: BindingStatus
    reason: str
    target_id: str
    scan_id: str
    frame_ref: str
    frame_hash: str

    @property
    def valid(self) -> bool:
        return self.status is BindingStatus.MATCHED


def _selected_item(snapshot: TargetScanSnapshot, target_id: str) -> TargetScanItem:
    for item in snapshot.items:
        if item.target_id == target_id:
            return item
    raise BindingError("target_not_in_scan")


def create_read_only_binding(
    snapshot: TargetScanSnapshot,
    *,
    binding_id: str,
    agent_id: str,
    target_id: str,
    surface_id: str = "surface:windows:bridge",
) -> ReadOnlyTargetBinding:
    """Select one current scan item and grant observation only."""

    if not binding_id or not agent_id or not surface_id:
        raise BindingError("binding_identity_required")
    if not snapshot.frame_ref or not snapshot.frame_hash or not snapshot.scan_id:
        raise BindingError("scan_witness_required")
    item = _selected_item(snapshot, target_id)
    if not item.visible:
        raise BindingError("target_not_visible")
    if item.availability != "available":
        raise BindingError("target_unavailable")
    if not (item.capabilities & frozenset({"inventory", "capture"})):
        raise BindingError("target_observation_capability_missing")
    # Deliberately do not inherit arbitrary scanner strings as action rights.
    # The first binding can only be used for read-only observation.
    return ReadOnlyTargetBinding(
        binding_id=binding_id,
        agent_id=agent_id,
        surface_id=surface_id,
        target_id=item.target_id,
        target_generation=item.generation,
        scan_id=snapshot.scan_id,
        frame_ref=snapshot.frame_ref,
        frame_hash=snapshot.frame_hash,
        capabilities=frozenset({Capability.OBSERVE}),
    )


def read_back_binding(
    binding: ReadOnlyTargetBinding,
    snapshot: TargetScanSnapshot,
) -> BindingReadback:
    """Revalidate a binding against a fresh coupled scan, fail-closed."""

    item = next((candidate for candidate in snapshot.items if candidate.target_id == binding.target_id), None)
    if item is None:
        reason = "target_missing"
    elif item.generation != binding.target_generation:
        reason = "target_generation_changed"
    elif snapshot.frame_ref != binding.frame_ref or snapshot.frame_hash != binding.frame_hash:
        reason = "paired_frame_changed"
    elif not item.visible:
        reason = "target_not_visible"
    elif item.availability != "available":
        reason = "target_unavailable"
    elif Capability.OBSERVE not in binding.capabilities:
        reason = "observation_capability_missing"
    else:
        return BindingReadback(
            binding_id=binding.binding_id,
            status=BindingStatus.MATCHED,
            reason="binding_read_back",
            target_id=binding.target_id,
            scan_id=snapshot.scan_id,
            frame_ref=snapshot.frame_ref,
            frame_hash=snapshot.frame_hash,
        )
    return BindingReadback(
        binding_id=binding.binding_id,
        status=BindingStatus.STALE,
        reason=reason,
        target_id=binding.target_id,
        scan_id=snapshot.scan_id,
        frame_ref=snapshot.frame_ref,
        frame_hash=snapshot.frame_hash,
    )
