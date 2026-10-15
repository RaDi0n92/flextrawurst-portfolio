#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB = Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/WIRKUNG/WIRKUNGSSTUFEN.sqlite')
STAGES = (
    'EXISTIERTE',
    'ERREICHBAR',
    'ANGEZEIGT',
    'GELESEN',
    'VERWENDET',
    'WIRKTE_AUF_HANDLUNG',
)
STATUSES = {'BEWIESEN', 'BEHAUPTET', 'UNBEKANNT', 'WIDERLEGT'}
EVIDENCE_CLASSES = {'DIRECT_SOURCE', 'SYSTEM_OBSERVED', 'USER_CONFIRMED', 'ATTRIBUTED_CLAIM', 'MODEL_DERIVED'}
SUFFICIENT = {
    'EXISTIERTE': {'DIRECT_SOURCE', 'SYSTEM_OBSERVED'},
    'ERREICHBAR': {'SYSTEM_OBSERVED', 'USER_CONFIRMED'},
    'ANGEZEIGT': {'SYSTEM_OBSERVED', 'USER_CONFIRMED'},
    'GELESEN': {'SYSTEM_OBSERVED', 'USER_CONFIRMED'},
    'VERWENDET': {'DIRECT_SOURCE', 'SYSTEM_OBSERVED', 'USER_CONFIRMED'},
    'WIRKTE_AUF_HANDLUNG': {'DIRECT_SOURCE', 'SYSTEM_OBSERVED', 'USER_CONFIRMED'},
}
SCHEMA = '''
pragma foreign_keys=on;
create table if not exists information_objects(
  object_id text primary key,
  object_type text not null,
  label text not null,
  source_path text,
  source_sha256 text,
  created_utc text not null,
  metadata_json text not null
);
create table if not exists attestations(
  attestation_id text primary key,
  object_id text not null references information_objects(object_id),
  stage text not null,
  status text not null,
  evidence_class text not null,
  evidence_ref text not null,
  evidence_sha256 text,
  actor text not null,
  observed_utc text not null,
  statement text not null,
  action_ref text,
  causal_relation text,
  metadata_json text not null,
  unique(object_id, stage, evidence_ref, statement)
);
create index if not exists idx_att_object_stage on attestations(object_id,stage);
create table if not exists stage_assessments(
  object_id text not null references information_objects(object_id),
  stage text not null,
  effective_status text not null,
  strongest_evidence_class text,
  attestation_count integer not null,
  sufficient_evidence_count integer not null,
  updated_utc text not null,
  explanation text not null,
  primary key(object_id,stage)
);
create table if not exists transitions(
  transition_id text primary key,
  object_id text not null references information_objects(object_id),
  from_stage text not null,
  to_stage text not null,
  status text not null,
  reason text not null,
  evaluated_utc text not null,
  unique(object_id,from_stage,to_stage)
);
create table if not exists audit_events(
  event_id text primary key,
  event_type text not null,
  timestamp_utc text not null,
  payload_json text not null
);
'''


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(prefix: str, *parts: str, length: int = 24) -> str:
    return prefix + ':' + hashlib.sha256('\0'.join(parts).encode('utf-8', errors='replace')).hexdigest()[:length]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def connection(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute('pragma journal_mode=WAL')
    conn.execute('pragma synchronous=FULL')
    conn.executescript(SCHEMA)
    return conn


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, default=str))


def audit(conn: sqlite3.Connection, event_type: str, payload: dict[str, Any]) -> None:
    event_id = stable_id('evt', event_type, utcnow(), json.dumps(payload, sort_keys=True, ensure_ascii=False))
    conn.execute('insert into audit_events values (?,?,?,?)', (event_id, event_type, utcnow(), json.dumps(payload, ensure_ascii=False, sort_keys=True)))


def create_object(args: argparse.Namespace) -> dict[str, Any]:
    source_path = Path(args.source_path).resolve() if args.source_path else None
    source_sha = None
    if source_path:
        if not source_path.exists() or not source_path.is_file():
            raise FileNotFoundError(source_path)
        source_sha = sha256_file(source_path)
    object_id = args.object_id or stable_id('info', args.object_type, args.label, str(source_path or ''), source_sha or '')
    metadata = json.loads(args.metadata_json) if args.metadata_json else {}
    with connection(args.db) as conn:
        conn.execute('insert into information_objects values (?,?,?,?,?,?,?)', (
            object_id, args.object_type, args.label, str(source_path) if source_path else None, source_sha, utcnow(), json.dumps(metadata, ensure_ascii=False, sort_keys=True)
        ))
        audit(conn, 'object_created', {'object_id': object_id, 'source_path': str(source_path) if source_path else None})
    return {'ok': True, 'object_id': object_id, 'source_sha256': source_sha}


