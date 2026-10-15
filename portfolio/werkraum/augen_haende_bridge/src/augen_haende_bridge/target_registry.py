"""Target inventory for the visible Windows bridge surface."""

from __future__ import annotations

from dataclasses import dataclass
import os
from threading import RLock
import time
from typing import Protocol

from .contracts import Target, TargetKind
from .terminal_adapter import KonsoleAdapter, TerminalSessionRef, TerminalSnapshot


class TerminalAdapter(Protocol):
    """Small adapter boundary so the Windows client never owns KDE discovery."""

    def discover(self) -> list[TerminalSessionRef]: ...

    def inspect(self, *, target_id: str, ref: TerminalSessionRef) -> TerminalSnapshot: ...


class PlatformUnavailableAdapter:
    """Explicit no-op adapter for clients without a local KDE session.

    The Windows overlay still needs a target registry, but it must not execute
    Linux `qdbus6` discovery locally. KDE/VPS targets will arrive through the
    bridge once that transport exists.
    """

    def discover(self) -> list[TerminalSessionRef]:
        return []

    def inspect(self, *, target_id: str, ref: TerminalSessionRef) -> TerminalSnapshot:
        return TerminalSnapshot(
            target_id=target_id,
            source="platform",
            availability="unavailable",
            status="unavailable",
            capture_method="platform-adapter:not-available",
            captured_at_ms=0,
            session_pid=ref.session_pid,
            foreground_pid=ref.foreground_pid,
            title=ref.title,
            output="",
            error="platform_adapter_not_available",
        )


def _default_terminal_adapter(platform_name: str | None = None) -> TerminalAdapter:
    """Select the local adapter without probing another operating system."""

    if (platform_name or os.name) == "nt":
        return PlatformUnavailableAdapter()
    return KonsoleAdapter()


def stable_terminal_identity(ref: TerminalSessionRef) -> str:
    """Return a D-Bus/session identity that rejects PID reuse."""

    process = "unknown" if ref.session_pid is None else str(ref.session_pid)
    return f"{ref.service}|{ref.session_path}|pid={process}"


@dataclass(frozen=True)
class TargetRecord:
    target: Target
    source: str
    availability: str
    capture_method: str
    terminal_ref: TerminalSessionRef | None = None
    stable_identity: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.target.id,
            "kind": self.target.kind.value,
            "host": self.target.host,
            "label": self.target.label,
            "source": self.source,
            "availability": self.availability,
            "capture_method": self.capture_method,
        }

    def to_bridge_dict(self) -> dict[str, object]:
        """Authenticated transport form; internal identity stays off the UI wire."""

        return {**self.to_dict(), "identity": self.stable_identity or ""}


