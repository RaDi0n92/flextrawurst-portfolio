from __future__ import annotations

import copy
import datetime as dt
import fcntl
import hashlib
import json
import os
import shutil
import tempfile
import uuid
import zipfile
from pathlib import Path
from typing import Any, Iterable

from .browser_capture import BrowserCaptureError, browser_chat_status, read_browser_timeline
from .browser_experiment_markdown import HUMAN_MARKDOWN_FILES, build_human_readable_export

STORE_ROOT = Path(
    os.environ.get(
        "FLEXTRAWURST_UI_VISIBLE_STORE_ROOT",
        "/root/werkraum/_gpt/ui_visible_conversations",
    )
)
EXPERIMENTS_ROOT = STORE_ROOT / "_experiments"
EXPERIMENT_SCHEMA_VERSION = "1.0-browser-multisession-experiment"
DEFAULT_SOFTWARE_VERSIONS = {
    "experiment_schema_version": EXPERIMENT_SCHEMA_VERSION,
    "recorder_schema_version": "2.1-browser-capture-b-timeline",
    "extension_version": "1.5.0",
    "receiver_version": "1.3.0",
    "mcp_version": "action-history-toolset-35",
    "vps_service_version": "chatgpt-browser-recorder.service",
}
EXPERIMENT_STATUSES = {"prepared", "active", "paused", "ended", "aborted", "incomplete"}
PARTICIPANT_STATES = {"active", "waiting", "completed"}
MESSAGE_STATES = {
    "created",
    "sent",
    "available",
    "read_confirmed",
    "explicitly_mentioned",
    "answered",
    "implemented",
    "contradicted",
    "unanswered",
}
INFLUENCE_CLASSES = {
    "direct_confirmed",
    "read_confirmed",
    "explicitly_acknowledged",
    "implemented_after_exposure",
    "human_relay_confirmed",
    "strongly_derived",
    "weakly_derived",
    "similarity_only",
    "contradicted",
    "unknown",
    "unattributed_context_possible",
}
DIRECT_EVIDENCE_TYPES = {
    "matching_correlation_id",
    "direct_reply",
    "read_then_explicit_reference",
    "verbatim_or_named_adoption",
    "technical_sender_receiver_chain",
    "human_relay_confirmed",
}
ANNOTATION_STATUSES = {"open", "confirmed", "refuted"}
KNOWN_CHANNELS = {
    "direct_mcp_message",
    "existing_inbox",
    "shared_file",
    "action_history",
    "claim_or_responsibility_body",
    "shared_project_state",
    "shared_database_entry",
    "daniel_manual_relay",
    "visible_browser_message",
    "other_proven_vps_channel",
    "unknown_or_unobservable",
}


class BrowserExperimentError(RuntimeError):
    pass


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _parse_time(value: Any) -> dt.datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def _safe_component(value: str, fallback: str = "item") -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in str(value or "").strip())
    cleaned = cleaned.strip("-._")
    return (cleaned or fallback)[:160]


