#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,shutil,sqlite3,tempfile
from datetime import datetime,timezone
from pathlib import Path

ROOT=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis')
DB=ROOT/'ANFORDERUNGEN/ANFORDERUNGSREGISTER.sqlite'
JSONL=ROOT/'ANFORDERUNGEN/ANFORDERUNGSREGISTER.jsonl'
MATRIX=ROOT/'ANFORDERUNGEN/ANFORDERUNGSMATRIX.md'
REPORT=ROOT/'EVIDENZ/GA-REQUIREMENTS-FINAL-BINDING-TECHNICAL.json'
BACKUP=ROOT/'ANFORDERUNGEN/BACKUPS'/f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}__ANFORDERUNGSREGISTER.sqlite"

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def merge(values,*extra):
 out=[]
 for x in [*values,*extra]:
  if x and x not in out:out.append(x)
 return out

def update(c,rid,status,paths=(),tech=(),pw=()):
 row=c.execute('select implementation_paths_json,technical_test_ids_json,playwright_test_ids_json from requirements where id=?',(rid,)).fetchone()
 if not row:raise KeyError(rid)
 c.execute('''update requirements set current_implementation_status=?,implementation_paths_json=?,technical_test_ids_json=?,playwright_test_ids_json=? where id=?''',(
  status,
  json.dumps(merge(json.loads(row[0]),*paths),ensure_ascii=False),
  json.dumps(merge(json.loads(row[1]),*tech),ensure_ascii=False),
  json.dumps(merge(json.loads(row[2]),*pw),ensure_ascii=False),rid))

BACKUP.parent.mkdir(parents=True,exist_ok=True)
shutil.copy2(DB,BACKUP)
c=sqlite3.connect(DB,timeout=60)
try:
 update(c,'GA-HOME-001','eighth_stream_registered_bridged_and_visible_validated',paths=(
  '/root/werkraum/_gpt/gesamtatlas/AI_STROEME.json','/root/werkraum/_gpt/gesamtatlas/AI_STROM_BRUECKEN.json',
  '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/AI_STROEME','/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/UI/ai-stroeme.html',
  '/root/werkraum/tools/gesamtatlas_endproduktbeweis/ai_streams/build_ai_streams_ui.py'),
  tech=('GA-HOME-001-CLAUDEWEB-TECH-001',),pw=('GA-HOME-001-CLAUDEWEB-PW-001',))
 capsule_paths=(
  '/root/werkraum/_gpt/gesamtatlas/GESAMTATLAS_KAPSEL_AKTUELL.zip',
  '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/BASE_AKTUELL.zip',
  '/root/werkraum/tools/gesamtatlas_endproduktbeweis/capsule/build_proof_capsule.py',
  '/root/werkraum/tools/gesamtatlas_endproduktbeweis/capsule/install_proof_capsule.py',
  '/etc/systemd/system/gesamtatlas-proof-capsule.service','/etc/systemd/system/gesamtatlas-proof-capsule.path','/etc/systemd/system/gesamtatlas-proof-capsule.timer',
  '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/KANONISCH_ABGENOMMEN')
 capsule_tech=('GA-CAPSULE-002-TECH-001','GA-CAPSULE-INSTALL-TECH-001','GA-CAPSULE-AUTOMATION-TECH-001','GA-CAPSULE-CANONICAL-TECH-001')
 capsule_pw=('GA-CAPSULE-002-PW-001','GA-CAPSULE-CANONICAL-PW-001')
 update(c,'GA-CAPSULE-001','private_canonical_capsule_installed_self_healing_validated',capsule_paths,capsule_tech,capsule_pw)
 update(c,'GA-CAPSULE-002','machine_core_exploration_contract_canonical_installed_validated',capsule_paths,capsule_tech,capsule_pw)
 update(c,'GA-TEST-001','all_current_vps_sections_requirement_bound_and_validated',paths=(
  '/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/EVIDENZ',
  '/root/werkraum/tools/gesamtatlas_endproduktbeweis/tests'),
  tech=('GA-REQUIREMENTS-FINAL-TECH-001','GA-HOME-001-CLAUDEWEB-TECH-001',*capsule_tech),
  pw=('GA-TEST-001-PW-001','GA-HOME-001-CLAUDEWEB-PW-001',*capsule_pw))
 c.commit();c.execute('pragma wal_checkpoint(TRUNCATE)');c.commit();c.row_factory=sqlite3.Row
 rows=[]
 for r in c.execute('select * from requirements order by rowid'):
  d=dict(r);rows.append({'id':d['id'],'title':d['title'],'category':d['category'],'source_class':d['source_class'],'source_path':d['source_path'],'source_lines':{'start':d['source_start'],'end':d['source_end']},'source_excerpt':d['source_excerpt'],'requirement_summary':d['requirement_summary'],'confidence':d['confidence'],'valid_status':d['valid_status'],'current_implementation_status':d['current_implementation_status'],'implementation_paths':json.loads(d['implementation_paths_json']),'technical_test_ids':json.loads(d['technical_test_ids_json']),'playwright_test_ids':json.loads(d['playwright_test_ids_json']),'external_test_required':bool(d['external_test_required']),'integration_requires_daniel':bool(d['integration_requires_daniel']),'truth_notes':d['truth_notes']})
