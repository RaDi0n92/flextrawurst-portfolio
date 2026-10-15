#!/usr/bin/env python3
"""Build one conservative P6 comparison for all five read-only recoveries."""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/root/werkraum/_gpt/ui_visible_conversations")
AUDITS = ROOT / "audit_runs"
OUT = AUDITS / "audit-20260813T-p6-combined-readonly-v1"

CHATS = [
    {
        "label": "Neuer Abschnitt RISSWANDLER",
        "conversation_id": "6a70f37b-e940-83ed-bb53-0d8cc6a07eef",
        "folder": "2026-08-03__Erfinde-dich-neu__6a70f37be940-93049da8a8",
        "run": "audit-20260813T-p6-recovery-readonly-neuer-abschnitt-v1",
        "ordinal": "01",
    },
    {
        "label": "Reise Dauerloop",
        "conversation_id": "6a70e4ad-7560-83ed-a69f-78381bb59f4e",
        "folder": "2026-08-03__Neuer-Risswandler-entwickelt__6a70e4ad7560-5e33ad0f89",
        "run": "audit-20260813T-p6-recovery-reise-v1",
        "ordinal": "01",
    },
    {
        "label": "VPS Stop Bestätigt",
        "conversation_id": "6a70e85a-3ad0-83ed-be41-fd20648fac93",
        "folder": "2026-08-03__VPS-Stop-Bestätigt__6a70e85a3ad0-d8285c6a98",
        "run": "audit-20260813T-p6-recovery-readonly-vps-stop-v1",
        "ordinal": "03",
    },
    {
        "label": "Neuer Name für VPS",
        "conversation_id": "6a70e498-5674-83eb-8714-a46b99a761ec",
        "folder": "2026-08-03__Neuer-Name-für-VPS__6a70e4985674-0a01518d54",
        "run": "audit-20260813T-p6-recovery-readonly-neuer-name-v1",
        "ordinal": "04",
    },
    {
        "label": "bau-browserextention",
        "conversation_id": "6a67edd5-59f4-83eb-89be-4e4284d02528",
        "folder": "2026-08-03__bau-browserextention__6a67edd559f4-a9b47ceed6",
        "run": "audit-20260813T-p6-recovery-readonly-browserextention-v1",
        "ordinal": "05",
    },
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize(text: str) -> str:
    return " ".join((text or "").split())


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def stable_id(message: dict) -> str | None:
    value = message.get("dom_id") or message.get("data_message_id")
    return str(value).removeprefix("message:") if value else None


def load_recovery(chat: dict) -> tuple[Path, dict]:
    path = AUDITS / chat["run"] / f'{chat["ordinal"]}-{chat["conversation_id"]}.json'
    return path, json.loads(path.read_text(encoding="utf-8"))


def compare(chat: dict) -> dict:
    old_folder = ROOT / chat["folder"]
    old_path = old_folder / "messages.jsonl"
    recovery_path, recovery = load_recovery(chat)
    old = [json.loads(line) for line in old_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    by_id: dict[str, list[int]] = defaultdict(list)
    by_content: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, message in enumerate(old, 1):
        ident = stable_id(message)
        if ident:
            by_id[ident].append(index)
        by_content[(message.get("role", "unknown"), normalize(message.get("content", "")))].append(index)

    counts: dict[str, int] = defaultdict(int)
    recovery_ids = {record.get("stable_id") for record in recovery.get("records", []) if record.get("stable_id")}
    matched_old: set[int] = set()
    record_findings = []
    for record in recovery.get("records", []):
        role = record.get("role", "unknown")
        text = normalize(record.get("raw_text", ""))
        ident = record.get("stable_id")
        candidates = by_id.get(ident, []) if ident else by_content[(role, text)]
        finding = {
            "recovery_run_id": chat["run"],
            "identity": record.get("identity"),
            "stable_id": ident,
            "role": role,
            "recovery_text_sha256": record.get("text_sha256") or digest(text),
            "recovery_text_length": len(text),
            "historical_candidates": candidates,
        }
        if not candidates:
            classification = "missing-vps"
        elif len(candidates) > 1:
            exact = [i for i in candidates if old[i - 1].get("role", "unknown") == role and normalize(old[i - 1].get("content", "")) == text]
            classification = "ambiguous-duplicate-history" if len(exact) == len(candidates) else "ambiguous-text-variant"
            matched_old.update(exact)
        else:
            index = candidates[0]
            matched_old.add(index)
            historical = old[index - 1]
            if historical.get("role", "unknown") != role:
                classification = "role-mismatch"
            elif normalize(historical.get("content", "")) != text:
                classification = "changed-text"
                finding["historical_text_sha256"] = digest(normalize(historical.get("content", "")))
            else:
                classification = "match"
        finding["classification"] = classification
        counts[classification] += 1
        record_findings.append(finding)

    missing_live = sorted(set(by_id) - recovery_ids)
    counts["missing-live"] += len(missing_live)
    run_source = recovery.get("source_contract", {})
    return {
        "label": chat["label"],
        "conversation_id": chat["conversation_id"],
        "recovery_run_id": chat["run"],
        "recovery_file": str(recovery_path),
        "historical_folder": str(old_folder),
        "historical_message_count": len(old),
        "recovery_record_count": len(recovery.get("records", [])),
        "window_count": len(recovery.get("windows", [])),
        "error_count": len(recovery.get("errors", [])),
        "at_bottom": recovery.get("end_checkpoint", {}).get("at_bottom") is True,
        "old_folder_modified": bool(run_source.get("old_vps_folder_modified", False)),
        "recorder_start_clicked": bool(run_source.get("recorder_start_clicked", False)),
        "recorder_finish_clicked": bool(run_source.get("recorder_finish_clicked", False)),
        "missing_live_stable_id_count": len(missing_live),
        "missing_live_stable_ids": missing_live,
        "classification_counts": dict(sorted(counts.items())),
        "semantically_complete": set(counts) <= {"match"} and counts.get("match", 0) == len(old),
        "records": record_findings,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    results = [compare(chat) for chat in CHATS]
    total = defaultdict(int)
    for result in results:
        for key, value in result["classification_counts"].items():
            total[key] += value
    manifest = {
        "run_id": "audit-20260813T-p6-combined-readonly-v1",
        "phase": "P6",
        "status": "p6_historical_partial",
        "mode": "manual_playwright_real_input_read_only_recovery",
        "source_contract": {
            "historical_folders_modified": False,
            "recorder_start_clicked": False,
            "recorder_finish_clicked": False,
            "exports_triggered": False,
            "downloads_triggered": False,
            "consolidated": False,
        },
        "comparison_rule": "full visible text compared after whitespace normalization; duplicate and variant history remain explicit",
        "classification_counts_total": dict(sorted(total.items())),
        "chats": results,
        "p7_eligible": False,
        "p7_blockers": ["historical_partial", "ambiguous_or_mismatched_records", "missing_live_records"],
        "created_utc": now(),
    }
    tmp = OUT / "manifest.json.tmp"
    tmp.write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(OUT / "manifest.json")
    print(json.dumps({"run_id": manifest["run_id"], "status": manifest["status"], "total": manifest["classification_counts_total"], "p7_eligible": manifest["p7_eligible"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
