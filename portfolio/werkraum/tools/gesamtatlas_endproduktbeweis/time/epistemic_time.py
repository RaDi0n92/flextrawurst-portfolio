#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB = Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/ZEITREISE/EPISTEMISCHE_MOMENTE.sqlite')
DEFAULT_HISTORY = Path('/root/werkraum/_gpt/session_history.jsonl')
STATES = ('EXISTIERTE','ERREICHBAR','ANGEZEIGT','GELESEN','VERWENDET')
STATUS = {'BEWIESEN','BEHAUPTET','UNBEKANNT','WIDERLEGT'}
EVIDENCE_CLASSES = {'DIRECT_SOURCE','SYSTEM_OBSERVED','USER_CONFIRMED','ATTRIBUTED_CLAIM','MODEL_DERIVED'}
SUFFICIENT = {
 'EXISTIERTE': {'DIRECT_SOURCE','SYSTEM_OBSERVED'},
 'ERREICHBAR': {'SYSTEM_OBSERVED','USER_CONFIRMED'},
 'ANGEZEIGT': {'SYSTEM_OBSERVED','USER_CONFIRMED'},
 'GELESEN': {'SYSTEM_OBSERVED','USER_CONFIRMED'},
 'VERWENDET': {'DIRECT_SOURCE','SYSTEM_OBSERVED','USER_CONFIRMED'},
}
SCHEMA='''
pragma foreign_keys=on;
create table if not exists history_events(
 event_id text primary key,timestamp_utc text not null,session_id text,actor text,action text,status text,
 target text,parent_event_id text,event_hash text,details_json text not null,raw_json text not null
);
create index if not exists idx_history_session_time on history_events(session_id,timestamp_utc,event_id);
create table if not exists moments(
 moment_id text primary key,title text not null,at_utc text not null,source_session_id text,
 anchor_event_id text references history_events(event_id),created_utc text not null,status text not null,
 truth_boundary text not null,metadata_json text not null
);
create table if not exists moment_items(
 item_id text primary key,moment_id text not null references moments(moment_id),label text not null,
 object_ref text not null,object_type text not null,first_known_utc text,source_path text,source_sha256 text,
 metadata_json text not null,unique(moment_id,object_ref)
);
create table if not exists item_attestations(
 attestation_id text primary key,item_id text not null references moment_items(item_id),state text not null,
 status text not null,evidence_class text not null,evidence_ref text not null,evidence_sha256 text,
 observed_utc text not null,actor text not null,statement text not null,metadata_json text not null,
 unique(item_id,state,evidence_ref,statement)
);
create table if not exists item_assessments(
 item_id text not null references moment_items(item_id),state text not null,effective_status text not null,
 attestation_count integer not null,sufficient_count integer not null,explanation text not null,
 updated_utc text not null,primary key(item_id,state)
);
create table if not exists technical_context(
 context_id text primary key,moment_id text not null references moments(moment_id),event_id text not null references history_events(event_id),
 context_type text not null,label text not null,truth_class text not null,unique(moment_id,event_id,context_type)
);
create table if not exists retrospective_meaning(
 meaning_id text primary key,moment_id text not null references moments(moment_id),learned_utc text not null,
 label text not null,source_ref text not null,source_sha256 text,statement text not null,
 truth_class text not null,metadata_json text not null
);
create table if not exists moment_assessments(
 moment_id text primary key references moments(moment_id),item_count integer not null,unknown_state_count integer not null,
 technical_event_count integer not null,tool_event_count integer not null,mutation_event_count integer not null,
 retrospective_count integer not null,completeness_status text not null,updated_utc text not null
);
'''

def utcnow()->str:return datetime.now(timezone.utc).isoformat()
def parse_time(value:str)->datetime:return datetime.fromisoformat(value.replace('Z','+00:00'))
def stable_id(prefix:str,*parts:str,length:int=24)->str:return prefix+':'+hashlib.sha256('\0'.join(parts).encode('utf-8',errors='replace')).hexdigest()[:length]
def sha256_file(path:Path)->str:
 d=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):d.update(chunk)
 return d.hexdigest()
def connect(path:Path)->sqlite3.Connection:
 path.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(path,timeout=30);c.row_factory=sqlite3.Row
 c.execute('pragma journal_mode=WAL');c.execute('pragma synchronous=FULL');c.executescript(SCHEMA);return c
