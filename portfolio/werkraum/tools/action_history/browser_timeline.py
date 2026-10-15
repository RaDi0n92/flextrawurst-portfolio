from __future__ import annotations

import datetime as dt
import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .history import acquire_flock

ACTION_HISTORY_PATH = Path(
    os.environ.get(
        "FLEXTRAWURST_ACTION_HISTORY",
        "/root/werkraum/_gpt/session_history.jsonl",
    )
)


class BrowserTimelineError(RuntimeError):
    pass


def _read_action_history(path: Path) -> list[dict[str, Any]]:
    """Liest die bestehende History mit Shared-Flock, ohne mkdir/chmod/touch oder andere Seiteneffekte."""
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        acquire_flock(handle, "browser-timeline-history-read", fcntl.LOCK_SH)
        try:
            for number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise BrowserTimelineError(f"Ungültige Action-History-Zeile {number}: {exc}") from exc
                if isinstance(value, dict):
                    rows.append(value)
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    return rows


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
                raise BrowserTimelineError(f"Ungültige JSONL-Zeile {number} in {path}: {exc}") from exc
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _atomic_text(path: Path, content: str, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = content.encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(encoded)
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


def _browser_time(event: dict[str, Any]) -> str | None:
    return str(event.get("timestamp_utc") or event.get("browser_timestamp_utc") or "").strip() or None


def _technical_time(event: dict[str, Any]) -> str | None:
    return str(event.get("timestamp_utc") or "").strip() or None


def _summary_for_browser(event: dict[str, Any]) -> str:
    event_type = str(event.get("event_type") or "visible_update")
    if event_type in {"message_final", "user_message_final", "assistant_message_final", "historical_import_message"}:
        role = str(event.get("role") or "unknown")
        content = str(event.get("content") or "").replace("\n", " ").strip()
        return f"{role}: {content[:220]}"
    if event_type == "visible_update":
        statuses = event.get("visible_statuses") if isinstance(event.get("visible_statuses"), list) else []
        return f"Sichtbarer UI-Zwischenstand mit {len(statuses)} Denk-/Arbeits-/Statusbereichen"
    if event_type.startswith("historical_import_"):
        return f"Altchat-Import: {event_type}"
    return event_type


def _summary_for_technical(event: dict[str, Any]) -> str:
    action = str(event.get("action") or "technical_action")
    target = str(event.get("target") or "").strip()
    status = str(event.get("status") or "unknown")
    return f"{action}{f' · {target}' if target else ''} · {status}"


def _turn_maps(manifest: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    turns = {
        str(turn_id): turn
        for turn_id, turn in (manifest.get("turns") or {}).items()
        if isinstance(turn, dict)
    }
    by_correlation: dict[str, str] = {}
    for turn_id, turn in turns.items():
        correlation_id = str(turn.get("correlation_id") or "").strip()
        if correlation_id:
            by_correlation[correlation_id] = turn_id
    return turns, by_correlation


def _matches_text(value: Any, expected: str | None) -> bool:
    if not expected:
        return True
    return str(value or "") == expected


def build_browser_timeline(
    folder: Path,
    manifest: dict[str, Any],
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
) -> dict[str, Any]:
    limit = max(1, min(int(limit), 20000))
    turns, by_correlation = _turn_maps(manifest)
    visible_stream_path = folder / "visible_stream.jsonl"
    browser_rows = _read_jsonl(visible_stream_path)

    requested_sessions = {str(mcp_session_id)} if mcp_session_id else set()
    explicitly_bound_sessions = {
        str(turn.get("mcp_session_id"))
        for turn in turns.values()
        if turn.get("mcp_session_id") and turn.get("mcp_binding_status") == "confirmed"
    }
    included_sessions = requested_sessions | explicitly_bound_sessions

    history_events: list[dict[str, Any]] = []
    if included_sessions:
        history_events = _read_action_history(ACTION_HISTORY_PATH)

    browser_entries: list[dict[str, Any]] = []
    for source_sequence, event in enumerate(browser_rows, start=1):
        row_turn_id = str(event.get("turn_id") or "").strip() or None
        turn = turns.get(row_turn_id or "", {})
        correlation_id = str(event.get("correlation_id") or turn.get("correlation_id") or "").strip() or None
        row_binding = str(turn.get("mcp_binding_status") or "not_bound")
        entry = {
            "timeline_event_id": f"browser:{event.get('event_id') or source_sequence}",
            "source": "browser_ui",
            "source_path": str(visible_stream_path),
            "source_event_id": event.get("event_id"),
            "source_sequence": source_sequence,
            "browser_sequence": event.get("sequence"),
            "provider_id": event.get("provider_id"),
            "conversation_id": manifest.get("conversation_id"),
            "chat_title": manifest.get("current_title"),
            "alias": manifest.get("alias"),
            "turn_id": row_turn_id,
            "ui_message_id": event.get("message_id"),
            "tab_instance_id": event.get("tab_instance_id"),
            "correlation_id": correlation_id,
            "event_type": event.get("event_type"),
            "reported_time_utc": _browser_time(event),
            "vps_received_time_utc": event.get("recorded_utc"),
            "classification": event.get("classification") or turn.get("classification") or "browser_only",
            "ui_completeness_status": turn.get("completeness_verdict") or turn.get("status") or "unknown",
            "mcp_binding_status": row_binding,
            "binding_evidence": list(turn.get("binding_evidence") or []),
            "summary": _summary_for_browser(event),
            "content": event.get("content") if event.get("event_type") in {
                "message_final", "user_message_final", "assistant_message_final", "historical_import_message"
            } else None,
            "visible_statuses": event.get("visible_statuses") if isinstance(event.get("visible_statuses"), list) else None,
            "gap": event.get("event_type") in {"capture_gap", "tab_discarded", "page_reload", "capture_error"},
            "source_order_proof": "browser_turn_sequence" if isinstance(event.get("sequence"), int) else "browser_append_order",
        }
        browser_entries.append(entry)

    browser_times_by_turn: dict[str, list[tuple[dt.datetime, dict[str, Any]]]] = {}
    for entry in browser_entries:
        parsed = _parse_time(entry.get("reported_time_utc"))
        if parsed and entry.get("turn_id"):
            browser_times_by_turn.setdefault(str(entry["turn_id"]), []).append((parsed, entry))

    technical_entries: list[dict[str, Any]] = []
    for action_sequence, event in enumerate(history_events, start=1):
        session_id = str(event.get("session_id") or "")
        if session_id not in included_sessions:
            continue
        details = event.get("details") if isinstance(event.get("details"), dict) else {}
        explicit_correlation = str(details.get("correlation_id") or "").strip() or None
        related_turn_id = by_correlation.get(explicit_correlation or "")
        relation_status = "unbound"
        evidence: list[dict[str, Any]] = []
        if related_turn_id:
            relation_status = "confirmed"
            evidence.append({
                "kind": "matching_correlation_id",
                "correlation_id": explicit_correlation,
                "action_history_event_id": event.get("event_id"),
            })
        else:
            session_turns = [
                (candidate_id, candidate)
                for candidate_id, candidate in turns.items()
                if candidate.get("mcp_session_id") == session_id
                and candidate.get("mcp_binding_status") == "confirmed"
            ]
            if len(session_turns) == 1:
                related_turn_id, bound_turn = session_turns[0]
                explicit_correlation = str(bound_turn.get("correlation_id") or "").strip() or None
                relation_status = "confirmed"
                evidence.append({
                    "kind": "explicit_session_binding",
                    "mcp_session_id": session_id,
                    "correlation_id": explicit_correlation,
                })
            elif include_derived:
                technical_time = _parse_time(_technical_time(event))
                nearest: tuple[float, str] | None = None
                if technical_time:
                    for candidate_id, browser_events in browser_times_by_turn.items():
                        for browser_time, _browser_entry in browser_events:
                            distance = abs((technical_time - browser_time).total_seconds())
                            if nearest is None or distance < nearest[0]:
                                nearest = (distance, candidate_id)
                if nearest and nearest[0] <= 120:
                    related_turn_id = nearest[1]
                    relation_status = "derived"
                    evidence.append({
                        "kind": "time_proximity_only",
                        "distance_seconds": nearest[0],
                        "warning": "Keine bestätigte Herkunft; nur zeitliche Nähe",
                    })
        related_turn = turns.get(str(related_turn_id or ""), {})
        entry = {
            "timeline_event_id": f"action_history:{event.get('event_id') or action_sequence}",
            "source": "mcp_action_history",
            "source_path": str(ACTION_HISTORY_PATH),
            "source_event_id": event.get("event_id"),
            "source_sequence": action_sequence,
            "action_history_sequence": action_sequence,
            "action_history_event_hash": event.get("event_hash"),
            "previous_action_history_hash": event.get("previous_hash"),
            "provider_id": manifest.get("provider_id") or None,
            "conversation_id": manifest.get("conversation_id"),
            "turn_id": related_turn_id,
            "correlation_id": explicit_correlation,
            "mcp_session_id": session_id,
            "event_type": event.get("action"),
            "reported_time_utc": _technical_time(event),
            "vps_received_time_utc": _technical_time(event),
            "classification": "technical_action",
            "ui_completeness_status": related_turn.get("completeness_verdict") or related_turn.get("status") or None,
            "mcp_binding_status": relation_status,
            "binding_evidence": evidence,
            "summary": _summary_for_technical(event),
            "action_status": event.get("status"),
            "target": event.get("target"),
            "details": details,
            "gap": False,
            "source_order_proof": "action_history_hash_chain_sequence",
        }
        technical_entries.append(entry)

    all_entries = browser_entries + technical_entries

    # Vorgänger/Folge gelten nur innerhalb derselben Primärquelle. Sie behaupten keine globale Kausalordnung.
    by_source: dict[str, list[dict[str, Any]]] = {}
    for entry in all_entries:
        by_source.setdefault(str(entry["source"]), []).append(entry)
    for rows in by_source.values():
        rows.sort(key=lambda item: int(item.get("source_sequence") or 0))
        for index, entry in enumerate(rows):
            entry["previous_source_event_id"] = rows[index - 1]["timeline_event_id"] if index else None
            entry["next_source_event_id"] = rows[index + 1]["timeline_event_id"] if index + 1 < len(rows) else None

    # Die kombinierte Sortierung ist nur eine lesbare Projektion nach gemeldeter Zeit, niemals ein Beweis perfekter Uhrsynchronität.
    def display_key(item: dict[str, Any]) -> tuple[dt.datetime, str, int]:
        parsed = _parse_time(item.get("reported_time_utc")) or dt.datetime.max.replace(tzinfo=dt.timezone.utc)
        return parsed, str(item.get("source")), int(item.get("source_sequence") or 0)

    all_entries.sort(key=display_key)
    second_groups: dict[str, list[dict[str, Any]]] = {}
    for entry in all_entries:
        parsed = _parse_time(entry.get("reported_time_utc"))
        key = parsed.strftime("%Y-%m-%dT%H:%M:%SZ") if parsed else "unknown-time"
        second_groups.setdefault(key, []).append(entry)
    for key, rows in second_groups.items():
        sources = {row.get("source") for row in rows}
        uncertain_parallel = len(rows) > 1 and len(sources) > 1
        for row in rows:
            row["parallel_group_id"] = key if uncertain_parallel else None
            row["cross_source_order_certainty"] = "parallel_or_uncertain" if uncertain_parallel else "not_compared"

    from_time = _parse_time(from_utc)
    to_time = _parse_time(to_utc)
    filtered: list[dict[str, Any]] = []
    for entry in all_entries:
        if provider_id and not _matches_text(entry.get("provider_id"), provider_id):
            continue
        if turn_id and not _matches_text(entry.get("turn_id"), turn_id):
            continue
        if mcp_session_id and entry.get("source") == "mcp_action_history" and not _matches_text(entry.get("mcp_session_id"), mcp_session_id):
            continue
        if event_type and not _matches_text(entry.get("event_type"), event_type):
            continue
        if binding_status and not _matches_text(entry.get("mcp_binding_status"), binding_status):
            continue
        parsed = _parse_time(entry.get("reported_time_utc"))
        if from_time and (not parsed or parsed < from_time):
            continue
        if to_time and (not parsed or parsed > to_time):
            continue
        filtered.append(entry)

    if len(filtered) > limit:
        filtered = filtered[-limit:]

    turn_summaries = []
    for candidate_id, turn in turns.items():
        if turn_id and candidate_id != turn_id:
            continue
        turn_summaries.append({
            "turn_id": candidate_id,
            "correlation_id": turn.get("correlation_id"),
            "ui_completeness_status": turn.get("completeness_verdict") or turn.get("status") or "unknown",
            "mcp_binding_status": turn.get("mcp_binding_status") or "not_bound",
            "mcp_session_id": turn.get("mcp_session_id"),
            "ui_event_count": turn.get("event_count", 0),
            "technical_event_count": sum(1 for row in technical_entries if row.get("turn_id") == candidate_id),
            "gap_count": turn.get("gap_count", 0),
            "binding_evidence": turn.get("binding_evidence") or [],
        })

    return {
        "ok": True,
        "schema_version": "1.0-b-shared-timeline",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "folder_name": folder.name,
        "conversation_id": manifest.get("conversation_id"),
        "chat_title": manifest.get("current_title"),
        "alias": manifest.get("alias"),
        "source_preservation": {
            "browser_primary_path": str(visible_stream_path),
            "action_history_primary_path": str(ACTION_HISTORY_PATH),
            "primary_sources_modified": False,
            "projection_regenerable": True,
        },
        "ordering_policy": {
            "browser_primary_order": "turn sequence, otherwise browser append order",
            "action_history_primary_order": "hash-chain append order",
            "combined_display_order": "reported timestamps only",
            "combined_display_order_is_exact_proof": False,
            "clock_synchrony_claimed": False,
            "same_second_cross_source_events": "parallel_or_uncertain unless explicit evidence exists",
        },
        "filters": {
            "provider_id": provider_id,
            "turn_id": turn_id,
            "mcp_session_id": mcp_session_id,
            "event_type": event_type,
            "binding_status": binding_status,
            "from_utc": from_utc,
            "to_utc": to_utc,
            "include_derived": include_derived,
            "limit": limit,
        },
        "turns": turn_summaries,
        "counts": {
            "browser_events_total": len(browser_entries),
            "technical_events_total": len(technical_entries),
            "returned_events": len(filtered),
            "confirmed_links": sum(1 for row in filtered if row.get("mcp_binding_status") == "confirmed"),
            "derived_links": sum(1 for row in filtered if row.get("mcp_binding_status") == "derived"),
            "unbound_or_unknown": sum(1 for row in filtered if row.get("mcp_binding_status") in {"unbound", "unknown", "not_bound"}),
            "gaps": sum(1 for row in filtered if row.get("gap")),
        },
        "events": filtered,
    }


def render_browser_timeline_markdown(timeline: dict[str, Any]) -> str:
    lines = [
        "# B – Gemeinsame Zeitspur",
        "",
        f"Gespräch: {timeline.get('chat_title') or 'Unbenannt'}",
        f"Conversation-ID: {timeline.get('conversation_id') or '–'}",
        f"Erzeugt: {timeline.get('generated_utc')}",
        "",
        "## Wahrheitsgrenze",
        "",
        "Browser- und Action-History-Primärquellen bleiben getrennt und unverändert.",
        "Die folgende gemeinsame Reihenfolge dient der Lesbarkeit nach gemeldeten Zeiten.",
        "Sie behauptet keine perfekte Uhrsynchronität und keine unsichtbaren internen Denkprozesse.",
        "",
        "## Turnstatus",
        "",
    ]
    for turn in timeline.get("turns", []):
        lines.append(
            f"- `{turn.get('turn_id')}` · UI: **{turn.get('ui_completeness_status')}** · "
            f"MCP-Bindung: **{turn.get('mcp_binding_status')}** · "
            f"UI-Ereignisse: {turn.get('ui_event_count', 0)} · technische Ereignisse: {turn.get('technical_event_count', 0)}"
        )
    lines.extend(["", "## Chronologische Projektion", ""])
    for event in timeline.get("events", []):
        marker = "UI" if event.get("source") == "browser_ui" else "MCP/VPS"
        uncertainty = " · parallel/zeitlich unsicher" if event.get("cross_source_order_certainty") == "parallel_or_uncertain" else ""
        binding = event.get("mcp_binding_status") or "not_bound"
        lines.append(
            f"- {event.get('reported_time_utc') or 'Zeit unbekannt'} · **{marker}** · "
            f"{event.get('summary') or event.get('event_type')} · Bindung: `{binding}`{uncertainty}"
        )
    lines.extend([
        "",
        "## Quellen",
        "",
        f"- Browser: `{timeline.get('source_preservation', {}).get('browser_primary_path')}`",
        f"- Action-History: `{timeline.get('source_preservation', {}).get('action_history_primary_path')}`",
        "",
    ])
    return "\n".join(lines)


def write_browser_timeline_projection(folder: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    timeline = build_browser_timeline(folder, manifest, include_derived=True, limit=20000)
    json_path = folder / "B_TIMELINE.json"
    markdown_path = folder / "B_ZEITSPUR.md"
    _atomic_text(json_path, json.dumps(timeline, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _atomic_text(markdown_path, render_browser_timeline_markdown(timeline) + "\n")
    return {
        "available": True,
        "generated_utc": timeline.get("generated_utc"),
        "machine_path": str(json_path),
        "human_path": str(markdown_path),
        "event_count": timeline.get("counts", {}).get("returned_events", 0),
        "confirmed_link_count": timeline.get("counts", {}).get("confirmed_links", 0),
        "derived_link_count": timeline.get("counts", {}).get("derived_links", 0),
        "turns": timeline.get("turns", []),
        "error": None,
    }
