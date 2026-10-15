from __future__ import annotations

import base64
import contextlib
import dataclasses
import datetime as dt
import hashlib
import json
import os
import re
import sqlite3
import stat
import zlib
from pathlib import Path
from typing import Any, Iterable, Iterator, Sequence

DEFAULT_DB = Path('/root/werkraum/_gpt/gesamtatlas/omega/OMEGA.sqlite')
DEFAULT_CHUNK_BYTES = 256 * 1024
DEFAULT_OVERLAP_BYTES = 2048
DEFAULT_MAX_RESULTS = 100
TEXT_SUFFIXES = {
    '.md', '.txt', '.json', '.jsonl', '.yaml', '.yml', '.toml', '.ini', '.conf',
    '.service', '.timer', '.py', '.js', '.mjs', '.cjs', '.ts', '.tsx', '.jsx',
    '.html', '.htm', '.css', '.scss', '.sql', '.sh', '.bash', '.zsh', '.fish',
    '.log', '.xml', '.csv', '.tsv', '.ps1', '.cmd', '.bat', '.env', '.properties',
    '.rst', '.adoc', '.tex', '.graphql', '.gql', '.vue', '.svelte', '.go', '.rs',
    '.java', '.c', '.cc', '.cpp', '.h', '.hpp', '.php', '.rb', '.pl', '.lua',
}
ABS_PATH_RE = re.compile(r'(?<![\w.-])(/(?:root|home|mnt|var|etc|opt|srv|tmp)/[^\s\x00\"\'<>|]{2,2048})')
WINDOWS_PATH_RE = re.compile(r'(?<![A-Za-z0-9_])([A-Za-z]:\\[^\r\n\t\"<>|]{2,2048})')
AI_STREAM_NAMES = ('claude', 'claudeweb', 'chatgpt', 'codex', 'gemini', 'kimi', 'glm')


class OmegaError(RuntimeError):
    pass


def utcnow() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def stable_id(prefix: str, *parts: Any) -> str:
    payload = '\x1f'.join(str(p) for p in parts).encode('utf-8', 'surrogatepass')
    return f'{prefix}_{hashlib.sha256(payload).hexdigest()[:32]}'


def _connect(db_path: str | Path = DEFAULT_DB, *, readonly: bool = False) -> sqlite3.Connection:
    p = Path(db_path)
    if readonly:
        uri = f'file:{p.as_posix()}?mode=ro'
        con = sqlite3.connect(uri, uri=True, timeout=30)
    else:
        p.parent.mkdir(parents=True, exist_ok=True)
        con = sqlite3.connect(p, timeout=60)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    con.execute('PRAGMA busy_timeout=60000')
    if not readonly:
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA synchronous=NORMAL')
        con.execute('PRAGMA temp_store=MEMORY')
    return con


