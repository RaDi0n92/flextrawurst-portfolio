from __future__ import annotations

import gzip
import json
import re
import shutil
import sqlite3
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from common import (
    ATLAS_ROOT,
    DETAIL_ROOT,
    load_json,
    read_jsonl,
    redact,
    sha256_file,
    stable_id,
    utcnow,
    write_jsonl,
)

BROWSER_ROOT = Path('/root/werkraum/_gpt/ui_visible_conversations')

BLITZ_RULES = [
    ('ursprung', re.compile(r'(?i)\b(erste idee|erstmals|ursprung|kam mir|ich stelle mir|ich möchte|wunsch|leitidee)\b')),
    ('entscheidung', re.compile(r'(?i)\b(entschieden|entscheidung|wir nehmen|ab jetzt|gilt|festgelegt|genau so)\b')),
    ('korrektur', re.compile(r'(?i)\b(korrektur|nein|nicht so|missverstanden|falsche richtung|zurück|eigentlich)\b')),
    ('irrweg', re.compile(r'(?i)\b(fehler|irrweg|kaputt|scheitert|timeout|falsch|wertlos|problem)\b')),
    ('offene_frage', re.compile(r'(?i)(\?|\bwie weiter\b|\bwas fehlt\b|\bunklar\b|\bhinterfragen\b)')),
]
HARDENING = re.compile(r'(?i)\b(muss|darf nicht|pflicht|regel|verbot|zwingend|ausschließlich|immer|niemals|constraint)\b')
WISH = re.compile(r'(?i)\b(ich möchte|ich will|ich stelle mir|wäre geil|wunsch|soll|könnte|idee)\b')


def _timestamp(row: dict[str, Any]) -> str | None:
    return row.get('timestamp_utc') or row.get('recorded_utc') or row.get('created_utc') or row.get('timestamp')


def _conversation_dirs() -> Iterable[Path]:
    if not BROWSER_ROOT.exists():
        return []
    return sorted((path for path in BROWSER_ROOT.iterdir() if path.is_dir() and not path.name.startswith('_')), key=lambda p: p.name)


def _messages(folder: Path) -> list[dict[str, Any]]:
    path = folder / 'messages.jsonl'
    rows = []
    if path.exists():
        for row in read_jsonl(path):
            content, redactions = redact(str(row.get('content') or row.get('text') or ''))
            rows.append({
                'message_id': row.get('message_id') or row.get('event_id') or stable_id('browser-message', json.dumps(row, sort_keys=True, default=str)),
                'turn_id': row.get('turn_id'),
                'role': row.get('role') or 'unknown',
                'content': content,
                'timestamp': _timestamp(row),
                'ordinal': row.get('ordinal'),
                'classification': row.get('classification'),
                'mcp_session_id': row.get('mcp_session_id'),
                'mcp_binding_status': row.get('mcp_binding_status'),
                'redactions': redactions,
                'source_path': str(path),
            })
    rows.sort(key=lambda row: (row.get('ordinal') is None, row.get('ordinal') or 0, row.get('timestamp') or ''))
    return rows


def _gaps(folder: Path) -> list[dict[str, Any]]:
    path = folder / 'capture_gaps.jsonl'
    return list(read_jsonl(path)) if path.exists() else []


def _visible_events(folder: Path) -> list[dict[str, Any]]:
    path = folder / 'visible_stream.jsonl'
    rows = []
    if path.exists():
        for row in read_jsonl(path):
            clean = dict(row)
            for key in ('content', 'text', 'visible_text', 'snapshot_text'):
                if isinstance(clean.get(key), str):
                    clean[key], _ = redact(clean[key])
            rows.append(clean)
    return rows


