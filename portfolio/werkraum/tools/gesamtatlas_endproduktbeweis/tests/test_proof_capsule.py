#!/usr/bin/env python3
from __future__ import annotations
import gzip, hashlib, json, re, sqlite3, stat, tempfile, zipfile
from pathlib import Path, PurePosixPath

ZIP=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/GESAMTATLAS_KAPSEL_MIT_ENDPRODUKTBEWEIS.zip')
CURRENT=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/AKTUELL')
STATUS=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/STATUS.json')
CANONICAL=Path('/root/werkraum/_gpt/gesamtatlas/GESAMTATLAS_KAPSEL_AKTUELL.zip')
BASE=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/BASE_AKTUELL.zip')
REPORT=Path('/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/EVIDENZ/GA-CAPSULE-002-TECHNICAL.json')
EXPECTED_SOURCE='643ba35ac435cf96ba71978f6594b9208e71e033953ef4dda06f0b320abb12c2'
EXPECTED_BASE=hashlib.sha256(BASE.read_bytes()).hexdigest() if BASE.exists() else ''
checks=[]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def manifest(path):
    with zipfile.ZipFile(path) as archive:
        name='ENDPRODUKTBEWEIS/MANIFEST.json'
        return json.loads(archive.read(name)) if name in archive.namelist() else None
def check(name,value,detail=''):
 checks.append({'name':name,'ok':bool(value),'detail':detail})
 if not value:raise AssertionError(f'{name}: {detail}')
def safe(name):
 p=PurePosixPath(name.replace('\\','/'))
 return bool(p.parts) and not p.is_absolute() and '..' not in p.parts