def init_db(db_path: str | Path = DEFAULT_DB) -> dict[str, Any]:
    with _connect(db_path) as con:
        con.executescript(
            """
            CREATE TABLE IF NOT EXISTS meta(
                key TEXT PRIMARY KEY,
                value_json TEXT NOT NULL,
                updated_utc TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS scans(
                scan_id TEXT PRIMARY KEY,
                started_utc TEXT NOT NULL,
                completed_utc TEXT,
                mode TEXT NOT NULL,
                roots_json TEXT NOT NULL,
                status TEXT NOT NULL,
                stats_json TEXT NOT NULL DEFAULT '{}',
                error TEXT
            );
            CREATE TABLE IF NOT EXISTS objects(
                object_id TEXT PRIMARY KEY,
                identity_kind TEXT NOT NULL,
                device INTEGER,
                inode INTEGER,
                first_seen_utc TEXT NOT NULL,
                last_seen_utc TEXT NOT NULL,
                current_version_id TEXT,
                current_primary_path TEXT,
                deleted INTEGER NOT NULL DEFAULT 0,
                markers_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE UNIQUE INDEX IF NOT EXISTS idx_objects_dev_inode
                ON objects(device,inode) WHERE device IS NOT NULL AND inode IS NOT NULL;
            CREATE TABLE IF NOT EXISTS paths(
                path TEXT PRIMARY KEY,
                object_id TEXT NOT NULL REFERENCES objects(object_id),
                root_path TEXT NOT NULL,
                root_name TEXT NOT NULL,
                kind TEXT NOT NULL,
                is_dir INTEGER NOT NULL,
                is_symlink INTEGER NOT NULL,
                symlink_target TEXT,
                first_seen_utc TEXT NOT NULL,
                last_seen_utc TEXT NOT NULL,
                last_scan_id TEXT NOT NULL,
                exists_flag INTEGER NOT NULL DEFAULT 1,
                size INTEGER,
                mtime_ns INTEGER,
                ctime_ns INTEGER,
                mode INTEGER,
                suffix TEXT,
                parent_path TEXT,
                markers_json TEXT NOT NULL DEFAULT '{}'
            );
            CREATE INDEX IF NOT EXISTS idx_paths_object ON paths(object_id);
            CREATE INDEX IF NOT EXISTS idx_paths_root ON paths(root_name);
            CREATE INDEX IF NOT EXISTS idx_paths_parent ON paths(parent_path);
            CREATE INDEX IF NOT EXISTS idx_paths_exists ON paths(exists_flag);
            CREATE TABLE IF NOT EXISTS versions(
                version_id TEXT PRIMARY KEY,
                object_id TEXT NOT NULL REFERENCES objects(object_id),
                epoch INTEGER NOT NULL,
                previous_version_id TEXT,
                observed_utc TEXT NOT NULL,
                source_path TEXT NOT NULL,
                size INTEGER NOT NULL,
                mtime_ns INTEGER,
                ctime_ns INTEGER,
                content_fingerprint TEXT NOT NULL,
                fingerprint_kind TEXT NOT NULL,
                file_sha256 TEXT,
                chunk_count INTEGER NOT NULL,
                complete INTEGER NOT NULL,
                encoding TEXT,
                decode_error_count INTEGER NOT NULL DEFAULT 0,
                change_kind TEXT NOT NULL,
                append_from_byte INTEGER,
                UNIQUE(object_id,epoch)
            );
            CREATE INDEX IF NOT EXISTS idx_versions_object ON versions(object_id,epoch DESC);
            CREATE INDEX IF NOT EXISTS idx_versions_fingerprint ON versions(content_fingerprint);
            CREATE TABLE IF NOT EXISTS chunk_blobs(
                chunk_pk INTEGER PRIMARY KEY,
                chunk_sha256 TEXT NOT NULL UNIQUE,
                raw_size INTEGER NOT NULL,
                compressed_raw BLOB NOT NULL,
                text_body TEXT NOT NULL,
                encoding TEXT NOT NULL,
                decode_error_count INTEGER NOT NULL DEFAULT 0,
                is_text INTEGER NOT NULL DEFAULT 1
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS chunk_fts USING fts5(
                text_body,
                content='chunk_blobs',
                content_rowid='chunk_pk',
                tokenize='unicode61 remove_diacritics 2'
            );
            CREATE TRIGGER IF NOT EXISTS chunk_ai AFTER INSERT ON chunk_blobs WHEN new.is_text=1 BEGIN
                INSERT INTO chunk_fts(rowid,text_body) VALUES (new.chunk_pk,new.text_body);
            END;
            CREATE TRIGGER IF NOT EXISTS chunk_ad AFTER DELETE ON chunk_blobs WHEN old.is_text=1 BEGIN
                INSERT INTO chunk_fts(chunk_fts,rowid,text_body) VALUES('delete',old.chunk_pk,old.text_body);
            END;
            CREATE TRIGGER IF NOT EXISTS chunk_au AFTER UPDATE ON chunk_blobs BEGIN
                INSERT INTO chunk_fts(chunk_fts,rowid,text_body)
                    SELECT 'delete',old.chunk_pk,old.text_body WHERE old.is_text=1;
                INSERT INTO chunk_fts(rowid,text_body)
                    SELECT new.chunk_pk,new.text_body WHERE new.is_text=1;
            END;
            CREATE TABLE IF NOT EXISTS version_chunks(
                version_id TEXT NOT NULL REFERENCES versions(version_id) ON DELETE CASCADE,
                seq INTEGER NOT NULL,
                chunk_pk INTEGER NOT NULL REFERENCES chunk_blobs(chunk_pk),
                start_byte INTEGER NOT NULL,
                end_byte INTEGER NOT NULL,
                PRIMARY KEY(version_id,seq)
            );
            CREATE INDEX IF NOT EXISTS idx_vchunks_chunk ON version_chunks(chunk_pk);
            CREATE TABLE IF NOT EXISTS mentions(
                mention_id TEXT PRIMARY KEY,
                source_version_id TEXT NOT NULL REFERENCES versions(version_id) ON DELETE CASCADE,
                source_object_id TEXT NOT NULL,
                mentioned_path TEXT NOT NULL,
                mention_count INTEGER NOT NULL,
                first_byte INTEGER,
                resolved_object_id TEXT,
                evidence_class TEXT NOT NULL DEFAULT 'EXACT_TEXT'
            );
            CREATE INDEX IF NOT EXISTS idx_mentions_path ON mentions(mentioned_path);
            CREATE TABLE IF NOT EXISTS edges(
                edge_id TEXT PRIMARY KEY,
                src_object_id TEXT NOT NULL,
                dst_object_id TEXT NOT NULL,
                edge_type TEXT NOT NULL,
                evidence_class TEXT NOT NULL,
                evidence_json TEXT NOT NULL,
                first_seen_utc TEXT NOT NULL,
                last_seen_utc TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                UNIQUE(src_object_id,dst_object_id,edge_type,evidence_class)
            );
            CREATE INDEX IF NOT EXISTS idx_edges_src ON edges(src_object_id,edge_type);
            CREATE INDEX IF NOT EXISTS idx_edges_dst ON edges(dst_object_id,edge_type);
            CREATE TABLE IF NOT EXISTS events(
                event_id TEXT PRIMARY KEY,
                object_id TEXT,
                path TEXT,
                event_type TEXT NOT NULL,
                occurred_utc TEXT NOT NULL,
                scan_id TEXT,
                details_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_events_object ON events(object_id,occurred_utc);
            """
        )
        chunk_columns = {str(row['name']) for row in con.execute('PRAGMA table_info(chunk_blobs)').fetchall()}
        if 'is_text' not in chunk_columns:
            con.execute('ALTER TABLE chunk_blobs ADD COLUMN is_text INTEGER NOT NULL DEFAULT 1')
        con.executescript(
            """
            DROP TRIGGER IF EXISTS chunk_ai;
            DROP TRIGGER IF EXISTS chunk_ad;
            DROP TRIGGER IF EXISTS chunk_au;
            CREATE TRIGGER chunk_ai AFTER INSERT ON chunk_blobs WHEN new.is_text=1 BEGIN
                INSERT INTO chunk_fts(rowid,text_body) VALUES (new.chunk_pk,new.text_body);
            END;
            CREATE TRIGGER chunk_ad AFTER DELETE ON chunk_blobs WHEN old.is_text=1 BEGIN
                INSERT INTO chunk_fts(chunk_fts,rowid,text_body) VALUES('delete',old.chunk_pk,old.text_body);
            END;
            CREATE TRIGGER chunk_au AFTER UPDATE ON chunk_blobs BEGIN
                INSERT INTO chunk_fts(chunk_fts,rowid,text_body)
                    SELECT 'delete',old.chunk_pk,old.text_body WHERE old.is_text=1;
                INSERT INTO chunk_fts(rowid,text_body)
                    SELECT new.chunk_pk,new.text_body WHERE new.is_text=1;
            END;
            """
        )
        now = utcnow()
        con.execute(
            "INSERT INTO meta(key,value_json,updated_utc) VALUES('schema_version','\"1.0\"',?) "
            "ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json,updated_utc=excluded.updated_utc",
            (now,),
        )
    return {'ok': True, 'db_path': str(Path(db_path)), 'schema_version': '1.0'}


