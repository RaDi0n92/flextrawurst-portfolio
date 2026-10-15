#!/usr/bin/env python3
"""Persistent run projection for existing gkos.koerper.v1 bodies.

A Koerper is the reusable route/structure. A Run is one concrete attempt moving
through it. This module intentionally does not execute tools or infer agency; it
only persists the durable run state that the rest of the world may project.
"""
from __future__ import annotations

import copy
import uuid
from typing import Any

from world_state import DEFAULT_STORE, WorldStateStore, now_iso


RUN_SCHEMA = "gkos.run.v0"
RUN_PHASES = {
    "prepared",
    "running",
    "waiting",
    "review",
    "completed",
    "failed",
    "cancelled",
}
TERMINAL_PHASES = {"completed", "failed", "cancelled"}
ALLOWED_TRANSITIONS = {
    "prepared": {"prepared", "running", "waiting", "cancelled"},
    "running": {"running", "waiting", "review", "completed", "failed", "cancelled"},
    "waiting": {"waiting", "running", "review", "failed", "cancelled"},
    "review": {"review", "running", "waiting", "completed", "failed", "cancelled"},
    "completed": {"completed"},
    "failed": {"failed"},
    "cancelled": {"cancelled"},
}


class RunStateError(RuntimeError):
    pass


class RunNotFound(RunStateError):
    pass


class RunVersionConflict(RunStateError):
    def __init__(self, run_id: str, expected: int, actual: int):
        super().__init__(
            f"run_version_conflict: run={run_id} expected={expected} actual={actual}"
        )
        self.run_id = run_id
        self.expected = expected
        self.actual = actual


class InvalidRunTransition(RunStateError):
    pass


def _runs(state: dict[str, Any]) -> list[dict[str, Any]]:
    runs = state.setdefault("runs", [])
    if not isinstance(runs, list):
        raise RunStateError("runs_must_be_list")
    return runs


def _find_run(state: dict[str, Any], run_id: str) -> dict[str, Any]:
    for run in _runs(state):
        if isinstance(run, dict) and run.get("id") == run_id:
            return run
    raise RunNotFound(run_id)


def _clean_refs(values: list[str] | tuple[str, ...] | None) -> list[str]:
    if not values:
        return []
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _validate_phase(phase: str) -> str:
    value = str(phase or "").strip()
    if value not in RUN_PHASES:
        raise InvalidRunTransition(f"invalid_run_phase: {value}")
    return value


def _validate_wait(phase: str, wait: dict[str, Any] | None) -> None:
    if phase == "waiting":
        if not isinstance(wait, dict) or not str(wait.get("reason") or "").strip():
            raise InvalidRunTransition("waiting_requires_wait_reason")
    elif wait is not None:
        raise InvalidRunTransition("wait_payload_requires_waiting_phase")


def read_runs(store: WorldStateStore = DEFAULT_STORE) -> list[dict[str, Any]]:
    state = store.read_wrapper()["state"]
    return copy.deepcopy(_runs(state))


def read_run(run_id: str, store: WorldStateStore = DEFAULT_STORE) -> dict[str, Any]:
    state = store.read_wrapper()["state"]
    return copy.deepcopy(_find_run(state, run_id))


def create_run(
    *,
    koerper_ref: str,
    goal_ref: str | None = None,
    scope_refs: list[str] | tuple[str, ...] | None = None,
    actor: dict[str, Any] | None = None,
    phase: str = "prepared",
    current_node_ref: str | None = None,
    wait: dict[str, Any] | None = None,
    iteration: int = 1,
    run_id: str | None = None,
    store: WorldStateStore = DEFAULT_STORE,
    expected_server_revision: int | None = None,
) -> dict[str, Any]:
    koerper_ref = str(koerper_ref or "").strip()
    if not koerper_ref:
        raise RunStateError("koerper_ref_required")
    phase = _validate_phase(phase)
    _validate_wait(phase, wait)
    if int(iteration) < 1:
        raise RunStateError("iteration_must_be_positive")

    at = now_iso()
    rid = str(run_id or f"run-{uuid.uuid4()}")
    new_run = {
        "schema": RUN_SCHEMA,
        "id": rid,
        "version": 1,
        "goalRef": str(goal_ref).strip() if goal_ref else None,
        "koerperRef": koerper_ref,
        "scopeRefs": _clean_refs(scope_refs),
        "actor": copy.deepcopy(actor) if isinstance(actor, dict) else None,
        "phase": phase,
        "currentNodeRef": str(current_node_ref).strip() if current_node_ref else None,
        "iteration": int(iteration),
        "wait": copy.deepcopy(wait),
        "createdAt": at,
        "startedAt": at if phase == "running" else None,
        "updatedAt": at,
        "completedAt": at if phase in TERMINAL_PHASES else None,
        "evidenceRefs": [],
        "eventRefs": [],
        "handoffRef": None,
    }

    def mutate(state: dict[str, Any]):
        runs = _runs(state)
        if any(isinstance(item, dict) and item.get("id") == rid for item in runs):
            raise RunStateError(f"run_already_exists: {rid}")
        runs.append(copy.deepcopy(new_run))
        return {
            "runRef": rid,
            "koerperRef": koerper_ref,
            "goalRef": new_run["goalRef"],
            "phase": phase,
            "runVersion": 1,
        }

    result = store.commit(
        mutate,
        event_type="run.created",
        event_data={
            "runRef": rid,
            "koerperRef": koerper_ref,
            "goalRef": new_run["goalRef"],
            "phase": phase,
            "currentNodeRef": new_run["currentNodeRef"],
        },
        actor=new_run["actor"],
        expected_server_revision=expected_server_revision,
    )
    return copy.deepcopy(_find_run(result.wrapper["state"], rid))


