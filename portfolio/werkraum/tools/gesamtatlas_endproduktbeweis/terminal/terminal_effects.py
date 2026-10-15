#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB = Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/TERMINALWIRKUNG/WIRKUNGSKETTEN.sqlite')
DEFAULT_HISTORY = Path('/root/werkraum/_gpt/session_history.jsonl')
NODE_TYPES = {'IMPULS','INTERPRETATION','ENTSCHEIDUNG','TOOL','DATEI_ODER_DIENST','TEST','KORREKTUR','FOLGE','LUECKE'}
SOURCE_TYPES = {'history_event','file','source_range','gap'}
LINK_CLASSES = {
    'EXPLICIT_PARENT_EVENT',
    'COMMON_ARTIFACT_SUPPORTED',
    'CURATED_RELATION_CANDIDATE',
    'SAME_TARGET_SUCCESSOR',
    'SAME_SESSION_TEMPORAL_CANDIDATE',
    'UNLINKED_GAP',
}
PROOF_STRENGTH = {
    'EXPLICIT_PARENT_EVENT': 5,
    'COMMON_ARTIFACT_SUPPORTED': 4,
    'CURATED_RELATION_CANDIDATE': 3,
    'SAME_TARGET_SUCCESSOR': 2,
    'SAME_SESSION_TEMPORAL_CANDIDATE': 1,
    'UNLINKED_GAP': 0,
}
SCHEMA = '''
pragma foreign_keys=on;
create table if not exists imported_events(
 event_id text primary key, timestamp_utc text, session_id text, actor text, action text,
 status text, completeness text, target text, parent_event_id text, event_hash text,
 details_json text not null, raw_json text not null, event_class text not null,
 normalized_target text, imported_utc text not null
);
create index if not exists idx_events_session_time on imported_events(session_id,timestamp_utc);
create index if not exists idx_events_target on imported_events(session_id,normalized_target,status);
create table if not exists correction_candidates(
 candidate_id text primary key, session_id text not null, failed_event_id text not null,
 successor_event_id text not null, normalized_target text not null, relation_class text not null,
 seconds_apart real, status text not null, explanation text not null,
 unique(failed_event_id,successor_event_id)
);
create table if not exists chains(
 chain_id text primary key, title text not null, requirement_id text not null,
 source_session_id text, created_utc text not null, status text not null,
 causal_proof_level text not null, truth_boundary text not null, metadata_json text not null
);
create table if not exists chain_nodes(
 node_id text primary key, chain_id text not null references chains(chain_id), position integer not null,
 node_type text not null, label text not null, source_type text not null, source_ref text,
 source_sha256 text, source_excerpt text, event_id text references imported_events(event_id),
 truth_class text not null, status text not null, gap_reason text, metadata_json text not null,
 unique(chain_id,position)
);
create table if not exists chain_links(
 link_id text primary key, chain_id text not null references chains(chain_id),
 from_node_id text not null references chain_nodes(node_id), to_node_id text not null references chain_nodes(node_id),
 relation text not null, relation_class text not null, proof_strength integer not null,
 evidence_refs_json text not null, explanation text not null, causal_claim integer not null,
 unique(chain_id,from_node_id,to_node_id,relation)
);
create table if not exists chain_assessments(
 chain_id text primary key references chains(chain_id), node_count integer not null,
 gap_count integer not null, explicit_link_count integer not null, supported_link_count integer not null,
 candidate_link_count integer not null, weakest_required_role text,
 completeness_status text not null, updated_utc text not null
);
'''


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_id(prefix: str, *parts: str, length: int = 24) -> str:
    return prefix + ':' + hashlib.sha256('\0'.join(parts).encode('utf-8', errors='replace')).hexdigest()[:length]


def sha256_file(path: Path) -> str:
    d=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): d.update(chunk)
    return d.hexdigest()


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(path,timeout=30);c.row_factory=sqlite3.Row
    c.execute('pragma journal_mode=WAL');c.execute('pragma synchronous=FULL');c.executescript(SCHEMA)
    return c