def _decode(raw: bytes) -> tuple[str, str, int]:
    try:
        return raw.decode('utf-8'), 'utf-8', 0
    except UnicodeDecodeError:
        text = raw.decode('utf-8', errors='replace')
        return text, 'utf-8-replace', text.count('\ufffd')


def _object_id(st: os.stat_result, path: Path) -> tuple[str, str]:
    if getattr(st, 'st_ino', 0):
        return stable_id('obj', st.st_dev, st.st_ino), 'DEVICE_INODE'
    return stable_id('objpath', str(path)), 'PATH_FALLBACK'


def _classify_path(path: Path, st: os.stat_result) -> tuple[str, bool, bool]:
    mode = st.st_mode
    if stat.S_ISDIR(mode):
        return 'directory', True, False
    if stat.S_ISLNK(mode):
        return 'symlink', False, True
    if stat.S_ISREG(mode):
        return 'file', False, False
    return 'other', False, False


def _is_text_candidate(path: Path, *, include_suffixes: set[str] | None = None) -> bool:
    suffixes = include_suffixes or TEXT_SUFFIXES
    return path.suffix.lower() in suffixes or path.name.lower() in {'dockerfile', 'makefile', 'readme', 'license'}


def _iter_tree(root: Path) -> Iterator[Path]:
    yield root
    if not root.exists() or not root.is_dir():
        return
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        dirnames.sort()
        filenames.sort()
        for name in dirnames:
            yield base / name
        for name in filenames:
            yield base / name


def _insert_event(con: sqlite3.Connection, *, object_id: str | None, path: str | None, event_type: str, scan_id: str | None, details: dict[str, Any]) -> None:
    event_id = stable_id('evt', event_type, object_id, path, scan_id, utcnow(), json.dumps(details, sort_keys=True))
    con.execute(
        'INSERT INTO events(event_id,object_id,path,event_type,occurred_utc,scan_id,details_json) VALUES(?,?,?,?,?,?,?)',
        (event_id, object_id, path, event_type, utcnow(), scan_id, json.dumps(details, ensure_ascii=False, sort_keys=True)),
    )


def _upsert_edge(con: sqlite3.Connection, src: str, dst: str, edge_type: str, evidence_class: str, evidence: dict[str, Any]) -> None:
    now = utcnow()
    edge_id = stable_id('edge', src, dst, edge_type, evidence_class)
    con.execute(
        """INSERT INTO edges(edge_id,src_object_id,dst_object_id,edge_type,evidence_class,evidence_json,first_seen_utc,last_seen_utc,active)
           VALUES(?,?,?,?,?,?,?,?,1)
           ON CONFLICT(src_object_id,dst_object_id,edge_type,evidence_class)
           DO UPDATE SET evidence_json=excluded.evidence_json,last_seen_utc=excluded.last_seen_utc,active=1""",
        (edge_id, src, dst, edge_type, evidence_class, json.dumps(evidence, ensure_ascii=False, sort_keys=True), now, now),
    )


def _store_blob(con: sqlite3.Connection, raw: bytes, *, index_text: bool = True) -> tuple[int, str, str, int]:
    chunk_sha = sha256_bytes(raw)
    row = con.execute(
        'SELECT chunk_pk,encoding,decode_error_count,is_text FROM chunk_blobs WHERE chunk_sha256=?',
        (chunk_sha,),
    ).fetchone()
    if row:
        if index_text and not bool(row['is_text']):
            text, encoding, errors = _decode(raw)
            con.execute(
                'UPDATE chunk_blobs SET text_body=?,encoding=?,decode_error_count=?,is_text=1 WHERE chunk_pk=?',
                (text, encoding, errors, row['chunk_pk']),
            )
            return int(row['chunk_pk']), chunk_sha, encoding, errors
        return int(row['chunk_pk']), chunk_sha, str(row['encoding']), int(row['decode_error_count'])
    if index_text:
        text, encoding, errors = _decode(raw)
    else:
        text, encoding, errors = '', 'binary', 0
    cur = con.execute(
        'INSERT INTO chunk_blobs(chunk_sha256,raw_size,compressed_raw,text_body,encoding,decode_error_count,is_text) VALUES(?,?,?,?,?,?,?)',
        (chunk_sha, len(raw), sqlite3.Binary(zlib.compress(raw, level=6)), text, encoding, errors, int(index_text)),
    )
    return int(cur.lastrowid), chunk_sha, encoding, errors


def _chunk_file(path: Path, *, chunk_bytes: int, start_byte: int = 0) -> Iterator[tuple[int, int, bytes]]:
    with path.open('rb', buffering=0) as f:
        f.seek(start_byte)
        pos = start_byte
        while True:
            raw = f.read(chunk_bytes)
            if not raw:
                break
            yield pos, pos + len(raw), raw
            pos += len(raw)


def _version_rows(con: sqlite3.Connection, object_id: str) -> list[sqlite3.Row]:
    return con.execute('SELECT * FROM versions WHERE object_id=? ORDER BY epoch DESC', (object_id,)).fetchall()


def _previous_chunks(con: sqlite3.Connection, version_id: str) -> list[sqlite3.Row]:
    return con.execute(
        'SELECT vc.*,cb.chunk_sha256,cb.raw_size FROM version_chunks vc JOIN chunk_blobs cb ON cb.chunk_pk=vc.chunk_pk WHERE vc.version_id=? ORDER BY vc.seq',
        (version_id,),
    ).fetchall()


def _decompress_chunk(con: sqlite3.Connection, chunk_pk: int) -> bytes:
    row = con.execute('SELECT compressed_raw FROM chunk_blobs WHERE chunk_pk=?', (chunk_pk,)).fetchone()
    if not row:
        raise OmegaError(f'chunk missing: {chunk_pk}')
    return zlib.decompress(bytes(row['compressed_raw']))


