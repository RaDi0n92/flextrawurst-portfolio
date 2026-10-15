#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
GLOBAL_HISTORY=Path('/root/werkraum/_gpt/session_history.jsonl')
LOCAL_HISTORY=ROOT/'07_HISTORY/GRUENDUNGSEVENTS.jsonl'
OUTPUT=ROOT/'Zeitstrom'
ROOT_ENTRY=ROOT/'ZEITSTROM.md'
BERLIN=ZoneInfo('Europe/Berlin')
UTC=dt.timezone.utc
TARGET=str(ROOT)
KEYWORDS=('worldwords_antibibel','worldwords-antibibel','ANTIBIBEL','antibibel-foundation')


def sha(path:Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()

def atomic(path:Path,text:str)->None:
 path.parent.mkdir(parents=True,exist_ok=True)
 data=(text.rstrip()+'\n').encode('utf-8')
 fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass
 if path.read_bytes()!=data:raise RuntimeError(f'Rücklesefehler {path}')

def safe(value:str)->str:
 return re.sub(r'[^A-Za-z0-9_.-]+','-',value).strip('-')[:180] or 'unknown'

def read_jsonl(path:Path):
 if not path.exists():return []
 rows=[]
 for no,line in enumerate(path.read_text(encoding='utf-8',errors='replace').splitlines(),1):
  if not line.strip():continue
  try:r=json.loads(line)
  except Exception as e:raise RuntimeError(f'Ungültiges JSONL {path}:{no}: {e}')
  if isinstance(r,dict):rows.append(r)
 return rows

def relevant(event:dict)->bool:
 raw=json.dumps(event,ensure_ascii=False)
 return TARGET in raw or any(k in raw for k in KEYWORDS)

def normalize_global(event:dict)->dict:
 raw=str(event.get('timestamp_utc') or '')
 try:
  stamp=dt.datetime.fromisoformat(raw.replace('Z','+00:00'))
  if stamp.tzinfo is None:stamp=stamp.replace(tzinfo=UTC)
  stamp=stamp.astimezone(UTC);berlin=stamp.astimezone(BERLIN)
  precise=True
 except Exception:
  stamp=None;berlin=None;precise=False
 details=event.get('details') if isinstance(event.get('details'),dict) else {}
 summary=details.get('summary') or details.get('title') or event.get('action') or 'Ereignis'
 return {
  'schema_version':'1.0','event_id':str(event.get('event_id') or hashlib.sha256(json.dumps(event,sort_keys=True).encode()).hexdigest()[:32]),
  'source_kind':'global_hash_history','timestamp_utc':stamp.isoformat() if stamp else None,
  'timestamp_berlin':berlin.isoformat() if berlin else None,'time_precision':'exact' if precise else 'unknown',
  'date_berlin':berlin.date().isoformat() if berlin else None,'parallel_second_key_utc':stamp.strftime('%Y-%m-%dT%H:%M:%SZ') if stamp else None,
  'session_id':str(event.get('session_id') or 'unknown-session'),'actor':str(event.get('actor') or 'unknown-actor'),
  'action':str(event.get('action') or 'unknown'),'status':str(event.get('status') or 'unknown'),
  'summary':re.sub(r'\s+',' ',str(summary)).strip()[:800],'target':event.get('target'),
  'event_hash':event.get('event_hash'),'parent_event_id':event.get('parent_event_id'),'details':details,
  'truth_class':'BESTAETIGT_TECHNISCHE_HISTORY'
 }

def normalize_local(event:dict)->dict:
 payload=json.dumps(event,ensure_ascii=False,sort_keys=True)
 eid='local-'+hashlib.sha256(payload.encode()).hexdigest()[:24]
 raw=event.get('timestamp_utc');stamp=None;berlin=None
 if raw:
  try:
   stamp=dt.datetime.fromisoformat(str(raw).replace('Z','+00:00'))
   if stamp.tzinfo is None:stamp=stamp.replace(tzinfo=UTC)
   stamp=stamp.astimezone(UTC);berlin=stamp.astimezone(BERLIN)
  except Exception:pass
 return {
  'schema_version':'1.0','event_id':eid,'source_kind':'local_meaning_history','timestamp_utc':stamp.isoformat() if stamp else None,
  'timestamp_berlin':berlin.isoformat() if berlin else None,'time_precision':event.get('timestamp_precision','unknown'),
  'date_berlin':berlin.date().isoformat() if berlin else event.get('date'),'parallel_second_key_utc':stamp.strftime('%Y-%m-%dT%H:%M:%SZ') if stamp else None,
  'session_id':str(event.get('session_id') or 'chatgpt-20260726T050656Z-20db395fc624'),'actor':event.get('actor','Daniel und beteiligte AI-Ströme'),
  'action':event.get('kind','local.event'),'status':event.get('status','recorded'),'summary':event.get('summary','Lokales Bedeutungsereignis'),
  'target':event.get('target'),'event_hash':None,'parent_event_id':None,'details':event,'truth_class':event.get('truth_class','BESTAETIGT_LOKAL')
 }

def sort_key(t:dict):
 if t.get('timestamp_utc'):
  try:return (0,dt.datetime.fromisoformat(t['timestamp_utc']).timestamp(),t['event_id'])
  except Exception:pass
 return (1,str(t.get('date_berlin') or ''),int(t.get('details',{}).get('sequence',999999)),t['event_id'])

def event_link(eid:str)->str:return f'[[Zeitstrom/ereignisse/{eid}|{eid[:14]}]]'
def session_link(sid:str)->str:
 p=ROOT/'sessions'/sid/'SESSION_ORIGIN.md'
 return f'[[sessions/{sid}/SESSION_ORIGIN|{sid}]]' if p.exists() else f'`{sid}`'
def tick_line(t:dict)->str:
 when=t.get('timestamp_berlin') or f"{t.get('date_berlin') or 'Zeit unbekannt'} · Reihenfolge {t.get('details',{}).get('sequence','?')}"
 return f"- **{when}** · {event_link(t['event_id'])} · {session_link(t['session_id'])} · `{t['action']}` · {t['summary']}"
def event_page(t:dict)->str:
 target_display=json.dumps(t.get('target'),ensure_ascii=False).replace('`','\\u0060').replace('[','\\u005b').replace(']','\\u005d')
 return f'''---
title: "Zeitereignis {t['event_id']}"
type: project-time-event
event_id: "{t['event_id']}"
session_id: "{t['session_id']}"
generated: true
truth_class: "{t['truth_class']}"
---

# {t['summary']}

- **Quelle:** `{t['source_kind']}`
- **UTC:** `{t.get('timestamp_utc')}`
- **Berlin:** `{t.get('timestamp_berlin')}`
- **Zeitpräzision:** `{t.get('time_precision')}`
- **Session:** {session_link(t['session_id'])}
- **Akteur:** `{t.get('actor')}`
- **Aktion:** `{t.get('action')}`
- **Status:** `{t.get('status')}`
- **Ziel:** `{target_display[:12000]}`
- **Event-Hash:** `{t.get('event_hash')}`
- **Parent:** `{t.get('parent_event_id')}`

## Technische beziehungsweise lokale Details

```json
{json.dumps(t.get('details',{}),ensure_ascii=False,indent=2)}
```

## Navigation

- [[ZEITSTROM|Zeitstrom]]
- [[HOME|Vault Home]]
'''
def root_page(ticks:list[dict])->str:
 exact=[t for t in ticks if t.get('timestamp_utc')];floating=[t for t in ticks if not t.get('timestamp_utc')]
 by_day=Counter(t.get('date_berlin') or 'unbekannt' for t in ticks);by_session=Counter(t['session_id'] for t in ticks)
 text='''---
title: "WorldWORDS ANTIBIBEL · Zeitstrom"
type: project-time-stream
generated: true
truth_class: ABGELEITET_AUS_GLOBALER_UND_LOKALER_HISTORY
---

# Zeitstrom der WorldWORDS ANTIBIBEL

> Die globale hashverkettete History bleibt technische Primärquelle. Dieser Zeitstrom filtert nur reale ANTIBIBEL-Bezüge und ergänzt lokale Bedeutungsereignisse. Ereignisse ohne belegte Uhrzeit werden nicht künstlich sekundengenau gemacht.

'''
 text+=f'- **Ereignisse:** `{len(ticks)}`\n- **Mit exakter Uhrzeit:** `{len(exact)}`\n- **Nur Gesprächsreihenfolge:** `{len(floating)}`\n- **Sessions:** `{len(by_session)}`\n\n## Tage\n\n'
 for day,count in sorted(by_day.items(),reverse=True):text+=f'- [[Zeitstrom/tage/{safe(day)}|{day}]] · `{count}`\n'
 text+='\n## Sessions\n\n'
 for sid,count in by_session.most_common():text+=f'- [[Zeitstrom/sessions/{safe(sid)}|{sid}]] · `{count}`\n'
 text+='\n## Chronik\n\n'
 for t in ticks:text+=tick_line(t)+'\n'
 text+='\n## Weitere Netze\n\n- [[GESPRAECHSNETZ|Gesprächs- und Bedeutungsnetz]]\n- [[AKTUELLE_WAHRHEIT|Aktuelle Wahrheit]]\n- [[HOME|Vault Home]]\n'
 return text

def build()->dict:
 global_rows=[normalize_global(e) for e in read_jsonl(GLOBAL_HISTORY) if relevant(e)]
 local_rows=[normalize_local(e) for e in read_jsonl(LOCAL_HISTORY)]
 seen={};
 for t in global_rows+local_rows:seen[t['event_id']]=t
 ticks=sorted(seen.values(),key=sort_key)
 temp=Path(tempfile.mkdtemp(prefix='.zeitstrom-build-',dir=ROOT))
 try:
  for sub in ['ereignisse','tage','sessions']: (temp/sub).mkdir(parents=True,exist_ok=True)
  for t in ticks:atomic(temp/'ereignisse'/f"{t['event_id']}.md",event_page(t))
  by_day=defaultdict(list);by_session=defaultdict(list)
  for t in ticks:by_day[t.get('date_berlin') or 'unbekannt'].append(t);by_session[t['session_id']].append(t)
  for day,rows in by_day.items():
   body=f'# Zeitstrom · {day}\n\n'+''.join(tick_line(t)+'\n' for t in rows)+'\n- [[ZEITSTROM|Zeitstrom]]\n'
   atomic(temp/'tage'/f'{safe(day)}.md',body)
  for sid,rows in by_session.items():
   body=f'# Sessionzeit · {sid}\n\n'+''.join(tick_line(t)+'\n' for t in rows)+'\n- [[ZEITSTROM|Zeitstrom]]\n'
   atomic(temp/'sessions'/f'{safe(sid)}.md',body)
  jsonl=''.join(json.dumps(t,ensure_ascii=False,sort_keys=True)+'\n' for t in ticks)
  atomic(temp/'events.jsonl',jsonl)
  manifest={'schema_version':'1.0','generated_utc':dt.datetime.now(UTC).isoformat(),'truth_class':'ABGELEITET','global_history_path':str(GLOBAL_HISTORY),'global_history_sha256':sha(GLOBAL_HISTORY) if GLOBAL_HISTORY.exists() else None,'local_history_path':str(LOCAL_HISTORY),'local_history_sha256':sha(LOCAL_HISTORY) if LOCAL_HISTORY.exists() else None,'global_matched_events':len(global_rows),'local_meaning_events':len(local_rows),'event_count':len(ticks),'session_count':len(by_session),'day_count':len(by_day),'first_exact_utc':next((t['timestamp_utc'] for t in ticks if t.get('timestamp_utc')),None),'last_exact_utc':next((t['timestamp_utc'] for t in reversed(ticks) if t.get('timestamp_utc')),None)}
  atomic(temp/'MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
  page=root_page(ticks);atomic(temp/'ZEITSTROM.md',page)
  if OUTPUT.exists():shutil.rmtree(OUTPUT)
  os.replace(temp,OUTPUT);atomic(ROOT_ENTRY,page)
 finally:
  if temp.exists():shutil.rmtree(temp,ignore_errors=True)
 return {'ok':True,'manifest':manifest,'root_entry':str(ROOT_ENTRY),'output':str(OUTPUT)}
if __name__=='__main__':print(json.dumps(build(),ensure_ascii=False,indent=2))
