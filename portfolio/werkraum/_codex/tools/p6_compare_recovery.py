#!/usr/bin/env python3
"""Conservative comparison of one P6 visible-text recovery with old VPS data.

The old folder is read-only. The comparison is written beside the new recovery
run and never consolidates or rewrites either source.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "audit-20260813T-p6-recovery-reise-v2"
CID = "6a70e4ad-7560-83ed-a69f-78381bb59f4e"
RUN = Path("/root/werkraum/_gpt/ui_visible_conversations/audit_runs") / RUN_ID
RECOVERY = RUN / f"01-{CID}.json"
OLD = Path("/root/werkraum/_gpt/ui_visible_conversations/2026-08-03__Neuer-Risswandler-entwickelt__6a70e4ad7560-5e33ad0f89")
OLD_MESSAGES = OLD / "messages.jsonl"
OUT = RUN / "manifest.json"


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(text: str) -> str:
    return " ".join((text or "").split())


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def old_id(message: dict) -> str | None:
    value = message.get("dom_id") or message.get("data_message_id")
    if not value:
        return None
    return str(value).removeprefix("message:")


def write(value: dict) -> None:
    tmp = OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(OUT)


def main() -> None:
    recovery = json.loads(RECOVERY.read_text(encoding="utf-8"))
    old = [json.loads(line) for line in OLD_MESSAGES.read_text(encoding="utf-8").splitlines() if line.strip()]

    by_id: dict[str, list[tuple[int, dict]]] = defaultdict(list)
    by_content: dict[tuple[str, str], list[tuple[int, dict]]] = defaultdict(list)
    for index, message in enumerate(old, 1):
        key = (message.get("role", "unknown"), normalize(message.get("content", "")))
        by_content[key].append((index, message))
        ident = old_id(message)
        if ident:
            by_id[ident].append((index, message))

    comparisons = []
    counts = defaultdict(int)
    matched_old_occurrences: set[int] = set()
    recovery_ids: set[str] = set()
    for record in recovery.get("records", []):
        stable_id = record.get("stable_id")
        role = record.get("role", "unknown")
        text = record.get("normalized_text", "")
        candidates = by_id.get(stable_id, []) if stable_id else by_content[(role, text)]
        entry = {
            "recovery_run_id": RUN_ID,
            "identity": record.get("identity"),
            "stable_id": stable_id,
            "role": role,
            "recovery_text_sha256": record.get("text_sha256") or sha(text),
            "recovery_text_length": len(text),
            "historical_candidates": [index for index, _ in candidates],
        }
        if stable_id:
            recovery_ids.add(stable_id)
        if not candidates:
            entry["classification"] = "missing-vps"
            counts["missing-vps"] += 1
        elif len(candidates) > 1:
            exact = [
                (index, message)
                for index, message in candidates
                if message.get("role", "unknown") == role and normalize(message.get("content", "")) == text
            ]
            if exact and len(exact) == len(candidates):
                entry["classification"] = "ambiguous-duplicate-history"
                entry["matched_exact_occurrences"] = [index for index, _ in exact]
                matched_old_occurrences.update(index for index, _ in exact)
            else:
                entry["classification"] = "ambiguous-text-variant"
            counts[entry["classification"]] += 1
        else:
            index, message = candidates[0]
            matched_old_occurrences.add(index)
            historical_role = message.get("role", "unknown")
            historical_text = normalize(message.get("content", ""))
            if historical_role != role:
                entry["classification"] = "role-mismatch"
                counts["role-mismatch"] += 1
            elif historical_text != text:
                entry["classification"] = "changed-text"
                entry["historical_text_sha256"] = sha(historical_text)
                entry["historical_text_length"] = len(historical_text)
                counts["changed-text"] += 1
            else:
                entry["classification"] = "match"
                counts["match"] += 1
        comparisons.append(entry)

    old_stable_ids = set(by_id)
    missing_live_ids = sorted(old_stable_ids - recovery_ids)
    for ident in missing_live_ids:
        counts["missing-live"] += 1

    result = {
        "run_id": RUN_ID,
        "phase": "P6",
        "status": "p6_historical_partial",
        "comparison_scope": "Reise Dauerloop / visible raw-text recovery versus old VPS messages.jsonl",
        "recovery_run_id": RUN_ID,
        "sources": {
            "recovery_file": str(RECOVERY),
            "old_vps_folder": str(OLD),
            "old_vps_folder_modified": False,
            "recorder_start_clicked": False,
            "recorder_finish_clicked": False,
        },
        "full_text_comparison": True,
        "old_message_count": len(old),
        "recovery_record_count": len(recovery.get("records", [])),
        "old_stable_id_count": len(old_stable_ids),
        "recovery_stable_id_count": len(recovery_ids),
        "old_stable_ids_missing_live_count": len(missing_live_ids),
        "old_stable_ids_missing_live": missing_live_ids,
        "matched_old_occurrence_count": len(matched_old_occurrences),
        "classification_counts": dict(sorted(counts.items())),
        "records": comparisons,
        "consolidated": False,
        "exports_triggered": False,
        "downloads_triggered": False,
        "created_utc": now(),
        "interpretation": (
            "Recovery text was compared exactly after whitespace normalization. "
            "Historical duplicates and text variants remain explicit; no record was silently merged."
        ),
    }
    write(result)
    print(json.dumps({"run_id": RUN_ID, "status": result["status"], "classification_counts": result["classification_counts"], "old_message_count": len(old), "recovery_record_count": len(recovery.get("records", []))}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