def _detect_append(con: sqlite3.Connection, path: Path, previous: sqlite3.Row, *, chunk_bytes: int) -> tuple[bool, int, list[sqlite3.Row]]:
    old_size = int(previous['size'])
    new_size = path.stat().st_size
    if new_size <= old_size or old_size == 0:
        return False, 0, []
    chunks = _previous_chunks(con, str(previous['version_id']))
    if not chunks:
        return False, 0, []
    last = chunks[-1]
    last_raw = _decompress_chunk(con, int(last['chunk_pk']))
    with path.open('rb', buffering=0) as f:
        f.seek(int(last['start_byte']))
        current = f.read(len(last_raw))
    if current != last_raw:
        return False, 0, []
    rewrite_start = int(last['start_byte'])
    reusable = [r for r in chunks if int(r['end_byte']) <= rewrite_start]
    return True, rewrite_start, reusable


def _collect_mentions(text: str, base_offset: int) -> dict[str, tuple[int, int]]:
    out: dict[str, tuple[int, int]] = {}
    for regex in (ABS_PATH_RE, WINDOWS_PATH_RE):
        for match in regex.finditer(text):
            value = match.group(1).rstrip('.,;:)]}')
            count, first = out.get(value, (0, base_offset + match.start(1)))
            out[value] = (count + 1, first)
    return out


