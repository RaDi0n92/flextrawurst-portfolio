"""Stufe 5 des Megaplans: echter VPS-Dateisystemzugriff, ausserhalb des sicheren
data/tree/-Sandkastens. Bewusst zuletzt gebaut (hoechstes Risiko), bewusst getrennt
von planner_api.py gehalten.

Architektur-Entscheidung (mit Daniel abgestimmt, 2026-09-02, nach zwei ueber den
Auto-Mode-Klassifizierer blockierten Anlaeufen mit direktem Sofort-Schreiben):

- Umfang bewusst auf ALLOWED_ROOT (/root) begrenzt, nicht das ganze Server-
  Dateisystem. Daniels Grund: die Surface (flextrawurst-UI) liegt ausserhalb von
  /root/werkraum, aber innerhalb von /root - kein System-Ordner (/etc, andere Nutzer,
  System-Configs) ist erreichbar.
- LESEN ist direkt moeglich (browse/read) - reine Auskunft, kein Risiko.
- SCHREIBEN ist zweistufig, nicht direkt: ein AI-Strom ohne eigenen Terminal-Zugriff
  (z.B. ein reines Web-/MCP-Anbindung ohne Dateisystemzugriff - Stroeme MIT eigenem
  Terminal wie Claude Code/Codex/Gemini/GLM brauchen das hier ohnehin nicht, die
  schreiben laengst direkt) kann nur einen VORSCHLAG einreichen (propose_write).
  Der wird als pending_change gespeichert, OHNE die echte Datei anzufassen. Erst wenn
  Daniel (is_staff, im Planer) den Vorschlag explizit bestaetigt (approve), wird
  wirklich geschrieben. Kein Endpunkt ausser approve() schreibt je auf die echte
  Datei - "Login reicht fuer sofortigen unbeaufsichtigten Schreibzugriff" existiert
  hier bewusst nicht.
- Vor jedem tatsaechlichen Schreiben: automatisches Backup (Grundgesetz 4).
"""
from __future__ import annotations

import json
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from planner_api import _require_staff, _same_origin, MAX_FILE_BYTES
from real_fs_store import (
    ChangeAlreadyResolved,
    ChangeNotFound,
    JsonListStore,
    RealFsChangeStore,
    RealFsStoreError,
    StaleTarget,
    atomic_text_write,
    same_target,
    sha256_text,
    target_fingerprint,
)
from world_state import DEFAULT_STORE
from run_state import RunNotFound, read_run

ROOT = Path("/root/werkraum/Mein-Gesamtkonstrukt-planer")
ALLOWLIST_FILE = ROOT / "data" / "real_fs_paths.json"
ALLOWLIST_LOCK = ROOT / "data" / ".real_fs_paths.lock"
PENDING_FILE = ROOT / "data" / "real_fs_pending_changes.json"
PENDING_LOCK = ROOT / "data" / ".real_fs_pending_changes.lock"
BACKUPS_DIR = ROOT / "data" / "realfs_backups"

# Harte, im Code verankerte Grenze - siehe Modul-Docstring.
ALLOWED_ROOT = Path("/root").resolve()


def _allowlist_store() -> JsonListStore:
    return JsonListStore(ALLOWLIST_FILE, ALLOWLIST_LOCK)


def _pending_store() -> RealFsChangeStore:
    return RealFsChangeStore(PENDING_FILE, PENDING_LOCK)


def _staff_actor(request) -> dict:
    user = getattr(request, "user", None)
    account = ""
    getter = getattr(user, "get_username", None)
    if callable(getter):
        try:
            account = str(getter() or "").strip()
        except Exception:
            account = ""
    if not account:
        account = str(getattr(user, "username", "") or "").strip()
    return {"kind": "human", "account": account or "authenticated_staff"}


