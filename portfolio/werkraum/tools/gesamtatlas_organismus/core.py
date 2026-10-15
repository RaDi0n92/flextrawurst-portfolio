from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

from common import (
    ATLAS_ROOT,
    PREVIEW_CHARS,
    SOURCE_ROOTS,
    load_json,
    redact,
    sha256_file,
    sqlite,
    stable_id,
    utcnow,
)

PATH_DB = ATLAS_ROOT / 'PFADINDEX.sqlite'
TEXT_DB = ATLAS_ROOT / 'BEGRIFFSINDEX.sqlite'
REL_DB = ATLAS_ROOT / 'BEZIEHUNGSREGISTER.sqlite'
PROJECTS = ATLAS_ROOT / 'PROJEKTREGISTER.json'
STREAMS = ATLAS_ROOT / 'AI_STROEME.json'
STATUS = ATLAS_ROOT / 'ATLAS_STATUS.json'

SCHEMA = '''
create table if not exists meta(key text primary key, value_json text not null);
create table if not exists roots(
  root_id text primary key, title text not null, path text not null, kind text not null,
  description text not null, exists_flag integer not null, source_bytes integer,
  source_file_count integer, access_mode text not null
);
create table if not exists paths(
  object_id text primary key, path text unique not null, root_name text, root_path text,
  kind text, is_dir integer, is_symlink integer, size integer, mtime_ns integer,
  suffix text, depth integer, basename text, parent text, markers_json text,
  excluded_reason text, access_mode text not null default 'reference_only'
);
create index if not exists idx_paths_basename on paths(basename);
create index if not exists idx_paths_root on paths(root_name);
create index if not exists idx_paths_parent on paths(parent);
create table if not exists projects(
  project_id text primary key, name text, path text, project_class text, status text,
  summary text, metadata_json text not null
);
create table if not exists streams(
  stream_id text primary key, title text, home_path text, home_exists integer,
  session_source text, metadata_json text not null
);
create table if not exists relation_nodes(
  node_id text primary key, node_type text, identity text, label text, path text,
  truth_class text, metadata_json text not null
);
create table if not exists relation_edges(
  edge_id text primary key, source_node_id text, target_node_id text, relation text,
  truth_class text, evidence_json text not null
);
create virtual table if not exists previews using fts5(
  path unindexed, title, headings, preview,
  tokenize='unicode61 remove_diacritics 2'
);
create table if not exists build_coverage(
  component text primary key, source_path text, status text, item_count integer,
  bytes integer, note text, checked_utc text
);
'''


def _dir_size_and_count(root: Path) -> tuple[int, int]:
    total = count = 0
    if not root.exists():
        return 0, 0
    for base, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if name not in {'.git', 'node_modules', '__pycache__', '.cache', 'organismus', 'dateikoerper'}]
        for name in files:
            path = Path(base) / name
            try:
                if path.is_file() and not path.is_symlink():
                    total += path.stat().st_size
                    count += 1
            except OSError:
                continue
    return total, count


