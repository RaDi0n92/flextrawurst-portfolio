#!/usr/bin/env python3
"""Shared canonical-world mutation helper for the Gesamtkonstrukt planner.

This module deliberately does NOT expose HTTP and does NOT replace planner_api.py.
It only provides one small compatibility boundary:

- use the same current.json wrapper shape
- use the same .state.lock file
- preserve the complete existing state
- bump serverRevision exactly once per canonical mutation
- write current.json atomically
- keep a bounded in-state worldEvents ring as canonical provenance
- optionally append the same world event to rebuildable NDJSON history

High-frequency activity (reads, searches, cursor/focus, live process chatter) does
not belong here. Only durable world consequences should call this helper.
"""
from __future__ import annotations

import copy
import fcntl
import hashlib
import json
import os
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


WORLD_EVENT_SCHEMA = "gkos.world-event.v0"
WORLD_EVENTS_LIMIT = 240


class WorldStateError(RuntimeError):
    """Base error for canonical world-state mutations."""


class RevisionConflict(WorldStateError):
    def __init__(self, expected: int, actual: int):
        super().__init__(f"server_revision_conflict: expected={expected} actual={actual}")
        self.expected = expected
        self.actual = actual


class InvalidState(WorldStateError):
    pass


@dataclass(frozen=True)
class CommitResult:
    wrapper: dict[str, Any]
    event: dict[str, Any]
    event_log_written: bool


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_state_bytes(state: dict[str, Any]) -> bytes:
    return json.dumps(
        state,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def state_hash(state: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_state_bytes(state)).hexdigest()


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    payload = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    with temporary.open("w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def validate_legacy_compatible_state(state: Any) -> None:
    """Keep the same minimum compatibility contract as planner_api._valid_state()."""
    if not (
        isinstance(state, dict)
        and isinstance(state.get("title"), str)
        and isinstance(state.get("objects"), list)
        and isinstance(state.get("edges"), list)
        and isinstance(state.get("feedback"), list)
    ):
        raise InvalidState("invalid_state")


class WorldStateStore:
    """Atomic, lock-compatible writer for durable world-state facets."""

    def __init__(self, current: Path, lock: Path, events_dir: Path | None = None):
        self.current = Path(current)
        self.lock = Path(lock)
        self.events_dir = Path(events_dir) if events_dir else None

    @contextmanager
    def locked(self):
        self.lock.parent.mkdir(parents=True, exist_ok=True)
        with self.lock.open("a+", encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)

    def read_wrapper(self) -> dict[str, Any]:
        with self.current.open("r", encoding="utf-8") as handle:
            wrapper = json.load(handle)
        if not isinstance(wrapper, dict) or not isinstance(wrapper.get("state"), dict):
            raise InvalidState("invalid_current_wrapper")
        validate_legacy_compatible_state(wrapper["state"])
        return wrapper

    def commit(
        self,
        mutator: Callable[[dict[str, Any]], Any],
        *,
        event_type: str,
        event_data: dict[str, Any] | None = None,
        actor: dict[str, Any] | str | None = None,
        expected_server_revision: int | None = None,
    ) -> CommitResult:
        """Mutate the canonical state once and bump serverRevision once.

        The mutator receives a deep copy of the full existing state. Unknown
        top-level fields are therefore preserved unless the mutator explicitly
        changes them.
        """
        if not event_type or not isinstance(event_type, str):
            raise ValueError("event_type_required")

        with self.locked():
            previous = self.read_wrapper()
            actual_revision = int(previous.get("serverRevision") or 0)
            if (
                expected_server_revision is not None
                and int(expected_server_revision) != actual_revision
            ):
                raise RevisionConflict(int(expected_server_revision), actual_revision)

            state = copy.deepcopy(previous["state"])
            mutator_result = mutator(state)
            validate_legacy_compatible_state(state)

            next_revision = actual_revision + 1
            at = now_iso()
            event: dict[str, Any] = {
                "schema": WORLD_EVENT_SCHEMA,
                "id": f"world-{uuid.uuid4()}",
                "at": at,
                "type": event_type,
                "serverRevision": next_revision,
                "previousServerRevision": actual_revision,
            }
            if actor is not None:
                event["actor"] = actor
            if event_data:
                event["data"] = copy.deepcopy(event_data)
            if mutator_result is not None:
                event["mutationResult"] = copy.deepcopy(mutator_result)

            world_events = state.setdefault("worldEvents", [])
            if not isinstance(world_events, list):
                raise InvalidState("worldEvents_must_be_list")
            world_events.append(event)
            state["worldEvents"] = world_events[-WORLD_EVENTS_LIMIT:]

            wrapper = {
                "schemaVersion": int(previous.get("schemaVersion") or 1),
                "serverRevision": next_revision,
                "updatedAt": at,
                "sha256": state_hash(state),
                "state": state,
            }
            atomic_json(self.current, wrapper)

            event_log_written = self._append_event_log(event)
            return CommitResult(
                wrapper=wrapper,
                event=event,
                event_log_written=event_log_written,
            )

    def _append_event_log(self, event: dict[str, Any]) -> bool:
        if self.events_dir is None:
            return False
        try:
            self.events_dir.mkdir(parents=True, exist_ok=True)
            target = self.events_dir / f"{str(event['at'])[:10]}.ndjson"
            with target.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, ensure_ascii=False) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            return True
        except OSError:
            # current.json already contains the canonical event. The NDJSON file
            # is rebuildable provenance, so failure here must not pretend the
            # canonical mutation failed or roll back an already durable state.
            return False


ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
DEFAULT_STORE = WorldStateStore(
    current=ROOT / "data" / "current.json",
    lock=ROOT / "data" / ".state.lock",
    events_dir=ROOT / "data" / "world_events",
)