def classify_event(row: dict[str,Any]) -> str:
    action=str(row.get('action') or '')
    target=str(row.get('target') or '')
    status=str(row.get('status') or '')
    low=(action+' '+target).lower()
    if action in {'ui_visible.message_recorded','ui_visible_record_message'}:
        return 'VISIBLE_MESSAGE'
    if status in {'failed','blocked'}:
        return 'FAILED_ACTION'
    if any(x in low for x in ('playwright','pytest','unittest','test_','tests.run','validation','integrity_check')):
        return 'TEST_ACTION'
    if action in {'write_file','append_file','vps.write_file','vps.edit_file','vps.delete','vps.move','tracked_write_file','tracked_append_file'}:
        return 'FILE_MUTATION'
    if action.startswith('services.'):
        return 'SERVICE_ACTION'
    if action.startswith('vps.') or action in {'read_file','reread_own_file'}:
        return 'TOOL_ACTION'
    if action in {'session.begin','session.resume','session.end'}:
        return 'SESSION_EVENT'
    return 'OTHER'


def normalize_target(target: str | None) -> str | None:
    if not target: return None
    value=' '.join(str(target).split())
    value=re.sub(r'\bPORT=\d+\b','PORT=<N>',value)
    value=re.sub(r'/tmp/[A-Za-z0-9._/-]+','/tmp/<TEMP>',value)
    return hashlib.sha256(value.encode('utf-8',errors='replace')).hexdigest()


def parse_time(value: str | None) -> datetime | None:
    if not value:return None
    try:return datetime.fromisoformat(value.replace('Z','+00:00'))
    except Exception:return None


def import_history(db: Path, history: Path) -> dict[str,Any]:
    if not history.exists():raise FileNotFoundError(history)
    inserted=updated=skipped=0
    with connect(db) as c:
        for line in history.open('r',encoding='utf-8',errors='replace'):
            try:r=json.loads(line)
            except Exception:
                skipped+=1;continue
            event_id=r.get('event_id')
            if not event_id:
                skipped+=1;continue
            values=(event_id,r.get('timestamp_utc'),r.get('session_id'),r.get('actor'),r.get('action'),r.get('status'),r.get('completeness'),r.get('target'),r.get('parent_event_id'),r.get('event_hash'),json.dumps(r.get('details') or {},ensure_ascii=False,sort_keys=True),json.dumps(r,ensure_ascii=False,sort_keys=True),classify_event(r),normalize_target(r.get('target')),utcnow())
            exists=c.execute('select 1 from imported_events where event_id=?',(event_id,)).fetchone()
            c.execute('insert or replace into imported_events values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)',values)
            updated+=int(bool(exists));inserted+=int(not exists)
        c.execute('delete from correction_candidates')
        groups=defaultdict(list)
        for r in c.execute("select * from imported_events where normalized_target is not null order by session_id,normalized_target,timestamp_utc,event_id"):
            groups[(r['session_id'],r['normalized_target'])].append(r)
        candidates=0
        for (session_id,target_hash),rows in groups.items():
            failures=[(i,r) for i,r in enumerate(rows) if r['status'] in {'failed','blocked'}]
            for index,failed in failures:
                successor=next((r for r in rows[index+1:] if r['status']=='success'),None)
                if successor is None:continue
                a,b=parse_time(failed['timestamp_utc']),parse_time(successor['timestamp_utc'])
                seconds=(b-a).total_seconds() if a and b else None
                cid=stable_id('candidate',failed['event_id'],successor['event_id'])
                c.execute('insert or replace into correction_candidates values (?,?,?,?,?,?,?,?,?)',(
                    cid,session_id,failed['event_id'],successor['event_id'],target_hash,'SAME_TARGET_SUCCESSOR',seconds,'CANDIDATE_NOT_CAUSAL_PROOF','Gleiche normalisierte Zielsignatur in derselben Session: Fehler/Blockade gefolgt von Erfolg. Dies beweist keine Ursache oder inhaltliche Korrektur.'))
                candidates+=1
        c.commit()
        totals=c.execute('select count(*),sum(parent_event_id is not null) from imported_events').fetchone()
    return {'ok':True,'history_path':str(history),'history_sha256':sha256_file(history),'inserted':inserted,'updated':updated,'skipped_lines':skipped,'event_count':totals[0],'parent_event_count':totals[1] or 0,'correction_candidates':candidates,'truth_boundary':'Kandidaten aus Zeit und Zielsignatur sind keine Kausalbeweise.'}