class TargetRegistry:
    """Keeps platform targets and their provenance separate from core policy."""

    def __init__(self, adapter: TerminalAdapter | None = None) -> None:
        self.adapter = adapter if adapter is not None else _default_terminal_adapter()
        self._lock = RLock()
        self.records: dict[str, TargetRecord] = {}
        self.selected_target_id = "win-desktop"
        self._static_terminal_record: TargetRecord | None = None
        self._discovered_terminal_ids: set[str] = set()
        self._terminal_slot_by_identity: dict[str, str] = {}
        self._probe_identities: set[str] = set()
        self._remote_terminal_ids: set[str] = set()
        self._refresh_sequence = 0
        self._refresh_in_flight = False
        self._register_static_targets()
        self.refresh_terminals()

    def _register_static_targets(self) -> None:
        static = (
            TargetRecord(
                Target("win-desktop", TargetKind.WINDOWS_DESKTOP, "Windows kompletter Desktop", "thinkpad"),
                "planned",
                "unavailable",
                "windows-adapter:not-built",
            ),
            TargetRecord(
                Target("kde-1", TargetKind.LINUX_KDE_DESKTOP, "Linux KDE Desktop 1", "vps"),
                "planned",
                "unavailable",
                "kde-adapter:not-built",
            ),
            TargetRecord(
                Target("kde-2", TargetKind.LINUX_KDE_DESKTOP, "Linux KDE Desktop 2", "vps"),
                "planned",
                "unavailable",
                "kde-adapter:not-built",
            ),
            TargetRecord(
                Target("terminal-1", TargetKind.LINUX_TERMINAL, "Original-Terminal 1", "vps"),
                "synthetic",
                "unavailable",
                "konsole-dbus:not-discovered",
            ),
        )
        for record in static:
            self.records[record.target.id] = record
            if record.target.id == "terminal-1":
                self._static_terminal_record = record

    def refresh_terminals(self) -> None:
        # Discovery is replace-style: a closed KDE session must disappear on
        # the next scan, while an explicitly registered probe remains intact.
        with self._lock:
            if self._refresh_in_flight:
                return
            self._refresh_in_flight = True
            self._refresh_sequence += 1
            refresh_sequence = self._refresh_sequence

        try:
            # qdbus can perform several blocking calls. Do not hold the
            # registry lock while the platform adapter is doing I/O; readers
            # keep seeing the last complete snapshot during discovery.
            discover_result = getattr(self.adapter, "discover_result", None)
            if discover_result is not None:
                discovery = discover_result()
                if discovery.status != "ok":
                    return
                refs = list(discovery.refs)
            else:
                refs = self.adapter.discover()

            with self._lock:
                if refresh_sequence != self._refresh_sequence:
                    return
                self._apply_refresh(refs)
        finally:
            with self._lock:
                self._refresh_in_flight = False

    def _apply_refresh(self, refs: list[TerminalSessionRef]) -> None:
        previous_selected_id = self.selected_target_id
        previous_selected = self.records.get(previous_selected_id)

        # Build a replacement dictionary off to the side. Readers see the old
        # complete state until this method swaps in the new complete state;
        # they never observe the pop/repopulate gap.
        new_records = dict(self.records)
        for target_id in self._discovered_terminal_ids:
            new_records.pop(target_id, None)
        if self._static_terminal_record is not None:
            new_records.setdefault("terminal-1", self._static_terminal_record)

        candidates: list[tuple[TerminalSessionRef, str]] = []
        seen_identities: set[str] = set()
        for ref in refs:
            identity = stable_terminal_identity(ref)
            if identity in self._probe_identities or identity in seen_identities:
                continue
            seen_identities.add(identity)
            candidates.append((ref, identity))

        # Reserve all remembered slots first. A newly discovered session must
        # not steal a surviving session's old slot just because it appeared
        # earlier in the adapter's result order.
        used_slots: set[str] = set()
        assigned_slots: dict[str, str] = {}
        for _ref, identity in candidates:
            remembered = self._terminal_slot_by_identity.get(identity)
            if (
                remembered
                and remembered not in used_slots
                and self._slot_is_available(remembered, new_records)
            ):
                assigned_slots[identity] = remembered
                used_slots.add(remembered)

        new_terminal_ids: set[str] = set()
        new_slot_by_identity = dict(self._terminal_slot_by_identity)
        for ref, identity in candidates:
            target_id = assigned_slots.get(identity)
            if target_id is None:
                target_id = self._next_available_slot(used_slots, new_records)
                assigned_slots[identity] = target_id
            used_slots.add(target_id)
            slot_number = target_id.removeprefix("terminal-")
            label = f"Original-Terminal {slot_number}"
            if ref.title:
                label = f"{label} — {ref.title}"
            new_records[target_id] = TargetRecord(
                Target(
                    target_id,
                    TargetKind.LINUX_TERMINAL,
                    label,
                    "vps",
                ),
                "real",
                "available",
                "konsole-dbus:getAllDisplayedText",
                ref,
                identity,
            )
            new_terminal_ids.add(target_id)
            new_slot_by_identity[identity] = target_id

        self.records = new_records
        self._discovered_terminal_ids = new_terminal_ids
        self._terminal_slot_by_identity = new_slot_by_identity
        if previous_selected and previous_selected.stable_identity:
            current_selected = self.records.get(previous_selected_id)
            if not current_selected or current_selected.stable_identity != previous_selected.stable_identity:
                self.selected_target_id = "win-desktop"
        elif self.selected_target_id not in self.records:
            self.selected_target_id = "win-desktop"

    @staticmethod
    def _next_available_slot(used_slots: set[str], records: dict[str, TargetRecord]) -> str:
        index = 1
        while True:
            candidate = f"terminal-{index}"
            if candidate not in used_slots and (
                candidate not in records or records[candidate].source == "synthetic"
            ):
                return candidate
            index += 1

    @staticmethod
    def _slot_is_available(target_id: str, records: dict[str, TargetRecord]) -> bool:
        record = records.get(target_id)
        return record is None or record.source == "synthetic"

    def register_probe(self, ref: TerminalSessionRef) -> TargetRecord:
        with self._lock:
            self._refresh_sequence += 1
            identity = stable_terminal_identity(ref)
            new_records = dict(self.records)
            new_discovered_ids = set(self._discovered_terminal_ids)
            new_probe_identities = set(self._probe_identities)
            previous = new_records.get("terminal-probe")
            if previous and previous.stable_identity:
                new_probe_identities.discard(previous.stable_identity)
            selected_probe_source = False
            for target_id in tuple(new_discovered_ids):
                record = new_records.get(target_id)
                if record and record.stable_identity == identity:
                    selected_probe_source = self.selected_target_id == target_id
                    new_records.pop(target_id, None)
                    new_discovered_ids.discard(target_id)
            if self._static_terminal_record is not None:
                new_records.setdefault("terminal-1", self._static_terminal_record)
            new_probe_identities.add(identity)
            record = TargetRecord(
                Target(
                    "terminal-probe",
                    TargetKind.LINUX_TERMINAL,
                    "Isoliertes Bridge-Probe-Terminal",
                    "vps",
                ),
                "real",
                "available",
                "konsole-dbus:getAllDisplayedText+pty-controller:unix-socket",
                ref,
                identity,
            )
            new_records[record.target.id] = record
            self.records = new_records
            self._discovered_terminal_ids = new_discovered_ids
            self._probe_identities = new_probe_identities
            if selected_probe_source:
                self.selected_target_id = record.target.id
            return record

    def unregister_probe(self, *, stable_identity: str | None = None) -> bool:
        """Release an explicit probe so its session can return to discovery."""

        with self._lock:
            record = self.records.get("terminal-probe")
            if record is None:
                return False
            if stable_identity is not None and record.stable_identity != stable_identity:
                return False
            self._refresh_sequence += 1
            new_records = dict(self.records)
            new_records.pop("terminal-probe", None)
            new_probe_identities = set(self._probe_identities)
            if record.stable_identity:
                new_probe_identities.discard(record.stable_identity)
            self.records = new_records
            self._probe_identities = new_probe_identities
            if self.selected_target_id == "terminal-probe":
                self.selected_target_id = "win-desktop"
            return True

    def targets(self) -> tuple[Target, ...]:
        with self._lock:
            return tuple(record.target for record in self.records.values())

    def select(self, target_id: str) -> TargetRecord:
        with self._lock:
            if target_id not in self.records:
                raise KeyError(f"unknown target: {target_id}")
            self.selected_target_id = target_id
            return self.records[target_id]

    def selected(self) -> TargetRecord:
        with self._lock:
            return self.records[self.selected_target_id]

    def bridge_inventory(self) -> dict[str, object]:
        """Return the small read-only terminal inventory served to the overlay."""

        with self._lock:
            targets = [
                record.to_bridge_dict()
                for record in self.records.values()
                if record.source == "real"
                and record.target.kind == TargetKind.LINUX_TERMINAL
                and record.target.id != "terminal-probe"
                and record.stable_identity
            ]
        return {
            "status": "ok",
            "captured_at_ms": int(time.time() * 1000),
            "targets": targets,
        }

    def apply_remote_inventory(
        self,
        payload: dict[str, object],
        *,
        authority: str = "bridge-agent",
    ) -> int:
        """Atomically apply an authenticated remote terminal inventory.

        This is deliberately inventory-only. A remote record has no local
        adapter reference yet, so selecting it is safe but inspection/input
        remains unavailable until the later remote-inspect gate exists.
        """

        if payload.get("status") != "ok":
            return 0
        raw_targets = payload.get("targets")
        if not isinstance(raw_targets, list):
            raise ValueError("invalid_remote_inventory")
        with self._lock:
            previous_selected = self.records.get(self.selected_target_id)
            new_records = dict(self.records)
            for target_id in getattr(self, "_remote_terminal_ids", set()):
                new_records.pop(target_id, None)
            if self._static_terminal_record is not None:
                new_records.setdefault("terminal-1", self._static_terminal_record)

            remote_ids: set[str] = set()
            seen_remote_source_ids: set[str] = set()
            for raw in raw_targets:
                if not isinstance(raw, dict):
                    raise ValueError("invalid_remote_inventory_target")
                try:
                    target_id = raw["id"]
                    kind = TargetKind(raw["kind"])
                    host = raw["host"]
                    label = raw["label"]
                    source = raw["source"]
                    availability = raw["availability"]
                    capture_method = raw["capture_method"]
                    identity = raw["identity"]
                except (KeyError, TypeError, ValueError) as exc:
                    raise ValueError("invalid_remote_inventory_target") from exc
                if not all(isinstance(value, str) for value in
                           (target_id, host, label, source, availability, capture_method, identity)):
                    raise ValueError("invalid_remote_inventory_target")
                if kind is not TargetKind.LINUX_TERMINAL or not target_id.startswith("terminal-"):
                    raise ValueError("invalid_remote_inventory_target_kind")
                if not identity:
                    raise ValueError("invalid_remote_inventory_identity")
                if target_id in seen_remote_source_ids:
                    raise ValueError("duplicate_remote_inventory_target")
                seen_remote_source_ids.add(target_id)
                # Remote and local discovery use independent slot allocators.
                # Namespace the receiver-side id so a Linux test/client registry
                # cannot silently overwrite a local terminal-N record.
                remote_id = f"{authority}:{target_id}"
                new_records[remote_id] = TargetRecord(
                    Target(remote_id, kind, label, host),
                    f"{authority}:{source}",
                    # The remote value is a report about the VPS. This client
                    # has no remote inspect adapter yet, so it must not render
                    # the target as locally available or permit inspection.
                    "unavailable",
                    capture_method,
                    None,
                    identity,
                )
                remote_ids.add(remote_id)

            self.records = new_records
            self._remote_terminal_ids = remote_ids
            if previous_selected and previous_selected.stable_identity:
                current = self.records.get(previous_selected.target.id)
                if not current or current.stable_identity != previous_selected.stable_identity:
                    self.selected_target_id = "win-desktop"
            elif self.selected_target_id not in self.records:
                self.selected_target_id = "win-desktop"
            return len(remote_ids)

    def inspect(self, target_id: str | None = None) -> TerminalSnapshot:
        with self._lock:
            record = self.records[target_id or self.selected_target_id]
            terminal_ref = record.terminal_ref
            if terminal_ref is None:
                return TerminalSnapshot(
                    target_id=record.target.id,
                    source=record.source,
                    availability=record.availability,
                    status="unavailable",
                    capture_method=record.capture_method,
                    captured_at_ms=0,
                    session_pid=None,
                    foreground_pid=None,
                    title=record.target.label,
                    output="",
                    error="adapter_not_available",
                )
        return self.adapter.inspect(target_id=record.target.id, ref=terminal_ref)