def _signal_world(event_type: str, data: dict, actor=None) -> dict:
    """Best-effort durable world pulse after a real_fs lifecycle change.

    The native real_fs record remains authoritative for the operation itself.
    current.json gets a canonical world event + serverRevision pulse so Planer and
    Schrottplatz can observe the durable consequence. Failure is returned instead
    of disguised as success or causing an unsafe retry of the already-finished
    native operation.
    """
    try:
        result = DEFAULT_STORE.commit(
            lambda state: None,
            event_type=event_type,
            event_data=data,
            actor=actor,
        )
        return {
            "ok": True,
            "serverRevision": result.wrapper["serverRevision"],
            "eventId": result.event["id"],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _read_json_list(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _write_json_list(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def _find_entry(entries: list[dict], entry_id: str) -> dict | None:
    for entry in entries:
        if entry.get("id") == entry_id:
            return entry
    return None


def _within_allowed_root(path: Path) -> bool:
    try:
        path.relative_to(ALLOWED_ROOT)
        return True
    except ValueError:
        return False


def _resolve_within(entry: dict, relative: str) -> Path:
    base = Path(entry["path"]).resolve()
    if entry["kind"] == "file":
        if relative:
            raise ValueError("file_entry_has_no_subpath")
        target = base
    else:
        target = (base / (relative or "").lstrip("/")).resolve()
    try:
        target.relative_to(base)
    except ValueError:
        raise ValueError("path_escapes_allowlisted_root")
    if not _within_allowed_root(target):
        raise ValueError("path_escapes_allowed_root")
    return target


def _backup(target: Path) -> str | None:
    if not target.exists() or not target.is_file():
        return None
    BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    safe_name = str(target).strip("/").replace("/", "__")[-180:]
    backup_path = BACKUPS_DIR / f"{stamp}__{safe_name}"
    shutil.copy2(target, backup_path)
    return str(backup_path)


def _entry_public(entry: dict) -> dict:
    return {"id": entry["id"], "path": entry["path"], "label": entry.get("label") or entry["path"], "kind": entry["kind"], "addedAt": entry.get("addedAt")}


def _node_info(path: Path) -> dict:
    stat = path.stat()
    return {
        "name": path.name,
        "kind": "folder" if path.is_dir() else "file",
        "size": stat.st_size if path.is_file() else None,
        "modifiedAt": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat().replace("+00:00", "Z"),
    }


@csrf_exempt
def real_fs_list(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)
    return JsonResponse({"ok": True, "entries": [_entry_public(e) for e in _read_json_list(ALLOWLIST_FILE)]}, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
def real_fs_add(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse({"ok": False, "error": "method_or_origin_not_allowed"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
    raw_path = str(body.get("path") or "").strip()
    label = str(body.get("label") or "").strip()
    if not raw_path.startswith("/"):
        return JsonResponse({"ok": False, "error": "path_must_be_absolute"}, status=400)
    resolved = Path(raw_path).resolve()
    if not _within_allowed_root(resolved):
        return JsonResponse({"ok": False, "error": "path_outside_allowed_root", "allowedRoot": str(ALLOWED_ROOT)}, status=403)
    if not resolved.exists():
        return JsonResponse({"ok": False, "error": "path_not_found"}, status=404)

    entry = {
        "id": f"rfs-{uuid.uuid4()}",
        "path": str(resolved),
        "label": label or str(resolved),
        "kind": "folder" if resolved.is_dir() else "file",
        "addedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }

    try:
        def mutate(entries):
            if any(Path(e["path"]) == resolved for e in entries):
                raise RealFsStoreError("already_added")
            entries.append(entry)
            return entry

        _allowlist_store().mutate(mutate)
    except RealFsStoreError as exc:
        if str(exc) == "already_added":
            return JsonResponse({"ok": False, "error": "already_added"}, status=409)
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    world = _signal_world(
        "world.connection.added",
        {"kind": "real_fs", "entryId": entry["id"], "path": entry["path"]},
        actor=_staff_actor(request),
    )
    return JsonResponse(
        {"ok": True, "entry": _entry_public(entry), "worldSignal": world},
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
def real_fs_remove(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse({"ok": False, "error": "method_or_origin_not_allowed"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
    entry_id = str(body.get("id") or "")

    try:
        def mutate(entries):
            for index, entry in enumerate(entries):
                if entry.get("id") == entry_id:
                    return entries.pop(index)
            raise ChangeNotFound(entry_id)

        removed = _allowlist_store().mutate(mutate)
    except ChangeNotFound:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    except RealFsStoreError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    world = _signal_world(
        "world.connection.removed",
        {"kind": "real_fs", "entryId": entry_id, "path": removed.get("path")},
        actor=_staff_actor(request),
    )
    return JsonResponse({"ok": True, "worldSignal": world})


@csrf_exempt
def real_fs_browse(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)
    entries = _read_json_list(ALLOWLIST_FILE)
    entry = _find_entry(entries, request.GET.get("id") or "")
    if not entry:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    if entry["kind"] != "folder":
        return JsonResponse({"ok": False, "error": "not_a_folder"}, status=400)
    try:
        target = _resolve_within(entry, request.GET.get("path") or "")
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    if not target.is_dir():
        return JsonResponse({"ok": False, "error": "not_a_folder"}, status=400)
    try:
        children = sorted(
            (_node_info(child) for child in target.iterdir()),
            key=lambda n: (n["kind"] != "folder", n["name"].lower()),
        )
    except PermissionError:
        return JsonResponse({"ok": False, "error": "permission_denied_on_host"}, status=403)
    return JsonResponse({"ok": True, "path": request.GET.get("path") or "", "children": children}, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
def real_fs_read(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)
    entries = _read_json_list(ALLOWLIST_FILE)
    entry = _find_entry(entries, request.GET.get("id") or "")
    if not entry:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    try:
        target = _resolve_within(entry, request.GET.get("path") or "")
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    if not target.is_file():
        return JsonResponse({"ok": False, "error": "not_a_file"}, status=400)
    try:
        size = target.stat().st_size
        if size > MAX_FILE_BYTES:
            return JsonResponse({"ok": False, "error": "file_too_large"}, status=413)
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return JsonResponse({"ok": False, "error": "not_utf8_text"}, status=415)
    except PermissionError:
        return JsonResponse({"ok": False, "error": "permission_denied_on_host"}, status=403)
    return JsonResponse({"ok": True, "content": content, "modifiedAt": _node_info(target)["modifiedAt"]}, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
def real_fs_propose_write(request):
    """Schreibt NIE direkt - legt nur einen pending_change an. Siehe Moduldoku."""
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse({"ok": False, "error": "method_or_origin_not_allowed"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
    entries = _read_json_list(ALLOWLIST_FILE)
    entry = _find_entry(entries, str(body.get("id") or ""))
    if not entry:
        return JsonResponse({"ok": False, "error": "not_found"}, status=404)
    relative = str(body.get("path") or "")
    try:
        target = _resolve_within(entry, relative)
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)
    if target.is_dir():
        return JsonResponse({"ok": False, "error": "target_is_a_folder"}, status=400)
    content = str(body.get("content") or "")
    if len(content.encode("utf-8")) > MAX_FILE_BYTES:
        return JsonResponse({"ok": False, "error": "file_too_large"}, status=413)
    proposed_by = str(body.get("proposedBy") or "unbekannter Strom").strip()[:100]

    correlation = None
    run_ref = str(body.get("runRef") or "").strip()
    if run_ref:
        try:
            run = read_run(run_ref, store=DEFAULT_STORE)
        except RunNotFound:
            return JsonResponse({"ok": False, "error": "run_not_found", "runRef": run_ref}, status=404)
        expected_run_version = body.get("expectedRunVersion")
        actual_run_version = int(run.get("version") or 0)
        if expected_run_version is not None and int(expected_run_version) != actual_run_version:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "run_version_conflict",
                    "runRef": run_ref,
                    "expectedRunVersion": int(expected_run_version),
                    "actualRunVersion": actual_run_version,
                },
                status=409,
            )
        requested_node = str(body.get("nodeRef") or "").strip()
        actual_node = str(run.get("currentNodeRef") or "").strip()
        if requested_node and actual_node and requested_node != actual_node:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "run_node_mismatch",
                    "runRef": run_ref,
                    "requestedNodeRef": requested_node,
                    "actualNodeRef": actual_node,
                },
                status=409,
            )
        requested_goal = str(body.get("goalRef") or "").strip()
        actual_goal = str(run.get("goalRef") or "").strip()
        if requested_goal and actual_goal and requested_goal != actual_goal:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "run_goal_mismatch",
                    "runRef": run_ref,
                    "requestedGoalRef": requested_goal,
                    "actualGoalRef": actual_goal,
                },
                status=409,
            )
        correlation = {
            "runRef": run_ref,
            "runVersionAtProposal": actual_run_version,
            "nodeRef": requested_node or actual_node or None,
            "goalRef": requested_goal or actual_goal or None,
        }

    try:
        expected_target = target_fingerprint(target)
    except PermissionError:
        return JsonResponse({"ok": False, "error": "permission_denied_on_host"}, status=403)

    current_content = None
    if target.is_file():
        try:
            current_content = target.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return JsonResponse({"ok": False, "error": "not_utf8_text"}, status=415)
        except PermissionError:
            return JsonResponse({"ok": False, "error": "permission_denied_on_host"}, status=403)

    change = {
        "id": f"rfsc-{uuid.uuid4()}",
        "entryId": entry["id"],
        "path": relative,
        "targetPath": str(target),
        "proposedContent": content,
        "proposedContentSha256": sha256_text(content),
        "currentContent": current_content,
        "expectedTarget": expected_target,
        "proposedBy": proposed_by,
        "proposedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": "pending",
        "approvalStatus": "pending",
        "effectStatus": "not_started",
        "correlation": correlation,
    }
    try:
        _pending_store().add(change)
    except RealFsStoreError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    world = _signal_world(
        "approval.requested",
        {
            "kind": "real_fs.write",
            "approvalRef": change["id"],
            "entryId": entry["id"],
            "targetPath": str(target),
            "expectedTarget": expected_target,
            "correlation": correlation,
            "declaredProposedBy": proposed_by,
        },
        actor=None,
    )
    return JsonResponse(
        {"ok": True, "changeId": change["id"], "worldSignal": world},
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
def real_fs_pending_list(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "GET":
        return JsonResponse({"ok": False, "error": "method_not_allowed"}, status=405)
    try:
        pending = [c for c in _pending_store().read_all() if c.get("status") == "pending"]
    except RealFsStoreError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)
    return JsonResponse({"ok": True, "pending": pending}, json_dumps_params={"ensure_ascii": False})


@csrf_exempt
def real_fs_approve(request):
    """Human approval + separately verified real file effect."""
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse({"ok": False, "error": "method_or_origin_not_allowed"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
    change_id = str(body.get("id") or "")

    try:
        change = _pending_store().get(change_id)
    except ChangeNotFound:
        return JsonResponse({"ok": False, "error": "not_found_or_already_resolved"}, status=404)
    except RealFsStoreError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)
    if change.get("status") != "pending":
        return JsonResponse({"ok": False, "error": "not_found_or_already_resolved"}, status=404)

    entries = _read_json_list(ALLOWLIST_FILE)
    entry = _find_entry(entries, change["entryId"])
    if not entry:
        return JsonResponse({"ok": False, "error": "entry_no_longer_allowlisted"}, status=404)
    try:
        target = _resolve_within(entry, change["path"])
    except ValueError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=400)

    try:
        actual_before_approval = target_fingerprint(target)
        claimed = _pending_store().claim_approval(
            change_id,
            actual_target=actual_before_approval,
        )
    except StaleTarget as exc:
        world = _signal_world(
            "approval.stale",
            {
                "kind": "real_fs.write",
                "approvalRef": change_id,
                "targetPath": str(target),
                "expectedTarget": exc.expected,
                "actualTarget": exc.actual,
                "correlation": change.get("correlation"),
            },
            actor=_staff_actor(request),
        )
        return JsonResponse(
            {
                "ok": False,
                "error": "stale_target",
                "expectedTarget": exc.expected,
                "actualTarget": exc.actual,
                "worldSignal": world,
            },
            status=409,
            json_dumps_params={"ensure_ascii": False},
        )
    except (ChangeNotFound, ChangeAlreadyResolved):
        return JsonResponse({"ok": False, "error": "not_found_or_already_resolved"}, status=404)
    except RealFsStoreError as exc:
        status = 409 if str(exc) == "proposal_missing_expected_target" else 500
        return JsonResponse({"ok": False, "error": str(exc)}, status=status)
    except PermissionError:
        return JsonResponse({"ok": False, "error": "permission_denied_on_host"}, status=403)

    approval_world = _signal_world(
        "approval.approved",
        {
            "kind": "real_fs.write",
            "approvalRef": change_id,
            "targetPath": str(target),
            "correlation": claimed.get("correlation"),
        },
        actor=_staff_actor(request),
    )

    backup_path = None
    try:
        backup_path = _backup(target)

        # Narrow the race window once more after backup and immediately before
        # the atomic replace. This is still best-effort against external writers
        # that do not honor our locks, not mathematical filesystem CAS.
        final_precondition = target_fingerprint(target)
        expected_target = claimed.get("expectedTarget")
        if not isinstance(expected_target, dict) or not same_target(expected_target, final_precondition):
            failed = _pending_store().finish_effect(
                change_id,
                effect_status="failed",
                effect={
                    "reason": "precondition_changed_after_approval",
                    "expectedTarget": expected_target,
                    "actualTarget": final_precondition,
                },
                backup=backup_path,
            )
            effect_world = _signal_world(
                "effect.failed",
                {
                    "kind": "real_fs.write",
                    "approvalRef": change_id,
                    "targetPath": str(target),
                    "reason": "precondition_changed_after_approval",
                    "correlation": claimed.get("correlation"),
                },
                actor=_staff_actor(request),
            )
            return JsonResponse(
                {
                    "ok": False,
                    "error": "stale_target_after_approval",
                    "effectStatus": failed.get("effectStatus"),
                    "worldSignal": {"approval": approval_world, "effect": effect_world},
                },
                status=409,
                json_dumps_params={"ensure_ascii": False},
            )

        atomic_text_write(target, claimed["proposedContent"])
        actual_effect = target_fingerprint(target)
        expected_effect_hash = claimed.get("proposedContentSha256") or sha256_text(claimed["proposedContent"])
        if actual_effect.get("sha256") != expected_effect_hash:
            failed = _pending_store().finish_effect(
                change_id,
                effect_status="failed",
                effect={
                    "reason": "effect_hash_mismatch",
                    "target": actual_effect,
                    "expectedSha256": expected_effect_hash,
                },
                backup=backup_path,
            )
            effect_world = _signal_world(
                "effect.failed",
                {
                    "kind": "real_fs.write",
                    "approvalRef": change_id,
                    "targetPath": str(target),
                    "reason": "effect_hash_mismatch",
                    "correlation": claimed.get("correlation"),
                },
                actor=_staff_actor(request),
            )
            return JsonResponse(
                {
                    "ok": False,
                    "error": "effect_hash_mismatch",
                    "effectStatus": failed.get("effectStatus"),
                    "actualTarget": actual_effect,
                    "worldSignal": {"approval": approval_world, "effect": effect_world},
                },
                status=500,
                json_dumps_params={"ensure_ascii": False},
            )

        finished = _pending_store().finish_effect(
            change_id,
            effect_status="confirmed",
            effect={"target": actual_effect},
            backup=backup_path,
        )
        effect_world = _signal_world(
            "effect.confirmed",
            {
                "kind": "real_fs.write",
                "approvalRef": change_id,
                "targetPath": str(target),
                "target": actual_effect,
                "correlation": claimed.get("correlation"),
            },
            actor=_staff_actor(request),
        )
        return JsonResponse(
            {
                "ok": True,
                "backup": backup_path,
                "modifiedAt": _node_info(target)["modifiedAt"],
                "sha256": actual_effect.get("sha256"),
                "effectStatus": finished.get("effectStatus"),
                "worldSignal": {"approval": approval_world, "effect": effect_world},
            },
            json_dumps_params={"ensure_ascii": False},
        )
    except PermissionError:
        error = "permission_denied_on_host"
        status = 403
    except Exception as exc:
        error = f"effect_failed: {exc}"
        status = 500

    try:
        _pending_store().finish_effect(
            change_id,
            effect_status="failed",
            effect={"reason": error},
            backup=backup_path,
        )
    except RealFsStoreError:
        pass
    effect_world = _signal_world(
        "effect.failed",
        {
            "kind": "real_fs.write",
            "approvalRef": change_id,
            "targetPath": str(target),
            "reason": error,
            "correlation": claimed.get("correlation"),
        },
        actor=_staff_actor(request),
    )
    return JsonResponse(
        {
            "ok": False,
            "error": error,
            "worldSignal": {"approval": approval_world, "effect": effect_world},
        },
        status=status,
        json_dumps_params={"ensure_ascii": False},
    )


@csrf_exempt
def real_fs_reject(request):
    denied = _require_staff(request)
    if denied:
        return denied
    if request.method != "POST" or not _same_origin(request):
        return JsonResponse({"ok": False, "error": "method_or_origin_not_allowed"}, status=405)
    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
    except Exception:
        return JsonResponse({"ok": False, "error": "invalid_json"}, status=400)
    change_id = str(body.get("id") or "")
    try:
        change = _pending_store().reject(change_id)
    except (ChangeNotFound, ChangeAlreadyResolved):
        return JsonResponse({"ok": False, "error": "not_found_or_already_resolved"}, status=404)
    except RealFsStoreError as exc:
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)

    world = _signal_world(
        "approval.rejected",
        {
            "kind": "real_fs.write",
            "approvalRef": change_id,
            "targetPath": change.get("targetPath"),
            "correlation": change.get("correlation"),
        },
        actor=_staff_actor(request),
    )
    return JsonResponse({"ok": True, "worldSignal": world})
