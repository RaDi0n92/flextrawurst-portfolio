#!/usr/bin/env python3
"""Explain strict P6 text differences without weakening the P7 gate.

The strict comparison remains authoritative.  This report only records when a
different visible projection is attributable to controls or structured UI that
was present in one renderer but not the other.
"""

from __future__ import annotations

import difflib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/root/werkraum/_gpt/ui_visible_conversations")
AUDITS = ROOT / "audit_runs"
COMBINED = AUDITS / "audit-20260813T-p6-canonical-combined-v1"
OUT = AUDITS / "audit-20260813T-p6-presentation-analysis-v1"


def stable_id(row: dict) -> str | None:
    value = row.get("dom_id") or row.get("data_message_id")
    return str(value).removeprefix("message:") if value else None


def compact(value: str) -> str:
    return " ".join((value or "").split())


def presentation_shape(value: str) -> str:
    text = compact(value)
    text = re.sub(r"\s+(?:Mehr anzeigen|Weniger anzeigen)$", "", text)
    text = re.sub(r"(\.(?:txt|md|pdf|csv|json|py|js))Dokument", r"\1 Dokument", text, flags=re.I)
    text = re.sub(r"Dokument(?=\w)", "Dokument ", text)
    text = re.sub(r"(/root/[^ ]+)_$", r"\1", text)
    text = text.replace("MMicrosoft+2Microsoft+2Turn-", "M Microsoft +2 Microsoft +2 Turn-")
    return compact(text)


def reason(old: str, current: str) -> str | None:
    old_c = compact(old)
    current_c = compact(current)
    if re.search(r"\s+(?:Mehr anzeigen|Weniger anzeigen)$", old_c) and old_c.removesuffix(" Mehr anzeigen").removesuffix(" Weniger anzeigen") == current_c:
        return "historical_expand_control_label"
    if old_c.endswith("_") and old_c[:-1] == current_c:
        return "historical_markdown_trailing_underscore"
    if "Eingefügter Text" in old_c and (
        compact(old_c.replace("Eingefügter Text", "")) == current_c
        or "".join(old_c.replace("Eingefügter Text", "").split()) == "".join(current_c.split())
    ):
        return "historical_attachment_tile_label"
    if presentation_shape(old) == presentation_shape(current):
        if "Eingefügter Text" in old_c and "Eingefügter Text" not in current_c:
            return "historical_attachment_tile_label"
        if "Microsoft+2" in current_c or "webpage" in current_c.lower():
            return "structured_webpage_citation_pill_spacing"
        if ".txtDokument" in current_c or "Dokumenthier" in current_c:
            return "structured_attachment_tile_spacing"
        return "presentation_whitespace_projection"
    if "".join(old_c.split()) == "".join(current_c.split()):
        return "historical_structured_table_spacing"
    return None


def main() -> None:
    run_id = OUT.name
    combined = json.loads((COMBINED / "manifest.json").read_text(encoding="utf-8"))
    cases: list[dict] = []
    for chat in combined["chats"]:
        old_rows = [
            json.loads(line)
            for line in (Path(chat["historical_folder"]) / "messages.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        old_by_id = {stable_id(row): row for row in old_rows}
        recovery = json.loads(Path(chat["recovery_file"]).read_text(encoding="utf-8"))
        current_by_id = {row.get("stable_id"): row for row in recovery.get("records", [])}
        for finding in chat["records"]:
            if finding.get("classification") != "changed-text":
                continue
            ident = finding.get("stable_id")
            old = compact(old_by_id.get(ident, {}).get("content", ""))
            current = compact(current_by_id.get(ident, {}).get("raw_text", ""))
            why = reason(old, current)
            cases.append({
                "conversation_id": chat["conversation_id"],
                "label": chat["label"],
                "stable_id": ident,
                "strict_classification": finding["classification"],
                "reason": why or "requires_manual_content_review",
                "presentation_equivalent": why is not None,
                "historical_text_length": len(old),
                "current_text_length": len(current),
                "sequence_ratio": round(difflib.SequenceMatcher(None, old, current).ratio(), 6),
            })

    equivalent = sum(case["presentation_equivalent"] for case in cases)
    report = {
        "run_id": run_id,
        "phase": "P6",
        "strict_comparison_unchanged": True,
        "strict_p7_eligible": bool(combined.get("p7_eligible")),
        "strict_classification_counts": combined["classification_counts_total"],
        "changed_text_count": len(cases),
        "presentation_equivalent_count": equivalent,
        "content_review_count": len(cases) - equivalent,
        "source_contract": combined["source_contract"],
        "cases": cases,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.mkdir(parents=True, exist_ok=False)
    (OUT / "manifest.json").write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "run_id": report["run_id"],
        "strict_p7_eligible": report["strict_p7_eligible"],
        "changed_text_count": report["changed_text_count"],
        "presentation_equivalent_count": report["presentation_equivalent_count"],
        "content_review_count": report["content_review_count"],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
