from __future__ import annotations
import datetime as dt
import hashlib
import json
import sqlite3
from pathlib import Path

ROOT=Path('/root/werkraum/_gpt/gesamtatlas/ursprungsring')
OUT=ROOT/'evidenz/TECHNICAL_VALIDATION.json'
EXPECTED_STREAMS={'claude','claudeweb','chatgpt','codex','gemini','kimi','glm'}

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p:Path):return json.loads(p.read_text('utf-8'))
checks=[]
def check(name,ok,detail=None):
 checks.append({'name':name,'ok':bool(ok),'detail':detail})
 if not ok: raise AssertionError(f'{name}: {detail}')

b=ROOT/'originalzeugen/VOR_VPS_PRIMAERZEUGE_B_EXAKT.txt'
a=ROOT/'originalzeugen/ZEUGE_A_ERGAENZUNG_ORIGINALZEILEN_388_636.txt'
manifest=load(ROOT/'MANIFEST.json'); witnesses=load(ROOT/'ZEUGENREGISTER.json'); truths=load(ROOT/'URSPRUNGSWAHRHEITEN.json'); drift=load(ROOT/'DRIFTVERGLEICH.json')
check('Primärzeuge vorhanden',b.is_file(),str(b));check('Primärzeuge Bytes',b.stat().st_size==75196,b.stat().st_size);check('Primärzeuge Hash',sha(b)=='e6301a898639b4568d13c5214387a3f945107d8c9159221462960312723a5e10',sha(b));check('Primärzeuge 2536 Zeilen',len(b.read_text('utf-8').splitlines())==2536,len(b.read_text('utf-8').splitlines()))
check('Zeuge-A-Ergänzung vorhanden',a.is_file(),str(a));check('Zeuge-A Bytes',a.stat().st_size==7042,a.stat().st_size);check('Zeuge-A Hash',sha(a)=='b3068bd89dda56d03aaed196e2a440c149c80fc7caa7a72ade758814f4f6dd83',sha(a))
check('Vor-VPS-Verbot sichtbar','keine VPS-Suche' in b.read_text('utf-8') and 'keine Datei- oder Datenbanklesung' in b.read_text('utf-8'))
check('Vor-VPS-Endgrenze sichtbar','NOCH NICHT AUSGEFÜHRT' in b.read_text('utf-8') and b.read_text('utf-8').splitlines()[-1]=='1m 59s nachgedacht')
check('Originalschutz in Zeuge A','niemals anstelle der Originale' in a.read_text('utf-8'))
check('Original-Ableitung-Reaktion in Zeuge A',all(x in a.read_text('utf-8') for x in ('ORIGINAL:','ABLEITUNG:','REAKTION:')))
check('Manifest gebaut',manifest['status']=='BUILT',manifest['status']);check('Manifest 846 Segmente',manifest['segment_count']==846,manifest['segment_count']);check('Manifest 12 Wahrheiten',manifest['truth_count']==12,manifest['truth_count']);check('Manifest 8 Driftbefunde',manifest['drift_count']==8,manifest['drift_count']);check('Manifest sieben Ströme',set(manifest['stream_paths'])==EXPECTED_STREAMS,manifest['stream_paths'])
check('Zwei Zeugen registriert',len(witnesses['witnesses'])==2,len(witnesses['witnesses']));check('Vollhash Zeuge A registriert',witnesses['witnesses'][0]['sha256']=='74ab42c0752dcab452b3593f6b44b5b24c83ddc67b41d5adb1f7bf48a5d540b1');check('Vollhash Zeuge B registriert',witnesses['witnesses'][1]['sha256']=='4a9f57921cf1174f970ddeba85dc152c3a2f17997ec4cb67e089b60b9c051cf3')
segments=[json.loads(x) for x in (ROOT/'SEGMENTREGISTER.jsonl').read_text('utf-8').splitlines() if x.strip()]
check('JSONL 846 Segmente',len(segments)==846,len(segments));check('Segment-IDs eindeutig',len({x['segment_id'] for x in segments})==len(segments));check('Alle Segmenthashes korrekt',all(hashlib.sha256(x['text'].encode()).hexdigest()==x['text_sha256'] for x in segments));check('Alle Segmente quellengebunden',all(x['source_id'] and x['source_lines']['start']<=x['source_lines']['end'] for x in segments));check('Zwei direkte Daniel-Nachrichten',sum(x['kind']=='DANIEL_NACHRICHT' for x in segments)==2);check('Vier belegte Nutzerlücken',sum(x['kind']=='LUECKE_BELEGT' for x in segments)==4);check('Bekannte Lückenzeilen',sorted(x['source_lines']['start'] for x in segments if x['kind']=='LUECKE_BELEGT')==[543,784,863,2002]);check('Ein Exportduplikat',sum(x['kind']=='DUPLIKAT_IM_EXPORT' for x in segments)==1);check('Duplikatzeile 41',next(x for x in segments if x['kind']=='DUPLIKAT_IM_EXPORT')['source_lines']['start']==41)
con=sqlite3.connect(ROOT/'REKONSTRUKTIONSREGISTER.sqlite');check('SQLite integer',con.execute('pragma integrity_check').fetchone()[0]=='ok');check('SQLite Segmentzahl',con.execute('select count(*) from segments').fetchone()[0]==846);check('SQLite Lückenzahl',con.execute("select count(*) from segments where kind='LUECKE_BELEGT'").fetchone()[0]==4);con.close()
check('Zwölf Ursprungswahrheiten',len(truths['truths'])==12);check('Wahrheits-IDs eindeutig',len({x['id'] for x in truths['truths']})==12);check('Jede Wahrheit mit Quelle',all(x['source_ref'] and x['evidence_class'] for x in truths['truths']));check('Acht Driftbefunde',len(drift['comparisons'])==8);check('Driftstatus enthält Spannung',any(x['status']=='OPEN_TENSION' for x in drift['comparisons']));check('Zensi-Korrektur dokumentiert',any('Zensi' in x['current_finding'] for x in drift['comparisons']))
for stream in EXPECTED_STREAMS:
 folder=ROOT/'ai-stroeme'/stream;check(f'{stream}: Startpfad', (folder/'START_HIER.md').is_file());check(f'{stream}: Lesung offen', 'NOCH_NICHT_DURCHGEFUEHRT' in (folder/'LESUNG.md').read_text('utf-8'))
