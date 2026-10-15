from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

from mcp_atlas_entities import merge_into_relationship_graph


DATENSTAND_AUS_VERLAUF = "DERIVED_FROM_ACTION_HISTORY"
DATENSTAND_EXAKTER_PFAD = "EXACT_PATH_RELATION"
DATENSTAND_EXAKTE_ERWAEHNUNG = "FULLTEXT_EXACT_MENTION_DERIVED"
TRUTH_DECLARED = "DECLARED_SOURCE_RELATION"
TRUTH_STRUCTURAL = "STRUCTURAL_PATH_RELATION"

# Zuordnung protokollierter Akteure zu registrierten AI-Stroemen.
# Belegt aus den tatsaechlich in beiden History-Ketten vorkommenden
# actor-Werten (Stand 2026-08-01): GPT-5.6-sol-hoch, claude-code,
# codex-cli, glm-unbekannt, web-claude-check-in.
AKTEUR_PRAEFIX_ZU_STROM: tuple[tuple[str, str], ...] = (
    ("web-claude", "claudeweb"),
    ("claudeweb", "claudeweb"),
    ("claude-code", "claude"),
    ("claude", "claude"),
    ("gpt", "chatgpt"),
    ("chatgpt", "chatgpt"),
    ("codex", "codex"),
    ("kimi", "kimi"),
    ("gemini", "gemini"),
    ("glm", "glm"),
    ("grok", "grok"),
)


def strom_fuer_akteur(actor: Any) -> str | None:
    """Ordnet einen protokollierten Akteur einem AI-Strom zu.

    Reihenfolge ist bedeutsam: 'web-claude' muss vor 'claude' greifen,
    sonst wird der Web-Konnektor faelschlich Claude Code zugerechnet.
    Unbekannte Akteure liefern None und erzeugen KEINE Kante -- lieber
    keine Aussage als eine erfundene Zugehoerigkeit.
    """
    name = str(actor or "").strip().casefold()
    if not name:
        return None
    for praefix, strom in AKTEUR_PRAEFIX_ZU_STROM:
        if name.startswith(praefix):
            return strom
    return None


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def stable_id(*parts: Any, length: int = 24) -> str:
    payload = "\x1f".join(str(part) for part in parts).encode("utf-8", errors="replace")
    return hashlib.sha256(payload).hexdigest()[:length]


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass


def atomic_json(path: Path, value: Any) -> None:
    payload = (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    try:
        if path.read_bytes() == payload:
            return
    except FileNotFoundError:
        pass
    atomic_bytes(path, payload)


def atomic_text(path: Path, value: str) -> None:
    payload = value.encode("utf-8")
    try:
        if path.read_bytes() == payload:
            return
    except FileNotFoundError:
        pass
    atomic_bytes(path, payload)


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        handle = path.open("r", encoding="utf-8", errors="replace")
    except OSError:
        return rows
    with handle:
        for line in handle:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                rows.append(value)
    return rows


def is_within(path: str | Path, parent: str | Path) -> bool:
    try:
        child = Path(str(path)).resolve(strict=False)
        root = Path(str(parent)).resolve(strict=False)
        return child == root or child.is_relative_to(root)
    except (OSError, ValueError):
        return False


def paths_overlap(left: str | Path, right: str | Path) -> bool:
    return is_within(left, right) or is_within(right, left)


def project_match(projects: Iterable[dict[str, Any]], candidates: Iterable[str]) -> dict[str, Any] | None:
    cleaned = [str(value) for value in candidates if isinstance(value, str) and value.strip()]
    matches: list[tuple[int, dict[str, Any]]] = []
    for project in projects:
        path = str(project.get("path") or "")
        if not path:
            continue
        for candidate in cleaned:
            if is_within(candidate, path) or path in candidate:
                matches.append((len(path), project))
                break
    return max(matches, key=lambda item: item[0])[1] if matches else None


def extract_absolute_paths(value: str | None) -> list[str]:
    if not value:
        return []
    candidates = re.findall(r"/(?:root|etc|mnt|var|srv|opt|home)/[^\s'\"`|;<>]+", value)
    return [candidate.rstrip(").,]}:") for candidate in candidates]


ZUSATZ_HISTORIEN: tuple[Path, ...] = (
    Path("/root/werkraum/_shared/mcp_shared/action_history_sauber.jsonl"),
)


def read_history_events(history_path: Path) -> list[dict[str, Any]]:
    """Liest die Haupt-History und vereinigt sie mit bekannten Nebenketten.

    Hintergrund (geprueft am 2026-08-01): Es existieren zwei getrennte
    append-only Ketten mit disjunkten Akteuren --
    _gpt/session_history.jsonl fuehrt die VPS-ansaessigen Agenten
    (GPT-5.6-sol-hoch, claude-code, codex-cli, glm), und
    _shared/mcp_shared/action_history_sauber.jsonl fuehrt ausschliesslich
    den Web-Claude-MCP-Konnektor. Ohne Vereinigung erscheint der
    claudeweb-Strom im Beziehungsgraphen mit null Sessions.

    Dedup laeuft ueber event_id: heute ist die Schnittmenge leer, die
    Pruefung bleibt trotzdem stehen, damit eine spaetere Zusammenlegung
    der Ketten keine Doppelkanten erzeugt.
    """
    rows = read_jsonl(history_path)
    gesehen = {str(row.get("event_id")) for row in rows if row.get("event_id")}
    for zusatz in ZUSATZ_HISTORIEN:
        if zusatz == history_path:
            continue
        for row in read_jsonl(zusatz):
            event_id = row.get("event_id")
            if event_id and str(event_id) in gesehen:
                continue
            if event_id:
                gesehen.add(str(event_id))
            rows.append(row)
    rows.sort(key=event_order_key)
    return rows


def summary_text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, dict):
        for key in ("summary", "result", "task", "title", "reason"):
            result = summary_text(value.get(key))
            if result:
                return result
        for nested in value.values():
            result = summary_text(nested)
            if result:
                return result
    if isinstance(value, list):
        for nested in value:
            result = summary_text(nested)
            if result:
                return result
    return None


def event_is_mutation(event: dict[str, Any]) -> bool:
    action = str(event.get("action") or "")
    return action.startswith(
        (
            "vps.shell",
            "vps.exec_allowlisted",
            "vps.write",
            "vps.edit",
            "vps.move",
            "vps.delete",
            "tracked_write",
            "git.commit",
            "services.start",
            "services.stop",
            "services.restart",
            "services.enable",
            "services.disable",
            "services.install",
            "database.execute",
        )
    ) or any(token in action for token in ("completed", "commit", "write", "edit", "move", "delete"))


def event_is_verification(event: dict[str, Any]) -> bool:
    haystack = " ".join(
        [
            str(event.get("action") or ""),
            str(event.get("target") or ""),
            json.dumps(event.get("details") or {}, ensure_ascii=False),
        ]
    ).lower()
    return event.get("status") == "success" and any(
        token in haystack for token in ("test", "valid", "verify", "health", "probe", "integrity", "playwright")
    )


