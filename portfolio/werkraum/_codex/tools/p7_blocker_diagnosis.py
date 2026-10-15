#!/usr/bin/env python3
"""Diagnose strict P7 blockers using the existing Playwright recoveries."""

from __future__ import annotations

import asyncio
import difflib
import json
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import async_playwright


ROOT = Path("/root/werkraum/_gpt/ui_visible_conversations")
AUDITS = ROOT / "audit_runs"
COMBINED = AUDITS / "audit-20260813T-p6-canonical-combined-v1" / "manifest.json"
OUT = AUDITS / "audit-20260813T-p7-blocker-diagnosis-v1" / "manifest.json"


def stable_id(row: dict) -> str | None:
    value = row.get("dom_id") or row.get("data_message_id")
    return str(value).removeprefix("message:") if value else None


def normalized(value: str) -> str:
    return " ".join((value or "").split())


async def main() -> None:
    run_id = OUT.parent.name
    combined = json.loads(COMBINED.read_text(encoding="utf-8"))
    browser_checks: dict[str, dict] = {}
    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
        for chat in combined["chats"]:
            page = next(
                page
                for context in browser.contexts
                for page in context.pages
                if page.url.endswith("/c/" + chat["conversation_id"])
            )
            await page.bring_to_front()
            root = page.locator('div[class*="scroll-root"]').first
            box = await root.bounding_box()
            await root.click(position={"x": 8, "y": max(8, min(100, box["height"] / 2))})
            await page.keyboard.press("Home")
            await page.wait_for_timeout(700)
            snapshot = await page.evaluate(
                """() => {
                    const root = [...document.querySelectorAll('div')].find(e => String(e.className || '').includes('scroll-root'));
                    const blocks = [...document.querySelectorAll('[data-message-author-role]')];
                    const ids = blocks.map(e => e.getAttribute('data-message-id')).filter(Boolean);
                    return {
                        scroll_top: root?.scrollTop,
                        scroll_height: root?.scrollHeight,
                        viewport_height: root?.clientHeight,
                        max_scroll: root ? Math.max(0, root.scrollHeight - root.clientHeight) : null,
                        dom_block_count: blocks.length,
                        dom_ids_at_home: ids,
                    };
                }"""
            )
            browser_checks[chat["conversation_id"]] = snapshot
        await browser.close()

    results = []
    for chat in combined["chats"]:
        old_rows = [
            json.loads(line)
            for line in (Path(chat["historical_folder"]) / "messages.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        historical_ids = {stable_id(row) for row in old_rows if stable_id(row)}
        recovery = json.loads(Path(chat["recovery_file"]).read_text(encoding="utf-8"))
        recovery_ids = {row.get("stable_id") for row in recovery.get("records", []) if row.get("stable_id")}
        recovery_texts = [
            (row.get("role", "unknown"), normalized(row.get("raw_text", "")), row.get("stable_id"))
            for row in recovery.get("records", [])
        ]
        missing = sorted(historical_ids - recovery_ids)
        placeholder = [value for value in missing if value.startswith("request-placeholder-")]
        missing_rows = {stable_id(row): row for row in old_rows if stable_id(row) in set(missing)}
        exact_other_id = []
        near_variant = []
        no_content_candidate = []
        for ident, row in missing_rows.items():
            key = (row.get("role", "unknown"), normalized(row.get("content", "")))
            exact = [candidate for candidate in recovery_texts if candidate[:2] == key]
            if exact:
                exact_other_id.append({"historical_id": ident, "recovery_id": exact[0][2]})
                continue
            best = (0.0, None)
            for role, text, recovery_id in recovery_texts:
                if role != key[0]:
                    continue
                ratio = difflib.SequenceMatcher(None, key[1], text).ratio()
                if ratio > best[0]:
                    best = (ratio, recovery_id)
            if best[0] >= 0.96:
                near_variant.append({"historical_id": ident, "recovery_id": best[1], "ratio": round(best[0], 6)})
            else:
                no_content_candidate.append(ident)
        results.append(
            {
                "label": chat["label"],
                "conversation_id": chat["conversation_id"],
                "playwright_home_snapshot": browser_checks[chat["conversation_id"]],
                "canonical_p6_run": chat["recovery_run_id"],
                "canonical_at_bottom": chat["at_bottom"],
                "canonical_error_count": chat["error_count"],
                "historical_unique_dom_id_count": len(historical_ids),
                "canonical_recovered_unique_id_count": len(recovery_ids),
                "missing_after_full_playwright_run": len(missing),
                "missing_placeholder_id_count": len(placeholder),
                "missing_placeholder_id_sample": placeholder[:8],
                "missing_non_placeholder_id_sample": [value for value in missing if value not in placeholder][:8],
                "missing_exact_content_under_other_id_count": len(exact_other_id),
                "missing_near_variant_count": len(near_variant),
                "missing_without_content_candidate_count": len(no_content_candidate),
                "missing_exact_content_under_other_id_sample": exact_other_id[:8],
                "diagnosis": (
                    "current_live_body_shorter_or_rewritten_than_historical_folder"
                    if chat["at_bottom"] and chat["error_count"] == 0 and len(historical_ids) > len(recovery_ids)
                    else "requires_further_identity_review"
                ),
            }
        )

    report = {
        "run_id": run_id,
        "phase": "P7",
        "mode": "manual_playwright_real_input_read_only_diagnosis",
        "strict_p7_eligible": False,
        "rule": "a missing ID is only diagnosed after the canonical Playwright run reached the bottom with zero errors",
        "blockers": ["historical_body_longer_or_rewritten", "placeholder_and_provider_ids", "ambiguous_history_remains_explicit"],
        "chats": results,
        "created_utc": datetime.now(timezone.utc).isoformat(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=False)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "run_id": report["run_id"],
        "strict_p7_eligible": report["strict_p7_eligible"],
        "chats": [
            {
                "label": result["label"],
                "historical_unique": result["historical_unique_dom_id_count"],
                "recovered_unique": result["canonical_recovered_unique_id_count"],
                "missing": result["missing_after_full_playwright_run"],
                "placeholder_missing": result["missing_placeholder_id_count"],
            }
            for result in results
        ],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