check('Kandidaten-ZIP existiert',ZIP.exists())
check('Kandidaten-ZIP nicht kanonischer Pfad',ZIP.resolve()!=CANONICAL.resolve())
status=json.loads(STATUS.read_text('utf-8'))
check('Status grün',status['ok'] is True)
check('Kandidatenstatus bleibt als Vorinstallationskörper markiert',status['canonical_installed'] is False)
check('ZIP unter 25 MB',0<ZIP.stat().st_size<=25_000_000,str(ZIP.stat().st_size))
check('Statusgröße stimmt',status['candidate_zip_bytes']==ZIP.stat().st_size)
check('Statushash stimmt',status['candidate_zip_sha256']==sha(ZIP))
check('Ausgangskapsel-Hash gebunden',status['base_capsule_sha256']==EXPECTED_BASE,status['base_capsule_sha256'])
check('Separat gespeicherte Basis unverändert',BASE.exists() and sha(BASE)==EXPECTED_BASE,sha(BASE) if BASE.exists() else 'missing')
check('Kanonischer WinSCP-Pfad trägt Beweiskapsel',manifest(CANONICAL) is not None)
check('Kanonischer WinSCP-Pfad entspricht Kandidat',sha(CANONICAL)==sha(ZIP),f'{sha(CANONICAL)} != {sha(ZIP)}')
check('Browser-Realabnahme offen',status['browser_real_acceptance']=='OPEN_BLOCKED_EXTERNAL')
check('Keine Fremdantworten behauptet',status['external_response_count']==0)
check('Geheimnisscan ohne Hochkonfidenzfund',status['privacy_high_confidence_findings']==0)
with zipfile.ZipFile(ZIP) as z:
 check('ZIP-Integrität',z.testzip() is None)
 infos=z.infolist();names={i.filename for i in infos}
 check('Mindestens Ausgangs- und Beweiskörper',len(infos)>=70,str(len(infos)))
 check('Alle ZIP-Pfade sicher',all(safe(i.filename) for i in infos))
 check('Keine Symlinks',all(((i.external_attr>>16)&0o170000)!=stat.S_IFLNK for i in infos))
 required={
  '00_START_HIER.md','01_ENDPRODUKTBEWEIS_START.md','OFFLINE/index.html','MASCHINE/KAPSEL.sqlite',
  'ENDPRODUKTBEWEIS/00_START_HIER.md','ENDPRODUKTBEWEIS/MANIFEST.json','ENDPRODUKTBEWEIS/SHA256SUMS.txt',
  'ENDPRODUKTBEWEIS/ANFORDERUNGEN/ANFORDERUNGSMATRIX.md','ENDPRODUKTBEWEIS/ANFORDERUNGEN/ANFORDERUNGSREGISTER.jsonl',
  'ENDPRODUKTBEWEIS/MASCHINE/ANFORDERUNGSREGISTER.sqlite','ENDPRODUKTBEWEIS/MASCHINE/WIRKUNGSSTUFEN.sqlite',
  'ENDPRODUKTBEWEIS/INTEGRATION/LLM_ABNAHME_AUFGABEN.json','ENDPRODUKTBEWEIS/INTEGRATION/RAW_RESPONSE_SCHEMA.json',
  'ENDPRODUKTBEWEIS/QUELLEN/NACHGEREICHTER_SICHTBARER_VERLAUF.txt.gz','ENDPRODUKTBEWEIS/QUELLEN/LUECKEN_UND_DUPLIKATE.json',
  'ENDPRODUKTBEWEIS/WIRKUNG/BEISPIEL_ORIGINALVERLAUF.json','ENDPRODUKTBEWEIS/TERMINALWIRKUNG/BEISPIEL_PLAYWRIGHT_KORREKTUR.json',
  'ENDPRODUKTBEWEIS/ZEITREISE/BEISPIEL_MOMENT_203015.json','ENDPRODUKTBEWEIS/UI/index.html','ENDPRODUKTBEWEIS/UI/wirkung.html',
  'ENDPRODUKTBEWEIS/UI/terminalwirkung.html','ENDPRODUKTBEWEIS/UI/zeitreise.html','ENDPRODUKTBEWEIS/UI/ai-stroeme.html',
  'ENDPRODUKTBEWEIS/AI_STROEME/STATUS.json','ENDPRODUKTBEWEIS/AI_STROEME/AI_STROEME.json',
  'ENDPRODUKTBEWEIS/AI_STROEME/AI_STROM_BRUECKEN.json','ENDPRODUKTBEWEIS/MASCHINE/build_ai_streams_ui.py',
  'ENDPRODUKTBEWEIS/EVIDENZ/GA-TIME-011-PLAYWRIGHT.json','ENDPRODUKTBEWEIS/EVIDENZ/GA-HOME-001-CLAUDEWEB-PLAYWRIGHT.json',
  'ENDPRODUKTBEWEIS/UI/groessenwahrheit.html','ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/STATUS.json',
  'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/GROESSENWAHRHEIT.json','ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/EINGANG_START_HIER.md',
  'ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/EINGANG_MANIFEST.json','ENDPRODUKTBEWEIS/MASCHINE/build_size_truth_ui.py',
  'ENDPRODUKTBEWEIS/ERGAENZUNGEN/GROESSENWAHRHEIT_ZENSI_EINGANG_SCHLANKHEIT.json',
  'ENDPRODUKTBEWEIS/SCHLANKHEIT/SCHLANKHEITSAUDIT.json','ENDPRODUKTBEWEIS/VERTRAEGE/gesamtatlas_v1.json',
  'ENDPRODUKTBEWEIS/EVIDENZ/GA-SIZE-TRUTH-INTAKE-TECHNICAL.json','ENDPRODUKTBEWEIS/EVIDENZ/GA-SIZE-TRUTH-INTAKE-PLAYWRIGHT.json'
 }
 check('Alle Pflichtkörper enthalten',required<=names,str(sorted(required-names)))
 check('Keine Screenshots oder Traces eingebettet',not any(n.lower().endswith(('.png','.jpg','.jpeg','trace.zip')) for n in names))
 check('Keine großen Arbeitsdatenbanken eingebettet','ENDPRODUKTBEWEIS/TERMINALWIRKUNG/WIRKUNGSKETTEN.sqlite' not in names and 'ENDPRODUKTBEWEIS/ZEITREISE/EPISTEMISCHE_MOMENTE.sqlite' not in names)
 manifest=json.loads(z.read('ENDPRODUKTBEWEIS/MANIFEST.json'))
 check('Manifest privat',manifest['public_delivery'] is False)
 check('Manifest Kandidat, nicht kanonisch',manifest['candidate_only'] is True and manifest['canonical_installation'] is False)
 check('Manifest hat 21 Anforderungen',manifest['requirement_count']==21)
 check('Manifest hat zehn Clean-Room-Aufgaben',manifest['clean_room_task_count']==10)
 check('Manifest hat null Fremdantworten',manifest['external_response_count']==0)
 check('Manifest hält Browser rot',manifest['browser_real_acceptance']=='OPEN_BLOCKED_EXTERNAL')
 check('Manifest nennt vollständige Tiefendatenbanken nur als Referenz',len(manifest['reference_only_large_databases'])==2)
 sums=z.read('ENDPRODUKTBEWEIS/SHA256SUMS.txt').decode('utf-8').splitlines()
 sum_map={line.split('  ',1)[1]:line.split('  ',1)[0] for line in sums if '  ' in line}
 check('Prüfsummenliste umfangreich',len(sum_map)>=35,str(len(sum_map)))
 mismatches=[]
 for rel,expected in sum_map.items():
  actual=hashlib.sha256(z.read(rel)).hexdigest()
  if actual!=expected:mismatches.append((rel,expected,actual))
 check('Alle Zusatzhashes stimmen',not mismatches,str(mismatches[:3]))
 raw=gzip.decompress(z.read('ENDPRODUKTBEWEIS/QUELLEN/NACHGEREICHTER_SICHTBARER_VERLAUF.txt.gz'))
 check('Originalverlauf dekomprimiert hashgleich',hashlib.sha256(raw).hexdigest()==EXPECTED_SOURCE,hashlib.sha256(raw).hexdigest())
 issues=json.loads(z.read('ENDPRODUKTBEWEIS/QUELLEN/LUECKEN_UND_DUPLIKATE.json'))['issues']
 check('Sieben Integritätsbefunde enthalten',len(issues)==7,str(len(issues)))
 tasks=json.loads(z.read('ENDPRODUKTBEWEIS/INTEGRATION/LLM_ABNAHME_AUFGABEN.json'))
 check('Zehn identische Fremdaufgaben',len(tasks['tasks'])==10)
 check('Aufgaben verbieten erfundenen VPS-Zugriff',any('keinen Zugriff auf den VPS' in x for x in tasks['instructions']))
 integration=json.loads(z.read('ENDPRODUKTBEWEIS/INTEGRATION/STATUS.json'))
 check('Integrationsstatus ohne Antworten',integration['raw_response_count']==0 and integration['canonical_count']==0)
 browser=json.loads(z.read('ENDPRODUKTBEWEIS/ABHAENGIGKEITEN/BROWSER_EXTENSION_REALABNAHME_OFFEN.json'))
 check('Browserstatus blockiert realen Test',browser['status']=='blocked_by_external_real_test')
 req_ui=z.read('ENDPRODUKTBEWEIS/UI/index.html').decode('utf-8')
 check('Kapsel-UI nutzt lokale Anforderungs-SQLite','../MASCHINE/ANFORDERUNGSREGISTER.sqlite' in req_ui and '../ANFORDERUNGEN/ANFORDERUNGSREGISTER.sqlite' not in req_ui)
 effect_ui=z.read('ENDPRODUKTBEWEIS/UI/wirkung.html').decode('utf-8')
 check('Kapsel-UI nutzt lokale Wirkungs-SQLite','../MASCHINE/WIRKUNGSSTUFEN.sqlite' in effect_ui and '../WIRKUNG/WIRKUNGSSTUFEN.sqlite' not in effect_ui)
 terminal_ui=z.read('ENDPRODUKTBEWEIS/UI/terminalwirkung.html').decode('utf-8')
 time_ui=z.read('ENDPRODUKTBEWEIS/UI/zeitreise.html').decode('utf-8')
 check('Große Terminal-DB nicht tot verlinkt','WIRKUNGSKETTEN.sqlite' not in terminal_ui and 'vollständige SQLite bleibt auf dem VPS' in terminal_ui)
 check('Große Zeitreise-DB nicht tot verlinkt','EPISTEMISCHE_MOMENTE.sqlite' not in time_ui and 'vollständige SQLite bleibt auf dem VPS' in time_ui)
 ai_ui=z.read('ENDPRODUKTBEWEIS/UI/ai-stroeme.html').decode('utf-8')
 ai_status=json.loads(z.read('ENDPRODUKTBEWEIS/AI_STROEME/STATUS.json'))
 ai_streams=json.loads(z.read('ENDPRODUKTBEWEIS/AI_STROEME/AI_STROEME.json'))
 ai_bridges=json.loads(z.read('ENDPRODUKTBEWEIS/AI_STROEME/AI_STROM_BRUECKEN.json'))['streams']
 check('Acht-Strom-Seite in Kapsel lesbar','Acht Zuhause' in ai_ui and 'claudeweb' in ai_ui)
 check('Acht-Strom-Status grün',ai_status['ok'] is True and ai_status['stream_count']==8 and ai_status['bridge_count']==8)
 check('Acht maschinelle Ströme enthalten',len(ai_streams)==8 and [x['id'] for x in ai_streams]==['chatgpt','claudeweb','claude','codex','kimi','gemini','glm','grok'])
 check('Acht maschinelle Brücken enthalten',set(ai_bridges)=={x['id'] for x in ai_streams})
 cw=next(x for x in ai_streams if x['id']=='claudeweb')
 check('Claude Web hat getrennte Identitätsgrenze','nicht Claude Code und nicht ChatGPT' in cw['identity_boundary'])
 size_ui=z.read('ENDPRODUKTBEWEIS/UI/groessenwahrheit.html').decode('utf-8')
 size_status=json.loads(z.read('ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/STATUS.json'))
 size_data=json.loads(z.read('ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/GROESSENWAHRHEIT.json'))
 intake_manifest=json.loads(z.read('ENDPRODUKTBEWEIS/GROESSENWAHRHEIT/EINGANG_MANIFEST.json'))
 addendum=json.loads(z.read('ENDPRODUKTBEWEIS/ERGAENZUNGEN/GROESSENWAHRHEIT_ZENSI_EINGANG_SCHLANKHEIT.json'))
 slim=json.loads(z.read('ENDPRODUKTBEWEIS/SCHLANKHEIT/SCHLANKHEITSAUDIT.json'))
 contract=json.loads(z.read('ENDPRODUKTBEWEIS/VERTRAEGE/gesamtatlas_v1.json'))
 check('Größenwahrheit sichtbar enthalten','Nicht 54 GB Atlas' in size_ui and '/root/werkraum_gesamtatlas_eingang' in size_ui)
 check('Größenstatus grün',size_status['ok'] is True and size_status['technical_checks']==33)
 check('Quelllandschaft größer als Atlas',size_data['source_landscape_logical_bytes']>size_data['atlas_workspace_logical_bytes_excluding_self_reports']>size_data['portable_capsule_bytes'])
 check('Eingangsmanifest als Primärquelle',intake_manifest['kind']=='curated_manual_intake' and intake_manifest['source_status']=='primary_source_kept_in_place')
 check('Vier Nachversiegelungs-IDs',addendum['base_requirement_count']==21 and addendum['addendum_count']==4)
 check('Schlankheitsaudit nicht destruktiv',slim['ok'] is True and 'Keine Datei wurde gelöscht' in slim['truth_boundary'])
 check('Gesamtatlas-Vertrag Version 3',contract['protocol_version']==3 and contract['canonical_files']['manual_intake']=='/root/werkraum_gesamtatlas_eingang/START_HIER.md')
 check('Keine Kapsel-Selbstabnahmen eingebettet',not any(n.startswith('ENDPRODUKTBEWEIS/EVIDENZ/GA-CAPSULE') for n in names))
 high_patterns=[re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),re.compile(r'\bsk-[A-Za-z0-9_-]{20,}\b'),re.compile(r'(?i)authorization\s*[:=]\s*bearer\s+[A-Za-z0-9._~+\-/=]{16,}')]
 findings=[]
 for n in names:
  if not n.startswith('ENDPRODUKTBEWEIS/') or not n.lower().endswith(('.md','.txt','.json','.jsonl','.py','.html','.js','.sql')):continue
  data=z.read(n)
  if len(data)>5_000_000:continue
  text=data.decode('utf-8',errors='replace')
  for p in high_patterns:
   if p.search(text):findings.append((n,p.pattern))
 check('Zusatzkörper ohne Hochkonfidenzgeheimnisse',not findings,str(findings))
