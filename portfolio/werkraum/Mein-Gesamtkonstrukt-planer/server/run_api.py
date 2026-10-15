#!/usr/bin/env python3
"""HTTP skin for persistent gkos.run.v0 state.

No execution happens here. These endpoints only create/read/transition durable
runs that point at existing Koerper routes and goals. Tool/process adapters may
later drive the same functions without changing the canonical run model.
"""
from __future__ import annotations

import json
from typing import Any

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from planner_api import _require_staff, _same_origin, MAX_BODY_BYTES
from run_state import (
    InvalidRunTransition,
    RunNotFound,
    RunStateError,
    RunVersionConflict,
    create_run,
    read_run,
    read_runs,
    transition_run,
)
from world_state import DEFAULT_STORE, RevisionConflict, WorldStateError


STORE = DEFAULT_STORE


def _body(request) -> dict[str, Any]:
    if len(request.body) > MAX_BODY_BYTES:
        raise ValueError("body_too_large")
    value = json.loads(request.body.decode("utf-8") or "{}")
    if not isinstance(value, dict):
        raise ValueError("invalid_json")
    return value


def _server_revision() -> int:
    return int(STORE.read_wrapper().get("serverRevision") or 0)


def _error_response(exc: Exception) -> JsonResponse:
    if isinstance(exc, RunNotFound):
        return JsonResponse({"ok": False, "error": "run_not_found"}, status=404)
    if isinstance(exc, RunVersionConflict):
        return JsonResponse(
            {
                "ok": False,
                "error": "run_version_conflict",
                "runId": exc.run_id,
                "expectedRunVersion": exc.expected,
                "actualRunVersion": exc.actual,
            },
            status=409,
        )
    if isinstance(exc, RevisionConflict):
        return JsonResponse(
            {
                "ok": False,
                "error": "server_revision_conflict",
                "expectedServerRevision": exc.expected,
                "actualServerRevision": exc.actual,
            },
            status=409,
        )
    if isinstance(exc, InvalidRunTransition):
        return JsonResponse({"ok": False, "error": str(exc)}, status=409)
    if isinstance(exc, (RunStateError, WorldStateError, ValueError)):
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    return JsonResponse({"ok": False, "error": f"run_api_failed: {exc}"}, status=500)


@csrf_exempt
def run_list_create(request):
    denied = _require_staff(request)
    if denied:
        return denied

    if request.method == "GET":
        try:
            run_id = str(request.GET.get("id") or "").strip()
            if run_id:
                run = read_run(run_id, store=STORE)
                return JsonResponse(
                    {"ok": True, "serverRevision": _server_revision(), "run": run},
                    json_dumps_params={"ensure_ascii": False},
                )
            runs = read_runs(store=STORE)
            phase = str(request.GET.get("phase") or "").strip()
            if phase:
                runs = [run for run in runs if run.get("phase") == phase]
            return JsonResponse(
                {"ok": True, "serverRevision": _server_revision(), "runs": runs},
                json_dumps_params={"ensure_ascii": False},
            )
        except Exception as exc:
            return _error_response(exc)

    if request.method != "POST" or not _same_origin(request):
        return JsonResponse(
            {"ok": False, "error": "method_or_origin_not_allowed"}, status=405
        )

    try:
        body = _body(request)
        run = create_run(
            koerper_ref=str(body.get("koerperRef") or ""),
            goal_ref=body.get("goalRef"),
            scope_refs=body.get("scopeRefs") if isinstance(body.get("scopeRefs"), list) else None,
            actor=body.get("actor") if isinstance(body.get("actor"), dict) else None,
            phase=str(body.get("phase") or "prepared"),
            current_node_ref=body.get("currentNodeRef"),
            wait=body.get("wait") if isinstance(body.get("wait"), dict) else None,
            iteration=int(body.get("iteration") or 1),
            run_id=str(body.get("runId") or "").strip() or None,
            store=STORE,
            expected_server_revision=(
                int(body["expectedServerRevision"])
                if body.get("expectedServerRevision") is not None
                else None
            ),
        )
        return JsonResponse(
            {"ok": True, "serverRevision": _server_revision(), "run": run},
            status=201,
            json_dumps_params={"ensure_ascii": False},
        )
    except Exception as exc:
        return _error_response(exc)


@csrf_exempt
def run_transition(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse(
            {"ok": False, "error": "method_or_origin_not_allowed"}, status=405
        )

    try:
        body = _body(request)
        run_id = str(body.get("runId") or "").strip()
        if not run_id:
            raise ValueError("run_id_required")

        kwargs: dict[str, Any] = {
            "phase": body.get("phase"),
            "iteration": int(body["iteration"]) if body.get("iteration") is not None else None,
            "evidence_ref": str(body.get("evidenceRef") or "").strip() or None,
            "native_event_ref": str(body.get("nativeEventRef") or "").strip() or None,
            "expected_run_version": (
                int(body["expectedRunVersion"])
                if body.get("expectedRunVersion") is not None
                else None
            ),
            "expected_server_revision": (
                int(body["expectedServerRevision"])
                if body.get("expectedServerRevision") is not None
                else None
            ),
            "store": STORE,
        }
        # Missing keys mean "leave unchanged". Explicit null means "clear".
        if "currentNodeRef" in body:
            kwargs["current_node_ref"] = body.get("currentNodeRef")
        if "actor" in body:
            kwargs["actor"] = body.get("actor") if isinstance(body.get("actor"), dict) else None
        if "wait" in body:
            kwargs["wait"] = body.get("wait") if isinstance(body.get("wait"), dict) else None
        if "handoffRef" in body:
            kwargs["handoff_ref"] = body.get("handoffRef")

        run = transition_run(run_id, **kwargs)
        return JsonResponse(
            {"ok": True, "serverRevision": _server_revision(), "run": run},
            json_dumps_params={"ensure_ascii": False},
        )
    except Exception as exc:
        return _error_response(exc)