index=(ROOT/'ui/index.html').read_text('utf-8');check('UI vorhanden',bool(index));check('UI Einladung vor Regeln','Einladung' in (ROOT/'START_HIER.md').read_text('utf-8'));check('UI 12 Wahrheitskarten',index.count('class="truth"')==12,index.count('class="truth"'));check('UI 7 Stromkarten',index.count('class="stream"')==7,index.count('class="stream"'));check('UI drei Ebenen',all(f'<h2>{x}</h2>' in index for x in ('Original','Ableitung','Reaktion')));check('Quellansicht B', (ROOT/'ui/source-b.html').is_file() and 'id="L2535"' in (ROOT/'ui/source-b.html').read_text('utf-8'));check('Quellansicht A', (ROOT/'ui/source-a.html').is_file() and 'niemals anstelle der Originale' in (ROOT/'ui/source-a.html').read_text('utf-8'))
result={'schema_version':'1.0','ok':all(x['ok'] for x in checks),'generated_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'check_count':len(checks),'checks':checks,'manifest_sha256':sha(ROOT/'MANIFEST.json'),'truth_boundary':'Technische Validierung beweist Quellenhashes, Register, Lückenmarkierung, getrennte Lesepfade und UI-Körper; sie behauptet keine bereits erfolgten sieben AI-Lesungen.'}
OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n','utf-8')
print(json.dumps({'ok':result['ok'],'check_count':len(checks),'path':str(OUT),'sha256':sha(OUT)},ensure_ascii=False,indent=2))
