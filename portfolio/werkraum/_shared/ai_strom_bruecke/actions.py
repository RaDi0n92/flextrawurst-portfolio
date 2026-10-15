#!/usr/bin/env python3
"""Lease-protected native input with guaranteed button/key release."""

from __future__ import annotations

import fcntl
import os
import subprocess
import time
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Protocol

from .contracts import ActionExpectation, ActionPhase, ActionTransaction


class InputBackend(Protocol):
    def move(self, x: int, y: int) -> None: ...
    def button_down(self, button: int) -> None: ...
    def button_up(self, button: int) -> None: ...
    def key_down(self, key: str) -> None: ...
    def key_up(self, key: str) -> None: ...
    def click(self, button: int = 1) -> None: ...
    def key(self, key: str) -> None: ...
    def type_text(self, value: str, delay_ms: float = 0) -> None: ...
    def wheel(self, direction: int) -> None: ...


class XdotoolBackend:
    def __init__(self, container: str = "virtuellerdesktop2", display: str = ":1") -> None:
        self.container = container
        self.display = display

    def _run(self, *args: str) -> None:
        subprocess.run(
            ["docker", "exec", "-e", f"DISPLAY={self.display}", self.container, "xdotool", *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def move(self, x: int, y: int) -> None:
        self._run("mousemove", "--sync", str(int(x)), str(int(y)))

    def button_down(self, button: int) -> None:
        self._run("mousedown", str(button))

    def button_up(self, button: int) -> None:
        self._run("mouseup", str(button))

    def key_down(self, key: str) -> None:
        self._run("keydown", key)

    def key_up(self, key: str) -> None:
        self._run("keyup", key)

    def click(self, button: int = 1) -> None:
        self._run("click", str(button))

    def key(self, key: str) -> None:
        self._run("key", key)

    def type_text(self, value: str, delay_ms: float = 0) -> None:
        self._run("type", "--delay", str(max(0, int(delay_ms))), value)

    def wheel(self, direction: int) -> None:
        self._run("click", "4" if direction > 0 else "5")


class RecordingBackend:
    """Deterministic backend for tests and dry-run verification."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, Any]] = []

    def _record(self, name: str, *values: Any) -> None:
        self.calls.append((name, *values))

    def move(self, x: int, y: int) -> None: self._record("move", x, y)
    def button_down(self, button: int) -> None: self._record("mousedown", button)
    def button_up(self, button: int) -> None: self._record("mouseup", button)
    def key_down(self, key: str) -> None: self._record("keydown", key)
    def key_up(self, key: str) -> None: self._record("keyup", key)
    def click(self, button: int = 1) -> None: self._record("click", button)
    def key(self, key: str) -> None: self._record("key", key)
    def type_text(self, value: str, delay_ms: float = 0) -> None: self._record("type", value, delay_ms)
    def wheel(self, direction: int) -> None: self._record("wheel", direction)


class ControlLease:
    def __init__(self, path: Path, actor: str, target: str) -> None:
        self.path = path
        self.actor = actor
        self.target = target
        self.handle = None
        self.lease_id = f"lease-{uuid.uuid4().hex}"

    def __enter__(self) -> "ControlLease":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+", encoding="utf-8")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            self.handle.close()
            self.handle = None
            raise RuntimeError("Control-Lease ist bereits vergeben") from error
        self.handle.write(f"{self.lease_id} actor={self.actor} target={self.target}\n")
        self.handle.flush()
        return self

    def __exit__(self, *_: object) -> None:
        if self.handle is not None:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
            self.handle.close()
            self.handle = None


class ActionExecutor:
    def __init__(self, backend: InputBackend, *, lease_path: Path = Path("/tmp/ai-strom-bruecke-control.lock")) -> None:
        self.backend = backend
        self.lease_path = lease_path
        self.held_buttons: set[int] = set()
        self.held_keys: set[str] = set()

    def _release_all(self) -> list[dict[str, Any]]:
        released: list[dict[str, Any]] = []
        for button in sorted(self.held_buttons):
            try:
                self.backend.button_up(button)
                released.append({"kind": "mouseup", "value": button})
            finally:
                self.held_buttons.discard(button)
        for key in sorted(self.held_keys):
            try:
                self.backend.key_up(key)
                released.append({"kind": "keyup", "value": key})
            finally:
                self.held_keys.discard(key)
        return released

    @contextmanager
    def _safe_holds(self, transaction: ActionTransaction) -> Iterator[None]:
        try:
            yield
        finally:
            transaction.input_sequence.extend(self._release_all())
            transaction.released_at = time.time()

    def gesture(
        self,
        *,
        actor: str,
        target: str,
        points: list[tuple[int, int]],
        button: int = 1,
        hold_delay_s: float = 0.012,
        expectation: ActionExpectation | None = None,
        timeout_s: float | None = None,
    ) -> ActionTransaction:
        if len(points) < 2:
            raise ValueError("eine Geste braucht mindestens zwei Punkte")
        transaction = ActionTransaction(
            action_id=f"action-{uuid.uuid4().hex}",
            actor=actor,
            lease_id=None,
            target=target,
            action_type="gesture",
            phase=ActionPhase.PLANNED,
            planned_at=time.time(),
            pointer_start={"x": points[0][0], "y": points[0][1]},
            pointer_end={"x": points[-1][0], "y": points[-1][1]},
            button=button,
            expectation=expectation or ActionExpectation(),
        )
        deadline = time.monotonic() + (timeout_s or transaction.expectation.timeout_ms / 1000)
        with ControlLease(self.lease_path, actor, target) as lease:
            transaction.lease_id = lease.lease_id
            try:
                with self._safe_holds(transaction):
                    self.backend.move(*points[0])
                    self.backend.button_down(button)
                    self.held_buttons.add(button)
                    transaction.input_sequence.append({"kind": "mousedown", "value": button})
                    transaction.transition(ActionPhase.DISPATCHED)
                    transaction.dispatched_at = time.time()
                    for x, y in points[1:]:
                        if time.monotonic() > deadline:
                            transaction.transition(ActionPhase.TIMED_OUT, reason="dispatch-timeout")
                            break
                        self.backend.move(x, y)
                        transaction.input_sequence.append({"kind": "mousemove", "x": x, "y": y})
                        if hold_delay_s > 0:
                            time.sleep(hold_delay_s)
                    else:
                        # Dispatch completion is not visual acceptance.  A
                        # later fresh frame/claim must call acknowledge().
                        transaction.result["dispatch_complete"] = True
            except Exception as error:
                transaction.transition(ActionPhase.ABORTED, reason=str(error))
                transaction.rejection_reason = str(error)
        return transaction

    def move_path(
        self,
        *,
        actor: str,
        target: str,
        points: list[tuple[int, int]],
        hold_delay_s: float = 0.012,
        expectation: ActionExpectation | None = None,
        timeout_s: float | None = None,
    ) -> ActionTransaction:
        if not points:
            raise ValueError("move_path braucht mindestens einen Punkt")
        transaction = ActionTransaction(
            action_id=f"action-{uuid.uuid4().hex}", actor=actor, lease_id=None,
            target=target, action_type="pointer-move", phase=ActionPhase.PLANNED,
            planned_at=time.time(), pointer_start={"x": points[0][0], "y": points[0][1]},
            pointer_end={"x": points[-1][0], "y": points[-1][1]},
            expectation=expectation or ActionExpectation(),
        )
        deadline = time.monotonic() + (timeout_s or transaction.expectation.timeout_ms / 1000)
        with ControlLease(self.lease_path, actor, target) as lease:
            transaction.lease_id = lease.lease_id
            try:
                self.backend.move(*points[0])
                transaction.input_sequence.append({"kind": "mousemove", "x": points[0][0], "y": points[0][1]})
                transaction.transition(ActionPhase.DISPATCHED)
                transaction.dispatched_at = time.time()
                for x, y in points[1:]:
                    if time.monotonic() > deadline:
                        transaction.transition(ActionPhase.TIMED_OUT, reason="dispatch-timeout")
                        break
                    self.backend.move(x, y)
                    transaction.input_sequence.append({"kind": "mousemove", "x": x, "y": y})
                    if hold_delay_s > 0:
                        time.sleep(hold_delay_s)
                else:
                    transaction.result["dispatch_complete"] = True
            except Exception as error:
                transaction.transition(ActionPhase.ABORTED, reason=str(error))
                transaction.rejection_reason = str(error)
        return transaction

    def key_hold(
        self,
        *,
        actor: str,
        target: str,
        key: str,
        duration_s: float,
        expectation: ActionExpectation | None = None,
    ) -> ActionTransaction:
        if duration_s <= 0:
            raise ValueError("duration_s muss positiv sein")
        transaction = ActionTransaction(
            action_id=f"action-{uuid.uuid4().hex}",
            actor=actor,
            lease_id=None,
            target=target,
            action_type="key-hold",
            phase=ActionPhase.PLANNED,
            planned_at=time.time(),
            key=key,
            expectation=expectation or ActionExpectation(),
        )
        with ControlLease(self.lease_path, actor, target) as lease:
            transaction.lease_id = lease.lease_id
            try:
                with self._safe_holds(transaction):
                    self.backend.key_down(key)
                    self.held_keys.add(key)
                    transaction.input_sequence.append({"kind": "keydown", "value": key})
                    transaction.transition(ActionPhase.DISPATCHED)
                    transaction.dispatched_at = time.time()
                    time.sleep(duration_s)
                    transaction.result["dispatch_complete"] = True
            except Exception as error:
                transaction.transition(ActionPhase.ABORTED, reason=str(error))
                transaction.rejection_reason = str(error)
        return transaction

    def pulse(
        self,
        *,
        actor: str,
        target: str,
        action_type: str,
        callback,
        button: int | None = None,
        key: str | None = None,
        expectation: ActionExpectation | None = None,
    ) -> ActionTransaction:
        """Run one atomic click/wheel/key pulse under the same transaction."""
        transaction = ActionTransaction(
            action_id=f"action-{uuid.uuid4().hex}",
            actor=actor,
            lease_id=None,
            target=target,
            action_type=action_type,
            phase=ActionPhase.PLANNED,
            planned_at=time.time(),
            button=button,
            key=key,
            expectation=expectation or ActionExpectation(),
        )
        with ControlLease(self.lease_path, actor, target) as lease:
            transaction.lease_id = lease.lease_id
            try:
                callback()
                transaction.input_sequence.append({"kind": action_type, "button": button, "key": key})
                transaction.transition(ActionPhase.DISPATCHED, dispatch_complete=True)
                transaction.dispatched_at = time.time()
            except Exception as error:
                transaction.transition(ActionPhase.ABORTED, reason=str(error))
                transaction.rejection_reason = str(error)
        return transaction

    def click(
        self,
        *,
        actor: str,
        target: str,
        button: int = 1,
        expectation: ActionExpectation | None = None,
    ) -> ActionTransaction:
        return self.pulse(
            actor=actor,
            target=target,
            action_type="click",
            button=button,
            expectation=expectation,
            callback=lambda: self.backend.click(button),
        )

    def wheel(
        self,
        *,
        actor: str,
        target: str,
        direction: int,
        expectation: ActionExpectation | None = None,
    ) -> ActionTransaction:
        if direction == 0:
            raise ValueError("wheel direction darf nicht 0 sein")
        return self.pulse(
            actor=actor,
            target=target,
            action_type="wheel",
            expectation=expectation,
            callback=lambda: self.backend.wheel(direction),
        )

    def key_press(self, *, actor: str, target: str, key: str, expectation: ActionExpectation | None = None) -> ActionTransaction:
        return self.pulse(
            actor=actor, target=target, action_type="key", key=key,
            expectation=expectation, callback=lambda: self.backend.key(key),
        )

    def type_text(self, *, actor: str, target: str, value: str, delay_ms: float = 0, expectation: ActionExpectation | None = None) -> ActionTransaction:
        return self.pulse(
            actor=actor, target=target, action_type="type",
            expectation=expectation, callback=lambda: self.backend.type_text(value, delay_ms),
        )

    def emergency_release(self) -> list[dict[str, Any]]:
        return self._release_all()

    @staticmethod
    def acknowledge(
        transaction: ActionTransaction,
        *,
        accepted: bool,
        frame_ids: list[str] | None = None,
        evidence: dict[str, Any] | None = None,
        reason: str | None = None,
    ) -> ActionTransaction:
        """Move dispatch to observed and then accepted/rejected only on proof."""
        transaction.observed_at = time.time()
        transaction.observed_frames.extend(frame_ids or [])
        transaction.result.update(evidence or {})
        transaction.transition(ActionPhase.OBSERVED, evidence_present=bool(evidence or frame_ids))
        if accepted:
            transaction.transition(ActionPhase.ACCEPTED)
        else:
            transaction.rejection_reason = reason or "Erwartete sichtbare Folge nicht belegt"
            transaction.transition(ActionPhase.REJECTED, reason=transaction.rejection_reason)
        return transaction
