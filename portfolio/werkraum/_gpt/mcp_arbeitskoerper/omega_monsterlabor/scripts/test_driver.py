#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path('/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor')
MAN = ROOT / 'manifests'
REPORTS = ROOT / 'reports'
CORE = Path('/root/werkraum/_gpt/gesamtatlas/omega/checkpoints/CORE_READY.json')
INBOX = Path('/root/werkraum/_gpt/mcp_arbeitskoerper/coordination/inbox')
SID = 'chatgpt-20260730T063100Z-omega-monsterlabor'
ALLOWED = {'PASS', 'FAIL', 'UNKNOWN', 'BLOCKED'}


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    return json.loads(path.read_text('utf-8'))


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
    if path.read_bytes() != data:
        raise RuntimeError(f'readback mismatch: {path}')


def result(test_id: str, ok: bool | None, expected=None, actual=None, detail: str = '') -> dict:
    status = 'PASS' if ok is True else ('FAIL' if ok is False else 'UNKNOWN')
    return {'id': test_id, 'status': status, 'expected': expected, 'actual': actual, 'detail': detail}


def find_permission() -> dict | None:
    owner_session = 'chatgpt-20260730T060500Z-gesamtatlas-eli5-vollverwirklichung'
    for path in sorted(INBOX.glob('*.json'), reverse=True):
        try:
            data = load(path)
        except Exception:
            continue
        if data.get('from_session_id') != owner_session or data.get('to_session_id') != SID:
            continue
        authorization = data.get('authorization') if isinstance(data.get('authorization'), dict) else {}
        explicitly_allowed = (
            data.get('execute_against_omega') is True
            or data.get('monsterlabor_permission') is True
            or authorization.get('execute_against_omega') is True
        )
        if explicitly_allowed:
            data['_path'] = str(path)
            return data
    return None


def run_race_test() -> dict:
    active = ROOT / 'fixtures/race/race_target.txt'
    baseline = ROOT / 'snapshots/E000_BASELINE/race/race_target.txt'
    shutil.copy2(baseline, active)
    before = active.stat()
    start_hash = sha_file(active)
    trigger = threading.Event()
    done = threading.Event()
    mutation = b'OMEGA_PARALLEL_MUTATION'

    def writer():
        trigger.wait(5)
        with active.open('r+b') as f:
            f.seek(4 * 1024 * 1024)
            f.write(mutation)
            f.flush(); os.fsync(f.fileno())
        done.set()

    t = threading.Thread(target=writer, daemon=True)
    t.start()
    observed = hashlib.sha256()
    chunks = 0
    with active.open('rb') as f:
        while True:
            chunk = f.read(256 * 1024)
            if not chunk: break
            observed.update(chunk)
            chunks += 1
            if chunks == 2:
                trigger.set()
            time.sleep(0.002)
    done.wait(5)
    t.join(5)
    after = active.stat()
    final_hash = sha_file(active)
    changed = final_hash != start_hash
    classification = 'CHANGED_DURING_SCAN' if changed and done.is_set() else 'NOT_DETECTED'
    scan_hash_matches_start = observed.hexdigest() == start_hash
    scan_hash_matches_final = observed.hexdigest() == final_hash
    shutil.copy2(baseline, active)
    return {
        'status': 'PASS' if classification == 'CHANGED_DURING_SCAN' else 'FAIL',
        'classification': classification,
        'before_size': before.st_size,
        'after_size': after.st_size,
        'start_sha256': start_hash,
        'scan_sha256': observed.hexdigest(),
        'final_sha256': final_hash,
        'scan_hash_matches_start': scan_hash_matches_start,
        'scan_hash_matches_final': scan_hash_matches_final,
        'writer_completed': done.is_set(),
        'restored_sha256': sha_file(active),
        'baseline_sha256': sha_file(baseline),
    }


