#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path('/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor')
SNAP = ROOT / 'snapshots'
WORK = ROOT / 'state/replay_workspace'
REPORT = ROOT / 'reports/MUTATION_REPLAY_REPORT.json'


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def atomic_json(path: Path, obj: object) -> None:
    data = (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)


def copy_snapshot(epoch: str, logical: str, target: Path) -> None:
    source = SNAP / epoch / logical
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def state(path: Path) -> dict:
    st = path.stat()
    return {'path': str(path), 'bytes': st.st_size, 'mtime_ns': st.st_mtime_ns, 'sha256': sha(path)}


def reset() -> dict:
    if WORK.exists(): shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    mapping = [
        ('E000_BASELINE', 'append/append_only.jsonl'),
        ('E000_BASELINE', 'rewrite/rewrite_target.txt'),
        ('E000_BASELINE', 'rename/original/rename_source.txt'),
        ('E000_BASELINE', 'stealth/same_size_same_mtime.txt'),
        ('E000_BASELINE', 'race/race_target.txt'),
    ]
    for epoch, logical in mapping:
        copy_snapshot(epoch, logical, WORK / logical)
    return {'id': 'RESET', 'status': 'PASS', 'files': [state(WORK / logical) for _, logical in mapping]}


def append_only() -> dict:
    target = WORK / 'append/append_only.jsonl'
    before = target.read_bytes()
    final = (SNAP / 'E010_APPEND/append/append_only.jsonl').read_bytes()
    if not final.startswith(before):
        return {'id': 'APPEND_ONLY', 'status': 'FAIL', 'reason': 'expected final snapshot does not preserve baseline prefix'}
    with target.open('ab') as f:
        f.write(final[len(before):]); f.flush(); os.fsync(f.fileno())
    actual = target.read_bytes()
    return {'id': 'APPEND_ONLY', 'status': 'PASS' if actual == final else 'FAIL', 'before_bytes': len(before), 'after': state(target), 'prefix_unchanged': actual[:len(before)] == before}


def truncate() -> dict:
    target = WORK / 'rewrite/rewrite_target.txt'
    before = state(target)
    copy_snapshot('E020_TRUNCATE', 'rewrite/rewrite_target.txt', target)
    after = state(target)
    return {'id': 'TRUNCATE', 'status': 'PASS' if after['bytes'] < before['bytes'] and after['sha256'] != before['sha256'] else 'FAIL', 'before': before, 'after': after}


def full_rewrite() -> dict:
    target = WORK / 'rewrite/rewrite_target.txt'
    before = state(target)
    copy_snapshot('E030_FULL_REWRITE', 'rewrite/rewrite_target.txt', target)
    after = state(target)
    return {'id': 'FULL_REWRITE', 'status': 'PASS' if after['bytes'] > before['bytes'] and after['sha256'] != before['sha256'] else 'FAIL', 'before': before, 'after': after}


def rename_move() -> dict:
    source = WORK / 'rename/original/rename_source.txt'
    destination = WORK / 'rename/moved/deeper/rename_destination.txt'
    before = state(source)
    destination.parent.mkdir(parents=True, exist_ok=True)
    os.replace(source, destination)
    after = state(destination)
    ok = not source.exists() and destination.exists() and before['sha256'] == after['sha256']
    return {'id': 'RENAME_MOVE', 'status': 'PASS' if ok else 'FAIL', 'source_exists': source.exists(), 'before': before, 'after': after}


def stealth_middle() -> dict:
    target = WORK / 'stealth/same_size_same_mtime.txt'
    before = state(target)
    source = SNAP / 'E050_STEALTH_MIDDLE/stealth/same_size_same_mtime.txt'
    data = source.read_bytes()
    fd, tmp = tempfile.mkstemp(prefix='.stealth.', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, target)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
    os.utime(target, ns=(before['mtime_ns'], before['mtime_ns']))
    after = state(target)
    truth = {'same_size': before['bytes'] == after['bytes'], 'same_mtime': before['mtime_ns'] == after['mtime_ns'], 'changed_sha256': before['sha256'] != after['sha256']}
    return {'id': 'SAME_SIZE_MTIME_MIDDLE_CHANGE', 'status': 'PASS' if all(truth.values()) else 'FAIL', 'truth': truth, 'before': before, 'after': after}


def parallel_scan() -> dict:
    target = WORK / 'race/race_target.txt'
    start_hash = sha(target)
    trigger = threading.Event(); done = threading.Event()
    mutation = b'OMEGA_PARALLEL_MUTATION'

    def writer() -> None:
        trigger.wait(5)
        with target.open('r+b') as f:
            f.seek(4 * 1024 * 1024); f.write(mutation); f.flush(); os.fsync(f.fileno())
        done.set()

    t = threading.Thread(target=writer, daemon=True); t.start()
    scan = hashlib.sha256(); chunks = 0
    with target.open('rb') as f:
        while True:
            chunk = f.read(256 * 1024)
            if not chunk: break
            scan.update(chunk); chunks += 1
            if chunks == 2: trigger.set()
            time.sleep(0.002)
    done.wait(5); t.join(5)
    final_hash = sha(target)
    classification = 'CHANGED_DURING_SCAN' if done.is_set() and final_hash != start_hash else 'NOT_DETECTED'
    return {'id': 'PARALLEL_CHANGE_DURING_SCAN', 'status': 'PASS' if classification == 'CHANGED_DURING_SCAN' else 'FAIL', 'classification': classification, 'start_sha256': start_hash, 'scan_sha256': scan.hexdigest(), 'final_sha256': final_hash, 'writer_completed': done.is_set()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--step', choices=['reset', 'append', 'truncate', 'rewrite', 'rename', 'stealth', 'parallel', 'all'], default='all')
    args = ap.parse_args()
    functions = {'append': append_only, 'truncate': truncate, 'rewrite': full_rewrite, 'rename': rename_move, 'stealth': stealth_middle, 'parallel': parallel_scan}
    results = [reset()]
    if args.step != 'reset':
        order = list(functions) if args.step == 'all' else [args.step]
        for name in order: results.append(functions[name]())
    overall = 'PASS' if all(x['status'] == 'PASS' for x in results) else 'FAIL'
    report = {'schema_version': '1.0', 'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'overall_status': overall, 'requested_step': args.step, 'results': results, 'truth_boundary': 'All writes are confined to omega_monsterlabor/state/replay_workspace.'}
    atomic_json(REPORT, report)
    print(json.dumps({'overall_status': overall, 'steps': [{'id': x['id'], 'status': x['status']} for x in results], 'report': str(REPORT)}, ensure_ascii=False, indent=2))
    return 0 if overall == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
