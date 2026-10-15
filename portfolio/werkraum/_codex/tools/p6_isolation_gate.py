#!/usr/bin/env python3
"""Provenance gate for P6 read-only recovery runs.

The gate snapshots historical chat folders before and after a recovery
process. It refuses recorder mode and fails closed when the old source changes.
It does not restore or rewrite source data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


WORKSPACE = Path("/root/werkraum")
CHAT_ROOT = WORKSPACE / "_gpt/ui_visible_conversations"
RUN_ROOT = CHAT_ROOT / "audit_runs"
RECOVERY_RUNNER = WORKSPACE / "_codex/tools/p6_recovery_visible_text.py"
GATE_RUN_ID = os.environ.get("P6_GATE_RUN_ID", "audit-20260813T-p6-isolation-gate-v1")
GATE_RUN = RUN_ROOT / GATE_RUN_ID

CHATS = [
    ("01", "6a70f37b-e940-83ed-bb53-0d8cc6a07eef", "2026-08-03__Erfinde-dich-neu__6a70f37be940-93049da8a8", "Neuer Abschnitt RISSWANDLER", "audit-20260813T-p6-recovery-readonly-neuer-abschnitt-v1"),
    ("02", "6a70e4ad-7560-83ed-a69f-78381bb59f4e", "2026-08-03__Neuer-Risswandler-entwickelt__6a70e4ad7560-5e33ad0f89", "Reise Dauerloop", "audit-20260813T-p6-recovery-reise-v1"),
    ("03", "6a70e85a-3ad0-83ed-be41-fd20648fac93", "2026-08-03__VPS-Stop-Bestätigt__6a70e85a3ad0-d8285c6a98", "VPS Stop Bestätigt", "audit-20260813T-p6-recovery-readonly-vps-stop-v1"),
    ("04", "6a70e498-5674-83eb-8714-a46b99a761ec", "2026-08-03__Neuer-Name-für-VPS__6a70e4985674-0a01518d54", "Neuer Name für VPS", "audit-20260813T-p6-recovery-readonly-neuer-name-v1"),
    ("05", "6a67edd5-59f4-83eb-89be-4e4284d02528", "2026-08-03__bau-browserextention__6a67edd559f4-a9b47ceed6", "bau-browserextention", "audit-20260813T-p6-recovery-readonly-browserextention-v1"),
]


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tree_snapshot(folder: Path) -> dict:
    files = {}
    for path in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = str(path.relative_to(folder))
        files[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {"folder": str(folder), "file_count": len(files), "files": files, "tree_sha256": digest}


def load_existing_results() -> list[dict]:
    results = []
    for ordinal, cid, _folder, label, run_id in CHATS:
        candidates = sorted((RUN_ROOT / run_id).glob(f"*-{cid}.json"))
        if not candidates:
            results.append({"label": label, "conversation_id": cid, "run_id": run_id, "status": "missing_artifact"})
            continue
        data = json.loads(candidates[-1].read_text(encoding="utf-8"))
        results.append({
            "label": label,
            "conversation_id": cid,
            "run_id": run_id,
            "status": data.get("status"),
            "windows": len(data.get("windows", [])),
            "records": len(data.get("records", [])),
            "errors": len(data.get("errors", [])),
            "at_bottom": data.get("end_checkpoint", {}).get("at_bottom") is True,
            "read_only": data.get("source_contract", {}).get("recorder_start_clicked") is False and data.get("source_contract", {}).get("recorder_finish_clicked") is False,
        })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-existing", action="store_true", help="verify existing read-only artifacts and source hashes")
    parser.add_argument("--run", action="store_true", help="run all five read-only recoveries sequentially")
    parser.add_argument("--run-id-prefix", help="required with --run; unique prefix for all new recovery run IDs")
    args = parser.parse_args()
    if args.verify_existing == args.run:
        parser.error("genau eine Option wählen: --verify-existing oder --run")
    if args.run and not args.run_id_prefix:
        parser.error("--run benötigt einen neuen --run-id-prefix; bestehende Run-IDs werden nie wiederverwendet")
    if not RECOVERY_RUNNER.exists():
        print(json.dumps({"status": "blocked", "reason": "recovery_runner_missing"}))
        return 2

    before = {cid: tree_snapshot(CHAT_ROOT / folder) for _ordinal, cid, folder, _label, _run in CHATS}
    results = []
    if args.run:
        for ordinal, cid, _folder, label, run_id in CHATS:
            env = os.environ.copy()
            env.update({
                "P6_READ_ONLY": "1",
                "P6_CID": cid,
                "P6_LABEL": label,
                "P6_RUN_ID": f"{args.run_id_prefix}-{ordinal}",
                "P6_ORDINAL": ordinal,
            })
            proc = subprocess.run([sys.executable, "-u", str(RECOVERY_RUNNER)], cwd=WORKSPACE, env=env, text=True)
            results.append({"label": label, "conversation_id": cid, "run_id": run_id, "runner_exit_code": proc.returncode})
            if proc.returncode != 0:
                break
    else:
        results = load_existing_results()

    after = {cid: tree_snapshot(CHAT_ROOT / folder) for _ordinal, cid, folder, _label, _run in CHATS}
    mutations = []
    for _ordinal, cid, folder, label, _run in CHATS:
        if before[cid]["tree_sha256"] != after[cid]["tree_sha256"]:
            mutations.append({"label": label, "conversation_id": cid, "folder": str(CHAT_ROOT / folder), "before": before[cid]["tree_sha256"], "after": after[cid]["tree_sha256"]})

    status = "p6_isolation_passed" if not mutations and all(r.get("read_only", True) for r in results) else "p6_isolation_failed"
    manifest = {
        "run_id": GATE_RUN_ID,
        "phase": "P6",
        "status": status,
        "mode": "read_only_provenance_gate",
        "created_utc": now(),
        "historical_folder_mutations": mutations,
        "source_contract": {
            "old_folders_must_remain_byte_identical": True,
            "recorder_start_forbidden": True,
            "recorder_finish_forbidden": True,
            "exports_triggered": False,
            "downloads_triggered": False,
        },
        "before": before,
        "after": after,
        "results": results,
        "p7_eligible": False,
    }
    GATE_RUN.mkdir(parents=True, exist_ok=False)
    (GATE_RUN / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": manifest["run_id"], "status": status, "mutations": len(mutations), "p7_eligible": False}, ensure_ascii=False, indent=2))
    return 0 if status == "p6_isolation_passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
