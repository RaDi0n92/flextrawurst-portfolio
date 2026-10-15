#!/usr/bin/env python3
"""Export one Codex rollout's visible user/assistant messages verbatim.

The rollout is the source of truth.  This tool does not summarize, normalize,
deduplicate, or ask a model to rewrite anything.  It writes a machine-readable
JSONL copy and a human-readable Markdown transcript beside it.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def text_from_content(content: list[dict[str, object]]) -> str:
    parts: list[str] = []
    for item in content:
        value = item.get("text")
        if isinstance(value, str):
            parts.append(value)
    return "\n".join(parts)


def export(
    source: Path,
    out_dir: Path,
    session_id: str,
    *,
    start_ordinal: int = 1,
    stem_suffix: str = "",
) -> tuple[Path, Path, int]:
    records: list[dict[str, object]] = []
    with source.open("r", encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            if row.get("type") != "response_item":
                continue
            payload = row.get("payload")
            if not isinstance(payload, dict) or payload.get("type") != "message":
                continue
            role = payload.get("role")
            if role not in {"user", "assistant"}:
                continue
            content = payload.get("content")
            if not isinstance(content, list):
                continue
            records.append(
                {
                    "ordinal": len(records) + 1,
                    "timestamp": row.get("timestamp"),
                    "id": payload.get("id"),
                    "role": role,
                    "content": content,
                    "text": text_from_content(content),
                }
            )

    records = [record for record in records if int(record["ordinal"]) >= start_ordinal]
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = f"codex-session-{session_id}{stem_suffix}"
    jsonl_path = out_dir / f"{stem}-messages.jsonl"
    markdown_path = out_dir / f"{stem}-messages.md"

    with jsonl_path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")

    with markdown_path.open("w", encoding="utf-8") as handle:
        handle.write("# Codex-Sitzung — Wortlaut-Export\n\n")
        handle.write("Dieser Export enthält die sichtbaren User-/Assistant-Nachrichten aus der lokalen Rollout-Quelle. Die Nachrichtentexte wurden nicht umformuliert. Die JSONL-Datei ist die maschinenlesbare Primärkopie.\n\n")
        handle.write(f"- Session: `{session_id}`\n")
        handle.write(f"- Quelle: `{source}`\n")
        handle.write(f"- Exportzeitpunkt: `{datetime.now(timezone.utc).isoformat()}`\n")
        handle.write(f"- Nachrichten: `{len(records)}`\n")
        handle.write(f"- Start im vollständigen Export: `#{start_ordinal}`\n\n")
        handle.write("Hinweis: Toolausgaben, interne Denkprotokolle und System-/Developer-Nachrichten sind nicht Teil dieses sichtbaren Gesprächstranskripts.\n\n---\n\n")
        for record in records:
            role = str(record["role"]).upper()
            timestamp = record.get("timestamp", "")
            message_id = record.get("id", "")
            handle.write(f"## {record['ordinal']:04d} — {role} — {timestamp}\n\n")
            handle.write(f"<!-- message_id: {message_id} -->\n\n")
            handle.write(str(record["text"]))
            handle.write("\n\n---\n\n")

    return jsonl_path, markdown_path, len(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("session_id")
    parser.add_argument("--start-ordinal", type=int, default=1)
    parser.add_argument("--stem-suffix", default="")
    args = parser.parse_args()
    jsonl_path, markdown_path, count = export(
        args.source,
        args.out_dir,
        args.session_id,
        start_ordinal=args.start_ordinal,
        stem_suffix=args.stem_suffix,
    )
    print(f"exported={count}")
    print(f"jsonl={jsonl_path}")
    print(f"markdown={markdown_path}")


if __name__ == "__main__":
    main()
