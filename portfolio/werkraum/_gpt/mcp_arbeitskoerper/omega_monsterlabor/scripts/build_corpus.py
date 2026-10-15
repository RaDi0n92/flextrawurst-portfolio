#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path

ROOT = Path('/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor')
FIX = ROOT / 'fixtures'
MAN = ROOT / 'manifests'
SNAP = ROOT / 'snapshots'
STATE = ROOT / 'state'
REPORTS = ROOT / 'reports'
NS = uuid.UUID('8d0f2fcb-8737-4f7a-9a6f-4ecf0a4db11f')
T0_NS = 1785391200000000000
ALLOWED = {'PASS', 'FAIL', 'UNKNOWN', 'BLOCKED'}


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def uid(kind: str, key: str) -> str:
    return f'urn:uuid:{uuid.uuid5(NS, kind + ":" + key)}'


def atomic_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if path.read_bytes() != data:
        raise RuntimeError(f'atomic reread mismatch: {path}')


def atomic_json(path: Path, obj: object) -> None:
    atomic_bytes(path, (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + '\n').encode('utf-8'))


def set_mtime(path: Path, ns: int = T0_NS) -> None:
    os.utime(path, ns=(ns, ns), follow_symlinks=False)


def snapshot(epoch: str, logical: str, source: Path) -> dict:
    target = SNAP / epoch / logical
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target, follow_symlinks=False)
    return {
        'epoch': epoch,
        'logical': logical,
        'path': str(target),
        'bytes': target.lstat().st_size,
        'sha256': sha_file(target) if target.is_file() and not target.is_symlink() else None,
        'mtime_ns': target.lstat().st_mtime_ns,
    }


def write_fixed(path: Path, data: bytes, mtime_ns: int = T0_NS) -> None:
    atomic_bytes(path, data)
    set_mtime(path, mtime_ns)


def reset_dirs() -> None:
    for d in (FIX, MAN, SNAP, STATE):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    for child in REPORTS.iterdir():
        if child.name in {'history', 'playwright'}:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()


def make_jsonl(path: Path, count: int, needle_line: int) -> tuple[int, int, str]:
    needle = 'OMEGA_JSONL_DEEP_NEEDLE'
    offset = 0
    needle_offset = -1
    with path.open('wb') as f:
        for i in range(count):
            payload = needle if i == needle_line else f'payload-{i:06d}-' + ('x' * 96)
            row = json.dumps({'seq': i, 'id': f'row-{i:06d}', 'payload': payload}, separators=(',', ':'), ensure_ascii=False).encode() + b'\n'
            if i == needle_line:
                needle_offset = offset + row.index(needle.encode())
            f.write(row)
            offset += len(row)
        f.flush()
        os.fsync(f.fileno())
    set_mtime(path)
    return count, needle_offset, needle


