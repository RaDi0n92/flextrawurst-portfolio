from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

CONVERSATION_FILE_NAME = "GESPRAECH_1ZU1.md"
COMBINED_CONVERSATION_FILE_NAME = "ALLE_GESPRAECHE_1ZU1.md"


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


def _atomic_text_exact(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
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


def _latest_by_key(source: list[dict[str, Any]], *, historical_mode: bool) -> list[dict[str, Any]]:
    order: list[tuple[Any, ...]] = []
    selected: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in source:
        role = str(row.get("role") or "")
        dom_id = str(row.get("dom_id") or "").strip()
        turn_id = str(row.get("turn_id") or "").strip()
        message_id = str(row.get("message_id") or row.get("event_id") or row.get("_source_index"))
        # A manual historical import can see the same DOM window more than once
        # while somebody scrolls.  Its recorded event id is the stable identity;
        # a fallback DOM id such as "turn-3" is only local to that window and
        # would otherwise overwrite a different, real message.
        if historical_mode and message_id:
            key = ("historical_event", message_id, role)
        elif dom_id:
            key = (
                "historical" if historical_mode else "live",
                "" if historical_mode else turn_id,
                dom_id,
                role,
            )
        else:
            key = ("message", message_id, role)
        if key not in selected:
            order.append(key)
        selected[key] = row
    return [selected[key] for key in order]


def _historical_order_key(row: dict[str, Any]) -> tuple[Any, ...]:
    """Use the recorder's global first-seen order, never viewport-local ordinal."""
    evidence = row.get("history_evidence") if isinstance(row.get("history_evidence"), dict) else {}
    provider_position = row.get("provider_position")
    if not isinstance(provider_position, (int, float)):
        provider_position = evidence.get("provider_position")
    if isinstance(provider_position, (int, float)):
        # Gemini exposes an absolute position in its chat scroller.  It is the
        # conversation order; capture_order remains the independent first-seen
        # proof and is only the fallback for older captures/providers.
        return (0, float(provider_position), int(row.get("_source_index") or 0))
    for candidate in (row.get("capture_order"), evidence.get("capture_order")):
        if isinstance(candidate, int):
            return (1, candidate, int(row.get("_source_index") or 0))
    # Older captures lack capture_order.  Keep a conservative fallback that
    # follows first visible scroll position before timestamp/source order.
    first_scroll = evidence.get("first_seen_scroll_y")
    try:
        scroll_key = float(first_scroll)
    except (TypeError, ValueError):
        scroll_key = float("inf")
    return (2, scroll_key, str(evidence.get("first_seen_utc") or ""), int(row.get("_source_index") or 0))


def canonical_conversation_messages(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    usable: list[dict[str, Any]] = []
    ignored_roles = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            continue
        role = str(row.get("role") or "").strip().lower()
        if role not in {"user", "assistant"}:
            ignored_roles += 1
            continue
        content = row.get("content")
        if not isinstance(content, str):
            continue
        copied = dict(row)
        copied["_source_index"] = index
        usable.append(copied)

    historical = [row for row in usable if row.get("capture_kind") == "historical_import"]
    live = [row for row in usable if row.get("capture_kind") != "historical_import"]
    latest_historical = _latest_by_key(historical, historical_mode=True)
    latest_live = _latest_by_key(live, historical_mode=False)

    historical_exact = {
        (str(row.get("dom_id") or ""), str(row.get("role") or ""), row.get("content"))
        for row in latest_historical
        if row.get("dom_id")
    }
    combined = list(latest_historical)
    for row in latest_live:
        exact_key = (str(row.get("dom_id") or ""), str(row.get("role") or ""), row.get("content"))
        if row.get("dom_id") and exact_key in historical_exact:
            continue
        combined.append(row)

    if latest_historical:
        combined.sort(key=_historical_order_key)
    else:
        combined.sort(key=lambda row: int(row.get("_source_index") or 0))

    seen_exact: set[tuple[str, str, str]] = set()
    final: list[dict[str, Any]] = []
    exact_duplicates = 0
    for row in combined:
        if row.get("capture_kind") == "historical_import":
            # Repeating an identical sentence in a long conversation is valid.
            # The recorded event identity distinguishes it from a duplicate
            # observation of the same visible message.
            key = ("historical_event", str(row.get("event_id") or row.get("_source_index")), "")
        else:
            key = (
                str(row.get("role") or ""),
                str(row.get("content") or ""),
                str(row.get("turn_id") or ""),
            )
        if key in seen_exact:
            exact_duplicates += 1
            continue
        seen_exact.add(key)
        final.append(row)

    metadata = {
        "source_message_count": len(rows),
        "usable_visible_message_count": len(usable),
        "selected_message_count": len(final),
        "ignored_non_conversation_role_count": ignored_roles,
        "superseded_or_duplicate_variant_count": len(usable) - len(final),
        "exact_duplicate_count": exact_duplicates,
        "historical_import_present": bool(latest_historical),
        "ordering_rule": (
            "latest visible DOM variant, then recorder-global capture_order; "
            "older captures fall back to first_seen_scroll_y, never viewport-local ordinal"
        ),
    }
    return final, metadata


def render_conversation_exact(messages: list[dict[str, Any]], assistant_label: str) -> str:
    blocks: list[str] = []
    for row in messages:
        role = str(row.get("role") or "").strip().lower()
        content = row.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        speaker = "Daniel" if role == "user" else assistant_label
        blocks.append(f"{speaker}:\n\n{content}")
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def conversation_export_from_primary_data(
    export_root: str | Path,
    state: dict[str, Any],
    *,
    write: bool = True,
) -> dict[str, Any]:
    root = Path(export_root)
    participants_root = root / "participants"
    participants = state.get("participants") if isinstance(state.get("participants"), dict) else {}
    contents: dict[str, str] = {}
    records: list[dict[str, Any]] = []

    for participant_id in state.get("participant_order") or sorted(participants):
        participant = participants.get(participant_id)
        if not isinstance(participant, dict) or participant.get("removed_utc"):
            continue
        participant_dir = participants_root / str(participant_id)
        source_path = participant_dir / "messages.jsonl"
        source_rows = _read_jsonl(source_path)
        selected, selection = canonical_conversation_messages(source_rows)
        assistant_label = (
            str(participant.get("alias") or participant.get("chat_title") or "ChatGPT")
            .replace("\r", " ")
            .replace("\n", " ")
            .strip()
            or "ChatGPT"
        )
        content = render_conversation_exact(selected, assistant_label)
        relative_path = str(Path("participants") / str(participant_id) / CONVERSATION_FILE_NAME)
        contents[relative_path] = content
        records.append(
            {
                "participant_id": participant_id,
                "participant_alias": assistant_label,
                "source_messages_path": str(source_path.relative_to(root)),
                "source_messages_sha256": _sha_file(source_path) if source_path.exists() else None,
                "conversation_path": relative_path,
                "conversation_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                "speaker_labels_only_metadata_added": True,
                "timestamps_or_ids_added_to_conversation": False,
                "content_characters_changed": False,
                "selected_content_sha256_sequence": [
                    hashlib.sha256(str(row.get("content") or "").encode("utf-8")).hexdigest()
                    for row in selected
                ],
                "selected_roles": [str(row.get("role") or "") for row in selected],
                **selection,
            }
        )

    combined_generated = False
    combined_reason = "Nicht erzeugt: Exakte gemeinsame Reihenfolge paralleler Sitzungen wird nicht behauptet."
    if len(records) == 1:
        only = records[0]
        contents[CONVERSATION_FILE_NAME] = contents[only["conversation_path"]]
        combined_reason = "Einzelteilnehmer: Root-Gespräch ist identisch mit dem Teilnehmerdokument."

    if write:
        for relative_path, content in contents.items():
            _atomic_text_exact(root / relative_path, content)

    return {
        "ok": True,
        "contents": contents,
        "participants": records,
        "combined_conversation_generated": combined_generated,
        "combined_conversation_path": COMBINED_CONVERSATION_FILE_NAME if combined_generated else None,
        "combined_conversation_reason": combined_reason,
        "authoritative_multisession_form": "separate participant conversation documents",
    }
