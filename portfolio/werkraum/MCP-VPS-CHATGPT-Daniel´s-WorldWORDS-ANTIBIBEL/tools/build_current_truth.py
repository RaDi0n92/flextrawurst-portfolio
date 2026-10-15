#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ENGINE=ROOT/'truth_engine'
UTC=dt.timezone.utc
GENERATED_PREFIXES=('MOC/','Verweise/','Zeitstrom/','truth_engine/','validation/','.obsidian/','ui_exports/')
GENERATED_ROOT={'HOME.md','GESPRAECHSNETZ.md','ZEITSTROM.md','AKTUELLE_WAHRHEIT.md','AKTUELLE_WAHRHEIT.json'}

def sha(p:Path)->str:
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''):h.update(c)
 return h.hexdigest()
def atomic(path:Path,data:bytes)->None:
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  try:os.unlink(tmp)
  except FileNotFoundError:pass
 if path.read_bytes()!=data:raise RuntimeError(f'Rücklesefehler {path}')
def jread(path:Path,default=None):
 try:return json.loads(path.read_text(encoding='utf-8'))
 except Exception:return default

def primary_files()->list[Path]:
 out=[]
 for p in ROOT.rglob('*'):
  if not p.is_file() or '__pycache__' in p.parts:continue
  r=p.relative_to(ROOT).as_posix()
  if r in GENERATED_ROOT or any(r.startswith(x) for x in GENERATED_PREFIXES):continue
  out.append(p)
 return sorted(out,key=lambda p:p.relative_to(ROOT).as_posix())
def inventory(files:list[Path])->list[dict]:
 return [{'path':p.relative_to(ROOT).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p),'modified_utc':dt.datetime.fromtimestamp(p.stat().st_mtime,tz=UTC).isoformat()} for p in files]
def fingerprint(rows:list[dict])->str:
 raw='\n'.join(f"{r['path']}\0{r['sha256']}\0{r['bytes']}" for r in rows).encode();return hashlib.sha256(raw).hexdigest()
def markdown(data:dict)->str:
 v=data['validation'];g=data['conversation_graph'];t=data['time_stream'];w=data['watchdog'];words=data['word_entries'];gaps=data['open_gaps']
 text=f'''---
title: "Aktuelle Wahrheit · WorldWORDS ANTIBIBEL"
type: current-truth
truth_status: "{data['truth_status']}"
generation_id: "{data['generation_id']}"
source_fingerprint: "{data['source_fingerprint']}"
generated_utc: "{data['generated_utc']}"
generated: true
---

# Aktuelle Wahrheit der WorldWORDS ANTIBIBEL

> [!important] Status: {data['truth_status']}
> Diese Sicht ist beweisgebunden und vorläufig. Sie darf durch neue Gespräche, Korrekturen, Wortfunde und reale Verkörperungen wachsen. Der lokale Watchdog ist nicht als Systemdienst installiert; automatische Aktualität ist deshalb nicht behauptet.

## Bestätigter Kern

- Der Projektkörper existiert unter `{ROOT}`.
- Die Freundesanekdote ist durch Daniel bestätigt; Name, Zeitpunkt und exakter damaliger Wortlaut bleiben unbekannt.
- Daniel verwendet ungewöhnliche Wörter seit der Arbeit mit AI-Strömen bewusst als Bedeutungs- und Baukeime.
- `Verdeutschen` bedeutet hier verbindlich freiwillige Übernahme nach Verstehen der Tragweite, niemals Sprachzwang.
- Die ANTIBIBEL ist ausdrücklich kein Kanon und keine Sprachuniform.
- `Symbositierung` besitzt bereits externe reale Verkörperungen im verwandten Hauptprojekt.

## Zahlen

- **Primär-/Arbeitsdateien:** `{data['primary_file_count']}`
- **Primärbytes:** `{data['primary_total_bytes']}`
- **Wortkörper:** `{len(words)}`
- **Gesprächsquellen:** `{data['conversation_source_count']}`
- **Graphquellen:** `{g.get('source_count')}`
- **Graphabschnitte:** `{g.get('section_count')}`
- **Begriffsknoten:** `{g.get('concept_count')}`
- **Verwandtschaftskanten:** `{g.get('related_edge_count')}`
- **Zeitereignisse:** `{t.get('event_count')}`
- **Interne Links geprüft:** `{v.get('internal_links_checked')}`
- **Tote Links:** `{len(v.get('broken_links',[]))}`

## Wortkörper

'''
 for word in words:text+=f"- [[02_WORTKOERPER/{word['stem']}|{word['title']}]] · `{word['truth_class']}`\n"
 text+='\n## Watchdog\n\n'
 text+=f"- **Status:** `{w.get('status','UNKNOWN')}`\n- **systemd installiert:** `{w.get('systemd_installed',False)}`\n- **automatische Aktualität bestätigt:** `{data['automatic_freshness_confirmed']}`\n"
 text+='\n## Validierung\n\n'
 text+=f"- **OK:** `{v.get('ok')}`\n- **Tote Links:** `{len(v.get('broken_links',[]))}`\n- **Fehlende Katalogeinträge:** `{len(v.get('missing_from_catalog',[]))}`\n- **Quellhash-Fehler:** `{len(v.get('source_manifest_errors',[]))}`\n"
 text+='\n## Offene Lücken\n\n'
 if gaps:
  for gap in gaps:text+=f"- **{gap.get('gap_id')} · {gap.get('status')}:** {gap.get('title')} · {gap.get('need')}\n"
 else:text+='- Keine offenen Lücken gelesen. Das wäre verdächtig.\n'
 text+='\n## Navigation\n\n- [[HOME|Vault Home]]\n- [[GESPRAECHSNETZ|Gesprächsnetz]]\n- [[ZEITSTROM|Zeitstrom]]\n- [[validation/VALIDATION_REPORT|Validierung]]\n'
 return text