def lab_mode() -> tuple[dict, int]:
    identities = load(MAN / 'OBJECT_IDENTITIES.json')
    versions = load(MAN / 'EXPECTED_VERSIONS.json')['versions']
    epochs = load(MAN / 'EXPECTED_EPOCHS.json')['epochs']
    searches = load(MAN / 'EXPECTED_SEARCH_HITS.json')['hits']
    rels = load(MAN / 'EXPECTED_RELATIONSHIPS.json')['relationships']
    ranges = load(MAN / 'EXPECTED_ORIGINAL_RANGES.json')['ranges']
    test_cases = load(MAN / 'TEST_CASES.json')['test_cases']
    mutation = load(MAN / 'MUTATION_PLAN.json')
    corpus = load(MAN / 'CORPUS_MANIFEST.json')
    tests = []

    # Exact active object truth.
    for obj in identities['objects']:
        p = Path(obj['path'])
        exists = p.is_symlink() or p.exists()
        tests.append(result('OBJECT_EXISTS:' + obj['relative_path'], exists, True, exists))
        if not exists: continue
        st = p.lstat()
        tests.append(result('OBJECT_KIND:' + obj['relative_path'], ('symlink' if p.is_symlink() else 'regular') == obj['kind'], obj['kind'], 'symlink' if p.is_symlink() else 'regular'))
        if p.is_symlink():
            tests.append(result('SYMLINK_TEXT:' + obj['relative_path'], os.readlink(p) == obj['symlink_target'], obj['symlink_target'], os.readlink(p)))
            tests.append(result('SYMLINK_TARGET_EXISTENCE:' + obj['relative_path'], p.exists() == obj['target_exists'], obj['target_exists'], p.exists()))
        else:
            actual_sha = sha_file(p)
            tests.append(result('SHA256:' + obj['relative_path'], actual_sha == obj['sha256'], obj['sha256'], actual_sha))
            tests.append(result('SIZE:' + obj['relative_path'], st.st_size == obj['size'], obj['size'], st.st_size))

    # Complete original-byte ranges and deterministic page truth.
    for spec in ranges:
        p = Path(spec['path'])
        if spec['access_mode'] == 'readlink':
            actual_target = os.readlink(p)
            tests.append(result('ORIGINAL_READLINK:' + p.name, actual_target == spec['expected_target_text'] and p.exists() == spec['expected_target_exists'], {'target': spec['expected_target_text'], 'exists': spec['expected_target_exists']}, {'target': actual_target, 'exists': p.exists()}))
            continue
        data = p.read_bytes()
        full = spec['full_range']
        tests.append(result('ORIGINAL_FULL_RANGE:' + p.name, len(data) == full['bytes'] and hashlib.sha256(data).hexdigest() == full['sha256'], full, {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}))
        cursor = 0
        pages_ok = True
        for page in spec['pages']:
            chunk = data[page['start_byte']:page['end_byte_exclusive']]
            pages_ok = pages_ok and page['start_byte'] == cursor and len(chunk) == page['bytes'] and hashlib.sha256(chunk).hexdigest() == page['sha256']
            cursor = page['end_byte_exclusive']
        pages_ok = pages_ok and cursor == len(data) and len(spec['pages']) == spec['page_count']
        tests.append(result('ORIGINAL_PAGES:' + p.name, pages_ok, {'continuous_to': len(data), 'page_count': spec['page_count']}, {'continuous_to': cursor, 'page_count': len(spec['pages'])}))

    required_case_fields = {'fixture_id', 'logical_name', 'initial_state', 'mutation_steps', 'expected_object_identity', 'expected_versions', 'expected_relations', 'expected_search_hits', 'expected_original_ranges', 'expected_error_or_success'}
    fixture_ids = [x.get('fixture_id') for x in test_cases]
    logical_names = [x.get('logical_name') for x in test_cases]
    tests.append(result('TEST_CASE_IDS_UNIQUE', len(fixture_ids) == len(set(fixture_ids)) and None not in fixture_ids, 'unique non-null', fixture_ids))
    tests.append(result('TEST_CASE_COVERAGE', set(logical_names) == set(identities['logical_lineages']), sorted(identities['logical_lineages']), sorted(logical_names)))
    tests.append(result('TEST_CASE_REQUIRED_FIELDS', all(required_case_fields.issubset(x) for x in test_cases), sorted(required_case_fields), [sorted(set(x) & required_case_fields) for x in test_cases]))

    # Search offsets and counts.
    for spec in searches:
        p = Path(spec['path'])
        token = spec['term_utf8'].encode('utf-8')
        data = p.read_bytes()
        found = []
        start = 0
        while True:
            i = data.find(token, start)
            if i < 0: break
            found.append(i); start = i + 1
        tests.append(result('SEARCH:' + spec['relative_path'] + ':' + spec['term_utf8'], found == spec['expected_byte_offsets'], spec['expected_byte_offsets'], found))

    late = corpus['requirements']['search_term_beyond_49152']
    tests.append(result('LATE_NEEDLE_BOUNDARY', late['offset'] > 49152, '>49152', late['offset']))
    big = corpus['requirements']['text_over_2_5MiB']
    tests.append(result('TEXT_OVER_2_5_MIB', big['bytes'] > 2.5 * 1024 * 1024, '>2621440', big['bytes']))

    # Full JSONL validity, not a cute little prefix sample pretending to be science.
    huge = Path(corpus['requirements']['very_large_jsonl']['path'])
    line_count = 0
    json_errors = []
    with huge.open('rb') as f:
        for line_count, line in enumerate(f, 1):
            try: json.loads(line)
            except Exception as e:
                json_errors.append({'line': line_count, 'error': repr(e)})
                if len(json_errors) >= 5: break
    tests.append(result('JSONL_FULL_VALIDITY', not json_errors and line_count == corpus['requirements']['very_large_jsonl']['lines'], {'lines': corpus['requirements']['very_large_jsonl']['lines'], 'errors': 0}, {'lines': line_count, 'errors': json_errors}))

    # Version/epoch invariants.
    by_name = {}
    for v in versions: by_name.setdefault(v['logical_name'], []).append(v)
    append_v = sorted(by_name['append_log'], key=lambda x: x['version_number'])
    a1, a2 = map(lambda x: Path(x['path']).read_bytes(), append_v)
    tests.append(result('APPEND_PREFIX_UNCHANGED', a2[:len(a1)] == a1 and len(a2) > len(a1), {'prefix_unchanged': True, 'grew': True}, {'prefix_unchanged': a2[:len(a1)] == a1, 'before': len(a1), 'after': len(a2)}))
    tests.append(result('APPEND_EPOCH_STABLE', append_v[0]['content_epoch'] == append_v[1]['content_epoch'], append_v[0]['content_epoch'], append_v[1]['content_epoch']))

    rewrite_v = sorted(by_name['rewrite_target'], key=lambda x: x['version_number'])
    rewrite_epochs = [x['content_epoch'] for x in rewrite_v]
    tests.append(result('REWRITE_NEW_EPOCHS', len(set(rewrite_epochs)) == 3, 3, len(set(rewrite_epochs))))
    tests.append(result('TRUNCATE_SIZE_DROP', rewrite_v[1]['bytes'] < rewrite_v[0]['bytes'], '<baseline', {'baseline': rewrite_v[0]['bytes'], 'truncate': rewrite_v[1]['bytes']}))

    rename_v = sorted(by_name['rename_lineage'], key=lambda x: x['version_number'])
    old = ROOT / 'fixtures/rename/original/rename_source.txt'
    new = ROOT / 'fixtures/rename/moved/deeper/rename_destination.txt'
    tests.append(result('RENAME_OLD_ABSENT_NEW_PRESENT', not old.exists() and new.exists(), {'old': False, 'new': True}, {'old': old.exists(), 'new': new.exists()}))
    tests.append(result('RENAME_LINEAGE_STABLE', rename_v[0]['lineage_id'] == rename_v[1]['lineage_id'], rename_v[0]['lineage_id'], rename_v[1]['lineage_id']))
    tests.append(result('RENAME_CONTENT_STABLE', rename_v[0]['sha256'] == rename_v[1]['sha256'], rename_v[0]['sha256'], rename_v[1]['sha256']))

    stealth_v = sorted(by_name['stealth_middle_change'], key=lambda x: x['version_number'])
    stealth_truth = {'same_size': stealth_v[0]['bytes'] == stealth_v[1]['bytes'], 'same_mtime': stealth_v[0]['mtime_ns'] == stealth_v[1]['mtime_ns'], 'hash_changed': stealth_v[0]['sha256'] != stealth_v[1]['sha256'], 'epoch_changed': stealth_v[0]['content_epoch'] != stealth_v[1]['content_epoch']}
    tests.append(result('STEALTH_SAME_SIZE_MTIME_CHANGED_MIDDLE', all(stealth_truth.values()), {'same_size': True, 'same_mtime': True, 'hash_changed': True, 'epoch_changed': True}, stealth_truth))

    # Inode semantics.
    hard_a, hard_b = map(Path, identities['hardlink_expectation']['paths'])
    copy_a, copy_b = map(Path, identities['copy_expectation']['paths'])
    ha, hb, ca, cb = hard_a.stat(), hard_b.stat(), copy_a.stat(), copy_b.stat()
    tests.append(result('HARDLINK_SAME_DEVICE_INODE', (ha.st_dev, ha.st_ino) == (hb.st_dev, hb.st_ino), 'same', [(ha.st_dev, ha.st_ino), (hb.st_dev, hb.st_ino)]))
    tests.append(result('COPY_SAME_CONTENT_DISTINCT_INODE', sha_file(copy_a) == sha_file(copy_b) and (ca.st_dev, ca.st_ino) != (cb.st_dev, cb.st_ino), {'same_sha256': True, 'distinct_inode': True}, {'same_sha256': sha_file(copy_a) == sha_file(copy_b), 'inodes': [(ca.st_dev, ca.st_ino), (cb.st_dev, cb.st_ino)]}))

    # Encoding.
    valid = ROOT / 'fixtures/encoding/valid_utf8.txt'
    invalid = ROOT / 'fixtures/encoding/invalid_utf8.bin'
    valid_ok = True
    try: valid.read_bytes().decode('utf-8')
    except UnicodeDecodeError: valid_ok = False
    invalid_rejected = False
    try: invalid.read_bytes().decode('utf-8')
    except UnicodeDecodeError: invalid_rejected = True
    tests.append(result('VALID_UTF8_ACCEPTED', valid_ok, True, valid_ok))
    tests.append(result('INVALID_UTF8_REJECTED', invalid_rejected, True, invalid_rejected))

    # Relationship proof, including duplicate absolute mention count.
    mention_text = (ROOT / 'fixtures/paths/absolute_mentions.txt').read_text('utf-8')
    for rel in rels:
        if rel['type'] == 'PATH_MENTIONS':
            actual = mention_text.count(rel['mentioned_absolute_path'])
            tests.append(result('PATH_MENTIONS:' + rel['mentioned_absolute_path'], actual == rel['expected_occurrences'], rel['expected_occurrences'], actual))

    # Epoch sequence is exact and strictly increasing.
    seq = [x['sequence'] for x in epochs]
    tests.append(result('EPOCH_TIMELINE_STRICT', seq == sorted(seq) and len(seq) == len(set(seq)), 'strict unique ascending', seq))
    tests.append(result('MUTATION_STATUSES_ENUM', all(x['status'] in ALLOWED for x in mutation['steps']), sorted(ALLOWED), [x['status'] for x in mutation['steps']]))

    race = run_race_test()
    tests.append({'id': 'PARALLEL_CHANGE_DURING_SCAN', 'status': race['status'], 'expected': 'CHANGED_DURING_SCAN', 'actual': race['classification'], 'detail': race})

    failures = [x for x in tests if x['status'] == 'FAIL']
    unknown = [x for x in tests if x['status'] == 'UNKNOWN']
    overall = 'FAIL' if failures else ('UNKNOWN' if unknown else 'PASS')
    report = {
        'schema_version': '1.0', 'mode': 'lab', 'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
        'overall_status': overall, 'test_count': len(tests), 'pass_count': sum(x['status'] == 'PASS' for x in tests),
        'fail_count': len(failures), 'unknown_count': len(unknown), 'tests': tests,
        'truth_boundary': 'Validates only the isolated synthetic laboratory. No Omega product file, service, database or protocol was touched.'
    }
    atomic_json(REPORTS / 'LAB_TEST_REPORT.json', report)
    md = [f'# Monsterlabor Lab-Test: {overall}', '', f'- Tests: {len(tests)}', f'- PASS: {report["pass_count"]}', f'- FAIL: {report["fail_count"]}', f'- UNKNOWN: {report["unknown_count"]}', '', '## Ergebnisse']
    md += [f'- **{x["status"]}** `{x["id"]}`' for x in tests]
    (REPORTS / 'LAB_TEST_REPORT.md').write_text('\n'.join(md) + '\n', 'utf-8')
    status = load(ROOT / 'STATUS.json')
    status['updated_utc'] = report['generated_utc']; status['laboratory_validation'] = overall
    atomic_json(ROOT / 'STATUS.json', status)
    return report, 0 if overall == 'PASS' else 1


