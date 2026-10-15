from __future__ import annotations

import base64
import csv
import datetime as dt
import fcntl
import hashlib
import html
import io
import json
import os
import re
import tempfile
import uuid
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from .browser_experiment_conversation import canonical_conversation_messages, render_conversation_exact
from .browser_timeline import build_browser_timeline, write_browser_timeline_projection

STORE_ROOT = Path(os.environ.get(
    "FLEXTRAWURST_UI_VISIBLE_STORE_ROOT",
    "/root/werkraum/_gpt/ui_visible_conversations",
))
INDEX_PATH = STORE_ROOT / "BROWSER_CONVERSATIONS_INDEX.json"
INDEX_LOCK = STORE_ROOT / ".browser-conversations-index.lock"
IDENTITY_CONFLICTS_PATH = STORE_ROOT / "IDENTITY_CONFLICTS.jsonl"
COLLECTION_ARTIFACT_MANIFEST_ROOT = STORE_ROOT / "collection_artifact_manifests"
BERLIN = ZoneInfo("Europe/Berlin")
SAFE = re.compile(r"[^A-Za-z0-9ÄÖÜäöüß._-]+")
TURN_CLASSES = {
    "browser_only",
    "browser_with_mcp",
    "mcp_link_unknown",
    "capture_incomplete",
}
MESSAGE_TYPES = {"message_final", "user_message_final", "assistant_message_final", "historical_import_message"}
GAP_TYPES = {"capture_gap", "tab_discarded", "page_reload", "capture_error"}
SURROGATE = re.compile(r"[\ud800-\udfff]")


def _human_provider_label(provider_id: Any) -> str:
    """Use the visible provider name, never the generic Assistant role."""
    value = str(provider_id or "").strip()
    return "ChatGPT" if re.search(r"chatgpt|openai", value, re.IGNORECASE) else "AI-Strom"


class BrowserCaptureError(RuntimeError):
    pass


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _unicode_safe(value: Any) -> Any:
    """Replace invalid lone UTF-16 surrogates without rejecting the whole event."""
    if isinstance(value, str):
        return SURROGATE.sub("\ufffd", value)
    if isinstance(value, list):
        return [_unicode_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_unicode_safe(item) for item in value]
    if isinstance(value, dict):
        return {
            _unicode_safe(key) if isinstance(key, str) else key: _unicode_safe(item)
            for key, item in value.items()
        }
    return value


def _berlin_date() -> str:
    return dt.datetime.now(BERLIN).date().isoformat()


def _sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _safe_component(value: str, fallback: str = "CHAT") -> str:
    value = SAFE.sub("-", str(value or "").strip()).strip("-._")
    value = re.sub(r"-+", "-", value)
    return (value[:96] or fallback)


def _short_id(value: str) -> str:
    alnum = re.sub(r"[^A-Za-z0-9]", "", value or "")
    return (alnum[:12] or _sha(value or str(uuid.uuid4()))[:12]).lower()


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except json.JSONDecodeError as exc:
        raise BrowserCaptureError(f"Ungültiges JSON in {path}: {exc}") from exc