def build(phase:str)->dict:
 now=dt.datetime.now(UTC).isoformat();files=primary_files();rows=inventory(files);fp=fingerprint(rows)
 validation=jread(ROOT/'validation/VALIDATION_REPORT.json',{}) or {}
 graph=jread(ROOT/'Verweise/MANIFEST.json',{}) or {}
 timeline=jread(ROOT/'Zeitstrom/MANIFEST.json',{}) or {}
 watchdog=jread(ROOT/'watchdog/STATUS.json',{}) or {'status':'AVAILABLE_NOT_INSTALLED','systemd_installed':False}
 gap_doc=jread(ROOT/'sessions/chatgpt-20260726T050656Z-20db395fc624/OPEN_GAPS.json',{}) or {}
 word_entries=[]
 for p in sorted((ROOT/'02_WORTKOERPER').glob('*.md')):
  if p.name=='00_WORTREGISTER.md':continue
  text=p.read_text(encoding='utf-8',errors='replace');title=next((line[2:].strip() for line in text.splitlines() if line.startswith('# ')),p.stem)
  tc='BESTAETIGT' if 'truth_class: BESTAETIGT' in text else 'MODELLIERT_ODER_OFFEN'
  word_entries.append({'stem':p.stem,'title':title,'truth_class':tc,'sha256':sha(p)})
 status='LOCAL_VALIDATED_PROVISIONAL' if validation.get('ok') else ('LOCAL_PROVISIONAL_UNVALIDATED' if not validation else 'LOCAL_PROVISIONAL_WITH_VALIDATION_GAPS')
 gid=dt.datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')+'-'+fp[:12]
 data={'schema_version':'1.0','generation_id':gid,'generated_utc':now,'phase':phase,'truth_status':status,'source_fingerprint':fp,'primary_file_count':len(rows),'primary_total_bytes':sum(r['bytes'] for r in rows),'primary_inventory':rows,'word_entries':word_entries,'conversation_source_count':len(list((ROOT/'06_GESPRAECHE').glob('*.md'))),'conversation_graph':graph,'time_stream':timeline,'validation':validation,'watchdog':watchdog,'automatic_freshness_confirmed':False,'open_gaps':gap_doc.get('gaps',[]),'source_truth_rule':'Originalgespräche und Wortsetzungen bleiben Primärquellen; diese Ansicht ist regenerierbar.'}
 md=markdown(data);payload=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode();mdbytes=(md.rstrip()+'\n').encode()
 gen=ENGINE/'generations/live'/gid;gen.mkdir(parents=True,exist_ok=True)
 atomic(gen/'AKTUELLE_WAHRHEIT.json',payload);atomic(gen/'AKTUELLE_WAHRHEIT.md',mdbytes)
 hashes={'generation_id':gid,'files':{'AKTUELLE_WAHRHEIT.json':hashlib.sha256(payload).hexdigest(),'AKTUELLE_WAHRHEIT.md':hashlib.sha256(mdbytes).hexdigest()}}
 atomic(gen/'GENERATION_HASHES.json',(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n').encode())
 atomic(ROOT/'AKTUELLE_WAHRHEIT.json',payload);atomic(ROOT/'AKTUELLE_WAHRHEIT.md',mdbytes)
 pointer={'generation_id':gid,'published_utc':now,'truth_status':status,'source_fingerprint':fp,'generation_path':str(gen),'automatic_freshness_confirmed':False}
 atomic(ENGINE/'CURRENT_POINTER.json',(json.dumps(pointer,ensure_ascii=False,indent=2)+'\n').encode())
 if validation.get('ok'):atomic(ENGINE/'LAST_GOOD.json',(json.dumps(pointer,ensure_ascii=False,indent=2)+'\n').encode())
 health={'status':'healthy' if validation.get('ok') else 'provisional','updated_utc':now,'generation_id':gid,'truth_status':status,'watchdog_status':watchdog.get('status'),'automatic_freshness_confirmed':False,'validation_ok':validation.get('ok'),'source_fingerprint':fp}
 atomic(ENGINE/'runtime/health.json',(json.dumps(health,ensure_ascii=False,indent=2)+'\n').encode())
 return {'ok':True,'generation_id':gid,'truth_status':status,'source_fingerprint':fp,'primary_file_count':len(rows),'root_markdown':str(ROOT/'AKTUELLE_WAHRHEIT.md')}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--phase',default='manual');a=ap.parse_args();print(json.dumps(build(a.phase),ensure_ascii=False,indent=2))