def normalize_omega_result(data: dict) -> dict:
    return {
        'objects': data.get('objects', []),
        'search_hits': data.get('search_hits', []),
        'relationships': data.get('relationships', []),
        'versions': data.get('versions', []),
        'epochs': data.get('epochs', []),
    }


def omega_mode() -> tuple[dict, int]:
    permission = find_permission()
    if not CORE.exists() and not permission:
        report = {'schema_version': '1.0', 'mode': 'omega', 'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'overall_status': 'BLOCKED', 'reason': 'CORE_READY.json missing and no explicit Coordination-Inbox permission for monsterlabor.', 'core_marker': str(CORE)}
        atomic_json(REPORTS / 'OMEGA_TEST_REPORT.json', report)
        return report, 3
    gate = load(CORE) if CORE.exists() else permission
    adapter = gate.get('monsterlabor_adapter') if isinstance(gate, dict) else None
    result_path = adapter.get('result_json') if isinstance(adapter, dict) else None
    if not result_path:
        report = {'schema_version': '1.0', 'mode': 'omega', 'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'overall_status': 'BLOCKED', 'reason': 'Gate exists, but no read-only monsterlabor_adapter.result_json was declared. No interface is invented.', 'gate_source': str(CORE) if CORE.exists() else permission.get('_path')}
        atomic_json(REPORTS / 'OMEGA_TEST_REPORT.json', report)
        return report, 3
    rp = Path(result_path)
    if not rp.is_file():
        report = {'schema_version': '1.0', 'mode': 'omega', 'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'overall_status': 'BLOCKED', 'reason': 'Declared Omega result JSON does not exist.', 'result_json': str(rp)}
        atomic_json(REPORTS / 'OMEGA_TEST_REPORT.json', report)
        return report, 3

    omega = normalize_omega_result(load(rp))
    expected_ids = load(MAN / 'OBJECT_IDENTITIES.json')['objects']
    expected_search = load(MAN / 'EXPECTED_SEARCH_HITS.json')['hits']
    expected_rel = load(MAN / 'EXPECTED_RELATIONSHIPS.json')['relationships']
    expected_ver = load(MAN / 'EXPECTED_VERSIONS.json')['versions']
    expected_epochs = load(MAN / 'EXPECTED_EPOCHS.json')['epochs']
    tests = []

    omega_objects = {x.get('path_object_id'): x for x in omega['objects']}
    for obj in expected_ids:
        actual = omega_objects.get(obj['path_object_id'])
        tests.append(result('OMEGA_OBJECT:' + obj['relative_path'], actual is not None, obj['path_object_id'], actual and actual.get('path_object_id')))
        if actual and obj['kind'] == 'regular':
            tests.append(result('OMEGA_OBJECT_SHA:' + obj['relative_path'], actual.get('sha256') == obj['sha256'], obj['sha256'], actual.get('sha256')))

    search_key = lambda x: (x.get('path') or x.get('relative_path'), x.get('term_utf8'))
    omega_search = {search_key(x): x for x in omega['search_hits']}
    for exp in expected_search:
        actual = omega_search.get((exp['path'], exp['term_utf8'])) or omega_search.get((exp['relative_path'], exp['term_utf8']))
        tests.append(result('OMEGA_SEARCH:' + exp['relative_path'] + ':' + exp['term_utf8'], actual is not None and actual.get('byte_offsets') == exp['expected_byte_offsets'], exp['expected_byte_offsets'], actual and actual.get('byte_offsets')))

    # Relationship/version/epoch sets compare canonical JSON fingerprints.
    def fps(rows):
        return {hashlib.sha256(json.dumps(x, sort_keys=True, ensure_ascii=False).encode()).hexdigest() for x in rows}
    tests.append(result('OMEGA_RELATIONSHIPS_COMPLETE', fps(expected_rel).issubset(fps(omega['relationships'])), len(expected_rel), len(omega['relationships'])))
    expected_version_ids = {x['version_id'] for x in expected_ver}
    actual_version_ids = {x.get('version_id') for x in omega['versions']}
    tests.append(result('OMEGA_VERSIONS_COMPLETE', expected_version_ids.issubset(actual_version_ids), sorted(expected_version_ids), sorted(x for x in actual_version_ids if x)))
    expected_epoch_ids = {x['epoch_id'] for x in expected_epochs}
    actual_epoch_ids = {x.get('epoch_id') for x in omega['epochs']}
    tests.append(result('OMEGA_EPOCHS_COMPLETE', expected_epoch_ids.issubset(actual_epoch_ids), sorted(expected_epoch_ids), sorted(x for x in actual_epoch_ids if x)))

    failures = [x for x in tests if x['status'] == 'FAIL']
    overall = 'FAIL' if failures else 'PASS'
    report = {'schema_version': '1.0', 'mode': 'omega', 'generated_utc': dt.datetime.now(dt.timezone.utc).isoformat(), 'overall_status': overall, 'result_json': str(rp), 'test_count': len(tests), 'pass_count': sum(x['status'] == 'PASS' for x in tests), 'fail_count': len(failures), 'tests': tests, 'truth_boundary': 'Read-only comparison of an owner-declared Omega result JSON. The driver did not restart services or mutate product data.'}
    atomic_json(REPORTS / 'OMEGA_TEST_REPORT.json', report)
    return report, 0 if overall == 'PASS' else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['lab', 'omega'], default='lab')
    args = ap.parse_args()
    report, code = lab_mode() if args.mode == 'lab' else omega_mode()
    print(json.dumps({k: report.get(k) for k in ('mode', 'overall_status', 'test_count', 'pass_count', 'fail_count', 'unknown_count', 'reason', 'result_json') if k in report}, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