def event_project_ids(event: dict[str, Any], projects: list[dict[str, Any]]) -> list[str]:
    text_parts = [
        str(event.get("target") or ""),
        json.dumps(event.get("details") or {}, ensure_ascii=False),
    ]
    paths: list[str] = []
    for part in text_parts:
        paths.extend(extract_absolute_paths(part))
    combined = "\n".join(text_parts)
    matches: list[tuple[int, dict[str, Any]]] = []
    for project in projects:
        project_path = str(project.get("path") or "")
        project_id = str(project.get("project_id") or "")
        if not project_path or not project_id:
            continue
        if project_path in combined or any(is_within(path, project_path) for path in paths):
            matches.append((len(project_path), project))
    if not matches:
        return []
    longest = max(length for length, _project in matches)
    specific = [project for length, project in matches if length == longest]
    project_ids = {str(project["project_id"]) for project in specific}
    # Eine konkrete Strukturansicht oder Komponente bleibt sichtbar, aber ihr
    # kanonisches Elternprojekt erfährt ebenfalls von der Berührung.
    for project in specific:
        parent_id = project.get("canonical_parent_project_id")
        if parent_id:
            project_ids.add(str(parent_id))
    return sorted(project_ids)


def enrich_services(services: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unit_names = [str(row.get("unit")) for row in services if row.get("unit")]
    details: dict[str, dict[str, Any]] = {}
    if unit_names:
        try:
            raw = subprocess.check_output(
                [
                    "systemctl",
                    "show",
                    *unit_names,
                    "-p",
                    "Id",
                    "-p",
                    "FragmentPath",
                    "-p",
                    "WorkingDirectory",
                    "-p",
                    "ExecStart",
                    "-p",
                    "MainPID",
                    "-p",
                    "UnitFileState",
                ],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=30,
            )
            current: dict[str, str] = {}
            for line in raw.splitlines() + [""]:
                if not line.strip():
                    if current.get("Id"):
                        details[current["Id"]] = dict(current)
                    current = {}
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    current[key] = value
        except (subprocess.SubprocessError, OSError):
            details = {}
    enriched = []
    for row in services:
        unit = str(row.get("unit") or "")
        extra = details.get(unit, {})
        enriched.append(
            {
                **row,
                "fragment_path": extra.get("FragmentPath"),
                "working_directory": extra.get("WorkingDirectory"),
                "exec_start": extra.get("ExecStart"),
                "main_pid": int(extra.get("MainPID") or 0),
                "unit_file_state": extra.get("UnitFileState"),
            }
        )
    return enriched


def project_fingerprint(connection: sqlite3.Connection, project_path: str) -> dict[str, Any]:
    prefix = project_path.rstrip("/") + "/%"
    row = connection.execute(
        """
        SELECT
            count(*),
            sum(CASE WHEN is_dir=0 THEN 1 ELSE 0 END),
            sum(CASE WHEN is_dir=1 THEN 1 ELSE 0 END),
            coalesce(sum(CASE WHEN is_dir=0 THEN size ELSE 0 END),0),
            coalesce(max(mtime_ns),0)
        FROM paths
        WHERE path=? OR path LIKE ?
        """,
        (project_path, prefix),
    ).fetchone()
    values = {
        "node_count": int(row[0] or 0),
        "file_count": int(row[1] or 0),
        "directory_count": int(row[2] or 0),
        "byte_count": int(row[3] or 0),
        "max_mtime_ns": int(row[4] or 0),
    }
    values["fingerprint"] = hashlib.sha256(
        json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return values


def merge_project_revisions(
    *,
    projects: list[dict[str, Any]],
    path_db: Path,
    revision_path: Path,
    generated_utc: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    old = read_json(revision_path, {"projects": {}})
    old_projects = old.get("projects") if isinstance(old, dict) else {}
    if not isinstance(old_projects, dict):
        old_projects = {}
    connection = sqlite3.connect(path_db)
    changes: list[dict[str, Any]] = []
    new_state: dict[str, Any] = {}
    try:
        for project in projects:
            project_id = str(project["project_id"])
            stats = project_fingerprint(connection, str(project["path"]))
            previous = old_projects.get(project_id, {}) if isinstance(old_projects.get(project_id), dict) else {}
            revision = int(previous.get("revision") or 0)
            pending_ids = list(previous.get("pending_event_ids") or [])
            previous_fingerprint = previous.get("fingerprint")
            fingerprint_changed = previous_fingerprint != stats["fingerprint"]
            change_class = None
            if revision <= 0:
                revision = 1
                change_class = "project_revision_initialized"
            elif fingerprint_changed and pending_ids:
                change_class = "observed_mutation_materialized"
            elif fingerprint_changed:
                revision += 1
                change_class = "external_or_unobserved_scan_change"
            state = {
                "project_id": project_id,
                "path": project["path"],
                "revision": revision,
                "fingerprint": stats["fingerprint"],
                "fingerprint_stats": {key: value for key, value in stats.items() if key != "fingerprint"},
                "updated_utc": generated_utc,
                "pending_event_ids": [] if fingerprint_changed else pending_ids[-100:],
                "last_event_id": previous.get("last_event_id"),
                "last_event_hash": previous.get("last_event_hash"),
                "last_event_utc": previous.get("last_event_utc"),
                "last_event_session_id": previous.get("last_event_session_id"),
                "last_event_tool": previous.get("last_event_tool"),
                "last_event_target": previous.get("last_event_target"),
            }
            new_state[project_id] = state
            project.update(
                {
                    "project_revision": revision,
                    "project_fingerprint": stats["fingerprint"],
                    "fingerprint_stats": state["fingerprint_stats"],
                    "project_revision_updated_utc": generated_utc,
                }
            )
            if change_class:
                changes.append(
                    {
                        "kind": change_class,
                        "project_id": project_id,
                        "project_path": project["path"],
                        "project_revision": revision,
                        "previous_fingerprint": previous_fingerprint,
                        "fingerprint": stats["fingerprint"],
                        "materialized_event_ids": pending_ids,
                    }
                )
    finally:
        connection.close()
    payload = {"schema_version": "1.0", "generated_utc": generated_utc, "projects": new_state}
    atomic_json(revision_path, payload)
    return projects, payload, changes


def observe_project_event(
    *,
    projects_path: Path,
    revision_path: Path,
    event: dict[str, Any],
    tool_name: str,
    target: str | None,
    context_paths: Iterable[str] | None = None,
) -> dict[str, Any] | None:
    projects = read_json(projects_path, [])
    if not isinstance(projects, list):
        return None
    candidates = list(context_paths or []) + extract_absolute_paths(target)
    if target:
        candidates.append(target)
    project = project_match(projects, candidates)
    if not project:
        return None
    payload = read_json(revision_path, {"schema_version": "1.0", "projects": {}})
    state_map = payload.setdefault("projects", {})
    project_id = str(project["project_id"])
    state = state_map.get(project_id, {}) if isinstance(state_map.get(project_id), dict) else {}
    revision = max(1, int(state.get("revision") or project.get("project_revision") or 1)) + 1
    pending = list(state.get("pending_event_ids") or [])
    event_id = event.get("event_id")
    if event_id and event_id not in pending:
        pending.append(event_id)
    state.update(
        {
            "project_id": project_id,
            "path": project["path"],
            "revision": revision,
            "pending_event_ids": pending[-100:],
            "updated_utc": event.get("timestamp_utc") or utcnow(),
            "last_event_id": event_id,
            "last_event_hash": event.get("event_hash"),
            "last_event_utc": event.get("timestamp_utc"),
            "last_event_session_id": event.get("session_id"),
            "last_event_tool": tool_name,
            "last_event_target": target,
            "fingerprint": state.get("fingerprint") or project.get("project_fingerprint"),
            "fingerprint_stats": state.get("fingerprint_stats") or project.get("fingerprint_stats") or {},
        }
    )
    state_map[project_id] = state
    payload["generated_utc"] = utcnow()
    atomic_json(revision_path, payload)
    return {
        "project_id": project_id,
        "project_path": project["path"],
        "project_revision": revision,
        "event_id": event_id,
    }


def load_claims(projects: list[dict[str, Any]], global_claim_root: Path) -> list[dict[str, Any]]:
    paths = set(global_claim_root.glob("*.json")) if global_claim_root.exists() else set()
    for project in projects:
        candidate = Path(str(project.get("path") or "")) / "coordination" / "claims"
        if candidate.exists():
            paths.update(candidate.glob("*.json"))
    claims: list[dict[str, Any]] = []
    for path in sorted(paths):
        value = read_json(path, None)
        if not isinstance(value, dict):
            continue
        claims.append({**value, "claim_path": str(path)})
    return claims


def event_order_key(event: dict[str, Any]) -> tuple[int, str, str]:
    raw_ns = event.get("timestamp_unix_ns")
    if raw_ns is not None:
        try:
            return (int(raw_ns), str(event.get("timestamp_utc") or ""), str(event.get("event_id") or ""))
        except (TypeError, ValueError):
            pass
    raw_utc = str(event.get("timestamp_utc") or "")
    try:
        normalized = raw_utc.replace("Z", "+00:00")
        parsed = dt.datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        timestamp_ns = int(parsed.timestamp() * 1_000_000_000)
    except (TypeError, ValueError, OverflowError):
        timestamp_ns = 0
    return (timestamp_ns, raw_utc, str(event.get("event_id") or ""))


def session_groups(history_events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in history_events:
        session_id = str(event.get("session_id") or "")
        if session_id:
            groups[session_id].append(event)
    for rows in groups.values():
        rows.sort(key=event_order_key)
    return groups


def build_handoffs(
    *,
    history_events: list[dict[str, Any]],
    projects: list[dict[str, Any]],
    handoff_root: Path,
    register_path: Path,
    generated_utc: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    handoff_root.mkdir(parents=True, exist_ok=True, mode=0o700)
    rows: list[dict[str, Any]] = []
    by_session: dict[str, dict[str, Any]] = {}
    for session_id, events in session_groups(history_events).items():
        end_events = [event for event in events if event.get("action") == "session.end"]
        if not end_events:
            continue
        end_event = end_events[-1]
        start_event = next((event for event in events if event.get("action") == "session.begin"), None)
        handoff_id = stable_id("handoff", session_id, end_event.get("event_id"))
        mutations = [event for event in events if event_is_mutation(event)]
        failures = [event for event in events if event.get("status") in {"failed", "blocked"}]
        partial = [event for event in events if event.get("completeness") in {"partial", "unknown", "aborted"}]
        verifications = [event for event in events if event_is_verification(event)]
        markers = [
            event
            for event in events
            if any(token in str(event.get("action") or "") for token in ("marker", "completed", "consensus", "conflict"))
        ]
        project_ids = sorted({project_id for event in events for project_id in event_project_ids(event, projects)})
        project_lookup = {str(project["project_id"]): project for project in projects}
        related_projects = [
            {
                "project_id": project_id,
                "path": project_lookup[project_id]["path"],
                "name": project_lookup[project_id]["name"],
                "datenstand": DATENSTAND_EXAKTER_PFAD,
            }
            for project_id in project_ids
            if project_id in project_lookup
        ]
        changed_targets = []
        for event in mutations:
            target = event.get("target")
            if isinstance(target, str) and target and len(target) < 1200:
                changed_targets.append(target)
        summary = summary_text((end_event.get("details") or {}).get("summary")) or summary_text(end_event.get("details"))
        payload = {
            "schema_version": "1.0",
            "handoff_id": handoff_id,
            "datenstand": DATENSTAND_AUS_VERLAUF,
            "source_session_id": session_id,
            "actor": end_event.get("actor") or (start_event or {}).get("actor"),
            "started_utc": (start_event or {}).get("timestamp_utc"),
            "ended_utc": end_event.get("timestamp_utc"),
            "completion_summary": summary,
            "event_count": len(events),
            "mutation_count": len(mutations),
            "verification_count": len(verifications),
            "failure_count": len(failures),
            "partial_count": len(partial),
            "changed_targets": sorted(set(changed_targets))[:200],
            "related_projects": related_projects,
            "verification_events": [compact_event(event) for event in verifications[-30:]],
            "important_markers": [compact_event(event) for event in markers[-30:]],
            "failures_or_open_wounds": [compact_event(event) for event in (failures + partial)[-50:]],
            "source_event_ids": [event.get("event_id") for event in events if event.get("event_id")],
            "source_event_hashes": [event.get("event_hash") for event in events if event.get("event_hash")],
            "end_event_id": end_event.get("event_id"),
            "end_event_hash": end_event.get("event_hash"),
            "generated_utc": generated_utc,
            "einschraenkung": "Dieser Übergabekörper ist eine deterministische Ableitung aus der append-only Action-History. Er ersetzt weder den UI-Gesprächskörper noch Originaldateien.",
        }
        json_path = handoff_root / f"{session_id}.json"
        md_path = handoff_root / f"{session_id}.md"
        payload["json_path"] = str(json_path)
        payload["markdown_path"] = str(md_path)
        atomic_json(json_path, payload)
        lines = [
            f"# Sessionübergabe: {session_id}",
            "",
            f"> Datenstand: `{DATENSTAND_AUS_VERLAUF}`",
            "",
            "## Abschluss",
            "",
            summary or "Kein menschenlesbarer Abschluss in der technischen History vorhanden.",
            "",
            "## Bilanz",
            "",
            f"- Ereignisse: **{len(events)}**",
            f"- Mutationen: **{len(mutations)}**",
            f"- Prüfungen: **{len(verifications)}**",
            f"- Fehler/Blocker: **{len(failures)}**",
            f"- unvollständige Ereignisse: **{len(partial)}**",
            "",
            "## Zugeordnete Projekte",
            "",
        ]
        lines.extend(
            [f"- **{item['name']}** · `{item['path']}` · `{item['datenstand']}`" for item in related_projects]
            or ["- Keine beweisbare Projektzuordnung aus Pfaden und Historyzielen."]
        )
        lines.extend(["", "## Veränderte Ziele", ""])
        lines.extend([f"- `{target}`" for target in sorted(set(changed_targets))[:200]] or ["- Keine protokollierte Mutation."])
        lines.extend(["", "## Offene Wunden", ""])
        lines.extend(
            [f"- `{item.get('timestamp_utc')}` · `{item.get('action')}` · {item.get('summary') or item.get('target') or 'ohne Kurztext'}" for item in payload["failures_or_open_wounds"]]
            or ["- Keine in der technischen History."]
        )
        lines.extend(
            [
                "",
                "## Herkunft",
                "",
                f"- Endereignis: `{end_event.get('event_id')}`",
                f"- Endhash: `{end_event.get('event_hash')}`",
                f"- JSON: `{json_path}`",
                "",
            ]
        )
        atomic_text(md_path, "\n".join(lines))
        register_row = {
            key: payload[key]
            for key in (
                "handoff_id",
                "datenstand",
                "source_session_id",
                "actor",
                "started_utc",
                "ended_utc",
                "completion_summary",
                "event_count",
                "mutation_count",
                "verification_count",
                "failure_count",
                "partial_count",
                "related_projects",
                "end_event_id",
                "end_event_hash",
                "json_path",
                "markdown_path",
            )
        }
        rows.append(register_row)
        by_session[session_id] = register_row
    rows.sort(key=lambda row: row.get("ended_utc") or "", reverse=True)
    atomic_json(register_path, {"schema_version": "1.0", "generated_utc": generated_utc, "handoffs": rows})
    return rows, by_session


def compact_event(event: dict[str, Any]) -> dict[str, Any]:
    details = event.get("details") if isinstance(event.get("details"), dict) else {}
    summary = summary_text(details)
    target = event.get("target")
    if not summary and isinstance(target, str):
        summary = target.splitlines()[0][:420]
    return {
        "event_id": event.get("event_id"),
        "event_hash": event.get("event_hash"),
        "timestamp_utc": event.get("timestamp_utc"),
        "session_id": event.get("session_id"),
        "actor": event.get("actor"),
        "action": event.get("action"),
        "status": event.get("status"),
        "completeness": event.get("completeness"),
        "target": target if isinstance(target, str) and len(target) < 1000 else None,
        "summary": summary,
    }


def concept_documents_under(concept_db: Path, root_path: str) -> list[tuple[str, str]]:
    if not concept_db.exists() or not root_path:
        return []
    connection = sqlite3.connect(concept_db)
    try:
        return [
            (str(row[0]), "\n".join(str(value or "") for value in row[1:]))
            for row in connection.execute(
                "SELECT path,title,headings,body FROM documents WHERE path=? OR path LIKE ?",
                (root_path, root_path.rstrip("/") + "/%"),
            )
        ]
    except sqlite3.OperationalError:
        return []
    finally:
        connection.close()


def build_ai_bridges(
    *,
    streams: list[dict[str, Any]],
    projects: list[dict[str, Any]],
    history_events: list[dict[str, Any]],
    concept_db: Path,
    bridge_path: Path,
    generated_utc: str,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    old = read_json(bridge_path, {"streams": {}})
    old_map = old.get("streams") if isinstance(old, dict) else {}
    if not isinstance(old_map, dict):
        old_map = {}
    session_project_map: dict[str, set[str]] = defaultdict(set)
    for event in history_events:
        for project_id in event_project_ids(event, projects):
            session_project_map[str(event.get("session_id") or "")].add(project_id)
    project_lookup = {str(project["project_id"]): project for project in projects}
    bridges: dict[str, Any] = {}
    changes: list[dict[str, Any]] = []
    for stream in streams:
        stream_id = str(stream.get("id") or "")
        session_root = str(stream.get("sessions") or "")
        related: dict[str, dict[str, Any]] = {}
        evidence_documents: list[str] = []
        indexed_document_count = 0
        if stream_id == "chatgpt":
            for session_id, project_ids in session_project_map.items():
                for project_id in project_ids:
                    project = project_lookup.get(project_id)
                    if not project or not project.get("bridge_eligible"):
                        continue
                    row = related.setdefault(
                        project_id,
                        {
                            "project_id": project_id,
                            "name": project["name"],
                            "path": project["path"],
                            "project_class": project.get("project_class"),
                            "datenstand": DATENSTAND_EXAKTER_PFAD,
                            "evidence_sessions": [],
                            "evidence_paths": [],
                        },
                    )
                    if session_id and session_id not in row["evidence_sessions"]:
                        row["evidence_sessions"].append(session_id)
        elif session_root:
            documents = concept_documents_under(concept_db, session_root)
            indexed_document_count = len(documents)
            for document_path, text in documents:
                folded = text.casefold()
                for project in projects:
                    if not project.get("bridge_eligible"):
                        continue
                    project_path = str(project["path"])
                    project_name = str(project["name"])
                    name_match = len(project_name) >= 7 and project_name.casefold() in folded
                    path_match = project_path.casefold() in folded
                    if not (name_match or path_match):
                        continue
                    project_id = str(project["project_id"])
                    row = related.setdefault(
                        project_id,
                        {
                            "project_id": project_id,
                            "name": project_name,
                            "path": project_path,
                            "project_class": project.get("project_class"),
                            "datenstand": DATENSTAND_EXAKTE_ERWAEHNUNG,
                            "evidence_sessions": [],
                            "evidence_paths": [],
                        },
                    )
                    if document_path not in row["evidence_paths"] and len(row["evidence_paths"]) < 20:
                        row["evidence_paths"].append(document_path)
                        evidence_documents.append(document_path)
        source_stats = stream.get("session_source_stats") or {}
        fingerprint_input = {
            "home_exists": stream.get("home_exists"),
            "entry_files": stream.get("entry_files"),
            "session_source_stats": source_stats,
            "related_projects": sorted(related),
            "indexed_document_count": indexed_document_count,
        }
        fingerprint = hashlib.sha256(
            json.dumps(fingerprint_input, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()
        previous = old_map.get(stream_id, {}) if isinstance(old_map.get(stream_id), dict) else {}
        revision = int(previous.get("revision") or 0)
        if revision <= 0:
            revision = 1
        elif previous.get("fingerprint") != fingerprint:
            revision += 1
            changes.append(
                {
                    "kind": "ai_stream_bridge_change",
                    "stream_id": stream_id,
                    "stream_revision": revision,
                    "previous_fingerprint": previous.get("fingerprint"),
                    "fingerprint": fingerprint,
                }
            )
        bridge = {
            "stream_id": stream_id,
            "revision": revision,
            "fingerprint": fingerprint,
            "generated_utc": generated_utc,
            "home": stream.get("home"),
            "workspace": stream.get("workspace"),
            "session_source": stream.get("sessions"),
            "session_source_stats": source_stats,
            "indexed_session_document_count": indexed_document_count,
            "related_projects": sorted(related.values(), key=lambda row: row["path"]),
            "source_paths": sorted(
                {
                    str(path)
                    for path in [stream.get("home"), stream.get("workspace"), stream.get("sessions")]
                    if path
                }
            ),
            "einschraenkung": "Brücken verknüpfen belegte Pfade, Sessionquellen und exakte Erwähnungen. Sie verschmelzen keine AI-Ströme und erfinden keine gemeinsame Erinnerung.",
        }
        bridges[stream_id] = bridge
        stream["bridge"] = bridge
        stream["related_projects"] = bridge["related_projects"]
        stream["stream_revision"] = revision
    payload = {"schema_version": "1.0", "generated_utc": generated_utc, "streams": bridges}
    atomic_json(bridge_path, payload)
    return streams, payload, changes


def node_id(node_type: str, identity: str) -> str:
    return f"{node_type}:{stable_id(node_type, identity, length=20)}"


def add_node(nodes: dict[str, dict[str, Any]], node_type: str, identity: str, label: str, path: str | None, datenstand: str, metadata: dict[str, Any] | None = None) -> str:
    identifier = node_id(node_type, identity)
    nodes[identifier] = {
        "node_id": identifier,
        "node_type": node_type,
        "identity": identity,
        "label": label,
        "path": path,
        "datenstand": datenstand,
        "metadata": metadata or {},
    }
    return identifier


def add_edge(
    edges: dict[tuple[str, str, str, str], dict[str, Any]],
    source: str,
    target: str,
    relation: str,
    datenstand: str,
    evidence: dict[str, Any] | None = None,
    timestamp_utc: str | None = None,
) -> None:
    """Legt eine Kante an oder ergaenzt sie.

    timestamp_utc ist der belegte Zeitpunkt des ausloesenden Ereignisses.
    Kanten, die aus reiner Struktur entstehen (Enthaltensein, Deklaration),
    bekommen bewusst KEINEN Zeitpunkt: first_utc/last_utc bleiben dort NULL.
    Ein NULL ist hier eine Aussage, keine Luecke -- es bedeutet
    "diese Beziehung hat keinen Ereigniszeitpunkt", nicht "Zeit unbekannt".
    """
    key = (source, target, relation, datenstand)
    row = edges.setdefault(
        key,
        {
            "edge_id": stable_id(*key),
            "source_node_id": source,
            "target_node_id": target,
            "relation": relation,
            "datenstand": datenstand,
            "evidence": [],
            "first_utc": None,
            "last_utc": None,
        },
    )
    if evidence and evidence not in row["evidence"] and len(row["evidence"]) < 100:
        row["evidence"].append(evidence)
    stamp = str(timestamp_utc).strip() if timestamp_utc else ""
    if stamp:
        if not row["first_utc"] or stamp < row["first_utc"]:
            row["first_utc"] = stamp
        if not row["last_utc"] or stamp > row["last_utc"]:
            row["last_utc"] = stamp


def validation_artifact_class(path: str) -> str:
    name = Path(path).name.lower()
    suffix = Path(path).suffix.lower()
    if any(token in name for token in ("validierungsbericht", "validation_report", "final_validation")):
        return "summary_report"
    if name in {"result.json", "validation.json", "validierung.json"} or name.endswith("_result.json"):
        return "machine_result"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif"}:
        return "visual_evidence"
    if suffix in {".log", ".txt"}:
        return "log_or_text_evidence"
    if suffix == ".json":
        return "structured_evidence"
    if suffix == ".md":
        return "narrative_evidence"
    return "other_evidence"


def validation_paths(path_db: Path) -> list[str]:
    connection = sqlite3.connect(path_db)
    try:
        return [
            str(row[0])
            for row in connection.execute(
                """
                SELECT path FROM paths
                WHERE is_dir=0 AND (
                    lower(basename) LIKE '%validierungsbericht%'
                    OR lower(basename) IN ('result.json','validation.json','validierung.json')
                    OR lower(path) LIKE '%/validation/%'
                )
                LIMIT 10000
                """
            )
        ]
    finally:
        connection.close()


def build_relationship_layer(
    *,
    projects: list[dict[str, Any]],
    vaults: list[dict[str, Any]],
    services: list[dict[str, Any]],
    streams: list[dict[str, Any]],
    history_events: list[dict[str, Any]],
    claims: list[dict[str, Any]],
    handoffs: list[dict[str, Any]],
    consensus_rows: list[dict[str, Any]],
    conflict_rows: list[dict[str, Any]],
    path_db: Path,
    relation_db: Path,
    relation_json: Path,
    generated_utc: str,
    refresh_mode: str = "full",
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    project_nodes: dict[str, str] = {}
    project_lookup = {str(project["project_id"]): project for project in projects}
    for project in projects:
        project_id = str(project["project_id"])
        project_nodes[project_id] = add_node(
            nodes,
            "project",
            project_id,
            str(project["name"]),
            str(project["path"]),
            DATENSTAND_EXAKTER_PFAD,
            {"project_revision": project.get("project_revision"), "markers": project.get("markers")},
        )
        for view in project.get("generated_views") or []:
            view_node = add_node(nodes, "generated_view", str(view), Path(str(view)).name, str(view), TRUTH_STRUCTURAL)
            add_edge(edges, project_nodes[project_id], view_node, "HAS_GENERATED_VIEW", TRUTH_STRUCTURAL, {"path": view})
    for vault in vaults:
        path = str(vault.get("path") or "")
        if not path:
            continue
        vault_node = add_node(nodes, "vault", path, Path(path).name, path, DATENSTAND_EXAKTER_PFAD, vault)
        project = project_match(projects, [path])
        if project:
            add_edge(edges, project_nodes[str(project["project_id"])], vault_node, "CONTAINS_VAULT", TRUTH_STRUCTURAL, {"path": path})
    for service in services:
        unit = str(service.get("unit") or "")
        if not unit:
            continue
        service_node = add_node(nodes, "service", unit, unit, service.get("fragment_path"), TRUTH_DECLARED, service)
        candidates = [
            str(value)
            for value in (service.get("fragment_path"), service.get("working_directory"), service.get("exec_start"))
            if value
        ]
        project = project_match(projects, candidates)
        if project:
            add_edge(
                edges,
                project_nodes[str(project["project_id"])],
                service_node,
                "HAS_SERVICE",
                DATENSTAND_EXAKTER_PFAD,
                {"working_directory": service.get("working_directory"), "exec_start": service.get("exec_start")},
            )
    session_nodes: dict[str, str] = {}
    session_projects: dict[str, set[str]] = defaultdict(set)
    session_last_utc: dict[str, str] = {}
    session_actor: dict[str, str] = {}
    for event in history_events:
        session_id = str(event.get("session_id") or "")
        if not session_id:
            continue
        akteur = str(event.get("actor") or "").strip()
        if akteur and session_id not in session_actor:
            session_actor[session_id] = akteur
        event_utc = str(event.get("timestamp_utc") or "").strip() or None
        if event_utc and event_utc > session_last_utc.get(session_id, ""):
            session_last_utc[session_id] = event_utc
        if session_id not in session_nodes:
            session_nodes[session_id] = add_node(nodes, "session", session_id, session_id, None, DATENSTAND_AUS_VERLAUF, {"actor": event.get("actor")})
        for project_id in event_project_ids(event, projects):
            session_projects[session_id].add(project_id)
            add_edge(
                edges,
                session_nodes[session_id],
                project_nodes[project_id],
                "TOUCHED_PROJECT",
                DATENSTAND_EXAKTER_PFAD,
                {"event_id": event.get("event_id"), "event_hash": event.get("event_hash"), "target": event.get("target")},
                timestamp_utc=event_utc,
            )
    # --- Datei-Knoten (belegt, mit Schwelle) ------------------------------
    # Nur Dateien, die mindestens DATEI_KNOTEN_SCHWELLE mal in der History
    # vorkommen UND im Pfadindex real existieren.
    # Gemessen am 2026-08-01 ueber beide History-Ketten:
    #   Schwelle 1 -> 2017 Knoten (45% davon Einzelnennungen = lose Fransen)
    #   Schwelle 3 ->  710 Knoten
    # Erwaehnte Pfade ohne Eintrag im Pfadindex (rund die Haelfte aller
    # Fundstellen) werden hier bewusst NICHT zu Knoten. Sie sind belegte
    # Spuren verschwundener Dinge und gehoeren in eine Luecken-Ansicht,
    # nicht in den Bestandsgraphen.
    DATEI_KNOTEN_SCHWELLE = 3
    datei_zaehler: Counter[str] = Counter()
    datei_events: dict[str, set[str]] = defaultdict(set)
    datei_je_session: dict[str, set[str]] = defaultdict(set)
    for event in history_events:
        event_session = str(event.get("session_id") or "")
        event_id = str(event.get("event_id") or "")
        blob = str(event.get("target") or "") + "\n" + json.dumps(event.get("details") or {}, ensure_ascii=False)
        for kandidat in extract_absolute_paths(blob):
            datei_zaehler[kandidat] += 1
            if event_id:
                datei_events[kandidat].add(event_id)
            if event_session:
                datei_je_session[event_session].add(kandidat)
    kandidaten = [pfad for pfad, ev_set in datei_events.items() if len(ev_set) >= DATEI_KNOTEN_SCHWELLE]
    echte_dateien: dict[str, int] = {}
    if kandidaten:
        pfad_verbindung = sqlite3.connect(path_db)
        try:
            for start in range(0, len(kandidaten), 400):
                teil = kandidaten[start : start + 400]
                platzhalter = ",".join("?" for _ in teil)
                for pfad, ist_ordner, groesse in pfad_verbindung.execute(
                    f"SELECT path,is_dir,size FROM paths WHERE path IN ({platzhalter})", teil
                ):
                    if not ist_ordner:
                        echte_dateien[str(pfad)] = int(groesse or 0)
        finally:
            pfad_verbindung.close()
    datei_nodes: dict[str, str] = {}
    for pfad, groesse in sorted(echte_dateien.items()):
        datei_nodes[pfad] = add_node(
            nodes,
            "file",
            pfad,
            Path(pfad).name,
            pfad,
            DATENSTAND_EXAKTER_PFAD,
            {
                "size": groesse,
                "mention_count": datei_zaehler[pfad],
                "extension": Path(pfad).suffix.lower(),
            },
        )
        datei_projekt = project_match(projects, [pfad])
        if datei_projekt and str(datei_projekt["project_id"]) in project_nodes:
            add_edge(
                edges,
                project_nodes[str(datei_projekt["project_id"])],
                datei_nodes[pfad],
                "CONTAINS_FILE",
                TRUTH_STRUCTURAL,
                {"path": pfad},
            )
    for beruehrende_session, beruehrte_pfade in datei_je_session.items():
        session_node = session_nodes.get(beruehrende_session)
        if not session_node:
            continue
        for pfad in sorted(beruehrte_pfade & set(datei_nodes)):
            add_edge(
                edges,
                session_node,
                datei_nodes[pfad],
                "TOUCHED_FILE",
                DATENSTAND_EXAKTER_PFAD,
                {"mention_count": datei_zaehler[pfad]},
                timestamp_utc=session_last_utc.get(beruehrende_session),
            )
    claim_rows: list[dict[str, Any]] = []
    for claim in claims:
        claim_id = str(claim.get("claim_id") or stable_id(claim.get("claim_path")))
        claim_node = add_node(nodes, "claim", claim_id, claim_id, claim.get("claim_path"), TRUTH_DECLARED, claim)
        owner_session = str(claim.get("owner_session_id") or "")
        if owner_session:
            session_node = session_nodes.get(owner_session) or add_node(nodes, "session", owner_session, owner_session, None, TRUTH_DECLARED)
            session_nodes[owner_session] = session_node
            add_edge(edges, session_node, claim_node, "OWNS_CLAIM", TRUTH_DECLARED, {"claim_path": claim.get("claim_path")})
        related_projects = []
        owned_targets = [str(value) for value in claim.get("owned_targets") or []]
        for project in projects:
            if any(paths_overlap(target, str(project["path"])) for target in owned_targets):
                project_id = str(project["project_id"])
                related_projects.append(project_id)
                add_edge(edges, claim_node, project_nodes[project_id], "CLAIMS_PROJECT_OR_SUBTREE", TRUTH_DECLARED, {"owned_targets": owned_targets})
        claim_rows.append({**claim, "related_project_ids": sorted(set(related_projects))})
    validation_rows: list[dict[str, Any]] = []
    for path in validation_paths(path_db):
        artifact_class = validation_artifact_class(path)
        validation_node = add_node(
            nodes,
            "validation",
            path,
            Path(path).name,
            path,
            DATENSTAND_EXAKTER_PFAD,
            {"artifact_class": artifact_class},
        )
        project = project_match(projects, [path])
        related_project_id = None
        if project:
            related_project_id = str(project["project_id"])
            add_edge(edges, project_nodes[related_project_id], validation_node, "HAS_VALIDATION", TRUTH_STRUCTURAL, {"path": path})
        validation_rows.append({"path": path, "artifact_class": artifact_class, "related_project_id": related_project_id})
    for handoff in handoffs:
        handoff_id = str(handoff["handoff_id"])
        handoff_node = add_node(nodes, "handoff", handoff_id, handoff_id, handoff.get("markdown_path"), DATENSTAND_AUS_VERLAUF, handoff)
        session_id = str(handoff.get("source_session_id") or "")
        handoff_utc = str(handoff.get("ended_utc") or "").strip() or None
        if session_id:
            session_node = session_nodes.get(session_id) or add_node(nodes, "session", session_id, session_id, None, DATENSTAND_AUS_VERLAUF)
            session_nodes[session_id] = session_node
            add_edge(
                edges,
                session_node,
                handoff_node,
                "HAS_HANDOFF",
                DATENSTAND_AUS_VERLAUF,
                {"end_event_id": handoff.get("end_event_id")},
                timestamp_utc=handoff_utc,
            )
        for related in handoff.get("related_projects") or []:
            project_id = str(related.get("project_id") or "")
            if project_id in project_nodes:
                add_edge(
                    edges,
                    handoff_node,
                    project_nodes[project_id],
                    "HANDOFF_RELATES_TO_PROJECT",
                    DATENSTAND_EXAKTER_PFAD,
                    {"session_id": session_id},
                    timestamp_utc=handoff_utc,
                )
    for stream in streams:
        stream_id = str(stream.get("id") or "")
        stream_node = add_node(nodes, "ai_stream", stream_id, stream_id, stream.get("home"), TRUTH_DECLARED, stream)
        for related in stream.get("related_projects") or []:
            project_id = str(related.get("project_id") or "")
            if project_id in project_nodes:
                add_edge(edges, stream_node, project_nodes[project_id], "AI_STREAM_RELATES_TO_PROJECT", str(related.get("datenstand") or DATENSTAND_EXAKTE_ERWAEHNUNG), related)
        # Sessionherkunft folgt dem protokollierten Akteur, nicht einem
        # fest verdrahteten Strom. Vorher galt: nur "chatgpt" erhielt
        # PRODUCED_SESSION -- dadurch sah der Graph so aus, als haette
        # ausschliesslich ChatGPT je Sitzungen hervorgebracht.
        for session_id, session_node in session_nodes.items():
            if strom_fuer_akteur(session_actor.get(session_id)) != stream_id:
                continue
            add_edge(
                edges,
                stream_node,
                session_node,
                "PRODUCED_SESSION",
                DATENSTAND_AUS_VERLAUF,
                {"actor": session_actor.get(session_id)},
                timestamp_utc=session_last_utc.get(session_id),
            )
        # Begriffsarbeit 2026-08-02 (Claude Web): Sessionzahl allein verzerrt den
        # Aktivitaetsvergleich zwischen Stroemen -- ChatGPT verbindet sich bei jedem
        # neuen Chat neu, andere Stroeme bleiben in einer Session. Deshalb zwei
        # getrennte, beide reale Kennzahlen statt einer irrefuehrenden:
        #   anbindungsdichte: wie oft dieser Strom eine neue Session eroeffnet hat
        #   wirkdichte: wie viele TOUCHED_PROJECT/TOUCHED_FILE Kanten aus diesen
        #               Sessions tatsaechlich hervorgegangen sind
        eigene_sessions = {
            session_node
            for session_id, session_node in session_nodes.items()
            if strom_fuer_akteur(session_actor.get(session_id)) == stream_id
        }
        anbindungsdichte = len(eigene_sessions)
        wirkdichte = sum(
            1
            for row in edges.values()
            if row["relation"] in ("TOUCHED_PROJECT", "TOUCHED_FILE")
            and row["source_node_id"] in eigene_sessions
        )
        nodes[stream_node]["metadata"]["anbindungsdichte"] = anbindungsdichte
        nodes[stream_node]["metadata"]["wirkdichte"] = wirkdichte
    for row_type, rows, relation in (
        ("consensus", consensus_rows, "HAS_CONSENSUS"),
        ("conflict", conflict_rows, "HAS_CONFLICT"),
    ):
        for row in rows:
            identity = str(row.get(f"{row_type}_id") or stable_id(row_type, json.dumps(row, sort_keys=True, ensure_ascii=False)))
            statement = str(row.get("statement") or row.get("statement_a") or identity)
            row_node = add_node(nodes, row_type, identity, statement[:180], None, str(row.get("class") or row.get("status") or "UNBEKANNT"), row)
            encoded = json.dumps(row, ensure_ascii=False)
            for project in projects:
                if str(project["path"]) in encoded:
                    add_edge(edges, project_nodes[str(project["project_id"])], row_node, relation, DATENSTAND_EXAKTER_PFAD, {"source": row_type})
    # OMAPI: Die acht Urbewohner werden VOR dem atomaren DB-Guss ergänzt.
    # Eine nachträgliche SQLite-Manipulation würde beim nächsten Refresh verschwinden.
    urbewohner_summary = merge_into_relationship_graph(
        nodes=nodes,
        edges=edges,
        generated_utc=generated_utc,
        add_node=add_node,
        add_edge=add_edge,
        refresh_mode=refresh_mode,
    )

    edge_rows = list(edges.values())
    relation_counts = Counter(row["relation"] for row in edge_rows)
    node_counts = Counter(row["node_type"] for row in nodes.values())
    temp_path = relation_db.with_name(f".{relation_db.name}.{os.getpid()}.tmp")
    try:
        temp_path.unlink()
    except FileNotFoundError:
        pass
    connection = sqlite3.connect(temp_path)
    try:
        connection.executescript(
            """
            PRAGMA journal_mode=OFF;
            PRAGMA synchronous=OFF;
            CREATE TABLE nodes (
                node_id TEXT PRIMARY KEY,
                node_type TEXT NOT NULL,
                identity TEXT NOT NULL,
                label TEXT,
                path TEXT,
                datenstand TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            );
            CREATE TABLE edges (
                edge_id TEXT PRIMARY KEY,
                source_node_id TEXT NOT NULL,
                target_node_id TEXT NOT NULL,
                relation TEXT NOT NULL,
                datenstand TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                first_utc TEXT,
                last_utc TEXT
            );
            CREATE INDEX idx_nodes_type ON nodes(node_type);
            CREATE INDEX idx_nodes_identity ON nodes(identity);
            CREATE INDEX idx_nodes_path ON nodes(path);
            CREATE INDEX idx_edges_source ON edges(source_node_id);
            CREATE INDEX idx_edges_target ON edges(target_node_id);
            CREATE INDEX idx_edges_relation ON edges(relation);
            CREATE INDEX idx_edges_last_utc ON edges(last_utc);
            """
        )
        connection.executemany(
            "INSERT INTO nodes VALUES (?,?,?,?,?,?,?)",
            [
                (
                    row["node_id"],
                    row["node_type"],
                    row["identity"],
                    row["label"],
                    row["path"],
                    row["datenstand"],
                    json.dumps(row["metadata"], ensure_ascii=False),
                )
                for row in nodes.values()
            ],
        )
        connection.executemany(
            "INSERT INTO edges VALUES (?,?,?,?,?,?,?,?)",
            [
                (
                    row["edge_id"],
                    row["source_node_id"],
                    row["target_node_id"],
                    row["relation"],
                    row["datenstand"],
                    json.dumps(row["evidence"], ensure_ascii=False),
                    row.get("first_utc"),
                    row.get("last_utc"),
                )
                for row in edge_rows
            ],
        )
        connection.commit()
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise RuntimeError("Beziehungsregister-Integrität fehlgeschlagen")
    finally:
        connection.close()
    os.replace(temp_path, relation_db)
    summary = {
        "schema_version": "1.0",
        "generated_utc": generated_utc,
        "node_count": len(nodes),
        "edge_count": len(edge_rows),
        "node_counts": dict(sorted(node_counts.items())),
        "relation_counts": dict(sorted(relation_counts.items())),
        "database_path": str(relation_db),
        "urbewohner": urbewohner_summary,
        "einschraenkung": "Nur belegte Pfad-, Deklarations-, History- und exakte Erwähnungsbeziehungen werden als Kanten gespeichert. Semantische Nähe allein erzeugt keine Kante.",
        "begriffe": {
            "beziehungskoerper": "node_count HIER meint ausschliesslich Elemente mit mindestens einer belegten Kante -- Groessenordnung Tausende.",
            "bestandskoerper": "Die Gesamtzahl aller indizierten Pfade steht separat in ATLAS_STATUS.json unter scan.path_count -- Groessenordnung Hunderttausende. Nicht dasselbe wie node_count hier, auch wenn beides umgangssprachlich Knoten genannt wird.",
            "herkunftsgrad": "Bereits vorhanden als datenstand-Feld an jedem consensus/conflict-Knoten, entspricht der CONSENSUS_CLASSES-Reihenfolge DANIEL_EXPLIZIT_GESETZT bis UNBEKANNT -- kein neues Feld, nur diese Benennung ist neu (2026-08-02).",
            "ruhender_widerspruch": "Der Knotentyp conflict existiert im Schema und ist per atlas_record_conflict/atlas_conflicts voll funktionsfaehig, aber Stand 2026-08-02 leer (0 Eintraege) -- vorbereitet, nicht ungenutzt wegen eines Fehlers.",
            "anbindungsdichte_wirkdichte": "Am ai_stream-Knoten selbst gespeichert (metadata.anbindungsdichte = Sessionanzahl, metadata.wirkdichte = tatsaechliche TOUCHED_PROJECT/TOUCHED_FILE Kanten aus diesen Sessions) -- getrennt, weil Sessionanzahl allein (v.a. bei chatgpt) kein verlaessliches Aktivitaetsmass ist.",
            "festgelegt_am": "2026-08-01",
        },
    }
    atomic_json(relation_json, summary)
    project_relations: dict[str, dict[str, list[Any]]] = {
        project_id: defaultdict(list) for project_id in project_nodes
    }
    reverse_project_nodes = {node: project_id for project_id, node in project_nodes.items()}
    node_lookup = nodes
    for edge in edge_rows:
        source_project = reverse_project_nodes.get(edge["source_node_id"])
        target_project = reverse_project_nodes.get(edge["target_node_id"])
        project_id = source_project or target_project
        if not project_id:
            continue
        other_node_id = edge["target_node_id"] if source_project else edge["source_node_id"]
        other = node_lookup.get(other_node_id, {})
        project_relations[project_id][edge["relation"]].append(
            {
                "node_id": other_node_id,
                "node_type": other.get("node_type"),
                "label": other.get("label"),
                "path": other.get("path"),
                "datenstand": edge["datenstand"],
                "metadata": other.get("metadata") or {},
                "evidence": edge["evidence"],
            }
        )
    for project in projects:
        project_id = str(project["project_id"])
        relations = project_relations.get(project_id, {})
        project["relations"] = {key: value[:200] for key, value in sorted(relations.items())}
        project["relationship_counts"] = {key: len(value) for key, value in sorted(relations.items())}
        project["related_vaults"] = relations.get("CONTAINS_VAULT", [])
        project["related_services"] = relations.get("HAS_SERVICE", [])
        project["related_sessions"] = relations.get("TOUCHED_PROJECT", [])
        project["claims"] = relations.get("CLAIMS_PROJECT_OR_SUBTREE", [])
        project["validation_artifacts"] = relations.get("HAS_VALIDATION", [])
        project["validation_reports"] = [
            item
            for item in relations.get("HAS_VALIDATION", [])
            if ((item.get("metadata") or {}).get("artifact_class") in {"summary_report", "machine_result"})
            or any(
                token in str(item.get("label") or "").lower()
                for token in ("validierungsbericht", "validation_report", "final_validation", "result.json")
            )
        ]
        project["handoffs"] = relations.get("HANDOFF_RELATES_TO_PROJECT", [])
        project["ai_streams"] = relations.get("AI_STREAM_RELATES_TO_PROJECT", [])
        project["decisions"] = relations.get("HAS_CONSENSUS", [])
        project["conflicts"] = relations.get("HAS_CONFLICT", [])
    summary["claims"] = claim_rows
    summary["validations"] = validation_rows
    return projects, summary


def build_relational_layer(
    *,
    atlas_root: Path,
    path_db: Path,
    concept_db: Path,
    history_path: Path,
    projects: list[dict[str, Any]],
    vaults: list[dict[str, Any]],
    services: list[dict[str, Any]],
    streams: list[dict[str, Any]],
    history_snapshot: dict[str, Any],
    consensus_rows: list[dict[str, Any]],
    conflict_rows: list[dict[str, Any]],
    generated_utc: str,
    refresh_mode: str = "full",
) -> dict[str, Any]:
    relation_db = atlas_root / "BEZIEHUNGSREGISTER.sqlite"
    relation_json = atlas_root / "BEZIEHUNGSREGISTER.json"
    revision_path = atlas_root / "PROJEKTREVISIONEN.json"
    claim_path = atlas_root / "CLAIMREGISTER.json"
    validation_register_path = atlas_root / "VALIDIERUNGSREGISTER.json"
    handoff_root = atlas_root / "uebergaben"
    handoff_register_path = atlas_root / "UEBERGABEREGISTER.json"
    bridge_path = atlas_root / "AI_STROM_BRUECKEN.json"
    projects, revision_payload, project_changes = merge_project_revisions(
        projects=projects,
        path_db=path_db,
        revision_path=revision_path,
        generated_utc=generated_utc,
    )
    history_events = read_history_events(history_path)
    services = enrich_services(services)
    claims = load_claims(
        projects,
        Path("/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/claims"),
    )
    handoffs, handoff_by_session = build_handoffs(
        history_events=history_events,
        projects=projects,
        handoff_root=handoff_root,
        register_path=handoff_register_path,
        generated_utc=generated_utc,
    )
    session_rows = history_snapshot.get("sessions") or []
    for session in session_rows:
        session_id = str(session.get("session_id") or "")
        session["handoff"] = handoff_by_session.get(session_id)
        session["related_project_ids"] = sorted(
            {
                project_id
                for event in history_events
                if str(event.get("session_id") or "") == session_id
                for project_id in event_project_ids(event, projects)
            }
        )
    streams, bridge_payload, stream_changes = build_ai_bridges(
        streams=streams,
        projects=projects,
        history_events=history_events,
        concept_db=concept_db,
        bridge_path=bridge_path,
        generated_utc=generated_utc,
    )
    projects, relation_summary = build_relationship_layer(
        projects=projects,
        vaults=vaults,
        services=services,
        streams=streams,
        history_events=history_events,
        claims=claims,
        handoffs=handoffs,
        consensus_rows=consensus_rows,
        conflict_rows=conflict_rows,
        path_db=path_db,
        relation_db=relation_db,
        relation_json=relation_json,
        generated_utc=generated_utc,
        refresh_mode=refresh_mode,
    )
    claim_rows = relation_summary.pop("claims")
    validation_rows = relation_summary.pop("validations")
    atomic_json(claim_path, {"schema_version": "1.0", "generated_utc": generated_utc, "claims": claim_rows})
    atomic_json(
        validation_register_path,
        {"schema_version": "1.0", "generated_utc": generated_utc, "validations": validation_rows},
    )
    return {
        "projects": projects,
        "services": services,
        "streams": streams,
        "history": history_snapshot,
        "project_revisions": revision_payload,
        "project_changes": project_changes,
        "claims": read_json(claim_path, {}),
        "validations": read_json(validation_register_path, {}),
        "handoffs": {"schema_version": "1.0", "generated_utc": generated_utc, "handoffs": handoffs},
        "ai_bridges": bridge_payload,
        "stream_changes": stream_changes,
        "relationships": relation_summary,
        "paths": {
            "project_revisions": str(revision_path),
            "claims": str(claim_path),
            "validations": str(validation_register_path),
            "handoffs": str(handoff_register_path),
            "handoff_root": str(handoff_root),
            "ai_bridges": str(bridge_path),
            "relationships": str(relation_db),
            "relationship_summary": str(relation_json),
        },
    }


def query_relationships(
    *,
    relation_db: Path,
    query: str | None = None,
    node_type: str | None = None,
    relation: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    if not relation_db.exists():
        return {"ok": False, "error": f"Beziehungsregister fehlt: {relation_db}"}
    limit = max(1, min(int(limit), 500))
    connection = sqlite3.connect(relation_db)
    connection.row_factory = sqlite3.Row
    try:
        clauses = []
        params: list[Any] = []
        if query:
            clauses.append("(n.label LIKE ? OR n.path LIKE ? OR n.identity LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        if node_type:
            clauses.append("n.node_type=?")
            params.append(node_type)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        nodes = [dict(row) for row in connection.execute(f"SELECT * FROM nodes n{where} ORDER BY n.node_type,n.label LIMIT ?", (*params, limit))]
        for row in nodes:
            row["metadata"] = json.loads(row.pop("metadata_json") or "{}")
        node_ids = [row["node_id"] for row in nodes]
        edge_rows: list[dict[str, Any]] = []
        if node_ids:
            placeholders = ",".join("?" for _ in node_ids)
            edge_clauses = [f"(source_node_id IN ({placeholders}) OR target_node_id IN ({placeholders}))"]
            edge_params: list[Any] = node_ids + node_ids
            if relation:
                edge_clauses.append("relation=?")
                edge_params.append(relation)
            edge_params.append(limit * 10)
            for row in connection.execute(
                "SELECT * FROM edges WHERE " + " AND ".join(edge_clauses) + " ORDER BY relation LIMIT ?",
                edge_params,
            ):
                value = dict(row)
                value["evidence"] = json.loads(value.pop("evidence_json") or "[]")
                edge_rows.append(value)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
    finally:
        connection.close()
    return {
        "ok": integrity == "ok",
        "query": query,
        "node_type": node_type,
        "relation": relation,
        "nodes": nodes,
        "edges": edge_rows,
        "integrity": integrity,
        "einschraenkung": "Beziehungsfunde sind belegte Struktur-, Pfad-, Deklarations- oder Historykanten. Sie sind kein automatischer Konsens.",
    }


def handoff_state(register_path: Path, session_id: str | None = None, limit: int = 100) -> dict[str, Any]:
    payload = read_json(register_path, {"handoffs": []})
    rows = payload.get("handoffs") if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        rows = []
    if session_id:
        rows = [row for row in rows if row.get("source_session_id") == session_id]
    return {"ok": True, "count": len(rows), "handoffs": rows[: max(1, min(int(limit), 500))]}
