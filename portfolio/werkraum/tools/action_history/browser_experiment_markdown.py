from __future__ import annotations

import hashlib
import json
import os
import tempfile
import textwrap
from pathlib import Path
from typing import Any

from .browser_experiment_conversation import conversation_export_from_primary_data

RENDERER_VERSION = "1.0-human-readable-experiment-export"
HUMAN_MARKDOWN_FILES = (
    "ZEITSPUR.md",
    "TEILNEHMER.md",
    "PHASEN.md",
    "NACHRICHTEN_UND_EXPOSITIONEN.md",
    "ANNOTATIONEN.md",
    "ABLAUF_GEGEN_SELBSTERZAEHLUNG.md",
    "LUECKEN_UND_UNGEKLAERTE_HERKUNFT.md",
)
MAX_MARKDOWN_LINE_LENGTH = 112
CONVERSATION_FILE_NAME = "GESPRAECH_1ZU1.md"
COMBINED_CONVERSATION_FILE_NAME = "ALLE_GESPRAECHE_1ZU1.md"


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content.rstrip() + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
        os.chmod(path, 0o600)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def _atomic_json(path: Path, value: Any) -> None:
    _atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def _label(value: Any) -> str:
    return str(value or "–").replace("\n", " ").strip() or "–"


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, (int, float)):
        return str(value)
    return str(value).replace("\r\n", "\n").replace("\r", "\n")


def _wrapped_lines(text: str, *, prefix: str, continuation: str) -> list[str]:
    paragraphs = text.split("\n") or [""]
    lines: list[str] = []
    for index, paragraph in enumerate(paragraphs):
        if not paragraph:
            lines.append(prefix if index == 0 else continuation.rstrip())
            continue
        wrapper = textwrap.TextWrapper(
            width=MAX_MARKDOWN_LINE_LENGTH,
            initial_indent=prefix if index == 0 else continuation,
            subsequent_indent=continuation,
            break_long_words=True,
            break_on_hyphens=True,
            replace_whitespace=False,
            drop_whitespace=True,
        )
        lines.extend(wrapper.wrap(paragraph) or [prefix])
    return lines


def _render_value(lines: list[str], key: str, value: Any, *, depth: int = 0) -> None:
    indent = "  " * depth
    clean_key = _label(key)
    if isinstance(value, dict):
        if not value:
            lines.append(f"{indent}- **{clean_key}:** {{}}")
            return
        lines.append(f"{indent}- **{clean_key}:**")
        for child_key, child_value in value.items():
            _render_value(lines, str(child_key), child_value, depth=depth + 1)
        return
    if isinstance(value, list):
        if not value:
            lines.append(f"{indent}- **{clean_key}:** []")
            return
        lines.append(f"{indent}- **{clean_key}:**")
        for index, item in enumerate(value, start=1):
            if isinstance(item, dict):
                lines.append(f"{indent}  - **Eintrag {index}:**")
                for child_key, child_value in item.items():
                    _render_value(lines, str(child_key), child_value, depth=depth + 2)
            elif isinstance(item, list):
                _render_value(lines, f"Eintrag {index}", item, depth=depth + 1)
            else:
                text = _scalar(item)
                lines.extend(_wrapped_lines(text, prefix=f"{indent}  - ", continuation=f"{indent}    "))
        return
    text = _scalar(value)
    lines.extend(
        _wrapped_lines(
            text,
            prefix=f"{indent}- **{clean_key}:** ",
            continuation=f"{indent}  ",
        )
    )


def _header(title: str, state: dict[str, Any], timeline: dict[str, Any]) -> list[str]:
    return [
        f"# {title}",
        "",
        f"**Versuch:** {_label(state.get('name'))}",
        "",
        f"**Experiment-ID:** `{_label(state.get('experiment_id'))}`",
        "",
        f"**Status:** {_label(state.get('status'))}",
        "",
        f"**Datenstand:** {_label(timeline.get('generated_utc') or state.get('updated_utc'))}",
        "",
        "Diese Markdown-Datei ist eine deterministisch erzeugte menschliche Ansicht der im selben Export enthaltenen",
        "JSON-/JSONL-Primärdaten. Sie ersetzt keine Primärquelle.",
        "",
    ]


def _ordered_records(mapping: dict[str, Any], order: list[str] | None = None) -> list[tuple[str, dict[str, Any]]]:
    result: list[tuple[str, dict[str, Any]]] = []
    seen: set[str] = set()
    for key in order or []:
        item = mapping.get(key)
        if isinstance(item, dict):
            result.append((str(key), item))
            seen.add(str(key))
    for key in sorted(mapping):
        if str(key) in seen:
            continue
        item = mapping.get(key)
        if isinstance(item, dict):
            result.append((str(key), item))
    return result