def _value(obj: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in obj and obj[name] not in (None, ''):
            return obj[name]
    return default


def build_core(target: Path) -> dict[str, Any]:
    if target.exists():
        target.unlink()
    with sqlite(target) as out:
        out.executescript(SCHEMA)
        status = load_json(STATUS, {}) or {}
        out.execute('insert or replace into meta values (?,?)', ('generated_utc', json.dumps(utcnow())))
        out.execute('insert or replace into meta values (?,?)', ('atlas_status', json.dumps(status, ensure_ascii=False)))
        out.execute('insert or replace into meta values (?,?)', ('design', json.dumps({
            'copy_policy': 'reference_first',
            'full_originals': 'remain_at_source_paths',
            'portable_capsule': 'facet_complete_not_detail_complete',
            'size_budget_bytes': 1_500_000_000,
        }, ensure_ascii=False)))

        root_rows = []
        for source in SOURCE_ROOTS:
            total, count = _dir_size_and_count(source.path)
            row = (
                source.root_id, source.title, str(source.path), source.kind, source.description,
                int(source.path.exists()), total, count, 'live_reference',
            )
            out.execute('insert into roots values (?,?,?,?,?,?,?,?,?)', row)
            root_rows.append({'root_id': source.root_id, 'bytes': total, 'files': count, 'exists': source.path.exists()})

        path_count = 0
        if PATH_DB.exists():
            source = sqlite3.connect(f'file:{PATH_DB}?mode=ro', uri=True)
            source.row_factory = sqlite3.Row
            columns = {row[1] for row in source.execute('pragma table_info(paths)')}
            selected = ['path','root_name','root_path','kind','is_dir','is_symlink','size','mtime_ns','suffix','depth','basename','parent','markers_json']
            if 'excluded_reason' in columns:
                selected.append('excluded_reason')
            query = 'select ' + ','.join(selected) + ' from paths'
            batch = []
            for row in source.execute(query):
                path = row['path']
                object_id = stable_id('path', path)
                excluded = row['excluded_reason'] if 'excluded_reason' in selected else None
                batch.append((
                    object_id, path, row['root_name'], row['root_path'], row['kind'], row['is_dir'],
                    row['is_symlink'], row['size'], row['mtime_ns'], row['suffix'], row['depth'],
                    row['basename'], row['parent'], row['markers_json'], excluded, 'live_reference',
                ))
                if len(batch) >= 5000:
                    out.executemany('insert into paths values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
                    path_count += len(batch)
                    batch.clear()
            if batch:
                out.executemany('insert into paths values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
                path_count += len(batch)
            source.close()
        out.execute('insert into build_coverage values (?,?,?,?,?,?,?)', ('paths', str(PATH_DB), 'complete_copy_of_index_rows', path_count, target.stat().st_size if target.exists() else 0, 'No source files copied.', utcnow()))

        project_rows = load_json(PROJECTS, []) or []
        if isinstance(project_rows, dict):
            project_rows = project_rows.get('projects') or project_rows.get('items') or []
        project_count = 0
        for item in project_rows:
            if not isinstance(item, dict):
                continue
            project_id = str(_value(item, 'project_id', 'id', default=stable_id('project', str(item))))
            name = str(_value(item, 'name', 'title', default=project_id))
            path = _value(item, 'path', 'project_path')
            project_class = _value(item, 'project_class', 'class', 'kind')
            state = _value(item, 'status', 'state')
            summary = _value(item, 'summary', 'description', 'purpose')
            out.execute('insert or replace into projects values (?,?,?,?,?,?,?)', (
                project_id, name, path, project_class, state, summary,
                json.dumps(item, ensure_ascii=False, sort_keys=True),
            ))
            project_count += 1
        out.execute('insert into build_coverage values (?,?,?,?,?,?,?)', ('projects', str(PROJECTS), 'complete_registry_copy', project_count, PROJECTS.stat().st_size if PROJECTS.exists() else 0, '', utcnow()))

        stream_rows = load_json(STREAMS, []) or []
        if isinstance(stream_rows, dict):
            stream_rows = stream_rows.get('streams') or stream_rows.get('items') or []
        stream_count = 0
        for item in stream_rows:
            if not isinstance(item, dict):
                continue
            stream_id = str(_value(item, 'stream_id', 'id', 'name', default=stable_id('stream', str(item))))
            title = str(_value(item, 'title', 'label', 'name', default=stream_id))
            home = _value(item, 'home_path', 'home', 'zuhause_path')
            exists = int(bool(_value(item, 'home_exists', default=Path(home).exists() if home else False)))
            session_source = _value(item, 'session_source', 'sessions_path', 'source')
            out.execute('insert or replace into streams values (?,?,?,?,?,?)', (
                stream_id, title, home, exists, session_source,
                json.dumps(item, ensure_ascii=False, sort_keys=True),
            ))
            stream_count += 1
        out.execute('insert into build_coverage values (?,?,?,?,?,?,?)', ('streams', str(STREAMS), 'complete_registry_copy', stream_count, STREAMS.stat().st_size if STREAMS.exists() else 0, '', utcnow()))

        node_count = edge_count = 0
        if REL_DB.exists():
            source = sqlite3.connect(f'file:{REL_DB}?mode=ro', uri=True)
            source.row_factory = sqlite3.Row
            nodes = [tuple(row) for row in source.execute('select node_id,node_type,identity,label,path,truth_class,metadata_json from nodes')]
            edges = [tuple(row) for row in source.execute('select edge_id,source_node_id,target_node_id,relation,truth_class,evidence_json from edges')]
            out.executemany('insert into relation_nodes values (?,?,?,?,?,?,?)', nodes)
            out.executemany('insert into relation_edges values (?,?,?,?,?,?)', edges)
            node_count, edge_count = len(nodes), len(edges)
            source.close()
        out.execute('insert into build_coverage values (?,?,?,?,?,?,?)', ('relations', str(REL_DB), 'complete_registry_copy', node_count + edge_count, REL_DB.stat().st_size if REL_DB.exists() else 0, f'{node_count} nodes, {edge_count} edges', utcnow()))

        preview_count = redaction_count = 0
        if TEXT_DB.exists():
            source = sqlite3.connect(f'file:{TEXT_DB}?mode=ro', uri=True)
            source.row_factory = sqlite3.Row
            batch = []
            for row in source.execute('select path,title,headings,substr(body,1,?) as preview from documents', (PREVIEW_CHARS * 2,)):
                preview, redactions = redact(str(row['preview'] or ''))
                title, redactions_title = redact(str(row['title'] or ''))
                headings, redactions_headings = redact(str(row['headings'] or ''))
                redaction_count += redactions + redactions_title + redactions_headings
                batch.append((row['path'], title, headings, preview[:PREVIEW_CHARS]))
                if len(batch) >= 2000:
                    out.executemany('insert into previews(path,title,headings,preview) values (?,?,?,?)', batch)
                    preview_count += len(batch)
                    batch.clear()
            if batch:
                out.executemany('insert into previews(path,title,headings,preview) values (?,?,?,?)', batch)
                preview_count += len(batch)
            source.close()
        out.execute('insert into build_coverage values (?,?,?,?,?,?,?)', ('previews', str(TEXT_DB), 'truncated_redacted_previews_only', preview_count, target.stat().st_size if target.exists() else 0, f'{redaction_count} marked removals', utcnow()))
        out.execute('insert or replace into meta values (?,?)', ('counts', json.dumps({
            'roots': len(root_rows), 'paths': path_count, 'projects': project_count,
            'streams': stream_count, 'relation_nodes': node_count, 'relation_edges': edge_count,
            'previews': preview_count,
        }, ensure_ascii=False)))
        out.execute('pragma optimize')

    return {
        'ok': True,
        'path': str(target),
        'bytes': target.stat().st_size,
        'sha256': sha256_file(target),
        'counts': {
            'paths': path_count, 'projects': project_count, 'streams': stream_count,
            'relation_nodes': node_count, 'relation_edges': edge_count, 'previews': preview_count,
        },
        'root_rows': root_rows,
        'redactions': redaction_count,
    }


def search_core(db_path: Path, query: str, limit: int = 50) -> list[dict[str, Any]]:
    query = query.strip()
    if not query:
        return []
    rows: list[dict[str, Any]] = []
    with sqlite(db_path, readonly=True) as connection:
        fts_query = ' '.join(part.replace('"', '""') for part in query.split())
        try:
            for row in connection.execute(
                "select path,title,headings,preview,bm25(previews) as rank from previews where previews match ? order by rank limit ?",
                (fts_query, limit),
            ):
                rows.append({'kind': 'content_preview', **dict(row)})
        except sqlite3.OperationalError:
            pass
        remaining = max(0, limit - len(rows))
        if remaining:
            like = f'%{query.lower()}%'
            for row in connection.execute(
                'select object_id,path,root_name,kind,size,mtime_ns,suffix,excluded_reason from paths where lower(path) like ? or lower(basename) like ? limit ?',
                (like, like, remaining),
            ):
                rows.append({'kind': 'path', **dict(row)})
    return rows