def build() -> None:
    reset_dirs()
    generated = dt.datetime.now(dt.timezone.utc).isoformat()
    epochs = [
        {'epoch_id': 'E000_BASELINE', 'sequence': 0, 'logical_time': '2026-07-30T06:40:00Z', 'operation': 'initial corpus creation'},
        {'epoch_id': 'E010_APPEND', 'sequence': 10, 'logical_time': '2026-07-30T06:40:10Z', 'operation': 'append-only growth without prior-byte rewrite'},
        {'epoch_id': 'E020_TRUNCATE', 'sequence': 20, 'logical_time': '2026-07-30T06:40:20Z', 'operation': 'truncate rewrite creates new content epoch'},
        {'epoch_id': 'E030_FULL_REWRITE', 'sequence': 30, 'logical_time': '2026-07-30T06:40:30Z', 'operation': 'complete rewrite creates another content epoch'},
        {'epoch_id': 'E040_RENAME_MOVE', 'sequence': 40, 'logical_time': '2026-07-30T06:40:40Z', 'operation': 'rename and directory move preserve lineage'},
        {'epoch_id': 'E050_STEALTH_MIDDLE', 'sequence': 50, 'logical_time': '2026-07-30T06:40:50Z', 'operation': 'same size and mtime, changed middle bytes'},
        {'epoch_id': 'E060_PARALLEL_SCAN', 'sequence': 60, 'logical_time': '2026-07-30T06:41:00Z', 'operation': 'parallel mutation during scan, reproduced by test driver'},
    ]

    late = FIX / 'search/late_needle.txt'
    late_token = b'OMEGA_NEEDLE_AFTER_49152'
    late_offset = 65536
    write_fixed(late, b'A' * late_offset + late_token + b'\n' + b'Z' * 8192)

    large = FIX / 'large/large_text_utf8.txt'
    large_size = 3 * 1024 * 1024 + 333
    large_data = bytearray(b'L' * large_size)
    large_hits = [(524288, b'OMEGA_LARGE_NEEDLE_ALPHA'), (2900000, b'OMEGA_LARGE_NEEDLE_OMEGA')]
    for off, token in large_hits:
        large_data[off - 1] = 10
        large_data[off:off + len(token)] = token
        large_data[off + len(token)] = 10
    write_fixed(large, bytes(large_data))

    huge = FIX / 'jsonl/very_large.jsonl'
    huge.parent.mkdir(parents=True, exist_ok=True)
    jsonl_count, jsonl_needle_offset, jsonl_token = make_jsonl(huge, 75000, 70000)

    append_path = FIX / 'append/append_only.jsonl'
    initial_rows = [json.dumps({'seq': i, 'epoch': 'E000_BASELINE', 'payload': 'a' * 40}, separators=(',', ':')) + '\n' for i in range(100)]
    write_fixed(append_path, ''.join(initial_rows).encode())
    append_v1 = snapshot('E000_BASELINE', 'append/append_only.jsonl', append_path)
    with append_path.open('ab') as f:
        for i in range(100, 150):
            f.write((json.dumps({'seq': i, 'epoch': 'E010_APPEND', 'payload': 'b' * 40}, separators=(',', ':')) + '\n').encode())
        f.flush(); os.fsync(f.fileno())
    set_mtime(append_path, T0_NS + 10_000_000_000)
    append_v2 = snapshot('E010_APPEND', 'append/append_only.jsonl', append_path)

    rewrite = FIX / 'rewrite/rewrite_target.txt'
    write_fixed(rewrite, (b'BASELINE-REWRITE-BODY\n' * 4096))
    rewrite_v1 = snapshot('E000_BASELINE', 'rewrite/rewrite_target.txt', rewrite)
    write_fixed(rewrite, b'TRUNCATED-EPOCH\n' * 8, T0_NS + 20_000_000_000)
    rewrite_v2 = snapshot('E020_TRUNCATE', 'rewrite/rewrite_target.txt', rewrite)
    write_fixed(rewrite, (b'FULL-REWRITE-EPOCH-OMEGA\n' * 5000), T0_NS + 30_000_000_000)
    rewrite_v3 = snapshot('E030_FULL_REWRITE', 'rewrite/rewrite_target.txt', rewrite)

    rename_old = FIX / 'rename/original/rename_source.txt'
    write_fixed(rename_old, b'RENAME-LINEAGE-CONTENT\n' * 32)
    rename_v1 = snapshot('E000_BASELINE', 'rename/original/rename_source.txt', rename_old)
    rename_new = FIX / 'rename/moved/deeper/rename_destination.txt'
    rename_new.parent.mkdir(parents=True, exist_ok=True)
    os.replace(rename_old, rename_new)
    set_mtime(rename_new, T0_NS + 40_000_000_000)
    rename_v2 = snapshot('E040_RENAME_MOVE', 'rename/moved/deeper/rename_destination.txt', rename_new)

    hard_src = FIX / 'identity/hardlink_source.bin'
    hard_alias = FIX / 'identity/hardlink_alias.bin'
    copy_path = FIX / 'identity/identical_copy_different_inode.bin'
    identity_data = (b'IDENTITY-CONTENT-OMEGA\0' * 4096)
    write_fixed(hard_src, identity_data)
    os.link(hard_src, hard_alias)
    shutil.copy2(hard_src, copy_path)

    valid_utf8 = FIX / 'encoding/valid_utf8.txt'
    write_fixed(valid_utf8, 'gültig – Ω – 日本語 – 🧪\n'.encode('utf-8'))
    invalid_utf8 = FIX / 'encoding/invalid_utf8.bin'
    write_fixed(invalid_utf8, b'valid-prefix\n\xff\xfe\xfaBROKEN-UTF8\nvalid-tail\n')

    valid_link = FIX / 'links/valid_symlink'
    broken_link = FIX / 'links/broken_symlink'
    valid_link.parent.mkdir(parents=True, exist_ok=True)
    valid_link.symlink_to('../search/late_needle.txt')
    broken_link.symlink_to('../missing/never_exists.txt')

    path_mentions = FIX / 'paths/absolute_mentions.txt'
    mentioned = [str(late), str(huge), str(rename_new), str(broken_link)]
    write_fixed(path_mentions, ('\n'.join(['ABSOLUTE PATH RELATIONSHIPS'] + mentioned + [mentioned[0]]) + '\n').encode())

    stealth = FIX / 'stealth/same_size_same_mtime.txt'
    stealth_initial_token = b'OMEGA_STEALTH_INITIAL'
    stealth_changed_token = b'OMEGA_STEALTH_CHANGED'
    if len(stealth_initial_token) != len(stealth_changed_token):
        raise RuntimeError('stealth fixture tokens must have identical byte length')
    stealth_initial = bytearray(b'S' * 16384)
    stealth_initial[100:100 + len(stealth_initial_token)] = stealth_initial_token
    write_fixed(stealth, bytes(stealth_initial))
    stealth_v1 = snapshot('E000_BASELINE', 'stealth/same_size_same_mtime.txt', stealth)
    original_stat = stealth.stat()
    stealth_final = bytearray(stealth.read_bytes())
    stealth_final[8192:8192 + len(stealth_changed_token)] = stealth_changed_token
    atomic_bytes(stealth, bytes(stealth_final))
    os.utime(stealth, ns=(original_stat.st_atime_ns, original_stat.st_mtime_ns))
    stealth_v2 = snapshot('E050_STEALTH_MIDDLE', 'stealth/same_size_same_mtime.txt', stealth)

    race = FIX / 'race/race_target.txt'
    race_data = bytearray(b'R' * (8 * 1024 * 1024))
    race_offset = 6 * 1024 * 1024
    race_token = b'OMEGA_RACE_LATE_NEEDLE'
    race_data[race_offset - 1] = 10
    race_data[race_offset:race_offset + len(race_token)] = race_token
    race_data[race_offset + len(race_token)] = 10
    write_fixed(race, bytes(race_data))
    race_v1 = snapshot('E000_BASELINE', 'race/race_target.txt', race)

    # Deterministic expected search hits.
    search_specs = []
    for path, tokens in [
        (late, [late_token]),
        (large, [x[1] for x in large_hits]),
        (huge, [jsonl_token.encode()]),
        (path_mentions, [x.encode() for x in mentioned]),
        (stealth, [b'OMEGA_STEALTH_CHANGED__']),
        (race, [race_token]),
    ]:
        data = path.read_bytes()
        for token in tokens:
            offsets = []
            start = 0
            while True:
                i = data.find(token, start)
                if i < 0: break
                offsets.append(i); start = i + 1
            search_specs.append({'path': str(path), 'relative_path': str(path.relative_to(ROOT)), 'term_utf8': token.decode('utf-8'), 'expected_byte_offsets': offsets, 'expected_count': len(offsets)})

    logical = {
        'late_needle': {'lineage_id': uid('lineage', 'late_needle'), 'paths': [late]},
        'large_text': {'lineage_id': uid('lineage', 'large_text'), 'paths': [large]},
        'very_large_jsonl': {'lineage_id': uid('lineage', 'very_large_jsonl'), 'paths': [huge]},
        'append_log': {'lineage_id': uid('lineage', 'append_log'), 'paths': [append_path]},
        'rewrite_target': {'lineage_id': uid('lineage', 'rewrite_target'), 'paths': [rewrite]},
        'rename_lineage': {'lineage_id': uid('lineage', 'rename_lineage'), 'paths': [rename_new], 'former_paths': [str(FIX / 'rename/original/rename_source.txt')]},
        'hardlink_source': {'lineage_id': uid('lineage', 'hardlink_source'), 'paths': [hard_src, hard_alias]},
        'identical_copy': {'lineage_id': uid('lineage', 'identical_copy'), 'paths': [copy_path]},
        'valid_utf8': {'lineage_id': uid('lineage', 'valid_utf8'), 'paths': [valid_utf8]},
        'invalid_utf8': {'lineage_id': uid('lineage', 'invalid_utf8'), 'paths': [invalid_utf8]},
        'valid_symlink': {'lineage_id': uid('lineage', 'valid_symlink'), 'paths': [valid_link]},
        'broken_symlink': {'lineage_id': uid('lineage', 'broken_symlink'), 'paths': [broken_link]},
        'path_mentions': {'lineage_id': uid('lineage', 'path_mentions'), 'paths': [path_mentions]},
        'stealth_middle_change': {'lineage_id': uid('lineage', 'stealth_middle_change'), 'paths': [stealth]},
        'parallel_race': {'lineage_id': uid('lineage', 'parallel_race'), 'paths': [race]},
    }

    objects = []
    for name, item in logical.items():
        for path in item['paths']:
            st = path.lstat()
            kind = 'symlink' if path.is_symlink() else 'regular'
            obj = {
                'logical_name': name,
                'path': str(path),
                'relative_path': str(path.relative_to(ROOT)),
                'path_object_id': uid('path', str(path.relative_to(ROOT))),
                'lineage_id': item['lineage_id'],
                'kind': kind,
                'size': st.st_size,
                'mtime_ns': st.st_mtime_ns,
                'device': st.st_dev,
                'inode': st.st_ino,
                'nlink': st.st_nlink,
            }
            if kind == 'symlink':
                obj['symlink_target'] = os.readlink(path)
                obj['target_exists'] = path.exists()
            else:
                obj['sha256'] = sha_file(path)
                obj['content_id'] = 'sha256:' + obj['sha256']
            objects.append(obj)

    by_path = {o['path']: o for o in objects}
    relationships = [
        {'type': 'HARDLINK_SAME_INODE', 'from_path_object_id': by_path[str(hard_src)]['path_object_id'], 'to_path_object_id': by_path[str(hard_alias)]['path_object_id'], 'expected_same_device_inode': True},
        {'type': 'SAME_CONTENT_DISTINCT_INODE', 'from_path_object_id': by_path[str(hard_src)]['path_object_id'], 'to_path_object_id': by_path[str(copy_path)]['path_object_id'], 'expected_same_sha256': True, 'expected_distinct_inode': True},
        {'type': 'SYMLINK_TARGETS', 'from_path_object_id': by_path[str(valid_link)]['path_object_id'], 'to_path_object_id': by_path[str(late)]['path_object_id'], 'target_text': '../search/late_needle.txt'},
        {'type': 'BROKEN_SYMLINK_TARGET_MISSING', 'from_path_object_id': by_path[str(broken_link)]['path_object_id'], 'target_text': '../missing/never_exists.txt'},
        {'type': 'RENAMED_FROM', 'lineage_id': logical['rename_lineage']['lineage_id'], 'from_path': str(FIX / 'rename/original/rename_source.txt'), 'to_path': str(rename_new), 'content_sha256_unchanged': sha_file(rename_v1_path := Path(rename_v1['path'])) == sha_file(rename_new)},
    ]
    for p in mentioned:
        relationships.append({'type': 'PATH_MENTIONS', 'from_path_object_id': by_path[str(path_mentions)]['path_object_id'], 'mentioned_absolute_path': p, 'expected_occurrences': path_mentions.read_text('utf-8').count(p)})

    versions = [
        {'logical_name': 'append_log', 'lineage_id': logical['append_log']['lineage_id'], 'version_number': 1, 'version_id': uid('version', 'append_log:v1:' + append_v1['sha256']), 'content_epoch': 'CE_APPEND_1', **append_v1},
        {'logical_name': 'append_log', 'lineage_id': logical['append_log']['lineage_id'], 'version_number': 2, 'version_id': uid('version', 'append_log:v2:' + append_v2['sha256']), 'content_epoch': 'CE_APPEND_1', 'mutation_kind': 'append', **append_v2},
        {'logical_name': 'rewrite_target', 'lineage_id': logical['rewrite_target']['lineage_id'], 'version_number': 1, 'version_id': uid('version', 'rewrite:v1:' + rewrite_v1['sha256']), 'content_epoch': 'CE_REWRITE_1', **rewrite_v1},
        {'logical_name': 'rewrite_target', 'lineage_id': logical['rewrite_target']['lineage_id'], 'version_number': 2, 'version_id': uid('version', 'rewrite:v2:' + rewrite_v2['sha256']), 'content_epoch': 'CE_REWRITE_2', 'mutation_kind': 'truncate', **rewrite_v2},
        {'logical_name': 'rewrite_target', 'lineage_id': logical['rewrite_target']['lineage_id'], 'version_number': 3, 'version_id': uid('version', 'rewrite:v3:' + rewrite_v3['sha256']), 'content_epoch': 'CE_REWRITE_3', 'mutation_kind': 'full_rewrite', **rewrite_v3},
        {'logical_name': 'rename_lineage', 'lineage_id': logical['rename_lineage']['lineage_id'], 'version_number': 1, 'version_id': uid('version', 'rename:v1:' + rename_v1['sha256']), 'content_epoch': 'CE_RENAME_1', **rename_v1},
        {'logical_name': 'rename_lineage', 'lineage_id': logical['rename_lineage']['lineage_id'], 'version_number': 2, 'version_id': uid('version', 'rename:v2:' + rename_v2['sha256']), 'content_epoch': 'CE_RENAME_1', 'mutation_kind': 'rename_move', **rename_v2},
        {'logical_name': 'stealth_middle_change', 'lineage_id': logical['stealth_middle_change']['lineage_id'], 'version_number': 1, 'version_id': uid('version', 'stealth:v1:' + stealth_v1['sha256']), 'content_epoch': 'CE_STEALTH_1', **stealth_v1},
        {'logical_name': 'stealth_middle_change', 'lineage_id': logical['stealth_middle_change']['lineage_id'], 'version_number': 2, 'version_id': uid('version', 'stealth:v2:' + stealth_v2['sha256']), 'content_epoch': 'CE_STEALTH_2', 'mutation_kind': 'same_size_same_mtime_middle_change', **stealth_v2},
        {'logical_name': 'parallel_race', 'lineage_id': logical['parallel_race']['lineage_id'], 'version_number': 1, 'version_id': uid('version', 'race:v1:' + race_v1['sha256']), 'content_epoch': 'CE_RACE_1', **race_v1},
    ]

    mutation_plan = {
        'schema_version': '1.0',
        'steps': [
            {'sequence': 10, 'id': 'APPEND_ONLY', 'status': 'PASS', 'target': str(append_path), 'operation': 'append records 100..149; bytes 0..v1_size-1 remain identical', 'expected': {'same_content_epoch': True, 'prefix_sha256': append_v1['sha256'], 'before_bytes': append_v1['bytes'], 'after_bytes': append_v2['bytes']}},
            {'sequence': 20, 'id': 'TRUNCATE', 'status': 'PASS', 'target': str(rewrite), 'operation': 'replace long baseline with short body', 'expected': {'new_content_epoch': True}},
            {'sequence': 30, 'id': 'FULL_REWRITE', 'status': 'PASS', 'target': str(rewrite), 'operation': 'replace complete short body with new long body', 'expected': {'new_content_epoch': True}},
            {'sequence': 40, 'id': 'RENAME_MOVE', 'status': 'PASS', 'from': str(FIX / 'rename/original/rename_source.txt'), 'to': str(rename_new), 'expected': {'lineage_id_stable': logical['rename_lineage']['lineage_id'], 'content_hash_unchanged': True}},
            {'sequence': 50, 'id': 'SAME_SIZE_MTIME_MIDDLE_CHANGE', 'status': 'PASS', 'target': str(stealth), 'expected': {'size_equal': stealth_v1['bytes'] == stealth_v2['bytes'], 'mtime_equal': stealth_v1['mtime_ns'] == stealth_v2['mtime_ns'], 'sha256_changed': stealth_v1['sha256'] != stealth_v2['sha256'], 'new_content_epoch': True}},
            {'sequence': 60, 'id': 'PARALLEL_CHANGE_DURING_SCAN', 'status': 'UNKNOWN', 'target': str(race), 'operation': 'test_driver resets baseline, scans in chunks and mutates after scan start', 'expected': {'driver_classification': 'CHANGED_DURING_SCAN'}},
        ],
        'reproduce_command': ['python3', str(ROOT / 'scripts/test_driver.py'), '--mode', 'lab'],
    }

    corpus_manifest = {
        'schema_version': '1.0',
        'generated_utc': generated,
        'root': str(ROOT),
        'truth_model': {'path_object_id': 'UUIDv5 over relative path', 'lineage_id': 'UUIDv5 over logical lineage', 'content_id': 'full SHA-256', 'version_id': 'UUIDv5 over logical version and full hash'},
        'requirements': {
            'search_term_beyond_49152': {'status': 'PASS', 'path': str(late), 'offset': late_offset, 'term': late_token.decode()},
            'text_over_2_5MiB': {'status': 'PASS', 'path': str(large), 'bytes': large.stat().st_size},
            'very_large_jsonl': {'status': 'PASS', 'path': str(huge), 'bytes': huge.stat().st_size, 'lines': jsonl_count, 'deep_needle_offset': jsonl_needle_offset},
            'append_only_growth': {'status': 'PASS'},
            'truncate_and_rewrite': {'status': 'PASS'},
            'rename_and_move': {'status': 'PASS'},
            'hardlinks': {'status': 'PASS'},
            'identical_copy_distinct_inode': {'status': 'PASS'},
            'symlink_and_broken_symlink': {'status': 'PASS'},
            'valid_and_invalid_utf8': {'status': 'PASS'},
            'absolute_path_mentions': {'status': 'PASS'},
            'same_size_mtime_changed_middle': {'status': 'PASS'},
            'parallel_changes_during_scan': {'status': 'UNKNOWN', 'reason': 'validated by independent test driver'},
            'multiple_version_epochs': {'status': 'PASS', 'epoch_count': len(epochs)},
        },
        'counts': {'objects': len(objects), 'relationships': len(relationships), 'versions': len(versions), 'epochs': len(epochs), 'search_expectations': len(search_specs)},
        'gate': {'omega_test_status': 'BLOCKED', 'marker': '/root/werkraum/_gpt/gesamtatlas/omega/checkpoints/CORE_READY.json'},
    }

    identities = {
        'schema_version': '1.0',
        'objects': objects,
        'logical_lineages': {k: {'lineage_id': v['lineage_id'], 'active_paths': [str(x) for x in v['paths']], 'former_paths': v.get('former_paths', [])} for k, v in logical.items()},
        'hardlink_expectation': {'paths': [str(hard_src), str(hard_alias)], 'same_device': True, 'same_inode': True, 'distinct_path_object_ids': True},
        'copy_expectation': {'paths': [str(hard_src), str(copy_path)], 'same_sha256': True, 'distinct_inode': True, 'distinct_path_object_ids': True},
    }

    status_matrix = {
        'schema_version': '1.0',
        'allowed_statuses': sorted(ALLOWED),
        'overall_lab_status': 'UNKNOWN',
        'omega_execution': 'BLOCKED',
        'items': [{'id': k, 'status': v['status'], 'evidence': v} for k, v in corpus_manifest['requirements'].items()],
        'blockers': [
            {'id': 'OMEGA_CORE_GATE', 'status': 'BLOCKED', 'reason': 'CORE_READY.json missing and no explicit monsterlabor inbox permission.'},
            {'id': 'ACTION_HISTORY_SESSION_ISOLATION', 'status': 'BLOCKED', 'reason': 'Published MCP schema cannot pass required session_intent/new_session_reason; actions are compatibility-attributed.'},
        ],
    }

    original_ranges = []
    for obj in objects:
        path = Path(obj['path'])
        if obj['kind'] == 'symlink':
            original_ranges.append({
                'path_object_id': obj['path_object_id'],
                'path': obj['path'],
                'access_mode': 'readlink',
                'expected_target_text': obj['symlink_target'],
                'expected_target_exists': obj['target_exists'],
            })
            continue
        data = path.read_bytes()
        page_size = 65536
        pages = []
        for page_index, start in enumerate(range(0, len(data), page_size)):
            chunk = data[start:start + page_size]
            pages.append({
                'page_index': page_index,
                'start_byte': start,
                'end_byte_exclusive': start + len(chunk),
                'bytes': len(chunk),
                'sha256': sha_bytes(chunk),
            })
        original_ranges.append({
            'path_object_id': obj['path_object_id'],
            'path': obj['path'],
            'access_mode': 'bytes',
            'full_range': {'start_byte': 0, 'end_byte_exclusive': len(data), 'bytes': len(data), 'sha256': sha_bytes(data)},
            'page_size': page_size,
            'page_count': len(pages),
            'pages': pages,
        })

    test_cases = []
    for logical_name, item in logical.items():
        path_ids = [by_path[str(p)]['path_object_id'] for p in item['paths']]
        case_versions = [v for v in versions if v['logical_name'] == logical_name]
        case_search = [h for h in search_specs if h['path'] in {str(p) for p in item['paths']}]
        case_relations = [r for r in relationships if any(pid in json.dumps(r, ensure_ascii=False) for pid in path_ids) or any(str(p) in json.dumps(r, ensure_ascii=False) for p in item['paths'])]
        case_mutations = [s for s in mutation_plan['steps'] if any(str(p) in json.dumps(s, ensure_ascii=False) for p in item['paths']) or logical_name.lower() in s['id'].lower()]
        expected_outcome = {'status': 'PASS'}
        if logical_name == 'invalid_utf8':
            expected_outcome = {'status': 'PASS', 'decode_utf8': 'ERROR_EXPECTED'}
        elif logical_name == 'broken_symlink':
            expected_outcome = {'status': 'PASS', 'target_exists': False}
        elif logical_name == 'parallel_race':
            expected_outcome = {'status': 'PASS', 'scan_classification': 'CHANGED_DURING_SCAN'}
        test_cases.append({
            'fixture_id': uid('fixture', logical_name),
            'logical_name': logical_name,
            'initial_state': case_versions[0] if case_versions else {'active_path_object_ids': path_ids},
            'mutation_steps': case_mutations,
            'expected_object_identity': {'lineage_id': item['lineage_id'], 'path_object_ids': path_ids},
            'expected_versions': case_versions,
            'expected_relations': case_relations,
            'expected_search_hits': case_search,
            'expected_original_ranges': [r for r in original_ranges if r['path_object_id'] in path_ids],
            'expected_error_or_success': expected_outcome,
        })

    corpus_manifest['counts']['original_range_objects'] = len(original_ranges)
    corpus_manifest['counts']['test_cases'] = len(test_cases)
    atomic_json(MAN / 'CORPUS_MANIFEST.json', corpus_manifest)
    atomic_json(MAN / 'OBJECT_IDENTITIES.json', identities)
    atomic_json(MAN / 'EXPECTED_VERSIONS.json', {'schema_version': '1.0', 'versions': versions})
    atomic_json(MAN / 'EXPECTED_EPOCHS.json', {'schema_version': '1.0', 'epochs': epochs})
    atomic_json(MAN / 'EXPECTED_SEARCH_HITS.json', {'schema_version': '1.0', 'hits': search_specs})
    atomic_json(MAN / 'EXPECTED_RELATIONSHIPS.json', {'schema_version': '1.0', 'relationships': relationships})
    atomic_json(MAN / 'EXPECTED_ORIGINAL_RANGES.json', {'schema_version': '1.0', 'ranges': original_ranges})
    atomic_json(MAN / 'TEST_CASES.json', {'schema_version': '1.0', 'test_cases': test_cases})
    atomic_json(MAN / 'MUTATION_PLAN.json', mutation_plan)
    atomic_json(MAN / 'STATUS_MATRIX.json', status_matrix)
    atomic_json(STATE / 'CURRENT_EPOCH.json', {'schema_version': '1.0', 'current_epoch': 'E060_PARALLEL_SCAN', 'parallel_scan_mutation_pending_driver': True})
    contract_path = ROOT / 'OMEGA_ADAPTER_CONTRACT.json'
    if not contract_path.exists():
        atomic_json(contract_path, {
            'schema_version': '1.0',
            'status': 'BLOCKED',
            'gate_marker': '/root/werkraum/_gpt/gesamtatlas/omega/checkpoints/CORE_READY.json',
            'required_marker_field': 'monsterlabor_adapter.result_json',
            'contract': 'After Omega ingests/scans this laboratory, CORE_READY or explicit inbox permission must name a read-only result JSON. test_driver --mode omega compares that result against EXPECTED_* manifests. It performs no product mutation or service restart.'
        })
    status = json.loads((ROOT / 'STATUS.json').read_text('utf-8'))
    status.update({'updated_utc': generated, 'laboratory_build': 'PASS', 'laboratory_validation': 'UNKNOWN', 'omega_execution': 'BLOCKED'})
    atomic_json(ROOT / 'STATUS.json', status)
    print(json.dumps({'ok': True, 'root': str(ROOT), 'objects': len(objects), 'relationships': len(relationships), 'versions': len(versions), 'epochs': len(epochs), 'large_text_bytes': large.stat().st_size, 'jsonl_bytes': huge.stat().st_size, 'jsonl_lines': jsonl_count}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    build()