def transition_run(
    run_id: str,
    *,
    phase: str | None = None,
    current_node_ref: str | None | object = ...,
    actor: dict[str, Any] | None | object = ...,
    wait: dict[str, Any] | None | object = ...,
    iteration: int | None = None,
    evidence_ref: str | None = None,
    native_event_ref: str | None = None,
    handoff_ref: str | None | object = ...,
    expected_run_version: int | None = None,
    expected_server_revision: int | None = None,
    store: WorldStateStore = DEFAULT_STORE,
) -> dict[str, Any]:
    rid = str(run_id or "").strip()
    if not rid:
        raise RunStateError("run_id_required")

    transition_summary: dict[str, Any] = {}

    def mutate(state: dict[str, Any]):
        run = _find_run(state, rid)
        actual_version = int(run.get("version") or 0)
        if expected_run_version is not None and int(expected_run_version) != actual_version:
            raise RunVersionConflict(rid, int(expected_run_version), actual_version)

        old_phase = _validate_phase(str(run.get("phase") or ""))
        new_phase = _validate_phase(phase) if phase is not None else old_phase
        if new_phase not in ALLOWED_TRANSITIONS[old_phase]:
            raise InvalidRunTransition(f"invalid_transition: {old_phase}->{new_phase}")

        if iteration is not None and int(iteration) < 1:
            raise RunStateError("iteration_must_be_positive")

        next_wait: dict[str, Any] | None
        if wait is ...:
            next_wait = copy.deepcopy(run.get("wait")) if new_phase == "waiting" else None
        else:
            next_wait = copy.deepcopy(wait) if isinstance(wait, dict) else None
        _validate_wait(new_phase, next_wait)

        before = {
            "phase": old_phase,
            "currentNodeRef": run.get("currentNodeRef"),
            "iteration": run.get("iteration"),
            "runVersion": actual_version,
        }

        at = now_iso()
        run["phase"] = new_phase
        if current_node_ref is not ...:
            run["currentNodeRef"] = (
                str(current_node_ref).strip() if current_node_ref else None
            )
        if actor is not ...:
            run["actor"] = copy.deepcopy(actor) if isinstance(actor, dict) else None
        if iteration is not None:
            run["iteration"] = int(iteration)
        run["wait"] = next_wait
        if handoff_ref is not ...:
            run["handoffRef"] = str(handoff_ref).strip() if handoff_ref else None
        if evidence_ref:
            refs = _clean_refs([*run.get("evidenceRefs", []), evidence_ref])
            run["evidenceRefs"] = refs
        if native_event_ref:
            refs = _clean_refs([*run.get("eventRefs", []), native_event_ref])
            run["eventRefs"] = refs
        if not run.get("startedAt") and new_phase in {"running", "waiting", "review"}:
            run["startedAt"] = at
        if new_phase in TERMINAL_PHASES:
            run["completedAt"] = at
        run["updatedAt"] = at
        run["version"] = actual_version + 1

        after = {
            "phase": new_phase,
            "currentNodeRef": run.get("currentNodeRef"),
            "iteration": run.get("iteration"),
            "runVersion": run["version"],
        }
        transition_summary.update({"runRef": rid, "before": before, "after": after})
        if next_wait is not None:
            transition_summary["wait"] = copy.deepcopy(next_wait)
        if evidence_ref:
            transition_summary["evidenceRef"] = evidence_ref
        if native_event_ref:
            transition_summary["nativeEventRef"] = native_event_ref
        return copy.deepcopy(transition_summary)

    # The actor stored in the event should be the actor responsible after the
    # transition when explicitly supplied. If omitted, provenance still lives in
    # the run itself and nativeEventRef; we do not invent an actor here.
    event_actor = copy.deepcopy(actor) if isinstance(actor, dict) else None
    result = store.commit(
        mutate,
        event_type="run.transitioned",
        event_data={"runRef": rid},
        actor=event_actor,
        expected_server_revision=expected_server_revision,
    )
    return copy.deepcopy(_find_run(result.wrapper["state"], rid))
