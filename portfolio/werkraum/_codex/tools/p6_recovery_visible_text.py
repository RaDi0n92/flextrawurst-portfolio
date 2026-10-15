#!/usr/bin/env python3
"""Read-only P6 recovery pass for one already-bound ChatGPT tab.

No recorder start/finish button is touched. The old VPS capture remains
unchanged; this run stores a new raw-text evidence body under its own run_id.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright


CID = os.environ.get("P6_CID", "6a70e4ad-7560-83ed-a69f-78381bb59f4e")
LABEL = os.environ.get("P6_LABEL", "Reise Dauerloop")
RUN_ID = os.environ.get("P6_RUN_ID", "audit-20260813T-p6-recovery-reise-v2")
ORDINAL = os.environ.get("P6_ORDINAL", "01")
READ_ONLY = os.environ.get("P6_READ_ONLY", "0") == "1"
OUT = Path("/root/werkraum/_gpt/ui_visible_conversations/audit_runs") / RUN_ID
CHAT_OUT = OUT / f"{ORDINAL}-{CID}.json"

SNAPSHOT = r"""() => {
  function canonicalText(node) {
    if (!node) return '';
    const content = node.querySelector('[data-testid="collapsible-user-message-content"]') || node;
    const clone = content.cloneNode(true);
    clone.querySelectorAll('button, [role="button"], [aria-expanded], svg, script, style').forEach((e) => e.remove());
    clone.querySelectorAll('[data-inline-selection-pill][data-keyword]').forEach((pill) => {
      pill.replaceWith(document.createTextNode(`@${pill.getAttribute('data-keyword')}`));
    });
    return (clone.innerText || clone.textContent || '').replace(/\s+/g, ' ').trim();
  }
  const root = [...document.querySelectorAll('div')].find(e =>
    String(e.className || '').includes('scroll-root'));
  if (!root) return {error: 'scroll_root_not_found'};
  const blocks = [...document.querySelectorAll('[data-message-author-role]')].map((e, i) => {
    const attrs = {};
    for (const name of ['id', 'data-message-id', 'data-testid', 'data-turn-id', 'data-message-author-role']) {
      if (e.getAttribute(name)) attrs[name] = e.getAttribute(name);
    }
    const raw_text = canonicalText(e);
    const rect = e.getBoundingClientRect();
    return {
      i,
      attrs,
      role: e.getAttribute('data-message-author-role') || 'unknown',
      raw_text,
      text_length: raw_text.length,
      top: Math.round(rect.top),
      bottom: Math.round(rect.bottom)
    };
  });
  return {
    scroll_top: root.scrollTop,
    scroll_height: root.scrollHeight,
    viewport_height: root.clientHeight,
    max_scroll: Math.max(0, root.scrollHeight - root.clientHeight),
    blocks,
    loading: !!document.querySelector('[aria-busy="true"]')
  };
}"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalized(text: str) -> str:
    return " ".join((text or "").split())


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def save(value: dict) -> None:
    tmp = CHAT_OUT.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(CHAT_OUT)


async def snapshot(page):
    data = await page.evaluate(SNAPSHOT)
    for block in data.get("blocks", []):
        block["normalized_text"] = normalized(block.get("raw_text", ""))
        block["text_sha256"] = digest(block["normalized_text"])
    return data


def clean_snapshot(data: dict) -> dict:
    """Keep window evidence structural; retain full text only in records."""
    cleaned = json.loads(json.dumps(data, ensure_ascii=False))
    for block in cleaned.get("blocks", []):
        block.pop("raw_text", None)
    return cleaned


def structural_hash(data: dict) -> str:
    projection = {
        "scroll_top": data.get("scroll_top"),
        "scroll_height": data.get("scroll_height"),
        "viewport_height": data.get("viewport_height"),
        "max_scroll": data.get("max_scroll"),
        "blocks": [
            {k: b.get(k) for k in ("attrs", "role", "text_length", "text_sha256", "top", "bottom")}
            for b in data.get("blocks", [])
        ],
        "loading": data.get("loading"),
    }
    return digest(json.dumps(projection, ensure_ascii=False, sort_keys=True))