def validate_attestation(args: argparse.Namespace) -> tuple[str | None, str | None]:
    if args.stage not in STAGES:
        raise ValueError(f'Unbekannte Stufe: {args.stage}')
    if args.status not in STATUSES:
        raise ValueError(f'Unbekannter Status: {args.status}')
    if args.evidence_class not in EVIDENCE_CLASSES:
        raise ValueError(f'Unbekannte Beweisklasse: {args.evidence_class}')
    if not args.evidence_ref.strip():
        raise ValueError('evidence_ref darf nicht leer sein')
    evidence_sha = None
    if args.evidence_ref.startswith('/'):
        path = Path(args.evidence_ref)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(path)
        evidence_sha = sha256_file(path)
    if args.stage == 'WIRKTE_AUF_HANDLUNG':
        if not args.action_ref:
            raise ValueError('WIRKTE_AUF_HANDLUNG verlangt action_ref')
        if not args.causal_relation:
            raise ValueError('WIRKTE_AUF_HANDLUNG verlangt causal_relation')
    return evidence_sha, args.action_ref


def recompute(conn: sqlite3.Connection, object_id: str) -> list[dict[str, Any]]:
    result = []
    for stage in STAGES:
        rows = list(conn.execute('select * from attestations where object_id=? and stage=? order by observed_utc,attestation_id', (object_id, stage)))
        sufficient = [r for r in rows if r['evidence_class'] in SUFFICIENT[stage] and r['status'] in {'BEWIESEN', 'WIDERLEGT'}]
        proven = [r for r in sufficient if r['status'] == 'BEWIESEN']
        disproven = [r for r in sufficient if r['status'] == 'WIDERLEGT']
        claims = [r for r in rows if r['status'] == 'BEHAUPTET']
        if proven and disproven:
            effective = 'WIDERSPRUECHLICH'
            explanation = 'Sowohl beweisende als auch widerlegende hinreichende Belege liegen vor.'
        elif proven:
            effective = 'BEWIESEN'
            explanation = 'Mindestens ein für diese Stufe hinreichender Beleg liegt vor.'
        elif disproven:
            effective = 'WIDERLEGT'
            explanation = 'Mindestens ein hinreichender widerlegender Beleg liegt vor.'
        elif claims:
            effective = 'BEHAUPTET'
            explanation = 'Nur Behauptungen oder für diese Stufe nicht hinreichende Belege liegen vor.'
        else:
            effective = 'UNBEKANNT'
            explanation = 'Kein eigener Beleg für diese Stufe liegt vor.'
        strongest = sufficient[0]['evidence_class'] if sufficient else (rows[0]['evidence_class'] if rows else None)
        conn.execute('insert or replace into stage_assessments values (?,?,?,?,?,?,?,?)', (
            object_id, stage, effective, strongest, len(rows), len(sufficient), utcnow(), explanation
        ))
        result.append({'stage': stage, 'effective_status': effective, 'attestations': len(rows), 'sufficient': len(sufficient), 'explanation': explanation})
    conn.execute('delete from transitions where object_id=?', (object_id,))
    for index in range(len(STAGES) - 1):
        from_stage, to_stage = STAGES[index], STAGES[index + 1]
        a = result[index]['effective_status']
        b = result[index + 1]['effective_status']
        if b == 'BEWIESEN':
            status = 'DIRECTLY_EVIDENCED'
            reason = f'{to_stage} besitzt einen eigenen hinreichenden Beleg; keine Vererbung aus {from_stage}.'
        elif a == 'BEWIESEN':
            status = 'NOT_INFERRED'
            reason = f'{from_stage} ist bewiesen, aber {to_stage} bleibt ohne eigenen Beleg {b}.'
        else:
            status = 'UNRESOLVED'
            reason = f'Weder der Übergang noch {to_stage} sind eigenständig bewiesen.'
        transition_id = stable_id('transition', object_id, from_stage, to_stage)
        conn.execute('insert into transitions values (?,?,?,?,?,?,?)', (transition_id, object_id, from_stage, to_stage, status, reason, utcnow()))
    return result