def emit(v:Any)->None:print(json.dumps(v,ensure_ascii=False,indent=2,sort_keys=True,default=str))
def event_context_type(action:str,target:str|None)->str:
 low=(action+' '+str(target or '')).lower()
 if any(x in low for x in ('playwright','pytest','test_','validation','integrity')):return 'TEST'
 if action in {'write_file','append_file','vps.write_file','vps.edit_file','vps.delete','vps.move','tracked_write_file','tracked_append_file'}:return 'MUTATION'
 if action.startswith('services.'):return 'SERVICE'
 if action.startswith('vps.') or action in {'read_file','reread_own_file'}:return 'TOOL'
 return 'EVENT'

def import_history(db:Path,history:Path)->dict[str,Any]:
 if not history.exists():raise FileNotFoundError(history)
 inserted=updated=skipped=0
 with connect(db) as c:
  for line in history.open('r',encoding='utf-8',errors='replace'):
   try:r=json.loads(line)
   except Exception:skipped+=1;continue
   if not r.get('event_id') or not r.get('timestamp_utc'):skipped+=1;continue
   exists=c.execute('select 1 from history_events where event_id=?',(r['event_id'],)).fetchone()
   c.execute('insert or replace into history_events values (?,?,?,?,?,?,?,?,?,?,?)',(
    r['event_id'],r['timestamp_utc'],r.get('session_id'),r.get('actor'),r.get('action'),r.get('status'),r.get('target'),r.get('parent_event_id'),r.get('event_hash'),json.dumps(r.get('details') or {},ensure_ascii=False,sort_keys=True),json.dumps(r,ensure_ascii=False,sort_keys=True)))
   inserted+=int(not exists);updated+=int(bool(exists))
  count=c.execute('select count(*) from history_events').fetchone()[0]
 return {'ok':True,'history_path':str(history),'history_sha256':sha256_file(history),'inserted':inserted,'updated':updated,'skipped':skipped,'event_count':count}
def recompute_item(c:sqlite3.Connection,item_id:str)->list[dict[str,Any]]:
 out=[]
 for state in STATES:
  rows=list(c.execute('select * from item_attestations where item_id=? and state=? order by observed_utc,attestation_id',(item_id,state)))
  sufficient=[r for r in rows if r['evidence_class'] in SUFFICIENT[state] and r['status'] in {'BEWIESEN','WIDERLEGT'}]
  positive=[r for r in sufficient if r['status']=='BEWIESEN'];negative=[r for r in sufficient if r['status']=='WIDERLEGT']
  claims=[r for r in rows if r['status']=='BEHAUPTET']
  if positive and negative:eff='WIDERSPRUECHLICH';ex='Hinreichende Belege widersprechen einander.'
  elif positive:eff='BEWIESEN';ex='Eigener hinreichender Beleg für diese Stufe.'
  elif negative:eff='WIDERLEGT';ex='Eigener hinreichender Gegenbeleg für diese Stufe.'
  elif claims:eff='BEHAUPTET';ex='Nur Behauptungen oder unzureichende Beweisklassen.'
  else:eff='UNBEKANNT';ex='Kein eigener Beleg; frühere Stufen werden nicht vererbt.'
  c.execute('insert or replace into item_assessments values (?,?,?,?,?,?,?)',(item_id,state,eff,len(rows),len(sufficient),ex,utcnow()))
  out.append({'state':state,'effective_status':eff,'attestations':len(rows),'sufficient':len(sufficient),'explanation':ex})
 return out
def recompute_moment(c:sqlite3.Connection,moment_id:str)->dict[str,Any]:
 item_count=c.execute('select count(*) from moment_items where moment_id=?',(moment_id,)).fetchone()[0]
 unknown=c.execute("select count(*) from item_assessments a join moment_items i on i.item_id=a.item_id where i.moment_id=? and a.effective_status='UNBEKANNT'",(moment_id,)).fetchone()[0]
 event_count=c.execute('select count(*) from technical_context where moment_id=?',(moment_id,)).fetchone()[0]
 tools=c.execute("select count(*) from technical_context where moment_id=? and context_type in ('TOOL','SERVICE')",(moment_id,)).fetchone()[0]
 mutations=c.execute("select count(*) from technical_context where moment_id=? and context_type='MUTATION'",(moment_id,)).fetchone()[0]
 retro=c.execute('select count(*) from retrospective_meaning where moment_id=?',(moment_id,)).fetchone()[0]
 status='PARTIAL_WITH_UNKNOWNS' if unknown else ('EMPTY' if not item_count else 'EXPLICITLY_ATTESTED')
 c.execute('insert or replace into moment_assessments values (?,?,?,?,?,?,?,?,?)',(moment_id,item_count,unknown,event_count,tools,mutations,retro,status,utcnow()))
 return {'moment_id':moment_id,'item_count':item_count,'unknown_state_count':unknown,'technical_event_count':event_count,'tool_event_count':tools,'mutation_event_count':mutations,'retrospective_count':retro,'completeness_status':status}
