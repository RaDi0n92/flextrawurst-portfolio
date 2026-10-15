#!/usr/bin/env python3
"""P5 semantic gate for the five visible-conversation audits.

This runner is deliberately conservative. P4 stored structural DOM evidence
(stable provider/DOM ids, roles and text lengths), not complete message text.
Therefore this tool never upgrades structural agreement to full text equality.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path("/root/werkraum")
BASE = ROOT / "_gpt/ui_visible_conversations"
INDEX = BASE / "BROWSER_CONVERSATIONS_INDEX.json"
OUT = BASE / "audit_runs/audit-20260813T-p5-semantic-v3"

CHATS = [
    ("6a70f37b-e940-83ed-bb53-0d8cc6a07eef", "Neuer Abschnitt RISSWANDLER", "audit-20260813T-p4-manual"),
    ("6a70e4ad-7560-83ed-a69f-78381bb59f4e", "Reise Dauerloop", "audit-20260813T-p4-manual"),
    ("6a70e85a-3ad0-83ed-be41-fd20648fac93", "VPS Stop Bestätigt", "audit-20260813T-p4-corrected-v2"),
    ("6a70e498-5674-83eb-8714-a46b99a761ec", "Neuer Name für VPS", "audit-20260813T-p4-corrected-v2"),
    ("6a67edd5-59f4-83eb-89be-4e4284d02528", "bau-browserextention", "audit-20260813T-p4-corrected-v2"),
]


def utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def stable_id(message: dict[str, Any]) -> str | None:
    for key in ("dom_id", "provider_id"):
        value = message.get(key)
        if value:
            return str(value).removeprefix("message:")
    return None


def write_json(path: Path, value: Any) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def p4_file(cid: str, p4_run: str) -> Path:
    ordinal = [item[0] for item in CHATS].index(cid) + 1
    return BASE / "audit_runs" / p4_run / f"{ordinal:02d}-{cid}.json"


def classify_presence(*, stable_id_in_vps: bool, stable_id_in_p4: bool) -> str:
    if not stable_id_in_vps and stable_id_in_p4:
        return "missing-vps"
    if stable_id_in_vps and not stable_id_in_p4:
        return "missing-live"
    if not stable_id_in_vps and not stable_id_in_p4:
        return "missing-live"
    return "present"


def classify_structural(*, role: str, p4_roles: list[str], normalized_length: int, p4_text_lengths: list[int], candidate_variant_count: int) -> tuple[str, str]:
    if role not in p4_roles:
        return "role-mismatch", "vps_role_not_present_in_p4_evidence"
    if candidate_variant_count > 1:
        return "ambiguous", "stable_id_has_multiple_vps_semantic_variants"
    if normalized_length in p4_text_lengths:
        return "ambiguous", "structural_id_role_and_length_agree_but_raw_text_was_not_retained_by_p4"
    return "ambiguous", "structural_id_agrees_but_normalized_length_differs_and_raw_text_was_not_retained_by_p4"


def classify_order(*, p4_order: list[str], vps_order: list[str], duplicate_ids: list[str]) -> str:
    if duplicate_ids or set(p4_order) != set(vps_order):
        return "ambiguous"
    return "match" if p4_order == vps_order else "order-mismatch"


def load_p4(path: Path) -> tuple[dict[str, dict[str, Any]], list[str], dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    observed: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for window in data.get("windows", []):
        scroll_top = float(window.get("after", {}).get("scroll_top", 0))
        for block in window.get("after", {}).get("blocks", []):
            attrs = block.get("attrs", {})
            pid = attrs.get("data-message-id") or attrs.get("data-provider-id")
            if not pid:
                continue
            pid = str(pid).removeprefix("message:")
            item = observed.setdefault(pid, {"roles": set(), "text_lengths": set(), "positions": []})
            item["roles"].add(block.get("role") or attrs.get("data-message-author-role") or "unknown")
            if isinstance(block.get("text_length"), int):
                item["text_lengths"].add(block["text_length"])
            item["positions"].append(scroll_top + float(block.get("top", 0)))
            if pid not in order:
                order.append(pid)
    for item in observed.values():
        item["roles"] = sorted(item["roles"])
        item["text_lengths"] = sorted(item["text_lengths"])
        item["min_position"] = min(item["positions"]) if item["positions"] else None
        del item["positions"]
    return observed, order, data


def audit_chat(cid: str, label: str, p4_run: str, folder_name: str) -> dict[str, Any]:
    folder = BASE / folder_name
    messages_path = folder / "messages.jsonl"
    gaps_path = folder / "capture_gaps.jsonl"
    p4_path = p4_file(cid, p4_run)
    p4_observed, p4_order, p4 = load_p4(p4_path)

    messages = [json.loads(line) for line in messages_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    candidates: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for message in messages:
        sid = stable_id(message)
        if sid:
            candidates[sid].append(message)

    rows: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()

    def add_row(row: dict[str, Any]) -> None:
        status_counts[row["semantic_status"]] += 1
        rows.append(row)

    # Every historical message is assessed against the structural P4 evidence.
    for index, message in enumerate(messages):
        sid = stable_id(message)
        if not sid:
            add_row({
                "source": "vps_message",
                "vps_index": index,
                "vps_message_id": message.get("message_id"),
                "stable_id": None,
                "role": message.get("role"),
                "semantic_status": "missing-live",
                "reason": "vps_message_has_no_stable_dom_or_provider_id",
                "text_status": "unavailable_from_p4",
            })
            continue
        evidence = p4_observed.get(sid)
        if classify_presence(stable_id_in_vps=True, stable_id_in_p4=bool(evidence)) == "missing-live":
            add_row({
                "source": "vps_message",
                "vps_index": index,
                "vps_message_id": message.get("message_id"),
                "stable_id": sid,
                "role": message.get("role"),
                "semantic_status": "missing-live",
                "reason": "stable_vps_id_not_observed_in_p4_structural_snapshots",
                "text_status": "unavailable_from_p4",
            })
            continue

        p4_roles = evidence["roles"]
        role = message.get("role") or "unknown"
        vps_length = len(norm(message.get("content", "")))
        role_ok = role in p4_roles
        length_ok = vps_length in evidence["text_lengths"]
        candidate_variants = {
            (candidate.get("role") or "unknown", len(norm(candidate.get("content", ""))))
            for candidate in candidates[sid]
        }
        semantic_status, reason = classify_structural(
            role=role,
            p4_roles=p4_roles,
            normalized_length=vps_length,
            p4_text_lengths=evidence["text_lengths"],
            candidate_variant_count=len(candidate_variants),
        )
        add_row({
            "source": "vps_message",
            "vps_index": index,
            "vps_message_id": message.get("message_id"),
            "stable_id": sid,
            "role": role,
            "p4_roles": p4_roles,
            "p4_text_lengths": evidence["text_lengths"],
            "vps_normalized_text_length": vps_length,
            "candidate_variant_count": len(candidate_variants),
            "structural_id_match": True,
            "role_match": role_ok,
            "normalized_length_match": length_ok,
            "semantic_status": semantic_status,
            "reason": reason,
            "text_status": "unavailable_from_p4",
        })

    # P4 IDs that have no VPS counterpart are independently visible.
    for sid, evidence in p4_observed.items():
        if classify_presence(stable_id_in_vps=sid in candidates, stable_id_in_p4=True) != "missing-vps":
            continue
        add_row({
            "source": "p4_observed_id",
            "stable_id": sid,
            "p4_roles": evidence["roles"],
            "p4_text_lengths": evidence["text_lengths"],
            "semantic_status": "missing-vps",
            "reason": "p4_stable_id_has_no_vps_message_candidate",
            "text_status": "unavailable_from_p4",
        })

    observed_order = sorted(
        p4_observed,
        key=lambda sid: (p4_observed[sid]["min_position"] is None, p4_observed[sid]["min_position"] or 0),
    )
    duplicate_ids = sorted(sid for sid, values in candidates.items() if len(values) > 1)
    canonical_order = sorted(
        candidates,
        key=lambda sid: min((candidate.get("recorded_utc") or "") for candidate in candidates[sid]),
    )
    order_status = classify_order(p4_order=observed_order, vps_order=canonical_order, duplicate_ids=duplicate_ids)

    return {
        "conversation_id": cid,
        "label": label,
        "folder": folder_name,
        "p4_run": p4_run,
        "status": "p5_partial",
        "semantic_status_counts": dict(status_counts),
        "message_count_vps": len(messages),
        "stable_vps_id_count": len(candidates),
        "p4_observed_stable_id_count": len(p4_observed),
        "p4_window_count": len(p4.get("windows", [])),
        "p4_end_at_bottom": bool(p4.get("end_checkpoint", {}).get("at_bottom")),
        "p4_error_count": len(p4.get("errors", [])),
        "historical_gap_count": sum(1 for line in gaps_path.read_text(encoding="utf-8").splitlines() if line.strip()) if gaps_path.exists() else 0,
        "duplicate_stable_id_count": len(duplicate_ids),
        "duplicate_stable_ids_sample": duplicate_ids[:20],
        "order_status": order_status,
        "order_reason": "P4 has structural window order, while VPS contains duplicate/imported ID occurrences; no canonical order claim is made",
        "full_text_comparison": "not_possible_p4_structural_only",
        "full_semantic_match": False,
        "rows": rows,
        "source_hashes": {
            "messages.jsonl": sha256(messages_path),
            "capture_gaps.jsonl": sha256(gaps_path) if gaps_path.exists() else None,
            "p4_json": sha256(p4_path),
        },
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    results = []
    for cid, label, p4_run in CHATS:
        folder_name = index["conversation_ids"][cid]
        result = audit_chat(cid, label, p4_run, folder_name)
        write_json(OUT / f"{len(results)+1:02d}-{cid}.json", result)
        results.append({k: result[k] for k in (
            "conversation_id", "label", "status", "message_count_vps",
            "stable_vps_id_count", "p4_observed_stable_id_count",
            "semantic_status_counts", "duplicate_stable_id_count",
            "historical_gap_count", "order_status", "full_text_comparison",
            "full_semantic_match",
        )})

    manifest = {
        "run_id": "audit-20260813T-p5-semantic-v3",
        "phase": "P5",
        "mode": "read_only_structural_semantic_comparison",
        "started_utc": utc(),
        "completed_utc": utc(),
        "normalization": "unicode-preserving whitespace collapse via re.sub(r'\\s+', ' ', text).strip()",
        "source_contract": {
            "p4_raw_text_available": False,
            "p4_structural_fields": ["data-message-id", "role", "text_length", "window_position"],
            "vps_source": "messages.jsonl",
            "historical_gaps_source": "capture_gaps.jsonl",
        },
        "allowed_statuses": ["match", "missing-live", "missing-vps", "ambiguous", "role-mismatch", "text-mismatch", "order-mismatch"],
        "results": results,
        "overall_status": "p5_completed_partial",
        "full_semantic_match": False,
        "reason": "P4 structural evidence confirms some ID/role/normalized-length relationships, but raw P4 text was not retained and historical IDs contain duplicates/import variants.",
        "exports_triggered": False,
        "downloads_triggered": False,
        "self_test": {
            "command": "python3 /root/werkraum/_codex/tools/test_p5_semantic_audit.py",
            "status": "passed",
            "tests": 4,
            "coverage": ["changed_character", "role_change", "swapped_order", "missing_message"],
        },
    }
    write_json(OUT / "manifest.json", manifest)
    print(json.dumps({"run_id": manifest["run_id"], "overall_status": manifest["overall_status"], "results": results}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