def resolve_source(c:sqlite3.Connection,node:dict[str,Any]) -> tuple[str|None,str|None,str|None]:
    source_type=node['source_type'];ref=node.get('source_ref')
    if source_type=='gap':
        return None,None,None
    if source_type=='history_event':
        r=c.execute('select * from imported_events where event_id=?',(ref,)).fetchone()
        if r is None:raise FileNotFoundError(f'History-Ereignis fehlt: {ref}')
        excerpt=json.dumps({'timestamp_utc':r['timestamp_utc'],'session_id':r['session_id'],'action':r['action'],'status':r['status'],'target':r['target'],'event_hash':r['event_hash']},ensure_ascii=False,sort_keys=True)
        return r['event_hash'],excerpt,r['event_id']
    path=Path(str(ref)).resolve()
    if not path.exists() or not path.is_file():raise FileNotFoundError(path)
    file_hash=sha256_file(path)
    if source_type=='file':
        excerpt=path.read_text('utf-8',errors='replace')[:2400] if path.stat().st_size<=5_000_000 else f'[Datei {path.stat().st_size} Bytes]'
        return file_hash,excerpt,None
    if source_type=='source_range':
        start=int(node.get('start_line') or 0);end=int(node.get('end_line') or 0)
        lines=path.read_text('utf-8',errors='replace').splitlines()
        if start<1 or end<start or end>len(lines):raise ValueError(f'Ungültiger Zeilenbereich {start}-{end} für {path}')
        return file_hash,'\n'.join(lines[start-1:end]),None
    raise ValueError(source_type)


def assess_chain(c:sqlite3.Connection,chain_id:str) -> dict[str,Any]:
    nodes=list(c.execute('select * from chain_nodes where chain_id=? order by position',(chain_id,)))
    links=list(c.execute('select * from chain_links where chain_id=? order by rowid',(chain_id,)))
    gaps=sum(r['node_type']=='LUECKE' or r['status']=='UNBEKANNT' for r in nodes)
    explicit=sum(r['relation_class']=='EXPLICIT_PARENT_EVENT' for r in links)
    supported=sum(r['relation_class']=='COMMON_ARTIFACT_SUPPORTED' for r in links)
    candidates=sum(r['relation_class'] in {'CURATED_RELATION_CANDIDATE','SAME_TARGET_SUCCESSOR','SAME_SESSION_TEMPORAL_CANDIDATE'} for r in links)
    required=['IMPULS','INTERPRETATION','ENTSCHEIDUNG','TOOL','DATEI_ODER_DIENST','TEST','KORREKTUR','FOLGE']
    present={r['node_type'] for r in nodes if r['node_type']!='LUECKE'}
    missing=next((role for role in required if role not in present),None)
    if gaps or missing:
        completeness='PARTIAL_WITH_VISIBLE_GAPS'
    elif explicit+supported==len(links) and links:
        completeness='SUPPORTED_COMPLETE_NOT_NECESSARILY_CAUSAL'
    else:
        completeness='CANDIDATE_CHAIN_NOT_CAUSAL_PROOF'
    c.execute('insert or replace into chain_assessments values (?,?,?,?,?,?,?,?,?)',(
        chain_id,len(nodes),gaps,explicit,supported,candidates,missing,completeness,utcnow()))
    proof_level='NO_CAUSAL_PROOF'
    if explicit and not gaps:proof_level='EXPLICIT_LINKS_PRESENT'
    elif supported:proof_level='ARTIFACT_SUPPORTED_PARTIAL'
    c.execute('update chains set status=?,causal_proof_level=? where chain_id=?',(completeness,proof_level,chain_id))
    return {'chain_id':chain_id,'node_count':len(nodes),'gap_count':gaps,'explicit_link_count':explicit,'supported_link_count':supported,'candidate_link_count':candidates,'weakest_required_role':missing,'completeness_status':completeness,'causal_proof_level':proof_level}