async def stable_snapshot(page, limit: int = 30):
    first = await snapshot(page)
    previous = first
    for polls in range(1, limit + 1):
        await page.wait_for_timeout(150)
        current = await snapshot(page)
        if structural_hash(previous) == structural_hash(current):
            return first, previous, current, True, polls
        previous = current
    return first, previous, current, False, limit


async def close_visible_overlay(page, result: dict) -> bool:
    modal = page.locator('[role=dialog]:has-text("Prompt teilen")').first
    if await modal.count():
        try:
            await modal.locator('button[aria-label="Schließen"]').click()
            await page.wait_for_timeout(400)
            result["errors"].append({"reason": "visible_prompt_share_overlay", "recovered_by": "visible_close_button", "at": now()})
            return True
        except Exception:
            pass
    close = page.get_by_role("button", name="Schließen").last
    try:
        if await close.count() and await close.is_visible():
            await close.click()
            await page.wait_for_timeout(400)
            result["errors"].append({"reason": "visible_attachment_sheet", "recovered_by": "visible_close_button", "at": now()})
            return True
    except Exception:
        pass
    return False


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=False)
    result = {
        "run_id": RUN_ID,
        "phase": "P6",
        "mode": "manual_playwright_real_input_read_only_recovery" if READ_ONLY else "manual_playwright_real_input_recovery_scan",
        "conversation_id": CID,
        "label": LABEL,
        "status": "running",
        "started_utc": now(),
        "source_contract": {
            "old_vps_folder_modified": False,
            "recorder_start_clicked": False,
            "recorder_finish_clicked": False,
            "recovery_run_id": RUN_ID,
            "raw_visible_text_retained": True,
        },
        "windows": [],
        "records": [],
        "errors": [],
    }
    save(result)

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp("http://127.0.0.1:9222")
        page = next((p for context in browser.contexts for p in context.pages if p.url.endswith("/c/" + CID)), None)
        if not page:
            result.update(status="blocked", reason="chat_tab_not_found", finished_utc=now())
            save(result)
            return
        await page.bring_to_front()
        await close_visible_overlay(page, result)
        root = page.locator('div[class*="scroll-root"]').first
        if await root.count() == 0:
            result.update(status="blocked", reason="scroll_root_not_found", finished_utc=now())
            save(result)
            return

        panel = None
        if not READ_ONLY:
            for context in browser.contexts:
                for candidate in context.pages:
                    if not candidate.url.endswith("/sidepanel.html"):
                        continue
                    try:
                        identity = await candidate.locator("#chatIdentity").inner_text(timeout=700)
                    except Exception:
                        continue
                    if CID in identity:
                        panel = candidate
                        break
                if panel:
                    break
            if not panel:
                result.update(status="blocked", reason="bound_sidepanel_not_found", finished_utc=now())
                save(result)
                return

            if await panel.locator("#operatorReset").is_enabled():
                await panel.locator("#operatorReset").click()
                await panel.wait_for_timeout(700)
                result["recovery_reset_clicked"] = True
            await panel.locator("#startImport").click()
            await panel.wait_for_timeout(900)
            result["source_contract"]["recorder_start_clicked"] = True
            result["import_start_status"] = (await panel.locator("#importStatus").inner_text())[:800]
            auto_expand = panel.locator("#autoExpand")
            if await auto_expand.is_checked():
                await auto_expand.click()
                result["auto_expand_disabled_via_ui"] = True
            else:
                result["auto_expand_disabled_via_ui"] = False
        await page.bring_to_front()
        box = await root.bounding_box()
        await root.click(position={"x": 8, "y": max(8, min(100, box["height"] / 2))})

        box = await root.bounding_box()
        await root.click(position={"x": 8, "y": max(8, min(100, box["height"] / 2))})
        await page.keyboard.press("Home")
        first, second, third, top_stable, polls = await stable_snapshot(page)
        result["top_checkpoint"] = {
            "before": clean_snapshot(first),
            "after_first_stability": clean_snapshot(second),
            "after_second_stability": clean_snapshot(third),
            "stable": top_stable,
            "polls": polls,
            "real_home_sent": True,
        }
        if third.get("scroll_top", 999) > 8:
            result.update(status="blocked", reason="real_home_did_not_reach_top", finished_utc=now())
            save(result)
            return

        records: dict[tuple[str, str, str], dict] = {}
        step = 0
        while True:
            before = await snapshot(page)
            top = float(before.get("scroll_top", 0))
            maximum = float(before.get("max_scroll", 0))
            viewport = float(before.get("viewport_height", 0) or 0)
            if top >= maximum - 8:
                result["end_checkpoint"] = {"snapshot": clean_snapshot(before), "at_bottom": True}
                break
            delta = max(1, int(viewport * 0.70))
            overlap = 1 - delta / max(viewport, 1)
            if overlap < 0.30 - 1e-9:
                result["errors"].append({"reason": "overlap_below_threshold", "viewport_height": viewport, "delta": delta, "overlap": overlap})
                break
            try:
                box = await root.bounding_box()
                await root.click(position={"x": 8, "y": max(8, min(100, box["height"] / 2))})
                await page.mouse.wheel(0, delta)
            except PlaywrightTimeoutError as error:
                if await close_visible_overlay(page, result):
                    continue
                result["errors"].append({"reason": "pointer_interception", "message": str(error)[:500], "at": now()})
                break
            first, second, third, stable, polls = await stable_snapshot(page)
            step += 1
            for block in third.get("blocks", []):
                attrs = block.get("attrs", {})
                stable_id = attrs.get("data-message-id") or attrs.get("data-provider-id")
                identity = "id:" + str(stable_id).removeprefix("message:") if stable_id else "content:" + block.get("text_sha256", "")
                key = (identity, block.get("role", "unknown"), block.get("text_sha256", ""))
                record = records.setdefault(key, {
                    "identity": identity,
                    "identity_mode": "stable_dom_or_provider_id" if stable_id else "content_hash_without_stable_id",
                    "stable_id": str(stable_id).removeprefix("message:") if stable_id else None,
                    "role": block.get("role", "unknown"),
                    "text_length": block.get("text_length"),
                    "raw_text": block.get("raw_text", ""),
                    "normalized_text": block.get("normalized_text", ""),
                    "text_sha256": block.get("text_sha256"),
                    "occurrences": 0,
                    "first_window": step,
                })
                record["occurrences"] += 1
            result["windows"].append({
                "index": step,
                "before": clean_snapshot(before),
                "after_first_stability": clean_snapshot(first),
                "after_second_stability": clean_snapshot(second),
                "after": clean_snapshot(third),
                "stable": stable,
                "stability_polls": polls,
                "delta_y": delta,
                "viewport_height": viewport,
                "overlap_ratio": overlap,
                "real_click": True,
                "real_wheel": True,
                "timestamp_utc": now(),
            })
            if not stable:
                result["errors"].append({"reason": "double_stability_check_failed", "step": step, "at": now()})
            result["records"] = list(records.values())
            save(result)
            if step % 50 == 0:
                print(json.dumps({"step": step, "top": round(third.get("scroll_top", 0)), "max": round(third.get("max_scroll", 0)), "records": len(records), "stable": stable, "overlap": round(overlap, 4)}, ensure_ascii=False), flush=True)

        result["records"] = list(records.values())
        if panel:
            await panel.locator("#finishImport").click()
            await panel.wait_for_timeout(1400)
            result["source_contract"]["recorder_finish_clicked"] = True
            result["finish_status"] = (await panel.locator("#importStatus").inner_text())[:1200]
            result["panel_delivery_status"] = (await panel.locator("#deliveryDetail").inner_text())[:500]
        result["finished_utc"] = now()
        result["status"] = "p6_recovery_partial" if result.get("end_checkpoint", {}).get("at_bottom") and top_stable and all(w["stable"] for w in result["windows"]) else "p6_recovery_partial_not_abnahmefaehig"
        save(result)
        print(json.dumps({"run_id": RUN_ID, "status": result["status"], "windows": len(result["windows"]), "records": len(result["records"]), "errors": len(result["errors"]), "at_bottom": result.get("end_checkpoint", {}).get("at_bottom")}, ensure_ascii=False), flush=True)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