finally:c.close()

def atomic_text(path:Path,text:str):
 path.parent.mkdir(parents=True,exist_ok=True);fd,tmp=tempfile.mkstemp(prefix=f'.{path.name}.',dir=path.parent)
 try:
  with open(fd,'w',encoding='utf-8',closefd=True) as f:f.write(text);f.flush()
  Path(tmp).replace(path)
 except Exception:Path(tmp).unlink(missing_ok=True);raise
atomic_text(JSONL,''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in rows))
headers=['ID','Anforderung','Gültigkeit','Aktueller Stand','Fremdtest','Daniel-Freigabe']
md=['# Anforderungsmatrix','','Jede Zeile bleibt an Originalfundstelle, reale Umsetzung und Beweis-IDs gebunden. Externe Browser-, Fremd-LLM- und menschliche Abnahmen werden nicht durch VPS-Tests ersetzt.','','| '+' | '.join(headers)+' |','|'+'|'.join(['---']*len(headers))+'|']
for r in rows:md.append('| '+' | '.join([r['id'],r['title'].replace('|','/'),r['valid_status'],r['current_implementation_status'],'ja' if r['external_test_required'] else 'nein','ja' if r['integration_requires_daniel'] else 'nein'])+' |')
atomic_text(MATRIX,'\n'.join(md)+'\n')
by={r['id']:r for r in rows};checks=[]
def check(name,v,detail=''):
 checks.append({'name':name,'ok':bool(v),'detail':detail})
 if not v:raise AssertionError(f'{name}: {detail}')
check('21 Anforderungen erhalten',len(rows)==21,str(len(rows)))
check('Claude Web vollständig gebunden',by['GA-HOME-001']['current_implementation_status']=='eighth_stream_registered_bridged_and_visible_validated')
check('Claude-Web-Technikbeweis gebunden','GA-HOME-001-CLAUDEWEB-TECH-001' in by['GA-HOME-001']['technical_test_ids'])
check('Claude-Web-Playwright gebunden','GA-HOME-001-CLAUDEWEB-PW-001' in by['GA-HOME-001']['playwright_test_ids'])
for rid in ('GA-CAPSULE-001','GA-CAPSULE-002'):
 check(f'{rid} kanonisch markiert','canonical' in by[rid]['current_implementation_status'] and 'installed' in by[rid]['current_implementation_status'],by[rid]['current_implementation_status'])
 for tid in ('GA-CAPSULE-INSTALL-TECH-001','GA-CAPSULE-AUTOMATION-TECH-001','GA-CAPSULE-CANONICAL-TECH-001'):
  check(f'{rid} bindet {tid}',tid in by[rid]['technical_test_ids'])
 check(f'{rid} bindet kanonisches Playwright','GA-CAPSULE-CANONICAL-PW-001' in by[rid]['playwright_test_ids'])
check('Testpflicht bindet Acht-Strom-Playwright','GA-HOME-001-CLAUDEWEB-PW-001' in by['GA-TEST-001']['playwright_test_ids'])
check('Testpflicht bindet kanonisches Kapsel-Playwright','GA-CAPSULE-CANONICAL-PW-001' in by['GA-TEST-001']['playwright_test_ids'])
check('JSONL enthält 21 Zeilen',sum(1 for _ in JSONL.open())==21)
check('Matrix enthält alle IDs',all(r['id'] in MATRIX.read_text('utf-8') for r in rows))
check('SQLite-Integrität',sqlite3.connect(DB).execute('pragma integrity_check').fetchone()[0]=='ok')
report={'ok':all(x['ok'] for x in checks),'test_id':'GA-REQUIREMENTS-FINAL-TECH-001','generated_utc':datetime.now(timezone.utc).isoformat(),'check_count':len(checks),'checks':checks,'requirement_count':len(rows),'paths':{'sqlite':str(DB),'jsonl':str(JSONL),'matrix':str(MATRIX),'backup':str(BACKUP)},'hashes':{'sqlite':sha(DB),'jsonl':sha(JSONL),'matrix':sha(MATRIX),'backup':sha(BACKUP)},'truth_boundary':'Bindet den abschließenden VPS-Stand. Browser-Extension-, Fremd-LLM- und Daniels menschliche Abnahme bleiben als externe Schritte sichtbar.'}
atomic_text(REPORT,json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
print(json.dumps({'ok':report['ok'],'test_id':report['test_id'],'check_count':report['check_count'],'requirement_count':len(rows)},ensure_ascii=False))