def create_moment(db:Path,spec_path:Path)->dict[str,Any]:
 spec=json.loads(spec_path.read_text('utf-8'));at=parse_time(spec['at_utc']);mid=spec.get('moment_id') or stable_id('moment',spec['title'],spec['at_utc'])
 with connect(db) as c:
  if c.execute('select 1 from moments where moment_id=?',(mid,)).fetchone():raise FileExistsError(mid)
  anchor=spec.get('anchor_event_id')
  if anchor:
   e=c.execute('select * from history_events where event_id=?',(anchor,)).fetchone()
   if e is None:raise FileNotFoundError(f'anchor_event_id fehlt: {anchor}')
   if parse_time(e['timestamp_utc'])!=at:raise ValueError('at_utc muss exakt dem Anchor-Ereignis entsprechen')
  c.execute('insert into moments values (?,?,?,?,?,?,?,?,?)',(mid,spec['title'],spec['at_utc'],spec.get('source_session_id'),anchor,utcnow(),'BUILDING',spec.get('truth_boundary') or 'Spätere Erkenntnisse verändern den damaligen Wissensstand nicht.',json.dumps(spec.get('metadata') or {},ensure_ascii=False,sort_keys=True)))
  # Technical events up to the moment only.
  if spec.get('include_session_history',True) and spec.get('source_session_id'):
   for e in c.execute('select * from history_events where session_id=? and timestamp_utc<=? order by timestamp_utc,event_id',(spec['source_session_id'],spec['at_utc'])):
    kind=event_context_type(e['action'] or '',e['target'])
    cid=stable_id('ctx',mid,e['event_id'],kind)
    c.execute('insert into technical_context values (?,?,?,?,?,?)',(cid,mid,e['event_id'],kind,f"{e['action']} · {e['status']}",'TECHNICALLY_OBSERVED'))
  for item in spec.get('items') or []:
   source_path=item.get('source_path');source_sha=None
   if source_path:
    p=Path(source_path).resolve()
    if not p.exists() or not p.is_file():raise FileNotFoundError(p)
    source_sha=sha256_file(p)
   first=item.get('first_known_utc')
   if first and parse_time(first)>at and item.get('known_at_moment',False):raise ValueError('Nach dem Moment entstandene Information darf nicht als damals bekannt markiert werden')
   iid=item.get('item_id') or stable_id('item',mid,item['object_ref'])
   c.execute('insert into moment_items values (?,?,?,?,?,?,?,?,?)',(iid,mid,item['label'],item['object_ref'],item['object_type'],first,source_path,source_sha,json.dumps(item.get('metadata') or {},ensure_ascii=False,sort_keys=True)))
   for att in item.get('attestations') or []:
    state=att['state'];status=att['status'];eclass=att['evidence_class'];eref=att['evidence_ref']
    if state not in STATES or status not in STATUS or eclass not in EVIDENCE_CLASSES:raise ValueError(f'Ungültige Attestierung: {att}')
    observed=parse_time(att.get('observed_utc') or spec['at_utc'])
    if observed>at:raise ValueError('Beleg nach dem Moment gehört in retrospective_meaning, nicht in den damaligen Zustand')
    if state in {'ANGEZEIGT','GELESEN','VERWENDET'} and eclass=='MODEL_DERIVED' and status=='BEWIESEN':
     # Allowed as stored claim, but cannot become effective proof; keep explicit.
     pass
    esha=None
    if eref.startswith('/'):
     ep=Path(eref)
     if not ep.exists() or not ep.is_file():raise FileNotFoundError(ep)
     esha=sha256_file(ep)
    aid=stable_id('att',iid,state,status,eclass,eref,att['statement'])
    c.execute('insert into item_attestations values (?,?,?,?,?,?,?,?,?,?,?)',(aid,iid,state,status,eclass,eref,esha,att.get('observed_utc') or spec['at_utc'],att['actor'],att['statement'],json.dumps(att.get('metadata') or {},ensure_ascii=False,sort_keys=True)))
   recompute_item(c,iid)
  for retro in spec.get('retrospective_meaning') or []:
   learned=parse_time(retro['learned_utc'])
   if learned<=at:raise ValueError('Retrospektive Bedeutung muss nach dem Moment liegen')
   ref=retro['source_ref'];rsha=None
   if ref.startswith('/'):
    rp=Path(ref)
    if not rp.exists() or not rp.is_file():raise FileNotFoundError(rp)
    rsha=sha256_file(rp)
   rid=stable_id('retro',mid,retro['learned_utc'],retro['label'],ref)
   c.execute('insert into retrospective_meaning values (?,?,?,?,?,?,?,?,?)',(rid,mid,retro['learned_utc'],retro['label'],ref,rsha,retro['statement'],retro.get('truth_class') or 'RETROSPECTIVE_SOURCE_BOUND',json.dumps(retro.get('metadata') or {},ensure_ascii=False,sort_keys=True)))
  assessment=recompute_moment(c,mid);c.execute('update moments set status=? where moment_id=?',(assessment['completeness_status'],mid));c.commit()
 return {'ok':True,'moment_id':mid,'assessment':assessment}