def _atomic_json(path: Path, value: Any, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(_unicode_safe(value), ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
        os.chmod(path, mode)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def _atomic_text(path: Path, value: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(str(_unicode_safe(value)))
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
        os.chmod(path, mode)
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


def _lock(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    handle = path.open("a+", encoding="utf-8")
    os.chmod(path, 0o600)
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
    return handle


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(_unicode_safe(row), ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.chmod(path, 0o600)


def _read_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise BrowserCaptureError(f"Ungültige JSONL-Zeile {number} in {path}: {exc}") from exc
            if isinstance(item, dict):
                rows.append(item)
    return rows[-limit:] if limit else rows


def _collection_artifact_manifest_path(identifier: str) -> Path:
    clean = str(identifier or "").strip()
    if not clean or len(clean) > 160:
        raise BrowserCaptureError("Seitensammlungskennung fehlt oder ist zu lang")
    folder_name = f"{_safe_component(clean, 'collection')}-{_sha(clean)[:12]}"
    return COLLECTION_ARTIFACT_MANIFEST_ROOT / folder_name / "ARTIFACT_MANIFESTS.jsonl"


def _validate_collection_artifact_manifest(artifact: Any) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        raise BrowserCaptureError("Artefaktmanifest muss ein JSON-Objekt sein")
    if any(key in artifact for key in ("content_base64", "data_url", "raw_bytes")):
        raise BrowserCaptureError("Artefaktmanifest darf keine Rohbytes oder Data-URLs enthalten")
    candidate = _unicode_safe(artifact)
    artifact_id = str(candidate.get("artifact_id") or "").strip()
    if not artifact_id or len(artifact_id) > 180:
        raise BrowserCaptureError("Artefaktmanifest ohne gültige artifact_id")
    schema_version = str(candidate.get("schema_version") or "").strip()
    if not schema_version or len(schema_version) > 80:
        raise BrowserCaptureError("Artefaktmanifest ohne gültige schema_version")
    if "bytes" in candidate:
        try:
            byte_count = int(candidate["bytes"])
        except (TypeError, ValueError) as exc:
            raise BrowserCaptureError("Artefaktmanifest bytes ist ungültig") from exc
        if byte_count < 0 or byte_count > 512 * 1024 * 1024:
            raise BrowserCaptureError("Artefaktmanifest bytes liegt außerhalb der Grenze")
        candidate["bytes"] = byte_count
    if candidate.get("sha256") is not None and not re.fullmatch(r"[0-9a-fA-F]{64}", str(candidate["sha256"])):
        raise BrowserCaptureError("Artefaktmanifest sha256 ist kein SHA-256")
    serialized = json.dumps(candidate, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if len(serialized.encode("utf-8")) > 256 * 1024:
        raise BrowserCaptureError("Artefaktmanifest ist größer als 256 KiB")
    return candidate


def record_collection_artifact_manifest(identifier: str, artifact: Any) -> dict[str, Any]:
    """Persist metadata only; generated export bytes remain in the browser/local store."""
    path = _collection_artifact_manifest_path(identifier)
    candidate = _validate_collection_artifact_manifest(artifact)
    collection_id = str(identifier or "").strip()
    with _lock(path.with_suffix(".lock")):
        rows = _read_jsonl(path)
        for row in rows:
            existing = row.get("artifact") if isinstance(row.get("artifact"), dict) else {}
            if existing.get("artifact_id") != candidate["artifact_id"]:
                continue
            existing_fingerprint = (existing.get("sha256"), existing.get("bytes"), existing.get("format"))
            candidate_fingerprint = (candidate.get("sha256"), candidate.get("bytes"), candidate.get("format"))
            if existing_fingerprint != candidate_fingerprint:
                raise BrowserCaptureError("Artefaktmanifest-Konflikt: gleiche artifact_id mit anderem Fingerabdruck")
            return {
                "ok": True,
                "status": "already_present",
                "collection_id": collection_id,
                "artifact": existing,
                "artifacts": [item.get("artifact") for item in rows if isinstance(item.get("artifact"), dict)][-100:],
                "server_storage_path": str(path),
            }
        stored = {"collection_id": collection_id, "stored_utc": _now(), "artifact": candidate}
        _append_jsonl(path, stored)
        rows.append(stored)
        if len(rows) > 100:
            _atomic_text(path, "".join(json.dumps(_unicode_safe(row), ensure_ascii=False, sort_keys=True) + "\n" for row in rows[-100:]))
        artifacts = [item.get("artifact") for item in rows if isinstance(item.get("artifact"), dict)][-100:]
    return {
        "ok": True,
        "status": "persisted",
        "collection_id": collection_id,
        "artifact": candidate,
        "artifacts": artifacts,
        "server_storage_path": str(path),
    }


def list_collection_artifact_manifests(identifier: str, limit: int = 100) -> dict[str, Any]:
    path = _collection_artifact_manifest_path(identifier)
    rows = _read_jsonl(path, limit=max(1, min(int(limit), 100)))
    return {
        "ok": True,
        "status": "read_back",
        "collection_id": str(identifier or "").strip(),
        "artifacts": [item.get("artifact") for item in rows if isinstance(item.get("artifact"), dict)],
        "server_storage_path": str(path),
    }


def _contains_event(path: Path, event_id: str) -> bool:
    if not path.exists():
        return False
    needle = f'"event_id": "{event_id}"'
    with path.open("r", encoding="utf-8") as handle:
        return any(needle in line for line in handle)


def _human_field_label(key: str) -> str:
    labels = {
        "event_type": "Ereignis",
        "timestamp_utc": "Gemeldete Zeit (UTC)",
        "recorded_utc": "Gespeichert (UTC)",
        "turn_id": "Turn",
        "role": "Rolle",
        "content": "Sichtbarer Text",
        "capture_kind": "Aufnahmeart",
        "classification": "Klassifikation",
        "mcp_binding_status": "MCP-Bindung",
        "message_id": "Nachrichten-ID",
        "event_id": "Ereignis-ID",
        "marker": "Marker",
        "markers": "Marker",
        "reason": "Grund",
        "details": "Details",
        "completeness": "Vollständigkeit",
    }
    return labels.get(key, key.replace("_", " ").capitalize())


def _append_human_value(lines: list[str], label: str, value: Any, indent: str = "") -> None:
    if isinstance(value, dict):
        lines.append(f"{indent}- **{label}:**")
        if not value:
            lines.append(f"{indent}  - –")
        for key, nested in value.items():
            _append_human_value(lines, _human_field_label(str(key)), nested, indent + "  ")
        return
    if isinstance(value, list):
        lines.append(f"{indent}- **{label}:**")
        if not value:
            lines.append(f"{indent}  - –")
        for index, nested in enumerate(value, start=1):
            _append_human_value(lines, f"Eintrag {index}", nested, indent + "  ")
        return
    if isinstance(value, str) and "\n" in value:
        lines.append(f"{indent}- **{label}:**")
        lines.extend(f"{indent}  > {line}" if line else f"{indent}  >" for line in value.splitlines())
        return
    rendered = "–" if value is None or value == "" else str(value)
    lines.append(f"{indent}- **{label}:** {rendered}")


_HUMAN_EVENT_LABELS = {
    "turn_start": "Aufnahme eines neuen Gesprächszugs begonnen",
    "turn_complete": "Gesprächszug vollständig aufgezeichnet",
    "turn_incomplete": "Gesprächszug unvollständig aufgezeichnet",
    "live_follow_paused": "Live-Follow pausiert",
    "live_follow_resumed": "Live-Follow fortgesetzt",
    "live_follow_changed": "Live-Follow-Status geändert",
    "historical_import_start": "Aufnahme eines bestehenden Chats begonnen",
    "historical_import_finish": "Aufnahme eines bestehenden Chats abgeschlossen",
    "alias_set": "Chat-Alias gespeichert",
}

_HUMAN_EVENT_OMISSIONS = {
    "visible_update",
    "chat_seen",
    "message_final",
    "user_message_final",
    "assistant_message_final",
    "historical_import_message",
}


def _human_event_lines(event: dict[str, Any], *, stored_message_count_fallback: int | None = None) -> list[str]:
    """Render only meaningful capture changes, never raw DOM snapshots."""
    event_type = str(event.get("event_type") or "")
    if event_type in _HUMAN_EVENT_OMISSIONS:
        return []
    has_marker = bool(event.get("marker") or event.get("markers"))
    has_gap = "gap" in event_type or str(event.get("classification") or "") == "capture_incomplete"
    label = _HUMAN_EVENT_LABELS.get(event_type)
    if not label and not has_marker and not has_gap:
        return []
    if not label:
        label = "Aufnahmelücke erkannt" if has_gap else "Marker erkannt"

    when = event.get("timestamp_utc") or event.get("recorded_utc") or "Zeit unbekannt"
    lines = [f"- **{when}** — {label}."]
    markers = event.get("markers") or event.get("marker")
    if markers:
        if isinstance(markers, list):
            marker_text = "; ".join(str(item) for item in markers if str(item).strip())
        else:
            marker_text = str(markers)
        if marker_text:
            lines.append(f"  - Marker: {marker_text}")
    reason = event.get("reason")
    if reason:
        lines.append(f"  - Hinweis: {str(reason).replace('_', ' ')}")
    if event_type == "historical_import_finish":
        if event.get("complete") is not None:
            lines.append(f"  - Vollständig: {'ja' if event.get('complete') else 'nein'}")
        if event.get("verified") is not None:
            lines.append(f"  - Sichtbar geprüft: {'ja' if event.get('verified') else 'nein'}")
        counter_labels = (
            ("Sichtungen gesamt", "observed_count"),
            ("Sichtungen Daniel/Input", "observed_input_count"),
            ("Sichtungen ChatGPT/AI-Strom Output", "observed_output_count"),
            ("Beiträge gesamt", "recognized_count"),
            ("Beiträge Daniel/Input", "input_count"),
            ("Beiträge ChatGPT/AI-Strom Output", "output_count"),
            ("Neu an VPS gesichert", "new_saved_count"),
        )
        for label_text, field in counter_labels:
            if field not in event:
                continue
            value = event.get(field)
            if field == "new_saved_count" and not value and stored_message_count_fallback is not None:
                value = stored_message_count_fallback
            lines.append(f"  - {label_text}: {value}")
    return lines


def _refresh_human_chat_projections(folder: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Schreibt lesbare Projektionen ausschließlich aus den unveränderten Browser-Primärdaten."""
    messages_path = folder / "messages.jsonl"
    stream_path = folder / "visible_stream.jsonl"
    gaps_path = folder / "capture_gaps.jsonl"
    transcript_path = folder / "1zu1.md"
    enriched_path = folder / "1zu1+events+marker.md"

    source_messages = _read_jsonl(messages_path)
    messages, selection = canonical_conversation_messages(source_messages)
    speaker_label = _human_provider_label(manifest.get("provider_id"))
    transcript = render_conversation_exact(messages, speaker_label)
    _atomic_text(transcript_path, transcript)

    lines = [
        "# 1:1 + Ereignisse + Marker",
        "",
        f"Gespräch: {manifest.get('alias') or manifest.get('current_title') or 'Unbenannt'}",
        f"Conversation-ID: {manifest.get('conversation_id') or 'noch nicht vergeben'}",
        f"Erzeugt: {_now()}",
        "",
        "## Wahrheitsgrenze",
        "",
        "Dieses Dokument ist eine lesbare Projektion. Gespräch und Ereignisse stammen ausschließlich aus den danebenliegenden Browser-Primärdateien; fehlende oder unsichere Stellen werden als solche angezeigt und nicht ergänzt.",
        "",
        "## 1:1 Gespräch",
        "",
        transcript.rstrip() or "_Noch kein sichtbarer Nutzer- oder AI-Strom-Text gespeichert._",
        "",
        "## Aufnahmeumfang",
        "",
    ]
    lines.append(f"- Sichtbar gespeicherte Gesprächsbeiträge: {len(messages)}")
    if selection.get("historical_import_present"):
        lines.append("- Enthält einen als historisch gekennzeichneten Import.")

    lines.extend(["", "## Zeitliche Ereignisse und Marker", ""])
    stream = _read_jsonl(stream_path)
    last_import_id = str(manifest.get("last_import_id") or "").strip()
    import_record = (manifest.get("historical_imports") or {}).get(last_import_id, {})
    stored_message_count = import_record.get("stored_message_count")
    meaningful_event_lines = [
        line
        for event in stream
        for line in _human_event_lines(
            event,
            stored_message_count_fallback=(
                int(stored_message_count) if stored_message_count is not None else None
            ),
        )
    ]
    if meaningful_event_lines:
        lines.extend(meaningful_event_lines)
    else:
        lines.append("_Keine bedeutungsvollen Ereignisse oder Marker gespeichert; reine Sichtbarkeits-Schnappschüsse werden bewusst nicht gezeigt._")

    lines.extend(["## Erkannte Lücken", ""])
    gaps = _read_jsonl(gaps_path)
    if not gaps:
        lines.append("_Keine protokollierten Aufnahmelücken._")
    for index, gap in enumerate(gaps, start=1):
        when = gap.get("timestamp_utc") or gap.get("recorded_utc") or "Zeit unbekannt"
        reason = gap.get("reason") or gap.get("message") or "ohne näheren Grund"
        lines.append(f"- **{when}** — Aufnahmelücke: {str(reason).replace('_', ' ')}.")

    lines.extend([
        "## Herkunft",
        "",
        f"Die Gesprächszeilen stammen aus bestätigten Nutzer- und {speaker_label}-Beiträgen. Die Zeitspur enthält nur verständliche Änderungen und Marker; technische DOM-Schnappschüsse bleiben in den Primärdaten und erscheinen hier nicht.",
        "",
    ])
    _atomic_text(enriched_path, "\n".join(lines))
    return {
        "available": True,
        "generated_utc": _now(),
        "transcript_path": str(transcript_path),
        "enriched_path": str(enriched_path),
        "selected_message_count": len(messages),
        "visible_event_count": len(stream),
        "gap_count": len(gaps),
        "error": None,
    }


def _refresh_human_chat_projections_safely(folder: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    try:
        summary = _refresh_human_chat_projections(folder, manifest)
    except Exception as exc:
        summary = {
            "available": False,
            "generated_utc": _now(),
            "transcript_path": str(folder / "1zu1.md"),
            "enriched_path": str(folder / "1zu1+events+marker.md"),
            "error": repr(exc),
        }
        _append_jsonl(folder / "HUMAN_DOCUMENT_PROJECTION_ERRORS.jsonl", {
            "timestamp_utc": _now(),
            "error": repr(exc),
            "projection": "human_chat_documents",
            "primary_sources_preserved": True,
        })
    manifest["human_documents"] = summary
    paths = manifest.setdefault("paths", {})
    paths["transcript_1zu1"] = str(folder / "1zu1.md")
    paths["transcript_1zu1_with_events"] = str(folder / "1zu1+events+marker.md")
    paths["human_document_projection_errors"] = str(folder / "HUMAN_DOCUMENT_PROJECTION_ERRORS.jsonl")
    return summary


def _new_index() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "updated_utc": _now(),
        "conversation_ids": {},
        "local_ids": {},
        "aliases": {},
        "folders": {},
        "historical_imports": {},
        "identity_conflicts": [],
    }


def _manifest_path(folder: Path) -> Path:
    return folder / "MANIFEST.json"


def _refresh_timeline_projection(folder: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Regeneriert B fehlertolerant, ohne Browser- oder Action-History-Primärquellen zu verändern."""
    try:
        summary = write_browser_timeline_projection(folder, manifest)
    except Exception as exc:
        summary = {
            "available": False,
            "generated_utc": _now(),
            "machine_path": str(folder / "B_TIMELINE.json"),
            "human_path": str(folder / "B_ZEITSPUR.md"),
            "event_count": 0,
            "confirmed_link_count": 0,
            "derived_link_count": 0,
            "error": repr(exc),
        }
        _append_jsonl(folder / "B_PROJECTION_ERRORS.jsonl", {
            "timestamp_utc": _now(),
            "error": repr(exc),
            "projection": "B_shared_timeline",
            "primary_sources_preserved": True,
        })
    manifest["b_timeline"] = summary
    paths = manifest.setdefault("paths", {})
    paths["b_timeline_machine"] = str(folder / "B_TIMELINE.json")
    paths["b_timeline_human"] = str(folder / "B_ZEITSPUR.md")
    paths["b_projection_errors"] = str(folder / "B_PROJECTION_ERRORS.jsonl")
    return summary


def _new_manifest(folder_name: str, title: str, conversation_id: str | None, local_id: str | None) -> dict[str, Any]:
    now = _now()
    return {
        "schema_version": "2.1-browser-capture-b-timeline",
        "folder_name": folder_name,
        "provider_id": None,
        "conversation_id": conversation_id,
        "local_conversation_ids": [local_id] if local_id else [],
        "short_conversation_id": _short_id(conversation_id or local_id or folder_name),
        "alias": None,
        "current_title": title,
        "title_history": [{"title": title, "first_seen_utc": now}],
        "capture_started_utc": now,
        "updated_utc": now,
        "last_event_utc": None,
        "last_complete_turn_id": None,
        "last_turn_id": None,
        "turn_count": 0,
        "complete_turn_count": 0,
        "gap_count": 0,
        "message_count": 0,
        "visible_event_count": 0,
        "turns": {},
        "sequence_heads": {},
        "mcp_sessions": [],
        "action_history_event_ids": [],
        "identity_conflicts": [],
        "b_timeline": {
            "available": False,
            "generated_utc": None,
            "machine_path": str(STORE_ROOT / folder_name / "B_TIMELINE.json"),
            "human_path": str(STORE_ROOT / folder_name / "B_ZEITSPUR.md"),
            "event_count": 0,
            "confirmed_link_count": 0,
            "derived_link_count": 0,
            "error": None,
        },
        "human_documents": {
            "available": False,
            "generated_utc": None,
            "transcript_path": str(STORE_ROOT / folder_name / "1zu1.md"),
            "enriched_path": str(STORE_ROOT / folder_name / "1zu1+events+marker.md"),
            "error": None,
        },
        "historical_imports": {},
        "last_import_id": None,
        "last_import_status": None,
        "page_snapshots": {},
        "last_snapshot_id": None,
        "paths": {
            "manifest": str(STORE_ROOT / folder_name / "MANIFEST.json"),
            "messages": str(STORE_ROOT / folder_name / "messages.jsonl"),
            "visible_stream": str(STORE_ROOT / folder_name / "visible_stream.jsonl"),
            "turns": str(STORE_ROOT / folder_name / "turns"),
            "capture_gaps": str(STORE_ROOT / folder_name / "capture_gaps.jsonl"),
            "b_timeline_machine": str(STORE_ROOT / folder_name / "B_TIMELINE.json"),
            "b_timeline_human": str(STORE_ROOT / folder_name / "B_ZEITSPUR.md"),
            "b_projection_errors": str(STORE_ROOT / folder_name / "B_PROJECTION_ERRORS.jsonl"),
            "transcript_1zu1": str(STORE_ROOT / folder_name / "1zu1.md"),
            "transcript_1zu1_with_events": str(STORE_ROOT / folder_name / "1zu1+events+marker.md"),
            "human_document_projection_errors": str(STORE_ROOT / folder_name / "HUMAN_DOCUMENT_PROJECTION_ERRORS.jsonl"),
        },
    }


def _update_title(manifest: dict[str, Any], title: str) -> None:
    title = str(title or "Unbenannter Chat").strip()[:300]
    if not title:
        title = "Unbenannter Chat"
    if manifest.get("current_title") != title:
        manifest["current_title"] = title
        history = manifest.setdefault("title_history", [])
        if not any(item.get("title") == title for item in history if isinstance(item, dict)):
            history.append({"title": title, "first_seen_utc": _now()})


def _indexed_manifest(folder_name: str | None) -> dict[str, Any] | None:
    if not folder_name:
        return None
    path = _manifest_path(STORE_ROOT / folder_name)
    if not path.exists():
        return None
    value = _read_json(path, {})
    return value if isinstance(value, dict) else None


def _manifest_matches_identity(
    manifest: dict[str, Any] | None,
    *,
    conversation_id: str | None,
    local_conversation_id: str | None,
) -> bool:
    if not isinstance(manifest, dict):
        return False
    existing_cid = str(manifest.get("conversation_id") or "").strip() or None
    local_ids = {str(value) for value in manifest.get("local_conversation_ids", []) if str(value).strip()}
    if conversation_id:
        if existing_cid:
            return existing_cid == conversation_id
        return bool(local_conversation_id and local_conversation_id in local_ids)
    return bool(local_conversation_id and local_conversation_id in local_ids)


def _record_identity_conflict(index: dict[str, Any], conflict: dict[str, Any]) -> dict[str, Any]:
    stable = {
        key: conflict.get(key)
        for key in sorted(conflict)
        if key not in {"timestamp_utc", "conflict_id"}
    }
    conflict_id = f"identity-conflict-{_sha(json.dumps(stable, ensure_ascii=False, sort_keys=True))[:24]}"
    row = {
        "schema_version": "1.0-browser-identity-conflict",
        "conflict_id": conflict_id,
        "timestamp_utc": _now(),
        **stable,
        "primary_events_modified": False,
        "automatic_merge_performed": False,
    }
    known = index.setdefault("identity_conflicts", [])
    if conflict_id not in known:
        known.append(conflict_id)
        _append_jsonl(IDENTITY_CONFLICTS_PATH, row)
    return row


def _new_folder_name(clean_title: str, identity: str) -> str:
    # Lesbarer Prefix plus Hash: gemeinsame ID-Anfänge dürfen niemals dieselbe Ordneridentität erzeugen.
    identity_suffix = f"{_short_id(identity)}-{_sha(identity)[:10]}"
    base = f"{_berlin_date()}__{_safe_component(clean_title, 'Unbenannter-Chat')}__{identity_suffix}"
    candidate_name = base
    suffix = 2
    while True:
        candidate = STORE_ROOT / candidate_name
        if not candidate.exists():
            return candidate_name
        manifest = _indexed_manifest(candidate_name)
        existing_identity = str((manifest or {}).get("conversation_id") or "").strip()
        existing_locals = {str(value) for value in (manifest or {}).get("local_conversation_ids", []) if str(value).strip()}
        if existing_identity == identity or (not existing_identity and identity in existing_locals):
            return candidate_name
        candidate_name = f"{base}-{suffix}"
        suffix += 1


def resolve_conversation(
    *,
    conversation_id: str | None,
    local_conversation_id: str | None,
    title: str | None,
) -> tuple[Path, dict[str, Any], dict[str, Any]]:
    STORE_ROOT.mkdir(parents=True, exist_ok=True, mode=0o700)
    cid = str(conversation_id or "").strip() or None
    lid = str(local_conversation_id or "").strip() or None
    if not cid and not lid:
        raise BrowserCaptureError("conversation_id oder local_conversation_id ist erforderlich")
    clean_title = str(title or "Unbenannter Chat").strip()[:300] or "Unbenannter Chat"

    lock_handle = _lock(INDEX_LOCK)
    try:
        index = _read_json(INDEX_PATH, _new_index())
        by_cid = index.setdefault("conversation_ids", {})
        by_lid = index.setdefault("local_ids", {})
        index.setdefault("identity_conflicts", [])
        cid_folder = by_cid.get(cid) if cid else None
        local_folder = by_lid.get(lid) if lid else None
        folder_name: str | None = None
        pending_conflicts: list[dict[str, Any]] = []

        # Rang 1: stabile Conversation-ID. Ein veralteter oder korrupter Indexeintrag darf sie nicht umdeuten.
        if cid_folder:
            cid_manifest = _indexed_manifest(cid_folder)
            if _manifest_matches_identity(cid_manifest, conversation_id=cid, local_conversation_id=lid):
                folder_name = cid_folder
            else:
                pending_conflicts.append({
                    "reason": "conversation_id_index_points_to_different_manifest_identity",
                    "conversation_id": cid,
                    "local_conversation_id": lid,
                    "indexed_folder": cid_folder,
                    "indexed_manifest_conversation_id": (cid_manifest or {}).get("conversation_id"),
                })

        # Rang 2: Local-ID darf nur einen local-only Körper zur stabilen CID befördern, nie zwei stabile Chats verschmelzen.
        if not folder_name and local_folder:
            local_manifest = _indexed_manifest(local_folder)
            local_manifest_cid = str((local_manifest or {}).get("conversation_id") or "").strip() or None
            if not cid:
                folder_name = local_folder
            elif not local_manifest_cid or local_manifest_cid == cid:
                folder_name = local_folder
            else:
                pending_conflicts.append({
                    "reason": "shared_local_id_across_distinct_stable_conversations",
                    "conversation_id": cid,
                    "local_conversation_id": lid,
                    "local_index_folder": local_folder,
                    "local_index_manifest_conversation_id": local_manifest_cid,
                })

        if not folder_name:
            identity = cid or lid or str(uuid.uuid4())
            folder_name = _new_folder_name(clean_title, identity)

        folder = STORE_ROOT / folder_name
        folder.mkdir(parents=True, exist_ok=True, mode=0o700)
        (folder / "turns").mkdir(parents=True, exist_ok=True, mode=0o700)
        manifest = _read_json(_manifest_path(folder), _new_manifest(folder_name, clean_title, cid, lid))
        existing_manifest_cid = str(manifest.get("conversation_id") or "").strip() or None

        # Letzte harte Schutzkante: niemals eine bestehende stabile Manifestidentität überschreiben.
        if cid and existing_manifest_cid and existing_manifest_cid != cid:
            pending_conflicts.append({
                "reason": "selected_folder_has_different_stable_conversation_id",
                "conversation_id": cid,
                "local_conversation_id": lid,
                "selected_folder": folder_name,
                "selected_manifest_conversation_id": existing_manifest_cid,
            })
            folder_name = _new_folder_name(clean_title, cid)
            folder = STORE_ROOT / folder_name
            folder.mkdir(parents=True, exist_ok=True, mode=0o700)
            (folder / "turns").mkdir(parents=True, exist_ok=True, mode=0o700)
            manifest = _read_json(_manifest_path(folder), _new_manifest(folder_name, clean_title, cid, lid))
            existing_manifest_cid = str(manifest.get("conversation_id") or "").strip() or None
            if existing_manifest_cid and existing_manifest_cid != cid:
                raise BrowserCaptureError("Stabile Conversation-ID konnte nicht in einen isolierten Ordner aufgelöst werden")

        conflict_rows = [_record_identity_conflict(index, conflict) for conflict in pending_conflicts]
        if conflict_rows:
            known_manifest_conflicts = manifest.setdefault("identity_conflicts", [])
            known_ids = {str(item.get("conflict_id")) for item in known_manifest_conflicts if isinstance(item, dict)}
            for row in conflict_rows:
                if row["conflict_id"] not in known_ids:
                    known_manifest_conflicts.append(row)
                    known_ids.add(row["conflict_id"])

        _update_title(manifest, clean_title)
        if cid:
            old = by_cid.get(cid)
            if old and old != folder_name:
                row = _record_identity_conflict(index, {
                    "reason": "conversation_id_index_reassigned_after_identity_validation",
                    "conversation_id": cid,
                    "local_conversation_id": lid,
                    "previous_indexed_folder": old,
                    "validated_folder": folder_name,
                })
                if not any(isinstance(item, dict) and item.get("conflict_id") == row["conflict_id"] for item in manifest.setdefault("identity_conflicts", [])):
                    manifest["identity_conflicts"].append(row)
            by_cid[cid] = folder_name
            if not existing_manifest_cid:
                manifest["conversation_id"] = cid
                manifest["short_conversation_id"] = _short_id(cid)
            elif existing_manifest_cid != cid:
                raise BrowserCaptureError("Bestehende stabile Manifestidentität darf nicht überschrieben werden")
        if lid:
            local_ids = manifest.setdefault("local_conversation_ids", [])
            if lid not in local_ids:
                local_ids.append(lid)
            indexed_local_folder = by_lid.get(lid)
            if not indexed_local_folder or indexed_local_folder == folder_name:
                by_lid[lid] = folder_name
            else:
                owner_manifest = _indexed_manifest(indexed_local_folder)
                owner_cid = str((owner_manifest or {}).get("conversation_id") or "").strip() or None
                if cid and owner_cid and owner_cid != cid:
                    row = _record_identity_conflict(index, {
                        "reason": "local_id_kept_with_first_stable_owner",
                        "conversation_id": cid,
                        "local_conversation_id": lid,
                        "first_owner_folder": indexed_local_folder,
                        "first_owner_conversation_id": owner_cid,
                        "additional_isolated_folder": folder_name,
                    })
                    if not any(isinstance(item, dict) and item.get("conflict_id") == row["conflict_id"] for item in manifest.setdefault("identity_conflicts", [])):
                        manifest["identity_conflicts"].append(row)
                elif not cid:
                    folder_name = indexed_local_folder
                    folder = STORE_ROOT / folder_name
                    manifest = _read_json(_manifest_path(folder), manifest)

        index.setdefault("folders", {})[folder_name] = {
            "conversation_id": manifest.get("conversation_id"),
            "current_title": manifest.get("current_title"),
            "updated_utc": _now(),
        }
        index["updated_utc"] = _now()
        _atomic_json(INDEX_PATH, index)
        _atomic_json(_manifest_path(folder), manifest)
        return folder, manifest, index
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


def _resolve_historical_import(
    *,
    conversation_id: str | None,
    local_conversation_id: str | None,
    title: str,
    import_id: str,
) -> tuple[Path, dict[str, Any], dict[str, Any], str]:
    """Route one historical import into a dedicated recovery folder.

    Stable conversation folders are the live/source record. Historical imports
    are separate evidence runs and must never append to that source folder.
    """
    clean_import_id = str(import_id or "").strip()
    if not clean_import_id:
        raise BrowserCaptureError("Historischer Import benötigt eine import_id")
    cid = str(conversation_id or "").strip() or None
    lid = str(local_conversation_id or "").strip() or None
    lock_handle = _lock(INDEX_LOCK)
    try:
        index = _read_json(INDEX_PATH, _new_index())
        import_index = index.setdefault("historical_imports", {})
        existing = import_index.get(clean_import_id) if isinstance(import_index, dict) else None
        if isinstance(existing, dict) and existing.get("folder_name"):
            folder_name = str(existing["folder_name"])
            folder = STORE_ROOT / folder_name
            manifest = _read_json(_manifest_path(folder), {})
            existing_cid = str(manifest.get("conversation_id") or "").strip() or None
            if cid and existing_cid and cid != existing_cid:
                raise BrowserCaptureError("Historische import_id ist bereits einer anderen Conversation-ID zugeordnet")
            recovery_run_id = str(existing.get("recovery_run_id") or f"recovery-{clean_import_id}")
        else:
            identity = f"{cid or lid or 'unknown'}|recovery|{clean_import_id}"
            folder_name = _new_folder_name(f"{title} Recovery", identity)
            folder = STORE_ROOT / folder_name
            folder.mkdir(parents=True, exist_ok=True, mode=0o700)
            (folder / "turns").mkdir(parents=True, exist_ok=True, mode=0o700)
            manifest = _new_manifest(folder_name, title, cid, lid)
            recovery_run_id = f"recovery-{clean_import_id}"
            manifest.update({
                "capture_scope": "historical_import_recovery",
                "recovery_run_id": recovery_run_id,
                "historical_import_id": clean_import_id,
                "source_conversation_folder": index.get("conversation_ids", {}).get(cid) if cid else None,
                "source_folder_immutable": True,
            })
            _atomic_json(_manifest_path(folder), manifest)
            import_index[clean_import_id] = {
                "folder_name": folder_name,
                "conversation_id": cid,
                "local_conversation_id": lid,
                "recovery_run_id": recovery_run_id,
                "created_utc": _now(),
            }
            index.setdefault("folders", {})[folder_name] = {
                "conversation_id": cid,
                "current_title": title,
                "updated_utc": _now(),
                "capture_scope": "historical_import_recovery",
                "recovery_run_id": recovery_run_id,
            }
            index["updated_utc"] = _now()
            _atomic_json(INDEX_PATH, index)
        manifest = _read_json(_manifest_path(folder), manifest)
        manifest.setdefault("historical_imports", {})
        manifest.setdefault("last_import_id", None)
        manifest.setdefault("capture_scope", "historical_import_recovery")
        manifest.setdefault("recovery_run_id", recovery_run_id)
        manifest.setdefault("source_folder_immutable", True)
        _atomic_json(_manifest_path(folder), manifest)
        return folder, manifest, index, recovery_run_id
    finally:
        fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
        lock_handle.close()


def _turn_record(manifest: dict[str, Any], turn_id: str) -> dict[str, Any]:
    turns = manifest.setdefault("turns", {})
    if turn_id not in turns:
        turns[turn_id] = {
            "turn_id": turn_id,
            "started_utc": None,
            "completed_utc": None,
            "status": "recording",
            "classification": "browser_only",
            "correlation_id": None,
            "correlation_conflicts": [],
            "mcp_binding_status": "not_bound",
            "binding_evidence": [],
            "event_count": 0,
            "message_count": 0,
            "gap_count": 0,
            "tab_instance_ids": [],
            "mcp_session_id": None,
            "action_history_event_ids": [],
        }
        manifest["turn_count"] = int(manifest.get("turn_count", 0)) + 1
    return turns[turn_id]


def _record_gap(folder: Path, manifest: dict[str, Any], turn: dict[str, Any] | None, gap: dict[str, Any]) -> None:
    _append_jsonl(folder / "capture_gaps.jsonl", gap)
    manifest["gap_count"] = int(manifest.get("gap_count", 0)) + 1
    if turn is not None:
        turn["gap_count"] = int(turn.get("gap_count", 0)) + 1
        turn["classification"] = "capture_incomplete"
        turn["status"] = "incomplete"


def record_browser_event(event: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(event, dict):
        raise TypeError("event muss ein Objekt sein")
    event = _unicode_safe(event)
    event_id = str(event.get("event_id") or uuid.uuid4())
    event_type = str(event.get("event_type") or "visible_update")[:80]
    title = str(event.get("chat_title") or "Unbenannter Chat")
    import_id = str(event.get("import_id") or "").strip() or None
    recovery_run_id = None
    is_web_capture = str(event.get("provider_id") or "").strip() == "web"
    if event_type.startswith("historical_import_") and import_id and not is_web_capture:
        folder, manifest, _, recovery_run_id = _resolve_historical_import(
            conversation_id=event.get("conversation_id"),
            local_conversation_id=event.get("local_conversation_id"),
            title=title,
            import_id=import_id,
        )
    else:
        folder, manifest, _ = resolve_conversation(
            conversation_id=event.get("conversation_id"),
            local_conversation_id=event.get("local_conversation_id"),
            title=title,
        )
    folder_lock = _lock(folder / ".capture.lock")
    try:
        stream_path = folder / "visible_stream.jsonl"
        if _contains_event(stream_path, event_id):
            return {
                "ok": True, "duplicate": True, "event_id": event_id,
                "folder_name": folder.name,
                "recovery_run_id": recovery_run_id or manifest.get("recovery_run_id"),
                "manifest": manifest,
            }
        manifest = _read_json(_manifest_path(folder), manifest)
        _update_title(manifest, title)
        manifest.setdefault("historical_imports", {})
        manifest.setdefault("page_snapshots", {})
        manifest.setdefault("last_import_id", None)
        manifest.setdefault("last_import_status", None)
        manifest.setdefault("last_snapshot_id", None)
        manifest.setdefault("b_timeline", {"available": False, "error": None})
        manifest["provider_id"] = str(event.get("provider_id") or manifest.get("provider_id") or "unknown")
        now = _now()
        turn_id = str(event.get("turn_id") or "").strip() or None
        correlation_id = str(event.get("correlation_id") or "").strip() or None
        tab_id = str(event.get("tab_instance_id") or "unknown-tab")[:180]
        seq_raw = event.get("sequence")
        try:
            sequence = int(seq_raw) if seq_raw is not None else None
        except (TypeError, ValueError):
            sequence = None
        classification = str(event.get("classification") or "browser_only")
        if classification not in TURN_CLASSES:
            classification = "browser_only"

        normalized = {
            **event,
            "schema_version": "1.0",
            "event_id": event_id,
            "event_type": event_type,
            "recorded_utc": now,
            "conversation_id": manifest.get("conversation_id"),
            "folder_name": folder.name,
            "tab_instance_id": tab_id,
            "turn_id": turn_id,
            "correlation_id": correlation_id,
            "browser_timestamp_utc": str(event.get("timestamp_utc") or now),
            "sequence": sequence,
            "classification": classification,
            "recovery_run_id": recovery_run_id or event.get("recovery_run_id"),
        }
        turn = _turn_record(manifest, turn_id) if turn_id else None
        if turn is not None:
            manifest["last_turn_id"] = turn_id
            if tab_id not in turn["tab_instance_ids"]:
                turn["tab_instance_ids"].append(tab_id)
            if event_type == "turn_start" and not turn.get("started_utc"):
                turn["started_utc"] = str(event.get("timestamp_utc") or now)
            existing_correlation = str(turn.get("correlation_id") or "").strip() or None
            if correlation_id and not existing_correlation:
                turn["correlation_id"] = correlation_id
            elif correlation_id and existing_correlation != correlation_id:
                conflict = {
                    "timestamp_utc": now,
                    "existing_correlation_id": existing_correlation,
                    "received_correlation_id": correlation_id,
                    "event_id": event_id,
                }
                turn.setdefault("correlation_conflicts", []).append(conflict)
                turn["mcp_binding_status"] = "unknown"
                _record_gap(folder, manifest, turn, {
                    "schema_version": "1.0",
                    "gap_id": str(uuid.uuid4()),
                    "timestamp_utc": now,
                    "reason": "turn_correlation_conflict",
                    "turn_id": turn_id,
                    "tab_instance_id": tab_id,
                    "details": conflict,
                })
            if turn.get("classification") != "capture_incomplete":
                turn["classification"] = classification

        if turn_id and sequence is not None:
            key = f"{turn_id}|{tab_id}"
            previous = manifest.setdefault("sequence_heads", {}).get(key)
            if isinstance(previous, int) and sequence > previous + 1:
                gap = {
                    "schema_version": "1.0",
                    "gap_id": str(uuid.uuid4()),
                    "timestamp_utc": now,
                    "reason": "sequence_gap",
                    "turn_id": turn_id,
                    "tab_instance_id": tab_id,
                    "expected_sequence": previous + 1,
                    "received_sequence": sequence,
                    "missing_from": previous + 1,
                    "missing_to": sequence - 1,
                }
                _record_gap(folder, manifest, turn, gap)
            elif isinstance(previous, int) and sequence <= previous:
                normalized["out_of_order"] = True
            manifest["sequence_heads"][key] = max(sequence, previous or 0)

        _append_jsonl(stream_path, normalized)
        if turn_id:
            _append_jsonl(folder / "turns" / f"{_safe_component(turn_id, 'turn')}.jsonl", normalized)
        manifest["visible_event_count"] = int(manifest.get("visible_event_count", 0)) + 1
        manifest["last_event_utc"] = str(event.get("timestamp_utc") or now)
        manifest["updated_utc"] = now
        if turn is not None:
            turn["event_count"] = int(turn.get("event_count", 0)) + 1

        if event_type in MESSAGE_TYPES:
            role = str(event.get("role") or "unknown")
            content = str(event.get("content") or "")
            message = {
                "schema_version": "1.0",
                "message_id": str(event.get("message_id") or event_id),
                "event_id": event_id,
                "timestamp_utc": str(event.get("timestamp_utc") or now),
                "recorded_utc": now,
                "conversation_id": manifest.get("conversation_id"),
                "folder_name": folder.name,
                "turn_id": turn_id,
                "correlation_id": turn.get("correlation_id") if turn else correlation_id,
                "tab_instance_id": tab_id,
                "role": role,
                "content": content,
                "content_sha256": _sha(content),
                "reasoning": str(event.get("reasoning") or "").strip() or None,
                "reasoning_sha256": _sha(str(event.get("reasoning") or "")) if event.get("reasoning") else None,
                # Presentation is a provider-DOM-derived allow-list tree, not
                # raw HTML.  Keep it beside the immutable plain transcript so
                # old captures and unsupported providers retain their exact
                # text fallback without a schema migration.
                "rich_content": event.get("rich_content") if isinstance(event.get("rich_content"), dict) else None,
                "media": event.get("media") if isinstance(event.get("media"), list) else [],
                "links": event.get("links") if isinstance(event.get("links"), list) else [],
                "classification": turn.get("classification") if turn else classification,
                "mcp_session_id": turn.get("mcp_session_id") if turn else None,
                "mcp_binding_status": turn.get("mcp_binding_status") if turn else "not_bound",
                "capture_kind": event.get("capture_kind") or ("historical_import" if event_type == "historical_import_message" else "live"),
                "import_id": event.get("import_id"),
                "recovery_run_id": recovery_run_id or event.get("recovery_run_id"),
                "ordinal": event.get("ordinal"),
                "dom_id": event.get("dom_id"),
                "history_evidence": event.get("history_evidence") if isinstance(event.get("history_evidence"), dict) else None,
            }
            if not _contains_event(folder / "messages.jsonl", event_id):
                _append_jsonl(folder / "messages.jsonl", message)
                manifest["message_count"] = int(manifest.get("message_count", 0)) + 1
                if turn is not None:
                    turn["message_count"] = int(turn.get("message_count", 0)) + 1

        if event_type == "web_capture_metadata" and isinstance(event.get("page_capture"), dict):
            manifest["web_capture"] = _unicode_safe(event["page_capture"])
            manifest["capture_kind"] = "webpage"
            manifest.setdefault("paths", {})["web_page_markdown"] = str(folder / "PAGE.md")
            manifest.setdefault("paths", {})["web_page_html"] = str(folder / "PAGE.html")
            manifest.setdefault("paths", {})["web_links"] = str(folder / "LINKS.json")

        if event_type in GAP_TYPES:
            gap = {
                "schema_version": "1.0",
                "gap_id": str(event.get("gap_id") or event_id),
                "timestamp_utc": str(event.get("timestamp_utc") or now),
                "reason": str(event.get("reason") or event_type),
                "turn_id": turn_id,
                "tab_instance_id": tab_id,
                "sequence": sequence,
                "details": event.get("details") or {},
            }
            _record_gap(folder, manifest, turn, gap)


        import_id = str(event.get("import_id") or "").strip() or None
        if event_type.startswith("historical_import_") and import_id:
            imports = manifest.setdefault("historical_imports", {})
            record = imports.setdefault(import_id, {
                "import_id": import_id,
                "started_utc": None,
                "finished_utc": None,
                "status": "unknown",
                "verified": False,
                "complete": False,
                "observed_count": 0,
                "observed_input_count": 0,
                "observed_output_count": 0,
                "recognized_count": 0,
                "input_count": 0,
                "output_count": 0,
                "stored_message_count": 0,
                "new_saved_count_reported": 0,
                "duplicate_count_reported": 0,
                "top_reached": False,
                "bottom_reached": False,
                "collapsed_detected": 0,
                "collapsed_opened": 0,
                "collapsed_remaining": None,
                "loading": False,
                "uncertainties": [],
                "history_proof": {},
                "tab_instance_ids": [],
            })
            if tab_id not in record["tab_instance_ids"]:
                record["tab_instance_ids"].append(tab_id)
            manifest["last_import_id"] = import_id
            if recovery_run_id:
                record["recovery_run_id"] = recovery_run_id
                manifest["recovery_run_id"] = recovery_run_id
            if event_type == "historical_import_start":
                record["started_utc"] = str(event.get("timestamp_utc") or now)
                record["status"] = "running"
            elif event_type == "historical_import_message":
                record["stored_message_count"] = int(record.get("stored_message_count", 0)) + 1
            else:
                for source, target in (
                    ("status", "status"),
                    ("verified", "verified"),
                    ("complete", "complete"),
                    ("observed_count", "observed_count"),
                    ("observed_input_count", "observed_input_count"),
                    ("observed_output_count", "observed_output_count"),
                    ("recognized_count", "recognized_count"),
                    ("input_count", "input_count"),
                    ("output_count", "output_count"),
                    ("new_saved_count", "new_saved_count_reported"),
                    ("duplicate_count", "duplicate_count_reported"),
                    ("top_reached", "top_reached"),
                    ("bottom_reached", "bottom_reached"),
                    ("collapsed_detected", "collapsed_detected"),
                    ("collapsed_opened", "collapsed_opened"),
                    ("collapsed_remaining", "collapsed_remaining"),
                    ("loading", "loading"),
                ):
                    if source in event:
                        record[target] = event[source]
                if isinstance(event.get("uncertainties"), list):
                    record["uncertainties"] = [str(x) for x in event["uncertainties"]]
                elif isinstance(event.get("gaps"), list):
                    record["uncertainties"] = [str(x) for x in event["gaps"]]
                if isinstance(event.get("history_proof"), dict):
                    record["history_proof"] = dict(event["history_proof"])
            if event_type == "historical_import_finish":
                record["finished_utc"] = str(event.get("timestamp_utc") or now)
                manifest["last_import_status"] = record.get("status")
                if not bool(record.get("complete")):
                    gap = {
                        "schema_version": "1.0",
                        "gap_id": str(uuid.uuid4()),
                        "timestamp_utc": now,
                        "reason": "historical_import_not_confirmed_complete",
                        "import_id": import_id,
                        "tab_instance_id": tab_id,
                        "details": {
                            "uncertainties": record.get("uncertainties", []),
                            "history_proof": record.get("history_proof", {}),
                        },
                    }
                    _record_gap(folder, manifest, None, gap)

        if event_type == "page_snapshot":
            snapshot_id = str(event.get("snapshot_id") or event_id)
            snapshots = manifest.setdefault("page_snapshots", {})
            visible_messages = event.get("visible_messages") if isinstance(event.get("visible_messages"), list) else []
            snapshots[snapshot_id] = {
                "snapshot_id": snapshot_id,
                "timestamp_utc": str(event.get("timestamp_utc") or now),
                "scope": event.get("snapshot_scope") or "currently_loaded_dom_only",
                "complete_history_claimed": False,
                "visible_message_count": len(visible_messages),
                "visible_status_count": len(event.get("visible_statuses") or []) if isinstance(event.get("visible_statuses"), list) else 0,
                "collapsed_detected": event.get("collapsed_detected", 0),
                "loading": bool(event.get("loading")),
                "tab_instance_id": tab_id,
                "event_id": event_id,
            }
            manifest["last_snapshot_id"] = snapshot_id

        if turn is not None and event_type in {"turn_completeness", "turn_completeness_confirmed", "turn_complete"}:
            completeness = event.get("completeness")
            if isinstance(completeness, dict):
                turn["completeness"] = completeness
                turn["completeness_verdict"] = completeness.get("verdict")
                turn["completeness_updated_utc"] = str(event.get("timestamp_utc") or now)
                turn["vps_confirmation"] = bool(
                    event.get("vps_confirmation")
                    or completeness.get("vps_confirmation", {}).get("confirmed")
                )

        if event_type == "turn_complete" and turn is not None:
            turn["completed_utc"] = str(event.get("timestamp_utc") or now)
            if turn.get("classification") == "capture_incomplete" or int(turn.get("gap_count", 0)):
                turn["status"] = "incomplete"
                turn["classification"] = "capture_incomplete"
            else:
                turn["status"] = "complete"
                manifest["last_complete_turn_id"] = turn_id
                manifest["complete_turn_count"] = int(manifest.get("complete_turn_count", 0)) + 1

        _refresh_human_chat_projections_safely(folder, manifest)
        _atomic_json(_manifest_path(folder), manifest)
        timeline_summary = manifest.get("b_timeline") or {"available": False}
        if event_type in {"turn_complete", "turn_completeness_confirmed"}:
            timeline_summary = _refresh_timeline_projection(folder, manifest)
            _atomic_json(_manifest_path(folder), manifest)
        return {
            "ok": True,
            "duplicate": False,
            "event_id": event_id,
            "folder_name": folder.name,
            "conversation_id": manifest.get("conversation_id"),
            "recovery_run_id": recovery_run_id or manifest.get("recovery_run_id"),
            "turn_id": turn_id,
            "correlation_id": turn.get("correlation_id") if turn else correlation_id,
            "turn_status": turn.get("status") if turn else None,
            "ui_completeness_status": turn.get("completeness_verdict") if turn else None,
            "mcp_binding_status": turn.get("mcp_binding_status") if turn else "not_bound",
            "last_complete_turn_id": manifest.get("last_complete_turn_id"),
            "gap_count": manifest.get("gap_count"),
            "b_timeline": timeline_summary,
        }
    finally:
        fcntl.flock(folder_lock.fileno(), fcntl.LOCK_UN)
        folder_lock.close()


def record_browser_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    if not isinstance(events, list):
        raise TypeError("events muss eine Liste sein")
    if len(events) > 250:
        raise BrowserCaptureError("Maximal 250 Ereignisse pro Batch")
    results = [record_browser_event(event) for event in events]
    return {
        "ok": True,
        "submitted": len(events),
        "new_events": sum(not r.get("duplicate") for r in results),
        "duplicates": sum(bool(r.get("duplicate")) for r in results),
        "results": results,
    }


def _resolve_identifier(identifier: str, import_id: str | None = None) -> Path:
    index = _read_json(INDEX_PATH, _new_index())
    value = str(identifier or "").strip()
    requested_import = str(import_id or "").strip()
    if requested_import:
        historical = index.get("historical_imports", {}).get(requested_import)
        if isinstance(historical, dict) and historical.get("folder_name"):
            candidate = STORE_ROOT / str(historical["folder_name"])
            if (_manifest_path(candidate)).exists():
                return candidate
    folder_name = (
        index.get("conversation_ids", {}).get(value)
        or index.get("local_ids", {}).get(value)
        or index.get("aliases", {}).get(value)
        or (value if (STORE_ROOT / value / "MANIFEST.json").exists() else None)
    )
    if not folder_name:
        raise BrowserCaptureError(f"Unbekannter Gesprächskörper: {identifier}")
    return STORE_ROOT / folder_name


def list_browser_chats(limit: int = 100) -> dict[str, Any]:
    index = _read_json(INDEX_PATH, _new_index())
    chats: list[dict[str, Any]] = []
    for folder_name in index.get("folders", {}):
        path = STORE_ROOT / folder_name / "MANIFEST.json"
        if not path.exists():
            continue
        m = _read_json(path, {})
        chats.append({
            "folder_name": folder_name,
            "provider_id": m.get("provider_id"),
            "conversation_id": m.get("conversation_id"),
            "alias": m.get("alias"),
            "current_title": m.get("current_title"),
            "updated_utc": m.get("updated_utc"),
            "last_complete_turn_id": m.get("last_complete_turn_id"),
            "last_turn_id": m.get("last_turn_id"),
            "turn_count": m.get("turn_count", 0),
            "complete_turn_count": m.get("complete_turn_count", 0),
            "gap_count": m.get("gap_count", 0),
            "last_import_id": m.get("last_import_id"),
            "last_import_status": m.get("last_import_status"),
            "last_snapshot_id": m.get("last_snapshot_id"),
            "b_timeline": m.get("b_timeline") or {"available": False},
        })
    chats.sort(key=lambda item: str(item.get("updated_utc") or ""), reverse=True)
    return {"ok": True, "count": len(chats), "returned": min(len(chats), limit), "chats": chats[:limit]}


def browser_chat_status(identifier: str) -> dict[str, Any]:
    value = str(identifier or "").strip()
    if not value:
        raise BrowserCaptureError("Gesprächskennung darf nicht leer sein")
    try:
        folder = _resolve_identifier(value)
    except BrowserCaptureError as exc:
        if not str(exc).startswith("Unbekannter Gesprächskörper:"):
            raise
        return {
            "ok": True,
            "available": False,
            "not_stored_yet": True,
            "identifier": value,
            "folder": None,
            "manifest": {},
            "turns": [],
            "gaps": [],
            "b_timeline": {
                "available": False,
                "reason": "chat_not_stored_yet",
                "error": None,
            },
        }
    manifest = _read_json(_manifest_path(folder), {})
    turns = list(manifest.get("turns", {}).values())
    turns.sort(key=lambda t: str(t.get("started_utc") or ""))
    return {
        "ok": True,
        "available": True,
        "not_stored_yet": False,
        "identifier": value,
        "folder": str(folder),
        "manifest": manifest,
        "turns": turns,
        "gaps": _read_jsonl(folder / "capture_gaps.jsonl", limit=100),
        "b_timeline": manifest.get("b_timeline") or {"available": False},
    }


def browser_chat_export_data(identifier: str) -> dict[str, Any]:
    """Return one safe, canonical export payload for the complete stored chat."""
    return _browser_chat_export_data(identifier, recorded_segment=False)


def browser_chat_recorded_segment_export_data(identifier: str, *, import_id: str | None = None) -> dict[str, Any]:
    """Return only the selected historical or live recording segment."""
    return _browser_chat_export_data(identifier, recorded_segment=True, recorded_import_id=import_id)


def _browser_chat_export_data(
    identifier: str,
    *,
    recorded_segment: bool,
    recorded_import_id: str | None = None,
) -> dict[str, Any]:
    """Build either the complete chat export or an exact stopped-import segment."""
    requested_import_id = str(recorded_import_id or "").strip()
    folder = _resolve_identifier(str(identifier or "").strip(), requested_import_id or None)
    manifest = _read_json(_manifest_path(folder), {})
    last_import_id = requested_import_id or str(manifest.get("last_import_id") or "").strip()
    source_messages = _read_jsonl(folder / "messages.jsonl")
    segment_kind: str | None = None
    # A long chat can be sampled more than once.  An export after Stop must
    # represent the just-finished pass, rather than silently merging separate
    # scroll ranges from earlier attempts.
    if recorded_segment and requested_import_id and last_import_id not in (manifest.get("historical_imports") or {}):
        raise BrowserCaptureError(f"Die angeforderte Aufnahme {last_import_id} ist im VPS-Manifest nicht bekannt.")
    if recorded_segment and not last_import_id:
        source_messages = [row for row in source_messages if row.get("capture_kind") != "historical_import"]
        if not source_messages:
            raise BrowserCaptureError("Für diesen Chat gibt es noch keine gespeicherte Live-Aufnahme.")
        segment_kind = "live_session"
    elif recorded_segment and last_import_id:
        latest_messages = [row for row in source_messages if row.get("import_id") == last_import_id]
        if not latest_messages:
            raise BrowserCaptureError(f"Die Aufnahme {last_import_id} enthält keine gespeicherten Nachrichten.")
        source_messages = latest_messages
        segment_kind = "historical_import"
    selected, selection = canonical_conversation_messages(source_messages)
    selection["exported_import_id"] = last_import_id if recorded_segment else None
    title = str(manifest.get("alias") or manifest.get("current_title") or "Unbenannter Chat").strip()
    provider = _human_provider_label(manifest.get("provider_id"))
    events: list[dict[str, Any]] = []
    source_events = _read_jsonl(folder / "visible_stream.jsonl")
    if recorded_segment and last_import_id:
        latest_events = [row for row in source_events if row.get("import_id") == last_import_id]
        source_events = latest_events
    elif recorded_segment:
        source_events = [row for row in source_events if row.get("capture_kind") != "historical_import"]
    for event in source_events:
        event_type = str(event.get("event_type") or "event")
        if event_type in _HUMAN_EVENT_OMISSIONS:
            continue
        summary = " · ".join(str(value) for value in (
            event.get("reason"), event.get("status"), event.get("completeness_verdict"), event.get("classification")
        ) if value)
        if event_type == "historical_import_finish":
            counter_summary = " · ".join(
                f"{label} {event.get(field)}"
                for label, field in (
                    ("DOM-Kontakte (keine Beiträge)", "observed_count"),
                    ("Input-DOM-Kontakte", "observed_input_count"),
                    ("Output-DOM-Kontakte", "observed_output_count"),
                    ("Eindeutige Beiträge", "recognized_count"),
                    ("Input", "input_count"),
                    ("Output", "output_count"),
                    ("Neu auf VPS", "new_saved_count"),
                )
                if field in event
            )
            if counter_summary:
                summary = " · ".join(part for part in (summary, counter_summary) if part)
        events.append({
            "ordinal": len(events) + 1,
            "type": event_type,
            "timestamp": event.get("timestamp_utc") or event.get("recorded_utc") or _now(),
            "role": event.get("role"),
            "summary": summary or None,
            "turn_id": event.get("turn_id"),
            "correlation_id": event.get("correlation_id"),
        })
    turns = [
        {
            "ordinal": index,
            "role": row.get("role"),
            "text": row.get("content"),
            "reasoning": row.get("reasoning") or None,
            "timestamp": row.get("recorded_utc") or row.get("timestamp_utc") or _now(),
            "message_id": row.get("message_id") or row.get("event_id"),
            "dom_id": row.get("dom_id"),
            "proof_hash": row.get("content_sha256"),
            "history_evidence": row.get("history_evidence"),
            "capture_order": row.get("capture_order")
            if isinstance(row.get("capture_order"), int)
            else (row.get("history_evidence") or {}).get("capture_order")
            if isinstance(row.get("history_evidence"), dict)
            else None,
            "provider_position": row.get("provider_position")
            if isinstance(row.get("provider_position"), (int, float))
            else (row.get("history_evidence") or {}).get("provider_position")
            if isinstance(row.get("history_evidence"), dict)
            else None,
            "rich_content": row.get("rich_content") if isinstance(row.get("rich_content"), dict) else None,
            "media": row.get("media") if isinstance(row.get("media"), list) else [],
            "codeBlocks": [],
        }
        for index, row in enumerate(selected, start=1)
    ]
    finish_event = next(
        (event for event in reversed(source_events) if event.get("event_type") == "historical_import_finish"),
        None,
    )
    counter_summary = {
        field: finish_event[field]
        for field in (
            "observed_count",
            "observed_input_count",
            "observed_output_count",
            "recognized_count",
            "input_count",
            "output_count",
            "new_saved_count",
            "duplicate_count",
        )
        if finish_event and field in finish_event
    }
    if finish_event and not counter_summary.get("new_saved_count"):
        import_record = (manifest.get("historical_imports") or {}).get(last_import_id or "", {})
        stored_message_count = import_record.get("stored_message_count")
        if stored_message_count is not None:
            counter_summary["new_saved_count"] = stored_message_count
    import_record = (manifest.get("historical_imports") or {}).get(last_import_id or "", {})
    history_proof = (
        finish_event.get("history_proof")
        if isinstance(finish_event, dict) and isinstance(finish_event.get("history_proof"), dict)
        else import_record.get("history_proof") if isinstance(import_record.get("history_proof"), dict) else {}
    )
    return {
        "ok": True,
        "data": {
            "title": title,
            "provider": provider,
            "model": "Browser UI-Aufnahme",
            "timestamp": _now(),
            "conversation_id": manifest.get("conversation_id") or identifier,
            "session_id": manifest.get("conversation_id") or identifier,
            "vps_sync": {"synced": True, "status": "kanonische VPS-Speicherung; Vollständigkeitsbeleg separat prüfen"},
            "turns": turns,
            "events": events,
            "counter_summary": counter_summary,
            "history_proof": history_proof,
            "scope": "recorded_segment" if recorded_segment else "complete_chat",
            "recorded_import_id": last_import_id or None if recorded_segment else None,
            "recorded_segment_kind": segment_kind if recorded_segment else None,
            "selection": selection,
        },
    }


def _web_links(messages: list[dict[str, Any]], page_capture: dict[str, Any]) -> list[dict[str, Any]]:
    """Deduplicate only browser-observed links; never fetch or execute them."""
    result: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    candidates: list[Any] = []
    for message in messages:
        candidates.extend(message.get("links") if isinstance(message.get("links"), list) else [])
    candidates.extend(page_capture.get("links") if isinstance(page_capture.get("links"), list) else [])
    for item in candidates:
        if not isinstance(item, dict):
            continue
        href = str(item.get("href") or "").strip()
        if not re.match(r"^(?:https?|mailto|tel):", href, re.IGNORECASE):
            continue
        text = str(item.get("text") or href).strip()[:1000]
        key = (href, text)
        if key in seen:
            continue
        seen.add(key)
        result.append({
            "href": href,
            "text": text,
            "title": item.get("title"),
            "kind": item.get("kind") or "link",
            "source_block_id": item.get("source_block_id"),
            "top": item.get("top"),
        })
    return result


def browser_web_export_data(identifier: str) -> dict[str, Any]:
    """Render a script-free offline webpage transcript from visible events."""
    folder = _resolve_identifier(str(identifier or "").strip())
    manifest = _read_json(_manifest_path(folder), {})
    if manifest.get("provider_id") != "web" and manifest.get("capture_kind") != "webpage":
        raise BrowserCaptureError("Die Kennung gehört nicht zu einer Webseitenaufnahme")
    messages = _read_jsonl(folder / "messages.jsonl")
    if not messages:
        raise BrowserCaptureError("Für diese Webseite wurden noch keine sichtbaren Bereiche gespeichert")
    page_capture = manifest.get("web_capture") if isinstance(manifest.get("web_capture"), dict) else {}
    title = str(page_capture.get("title") or manifest.get("current_title") or "Unbenannte Webseite").strip()
    source_url = str(page_capture.get("source_url") or "").strip()
    links = _web_links(messages, page_capture)
    captured = _now()
    markdown_lines = [f"# {title}", "", f"Quelle: {source_url}" if source_url else "Quelle: unbekannt", f"Aufgenommen: {captured}", "", "---", ""]
    html_blocks: list[str] = []
    for index, message in enumerate(messages, start=1):
        content = str(message.get("content") or "").strip()
        if not content:
            continue
        role = str(message.get("role") or "webpage")
        markdown_lines.extend([f"## Bereich {index} · {role}", "", content, ""])
        block_links = [item for item in links if item.get("source_block_id") == message.get("dom_id")]
        if block_links:
            markdown_lines.append("Links in diesem Bereich:")
            for item in block_links:
                markdown_lines.append(f"- [{item['text']}]({item['href']})")
            markdown_lines.append("")
        link_html = "".join(
            f'<li><a href="{html.escape(item["href"], quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(item["text"])}</a></li>'
            for item in block_links
        )
        html_blocks.append(
            f'<article data-block="{index}"><h2>Bereich {index} · {html.escape(role)}</h2>'
            f'<div class="content">{html.escape(content).replace(chr(10), "<br>")}</div>'
            f'{f"<ul class=\"links\">{link_html}</ul>" if link_html else ""}</article>'
        )
    if links:
        markdown_lines.extend(["## Alle Links", ""])
        for item in links:
            markdown_lines.append(f"- [{item['text']}]({item['href']})")
        markdown_lines.append("")
    markdown = "\n".join(markdown_lines).rstrip() + "\n"
    html_doc = "<!doctype html>\n<html lang=\"de\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>" + html.escape(title) + "</title><style>body{font:16px/1.55 system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#202124}article{border-top:1px solid #ddd;padding:1.25rem 0}.content{white-space:normal}.links{margin-top:.7rem}a{color:#0645ad}</style></head><body><header><h1>" + html.escape(title) + "</h1>" + (f'<p>Quelle: <a href="{html.escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(source_url)}</a></p>' if source_url else "") + f"<p>Aufgenommen: {html.escape(captured)}</p></header>{''.join(html_blocks)}" + ("<section><h2>Alle Links</h2><ul>" + "".join(f'<li><a href="{html.escape(item["href"], quote=True)}" target="_blank" rel="noopener noreferrer">{html.escape(item["text"])}</a></li>' for item in links) + "</ul></section>" if links else "") + "</body></html>\n"
    links_payload = {"source_url": source_url, "title": title, "captured_utc": captured, "links": links}
    page_payload = {
        "schema_version": 1,
        "artifact_kind": "projection",
        "capture_id": manifest.get("conversation_id") or identifier,
        "source_url": source_url,
        "title": title,
        "captured_utc": captured,
        "messages": messages,
        "links": links,
        "known_gaps": manifest.get("known_gaps") if isinstance(manifest.get("known_gaps"), list) else [],
    }
    text_lines = [title, f"Quelle: {source_url}" if source_url else "Quelle: unbekannt", f"Aufgenommen: {captured}", ""]
    csv_buffer = io.StringIO(newline="")
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["ordinal", "role", "dom_id", "content", "source_url", "captured_utc"])
    for index, message in enumerate(messages, start=1):
        content = str(message.get("content") or "").strip()
        role = str(message.get("role") or "webpage")
        text_lines.extend([f"Bereich {index} · {role}", content, ""])
        csv_writer.writerow([index, role, message.get("dom_id") or "", content, source_url, captured])
    plain_text = "\n".join(text_lines).rstrip() + "\n"
    page_json = json.dumps(_unicode_safe(page_payload), ensure_ascii=False, indent=2) + "\n"
    page_csv = csv_buffer.getvalue()
    _atomic_text(folder / "PAGE.md", markdown)
    _atomic_text(folder / "PAGE.html", html_doc)
    _atomic_text(folder / "PAGE.txt", plain_text)
    _atomic_text(folder / "PAGE.csv", page_csv)
    _atomic_text(folder / "PAGE.json", page_json)
    _atomic_json(folder / "LINKS.json", links_payload)
    manifest["web_export"] = {"generated_utc": captured, "link_count": len(links), "message_count": len(messages), "markdown_path": str(folder / "PAGE.md"), "html_path": str(folder / "PAGE.html"), "text_path": str(folder / "PAGE.txt"), "csv_path": str(folder / "PAGE.csv"), "json_path": str(folder / "PAGE.json"), "links_path": str(folder / "LINKS.json")}
    manifest["updated_utc"] = captured
    _atomic_json(_manifest_path(folder), manifest)
    return {"ok": True, "data": {"capture_id": manifest.get("conversation_id") or identifier, "title": title, "source_url": source_url, "message_count": len(messages), "link_count": len(links), "messages": messages, "artifacts": {"markdown": str(folder / "PAGE.md"), "html": str(folder / "PAGE.html"), "text": str(folder / "PAGE.txt"), "csv": str(folder / "PAGE.csv"), "json": str(folder / "PAGE.json"), "links": str(folder / "LINKS.json"), "manifest": str(_manifest_path(folder))}, "markdown": markdown, "html": html_doc, "text": plain_text, "csv": page_csv, "json": page_json, "links": links}}


def browser_web_office_export(identifier: str, *, format_name: str) -> dict[str, Any]:
    """Render PDF/DOCX from the same visible webpage projection as PAGE.*."""
    export_payload = browser_web_export_data(identifier)
    data = export_payload.get("data") if isinstance(export_payload, dict) else None
    if not isinstance(data, dict):
        raise BrowserCaptureError("Die Webseitenprojektion enthält keine Daten")
    messages = data.get("messages") if isinstance(data.get("messages"), list) else []
    office_data = {
        "title": data.get("title") or "Unbenannte Webseite",
        "provider": "Webseite",
        "scope": "complete_chat",
        "conversation_id": data.get("capture_id") or identifier,
        "source_url": data.get("source_url") or "",
        "history_proof": {"status": "partial_chain", "source": "visible_webpage_projection"},
        "turns": [{"role": "webpage", "text": str(item.get("content") or "")} for item in messages if isinstance(item, dict) and str(item.get("content") or "").strip()],
    }
    from .office_export import OfficeExportError, build_office_artifact
    try:
        artifact = build_office_artifact(office_data, variant="transcript", format_name=str(format_name or "").strip().lower())
    except OfficeExportError as exc:
        raise BrowserCaptureError(str(exc)) from exc
    folder = _resolve_identifier(str(identifier or "").strip())
    artifact_dir = folder / "exports" / "webpage"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stored_utc = _now()
    stamp = re.sub(r"[^0-9A-Za-z]", "", stored_utc.replace("+00:00", "Z"))[:22]
    artifact_path = artifact_dir / f"{stamp}__{artifact.filename}"
    artifact_path.write_bytes(artifact.content)
    os.chmod(artifact_path, 0o600)
    metadata = {"schema_version": "1.0", "artifact_kind": "webpage_office_export", "stored_utc": stored_utc, "capture_id": data.get("capture_id") or identifier, "source_url": data.get("source_url") or "", "format": artifact.format, "filename": artifact.filename, "storage_path": str(artifact_path.relative_to(folder)), "mime_type": artifact.mime_type, "bytes": len(artifact.content), "sha256": hashlib.sha256(artifact.content).hexdigest(), "input_projection": "PAGE.json"}
    _append_jsonl(folder / "exports" / "ARTIFACTS.jsonl", metadata)
    return {"ok": True, "filename": artifact.filename, "mime_type": artifact.mime_type, "content_base64": base64.b64encode(artifact.content).decode("ascii"), "vps_artifact": metadata}


def browser_chat_office_export(
    identifier: str,
    *,
    scope: str,
    variant: str,
    format_name: str,
) -> dict[str, Any]:
    """Render one immutable DOCX/ODT/PDF artifact on the VPS, then return its bytes.

    The browser never sends a second, potentially divergent representation.  The
    exact canonical payload used for the download is rendered and persisted
    server-side first; the returned base64 therefore describes that VPS artifact
    byte-for-byte.
    """
    normalized_scope = str(scope or "").strip()
    if normalized_scope not in {"complete_chat", "recorded_segment"}:
        raise BrowserCaptureError("Office-Exportbereich muss complete_chat oder recorded_segment sein")
    export_payload = (
        browser_chat_recorded_segment_export_data(identifier)
        if normalized_scope == "recorded_segment"
        else browser_chat_export_data(identifier)
    )
    data = export_payload.get("data") if isinstance(export_payload, dict) else None
    if not isinstance(data, dict):
        raise BrowserCaptureError("Der kanonische Chat-Export enthält keine Daten")

    from .office_export import OfficeExportError, build_office_artifact

    try:
        artifact = build_office_artifact(data, variant=str(variant or ""), format_name=str(format_name or ""))
    except OfficeExportError as exc:
        raise BrowserCaptureError(str(exc)) from exc

    folder = _resolve_identifier(str(identifier or "").strip())
    recorded_import_id = str(data.get("recorded_import_id") or "").strip() or None
    scope_folder = _safe_component(recorded_import_id or normalized_scope, "office-export")
    artifact_dir = folder / "exports" / scope_folder
    artifact_dir.mkdir(parents=True, exist_ok=True)
    stored_utc = _now()
    stamp = re.sub(r"[^0-9A-Za-z]", "", stored_utc.replace("+00:00", "Z"))[:22]
    stored_name = f"{stamp}__{artifact.filename}"
    artifact_path = artifact_dir / stored_name
    artifact_path.write_bytes(artifact.content)
    os.chmod(artifact_path, 0o600)
    content_sha256 = hashlib.sha256(artifact.content).hexdigest()
    metadata = {
        "schema_version": "1.0",
        "artifact_kind": "office_export",
        "stored_utc": stored_utc,
        "conversation_id": data.get("conversation_id") or identifier,
        "scope": normalized_scope,
        "recorded_import_id": recorded_import_id,
        "variant": artifact.variant,
        "format": artifact.format,
        "filename": artifact.filename,
        "storage_path": str(artifact_path.relative_to(folder)),
        "mime_type": artifact.mime_type,
        "bytes": len(artifact.content),
        "sha256": content_sha256,
        "history_proof": data.get("history_proof") if isinstance(data.get("history_proof"), dict) else {},
    }
    _append_jsonl(folder / "exports" / "ARTIFACTS.jsonl", metadata)
    return {
        "ok": True,
        "filename": artifact.filename,
        "mime_type": artifact.mime_type,
        "content_base64": base64.b64encode(artifact.content).decode("ascii"),
        "vps_artifact": metadata,
    }


def browser_chat_client_artifact_export(
    identifier: str,
    *,
    scope: str,
    artifact_kind: str,
    filename: str,
    content_base64: str,
    content_sha256: str,
    turn_count: int,
    input_count: int | None = None,
    output_count: int | None = None,
    semantic_verification: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist browser-generated HTML/Markdown only after canonical count checks."""
    normalized_scope = str(scope or "").strip()
    if normalized_scope not in {"complete_chat", "recorded_segment"}:
        raise BrowserCaptureError("HTML/MD-Exportbereich muss complete_chat oder recorded_segment sein")
    normalized_kind = str(artifact_kind or "").strip().lower()
    suffixes = {
        "html": (".html", "text/html;charset=utf-8"),
        "markdown": (".md", "text/markdown;charset=utf-8"),
        "events_markdown": (".md", "text/markdown;charset=utf-8"),
    }
    if normalized_kind not in suffixes:
        raise BrowserCaptureError("Nur html, markdown oder events_markdown dürfen als Browserartefakt gespeichert werden")
    try:
        raw = base64.b64decode(str(content_base64 or ""), validate=True)
    except (ValueError, base64.binascii.Error) as exc:
        raise BrowserCaptureError("Browserartefakt enthält kein gültiges Base64") from exc
    if not raw or len(raw) > 25 * 1024 * 1024:
        raise BrowserCaptureError("Browserartefakt ist leer oder größer als 25 MiB")
    expected_hash = str(content_sha256 or "").strip().lower()
    actual_hash = hashlib.sha256(raw).hexdigest()
    if expected_hash != actual_hash:
        raise BrowserCaptureError("SHA-256 des Browserartefakts stimmt nicht mit den gesendeten Bytes überein")

    canonical_payload = (
        browser_chat_recorded_segment_export_data(identifier)
        if normalized_scope == "recorded_segment"
        else browser_chat_export_data(identifier)
    )
    data = canonical_payload.get("data") if isinstance(canonical_payload, dict) else None
    if not isinstance(data, dict):
        raise BrowserCaptureError("Der VPS besitzt keine kanonischen Exportdaten für diesen Chat")
    canonical_turns = data.get("turns") if isinstance(data.get("turns"), list) else []
    try:
        submitted_turn_count = int(turn_count)
    except (TypeError, ValueError) as exc:
        raise BrowserCaptureError("Turnzähler des Browserartefakts ist ungültig") from exc
    if submitted_turn_count != len(canonical_turns):
        raise BrowserCaptureError(
            f"Turnzähler stimmt nicht: Browser {submitted_turn_count}, VPS-Kanon {len(canonical_turns)}"
        )
    canonical_inputs = sum(1 for turn in canonical_turns if turn.get("role") == "user")
    canonical_outputs = sum(1 for turn in canonical_turns if turn.get("role") == "assistant")
    if input_count is not None and int(input_count) != canonical_inputs:
        raise BrowserCaptureError(f"Inputzähler stimmt nicht: Browser {input_count}, VPS-Kanon {canonical_inputs}")
    if output_count is not None and int(output_count) != canonical_outputs:
        raise BrowserCaptureError(f"Outputzähler stimmt nicht: Browser {output_count}, VPS-Kanon {canonical_outputs}")
    semantic = semantic_verification if isinstance(semantic_verification, dict) else {}
    if normalized_scope == "complete_chat":
        if semantic.get("status") != "verified":
            raise BrowserCaptureError("Semantischer Nachrichtenabgleich fehlt oder meldet Abweichungen")
        proof = data.get("history_proof") if isinstance(data.get("history_proof"), dict) else {}
        semantic_sequence = proof.get("semantic_sequence") if isinstance(proof.get("semantic_sequence"), dict) else {}
        if proof.get("status") != "browser_chain_verified" and semantic_sequence.get("status") != "verified":
            raise BrowserCaptureError("Semantische Nachrichtenfolge ist nicht verifiziert; HTML/MD wird nicht als Gesamtchat gespeichert")

    folder = _resolve_identifier(str(identifier or "").strip())
    recorded_import_id = str(data.get("recorded_import_id") or "").strip() or None
    scope_folder = _safe_component(recorded_import_id or normalized_scope, "browser-export")
    artifact_dir = folder / "exports" / scope_folder
    artifact_dir.mkdir(parents=True, exist_ok=True)
    extension, mime_type = suffixes[normalized_kind]
    clean_name = _safe_component(Path(str(filename or "chat-export")).stem, "chat-export") + extension
    stored_utc = _now()
    stamp = re.sub(r"[^0-9A-Za-z]", "", stored_utc.replace("+00:00", "Z"))[:22]
    artifact_path = artifact_dir / f"{stamp}__{clean_name}"
    artifact_path.write_bytes(raw)
    os.chmod(artifact_path, 0o600)
    canonical_hash = _sha(json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    metadata = {
        "schema_version": "1.0",
        "artifact_kind": f"browser_{normalized_kind}",
        "stored_utc": stored_utc,
        "conversation_id": data.get("conversation_id") or identifier,
        "scope": normalized_scope,
        "recorded_import_id": recorded_import_id,
        "filename": clean_name,
        "storage_path": str(artifact_path.relative_to(folder)),
        "mime_type": mime_type,
        "bytes": len(raw),
        "sha256": actual_hash,
        "turn_count": submitted_turn_count,
        "input_count": canonical_inputs,
        "output_count": canonical_outputs,
        "semantic_verification": semantic,
        "canonical_data_sha256": canonical_hash,
        "history_proof": data.get("history_proof") if isinstance(data.get("history_proof"), dict) else {},
    }
    _append_jsonl(folder / "exports" / "ARTIFACTS.jsonl", metadata)
    return {"ok": True, "vps_artifact": metadata}


def read_browser_chat(
    identifier: str,
    *,
    visible_limit: int = 500,
    message_limit: int = 500,
) -> dict[str, Any]:
    folder = _resolve_identifier(identifier)
    manifest = _read_json(_manifest_path(folder), {})
    return {
        "ok": True,
        "folder": str(folder),
        "manifest": manifest,
        "messages": _read_jsonl(folder / "messages.jsonl", limit=max(1, min(message_limit, 5000))),
        "visible_stream": _read_jsonl(folder / "visible_stream.jsonl", limit=max(1, min(visible_limit, 5000))),
        "gaps": _read_jsonl(folder / "capture_gaps.jsonl", limit=1000),
    }


def read_browser_turn(identifier: str, turn_id: str, limit: int = 1000) -> dict[str, Any]:
    folder = _resolve_identifier(identifier)
    safe_turn = _safe_component(turn_id, "turn")
    path = folder / "turns" / f"{safe_turn}.jsonl"
    events = _read_jsonl(path, limit=limit)
    if not path.exists():
        raise BrowserCaptureError(f"Turn nicht gefunden: {turn_id}")
    messages = [row for row in _read_jsonl(folder / "messages.jsonl") if row.get("turn_id") == turn_id]
    manifest = _read_json(_manifest_path(folder), {})
    return {
        "ok": True,
        "folder": str(folder),
        "turn": manifest.get("turns", {}).get(turn_id),
        "events": events,
        "messages": messages,
    }


def read_browser_timeline(
    identifier: str,
    *,
    provider_id: str | None = None,
    turn_id: str | None = None,
    mcp_session_id: str | None = None,
    event_type: str | None = None,
    binding_status: str | None = None,
    from_utc: str | None = None,
    to_utc: str | None = None,
    include_derived: bool = True,
    limit: int = 5000,
    refresh_projection: bool = True,
) -> dict[str, Any]:
    folder = _resolve_identifier(identifier)
    manifest = _read_json(_manifest_path(folder), {})
    timeline = build_browser_timeline(
        folder,
        manifest,
        provider_id=provider_id,
        turn_id=turn_id,
        mcp_session_id=mcp_session_id,
        event_type=event_type,
        binding_status=binding_status,
        from_utc=from_utc,
        to_utc=to_utc,
        include_derived=include_derived,
        limit=limit,
    )
    if refresh_projection and not any((provider_id, turn_id, mcp_session_id, event_type, binding_status, from_utc, to_utc)):
        folder_lock = _lock(folder / ".capture.lock")
        try:
            manifest = _read_json(_manifest_path(folder), manifest)
            _refresh_timeline_projection(folder, manifest)
            manifest["updated_utc"] = _now()
            _atomic_json(_manifest_path(folder), manifest)
        finally:
            fcntl.flock(folder_lock.fileno(), fcntl.LOCK_UN)
            folder_lock.close()
    return timeline


def set_browser_chat_alias(identifier: str, alias: str) -> dict[str, Any]:
    folder = _resolve_identifier(identifier)
    clean_alias = str(alias or "").strip()[:120]
    if not clean_alias:
        raise BrowserCaptureError("Alias darf nicht leer sein")
    index_lock = _lock(INDEX_LOCK)
    folder_lock = _lock(folder / ".capture.lock")
    try:
        index = _read_json(INDEX_PATH, _new_index())
        manifest = _read_json(_manifest_path(folder), {})
        old_alias = manifest.get("alias")
        if old_alias:
            index.setdefault("aliases", {}).pop(old_alias, None)
        index.setdefault("aliases", {})[clean_alias] = folder.name
        index["updated_utc"] = _now()
        manifest["alias"] = clean_alias
        manifest["updated_utc"] = _now()
        event = {
            "schema_version": "1.0", "event_id": str(uuid.uuid4()),
            "event_type": "alias_set", "timestamp_utc": _now(),
            "recorded_utc": _now(), "folder_name": folder.name,
            "alias": clean_alias, "previous_alias": old_alias,
        }
        _append_jsonl(folder / "visible_stream.jsonl", event)
        manifest["visible_event_count"] = int(manifest.get("visible_event_count", 0)) + 1
        _atomic_json(_manifest_path(folder), manifest)
        _atomic_json(INDEX_PATH, index)
        return {"ok": True, "folder_name": folder.name, "alias": clean_alias}
    finally:
        fcntl.flock(folder_lock.fileno(), fcntl.LOCK_UN)
        folder_lock.close()
        fcntl.flock(index_lock.fileno(), fcntl.LOCK_UN)
        index_lock.close()


def link_browser_turn_to_mcp(
    identifier: str,
    turn_id: str,
    mcp_session_id: str,
    action_history_event_ids: list[str] | None = None,
    correlation_id: str | None = None,
) -> dict[str, Any]:
    folder = _resolve_identifier(identifier)
    folder_lock = _lock(folder / ".capture.lock")
    try:
        manifest = _read_json(_manifest_path(folder), {})
        turn = manifest.get("turns", {}).get(turn_id)
        if not isinstance(turn, dict):
            raise BrowserCaptureError(f"Turn nicht gefunden: {turn_id}")
        clean_session = str(mcp_session_id or "").strip()
        if not clean_session:
            raise BrowserCaptureError("mcp_session_id darf nicht leer sein")
        browser_correlation = str(turn.get("correlation_id") or "").strip() or None
        supplied_correlation = str(correlation_id or "").strip() or None
        if supplied_correlation and browser_correlation and supplied_correlation != browser_correlation:
            raise BrowserCaptureError(
                "Korrelationskonflikt: Browserturn und MCP-Bindung tragen unterschiedliche correlation_id"
            )
        ids = sorted({str(x).strip() for x in (action_history_event_ids or []) if str(x).strip()})
        confirmed = bool(browser_correlation and supplied_correlation == browser_correlation)
        binding_status = "confirmed" if confirmed else "unknown"
        evidence = {
            "kind": "matching_correlation_id" if confirmed else "manual_session_reference_without_shared_correlation",
            "timestamp_utc": _now(),
            "correlation_id": browser_correlation if confirmed else supplied_correlation,
            "mcp_session_id": clean_session,
            "action_history_event_ids": ids,
            "confirmed": confirmed,
        }
        turn["mcp_session_id"] = clean_session
        turn["mcp_binding_status"] = binding_status
        turn.setdefault("binding_evidence", []).append(evidence)
        turn["action_history_event_ids"] = sorted(set(turn.get("action_history_event_ids", []) + ids))
        if confirmed and turn.get("classification") != "capture_incomplete":
            turn["classification"] = "browser_with_mcp"
        if clean_session not in manifest.setdefault("mcp_sessions", []):
            manifest["mcp_sessions"].append(clean_session)
        manifest["action_history_event_ids"] = sorted(set(manifest.get("action_history_event_ids", []) + ids))
        manifest["updated_utc"] = _now()
        event = {
            "schema_version": "1.0",
            "event_id": str(uuid.uuid4()),
            "event_type": "mcp_turn_linked" if confirmed else "mcp_turn_link_unconfirmed",
            "timestamp_utc": _now(),
            "recorded_utc": _now(),
            "folder_name": folder.name,
            "conversation_id": manifest.get("conversation_id"),
            "provider_id": manifest.get("provider_id"),
            "turn_id": turn_id,
            "correlation_id": browser_correlation,
            "mcp_session_id": clean_session,
            "mcp_binding_status": binding_status,
            "binding_evidence": [evidence],
            "action_history_event_ids": ids,
            "classification": turn["classification"],
        }
        _append_jsonl(folder / "visible_stream.jsonl", event)
        _append_jsonl(folder / "turns" / f"{_safe_component(turn_id, 'turn')}.jsonl", event)
        manifest["visible_event_count"] = int(manifest.get("visible_event_count", 0)) + 1
        turn["event_count"] = int(turn.get("event_count", 0)) + 1
        _atomic_json(_manifest_path(folder), manifest)
        timeline_summary = _refresh_timeline_projection(folder, manifest)
        _atomic_json(_manifest_path(folder), manifest)
        return {
            "ok": True,
            "folder_name": folder.name,
            "turn": turn,
            "binding_status": binding_status,
            "confirmed": confirmed,
            "b_timeline": timeline_summary,
        }
    finally:
        fcntl.flock(folder_lock.fileno(), fcntl.LOCK_UN)
        folder_lock.close()


def verify_browser_capture(identifier: str | None = None) -> dict[str, Any]:
    folders = [_resolve_identifier(identifier)] if identifier else [
        STORE_ROOT / name for name in _read_json(INDEX_PATH, _new_index()).get("folders", {})
    ]
    findings: list[dict[str, Any]] = []
    checked = 0
    for folder in folders:
        if not folder.exists():
            findings.append({"folder": str(folder), "severity": "error", "finding": "folder_missing"})
            continue
        checked += 1
        manifest = _read_json(_manifest_path(folder), {})
        for filename in ("messages.jsonl", "visible_stream.jsonl", "capture_gaps.jsonl"):
            try:
                _read_jsonl(folder / filename)
            except BrowserCaptureError as exc:
                findings.append({"folder": folder.name, "severity": "error", "finding": str(exc)})
        for turn_id in manifest.get("turns", {}):
            path = folder / "turns" / f"{_safe_component(turn_id, 'turn')}.jsonl"
            if not path.exists():
                findings.append({"folder": folder.name, "turn_id": turn_id, "severity": "error", "finding": "turn_file_missing"})
            else:
                try:
                    _read_jsonl(path)
                except BrowserCaptureError as exc:
                    findings.append({"folder": folder.name, "turn_id": turn_id, "severity": "error", "finding": str(exc)})
        if manifest.get("gap_count", 0) and not (folder / "capture_gaps.jsonl").exists():
            findings.append({"folder": folder.name, "severity": "error", "finding": "gap_count_without_file"})
    return {
        "ok": not any(item["severity"] == "error" for item in findings),
        "checked_folders": checked,
        "findings": findings,
        "store_root": str(STORE_ROOT),
        "index_path": str(INDEX_PATH),
    }