def _scan_file_version(
    con: sqlite3.Connection,
    *,
    path: Path,
    object_id: str,
    scan_id: str,
    chunk_bytes: int,
    force: bool = False,
    index_text: bool = True,
) -> tuple[str | None, str, int]:
    st = path.stat()
    initial_signature = (st.st_dev, st.st_ino, st.st_size, st.st_mtime_ns, st.st_ctime_ns)
    previous = con.execute('SELECT * FROM versions WHERE object_id=? ORDER BY epoch DESC LIMIT 1', (object_id,)).fetchone()
    if previous and not force and int(previous['size']) == st.st_size and int(previous['mtime_ns'] or -1) == st.st_mtime_ns and int(previous['ctime_ns'] or -1) == st.st_ctime_ns:
        return str(previous['version_id']), 'UNCHANGED', 0

    append = False
    rewrite_start = 0
    reusable: list[sqlite3.Row] = []
    if previous and not force:
        append, rewrite_start, reusable = _detect_append(con, path, previous, chunk_bytes=chunk_bytes)

    epoch = int(previous['epoch']) + 1 if previous else 1
    change_kind = 'APPEND' if append else ('INITIAL' if previous is None else 'REWRITE')
    chunk_links: list[tuple[int, int, int, int, str]] = []
    chunk_hashes: list[str] = []
    total_errors = 0
    encodings: set[str] = set()
    mentions: dict[str, tuple[int, int]] = {}

    seq = 0
    for old in reusable:
        chunk_links.append((seq, int(old['chunk_pk']), int(old['start_byte']), int(old['end_byte']), str(old['chunk_sha256'])))
        chunk_hashes.append(str(old['chunk_sha256']))
        seq += 1

    start = rewrite_start if append else 0
    file_hasher = hashlib.sha256()
    if start:
        with path.open('rb', buffering=0) as f:
            remaining = start
            while remaining:
                block = f.read(min(1024 * 1024, remaining))
                if not block:
                    break
                file_hasher.update(block)
                remaining -= len(block)

    observed_end = start
    for start_byte, end_byte, raw in _chunk_file(path, chunk_bytes=chunk_bytes, start_byte=start):
        file_hasher.update(raw)
        chunk_pk, chunk_sha, encoding, errors = _store_blob(con, raw, index_text=index_text)
        chunk_links.append((seq, chunk_pk, start_byte, end_byte, chunk_sha))
        if index_text:
            text, _, _ = _decode(raw)
            for mentioned, (count, first) in _collect_mentions(text, start_byte).items():
                old_count, old_first = mentions.get(mentioned, (0, first))
                mentions[mentioned] = (old_count + count, min(old_first, first))
        chunk_hashes.append(chunk_sha)
        encodings.add(encoding)
        total_errors += errors
        observed_end = end_byte
        seq += 1

    final_st = path.stat()
    final_signature = (final_st.st_dev, final_st.st_ino, final_st.st_size, final_st.st_mtime_ns, final_st.st_ctime_ns)
    if initial_signature != final_signature or observed_end != st.st_size:
        raise OmegaError(
            'SOURCE_CHANGED_DURING_SCAN: '
            + json.dumps(
                {
                    'path': str(path),
                    'initial': initial_signature,
                    'final': final_signature,
                    'observed_end': observed_end,
                },
                sort_keys=True,
            )
        )

    merkle = sha256_bytes(('\n'.join(chunk_hashes) + f'\nSIZE:{st.st_size}').encode())
    version_id = stable_id('ver', object_id, epoch, merkle)
    file_sha = file_hasher.hexdigest()
    encoding_summary = ','.join(sorted(encodings)) if encodings else ('utf-8' if index_text and st.st_size == 0 else 'binary')
    con.execute(
        """INSERT INTO versions(version_id,object_id,epoch,previous_version_id,observed_utc,source_path,size,mtime_ns,ctime_ns,
           content_fingerprint,fingerprint_kind,file_sha256,chunk_count,complete,encoding,decode_error_count,change_kind,append_from_byte)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            version_id, object_id, epoch, str(previous['version_id']) if previous else None, utcnow(), str(path), st.st_size,
            st.st_mtime_ns, st.st_ctime_ns, merkle, 'CHUNK_MERKLE_SHA256', file_sha, seq, 1, encoding_summary,
            total_errors, change_kind, rewrite_start if append else None,
        ),
    )
    con.executemany(
        'INSERT INTO version_chunks(version_id,seq,chunk_pk,start_byte,end_byte) VALUES(?,?,?,?,?)',
        [(version_id, seq_no, chunk_pk, start_byte, end_byte) for seq_no, chunk_pk, start_byte, end_byte, _ in chunk_links],
    )
    con.execute('UPDATE objects SET current_version_id=?,current_primary_path=?,last_seen_utc=?,deleted=0 WHERE object_id=?', (version_id, str(path), utcnow(), object_id))

    if index_text:
        for mentioned, (count, first) in mentions.items():
            mention_id = stable_id('mention', version_id, mentioned)
            con.execute(
                'INSERT INTO mentions(mention_id,source_version_id,source_object_id,mentioned_path,mention_count,first_byte,evidence_class) VALUES(?,?,?,?,?,?,?)',
                (mention_id, version_id, object_id, mentioned, count, first, 'EXACT_TEXT'),
            )

    _insert_event(
        con,
        object_id=object_id,
        path=str(path),
        event_type='VERSION_CREATED',
        scan_id=scan_id,
        details={
            'version_id': version_id,
            'previous_version_id': previous['version_id'] if previous else None,
            'change_kind': change_kind,
            'append_from_byte': rewrite_start if append else None,
            'index_text': index_text,
            'file_sha256': file_sha,
        },
    )
    return version_id, change_kind, seq


def _infer_stream(path: str) -> str | None:
    low = path.lower()
    for stream in AI_STREAM_NAMES:
        if f'/{stream}/' in low or f'_{stream}_' in low or f'-{stream}-' in low or low.endswith('/' + stream):
            return stream
    if 'claude' in low and 'web' in low:
        return 'claudeweb'
    return None


def _refresh_relationships(con: sqlite3.Connection) -> dict[str, int]:
    con.execute("UPDATE edges SET active=0 WHERE evidence_class IN ('STRUCTURE','CONTENT_FINGERPRINT','EXACT_TEXT','INFERRED_PATH')")
    path_rows = con.execute('SELECT path,object_id,parent_path,is_symlink,symlink_target,root_name FROM paths WHERE exists_flag=1').fetchall()
    path_to_object = {str(r['path']): str(r['object_id']) for r in path_rows}
    counts = {'parent_child': 0, 'symlink': 0, 'same_content': 0, 'path_mentions': 0, 'project_member': 0, 'ai_stream': 0}

    for row in path_rows:
        parent = row['parent_path']
        if parent and parent in path_to_object and path_to_object[parent] != row['object_id']:
            _upsert_edge(con, path_to_object[parent], str(row['object_id']), 'PARENT_CHILD', 'STRUCTURE', {'parent_path': parent, 'child_path': row['path']})
            counts['parent_child'] += 1
        target = row['symlink_target']
        if row['is_symlink'] and target:
            target_path = str((Path(str(row['path'])).parent / str(target)).resolve()) if not os.path.isabs(str(target)) else os.path.normpath(str(target))
            dst = path_to_object.get(target_path)
            if dst:
                _upsert_edge(con, str(row['object_id']), dst, 'SYMLINK_TARGET', 'STRUCTURE', {'source_path': row['path'], 'target_path': target_path})
                counts['symlink'] += 1

    fingerprint_groups = con.execute(
        """SELECT v.content_fingerprint,group_concat(v.object_id) AS object_ids,count(DISTINCT v.object_id) AS n
           FROM versions v JOIN objects o ON o.current_version_id=v.version_id
           WHERE v.complete=1 GROUP BY v.content_fingerprint HAVING n>1 LIMIT 250000"""
    ).fetchall()
    for group in fingerprint_groups:
        ids = sorted(set(str(group['object_ids']).split(',')))
        for i, src in enumerate(ids):
            for dst in ids[i + 1:]:
                _upsert_edge(con, src, dst, 'SAME_CONTENT', 'CONTENT_FINGERPRINT', {'content_fingerprint': group['content_fingerprint']})
                _upsert_edge(con, dst, src, 'SAME_CONTENT', 'CONTENT_FINGERPRINT', {'content_fingerprint': group['content_fingerprint']})
                counts['same_content'] += 2

    mention_rows = con.execute('SELECT mention_id,source_object_id,mentioned_path,mention_count,first_byte FROM mentions').fetchall()
    for row in mention_rows:
        dst = path_to_object.get(str(row['mentioned_path']))
        if not dst:
            continue
        con.execute('UPDATE mentions SET resolved_object_id=? WHERE mention_id=?', (dst, row['mention_id']))
        _upsert_edge(
            con, str(row['source_object_id']), dst, 'PATH_MENTIONS', 'EXACT_TEXT',
            {'mentioned_path': row['mentioned_path'], 'mention_count': row['mention_count'], 'first_byte': row['first_byte']},
        )
        counts['path_mentions'] += 1

    for row in path_rows:
        path = str(row['path'])
        obj = str(row['object_id'])
        parts = Path(path).parts
        project_root = None
        if path.startswith('/root/werkraum/') and len(parts) >= 4:
            project_root = str(Path(*parts[:4]))
        elif path.startswith('/root/') and len(parts) >= 3:
            project_root = str(Path(*parts[:3]))
        if project_root and project_root in path_to_object and path_to_object[project_root] != obj:
            _upsert_edge(con, obj, path_to_object[project_root], 'PROJECT_MEMBER', 'INFERRED_PATH', {'path': path, 'project_root': project_root})
            counts['project_member'] += 1
        stream = _infer_stream(path)
        if stream:
            stream_obj = stable_id('stream', stream)
            now = utcnow()
            con.execute(
                """INSERT INTO objects(object_id,identity_kind,first_seen_utc,last_seen_utc,current_primary_path,markers_json)
                   VALUES(?,?,?,?,?,?) ON CONFLICT(object_id) DO UPDATE SET last_seen_utc=excluded.last_seen_utc""",
                (stream_obj, 'AI_STREAM_VIRTUAL', now, now, f'ai-stream://{stream}', json.dumps({'stream': stream})),
            )
            _upsert_edge(con, obj, stream_obj, 'AI_STREAM_MEMBER', 'INFERRED_PATH', {'path': path, 'stream': stream})
            counts['ai_stream'] += 1
    return counts


def sync_roots(
    roots: Sequence[str | Path],
    *,
    db_path: str | Path = DEFAULT_DB,
    root_names: Sequence[str] | None = None,
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
    include_suffixes: Iterable[str] | None = None,
    force: bool = False,
) -> dict[str, Any]:
    init_db(db_path)
    roots_p = [Path(r).resolve() for r in roots]
    names = list(root_names or [r.name or 'root' for r in roots_p])
    if len(names) != len(roots_p):
        raise OmegaError('root_names length mismatch')
    suffixes = {s.lower() for s in include_suffixes} if include_suffixes else TEXT_SUFFIXES
    scan_id = stable_id('scan', utcnow(), *(str(r) for r in roots_p))
    stats = {
        'paths_seen': 0, 'files_seen': 0, 'directories_seen': 0, 'symlinks_seen': 0,
        'version_candidates': 0, 'text_candidates': 0, 'binary_candidates': 0,
        'versions_created': 0, 'versions_appended': 0, 'versions_rewritten': 0,
        'unchanged_files': 0, 'chunks_linked': 0, 'source_changed_during_scan': 0, 'errors': 0,
    }
    with _connect(db_path) as con:
        con.execute(
            'INSERT INTO scans(scan_id,started_utc,mode,roots_json,status,stats_json) VALUES(?,?,?,?,?,?)',
            (scan_id, utcnow(), 'FULL' if force else 'INCREMENTAL', json.dumps([str(r) for r in roots_p]), 'RUNNING', '{}'),
        )
        try:
            for root, root_name in zip(roots_p, names):
                if not root.exists() and not root.is_symlink():
                    stats['errors'] += 1
                    continue
                for path in _iter_tree(root):
                    stats['paths_seen'] += 1
                    try:
                        st = path.lstat()
                    except OSError as exc:
                        stats['errors'] += 1
                        _insert_event(con, object_id=None, path=str(path), event_type='STAT_ERROR', scan_id=scan_id, details={'error': repr(exc)})
                        continue
                    object_id, identity_kind = _object_id(st, path)
                    kind, is_dir, is_symlink = _classify_path(path, st)
                    now = utcnow()
                    con.execute(
                        """INSERT INTO objects(object_id,identity_kind,device,inode,first_seen_utc,last_seen_utc,current_primary_path,deleted)
                           VALUES(?,?,?,?,?,?,?,0)
                           ON CONFLICT(object_id) DO UPDATE SET last_seen_utc=excluded.last_seen_utc,current_primary_path=excluded.current_primary_path,deleted=0""",
                        (object_id, identity_kind, st.st_dev, st.st_ino, now, now, str(path)),
                    )
                    symlink_target = None
                    if is_symlink:
                        stats['symlinks_seen'] += 1
                        with contextlib.suppress(OSError):
                            symlink_target = os.readlink(path)
                    elif is_dir:
                        stats['directories_seen'] += 1
                    elif kind == 'file':
                        stats['files_seen'] += 1
                    con.execute(
                        """INSERT INTO paths(path,object_id,root_path,root_name,kind,is_dir,is_symlink,symlink_target,first_seen_utc,last_seen_utc,last_scan_id,exists_flag,size,mtime_ns,ctime_ns,mode,suffix,parent_path)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                           ON CONFLICT(path) DO UPDATE SET object_id=excluded.object_id,root_path=excluded.root_path,root_name=excluded.root_name,
                           kind=excluded.kind,is_dir=excluded.is_dir,is_symlink=excluded.is_symlink,symlink_target=excluded.symlink_target,
                           last_seen_utc=excluded.last_seen_utc,last_scan_id=excluded.last_scan_id,exists_flag=1,size=excluded.size,
                           mtime_ns=excluded.mtime_ns,ctime_ns=excluded.ctime_ns,mode=excluded.mode,suffix=excluded.suffix,parent_path=excluded.parent_path""",
                        (
                            str(path), object_id, str(root), root_name, kind, int(is_dir), int(is_symlink), symlink_target,
                            now, now, scan_id, 1, st.st_size, st.st_mtime_ns, st.st_ctime_ns, st.st_mode, path.suffix.lower(), str(path.parent) if path != root else None,
                        ),
                    )
                    if kind == 'file' and not is_symlink:
                        stats['version_candidates'] += 1
                        index_text = _is_text_candidate(path, include_suffixes=suffixes)
                        if index_text:
                            stats['text_candidates'] += 1
                        else:
                            stats['binary_candidates'] += 1
                        con.execute('SAVEPOINT omega_file_scan')
                        try:
                            _, change_kind, linked = _scan_file_version(
                                con,
                                path=path,
                                object_id=object_id,
                                scan_id=scan_id,
                                chunk_bytes=chunk_bytes,
                                force=force,
                                index_text=index_text,
                            )
                            con.execute('RELEASE SAVEPOINT omega_file_scan')
                            stats['chunks_linked'] += linked
                            if change_kind == 'UNCHANGED':
                                stats['unchanged_files'] += 1
                            else:
                                stats['versions_created'] += 1
                                if change_kind == 'APPEND':
                                    stats['versions_appended'] += 1
                                elif change_kind == 'REWRITE':
                                    stats['versions_rewritten'] += 1
                        except (OSError, sqlite3.Error, OmegaError) as exc:
                            con.execute('ROLLBACK TO SAVEPOINT omega_file_scan')
                            con.execute('RELEASE SAVEPOINT omega_file_scan')
                            stats['errors'] += 1
                            if 'SOURCE_CHANGED_DURING_SCAN' in str(exc):
                                stats['source_changed_during_scan'] += 1
                            _insert_event(con, object_id=object_id, path=str(path), event_type='INDEX_ERROR', scan_id=scan_id, details={'error': repr(exc)})
                con.execute(
                    "UPDATE paths SET exists_flag=0 WHERE root_path=? AND last_scan_id<>?",
                    (str(root), scan_id),
                )
            con.execute(
                "UPDATE objects SET deleted=1 WHERE object_id NOT IN (SELECT DISTINCT object_id FROM paths WHERE exists_flag=1) AND identity_kind<>'AI_STREAM_VIRTUAL'"
            )
            relation_counts = _refresh_relationships(con)
            stats['relations'] = relation_counts
            con.execute('UPDATE scans SET completed_utc=?,status=?,stats_json=? WHERE scan_id=?', (utcnow(), 'COMPLETE', json.dumps(stats, sort_keys=True), scan_id))
            con.commit()
        except Exception as exc:
            con.rollback()
            with _connect(db_path) as fail_con:
                fail_con.execute('UPDATE scans SET completed_utc=?,status=?,error=?,stats_json=? WHERE scan_id=?', (utcnow(), 'FAILED', repr(exc), json.dumps(stats), scan_id))
            raise
    return {'ok': True, 'scan_id': scan_id, 'db_path': str(Path(db_path)), 'stats': stats}


def sync_from_legacy_path_index(
    *,
    db_path: str | Path = DEFAULT_DB,
    legacy_path_db: str | Path = '/root/werkraum/_gpt/gesamtatlas/PFADINDEX.sqlite',
    chunk_bytes: int = DEFAULT_CHUNK_BYTES,
    limit: int | None = None,
) -> dict[str, Any]:
    legacy = _connect(legacy_path_db, readonly=True)
    try:
        rows = legacy.execute(
            """SELECT DISTINCT root_path,root_name FROM paths WHERE excluded_reason IS NULL OR excluded_reason='' ORDER BY root_name"""
        ).fetchall()
        roots = []
        names = []
        for row in rows:
            p = Path(str(row['root_path']))
            if p.exists() and str(p) not in {str(x) for x in roots}:
                roots.append(p)
                names.append(str(row['root_name']))
                if limit and len(roots) >= limit:
                    break
    finally:
        legacy.close()
    return sync_roots(roots, db_path=db_path, root_names=names, chunk_bytes=chunk_bytes)


def _fts_query(query: str) -> str:
    tokens = re.findall(r'[\wÀ-ÖØ-öø-ÿ]{2,}', query, flags=re.UNICODE)
    if not tokens:
        raise OmegaError('query contains no searchable tokens')
    return ' AND '.join(f'"{t.replace(chr(34), chr(34)*2)}"' for t in tokens[:20])


def search_full(query: str, *, db_path: str | Path = DEFAULT_DB, limit: int = 40, include_historic: bool = False) -> dict[str, Any]:
    limit = max(1, min(int(limit), DEFAULT_MAX_RESULTS))
    q = _fts_query(query)
    query_bytes = query.encode('utf-8')
    with _connect(db_path, readonly=True) as con:
        historic_clause = '' if include_historic else 'AND o.current_version_id=vc.version_id'
        rows = con.execute(
            f"""WITH hits AS (
                       SELECT rowid AS chunk_pk,bm25(chunk_fts) AS score,
                              snippet(chunk_fts,0,'⟦','⟧',' … ',18) AS snippet
                       FROM chunk_fts WHERE chunk_fts MATCH ? ORDER BY score LIMIT ?
                   )
                   SELECT hits.score,hits.snippet,cb.chunk_pk,cb.chunk_sha256,cb.compressed_raw,
                          vc.version_id,vc.seq,vc.start_byte,vc.end_byte,
                          v.object_id,v.epoch,v.source_path,v.size,v.change_kind,p.path
                   FROM hits
                   JOIN chunk_blobs cb ON cb.chunk_pk=hits.chunk_pk
                   JOIN version_chunks vc ON vc.chunk_pk=cb.chunk_pk
                   JOIN versions v ON v.version_id=vc.version_id
                   JOIN objects o ON o.object_id=v.object_id
                   LEFT JOIN paths p ON p.object_id=v.object_id AND p.exists_flag=1
                   WHERE 1=1 {historic_clause}
                   ORDER BY hits.score,vc.version_id,vc.seq,p.path LIMIT ?""",
            (q, limit * 4, limit),
        ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            raw = zlib.decompress(bytes(item.pop('compressed_raw')))
            local_offsets: list[int] = []
            if query_bytes:
                pos = 0
                while True:
                    found = raw.find(query_bytes, pos)
                    if found < 0:
                        break
                    local_offsets.append(found)
                    pos = found + 1
            item['match_byte_offsets'] = [int(item['start_byte']) + offset for offset in local_offsets]
            item['first_match_byte'] = item['match_byte_offsets'][0] if item['match_byte_offsets'] else None
            item['exact_literal_match_count'] = len(local_offsets)
            results.append(item)
    return {'ok': True, 'query': query, 'fts_query': q, 'include_historic': include_historic, 'result_count': len(results), 'results': results}


def _resolve_object(con: sqlite3.Connection, path_or_object: str) -> sqlite3.Row:
    row = con.execute('SELECT * FROM objects WHERE object_id=?', (path_or_object,)).fetchone()
    if row:
        return row
    row = con.execute('SELECT o.* FROM paths p JOIN objects o ON o.object_id=p.object_id WHERE p.path=? ORDER BY p.exists_flag DESC LIMIT 1', (str(Path(path_or_object)),)).fetchone()
    if row:
        return row
    raise OmegaError(f'object/path not found: {path_or_object}')


def object_view(path_or_object: str, *, db_path: str | Path = DEFAULT_DB, edge_limit: int = 100, version_limit: int = 100) -> dict[str, Any]:
    with _connect(db_path, readonly=True) as con:
        obj = _resolve_object(con, path_or_object)
        object_id = str(obj['object_id'])
        paths = [dict(r) for r in con.execute('SELECT * FROM paths WHERE object_id=? ORDER BY exists_flag DESC,path', (object_id,)).fetchall()]
        versions = [dict(r) for r in con.execute('SELECT * FROM versions WHERE object_id=? ORDER BY epoch DESC LIMIT ?', (object_id, max(1, min(version_limit, 500)))).fetchall()]
        edges_out = [dict(r) for r in con.execute('SELECT * FROM edges WHERE src_object_id=? AND active=1 ORDER BY edge_type LIMIT ?', (object_id, edge_limit)).fetchall()]
        edges_in = [dict(r) for r in con.execute('SELECT * FROM edges WHERE dst_object_id=? AND active=1 ORDER BY edge_type LIMIT ?', (object_id, edge_limit)).fetchall()]
        events = [dict(r) for r in con.execute('SELECT * FROM events WHERE object_id=? ORDER BY occurred_utc DESC LIMIT 100', (object_id,)).fetchall()]
    return {'ok': True, 'object': dict(obj), 'paths': paths, 'versions': versions, 'edges_out': edges_out, 'edges_in': edges_in, 'events': events}


def read_original(
    path_or_object: str,
    *,
    db_path: str | Path = DEFAULT_DB,
    version_id: str | None = None,
    start_byte: int = 0,
    max_bytes: int = 65536,
) -> dict[str, Any]:
    start_byte = max(0, int(start_byte))
    max_bytes = max(1, min(int(max_bytes), 1024 * 1024))
    with _connect(db_path, readonly=True) as con:
        obj = _resolve_object(con, path_or_object)
        object_id = str(obj['object_id'])
        if version_id:
            version = con.execute('SELECT * FROM versions WHERE version_id=? AND object_id=?', (version_id, object_id)).fetchone()
        else:
            version = con.execute('SELECT * FROM versions WHERE version_id=?', (obj['current_version_id'],)).fetchone()
        if not version:
            raise OmegaError('no indexed version')
        total = int(version['size'])
        end_byte = min(total, start_byte + max_bytes)
        pieces: list[bytes] = []
        rows = con.execute(
            """SELECT vc.*,cb.compressed_raw FROM version_chunks vc JOIN chunk_blobs cb ON cb.chunk_pk=vc.chunk_pk
               WHERE vc.version_id=? AND vc.end_byte>? AND vc.start_byte<? ORDER BY vc.seq""",
            (version['version_id'], start_byte, end_byte),
        ).fetchall()
        for row in rows:
            raw = zlib.decompress(bytes(row['compressed_raw']))
            left = max(0, start_byte - int(row['start_byte']))
            right = min(len(raw), end_byte - int(row['start_byte']))
            if right > left:
                pieces.append(raw[left:right])
        raw_range = b''.join(pieces)
        text, encoding, errors = _decode(raw_range)
    return {
        'ok': True,
        'object_id': object_id,
        'version_id': str(version['version_id']),
        'epoch': int(version['epoch']),
        'source_path': str(version['source_path']),
        'total_bytes': total,
        'start_byte': start_byte,
        'end_byte': start_byte + len(raw_range),
        'returned_bytes': len(raw_range),
        'has_more': start_byte + len(raw_range) < total,
        'next_start_byte': start_byte + len(raw_range) if start_byte + len(raw_range) < total else None,
        'range_sha256': sha256_bytes(raw_range),
        'content_fingerprint': str(version['content_fingerprint']),
        'file_sha256': version['file_sha256'],
        'stored_encoding': version['encoding'],
        'encoding': encoding,
        'decode_error_count': errors,
        'raw_base64': base64.b64encode(raw_range).decode('ascii'),
        'text': text,
    }


def timeline(path_or_object: str, *, db_path: str | Path = DEFAULT_DB, limit: int = 200) -> dict[str, Any]:
    with _connect(db_path, readonly=True) as con:
        obj = _resolve_object(con, path_or_object)
        object_id = str(obj['object_id'])
        versions = [dict(r) for r in con.execute('SELECT * FROM versions WHERE object_id=? ORDER BY epoch DESC LIMIT ?', (object_id, max(1, min(limit, 1000)))).fetchall()]
        path_history = [dict(r) for r in con.execute('SELECT path,first_seen_utc,last_seen_utc,exists_flag,last_scan_id FROM paths WHERE object_id=? ORDER BY first_seen_utc', (object_id,)).fetchall()]
        events = [dict(r) for r in con.execute('SELECT * FROM events WHERE object_id=? ORDER BY occurred_utc DESC LIMIT ?', (object_id, max(1, min(limit, 1000)))).fetchall()]
    return {'ok': True, 'object_id': object_id, 'versions': versions, 'path_history': path_history, 'events': events}


def health(*, db_path: str | Path = DEFAULT_DB) -> dict[str, Any]:
    p = Path(db_path)
    if not p.exists():
        return {'ok': False, 'status': 'MISSING', 'db_path': str(p)}
    with _connect(p, readonly=True) as con:
        integrity = con.execute('PRAGMA integrity_check').fetchone()[0]
        counts = {}
        for table in ('objects', 'paths', 'versions', 'chunk_blobs', 'version_chunks', 'mentions', 'edges', 'events', 'scans'):
            counts[table] = con.execute(f'SELECT count(*) FROM {table}').fetchone()[0]
        latest = con.execute('SELECT * FROM scans ORDER BY started_utc DESC LIMIT 1').fetchone()
        incomplete = con.execute('SELECT count(*) FROM versions WHERE complete=0').fetchone()[0]
        current_missing = con.execute('SELECT count(*) FROM objects WHERE current_version_id IS NOT NULL AND current_version_id NOT IN (SELECT version_id FROM versions)').fetchone()[0]
    return {
        'ok': integrity == 'ok' and incomplete == 0 and current_missing == 0,
        'status': 'READY' if integrity == 'ok' else 'CORRUPT',
        'db_path': str(p),
        'db_bytes': p.stat().st_size,
        'integrity': integrity,
        'counts': counts,
        'incomplete_versions': incomplete,
        'current_version_reference_errors': current_missing,
        'latest_scan': dict(latest) if latest else None,
    }


__all__ = [
    'DEFAULT_DB', 'OmegaError', 'init_db', 'sync_roots', 'sync_from_legacy_path_index',
    'search_full', 'object_view', 'read_original', 'timeline', 'health',
]