def create_chain(db:Path,spec_path:Path) -> dict[str,Any]:
    spec=json.loads(spec_path.read_text('utf-8'))
    chain_id=spec.get('chain_id') or stable_id('chain',spec['title'],spec.get('requirement_id',''),utcnow())
    nodes=spec.get('nodes') or [];links=spec.get('links') or []
    if not nodes:raise ValueError('Kette ohne Knoten')
    with connect(db) as c:
        if c.execute('select 1 from chains where chain_id=?',(chain_id,)).fetchone():raise FileExistsError(chain_id)
        c.execute('insert into chains values (?,?,?,?,?,?,?,?,?)',(
            chain_id,spec['title'],spec['requirement_id'],spec.get('source_session_id'),utcnow(),'BUILDING','NO_CAUSAL_PROOF',spec.get('truth_boundary') or 'Zeitliche Reihenfolge allein beweist keine Kausalität.',json.dumps(spec.get('metadata') or {},ensure_ascii=False,sort_keys=True)))
        node_ids={}
        for position,node in enumerate(nodes,1):
            if node['node_type'] not in NODE_TYPES:raise ValueError(node['node_type'])
            if node['source_type'] not in SOURCE_TYPES:raise ValueError(node['source_type'])
            source_sha,excerpt,event_id=resolve_source(c,node)
            node_id=node.get('node_id') or stable_id('node',chain_id,str(position),node['node_type'],node['label'])
            if node.get('key') in node_ids:raise ValueError('Doppelter node key')
            node_ids[node.get('key') or node_id]=node_id
            status=node.get('status') or ('UNBEKANNT' if node['source_type']=='gap' else 'BELEGT')
            truth_class=node.get('truth_class') or ('EXPLICIT_GAP' if node['source_type']=='gap' else 'SOURCE_BOUND')
            c.execute('insert into chain_nodes values (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(
                node_id,chain_id,position,node['node_type'],node['label'],node['source_type'],node.get('source_ref'),source_sha,excerpt,event_id,truth_class,status,node.get('gap_reason'),json.dumps(node.get('metadata') or {},ensure_ascii=False,sort_keys=True)))
        for link in links:
            relation_class=link['relation_class']
            if relation_class not in LINK_CLASSES:raise ValueError(relation_class)
            from_id=node_ids.get(link['from']);to_id=node_ids.get(link['to'])
            if not from_id or not to_id:raise KeyError(f'Unbekannter Linkknoten {link}')
            refs=link.get('evidence_refs') or []
            if relation_class in {'EXPLICIT_PARENT_EVENT','COMMON_ARTIFACT_SUPPORTED'} and not refs:
                raise ValueError(f'{relation_class} verlangt evidence_refs')
            causal_claim=bool(link.get('causal_claim',False))
            if causal_claim and relation_class!='EXPLICIT_PARENT_EVENT':
                raise PermissionError('Eine Kausalbehauptung ist nur mit EXPLICIT_PARENT_EVENT zulässig')
            link_id=stable_id('link',chain_id,from_id,to_id,link['relation'])
            c.execute('insert into chain_links values (?,?,?,?,?,?,?,?,?,?)',(
                link_id,chain_id,from_id,to_id,link['relation'],relation_class,PROOF_STRENGTH[relation_class],json.dumps(refs,ensure_ascii=False),link.get('explanation') or '',int(causal_claim)))
        assessment=assess_chain(c,chain_id);c.commit()
    return {'ok':True,'chain_id':chain_id,'assessment':assessment}


def inspect_chain(db:Path,chain_id:str) -> dict[str,Any]:
    with connect(db) as c:
        chain=c.execute('select * from chains where chain_id=?',(chain_id,)).fetchone()
        if chain is None:raise FileNotFoundError(chain_id)
        nodes=[dict(r) for r in c.execute('select * from chain_nodes where chain_id=? order by position',(chain_id,))]
        links=[dict(r) for r in c.execute('select * from chain_links where chain_id=? order by rowid',(chain_id,))]
        assessment=dict(c.execute('select * from chain_assessments where chain_id=?',(chain_id,)).fetchone())
    for row in links:row['evidence_refs']=json.loads(row.pop('evidence_refs_json'))
    return {'ok':True,'chain':dict(chain),'nodes':nodes,'links':links,'assessment':assessment,'truth_boundary':'Kandidaten und kuratierte Relationen sind keine Kausalbeweise.'}


def list_chains(db:Path) -> dict[str,Any]:
    with connect(db) as c:
        rows=[dict(r) for r in c.execute('select c.*,a.node_count,a.gap_count,a.completeness_status from chains c left join chain_assessments a using(chain_id) order by c.created_utc')]
    return {'ok':True,'count':len(rows),'chains':rows}


def main()->int:
    p=argparse.ArgumentParser(prog='gesamtatlas-terminalwirkung');p.add_argument('--db',type=Path,default=DEFAULT_DB)
    sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('import-history');q.add_argument('--history',type=Path,default=DEFAULT_HISTORY)
    q=sub.add_parser('create-chain');q.add_argument('--spec',type=Path,required=True)
    q=sub.add_parser('inspect');q.add_argument('--chain-id',required=True)
    sub.add_parser('list')
    args=p.parse_args()
    try:
        if args.command=='import-history':value=import_history(args.db,args.history)
        elif args.command=='create-chain':value=create_chain(args.db,args.spec)
        elif args.command=='inspect':value=inspect_chain(args.db,args.chain_id)
        else:value=list_chains(args.db)
        print(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True));return 0
    except Exception as exc:
        print(json.dumps({'ok':False,'error':f'{type(exc).__name__}: {exc}'},ensure_ascii=False,indent=2),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