def attest(args: argparse.Namespace) -> dict[str, Any]:
    evidence_sha, _ = validate_attestation(args)
    metadata = json.loads(args.metadata_json) if args.metadata_json else {}
    with connection(args.db) as conn:
        if conn.execute('select 1 from information_objects where object_id=?', (args.object_id,)).fetchone() is None:
            raise FileNotFoundError(f'Informationsobjekt fehlt: {args.object_id}')
        attestation_id = stable_id('att', args.object_id, args.stage, args.status, args.evidence_class, args.evidence_ref, args.statement)
        conn.execute('insert into attestations values (?,?,?,?,?,?,?,?,?,?,?,?,?)', (
            attestation_id, args.object_id, args.stage, args.status, args.evidence_class, args.evidence_ref, evidence_sha,
            args.actor, args.observed_utc or utcnow(), args.statement, args.action_ref, args.causal_relation,
            json.dumps(metadata, ensure_ascii=False, sort_keys=True)
        ))
        stages = recompute(conn, args.object_id)
        audit(conn, 'attestation_added', {'attestation_id': attestation_id, 'object_id': args.object_id, 'stage': args.stage})
    return {'ok': True, 'attestation_id': attestation_id, 'object_id': args.object_id, 'stages': stages}


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    with connection(args.db) as conn:
        obj = conn.execute('select * from information_objects where object_id=?', (args.object_id,)).fetchone()
        if obj is None:
            raise FileNotFoundError(args.object_id)
        stages = [dict(r) for r in conn.execute('select * from stage_assessments where object_id=? order by case stage ' + ' '.join(f"when '{stage}' then {i}" for i, stage in enumerate(STAGES)) + ' end', (args.object_id,))]
        if not stages:
            recompute(conn, args.object_id)
            stages = [dict(r) for r in conn.execute('select * from stage_assessments where object_id=? order by case stage ' + ' '.join(f"when '{stage}' then {i}" for i, stage in enumerate(STAGES)) + ' end', (args.object_id,))]
        transitions = [dict(r) for r in conn.execute('select * from transitions where object_id=? order by rowid', (args.object_id,))]
        attestations = [dict(r) for r in conn.execute('select * from attestations where object_id=? order by observed_utc,attestation_id', (args.object_id,))]
    return {'ok': True, 'object': dict(obj), 'stages': stages, 'transitions': transitions, 'attestations': attestations, 'truth_boundary': 'Keine Stufe wird aus einer früheren Stufe geerbt.'}


def list_objects(args: argparse.Namespace) -> dict[str, Any]:
    with connection(args.db) as conn:
        objects = [dict(r) for r in conn.execute('select * from information_objects order by created_utc,object_id')]
    return {'ok': True, 'count': len(objects), 'objects': objects}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='gesamtatlas-wirkungsstufen')
    parser.add_argument('--db', type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest='command', required=True)
    q = sub.add_parser('create-object'); q.add_argument('--object-id'); q.add_argument('--object-type', required=True); q.add_argument('--label', required=True); q.add_argument('--source-path'); q.add_argument('--metadata-json'); q.set_defaults(fn=create_object)
    q = sub.add_parser('attest'); q.add_argument('--object-id', required=True); q.add_argument('--stage', required=True, choices=STAGES); q.add_argument('--status', required=True, choices=sorted(STATUSES)); q.add_argument('--evidence-class', required=True, choices=sorted(EVIDENCE_CLASSES)); q.add_argument('--evidence-ref', required=True); q.add_argument('--actor', required=True); q.add_argument('--observed-utc'); q.add_argument('--statement', required=True); q.add_argument('--action-ref'); q.add_argument('--causal-relation'); q.add_argument('--metadata-json'); q.set_defaults(fn=attest)
    q = sub.add_parser('inspect'); q.add_argument('--object-id', required=True); q.set_defaults(fn=inspect)
    q = sub.add_parser('list'); q.set_defaults(fn=list_objects)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = args.fn(args)
        emit(result)
        return 0
    except Exception as exc:
        emit({'ok': False, 'error': f'{type(exc).__name__}: {exc}'})
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