def _canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _sha_value(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_bytes(path: Path, content: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, mode)
        os.replace(temporary, path)
        os.chmod(path, mode)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_bytes(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def _append_jsonl(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8") + b"\n"
    with path.open("ab") as handle:
        handle.write(encoded)
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o600)


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return copy.deepcopy(default)
    except json.JSONDecodeError as exc:
        raise BrowserExperimentError(f"Ungültiges JSON in {path}: {exc}") from exc


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise BrowserExperimentError(f"Ungültige JSONL-Zeile {number} in {path}: {exc}") from exc
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    handle = path.open("a+b")
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    return handle


def _experiment_folder(experiment_id: str) -> Path:
    safe = _safe_component(experiment_id, "experiment")
    folder = EXPERIMENTS_ROOT / safe
    if not folder.is_dir():
        raise BrowserExperimentError(f"Versuch nicht gefunden: {experiment_id}")
    return folder


def _state_path(folder: Path) -> Path:
    return folder / "EXPERIMENT.json"


def _events_path(folder: Path) -> Path:
    return folder / "experiment_events.jsonl"


def _public_state(state: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(state)


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4()}"


def _active_phase_id(state: dict[str, Any]) -> str | None:
    phase_id = state.get("active_phase_id")
    phase = state.get("phases", {}).get(str(phase_id or ""))
    return str(phase_id) if isinstance(phase, dict) and phase.get("status") == "active" else None


def _event(
    state: dict[str, Any],
    event_type: str,
    payload: dict[str, Any],
    *,
    source: str = "daniel_manual",
    timestamp_utc: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0-experiment-event",
        "event_id": _new_id("experiment-event"),
        "experiment_id": state["experiment_id"],
        "event_type": event_type,
        "timestamp_utc": timestamp_utc or _now(),
        "phase_id": _active_phase_id(state),
        "source": source,
        "payload": payload,
        "primary_browser_events_modified": False,
        "action_history_modified": False,
    }


def _commit(folder: Path, state: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    state["updated_utc"] = event["timestamp_utc"]
    state["event_count"] = int(state.get("event_count", 0)) + 1
    state["last_event_id"] = event["event_id"]
    _append_jsonl(_events_path(folder), event)
    _atomic_json(_state_path(folder), state)
    return event


def _record_error(folder: Path, operation: str, error: Exception) -> None:
    try:
        _append_jsonl(folder / "experiment_errors.jsonl", {
            "timestamp_utc": _now(),
            "operation": operation,
            "error": repr(error),
            "recorder_primary_sources_preserved": True,
            "action_history_preserved": True,
        })
    except Exception:
        pass


def create_browser_experiment(
    name: str,
    description: str | None = None,
    *,
    software_versions: dict[str, Any] | None = None,
) -> dict[str, Any]:
    clean_name = str(name or "").strip()
    if not clean_name:
        raise BrowserExperimentError("Versuchsname darf nicht leer sein")
    EXPERIMENTS_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    global_lock = _lock(EXPERIMENTS_ROOT / ".experiments.lock")
    try:
        created = _now()
        experiment_id = f"experiment-{created.replace(':', '').replace('.', '')}-{uuid.uuid4().hex[:8]}"
        folder = EXPERIMENTS_ROOT / _safe_component(experiment_id)
        folder.mkdir(parents=True, exist_ok=False, mode=0o700)
        versions = dict(DEFAULT_SOFTWARE_VERSIONS)
        versions.update({str(k): v for k, v in (software_versions or {}).items()})
        state = {
            "schema_version": EXPERIMENT_SCHEMA_VERSION,
            "experiment_id": experiment_id,
            "name": clean_name[:200],
            "description": str(description or "")[:4000] or None,
            "created_utc": created,
            "started_utc": None,
            "ended_utc": None,
            "updated_utc": created,
            "status": "prepared",
            "software_versions": versions,
            "participants": {},
            "participant_order": [],
            "phases": {},
            "phase_order": [],
            "active_phase_id": None,
            "stimuli": {},
            "snapshots": {},
            "messages": {},
            "exposures": {},
            "influences": {},
            "annotations": {},
            "self_reports": {},
            "comparisons": {},
            "control_conditions": {},
            "emergency_stop": {"active": False, "activated_utc": None, "released_utc": None},
            "event_count": 0,
            "last_event_id": None,
            "source_boundaries": {
                "browser_and_action_history_are_primary": True,
                "experiment_layer_is_regenerable_grouping": True,
                "automatic_communication": False,
                "automatic_role_assignment": False,
                "global_scientific_isolation_claimed": False,
            },
            "paths": {
                "state": str(folder / "EXPERIMENT.json"),
                "events": str(folder / "experiment_events.jsonl"),
                "timeline_machine": str(folder / "EXPERIMENT_TIMELINE.json"),
                "timeline_human": str(folder / "EXPERIMENT_TIMELINE.md"),
                "errors": str(folder / "experiment_errors.jsonl"),
                "exports": str(folder / "exports"),
            },
        }
        event = _event(state, "experiment_created", {
            "name": state["name"],
            "description": state["description"],
            "explicit_human_action_required_for_start": True,
        })
        _commit(folder, state, event)
        return {"ok": True, "folder": str(folder), "experiment": _public_state(state), "event": event}
    finally:
        fcntl.flock(global_lock.fileno(), fcntl.LOCK_UN)
        global_lock.close()


def list_browser_experiments(limit: int = 100) -> dict[str, Any]:
    limit = max(1, min(int(limit), 1000))
    if not EXPERIMENTS_ROOT.exists():
        return {"ok": True, "count": 0, "returned": 0, "experiments": []}
    rows: list[dict[str, Any]] = []
    for path in EXPERIMENTS_ROOT.glob("*/EXPERIMENT.json"):
        try:
            state = _read_json(path, {})
        except Exception:
            continue
        rows.append({
            "experiment_id": state.get("experiment_id"),
            "name": state.get("name"),
            "description": state.get("description"),
            "status": state.get("status"),
            "created_utc": state.get("created_utc"),
            "started_utc": state.get("started_utc"),
            "ended_utc": state.get("ended_utc"),
            "updated_utc": state.get("updated_utc"),
            "participant_count": sum(1 for p in state.get("participants", {}).values() if not p.get("removed_utc")),
            "active_phase_id": state.get("active_phase_id"),
            "emergency_stop": bool(state.get("emergency_stop", {}).get("active")),
        })
    rows.sort(key=lambda row: str(row.get("updated_utc") or ""), reverse=True)
    return {"ok": True, "count": len(rows), "returned": min(len(rows), limit), "experiments": rows[:limit]}


def _tab_ids_from_status(status: dict[str, Any]) -> list[str]:
    values: set[str] = set()
    for turn in status.get("turns", []):
        values.update(str(item) for item in (turn.get("tab_instance_ids") or []) if item)
    for record in (status.get("manifest", {}).get("imports") or {}).values():
        if isinstance(record, dict):
            values.update(str(item) for item in (record.get("tab_instance_ids") or []) if item)
    return sorted(values)


def _participant_live_view(participant: dict[str, Any]) -> dict[str, Any]:
    identifier = participant.get("conversation_id") or participant.get("local_conversation_id")
    if not identifier:
        return {"available": False, "error": "participant_without_conversation_identifier"}
    try:
        status = browser_chat_status(str(identifier))
        turns = status.get("turns", [])
        last_turn = turns[-1] if turns else None
        timeline = status.get("b_timeline") or {}
        return {
            "available": True,
            "folder": status.get("folder"),
            "chat_title": status.get("manifest", {}).get("current_title"),
            "alias": status.get("manifest", {}).get("alias"),
            "tab_instance_ids": _tab_ids_from_status(status),
            "last_turn_id": last_turn.get("turn_id") if last_turn else None,
            "last_turn_status": last_turn.get("status") if last_turn else None,
            "ui_completeness_status": last_turn.get("completeness_verdict") if last_turn else "unknown",
            "mcp_binding_status": last_turn.get("mcp_binding_status") if last_turn else "not_bound",
            "mcp_session_ids": sorted({
                str(turn.get("mcp_session_id"))
                for turn in turns
                if turn.get("mcp_session_id")
            }),
            "last_visible_activity_utc": status.get("manifest", {}).get("last_event_utc"),
            "last_technical_activity_utc": timeline.get("generated_utc") if timeline.get("confirmed_link_count") else None,
            "gap_count": status.get("manifest", {}).get("gap_count", 0),
            "b_timeline": timeline,
        }
    except Exception as exc:
        return {"available": False, "error": repr(exc)}


def browser_experiment_status(experiment_id: str, *, refresh_participants: bool = True) -> dict[str, Any]:
    folder = _experiment_folder(experiment_id)
    state = _read_json(_state_path(folder), {})
    result = _public_state(state)
    if refresh_participants:
        live: dict[str, Any] = {}
        for participant_id, participant in state.get("participants", {}).items():
            if participant.get("removed_utc"):
                continue
            live[participant_id] = _participant_live_view(participant)
        result["participant_live"] = live
    result["folder"] = str(folder)
    result["experiment_layer_errors"] = _read_jsonl(folder / "experiment_errors.jsonl")[-50:]
    return {"ok": True, "experiment": result}


def _require_participant(state: dict[str, Any], participant_id: str) -> dict[str, Any]:
    participant = state.get("participants", {}).get(str(participant_id))
    if not isinstance(participant, dict) or participant.get("removed_utc"):
        raise BrowserExperimentError(f"Aktiver Teilnehmer nicht gefunden: {participant_id}")
    return participant


def _require_phase(state: dict[str, Any], phase_id: str) -> dict[str, Any]:
    phase = state.get("phases", {}).get(str(phase_id))
    if not isinstance(phase, dict):
        raise BrowserExperimentError(f"Phase nicht gefunden: {phase_id}")
    return phase


def _validate_targets(state: dict[str, Any], values: Iterable[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        participant_id = str(value)
        _require_participant(state, participant_id)
        if participant_id not in result:
            result.append(participant_id)
    return result


def _latest_complete_turn(identifier: str) -> tuple[dict[str, Any], dict[str, Any]]:
    status = browser_chat_status(identifier)
    turns = [turn for turn in status.get("turns", []) if turn.get("status") == "complete"]
    if not turns:
        raise BrowserExperimentError(f"Kein vollständig erfasster Turn für {identifier}")
    return status, turns[-1]


def _refresh_participant_identity(participant: dict[str, Any]) -> dict[str, Any]:
    live = _participant_live_view(participant)
    participant["last_known_state"] = live
    participant["last_refresh_utc"] = _now()
    if live.get("available"):
        participant["chat_title"] = live.get("chat_title") or participant.get("chat_title")
        participant["tab_instance_ids"] = sorted(set(participant.get("tab_instance_ids", []) + live.get("tab_instance_ids", [])))
        participant["mcp_session_ids"] = sorted(set(participant.get("mcp_session_ids", []) + live.get("mcp_session_ids", [])))
        participant["ui_completeness_status"] = live.get("ui_completeness_status")
        participant["mcp_binding_status"] = live.get("mcp_binding_status")
        participant["last_visible_activity_utc"] = live.get("last_visible_activity_utc")
        participant["last_technical_activity_utc"] = live.get("last_technical_activity_utc")
        participant["last_turn_id"] = live.get("last_turn_id")
        participant["gap_count"] = live.get("gap_count", 0)
    return live


def apply_browser_experiment_action(
    experiment_id: str,
    action: str,
    payload: dict[str, Any] | None = None,
    *,
    source: str = "daniel_manual",
) -> dict[str, Any]:
    folder = _experiment_folder(experiment_id)
    payload = dict(payload or {})
    action = str(action or "").strip()
    if not action:
        raise BrowserExperimentError("Versuchsaktion fehlt")
    lock = _lock(folder / ".experiment.lock")
    try:
        state = _read_json(_state_path(folder), {})
        timestamp = _now()
        event_payload: dict[str, Any]

        if action == "experiment_start":
            if state.get("status") not in {"prepared", "paused"}:
                raise BrowserExperimentError(f"Versuch kann aus {state.get('status')} nicht gestartet werden")
            state["status"] = "active"
            state["started_utc"] = state.get("started_utc") or timestamp
            state["ended_utc"] = None
            event_payload = {"status": "active"}
        elif action == "experiment_pause":
            if state.get("status") != "active":
                raise BrowserExperimentError("Nur ein aktiver Versuch kann pausiert werden")
            state["status"] = "paused"
            event_payload = {"status": "paused"}
        elif action == "experiment_resume":
            if state.get("status") != "paused":
                raise BrowserExperimentError("Nur ein pausierter Versuch kann fortgesetzt werden")
            if state.get("emergency_stop", {}).get("active"):
                raise BrowserExperimentError("Not-Aus ist noch aktiv")
            state["status"] = "active"
            event_payload = {"status": "active"}
        elif action in {"experiment_end", "experiment_abort", "experiment_mark_incomplete"}:
            target = {"experiment_end": "ended", "experiment_abort": "aborted", "experiment_mark_incomplete": "incomplete"}[action]
            if state.get("status") in {"ended", "aborted"}:
                raise BrowserExperimentError("Versuch ist bereits abgeschlossen")
            active_phase_id = _active_phase_id(state)
            if active_phase_id:
                phase = state["phases"][active_phase_id]
                phase["status"] = "ended"
                phase["ended_utc"] = timestamp
                state["active_phase_id"] = None
            state["status"] = target
            state["ended_utc"] = timestamp
            event_payload = {"status": target, "active_phase_closed": active_phase_id}
        elif action == "experiment_metadata":
            if "name" in payload:
                name = str(payload.get("name") or "").strip()
                if not name:
                    raise BrowserExperimentError("Versuchsname darf nicht leer sein")
                state["name"] = name[:200]
            if "description" in payload:
                state["description"] = str(payload.get("description") or "")[:4000] or None
            event_payload = {"name": state.get("name"), "description": state.get("description")}
        elif action == "emergency_stop":
            emergency = state.setdefault("emergency_stop", {})
            emergency.update({"active": True, "activated_utc": timestamp, "released_utc": None})
            previous_status = state.get("status")
            if previous_status == "active":
                state["status"] = "paused"
            event_payload = {
                "active": True,
                "previous_experiment_status": previous_status,
                "local_queue_and_stored_data_must_be_preserved": True,
                "server_did_not_delete_or_send_any_browser_content": True,
            }
        elif action == "emergency_release":
            emergency = state.setdefault("emergency_stop", {})
            emergency.update({"active": False, "released_utc": timestamp})
            event_payload = {"active": False, "experiment_remains_paused_until_explicit_resume": True}
        elif action == "participant_add":
            identifier = str(payload.get("identifier") or "").strip()
            if not identifier:
                raise BrowserExperimentError("Chat-Identifier fehlt")
            status = browser_chat_status(identifier)
            manifest = status.get("manifest", {})
            provider_id = str(manifest.get("provider_id") or "unknown")
            conversation_id = str(manifest.get("conversation_id") or "").strip() or None
            local_conversation_id = str(manifest.get("local_conversation_id") or "").strip() or None
            identity_key = f"{provider_id}|{conversation_id or local_conversation_id}"
            existing = next((
                participant for participant in state.get("participants", {}).values()
                if participant.get("identity_key") == identity_key and not participant.get("removed_utc")
            ), None)
            if existing:
                existing["tab_instance_ids"] = sorted(set(existing.get("tab_instance_ids", []) + _tab_ids_from_status(status)))
                _refresh_participant_identity(existing)
                participant = existing
                duplicate = True
            else:
                participant_id = _new_id("participant")
                participant = {
                    "participant_id": participant_id,
                    "identity_key": identity_key,
                    "provider_id": provider_id,
                    "conversation_id": conversation_id,
                    "local_conversation_id": local_conversation_id,
                    "chat_title": manifest.get("current_title"),
                    "alias": str(payload.get("alias") or "")[:160] or None,
                    "label": str(payload.get("label") or "")[:160] or None,
                    "label_is_human_set_not_asserted_property": True,
                    "tab_instance_ids": _tab_ids_from_status(status),
                    "browser_turn_ids": [turn.get("turn_id") for turn in status.get("turns", []) if turn.get("turn_id")],
                    "mcp_session_ids": sorted({str(turn.get("mcp_session_id")) for turn in status.get("turns", []) if turn.get("mcp_session_id")}),
                    "participant_state": "active",
                    "recording_paused": False,
                    "added_utc": timestamp,
                    "removed_utc": None,
                    "ui_completeness_status": "unknown",
                    "mcp_binding_status": "not_bound",
                    "last_visible_activity_utc": manifest.get("last_event_utc"),
                    "last_technical_activity_utc": None,
                    "last_turn_id": manifest.get("last_turn_id"),
                    "local_queue_size": None,
                    "gap_count": manifest.get("gap_count", 0),
                    "last_known_state": None,
                    "last_refresh_utc": None,
                }
                _refresh_participant_identity(participant)
                state.setdefault("participants", {})[participant_id] = participant
                state.setdefault("participant_order", []).append(participant_id)
                duplicate = False
            event_payload = {
                "participant_id": participant["participant_id"],
                "identity_key": identity_key,
                "conversation_id": conversation_id,
                "tab_instance_ids": participant.get("tab_instance_ids", []),
                "duplicate_existing_participant": duplicate,
                "automatic_communication_started": False,
            }
        elif action == "participant_remove":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            participant["removed_utc"] = timestamp
            participant["recording_paused"] = True
            event_payload = {
                "participant_id": participant["participant_id"],
                "primary_events_deleted": False,
                "participant_identity_retained": True,
            }
        elif action == "participant_alias":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            participant["alias"] = str(payload.get("alias") or "")[:160] or None
            participant["label"] = str(payload.get("label") or participant.get("label") or "")[:160] or None
            event_payload = {
                "participant_id": participant["participant_id"],
                "alias": participant["alias"],
                "label": participant["label"],
                "label_is_human_set_not_asserted_property": True,
            }
        elif action == "participant_recording":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            paused = bool(payload.get("paused"))
            participant["recording_paused"] = paused
            event_payload = {"participant_id": participant["participant_id"], "recording_paused": paused}
        elif action == "participant_state":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            value = str(payload.get("state") or "")
            if value not in PARTICIPANT_STATES:
                raise BrowserExperimentError(f"Ungültiger Teilnehmerzustand: {value}")
            participant["participant_state"] = value
            event_payload = {"participant_id": participant["participant_id"], "participant_state": value}
        elif action == "participant_refresh":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            live = _refresh_participant_identity(participant)
            event_payload = {"participant_id": participant["participant_id"], "live": live}
        elif action == "participant_queue_state":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            value = payload.get("local_queue_size")
            participant["local_queue_size"] = int(value) if value is not None else None
            event_payload = {"participant_id": participant["participant_id"], "local_queue_size": participant["local_queue_size"]}
        elif action == "phase_create":
            name = str(payload.get("name") or "").strip()
            if not name:
                raise BrowserExperimentError("Phasenname darf nicht leer sein")
            phase_id = _new_id("phase")
            phase = {
                "phase_id": phase_id,
                "name": name[:200],
                "description": str(payload.get("description") or "")[:4000] or None,
                "created_utc": timestamp,
                "started_utc": None,
                "ended_utc": None,
                "order": len(state.get("phase_order", [])) + 1,
                "status": "prepared",
            }
            state.setdefault("phases", {})[phase_id] = phase
            state.setdefault("phase_order", []).append(phase_id)
            event_payload = phase
        elif action == "phase_start":
            if _active_phase_id(state):
                raise BrowserExperimentError("Es ist bereits eine Phase aktiv; zuerst ausdrücklich beenden")
            phase = _require_phase(state, str(payload.get("phase_id") or ""))
            if phase.get("status") not in {"prepared", "paused"}:
                raise BrowserExperimentError(f"Phase kann aus {phase.get('status')} nicht gestartet werden")
            phase["status"] = "active"
            phase["started_utc"] = phase.get("started_utc") or timestamp
            phase["ended_utc"] = None
            state["active_phase_id"] = phase["phase_id"]
            event_payload = {"phase_id": phase["phase_id"], "status": "active"}
        elif action == "phase_end":
            phase = _require_phase(state, str(payload.get("phase_id") or state.get("active_phase_id") or ""))
            if phase.get("status") != "active":
                raise BrowserExperimentError("Nur eine aktive Phase kann beendet werden")
            phase["status"] = "ended"
            phase["ended_utc"] = timestamp
            if state.get("active_phase_id") == phase["phase_id"]:
                state["active_phase_id"] = None
            event_payload = {"phase_id": phase["phase_id"], "status": "ended"}
        elif action == "stimulus_register":
            targets = _validate_targets(state, payload.get("target_participant_ids") or [])
            if not targets:
                raise BrowserExperimentError("Mindestens ein Zielteilnehmer ist erforderlich")
            text = str(payload.get("text") or "")
            supplied_hash = str(payload.get("text_hash") or "").strip() or None
            if not text and not supplied_hash:
                raise BrowserExperimentError("Impuls benötigt Text oder Text-Hash")
            text_hash = supplied_hash or hashlib.sha256(text.encode("utf-8")).hexdigest()
            stimulus_id = _new_id("stimulus")
            stimulus = {
                "stimulus_id": stimulus_id,
                "text_hash": text_hash,
                "text": text if bool(payload.get("store_full_text")) else None,
                "full_text_intentionally_stored": bool(payload.get("store_full_text")),
                "target_participant_ids": targets,
                "timestamp_utc": timestamp,
                "phase_id": _active_phase_id(state),
                "channel": str(payload.get("channel") or "visible_browser_message"),
                "distribution": str(payload.get("distribution") or "individual"),
                "identical_group_id": str(payload.get("identical_group_id") or "") or None,
                "visible_sent": bool(payload.get("visible_sent")),
                "technically_saved": True,
                "human_relay": bool(payload.get("human_relay")),
                "reactions": [],
            }
            state.setdefault("stimuli", {})[stimulus_id] = stimulus
            event_payload = stimulus
        elif action == "stimulus_reaction":
            stimulus = state.get("stimuli", {}).get(str(payload.get("stimulus_id") or ""))
            if not isinstance(stimulus, dict):
                raise BrowserExperimentError("Impuls nicht gefunden")
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            reaction = {
                "reaction_id": _new_id("reaction"),
                "participant_id": participant["participant_id"],
                "turn_id": str(payload.get("turn_id") or "") or None,
                "timestamp_utc": timestamp,
                "evidence": payload.get("evidence"),
            }
            stimulus.setdefault("reactions", []).append(reaction)
            event_payload = {"stimulus_id": stimulus["stimulus_id"], **reaction}
        elif action == "snapshot_seal":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            identifier = str(participant.get("conversation_id") or participant.get("local_conversation_id") or "")
            status, turn = _latest_complete_turn(identifier)
            requested_turn = str(payload.get("turn_id") or "").strip()
            if requested_turn:
                turn = next((candidate for candidate in status.get("turns", []) if candidate.get("turn_id") == requested_turn and candidate.get("status") == "complete"), None)
                if turn is None:
                    raise BrowserExperimentError("Gewünschter vollständiger Turn nicht gefunden")
            known_exposures = [
                exposure_id for exposure_id, exposure in state.get("exposures", {}).items()
                if exposure.get("target_participant_id") == participant["participant_id"]
                and _parse_time(exposure.get("available_utc"))
                and _parse_time(exposure.get("available_utc")) <= (_parse_time(timestamp) or dt.datetime.max.replace(tzinfo=dt.timezone.utc))
            ]
            material = {
                "experiment_id": state["experiment_id"],
                "participant_id": participant["participant_id"],
                "phase_id": _active_phase_id(state),
                "sealed_utc": timestamp,
                "turn_id": turn.get("turn_id"),
                "turn_correlation_id": turn.get("correlation_id"),
                "ui_completeness_status": turn.get("completeness_verdict"),
                "mcp_session_ids_known": sorted(participant.get("mcp_session_ids", [])),
                "known_exposure_ids": sorted(known_exposures),
                "last_complete_message_event_ids": turn.get("message_event_ids", []),
            }
            snapshot_id = _new_id("snapshot")
            snapshot = {
                "snapshot_id": snapshot_id,
                **material,
                "state_sha256": _sha_value(material),
                "before_proven_mcp_communication": not bool(participant.get("mcp_session_ids")),
                "before_proven_foreign_read": not any(state["exposures"][eid].get("read_utc") for eid in known_exposures),
                "technically_sealed_independent_snapshot": True,
                "global_independence_proven": False,
                "global_independence_limit": "Unsichtbare Plattformmechanismen sind nicht kontrollierbar",
            }
            state.setdefault("snapshots", {})[snapshot_id] = snapshot
            event_payload = snapshot
        elif action == "message_create":
            sender_id = str(payload.get("sender_participant_id") or "").strip() or None
            if sender_id:
                _require_participant(state, sender_id)
            recipients = _validate_targets(state, payload.get("recipient_participant_ids") or [])
            if not recipients:
                raise BrowserExperimentError("Mindestens ein Empfänger ist erforderlich")
            channel = str(payload.get("channel") or "unknown_or_unobservable")
            if channel not in KNOWN_CHANNELS:
                raise BrowserExperimentError(f"Unbekannter Kommunikationskanal: {channel}")
            message_id = str(payload.get("message_id") or "").strip() or _new_id("message")
            if message_id in state.get("messages", {}):
                raise BrowserExperimentError(f"Nachrichten-ID bereits vorhanden: {message_id}")
            content = str(payload.get("text") or "")
            message = {
                "message_id": message_id,
                "sender_participant_id": sender_id,
                "recipient_participant_ids": recipients,
                "channel": channel,
                "created_utc": timestamp,
                "phase_id": _active_phase_id(state),
                "text_hash": str(payload.get("text_hash") or "").strip() or (hashlib.sha256(content.encode("utf-8")).hexdigest() if content else None),
                "text": content if bool(payload.get("store_full_text")) else None,
                "full_text_intentionally_stored": bool(payload.get("store_full_text")),
                "resource": payload.get("resource"),
                "correlation_id": str(payload.get("correlation_id") or "").strip() or None,
                "states": {
                    "created": {"timestamp_utc": timestamp, "evidence": payload.get("evidence")},
                },
                "state_separation_rule": "states_are_never_automatically_promoted",
            }
            state.setdefault("messages", {})[message_id] = message
            event_payload = message
        elif action == "message_mark":
            message = state.get("messages", {}).get(str(payload.get("message_id") or ""))
            if not isinstance(message, dict):
                raise BrowserExperimentError("Nachricht nicht gefunden")
            value = str(payload.get("state") or "")
            if value not in MESSAGE_STATES:
                raise BrowserExperimentError(f"Ungültiger Nachrichtenstatus: {value}")
            message.setdefault("states", {})[value] = {
                "timestamp_utc": str(payload.get("timestamp_utc") or timestamp),
                "participant_id": str(payload.get("participant_id") or "") or None,
                "evidence": payload.get("evidence"),
            }
            event_payload = {"message_id": message["message_id"], "state": value, "state_record": message["states"][value]}
        elif action == "exposure_register":
            target = _require_participant(state, str(payload.get("target_participant_id") or ""))
            source_id = str(payload.get("source_participant_id") or "").strip() or None
            if source_id:
                _require_participant(state, source_id)
            resource = payload.get("resource")
            if not resource:
                raise BrowserExperimentError("Exposition benötigt eine Ressource")
            exposure_id = _new_id("exposure")
            exposure = {
                "exposure_id": exposure_id,
                "target_participant_id": target["participant_id"],
                "source_participant_id": source_id,
                "resource": resource,
                "available_utc": str(payload.get("available_utc") or timestamp),
                "read_utc": str(payload.get("read_utc") or "") or None,
                "contained_source_event_ids": list(payload.get("contained_source_event_ids") or []),
                "contained_files": list(payload.get("contained_files") or []),
                "evidence": payload.get("evidence"),
                "phase_id": _active_phase_id(state),
                "possible_reactions": list(payload.get("possible_reactions") or []),
                "availability_is_not_reading": True,
                "reading_is_not_understanding_or_use": True,
            }
            state.setdefault("exposures", {})[exposure_id] = exposure
            event_payload = exposure
        elif action == "exposure_mark_read":
            exposure = state.get("exposures", {}).get(str(payload.get("exposure_id") or ""))
            if not isinstance(exposure, dict):
                raise BrowserExperimentError("Exposition nicht gefunden")
            evidence = payload.get("evidence")
            if not evidence:
                raise BrowserExperimentError("Technisches Lesen benötigt einen Beleg")
            exposure["read_utc"] = str(payload.get("read_utc") or timestamp)
            exposure["read_evidence"] = evidence
            event_payload = {"exposure_id": exposure["exposure_id"], "read_utc": exposure["read_utc"], "evidence": evidence}
        elif action == "influence_record":
            influence_class = str(payload.get("influence_class") or "")
            if influence_class not in INFLUENCE_CLASSES:
                raise BrowserExperimentError(f"Ungültige Herkunftsklasse: {influence_class}")
            evidence = list(payload.get("evidence") or [])
            evidence_types = {str(item.get("type")) for item in evidence if isinstance(item, dict)}
            if influence_class == "direct_confirmed" and not (evidence_types & DIRECT_EVIDENCE_TYPES):
                raise BrowserExperimentError("direct_confirmed benötigt einen realen direkten Herkunftsbeleg")
            influence_id = _new_id("influence")
            influence = {
                "influence_id": influence_id,
                "source_participant_id": str(payload.get("source_participant_id") or "") or None,
                "target_participant_id": str(payload.get("target_participant_id") or "") or None,
                "source_event_ids": list(payload.get("source_event_ids") or []),
                "target_event_ids": list(payload.get("target_event_ids") or []),
                "influence_class": influence_class,
                "evidence": evidence,
                "timestamp_utc": timestamp,
                "phase_id": _active_phase_id(state),
                "human_annotation_only": bool(payload.get("human_annotation_only")),
                "causality_claimed": influence_class in {"direct_confirmed", "human_relay_confirmed"},
            }
            if influence["source_participant_id"]:
                _require_participant(state, influence["source_participant_id"])
            if influence["target_participant_id"]:
                _require_participant(state, influence["target_participant_id"])
            state.setdefault("influences", {})[influence_id] = influence
            event_payload = influence
        elif action == "annotation_add":
            annotation_id = _new_id("annotation")
            annotation = {
                "annotation_id": annotation_id,
                "human_source": "Daniel",
                "timestamp_utc": timestamp,
                "annotation_type": str(payload.get("annotation_type") or "free_note")[:160],
                "reference": payload.get("reference"),
                "text": str(payload.get("text") or "")[:10000],
                "expected_evidence": payload.get("expected_evidence"),
                "status": "open",
                "technical_evidence_class_unchanged": True,
                "primary_events_modified": False,
            }
            state.setdefault("annotations", {})[annotation_id] = annotation
            event_payload = annotation
        elif action == "annotation_status":
            annotation = state.get("annotations", {}).get(str(payload.get("annotation_id") or ""))
            if not isinstance(annotation, dict):
                raise BrowserExperimentError("Annotation nicht gefunden")
            value = str(payload.get("status") or "")
            if value not in ANNOTATION_STATUSES:
                raise BrowserExperimentError(f"Ungültiger Annotationsstatus: {value}")
            annotation["status"] = value
            annotation["resolved_utc"] = timestamp
            annotation["resolution_evidence"] = payload.get("evidence")
            event_payload = {"annotation_id": annotation["annotation_id"], "status": value, "evidence": payload.get("evidence")}
        elif action == "self_report_add":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            report_id = _new_id("self-report")
            report = {
                "self_report_id": report_id,
                "participant_id": participant["participant_id"],
                "question": str(payload.get("question") or "")[:4000],
                "answer": str(payload.get("answer") or "")[:50000],
                "question_turn_id": str(payload.get("question_turn_id") or "") or None,
                "answer_turn_id": str(payload.get("answer_turn_id") or "") or None,
                "timestamp_utc": timestamp,
                "phase_id": _active_phase_id(state),
                "truth_class": "session_self_report_not_objective_truth",
            }
            state.setdefault("self_reports", {})[report_id] = report
            event_payload = report
        elif action == "comparison_generate":
            participant = _require_participant(state, str(payload.get("participant_id") or ""))
            participant_id = participant["participant_id"]
            comparison_id = _new_id("comparison")
            comparison = {
                "comparison_id": comparison_id,
                "participant_id": participant_id,
                "generated_utc": timestamp,
                "independent_snapshots": [sid for sid, item in state.get("snapshots", {}).items() if item.get("participant_id") == participant_id],
                "received_stimuli": [sid for sid, item in state.get("stimuli", {}).items() if participant_id in item.get("target_participant_ids", [])],
                "available_exposures": [eid for eid, item in state.get("exposures", {}).items() if item.get("target_participant_id") == participant_id],
                "read_exposures": [eid for eid, item in state.get("exposures", {}).items() if item.get("target_participant_id") == participant_id and item.get("read_utc")],
                "sent_messages": [mid for mid, item in state.get("messages", {}).items() if item.get("sender_participant_id") == participant_id],
                "received_messages": [mid for mid, item in state.get("messages", {}).items() if participant_id in item.get("recipient_participant_ids", [])],
                "annotations": [aid for aid, item in state.get("annotations", {}).items() if participant_id in json.dumps(item.get("reference"), ensure_ascii=False)],
                "self_reports": [rid for rid, item in state.get("self_reports", {}).items() if item.get("participant_id") == participant_id],
                "influences": [iid for iid, item in state.get("influences", {}).items() if participant_id in {item.get("source_participant_id"), item.get("target_participant_id")}],
                "automatic_psychological_diagnosis": False,
                "technical_sequence_may_remain_undecidable": True,
            }
            comparison["comparison_sha256"] = _sha_value(comparison)
            state.setdefault("comparisons", {})[comparison_id] = comparison
            event_payload = comparison
        elif action == "control_condition_set":
            key = str(payload.get("key") or "").strip()
            if not key:
                raise BrowserExperimentError("Kontrollbedingung benötigt einen Schlüssel")
            record = {
                "key": key[:160],
                "value": payload.get("value"),
                "set_utc": timestamp,
                "human_set": True,
                "scientific_isolation_claimed": False,
            }
            state.setdefault("control_conditions", {})[key[:160]] = record
            event_payload = record
        else:
            raise BrowserExperimentError(f"Unbekannte Versuchsaktion: {action}")

        event = _event(state, action, event_payload, source=source, timestamp_utc=timestamp)
        _commit(folder, state, event)
        return {"ok": True, "action": action, "event": event, "experiment": _public_state(state)}
    except Exception as exc:
        _record_error(folder, action, exc)
        raise
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()


def _phase_for_time(state: dict[str, Any], timestamp_utc: str | None) -> str | None:
    value = _parse_time(timestamp_utc)
    if value is None:
        return None
    matches: list[tuple[int, str]] = []
    for phase_id in state.get("phase_order", []):
        phase = state.get("phases", {}).get(phase_id, {})
        start = _parse_time(phase.get("started_utc"))
        end = _parse_time(phase.get("ended_utc"))
        if start and value >= start and (end is None or value <= end):
            matches.append((int(phase.get("order") or 0), phase_id))
    return sorted(matches)[-1][1] if matches else None


def build_browser_experiment_timeline(
    experiment_id: str,
    *,
    participant_id: str | None = None,
    phase_id: str | None = None,
    source: str | None = None,
    event_type: str | None = None,
    influence_class: str | None = None,
    include_derived: bool = True,
    limit: int = 20000,
    write_projection: bool = True,
) -> dict[str, Any]:
    folder = _experiment_folder(experiment_id)
    state = _read_json(_state_path(folder), {})
    limit = max(1, min(int(limit), 50000))
    rows: list[dict[str, Any]] = []

    for sequence, event in enumerate(_read_jsonl(_events_path(folder)), start=1):
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        participant_refs = sorted({str(value) for value in [
            payload.get("participant_id"), payload.get("sender_participant_id"), payload.get("target_participant_id"), payload.get("source_participant_id")
        ] if value} | {str(value) for value in payload.get("recipient_participant_ids", []) if value} | {str(value) for value in payload.get("target_participant_ids", []) if value})
        rows.append({
            "timeline_event_id": f"experiment:{event.get('event_id') or sequence}",
            "source": "experiment_layer",
            "source_sequence": sequence,
            "source_event_id": event.get("event_id"),
            "experiment_id": state.get("experiment_id"),
            "participant_ids": participant_refs,
            "phase_id": event.get("phase_id"),
            "event_type": event.get("event_type"),
            "reported_time_utc": event.get("timestamp_utc"),
            "summary": event.get("event_type"),
            "payload": payload,
            "influence_class": payload.get("influence_class"),
            "truth_class": "manual_or_experiment_layer_record",
            "primary_source_modified": False,
        })

    participant_errors: list[dict[str, Any]] = []
    for pid in state.get("participant_order", []):
        participant = state.get("participants", {}).get(pid, {})
        if participant.get("removed_utc"):
            continue
        identifier = participant.get("conversation_id") or participant.get("local_conversation_id")
        if not identifier:
            continue
        try:
            participant_timeline = read_browser_timeline(
                str(identifier),
                include_derived=include_derived,
                limit=20000,
                refresh_projection=False,
            )
            for item in participant_timeline.get("events", []):
                copied = copy.deepcopy(item)
                copied["timeline_event_id"] = f"participant:{pid}:{item.get('timeline_event_id')}"
                copied["experiment_id"] = state.get("experiment_id")
                copied["participant_id"] = pid
                copied["participant_ids"] = [pid]
                copied["phase_id"] = _phase_for_time(state, copied.get("reported_time_utc"))
                copied["participant_alias"] = participant.get("alias")
                copied["participant_label"] = participant.get("label")
                copied["primary_source_modified"] = False
                rows.append(copied)
        except Exception as exc:
            participant_errors.append({"participant_id": pid, "identifier": identifier, "error": repr(exc)})

    def sort_key(item: dict[str, Any]) -> tuple[dt.datetime, str, int]:
        parsed = _parse_time(item.get("reported_time_utc")) or dt.datetime.max.replace(tzinfo=dt.timezone.utc)
        return parsed, str(item.get("source")), int(item.get("source_sequence") or 0)

    rows.sort(key=sort_key)
    by_second: dict[str, list[dict[str, Any]]] = {}
    for item in rows:
        parsed = _parse_time(item.get("reported_time_utc"))
        key = parsed.strftime("%Y-%m-%dT%H:%M:%SZ") if parsed else "unknown-time"
        by_second.setdefault(key, []).append(item)
    for key, group in by_second.items():
        source_kinds = {item.get("source") for item in group}
        uncertain = len(group) > 1 and len(source_kinds) > 1
        for item in group:
            item["parallel_group_id"] = key if uncertain else None
            item["cross_source_order_certainty"] = "parallel_or_uncertain" if uncertain else "not_compared"

    filtered: list[dict[str, Any]] = []
    for item in rows:
        if participant_id and participant_id not in set(item.get("participant_ids") or [item.get("participant_id")]):
            continue
        if phase_id and item.get("phase_id") != phase_id:
            continue
        if source and item.get("source") != source:
            continue
        if event_type and item.get("event_type") != event_type:
            continue
        if influence_class and item.get("influence_class") != influence_class:
            continue
        filtered.append(item)
    if len(filtered) > limit:
        filtered = filtered[-limit:]

    result = {
        "ok": True,
        "schema_version": "1.0-experiment-timeline",
        "generated_utc": _now(),
        "experiment_id": state.get("experiment_id"),
        "experiment_name": state.get("name"),
        "experiment_status": state.get("status"),
        "active_phase_id": state.get("active_phase_id"),
        "source_preservation": {
            "browser_primary_events_modified": False,
            "action_history_modified": False,
            "experiment_projection_regenerable": True,
        },
        "ordering_policy": {
            "combined_display_order": "reported timestamps for readability",
            "exact_cross_source_order_claimed": False,
            "same_second_cross_source_events": "parallel_or_uncertain",
            "time_proximity_confirms_influence": False,
        },
        "filters": {
            "participant_id": participant_id,
            "phase_id": phase_id,
            "source": source,
            "event_type": event_type,
            "influence_class": influence_class,
            "include_derived": include_derived,
            "limit": limit,
        },
        "participant_errors": participant_errors,
        "counts": {
            "returned_events": len(filtered),
            "experiment_events": sum(1 for item in filtered if item.get("source") == "experiment_layer"),
            "browser_events": sum(1 for item in filtered if item.get("source") == "browser_ui"),
            "technical_events": sum(1 for item in filtered if item.get("source") == "mcp_action_history"),
            "confirmed_links": sum(1 for item in filtered if item.get("mcp_binding_status") == "confirmed"),
            "derived_links": sum(1 for item in filtered if item.get("mcp_binding_status") == "derived"),
            "unattributed_context_possible": sum(1 for item in filtered if item.get("influence_class") == "unattributed_context_possible"),
            "gaps": sum(1 for item in filtered if item.get("gap")),
        },
        "events": filtered,
    }
    if write_projection and not any((participant_id, phase_id, source, event_type, influence_class)):
        _atomic_json(folder / "EXPERIMENT_TIMELINE.json", result)
        _atomic_bytes(folder / "EXPERIMENT_TIMELINE.md", render_browser_experiment_timeline_markdown(result).encode("utf-8") + b"\n")
    return result


def render_browser_experiment_timeline_markdown(timeline: dict[str, Any]) -> str:
    lines = [
        "# Mehrsitzungs-Versuchsraum – gemeinsame Zeitspur",
        "",
        f"Versuch: {timeline.get('experiment_name') or timeline.get('experiment_id')}",
        f"Status: {timeline.get('experiment_status')}",
        f"Erzeugt: {timeline.get('generated_utc')}",
        "",
        "## Wahrheitsgrenze",
        "",
        "Browser-, MCP- und Action-History-Ereignisse bleiben nach Quelle getrennt.",
        "Zeitnähe und ähnliche Sprache bestätigen keine Herkunft oder Kausalität.",
        "Nicht sicher sortierbare quellenübergreifende Ereignisse bleiben parallel oder zeitlich unsicher.",
        "",
        "## Ereignisse",
        "",
    ]
    for item in timeline.get("events", []):
        participants = ",".join(item.get("participant_ids") or [str(item.get("participant_id") or "")]).strip(",") or "–"
        uncertainty = " · parallel/unsicher" if item.get("cross_source_order_certainty") == "parallel_or_uncertain" else ""
        lines.append(
            f"- {item.get('reported_time_utc') or 'Zeit unbekannt'} · **{item.get('source')}** · "
            f"Teilnehmer `{participants}` · Phase `{item.get('phase_id') or '–'}` · "
            f"{item.get('summary') or item.get('event_type')}{uncertainty}"
        )
    if timeline.get("participant_errors"):
        lines.extend(["", "## Offene Projektionsfehler", ""])
        for error in timeline["participant_errors"]:
            lines.append(f"- `{error.get('participant_id')}`: {error.get('error')}")
    return "\n".join(lines)


def _copy_if_exists(source: Path, target: Path) -> dict[str, Any] | None:
    if not source.exists() or not source.is_file():
        return None
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    shutil.copy2(source, target)
    os.chmod(target, 0o600)
    return {"source": str(source), "export_path": str(target), "sha256": _sha_file(target), "bytes": target.stat().st_size}


def export_browser_experiment(experiment_id: str) -> dict[str, Any]:
    folder = _experiment_folder(experiment_id)
    lock = _lock(folder / ".experiment.lock")
    try:
        state = _read_json(_state_path(folder), {})
        timeline = build_browser_experiment_timeline(experiment_id, include_derived=True, limit=50000, write_projection=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        export_root = folder / "exports" / stamp
        export_root.mkdir(parents=True, exist_ok=False, mode=0o700)
        copied: list[dict[str, Any]] = []

        for source_name, target_name in [
            ("EXPERIMENT.json", "EXPERIMENT.json"),
            ("experiment_events.jsonl", "EXPERIMENT_EVENTS.jsonl"),
            ("EXPERIMENT_TIMELINE.json", "EXPERIMENT_TIMELINE.json"),
            ("EXPERIMENT_TIMELINE.md", "EXPERIMENT_TIMELINE.md"),
            ("experiment_errors.jsonl", "EXPERIMENT_ERRORS.jsonl"),
        ]:
            record = _copy_if_exists(folder / source_name, export_root / target_name)
            if record:
                copied.append(record)

        action_rows: list[dict[str, Any]] = []
        source_references: list[dict[str, Any]] = []
        for participant_id in state.get("participant_order", []):
            participant = state.get("participants", {}).get(participant_id, {})
            if participant.get("removed_utc"):
                continue
            identifier = participant.get("conversation_id") or participant.get("local_conversation_id")
            if not identifier:
                continue
            try:
                status = browser_chat_status(str(identifier))
                source_folder = Path(status["folder"])
                participant_root = export_root / "participants" / _safe_component(participant_id)
                _atomic_json(participant_root / "PARTICIPANT.json", participant)
                copied.append({
                    "source": "experiment_state.participant",
                    "export_path": str(participant_root / "PARTICIPANT.json"),
                    "sha256": _sha_file(participant_root / "PARTICIPANT.json"),
                    "bytes": (participant_root / "PARTICIPANT.json").stat().st_size,
                })
                for source_name in [
                    "MANIFEST.json",
                    "visible_stream.jsonl",
                    "messages.jsonl",
                    "capture_gaps.jsonl",
                    "B_TIMELINE.json",
                    "B_ZEITSPUR.md",
                ]:
                    record = _copy_if_exists(source_folder / source_name, participant_root / source_name)
                    if record:
                        copied.append(record)
                participant_timeline = read_browser_timeline(str(identifier), include_derived=True, limit=50000, refresh_projection=False)
                action_rows.extend([
                    row for row in participant_timeline.get("events", [])
                    if row.get("source") == "mcp_action_history"
                ])
                source_references.append({
                    "participant_id": participant_id,
                    "provider_id": participant.get("provider_id"),
                    "conversation_id": participant.get("conversation_id"),
                    "local_conversation_id": participant.get("local_conversation_id"),
                    "source_folder": str(source_folder),
                    "mcp_session_ids": participant.get("mcp_session_ids", []),
                })
            except Exception as exc:
                source_references.append({"participant_id": participant_id, "error": repr(exc)})

        unique_actions: dict[str, dict[str, Any]] = {}
        for row in action_rows:
            key = str(row.get("source_event_id") or row.get("timeline_event_id"))
            unique_actions[key] = row
        action_path = export_root / "MCP_ACTIONS.jsonl"
        for row in unique_actions.values():
            _append_jsonl(action_path, row)
        if action_path.exists():
            copied.append({"source": "filtered_action_history_projection", "export_path": str(action_path), "sha256": _sha_file(action_path), "bytes": action_path.stat().st_size})

        _atomic_json(export_root / "SOURCE_REFERENCES.json", source_references)
        copied.append({"source": "generated_source_references", "export_path": str(export_root / "SOURCE_REFERENCES.json"), "sha256": _sha_file(export_root / "SOURCE_REFERENCES.json"), "bytes": (export_root / "SOURCE_REFERENCES.json").stat().st_size})

        markdown_result = build_human_readable_export(export_root, write=True)

        manifest = {
            "schema_version": "1.0-experiment-export",
            "experiment_id": state.get("experiment_id"),
            "generated_utc": _now(),
            "software_versions": state.get("software_versions"),
            "primary_sources_replaced": False,
            "summaries_replace_raw_events": False,
            "automatic_communication_present": False,
            "files": [],
            "human_readable_markdown": {
                "required_files": list(HUMAN_MARKDOWN_FILES),
                "reproduction_file": "MARKDOWN_REPRODUKTION.json",
                "quality": markdown_result.get("quality"),
                "same_experiment_id": markdown_result.get("experiment_id") == state.get("experiment_id"),
                "deterministic_from_primary_export_files": True,
                "important_events_omitted_intentionally": False,
                "conversation_exports": markdown_result.get("conversation_exports"),
                "pure_conversation_contains_technical_metadata": False,
                "combined_parallel_order_invented": False,
            },
            "counts": {
                "participants": sum(1 for p in state.get("participants", {}).values() if not p.get("removed_utc")),
                "phases": len(state.get("phases", {})),
                "stimuli": len(state.get("stimuli", {})),
                "snapshots": len(state.get("snapshots", {})),
                "messages": len(state.get("messages", {})),
                "exposures": len(state.get("exposures", {})),
                "influences": len(state.get("influences", {})),
                "annotations": len(state.get("annotations", {})),
                "self_reports": len(state.get("self_reports", {})),
                "timeline_events": timeline.get("counts", {}).get("returned_events", 0),
            },
        }
        for path in sorted(export_root.rglob("*")):
            if path.is_file() and path.name not in {"MANIFEST.json", "HASHES.sha256"}:
                manifest["files"].append({
                    "path": str(path.relative_to(export_root)),
                    "sha256": _sha_file(path),
                    "bytes": path.stat().st_size,
                })
        _atomic_json(export_root / "MANIFEST.json", manifest)
        hashes = [f"{item['sha256']}  {item['path']}" for item in manifest["files"]]
        hashes.append(f"{_sha_file(export_root / 'MANIFEST.json')}  MANIFEST.json")
        _atomic_bytes(export_root / "HASHES.sha256", ("\n".join(hashes) + "\n").encode("utf-8"))

        archive = folder / "exports" / f"{_safe_component(state.get('name') or experiment_id)}__{stamp}.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as zip_handle:
            for path in sorted(export_root.rglob("*")):
                if path.is_file():
                    zip_handle.write(path, arcname=str(Path(export_root.name) / path.relative_to(export_root)))
        os.chmod(archive, 0o600)

        export_event = _event(state, "experiment_exported", {
            "export_folder": str(export_root),
            "archive": str(archive),
            "archive_sha256": _sha_file(archive),
            "file_count": len(manifest["files"]) + 2,
            "primary_sources_modified": False,
        }, source="explicit_export_action")
        _commit(folder, state, export_event)
        return {
            "ok": True,
            "experiment_id": state.get("experiment_id"),
            "export_folder": str(export_root),
            "archive": str(archive),
            "archive_sha256": _sha_file(archive),
            "manifest": manifest,
            "event": export_event,
        }
    except Exception as exc:
        _record_error(folder, "export", exc)
        raise
    finally:
        fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
        lock.close()
