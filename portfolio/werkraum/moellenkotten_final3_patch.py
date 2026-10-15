from pathlib import Path
import json, re

ROOT=Path('/root/werkraum/gemgems-spielbeobachtung/2026-09-04_MOELLENKOTTEN_FORSCHUNG')
SESSIONS=[
('S01','01_STRASSEN_UND_GEWEGE','Straßen und Gehwege'),
('S02','02_FASSADEN_FENSTER_TUEREN','Fassaden, Fenster und Türen'),
('S03','03_GESCHICHTE_UNTERGRUND_SPUREN','Geschichte und Untergrundspuren'),
('S04','04_HOEHEN_BOESCHUNGEN_TREPPEN','Höhen, Böschungen und Treppen'),
('S05','05_GEBAEUDEKOERPER_DAECHER','Gebäudekörper und Dächer'),
('S06','06_VEGETATION_GRUEN','Vegetation und Grün'),
('S07','07_TRAMPELPFADE_DURCHGAENGE','Trampelpfade und Durchgänge'),
('S08','08_STRASSENMOBILIAR_GRENZOBJEKTE','Straßenmobiliar und Grenzobjekte'),
('S09','09_SONDERORTE_OEFFENTLICHE_INNENRAEUME','Sonderorte und Innenräume'),
('S10','10_HISTORISCHE_KARTEN_LUFTBILDER','Historische Karten und Luftbilder'),
('S11','11_BILDQUELLEN_PERSPEKTIVEN','Bildquellen und Perspektiven'),
('S12','12_WIDERSPRUCH_LUECKEN_FACHSESSION','Widerspruch und Lücken'),
]

def write(rel,text):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text.rstrip()+'\n',encoding='utf-8')

# One canonical mapping between actor codes and real folders.
mapping={'schema_version':3,'sessions':[{'code':c,'folder':f,'title':t} for c,f,t in SESSIONS],'special_actors':['GRAVITY','REDTEAM01','REDTEAM02','STEUERUNG']}
write('maschinenvertrag/SESSIONEN.json',json.dumps(mapping,ensure_ascii=False,indent=2))

# Upgrade schema to v3 while live JSONL are still empty.
p=ROOT/'maschinenvertrag/DATENSCHEMA.json'; s=json.loads(p.read_text(encoding='utf-8')); s['schema_version']=3
for name,d in s['$defs'].items():
    if isinstance(d,dict) and 'properties' in d and 'schema_version' in d['properties']:
        d['properties']['schema_version']={'const':3}