def inspect_moment(db:Path,moment_id:str)->dict[str,Any]:
 with connect(db) as c:
  m=c.execute('select * from moments where moment_id=?',(moment_id,)).fetchone()
  if m is None:raise FileNotFoundError(moment_id)
  items=[]
  for item in c.execute('select * from moment_items where moment_id=? order by rowid',(moment_id,)):
   d=dict(item);d['states']=[dict(x) for x in c.execute("select * from item_assessments where item_id=? order by case state when 'EXISTIERTE' then 1 when 'ERREICHBAR' then 2 when 'ANGEZEIGT' then 3 when 'GELESEN' then 4 when 'VERWENDET' then 5 end",(item['item_id'],))];d['attestations']=[dict(x) for x in c.execute('select * from item_attestations where item_id=? order by observed_utc,attestation_id',(item['item_id'],))];items.append(d)
  ctx=[dict(r) for r in c.execute('select tc.*,he.timestamp_utc,he.action,he.status as event_status,he.target from technical_context tc join history_events he using(event_id) where tc.moment_id=? order by he.timestamp_utc,he.event_id',(moment_id,))]
  retro=[dict(r) for r in c.execute('select * from retrospective_meaning where moment_id=? order by learned_utc,meaning_id',(moment_id,))]
  assessment=dict(c.execute('select * from moment_assessments where moment_id=?',(moment_id,)).fetchone())
 return {'ok':True,'moment':dict(m),'items':items,'technical_context':ctx,'retrospective_meaning':retro,'assessment':assessment,'truth_boundary':'Technischer Kontext ist nicht automatisch kognitives Wissen. Retrospektive Bedeutung bleibt getrennt vom damaligen Zustand.'}
def list_moments(db:Path)->dict[str,Any]:
 with connect(db) as c:rows=[dict(r) for r in c.execute('select m.*,a.item_count,a.unknown_state_count,a.completeness_status from moments m left join moment_assessments a using(moment_id) order by at_utc')]
 return {'ok':True,'count':len(rows),'moments':rows}
def main()->int:
 p=argparse.ArgumentParser(prog='gesamtatlas-zeitreise');p.add_argument('--db',type=Path,default=DEFAULT_DB)
 sub=p.add_subparsers(dest='command',required=True)
 q=sub.add_parser('import-history');q.add_argument('--history',type=Path,default=DEFAULT_HISTORY)
 q=sub.add_parser('create-moment');q.add_argument('--spec',type=Path,required=True)
 q=sub.add_parser('inspect');q.add_argument('--moment-id',required=True)
 sub.add_parser('list')
 a=p.parse_args()
 try:
  if a.command=='import-history':v=import_history(a.db,a.history)
  elif a.command=='create-moment':v=create_moment(a.db,a.spec)
  elif a.command=='inspect':v=inspect_moment(a.db,a.moment_id)
  else:v=list_moments(a.db)
  emit(v);return 0
 except Exception as exc:emit({'ok':False,'error':f'{type(exc).__name__}: {exc}'});return 1
if __name__=='__main__':raise SystemExit(main())
