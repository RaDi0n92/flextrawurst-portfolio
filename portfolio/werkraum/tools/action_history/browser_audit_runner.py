#!/usr/bin/env python3
"""Independent read-only inventory and audit for visible ChatGPT captures.

This tool deliberately does not import the browser recorder extension or its
export engine.  It reads the existing ui_visible_conversations store and, when
given a CDP URL, reads currently rendered ChatGPT DOM through Playwright
without scrolling, clicking, typing, downloading, or changing page state.

P1:
    python3 browser_audit_runner.py inventory

P2:
    python3 browser_audit_runner.py audit --run-id <run-id> [--cdp-url URL]
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse


DEFAULT_STORE = Path("/root/werkraum/_gpt/ui_visible_conversations")
EXPECTED_PREFIX = "2026-08-03__"
MESSAGE_EVENTS = {
    "message_final",
    "user_message_final",
    "assistant_message_final",
    "historical_import_message",
}
GAP_EVENTS = {"capture_gap", "tab_discarded", "page_reload", "capture_error"}
ROLE_VALUES = {"user", "assistant", "tool", "thinking", "unknown"}


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def run_id() -> str:
    return "audit-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid.uuid4().hex[:8]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_load(path: Path, default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def jsonl_rows(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_number}: invalid JSONL: {exc}") from exc
            if isinstance(value, dict):
                rows.append(value)
    return rows


def canonical_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalized_hash(value: Any) -> str:
    return sha256_bytes(canonical_text(value).encode("utf-8"))


def role_of(row: dict[str, Any]) -> str:
    role = str(row.get("role") or row.get("message_role") or "unknown").lower().strip()
    return role if role in ROLE_VALUES else "unknown"


def text_of(row: dict[str, Any]) -> str:
    for key in ("content", "text", "message", "visible_text", "body"):
        if row.get(key) is not None:
            return canonical_text(row[key])
    return ""


def message_key(row: dict[str, Any], index: int) -> str:
    for key in ("message_id", "provider_message_id", "dom_id", "id", "turn_id"):
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return f"ordinal:{index + 1}"


def file_record(path: Path, root: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path.relative_to(root)),
        "absolute_path": str(path),
        "bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256_file(path),
    }


def discover_chat_dirs(store: Path) -> list[Path]:
    return sorted(
        path
        for path in store.iterdir()
        if path.is_dir() and path.name.startswith(EXPECTED_PREFIX) and (path / "MANIFEST.json").is_file()
    )


def manifest_identity(path: Path) -> dict[str, Any]:
    manifest = json_load(path / "MANIFEST.json", {}) or {}
    if not isinstance(manifest, dict):
        manifest = {}
    return {
        "folder_name": path.name,
        "conversation_id": manifest.get("conversation_id"),
        "short_conversation_id": manifest.get("short_conversation_id"),
        "alias": manifest.get("alias"),
        "source_url": manifest.get("source_url"),
        "provider_id": manifest.get("provider_id", "chatgpt"),
        "complete_turn_count": manifest.get("complete_turn_count"),
        "turn_count": manifest.get("turn_count"),
        "gap_count": manifest.get("gap_count"),
        "manifest_status": manifest.get("status"),
    }


def inventory_chat(path: Path, store: Path) -> dict[str, Any]:
    identity = manifest_identity(path)
    rows_by_file: dict[str, list[dict[str, Any]]] = {}
    for name in ("messages.jsonl", "visible_stream.jsonl", "capture_gaps.jsonl"):
        rows_by_file[name] = jsonl_rows(path / name)

    message_rows = [row for row in rows_by_file["messages.jsonl"] if row.get("event_type") in MESSAGE_EVENTS or "role" in row]
    gap_rows = rows_by_file["capture_gaps.jsonl"]
    all_files = [file_record(item, store) for item in sorted(path.rglob("*")) if item.is_file() and item.name != ".capture.lock"]
    return {
        **identity,
        "absolute_path": str(path),
        "lock_present": (path / ".capture.lock").exists(),
        "file_count": len(all_files),
        "files": all_files,
        "row_counts": {
            "messages_jsonl": len(rows_by_file["messages.jsonl"]),
            "message_like_rows": len(message_rows),
            "visible_stream_jsonl": len(rows_by_file["visible_stream.jsonl"]),
            "capture_gaps_jsonl": len(gap_rows),
        },
        "roles": {
            role: sum(1 for row in message_rows if role_of(row) == role)
            for role in sorted(ROLE_VALUES)
        },
        "gap_types": {
            str(row.get("event_type") or row.get("type") or "unknown"): sum(
                1 for gap in gap_rows if (gap.get("event_type") or gap.get("type") or "unknown") == (row.get("event_type") or row.get("type") or "unknown")
            )
            for row in gap_rows
        },
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def create_inventory(
    store: Path,
    audit_root: Path,
    requested_run_id: str | None = None,
    cdp_url: str | None = None,
) -> Path:
    chats = discover_chat_dirs(store)
    rid = requested_run_id or run_id()
    out = audit_root / rid
    out.mkdir(parents=True, exist_ok=False)
    generated = utc_now()
    chat_records = [inventory_chat(path, store) for path in chats]
    expected_ids = {str(record.get("conversation_id")) for record in chat_records if record.get("conversation_id")}
    browser_probe = probe_cdp(cdp_url, expected_ids) if cdp_url else {
        "status": "not_run",
        "source": None,
        "tabs": [],
    }
    inventory = {
        "schema_version": "browser-audit.inventory.v1",
        "phase": "P1",
        "run_id": rid,
        "generated_utc": generated,
        "store_root": str(store),
        "read_only": True,
        "expected_chat_prefix": EXPECTED_PREFIX,
        "chat_count": len(chat_records),
        "chat_records": chat_records,
        "browser_probe": {key: value for key, value in browser_probe.items() if key != "tabs"},
    }
    write_json(out / "inventory.json", inventory)
    write_jsonl(out / "vps-files.jsonl", (item for chat in chat_records for item in chat["files"]))
    write_json(out / "browser-tabs.json", {
        "schema_version": "browser-audit.browser-tabs.v1",
        "generated_utc": generated,
        "status": browser_probe.get("status", "not_run"),
        "read_only": True,
        "tabs": browser_probe.get("tabs", []),
    })
    checksum_rows = []
    for item in sorted(out.rglob("*")):
        if item.is_file() and item.name != "checksums.sha256":
            checksum_rows.append(f"{sha256_file(item)}  {item.relative_to(out)}")
    (out / "checksums.sha256").write_text("\n".join(checksum_rows) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "P1", "run_id": rid, "path": str(out), "chat_count": len(chat_records)}, ensure_ascii=False))
    return out


def live_message_from_dom(row: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "key": str(row.get("key") or row.get("message_id") or row.get("dom_id") or f"live:{index + 1}"),
        "role": role_of(row),
        "text": canonical_text(row.get("text") or row.get("content")),
        "raw_text_sha256": normalized_hash(row.get("text") or row.get("content")),
        "in_viewport": bool(row.get("in_viewport", False)),
        "identity_kind": row.get("identity_kind", "unknown"),
    }


def read_browser_snapshot(path: Path) -> dict[str, Any]:
    value = json_load(path, {})
    if not isinstance(value, dict):
        raise ValueError(f"browser snapshot is not an object: {path}")
    return value


def probe_cdp(cdp_url: str, expected_ids: set[str]) -> dict[str, Any]:
    """Read currently rendered tabs only; no input or navigation is issued."""
    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"status": "blocked", "reason": f"playwright_unavailable: {exc}", "tabs": []}

    tabs: list[dict[str, Any]] = []
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.connect_over_cdp(cdp_url)
            for context_index, context in enumerate(browser.contexts):
                for page_index, page in enumerate(context.pages):
                    url = page.url
                    parsed = urlparse(url)
                    match = re.search(r"/c/([^/?#]+)", parsed.path)
                    conversation_id = match.group(1) if match else None
                    if not conversation_id or conversation_id not in expected_ids:
                        continue
                    target_id = None
                    try:
                        session = context.new_cdp_session(page)
                        target_id = session.send("Target.getTargetInfo").get("targetInfo", {}).get("targetId")
                    except Exception:
                        pass
                    snapshot = page.evaluate(
                        """() => {
                          const visible = (node) => {
                            const style = getComputedStyle(node);
                            const r = node.getBoundingClientRect();
                            return style.display !== 'none' && style.visibility !== 'hidden' && r.width > 0 && r.height > 0;
                          };
                          const root = document.querySelector('main,[role="main"]') || document.body;
                          const selectors = [
                            '[data-message-author-role]',
                            'section[data-testid^="conversation-turn-"]',
                            'article[data-testid^="conversation-turn-"]',
                            '[data-message-id]'
                          ];
                          const seen = new Set(); const messages = [];
                          for (const node of root.querySelectorAll(selectors.join(','))) {
                            if (!visible(node)) continue;
                            const specific = node.matches('[data-message-author-role], [data-message-id]');
                            // ChatGPT exposes the same visible message as a
                            // conversation-turn wrapper plus a nested
                            // provider-message node. Prefer the provider
                            // carrier; counting both would manufacture a
                            // semantic mismatch before comparison starts.
                            if (!specific && node.querySelector('[data-message-author-role], [data-message-id]')) continue;
                            const r = node.getBoundingClientRect();
                            const key = node.getAttribute('data-message-id') || node.getAttribute('data-testid') || `wrapper:${messages.length + 1}`;
                            if (seen.has(key)) continue; seen.add(key);
                            const role = node.getAttribute('data-message-author-role') ||
                              (node.getAttribute('data-testid') || '').match(/(?:user|assistant|tool|thinking)/i)?.[0] || 'unknown';
                            messages.push({
                              key,
                              role: String(role).toLowerCase(),
                              text: String(node.innerText || node.textContent || '').replace(/\\s+/g, ' ').trim(),
                              in_viewport: r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth,
                              identity_kind: node.hasAttribute('data-message-id') ? 'provider_message_id' : 'conversation_turn_wrapper'
                            });
                          }
                          return {
                            title: document.title,
                            viewport: { width: innerWidth, height: innerHeight, device_pixel_ratio: devicePixelRatio },
                            scroll: { x: scrollX, y: scrollY },
                            message_count: messages.length,
                            messages,
                            dom_text_sha256_input: messages.map(x => `${x.key}|${x.role}|${x.text}`).join('\\n')
                          };
                        }"""
                    )
                    tabs.append({
                        "conversation_id": conversation_id,
                        "url": url,
                        "title": page.title(),
                        "context_index": context_index,
                        "page_index": page_index,
                        "tab_id": target_id,
                        "window_id": None,
                        "tab_instance_id": None,
                        "snapshot": snapshot,
                        "snapshot_scope": "currently_materialized_dom_without_scroll_or_input",
                    })
            # Do not call browser.close(): this is a CDP connection to an
            # externally owned Chromium session. Leaving it open is part of
            # the read-only contract; the Playwright context disconnects when
            # the sync_playwright scope ends.
    except Exception as exc:  # pragma: no cover - environment dependent
        return {"status": "blocked", "reason": f"cdp_connection_failed: {exc}", "cdp_url": cdp_url, "tabs": tabs}
    return {"status": "ok", "cdp_url": cdp_url, "read_only": True, "tabs": tabs}


def compare_messages(vps_rows: list[dict[str, Any]], live_rows: list[dict[str, Any]]) -> dict[str, Any]:
    vps = [
        {
            "key": message_key(row, index),
            "role": role_of(row),
            "text": text_of(row),
            "raw_text_sha256": normalized_hash(text_of(row)),
        }
        for index, row in enumerate(vps_rows)
        if row.get("event_type") in MESSAGE_EVENTS or "role" in row
    ]
    live = [live_message_from_dom(row, index) for index, row in enumerate(live_rows)]
    exact = 0
    role_mismatch = 0
    text_mismatch = 0
    missing_live = 0
    missing_vps = 0
    rows: list[dict[str, Any]] = []
    for index in range(max(len(vps), len(live))):
        left = vps[index] if index < len(vps) else None
        right = live[index] if index < len(live) else None
        if left and right and left["role"] == right["role"] and left["text"] == right["text"]:
            status = "match"
            exact += 1
        elif left and not right:
            status = "missing-live"
            missing_live += 1
        elif right and not left:
            status = "missing-vps"
            missing_vps += 1
        elif left and right and left["role"] != right["role"]:
            status = "role-mismatch"
            role_mismatch += 1
        else:
            status = "text-mismatch"
            text_mismatch += 1
        rows.append({
            "index": index,
            "vps_key": left["key"] if left else None,
            "live_key": right["key"] if right else None,
            "status": status,
            "vps_role": left["role"] if left else None,
            "live_role": right["role"] if right else None,
            "vps_text_sha256": left["raw_text_sha256"] if left else None,
            "live_text_sha256": right["raw_text_sha256"] if right else None,
        })
    return {
        "vps_messages": len(vps),
        "live_messages": len(live),
        "live_scope": "currently_materialized_dom_without_scroll_or_input",
        "exact_matches": exact,
        "missing_live": missing_live,
        "missing_vps": missing_vps,
        "role_mismatches": role_mismatch,
        "text_mismatches": text_mismatch,
        "rows": rows,
    }


def audit_status(record: dict[str, Any], browser_tab: dict[str, Any] | None) -> tuple[str, list[str]]:
    reasons: list[str] = []
    complete = record.get("complete_turn_count")
    turns = record.get("turn_count")
    gaps = record.get("gap_count")
    if isinstance(complete, int) and isinstance(turns, int) and complete < turns:
        reasons.append(f"complete_turn_count {complete} < turn_count {turns}")
    if isinstance(gaps, int) and gaps > 0:
        reasons.append(f"manifest gap_count={gaps}")
    if record.get("lock_present"):
        reasons.append("capture_lock_present")
    if browser_tab is None:
        reasons.append("live_dom_snapshot_missing")
        return "blocked" if not reasons[:-1] else "partial", reasons
    snapshot = browser_tab.get("snapshot") or {}
    reasons.append("live_probe_is_current_dom_only")
    if not snapshot.get("messages"):
        reasons.append("live_dom_has_no_message_snapshot")
        return "blocked", reasons
    comparison = record.get("comparison") or {}
    if any(comparison.get(key, 0) for key in ("missing_live", "missing_vps", "role_mismatches", "text_mismatches")):
        reasons.append("live_dom_and_vps_semantics_differ")
        return "partial", reasons
    # A DOM snapshot without the P4 overlapping scroll protocol cannot prove
    # completeness, even when every currently visible row matches the VPS.
    return "partial", reasons


def create_audit(inventory_dir: Path, cdp_url: str | None = None, browser_snapshot: Path | None = None) -> Path:
    inventory = json_load(inventory_dir / "inventory.json", {})
    if not inventory:
        raise ValueError(f"P1 inventory missing: {inventory_dir / 'inventory.json'}")
    store = Path(inventory["store_root"])
    expected_ids = {str(record.get("conversation_id")) for record in inventory.get("chat_records", []) if record.get("conversation_id")}
    if browser_snapshot:
        browser = read_browser_snapshot(browser_snapshot)
        browser["source"] = str(browser_snapshot)
    elif cdp_url:
        browser = probe_cdp(cdp_url, expected_ids)
    else:
        browser = {"status": "blocked", "reason": "no_cdp_url_or_browser_snapshot", "tabs": []}
    browser_by_id = {str(tab.get("conversation_id")): tab for tab in browser.get("tabs", [])}

    results: list[dict[str, Any]] = []
    for record in inventory.get("chat_records", []):
        path = Path(record["absolute_path"])
        message_rows = jsonl_rows(path / "messages.jsonl")
        tab = browser_by_id.get(str(record.get("conversation_id")))
        comparison = None
        if tab is not None:
            comparison = compare_messages(message_rows, (tab.get("snapshot") or {}).get("messages", []))
        result = {**record, "browser_tab": tab, "comparison": comparison}
        status, reasons = audit_status(result, tab)
        result["status"] = status
        result["reasons"] = reasons
        results.append(result)
    summary = {status: sum(1 for row in results if row["status"] == status) for status in ("complete", "partial", "blocked", "ambiguous")}
    report = {
        "schema_version": "browser-audit.report.v1",
        "phase": "P2",
        "run_id": inventory["run_id"],
        "generated_utc": utc_now(),
        "read_only": True,
        "independent_of_exporter": True,
        "browser_probe": {key: value for key, value in browser.items() if key != "tabs"},
        "chat_count": len(results),
        "summary": summary,
        "results": results,
        "acceptance": {
            "five_known_chats_present": len(results) == 5,
            "no_false_all_green": not (len(results) == 5 and all(row["status"] == "complete" for row in results)),
            "gaps_remain_visible": any(row.get("gap_count", 0) for row in results),
        },
    }
    write_json(inventory_dir / "audit.json", report)
    lines = [
        "# Browserrecorder P2 Audit",
        "",
        f"- Run: `{report['run_id']}`",
        f"- Generated: `{report['generated_utc']}`",
        "- Read-only: `true`",
        "- Independent of exporter: `true`",
        "",
        "## Summary",
        "",
        "| Chat | Status | VPS messages | Complete turns / turns | Gaps | Reasons |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in results:
        lines.append(
            f"| `{row['folder_name']}` | **{row['status']}** | {row['row_counts']['message_like_rows']} | "
            f"{row.get('complete_turn_count')} / {row.get('turn_count')} | {row.get('gap_count')} | "
            f"{'; '.join(row['reasons']) or '–'} |"
        )
    lines += [
        "",
        "## Boundary",
        "",
        "This report reads the existing VPS capture files and, when configured, the currently rendered DOM. It does not call the recorder exporter, click, scroll, type, download, or restart a service.",
        "",
        "## Acceptance",
        "",
        f"- Five known chats present: `{report['acceptance']['five_known_chats_present']}`",
        f"- No false all-green result: `{report['acceptance']['no_false_all_green']}`",
        f"- Gaps remain visible: `{report['acceptance']['gaps_remain_visible']}`",
    ]
    (inventory_dir / "audit-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"phase": "P2", "run_id": report["run_id"], "path": str(inventory_dir), "summary": summary}, ensure_ascii=False))
    return inventory_dir


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("command", choices=("inventory", "audit"))
    root.add_argument("--store-root", type=Path, default=DEFAULT_STORE)
    root.add_argument("--audit-root", type=Path)
    root.add_argument("--run-id")
    root.add_argument("--cdp-url")
    root.add_argument("--browser-snapshot", type=Path)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    audit_root = args.audit_root or (args.store_root / "audit_runs")
    try:
        if args.command == "inventory":
            create_inventory(args.store_root, audit_root, args.run_id, args.cdp_url)
        else:
            if not args.run_id:
                raise ValueError("audit requires --run-id from P1")
            create_audit(audit_root / args.run_id, args.cdp_url, args.browser_snapshot)
    except (OSError, ValueError) as exc:
        print(f"browser_audit_runner: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