pos={'type':'array','prefixItems':[{'type':'number','minimum':-180,'maximum':180},{'type':'number','minimum':-90,'maximum':90}],'items':False,'minItems':2,'maxItems':2}
point={'type':'object','properties':{'geometry_type':{'const':'POINT'},'crs':{'const':'EPSG:4326'},'coordinates':pos,'accuracy_m':{'type':['number','null'],'minimum':0},'location_method':{'type':'string','minLength':1}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False}
line={'type':'object','properties':{'geometry_type':{'const':'LINESTRING'},'crs':{'const':'EPSG:4326'},'coordinates':{'type':'array','items':pos,'minItems':2},'accuracy_m':{'type':['number','null'],'minimum':0},'location_method':{'type':'string','minLength':1}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False}
poly={'type':'object','properties':{'geometry_type':{'const':'POLYGON'},'crs':{'const':'EPSG:4326'},'coordinates':{'type':'array','items':{'type':'array','items':pos,'minItems':4},'minItems':1},'accuracy_m':{'type':['number','null'],'minimum':0},'location_method':{'type':'string','minLength':1}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False}
none={'type':'object','properties':{'geometry_type':{'const':'NONE'},'crs':{'type':'null'},'coordinates':{'type':'null'},'accuracy_m':{'type':'null'},'location_method':{'type':['string','null']}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False}
s['$defs']['point_geometry']=point
s['$defs']['geometry']={'oneOf':[point,line,poly,none]}
s['$defs']['control_point']={'type':'object','properties':{'geometry':{'$ref':'#/$defs/point_geometry'},'source_id':s['$defs']['control_point']['properties']['source_id'],'description':{'type':'string','minLength':1}},'required':['geometry','source_id','description'],'additionalProperties':False}

folders='|'.join(re.escape(f) for _,f,_ in SESSIONS)
segment=r'[A-Za-z0-9][A-Za-z0-9._-]*'
snapshot_pattern=rf'^(?:sessions/(?:{folders})/snapshots|zustand/quellen_snapshots)/{segment}(?:/{segment})*$'
sp=s['$defs']['source_event']['properties']['snapshot_path']; sp['pattern']=snapshot_pattern

# Canonical merge events must identify a real local merge origin.
for kind in ['source_event','finding_event','route_event']:
    d=s['$defs'][kind]; d.setdefault('allOf',[]).append({'if':{'properties':{'merge_status':{'const':'KANONISCH'}}},'then':{'properties':{'origin_event_ids':{'type':'array','items':d['properties']['origin_event_ids']['items'],'minItems':1,'uniqueItems':True}}}})
s['$defs']['source_event']['allOf'].append({'if':{'properties':{'merge_status':{'const':'KANONISCH'}}},'then':{'properties':{'alias_source_ids':{'type':'array','items':s['$defs']['source_event']['properties']['alias_source_ids']['items'],'minItems':1,'uniqueItems':True}}}})

# Calibration becomes a real machine contract.
dt={'type':'string','format':'date-time','pattern':r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$'}
source_id=s['$defs']['source_event']['properties']['source_id']
cal_props={
 'schema_version':{'const':3},'version':{'type':'integer','minimum':1},'status':{'enum':['NICHT_KALIBRIERT','KALIBRIERT']},'source_crs':{'const':'EPSG:4326'},'anchor_label':{'type':'string','minLength':1},'origin_coordinates':{'oneOf':[pos,{'type':'null'}]},'origin_elevation_m':{'type':['number','null']},'transformation_method':{'type':['string','null']},'calibrated_at':{'anyOf':[dt,{'type':'null'}]},'source_ids':{'type':'array','items':source_id,'uniqueItems':True},'godot_axes':{'type':'object','properties':{'x':{'type':'string'},'y':{'type':'string'},'z':{'type':'string'}},'required':['x','y','z'],'additionalProperties':False},'notes':{'type':['string','null']}
}
s['$defs']['calibration']={'type':'object','properties':cal_props,'required':list(cal_props),'additionalProperties':False,'allOf':[
 {'if':{'properties':{'status':{'const':'NICHT_KALIBRIERT'}}},'then':{'properties':{'origin_coordinates':{'type':'null'},'origin_elevation_m':{'type':'null'},'transformation_method':{'type':'null'},'calibrated_at':{'type':'null'},'source_ids':{'type':'array','maxItems':0}}}},
 {'if':{'properties':{'status':{'const':'KALIBRIERT'}}},'then':{'properties':{'origin_coordinates':pos,'origin_elevation_m':{'type':'number'},'transformation_method':{'type':'string','minLength':1},'calibrated_at':dt,'source_ids':{'type':'array','items':source_id,'minItems':1,'uniqueItems':True}}}}
]}
write('maschinenvertrag/DATENSCHEMA.json',json.dumps(s,ensure_ascii=False,indent=2))

# Upgrade uncalibrated state to schema v3.
cp=ROOT/'zustand/raumkalibrierung.json'; cal=json.loads(cp.read_text(encoding='utf-8')); cal.update({'schema_version':3,'calibrated_at':None,'source_ids':[]}); write('zustand/raumkalibrierung.json',json.dumps(cal,ensure_ascii=False,indent=2))

# Self-contained provenance note: auditor no longer depends on sibling directories.
write('provenienz/HISTORISCHER_8X_AUDIT_EINORDNUNG.md','''# Einordnung des historischen Achtfach-Audits

Die frühere Formulierung „608 Einzelprüfungen“ war zu stark. Belegt sind 608 Datei-Pass-Durchläufe eines deterministischen Transformationsskripts, nicht 608 unabhängige semantische Einzelprüfungen. Diese Einordnung liegt absichtlich im aktuellen Forschungsordner, damit ein ausgeliefertes Paket für seine eigene Prüfung keinen externen Geschwisterordner benötigt.
''')

# Operational STEUERUNG body.
write('steuerung/00_STEUERUNG.md','''# STEUERUNG — PERSISTENZ VON DANIELS GOAL-ENTSCHEIDUNGEN

## /goal
`STEUERUNG` ist kein autonomer Entscheider und keine weitere Forschungsfigur. Es ist die schmale technische Rolle, die eine bereits ausdrücklich von Daniel getroffene Goal-Entscheidung unverändert in `../zustand/freigaben.jsonl` persistiert.

## Ablauf
1. Daniel spricht eine konkrete Entscheidung für eine Session und ein Goal aus.
2. Der aufrufende Harness oder die aktuelle ChatGPT-Steuerung übergibt genau diese Entscheidung an `../werkzeuge/freigabe_schreiben.py`.
3. Das Werkzeug validiert Session, Goal, Entscheidung und Zeitfelder gegen Schema-Version 3.
4. Erst nach erfolgreichem append-only Schreiben gilt die Entscheidung im Forschungsbetrieb als persistent registriert.

`STEUERUNG` erfindet keine Freigabe, interpretiert kein Schweigen als Zustimmung und nimmt keine fachliche Prüfung vor.
''')

# Update writer contract / snapshot namespace / schema version prose.
ops=ROOT/'gemeinsam/09_BETRIEBSVERTRAG.md'; t=ops.read_text(encoding='utf-8')
t=t.replace('Alle neuen Ereignisse tragen `schema_version = 2`.', 'Alle neuen Ereignisse tragen `schema_version = 3`.')
t=t.replace('Da beim Übergang auf Version 2 alle Forschungs-JSONL leer waren', 'Da beim Übergang auf Version 3 alle Forschungs-JSONL weiterhin leer waren')
t=t.replace('Lokale Sessions speichern gesicherte Quellenkopien ausschließlich unter `sessions/<Session>/snapshots/`.', 'Lokale Sessions speichern gesicherte Quellenkopien ausschließlich unter ihrem echten Sessionordner `sessions/<voller Sessionordner>/snapshots/`. Die Zuordnung von `S01` bis `S12` zu diesen Ordnern steht kanonisch in `../maschinenvertrag/SESSIONEN.json`.')
t=t.replace('Wenn `snapshot_sha256` gesetzt ist, müssen Datei und Hash zusammenpassen.', 'Wenn `snapshot_sha256` gesetzt ist, müssen Datei und Hash zusammenpassen. Nach Pfadauflösung muss der Snapshot weiterhin innerhalb genau der für diese Quelle erlaubten Snapshotwurzel liegen; `../..` darf diese Wurzel nicht verlassen.')
write('gemeinsam/09_BETRIEBSVERTRAG.md',t)

# Tighten space/time/CRS prose.
rt=ROOT/'gemeinsam/10_RAUM_ZEIT_UND_GODOT.md'; t=rt.read_text(encoding='utf-8')
t=t.replace('Geografische Ausgangsdaten werden, soweit möglich, in `EPSG:4326` gespeichert.', 'Geografische Ausgangsdaten des Forschungsbestands werden in Schema-Version 3 ausschließlich in `EPSG:4326` gespeichert. Projizierte Koordinaten werden erst außerhalb dieses Quellschemas abgeleitet, damit Koordinatenbereich und CRS-Beschriftung nicht auseinanderlaufen.')
t=t.replace('Die verbindliche Kalibrierung steht in `../zustand/raumkalibrierung.json`.', 'Die verbindliche Kalibrierung steht in `../zustand/raumkalibrierung.json` und wird gegen `$defs.calibration` aus `../maschinenvertrag/DATENSCHEMA.json` validiert.')
write('gemeinsam/10_RAUM_ZEIT_UND_GODOT.md',t)

# Freigabe prose links to operational body.
g=ROOT/'gemeinsam/08_MANUELLE_GOAL_FREIGABE.md'; t=g.read_text(encoding='utf-8')
t=t.replace('`STEUERUNG` ist der einzige Writer von `../zustand/freigaben.jsonl`.', '`STEUERUNG` ist der einzige Writer von `../zustand/freigaben.jsonl`. Die praktische Rolle und der Aufrufweg stehen in `../steuerung/00_STEUERUNG.md` und `../werkzeuge/freigabe_schreiben.py`.')
write('gemeinsam/08_MANUELLE_GOAL_FREIGABE.md',t)

# Session snapshot directories already exist on VPS. Add no fake S01 directories.
# Pack routine will preserve these empty directories explicitly.
print('schema_mapping_contracts_v3_done')