# Extracted copy parity and SQLite checks.
check('Extrahierter Kandidat vorhanden',CURRENT.exists())
check('Extrahierter Start vorhanden',(CURRENT/'ENDPRODUKTBEWEIS/UI/index.html').exists())
for rel,table,count in [
 ('ENDPRODUKTBEWEIS/MASCHINE/ANFORDERUNGSREGISTER.sqlite','requirements',21),
 ('ENDPRODUKTBEWEIS/MASCHINE/WIRKUNGSSTUFEN.sqlite','stage_assessments',6),
]:
 db=CURRENT/rel;conn=sqlite3.connect(db)
 check(f'{rel} SQLite integer',conn.execute('pragma integrity_check').fetchone()[0]=='ok')
 check(f'{rel} erwartete Zeilen',conn.execute(f'select count(*) from {table}').fetchone()[0]==count)
 conn.close()
report={'ok':all(c['ok'] for c in checks),'test_id':'GA-CAPSULE-002-TECH-001','check_count':len(checks),'checks':checks,'candidate_zip':str(ZIP),'candidate_zip_bytes':ZIP.stat().st_size,'candidate_zip_sha256':sha(ZIP),'canonical_zip_sha256':sha(CANONICAL),'base_zip_sha256':sha(BASE),'truth_boundary':'Beweist Kandidateninhalt, Basisbindung und Bytegleichheit mit der aktuell privat installierten kanonischen WinSCP-Kapsel. Browser-, Fremd-LLM- und menschliche Abnahmen bleiben offen.'}
REPORT.parent.mkdir(parents=True,exist_ok=True);REPORT.write_text(json.dumps(report,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