def _timeline(folder: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    machine = folder / 'B_TIMELINE.json'
    if machine.exists():
        data = load_json(machine, {}) or {}
        data['source_class'] = 'existing_recorder_projection'
        data['source_path'] = str(machine)
        return data
    turns = []
    for turn_id, turn in (manifest.get('turns') or {}).items() if isinstance(manifest.get('turns'), dict) else []:
        turns.append({
            'turn_id': turn_id,
            'started_utc': turn.get('started_utc'),
            'completed_utc': turn.get('completed_utc'),
            'mcp_session_id': turn.get('mcp_session_id'),
            'mcp_binding_status': turn.get('mcp_binding_status') or 'not_bound',
            'classification': turn.get('classification'),
            'completeness_verdict': turn.get('completeness_verdict'),
            'source_class': 'manifest_derived',
        })
    return {'schema_version': 'atlas-browser-b-1.0', 'events': [], 'turns': turns, 'source_class': 'manifest_derived'}


def _blitz(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for index, message in enumerate(messages):
        text = message.get('content') or ''
        for marker_type, rule in BLITZ_RULES:
            match = rule.search(text)
            if not match:
                continue
            results.append({
                'marker_id': stable_id('blitz', f"{message['message_id']}:{marker_type}"),
                'marker_type': marker_type,
                'message_id': message['message_id'],
                'turn_id': message.get('turn_id'),
                'role': message.get('role'),
                'timestamp': message.get('timestamp'),
                'matched_text': match.group(0)[:160],
                'excerpt': text[max(0, match.start() - 220): match.end() + 420],
                'truth_class': 'HEURISTIC_DERIVATION',
                'review_status': 'unreviewed',
                'message_index': index,
            })
    return results


def _raw_vs_hardening(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    wishes = []
    pairs = []
    for index, message in enumerate(messages):
        text = message.get('content') or ''
        if message.get('role') == 'user' and WISH.search(text):
            wishes.append((index, message))
        if not HARDENING.search(text):
            continue
        candidates = [(wish_index, wish) for wish_index, wish in wishes if 0 < index - wish_index <= 16]
        if not candidates:
            continue
        wish_index, wish = candidates[-1]
        pairs.append({
            'pair_id': stable_id('raw-hardening', f"{wish['message_id']}:{message['message_id']}"),
            'raw_message_id': wish['message_id'],
            'raw_role': wish.get('role'),
            'raw_excerpt': (wish.get('content') or '')[:1200],
            'later_message_id': message['message_id'],
            'later_role': message.get('role'),
            'later_excerpt': text[:1200],
            'distance_messages': index - wish_index,
            'truth_class': 'HEURISTIC_CANDIDATE_NOT_CAUSAL_PROOF',
            'review_question': 'Wurde ein offener Wunsch hier sinnvoll präzisiert oder unnötig in einen Regelkoffer verhärtet?',
        })
    return pairs


def _conversation_text(messages: list[dict[str, Any]]) -> str:
    chunks = []
    for message in messages:
        role = {'user': 'Daniel', 'assistant': 'AI', 'tool': 'Werkzeug'}.get(message.get('role'), str(message.get('role') or 'Unbekannt'))
        chunks.append(f'{role}:\n{message.get("content") or ""}')
    return '\n\n'.join(chunks).rstrip() + '\n'


def build_browser(output: Path, core_db: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    conversations_dir = output / 'conversations'
    conversations_dir.mkdir(parents=True, exist_ok=True)
    origin_db = output / 'URSPRUNGSSUCHE.sqlite'
    if origin_db.exists():
        origin_db.unlink()
    connection = sqlite3.connect(origin_db)
    connection.execute('pragma journal_mode=WAL')
    connection.execute('create table conversations(conversation_id text primary key, folder text, title text, provider text, message_count integer, turn_count integer, gap_count integer, completeness text, source_path text, manifest_json text)')
    connection.execute("create virtual table message_search using fts5(message_id unindexed, conversation_id unindexed, turn_id unindexed, role unindexed, timestamp unindexed, content, tokenize='unicode61 remove_diacritics 2')")
    connection.execute('create table blitz(marker_id text primary key, conversation_id text, marker_type text, message_id text, turn_id text, role text, timestamp text, excerpt text, truth_class text, review_status text)')
    connection.execute('create table hardening(pair_id text primary key, conversation_id text, raw_message_id text, later_message_id text, raw_excerpt text, later_excerpt text, distance_messages integer, truth_class text, review_question text)')

    overview = []
    totals = defaultdict(int)
    for folder in _conversation_dirs():
        manifest = load_json(folder / 'MANIFEST.json', {}) or {}
        messages = _messages(folder)
        gaps = _gaps(folder)
        visible = _visible_events(folder)
        timeline = _timeline(folder, manifest)
        blitz = _blitz(messages)
        hardening = _raw_vs_hardening(messages)
        conversation_id = str(manifest.get('conversation_id') or manifest.get('session_id') or folder.name)
        title = str(manifest.get('current_title') or manifest.get('title') or folder.name)
        provider = str(manifest.get('provider_id') or 'chatgpt')
        completeness = 'complete' if manifest.get('full_browser_export_confirmed') or (manifest.get('gap_count', len(gaps)) == 0 and messages) else 'partial_or_unconfirmed'
        turn_count = int(manifest.get('turn_count') or len({m.get('turn_id') for m in messages if m.get('turn_id')}))
        target = conversations_dir / stable_id('conversation', conversation_id).split(':', 1)[1]
        target.mkdir(parents=True, exist_ok=True)
        with gzip.open(target / 'GESPRAECH_1ZU1.md.gz', 'wt', encoding='utf-8') as stream:
            stream.write(_conversation_text(messages))
        write_jsonl(target / 'A_ZEITREISE.jsonl.gz', [
            {
                'sequence': index,
                'event_type': 'message',
                **message,
                'visible_events_same_turn': sum(1 for event in visible if event.get('turn_id') and event.get('turn_id') == message.get('turn_id')),
            }
            for index, message in enumerate(messages)
        ], gzip_output=True)
        (target / 'B_UI_MCP_VERWEBUNG.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        write_jsonl(target / 'C_BLITZMOMENTE.jsonl.gz', blitz, gzip_output=True)
        write_jsonl(target / 'D_ROHWUNSCH_GEGEN_VERHAERTUNG.jsonl.gz', hardening, gzip_output=True)
        package_manifest = {
            'schema_version': 'atlas-browser-a-f-1.0',
            'conversation_id': conversation_id,
            'folder': folder.name,
            'source_path': str(folder),
            'title': title,
            'provider': provider,
            'message_count': len(messages),
            'turn_count': turn_count,
            'gap_count': len(gaps),
            'completeness': completeness,
            'organs': {
                'A': 'A_ZEITREISE.jsonl.gz',
                'B': 'B_UI_MCP_VERWEBUNG.json',
                'C': 'C_BLITZMOMENTE.jsonl.gz',
                'D': 'D_ROHWUNSCH_GEGEN_VERHAERTUNG.jsonl.gz',
                'E': 'package_conversation() creates a portable conversation body on demand',
                'F': 'URSPRUNGSSUCHE.sqlite and atlasctl origin',
            },
            'originals': {
                'messages': str(folder / 'messages.jsonl'),
                'visible_stream': str(folder / 'visible_stream.jsonl'),
                'manifest': str(folder / 'MANIFEST.json'),
            },
            'truth_boundary': 'A–D are reproducible views. C and D are heuristic derivations, not original claims.',
        }
        (target / 'MANIFEST.json').write_text(json.dumps(package_manifest, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        connection.execute('insert into conversations values (?,?,?,?,?,?,?,?,?,?)', (
            conversation_id, folder.name, title, provider, len(messages), turn_count, len(gaps), completeness, str(folder), json.dumps(manifest, ensure_ascii=False, sort_keys=True),
        ))
        connection.executemany('insert into message_search values (?,?,?,?,?,?)', [
            (message['message_id'], conversation_id, message.get('turn_id'), message.get('role'), message.get('timestamp'), message.get('content') or '')
            for message in messages
        ])
        connection.executemany('insert into blitz values (?,?,?,?,?,?,?,?,?,?)', [
            (item['marker_id'], conversation_id, item['marker_type'], item['message_id'], item.get('turn_id'), item.get('role'), item.get('timestamp'), item.get('excerpt'), item['truth_class'], item['review_status'])
            for item in blitz
        ])
        connection.executemany('insert into hardening values (?,?,?,?,?,?,?,?,?)', [
            (item['pair_id'], conversation_id, item['raw_message_id'], item['later_message_id'], item['raw_excerpt'], item['later_excerpt'], item['distance_messages'], item['truth_class'], item['review_question'])
            for item in hardening
        ])
        overview.append({
            'conversation_id': conversation_id,
            'folder': folder.name,
            'title': title,
            'provider': provider,
            'message_count': len(messages),
            'turn_count': turn_count,
            'gap_count': len(gaps),
            'completeness': completeness,
            'atlas_path': str(target),
            'source_path': str(folder),
            'blitz_count': len(blitz),
            'hardening_candidates': len(hardening),
        })
        totals['conversations'] += 1
        totals['messages'] += len(messages)
        totals['turns'] += turn_count
        totals['gaps'] += len(gaps)
        totals['blitz'] += len(blitz)
        totals['hardening_candidates'] += len(hardening)
    connection.commit()
    connection.execute('pragma optimize')
    connection.close()
    write_jsonl(output / 'GESPRÄCHSREGISTER.jsonl.gz', overview, gzip_output=True)
    status = {
        'ok': True,
        'generated_utc': utcnow(),
        'source_root': str(BROWSER_ROOT),
        'origin_database': str(origin_db),
        'origin_database_bytes': origin_db.stat().st_size,
        'totals': dict(totals),
        'a_to_f': {
            'A': 'implemented_time_travel_event_stream',
            'B': 'implemented_existing_or_manifest_derived_ui_mcp_timeline',
            'C': 'implemented_heuristic_blitz_markers',
            'D': 'implemented_heuristic_raw_wish_vs_hardening_pairs',
            'E': 'implemented_on_demand_package_export',
            'F': 'implemented_origin_fts_search',
        },
    }
    (output / 'STATUS.json').write_text(json.dumps(status, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return status


def origin_search(browser_dir: Path, query: str, limit: int = 50) -> list[dict[str, Any]]:
    db = browser_dir / 'URSPRUNGSSUCHE.sqlite'
    if not db.exists() or not query.strip():
        return []
    connection = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in connection.execute(
            'select message_id,conversation_id,turn_id,role,timestamp,content,bm25(message_search) as rank from message_search where message_search match ? order by rank limit ?',
            (' '.join(query.split()), limit),
        )]
    except sqlite3.OperationalError:
        rows = []
    connection.close()
    return rows


def package_conversation(browser_dir: Path, conversation_id: str, destination: Path | None = None) -> Path:
    register = browser_dir / 'GESPRÄCHSREGISTER.jsonl.gz'
    row = next((item for item in read_jsonl(register) if item.get('conversation_id') == conversation_id), None)
    if not row:
        raise FileNotFoundError(f'conversation not found: {conversation_id}')
    source = Path(row['source_path'])
    generated = Path(row['atlas_path'])
    destination = destination or (DETAIL_ROOT / f'GESPRÄCH_{stable_id("conversation", conversation_id).split(":",1)[1]}.zip')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_suffix('.tmp')
    with zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED, compresslevel=7, allowZip64=True) as archive:
        for path in sorted(generated.rglob('*')):
            if path.is_file():
                archive.write(path, f'ATLAS_ANSICHTEN/{path.relative_to(generated)}')
        for name in ('MANIFEST.json', 'messages.jsonl', 'visible_stream.jsonl', 'capture_gaps.jsonl', 'B_TIMELINE.json', 'B_ZEITSPUR.md'):
            path = source / name
            if path.exists() and path.is_file():
                archive.write(path, f'ORIGINALQUELLEN/{name}')
        readme = f'''# Gesprächs-Explorationskörper\n\nGespräch: {conversation_id}\nQuelle: {source}\n\n`ORIGINALQUELLEN/` enthält vorhandene Primärkörper. `ATLAS_ANSICHTEN/` enthält reproduzierbare A–F-Ansichten. Heuristische Blitz- und Verhärtungsmarker sind keine Originalaussagen.\n'''
        archive.writestr('00_START_HIER.md', readme)
    with zipfile.ZipFile(temp) as archive:
        bad = archive.testzip()
        if bad:
            raise RuntimeError(f'bad zip member: {bad}')
    temp.replace(destination)
    return destination