def _section_records(lines: list[str], title: str, records: list[tuple[str, dict[str, Any]]], id_label: str) -> None:
    lines.extend([f"## {title}", ""])
    if not records:
        lines.extend(["Keine Einträge vorhanden.", ""])
        return
    for index, (record_id, record) in enumerate(records, start=1):
        lines.extend([f"### {index}. {_label(record.get('name') or record.get('alias') or record_id)}", ""])
        _render_value(lines, id_label, record_id)
        for key, value in record.items():
            if str(key) == id_label:
                continue
            _render_value(lines, str(key), value)
        lines.append("")


def _render_timeline(state: dict[str, Any], timeline: dict[str, Any]) -> str:
    lines = _header("Zeitspur", state, timeline)
    lines.extend([
        "## Ordnungsregel",
        "",
        "Die Einträge folgen der im Primärkörper gespeicherten Zeitspur. Quellenübergreifende Gleichzeitigkeit wird",
        "nicht nachträglich als sichere Reihenfolge ausgegeben.",
        "",
        "## Chronologische Ereignisse",
        "",
    ])
    events = timeline.get("events") if isinstance(timeline.get("events"), list) else []
    if not events:
        lines.extend(["Keine Zeitspureinträge vorhanden.", ""])
    for index, event in enumerate(events, start=1):
        if not isinstance(event, dict):
            continue
        timestamp = _label(event.get("reported_time_utc") or event.get("timestamp_utc"))
        source = _label(event.get("source"))
        event_type = _label(event.get("event_type") or event.get("summary"))
        lines.extend([f"### {index}. {timestamp} · {source} · {event_type}", ""])
        for key, value in event.items():
            _render_value(lines, str(key), value)
        lines.append("")
    if timeline.get("participant_errors"):
        lines.extend(["## Projektionsfehler", ""])
        _render_value(lines, "participant_errors", timeline.get("participant_errors"))
        lines.append("")
    return "\n".join(lines)


def _render_participants(state: dict[str, Any], timeline: dict[str, Any], source_refs: list[dict[str, Any]]) -> str:
    lines = _header("Teilnehmer", state, timeline)
    participants = state.get("participants") if isinstance(state.get("participants"), dict) else {}
    _section_records(lines, "Teilnehmerbestand", _ordered_records(participants, state.get("participant_order") or []), "participant_id")
    lines.extend(["## Quellenzuordnungen", ""])
    _render_value(lines, "source_references", source_refs)
    lines.append("")
    return "\n".join(lines)


def _render_phases(state: dict[str, Any], timeline: dict[str, Any]) -> str:
    lines = _header("Phasen, Impulse und Snapshots", state, timeline)
    phases = state.get("phases") if isinstance(state.get("phases"), dict) else {}
    stimuli = state.get("stimuli") if isinstance(state.get("stimuli"), dict) else {}
    snapshots = state.get("snapshots") if isinstance(state.get("snapshots"), dict) else {}
    _section_records(lines, "Phasen", _ordered_records(phases, state.get("phase_order") or []), "phase_id")
    _section_records(lines, "Impulse", _ordered_records(stimuli), "stimulus_id")
    _section_records(lines, "Versiegelte Snapshots", _ordered_records(snapshots), "snapshot_id")
    return "\n".join(lines)


def _render_messages(state: dict[str, Any], timeline: dict[str, Any]) -> str:
    lines = _header("Nachrichten und Expositionen", state, timeline)
    messages = state.get("messages") if isinstance(state.get("messages"), dict) else {}
    exposures = state.get("exposures") if isinstance(state.get("exposures"), dict) else {}
    influences = state.get("influences") if isinstance(state.get("influences"), dict) else {}
    _section_records(lines, "Nachrichten mit getrennten Zuständen", _ordered_records(messages), "message_id")
    _section_records(lines, "Expositionen", _ordered_records(exposures), "exposure_id")
    _section_records(lines, "Herkunfts- und Einflusszuordnungen", _ordered_records(influences), "influence_id")
    return "\n".join(lines)


def _render_annotations(state: dict[str, Any], timeline: dict[str, Any]) -> str:
    lines = _header("Annotationen", state, timeline)
    annotations = state.get("annotations") if isinstance(state.get("annotations"), dict) else {}
    controls = state.get("control_conditions") if isinstance(state.get("control_conditions"), dict) else {}
    _section_records(lines, "Daniels Annotationen", _ordered_records(annotations), "annotation_id")
    _section_records(lines, "Manuell gesetzte Kontrollbedingungen", _ordered_records(controls), "key")
    return "\n".join(lines)


def _render_comparisons(state: dict[str, Any], timeline: dict[str, Any]) -> str:
    lines = _header("Ablauf gegen Selbsterzählung", state, timeline)
    reports = state.get("self_reports") if isinstance(state.get("self_reports"), dict) else {}
    comparisons = state.get("comparisons") if isinstance(state.get("comparisons"), dict) else {}
    _section_records(lines, "Selbsterzählungen", _ordered_records(reports), "self_report_id")
    _section_records(lines, "Regenerierbare Vergleiche", _ordered_records(comparisons), "comparison_id")
    lines.extend([
        "## Wahrheitsgrenze",
        "",
        "Selbsterzählungen sind subjektive spätere Berichte. Die Vergleichskörper ordnen Verweise auf Ablaufdaten",
        "zu, erzeugen aber keine psychologische Diagnose und keine nachträgliche objektive Innenansicht.",
        "",
    ])
    return "\n".join(lines)


def _load_participant_gaps(export_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    participants_root = export_root / "participants"
    if not participants_root.exists():
        return rows
    for participant_dir in sorted(path for path in participants_root.iterdir() if path.is_dir()):
        for gap in _read_jsonl(participant_dir / "capture_gaps.jsonl"):
            rows.append({"participant_directory": participant_dir.name, **gap})
    return rows


def _render_gaps(
    export_root: Path,
    state: dict[str, Any],
    timeline: dict[str, Any],
    experiment_errors: list[dict[str, Any]],
    source_refs: list[dict[str, Any]],
) -> str:
    lines = _header("Lücken und ungeklärte Herkunft", state, timeline)
    events = timeline.get("events") if isinstance(timeline.get("events"), list) else []
    uncertain_classes = {
        "strongly_derived",
        "weakly_derived",
        "similarity_only",
        "unknown",
        "unattributed_context_possible",
    }
    uncertain = [
        item for item in events
        if isinstance(item, dict)
        and (
            item.get("gap")
            or item.get("influence_class") in uncertain_classes
            or item.get("cross_source_order_certainty") == "parallel_or_uncertain"
        )
    ]
    participant_gaps = _load_participant_gaps(export_root)
    source_errors = [item for item in source_refs if isinstance(item, dict) and item.get("error")]
    unread_messages = []
    for message_id, message in (state.get("messages") or {}).items():
        if isinstance(message, dict) and "read_confirmed" not in (message.get("states") or {}):
            unread_messages.append({"message_id": message_id, "states": message.get("states"), "recipient_participant_ids": message.get("recipient_participant_ids")})
    unread_exposures = []
    for exposure_id, exposure in (state.get("exposures") or {}).items():
        if isinstance(exposure, dict) and not exposure.get("read_utc"):
            unread_exposures.append({"exposure_id": exposure_id, **exposure})

    lines.extend(["## Unsichere oder lückenbehaftete Zeitspureinträge", ""])
    _render_value(lines, "events", uncertain)
    lines.extend(["", "## Erfasste Browserlücken", ""])
    _render_value(lines, "capture_gaps", participant_gaps)
    lines.extend(["", "## Fehler beim Aufbau der Versuchsansicht", ""])
    _render_value(lines, "experiment_errors", experiment_errors)
    _render_value(lines, "participant_projection_errors", timeline.get("participant_errors") or [])
    _render_value(lines, "source_reference_errors", source_errors)
    lines.extend(["", "## Verfügbar, aber nicht technisch als gelesen bestätigt", ""])
    _render_value(lines, "messages_without_read_confirmation", unread_messages)
    _render_value(lines, "exposures_without_read_confirmation", unread_exposures)
    lines.extend([
        "",
        "## Grenze",
        "",
        "Nicht beobachtbare Plattformmechanismen werden weder bestätigt noch ausgeschlossen. Eine offene Herkunftsklasse",
        "ist kein Beweis für einen tatsächlichen Kontextübersprung.",
        "",
    ])
    return "\n".join(lines)


def _machine_source_paths(export_root: Path) -> list[Path]:
    paths: list[Path] = []
    excluded = {"MANIFEST.json", "MARKDOWN_REPRODUKTION.json"}
    for path in sorted(export_root.rglob("*")):
        if not path.is_file() or path.name in excluded:
            continue
        if path.suffix.lower() in {".json", ".jsonl"}:
            paths.append(path)
    return paths


def markdown_quality_report(contents: dict[str, str]) -> dict[str, Any]:
    files: dict[str, Any] = {}
    total_overlong = 0
    for name, content in sorted(contents.items()):
        lines = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        overlong = [index for index, line in enumerate(lines, start=1) if len(line) > MAX_MARKDOWN_LINE_LENGTH]
        total_overlong += len(overlong)
        files[name] = {
            "line_count": len(lines),
            "max_line_length": max((len(line) for line in lines), default=0),
            "overlong_line_count": len(overlong),
            "overlong_line_numbers": overlong[:50],
            "has_headings": any(line.startswith("# ") for line in lines),
            "has_normal_lf_linebreaks": "\r" not in content,
        }
    return {
        "max_allowed_line_length": MAX_MARKDOWN_LINE_LENGTH,
        "file_count": len(contents),
        "total_overlong_line_count": total_overlong,
        "directly_readable": total_overlong == 0 and all(item["has_headings"] and item["has_normal_lf_linebreaks"] for item in files.values()),
        "files": files,
    }


def build_human_readable_export(export_root: str | Path, *, write: bool = True) -> dict[str, Any]:
    root = Path(export_root)
    state = _read_json(root / "EXPERIMENT.json", {})
    timeline = _read_json(root / "EXPERIMENT_TIMELINE.json", {})
    experiment_errors = _read_jsonl(root / "EXPERIMENT_ERRORS.jsonl")
    source_refs = _read_json(root / "SOURCE_REFERENCES.json", [])
    if not isinstance(state, dict) or not state.get("experiment_id"):
        raise ValueError("EXPERIMENT.json fehlt oder enthält keine experiment_id")
    if not isinstance(timeline, dict) or timeline.get("experiment_id") != state.get("experiment_id"):
        raise ValueError("EXPERIMENT_TIMELINE.json verweist nicht auf denselben Versuch")
    if not isinstance(source_refs, list):
        source_refs = []
    conversation_result = conversation_export_from_primary_data(root, state, write=False)

    contents = {
        "ZEITSPUR.md": _render_timeline(state, timeline),
        "TEILNEHMER.md": _render_participants(state, timeline, source_refs),
        "PHASEN.md": _render_phases(state, timeline),
        "NACHRICHTEN_UND_EXPOSITIONEN.md": _render_messages(state, timeline),
        "ANNOTATIONEN.md": _render_annotations(state, timeline),
        "ABLAUF_GEGEN_SELBSTERZAEHLUNG.md": _render_comparisons(state, timeline),
        "LUECKEN_UND_UNGEKLAERTE_HERKUNFT.md": _render_gaps(root, state, timeline, experiment_errors, source_refs),
    }
    quality = markdown_quality_report(contents)
    if not quality["directly_readable"]:
        raise ValueError(f"Markdown-Qualitätsprüfung fehlgeschlagen: {quality}")

    source_files = [
        {
            "path": str(path.relative_to(root)),
            "sha256": _sha_file(path),
            "bytes": path.stat().st_size,
        }
        for path in _machine_source_paths(root)
    ]
    markdown_files = [
        {
            "path": name,
            "sha256": hashlib.sha256((content.rstrip() + "\n").encode("utf-8")).hexdigest(),
            "bytes": len((content.rstrip() + "\n").encode("utf-8")),
            "kind": "thematic_human_view",
        }
        for name, content in sorted(contents.items())
    ]
    markdown_files.extend(
        {
            "path": name,
            "sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
            "bytes": len(content.encode("utf-8")),
            "kind": "exact_visible_conversation",
        }
        for name, content in sorted(conversation_result.get("contents", {}).items())
    )
    reproduction = {
        "schema_version": RENDERER_VERSION,
        "experiment_id": state.get("experiment_id"),
        "experiment_name": state.get("name"),
        "source_of_truth": "JSON/JSONL files in the same export",
        "renderer": "tools.action_history.browser_experiment_markdown.build_human_readable_export",
        "deterministic_from_primary_export_files": True,
        "important_events_omitted_intentionally": False,
        "timeline_event_count_in_json": len(timeline.get("events") or []),
        "timeline_event_count_rendered_in_ZEITSPUR_md": len(timeline.get("events") or []),
        "machine_source_files": source_files,
        "markdown_files": markdown_files,
        "conversation_exports": {
            "participants": conversation_result.get("participants", []),
            "combined_conversation_generated": conversation_result.get("combined_conversation_generated"),
            "combined_conversation_path": conversation_result.get("combined_conversation_path"),
            "combined_conversation_reason": conversation_result.get("combined_conversation_reason"),
            "authoritative_multisession_form": conversation_result.get("authoritative_multisession_form"),
            "content_is_exact_visible_message_text": True,
            "technical_metadata_added_to_conversation": False,
        },
        "quality": quality,
    }

    if write:
        for name, content in contents.items():
            _atomic_text(root / name, content)
        conversation_export_from_primary_data(root, state, write=True)
        _atomic_json(root / "MARKDOWN_REPRODUKTION.json", reproduction)

    return {
        "ok": True,
        "experiment_id": state.get("experiment_id"),
        "contents": contents,
        "reproduction": reproduction,
        "conversation_exports": {
            "participants": conversation_result.get("participants", []),
            "combined_conversation_generated": conversation_result.get("combined_conversation_generated"),
            "combined_conversation_reason": conversation_result.get("combined_conversation_reason"),
        },
        "quality": quality,
    }
