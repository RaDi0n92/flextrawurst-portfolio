from pathlib import Path
import json, re

ROOT=Path('/root/werkraum/gemgems-spielbeobachtung/2026-09-04_MOELLENKOTTEN_FORSCHUNG')

def w(rel,text):
    p=ROOT/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text.rstrip()+'\n',encoding='utf-8')

def edit(rel, old, new):
    p=ROOT/rel; t=p.read_text(encoding='utf-8')
    if old not in t:
        print('NOT_FOUND',rel,old[:90])
    t=t.replace(old,new)
    p.write_text(t,encoding='utf-8')

session_enum=[f'S{i:02d}' for i in range(1,13)]+['GRAVITY','REDTEAM01','REDTEAM02','STEUERUNG']
approval_sessions=[f'S{i:02d}' for i in range(1,13)]+['GRAVITY']
goals=[
 'GOAL_01_START_UND_QUELLEN','GOAL_02_FACHKARTIERUNG','GOAL_03_GEGENPRUEFUNG_UND_LUECKEN','GOAL_04_UEBERGABE',
 'GRAVITY_01_GRENZBEWEIS','GRAVITY_02_LAUFENDE_AUFSICHT','GRAVITY_03_STAFFELPRUEFUNG','GRAVITY_04_NAECHSTE_STAFFEL',
 'SPAWNHAUS_REFERENZKOERPER'
]

def nullable(base): return {'oneOf':[base,{'type':'null'}]}
rfc3339={'type':'string','format':'date-time'}
date_or_dt={'oneOf':[{'type':'string','format':'date'},{'type':'string','format':'date-time'},{'type':'null'}]}
valid_time={'type':['object','null'],'properties':{'start':date_or_dt,'end':date_or_dt},'required':['start','end'],'additionalProperties':False}
session={'enum':session_enum}
event_id={'type':'string','pattern':r'^EREIGNIS-MOELLENKOTTEN-(S0[1-9]|S1[0-2]|GRAVITY|REDTEAM01|REDTEAM02|STEUERUNG)-[0-9]{6}$'}
source_id={'type':'string','pattern':r'^QUELLE-MOELLENKOTTEN-(S0[1-9]|S1[0-2]|KANON)-[0-9]{6}$'}
fund_id={'type':'string','pattern':r'^FUND-MOELLENKOTTEN-S(0[1-9]|1[0-2])-[0-9]{6}$'}
route_id={'type':'string','pattern':r'^WEGABSCHNITT-MOELLENKOTTEN-S(0[1-9]|1[0-2])-[0-9]{6}$'}
object_id={'type':'string','pattern':r'^OBJEKT-MOELLENKOTTEN-[0-9]{6}$'}
boundary_id={'type':'string','pattern':r'^GRENZE-MOELLENKOTTEN-[0-9]{6}$'}
message_id={'type':'string','pattern':r'^NACHRICHT-MOELLENKOTTEN-(S0[1-9]|S1[0-2]|GRAVITY|REDTEAM01|REDTEAM02|STEUERUNG)-[0-9]{6}$'}
approval_id={'type':'string','pattern':r'^FREIGABE-MOELLENKOTTEN-(S0[1-9]|S1[0-2]|GRAVITY)-[0-9]{6}$'}

def str_or_null(): return {'type':['string','null']}
def array_of(schema,minItems=0):
    d={'type':'array','items':schema,'uniqueItems':True}
    if minItems: d['minItems']=minItems
    return d

position={'type':'array','prefixItems':[{'type':'number','minimum':-180,'maximum':180},{'type':'number','minimum':-90,'maximum':90}],'items':False,'minItems':2,'maxItems':2}
geometry={
 'oneOf':[
  {'type':'object','properties':{'geometry_type':{'const':'POINT'},'crs':{'type':'string','pattern':r'^EPSG:[0-9]+$'},'coordinates':position,'accuracy_m':{'type':['number','null'],'minimum':0},'location_method':{'type':'string','minLength':1}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False},
  {'type':'object','properties':{'geometry_type':{'const':'LINESTRING'},'crs':{'type':'string','pattern':r'^EPSG:[0-9]+$'},'coordinates':{'type':'array','items':position,'minItems':2},'accuracy_m':{'type':['number','null'],'minimum':0},'location_method':{'type':'string','minLength':1}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False},
  {'type':'object','properties':{'geometry_type':{'const':'POLYGON'},'crs':{'type':'string','pattern':r'^EPSG:[0-9]+$'},'coordinates':{'type':'array','items':{'type':'array','items':position,'minItems':4},'minItems':1},'accuracy_m':{'type':['number','null'],'minimum':0},'location_method':{'type':'string','minLength':1}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False},
  {'type':'object','properties':{'geometry_type':{'const':'NONE'},'crs':{'type':'null'},'coordinates':{'type':'null'},'accuracy_m':{'type':'null'},'location_method':{'type':['string','null']}},'required':['geometry_type','crs','coordinates','accuracy_m','location_method'],'additionalProperties':False},
 ]
}
measurement={'type':'object','properties':{'name':{'type':'string','minLength':1},'value':{'type':'number'},'unit':{'type':'string','minLength':1},'method':{'type':'string','minLength':1},'uncertainty':{'type':['number','null'],'minimum':0},'source_ids':array_of(source_id)},'required':['name','value','unit','method','uncertainty','source_ids'],'additionalProperties':False}
control_point={'type':'object','properties':{'geometry':{'$ref':'#/$defs/geometry'},'source_id':source_id,'description':{'type':'string','minLength':1}},'required':['geometry','source_id','description'],'additionalProperties':False}

actions={'enum':['ANLEGEN','INHALT_KORRIGIEREN','MERGE_STATUS_AENDERN','VERWERFEN']}
merge={'enum':['LOKAL','ZUR_PRUEFUNG','KANONISCH','ABGELEHNT']}
lifecycle_allof=[
 {'if':{'properties':{'aktion':{'const':'ANLEGEN'}}},'then':{'properties':{'ersetzt_ereignis_id':{'type':'null'}}}},
 {'if':{'properties':{'aktion':{'enum':['INHALT_KORRIGIEREN','MERGE_STATUS_AENDERN','VERWERFEN']}}},'then':{'properties':{'ersetzt_ereignis_id':event_id}}}
]

source_props={
 'schema_version':{'const':2},'ereignis_id':event_id,'source_id':source_id,'aktion':actions,'ersetzt_ereignis_id':nullable(event_id),'origin_event_ids':array_of(event_id),'session':session,
 'quelltyp':{'enum':['EXTERNE_ORIGINALQUELLE','EXTERNE_SEKUNDAERQUELLE','DANIEL_ORTSKENNTNIS','DANIEL_ERINNERUNG','DANIEL_GRUNDRISS_ODER_ZEICHNUNG','DANIEL_FOTO_ODER_BILD','EIGENE_BEOBACHTUNG']},
 'origin_key':{'type':'string','minLength':3},'title':str_or_null(),'address':str_or_null(),'publisher':str_or_null(),'source_date':date_or_dt,'retrieved_at':nullable(rfc3339),'observed_at':nullable(rfc3339),'valid_time':valid_time,
 'snapshot_path':{'type':['string','null'],'pattern':r'^(sessions/S(0[1-9]|1[0-2])/snapshots/|zustand/quellen_snapshots/)[^/].*$'},'snapshot_sha256':{'type':['string','null'],'pattern':r'^[0-9a-f]{64}$'},
 'ursprungsquelle_id':nullable(source_id),'abgeleitet_von_source_ids':array_of(source_id),'alias_source_ids':array_of(source_id),'notes':str_or_null(),'merge_status':merge
}
source_required=list(source_props)
source_event={'type':'object','properties':source_props,'required':source_required,'additionalProperties':False,'allOf':lifecycle_allof+[
 {'if':{'properties':{'snapshot_sha256':{'type':'string'}}},'then':{'properties':{'snapshot_path':{'type':'string'}}}},
 {'if':{'properties':{'merge_status':{'const':'KANONISCH'}}},'then':{'properties':{'session':{'const':'GRAVITY'},'source_id':{'type':'string','pattern':r'^QUELLE-MOELLENKOTTEN-KANON-[0-9]{6}$'}}}}
]}

finding_props={
 'schema_version':{'const':2},'ereignis_id':event_id,'fund_id':fund_id,'aktion':actions,'ersetzt_ereignis_id':nullable(event_id),'origin_event_ids':array_of(event_id),'session':session,'fachgebiet':{'type':'string','minLength':1},'aussage':{'type':'string','minLength':1},
 'object_ids':array_of(object_id),'source_ids':array_of(source_id),'bestaetigungsstatus':{'enum':['NICHT_GEPRUEFT','EINZELBELEG','MEHRERE_NICHT_UNABHAENGIGE_BELEGE','UNABHAENGIG_BESTAETIGT','WIDERSPROCHEN']},'sicherheitsstatus':{'enum':['BESTAETIGT','WAHRSCHEINLICH','OFFEN','WIDERSPRUECHLICH','VERWORFEN']},'weltstatus':{'enum':['REALITAETSBEHAUPTUNG','SPIELERFINDUNG','UEBERGANG_REAL_ZU_SPIELERFINDUNG']},
 'geometry':{'$ref':'#/$defs/geometry'},'measurements':{'type':'array','items':{'$ref':'#/$defs/measurement'}},'source_date':date_or_dt,'observed_at':nullable(rfc3339),'valid_time':valid_time,'verknuepfte_fund_ids':array_of(fund_id),'widersprueche':{'type':'array','items':{'type':'string'}},'offene_punkte':{'type':'array','items':{'type':'string'}},'raumstatus':str_or_null(),'merge_status':merge
}
finding_event={'type':'object','properties':finding_props,'required':list(finding_props),'additionalProperties':False,'allOf':lifecycle_allof+[
 {'if':{'properties':{'weltstatus':{'const':'REALITAETSBEHAUPTUNG'}}},'then':{'properties':{'source_ids':array_of(source_id,1)}}},
 {'if':{'properties':{'sicherheitsstatus':{'const':'BESTAETIGT'}}},'then':{'properties':{'source_ids':array_of(source_id,1)}}},
 {'if':{'properties':{'bestaetigungsstatus':{'const':'UNABHAENGIG_BESTAETIGT'}}},'then':{'properties':{'source_ids':array_of(source_id,2)}}},
 {'if':{'properties':{'merge_status':{'const':'KANONISCH'}}},'then':{'properties':{'session':{'const':'GRAVITY'}}}}
]}

route_props={
 'schema_version':{'const':2},'ereignis_id':event_id,'wegabschnitt_id':route_id,'aktion':actions,'ersetzt_ereignis_id':nullable(event_id),'origin_event_ids':array_of(event_id),'session':session,'start_ref':{'type':'string','minLength':1},'end_ref':str_or_null(),'connection_type':{'type':'string','minLength':1},
 'geometry':{'$ref':'#/$defs/geometry'},'source_ids':array_of(source_id,1),'object_ids':array_of(object_id),'related_fund_ids':array_of(fund_id),'known_branch_refs':array_of(route_id),'open_branch_refs':array_of(route_id),'boundary_event_ids':array_of(event_id),
 'left_side_object_ids':array_of(object_id),'right_side_object_ids':array_of(object_id),'sightline_fund_ids':array_of(fund_id),'measurements':{'type':'array','items':{'$ref':'#/$defs/measurement'}},'open_points':{'type':'array','items':{'type':'string'}},
 'source_date':date_or_dt,'observed_at':nullable(rfc3339),'valid_time':valid_time,'status':{'enum':['OFFENER_RAND','UNTERSUCHT','NICHT_WEITERFUEHREND','GRENZLAGE_UNGEKLAERT','DURCH_GRENZE_BEENDET']},'merge_status':merge
}
route_event={'type':'object','properties':route_props,'required':list(route_props),'additionalProperties':False,'allOf':lifecycle_allof+[
 {'if':{'properties':{'merge_status':{'const':'KANONISCH'}}},'then':{'properties':{'session':{'const':'GRAVITY'}}}}
]}

object_props={
 'schema_version':{'const':2},'ereignis_id':event_id,'object_id':object_id,'aktion':actions,'ersetzt_ereignis_id':nullable(event_id),'origin_event_ids':array_of(event_id),'session':{'const':'GRAVITY'},'object_type':{'enum':['GEBAEUDE','WEGOBJEKT','VEGETATION','GELAENDE','SONDERORT','INNENRAUM','UNTERGRUND','SONSTIGES']},'label':{'type':'string','minLength':1},'aliases':{'type':'array','items':{'type':'string'},'uniqueItems':True},'geometry':{'$ref':'#/$defs/geometry'},'source_ids':array_of(source_id),'related_fund_ids':array_of(fund_id),'created_at':rfc3339,'notes':str_or_null()
}
object_event={'type':'object','properties':object_props,'required':list(object_props),'additionalProperties':False,'allOf':lifecycle_allof}

approval_props={'schema_version':{'const':2},'freigabe_id':approval_id,'session':{'enum':approval_sessions},'goal_id':{'enum':goals},'entscheidung':{'enum':['FREIGEGEBEN','NICHT_FREIGEGEBEN','ZURUECKGENOMMEN']},'issued_by':{'const':'DANIEL'},'persisted_by':{'const':'STEUERUNG'},'issued_at':rfc3339,'recorded_at':rfc3339,'reference':{'type':'string','minLength':1}}
approval_event={'type':'object','properties':approval_props,'required':list(approval_props),'additionalProperties':False}

boundary_props={'schema_version':{'const':2},'ereignis_id':event_id,'grenze_id':boundary_id,'aktion':actions,'ersetzt_ereignis_id':nullable(event_id),'origin_event_ids':array_of(event_id),'session':{'const':'GRAVITY'},'status':{'enum':['IN_PRUEFUNG','ORIGINALVERIFIZIERT','ORIGINALGRENZE_NOCH_NICHT_GEFUNDEN']},'created_at':rfc3339,'source_ids':array_of(source_id),'geometry':{'oneOf':[{'$ref':'#/$defs/geometry'},{'type':'null'}]},'control_points':{'type':'array','items':{'$ref':'#/$defs/control_point'}},'notes':str_or_null()}
boundary_event={'type':'object','properties':boundary_props,'required':list(boundary_props),'additionalProperties':False,'allOf':lifecycle_allof+[
 {'if':{'properties':{'status':{'const':'ORIGINALVERIFIZIERT'}}},'then':{'properties':{'source_ids':array_of(source_id,1),'geometry':{'allOf':[{'$ref':'#/$defs/geometry'},{'properties':{'geometry_type':{'const':'POLYGON'}}}]},'control_points':{'type':'array','items':{'$ref':'#/$defs/control_point'},'minItems':3}}}}
]}

message_props={'schema_version':{'const':2},'nachricht_id':message_id,'sender':session,'recipient':session,'created_at':rfc3339,'subject':{'type':'string','minLength':1},'related_ids':{'type':'array','items':{'type':'string'},'uniqueItems':True},'finding':{'type':'string','minLength':1},'why_relevant':{'type':'string','minLength':1},'evidence_ids':{'type':'array','items':{'type':'string'},'uniqueItems':True},'requested_check':{'type':'string','minLength':1}}
message={'type':'object','properties':message_props,'required':list(message_props),'additionalProperties':False}

schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'flextrawurst://moellenkotten/DATENSCHEMA.json','title':'Möllenkotten Forschungsdaten','schema_version':2,'$defs':{'geometry':geometry,'measurement':measurement,'control_point':control_point,'source_event':source_event,'finding_event':finding_event,'route_event':route_event,'object_event':object_event,'approval_event':approval_event,'boundary_event':boundary_event,'message':message}}
w('maschinenvertrag/DATENSCHEMA.json',json.dumps(schema,ensure_ascii=False,indent=2))

# New canonical stores / snapshot roots. Existing JSONL are empty, so no migration is required.
for rel in ['zustand/objektregister.jsonl']:
    p=ROOT/rel
    if not p.exists(): p.write_text('',encoding='utf-8')
(ROOT/'zustand/quellen_snapshots').mkdir(parents=True,exist_ok=True)
for sd in sorted((ROOT/'sessions').iterdir()):
    if sd.is_dir(): (sd/'snapshots').mkdir(exist_ok=True)

# Calibration schema marker.
calp=ROOT/'zustand/raumkalibrierung.json'
cal=json.loads(calp.read_text(encoding='utf-8')); cal['schema_version']=2; calp.write_text(json.dumps(cal,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# H1: STEUERUNG is the only writer for freigaben.jsonl.
w('gemeinsam/08_MANUELLE_GOAL_FREIGABE.md','''# MANUELLE GOAL-FREIGABE

## /goal
Goal-Stufen werden niemals autonom freigeschaltet. Eine Session prüft ihre eigene Arbeit, dokumentiert den Prüfstand und hält danach an. Der nächste Goal-Abschnitt beginnt erst nach einer ausdrücklichen Freigabe durch Daniel und deren persistenter Eintragung in `../zustand/freigaben.jsonl`.

## Selbstprüfung
Die Session schreibt `SELBSTPRUEFUNG_BESTANDEN` oder `SELBSTPRUEFUNG_NICHT_BESTANDEN`. Diese Einschätzung schaltet nichts frei.

## Einziger Writer der Freigabeliste
`STEUERUNG` ist der einzige Writer von `../zustand/freigaben.jsonl`. Fachsessions, Gravity und Red-Team schreiben diese Datei nicht.

Wenn Daniel eine Freigabe, Nichtfreigabe oder Rücknahme ausspricht, wird die Entscheidung an `STEUERUNG` übergeben. Erst nachdem `STEUERUNG` das Ereignis erfolgreich append-only persistiert hat, gilt die Freigabe für den Forschungsbetrieb als dauerhaft registriert.

Ein Freigabeereignis enthält `schema_version = 2`, `freigabe_id`, `session`, `goal_id`, `entscheidung`, `issued_by = DANIEL`, `persisted_by = STEUERUNG`, `issued_at`, `recorded_at` und `reference`.

## Aktueller Freigabestand
Die Dateireihenfolge in `freigaben.jsonl` ist die verbindliche Reihenfolge. Für dieselbe Kombination aus Session und Goal gilt das letzte schema-valide Ereignis in der Datei. `issued_at` und `recorded_at` müssen RFC-3339-Zeitstempel sein, werden aber nicht benutzt, um die append-only Reihenfolge umzuschreiben.

Ohne ein aktuell wirksames `FREIGEGEBEN` beginnt die Session das Goal nicht.

## Gravity und Red-Team
Gravity und Red-Team können Prüfung, Nacharbeit oder Freigabe empfehlen. Sie persistieren keine Freigabe im Namen Daniels.

## Wenn Daniel nicht freigibt
Die Session bleibt beim aktuellen Goal und bearbeitet nur ausdrücklich angeforderte Nachprüfung, neue Belege oder Korrekturen dieses Goals. Sie beginnt keine Inhalte des nächsten Goals vorab.

## /goal-check
Die Goal-Stufe ist fachlich bereit zur Vorlage, wenn die Selbstprüfung vollständig dokumentiert ist. Der tatsächliche Übergang ergibt sich ausschließlich aus dem von `STEUERUNG` geführten Freigabelog.
''')

# H1/H3/M6/M8/M10/M11 operating contract.
w('gemeinsam/09_BETRIEBSVERTRAG.md','''# BETRIEBSVERTRAG — SPEICHER, KENNUNGEN, MERGE UND SCHREIBRECHTE

## /goal
Dieser Vertrag legt fest, wo Daten liegen, wer sie schreiben darf und wie Korrekturen, Quellenidentität und Zusammenführungen funktionieren. Er soll Konflikte verhindern, nicht zusätzliche Bürokratie erzeugen.

## Kanonische gemeinsame Speicherorte
- `../zustand/beweiskoerper.jsonl` — geprüfte Fundereignisse
- `../zustand/quellenregister.jsonl` — geprüfte kanonische Quellenereignisse
- `../zustand/wegekarte.jsonl` — geprüfte Wegereignisse
- `../zustand/objektregister.jsonl` — kanonische Objektidentitäten
- `../zustand/grenzstatus.jsonl` — Grenzereignisse
- `../zustand/freigaben.jsonl` — Daniels manuelle Goal-Freigaben
- `../zustand/raumkalibrierung.json` — Koordinaten- und Godot-Kalibrierung
- `../zustand/SPAWNHAUS_REFERENZSTAND.md` — von Gravity erzeugte kanonische Spawnhaus-Synthese, sobald Material dafür reicht

`JSONL` bedeutet genau ein vollständiges JSON-Objekt pro Zeile. Ereignisdateien sind append-only.

## Schema-Version
Alle neuen Ereignisse tragen `schema_version = 2`. Da beim Übergang auf Version 2 alle Forschungs-JSONL leer waren, existieren keine unveränderlichen Version-1-Ereignisse, die migriert werden müssten. Eine spätere Schemaänderung bekommt eine neue Versionsnummer; alte Ereignisse werden dann nach ihrer eigenen Version validiert oder durch einen ausdrücklich dokumentierten Migrationsschritt behandelt.

## Lokale Sessionausgabe
Jede Fachsession besitzt ihren eigenen Schreibraum:
- `sessions/<Session>/ausgabe/funde.jsonl`
- `sessions/<Session>/ausgabe/quellen.jsonl`
- `sessions/<Session>/ausgabe/wege.jsonl`
- `sessions/<Session>/snapshots/`
- ihre eigenen `ERGEBNIS_*.md`

Eine Fachsession schreibt nicht direkt in kanonische Zustandsdateien und nicht in die Ausgabe einer anderen Session.

## Schreibrechte
- Fachsessions: eigener Sessionordner, eigener Snapshot-Ordner und eigene Inbox-Nachrichten.
- Gravity: kanonischer Beweiskörper, Quellenregister, Wegekarte, Objektregister, Grenzstatus, kanonische Quellensnapshots, Spawnhaus-Referenzstand, eigene Ergebnisse und Nachrichten.
- Red-Team: eigener Ergebnisbereich und Nachrichten; keine kanonischen Wahrheitsdateien.
- `STEUERUNG`: alleiniger Writer von `../zustand/freigaben.jsonl`.

## Append-only und Ereignis-Lifecycle
Bestehende Ereigniszeilen werden nicht verändert oder gelöscht.
- `ANLEGEN`: erstes Ereignis einer Sachkennung; `ersetzt_ereignis_id = null`.
- `INHALT_KORRIGIEREN`: inhaltliche Korrektur; verweist auf das ersetzte Ereignis.
- `MERGE_STATUS_AENDERN`: ausschließlich ein append-only Statusübergang wie `LOKAL` zu `ZUR_PRUEFUNG`; verweist auf das ersetzte Ereignis.
- `VERWERFEN`: verwirft einen früheren Stand; verweist auf das ersetzte Ereignis.

Grenzereignisse verwenden dieselbe Lifecycle-Semantik.

## Merge von Session zu Gravity
1. Die Fachsession legt lokal ein Ereignis mit `merge_status = LOKAL` an.
2. Nach eigener Prüfung erzeugt sie ein neues Ereignis mit `aktion = MERGE_STATUS_AENDERN`, `merge_status = ZUR_PRUEFUNG` und `ersetzt_ereignis_id` auf den lokalen Vorgänger.
3. Gravity prüft Quellenursprung, räumliche Logik, Statusachsen, Kennungen und Widersprüche.
4. Bei Annahme erzeugt Gravity im kanonischen Speicher ein neues `ANLEGEN`-Ereignis mit `merge_status = KANONISCH` und verweist über `origin_event_ids` auf die lokalen prüfreifen Ereignisse.
5. Bei Ablehnung bleibt der lokale Bestand erhalten; Gravity meldet den Grund über die Inbox.

## Kennungsräume
### Sessionlokal
- Fund: `FUND-MOELLENKOTTEN-S01-000001`
- Quelle: `QUELLE-MOELLENKOTTEN-S01-000001`
- Wegabschnitt: `WEGABSCHNITT-MOELLENKOTTEN-S01-000001`

Die Sessionnummer wird entsprechend angepasst. Der sechsstellige Zähler einer Sachkennung wird innerhalb einer Session nicht für einen anderen Sachgegenstand wiederverwendet. Mehrere Lifecycle-Ereignisse dürfen dieselbe Sachkennung tragen, aber jedes `ereignis_id` ist global eindeutig.

### Kanonisch durch Gravity
- Objekt: `OBJEKT-MOELLENKOTTEN-000001`
- Quelle: `QUELLE-MOELLENKOTTEN-KANON-000001`
- Grenze: `GRENZE-MOELLENKOTTEN-000001`

Gravity vergibt kanonische Objektkennungen früh, sobald mehrere Fachsessions dieselbe reale Entität referenzieren müssen. Funde tragen dafür `object_ids`. Das Objekt selbst wird append-only in `objektregister.jsonl` geführt.

## Quellenidentität und Deduplizierung
Jede Quelle besitzt zusätzlich `origin_key`. Dieser beschreibt den tatsächlichen Ursprung unabhängig von lokaler Sessionkennung, beispielsweise eine normalisierte Originaladresse oder eine stabile Kennung für Daniels bereitgestelltes Material.

Beim Merge prüft Gravity `origin_key` gegen das kanonische Quellenregister. Existiert derselbe Ursprung bereits, wird keine zweite kanonische Quelle erfunden. Stattdessen wird die vorhandene kanonische `source_id` wiederverwendet und die lokale Quellenkennung über `alias_source_ids` nachvollziehbar verbunden.

`ursprungsquelle_id` und `abgeleitet_von_source_ids` halten Ableitungsbeziehungen fest. Unterschiedliche Seiten mit derselben Ursprungsquelle zählen nicht als unabhängige Bestätigung.

## Snapshots
Lokale Sessions speichern gesicherte Quellenkopien ausschließlich unter `sessions/<Session>/snapshots/`. Gravity kann beim kanonischen Merge eine geprüfte Kopie nach `../zustand/quellen_snapshots/` übernehmen.

`snapshot_path` ist relativ zum Forschungsroot und darf nur in diesen vorgesehenen Snapshot-Wurzeln liegen. Wenn `snapshot_sha256` gesetzt ist, müssen Datei und Hash zusammenpassen. Der Final-Auditor prüft Existenz, Pfadsicherheit und Prüfsumme.

## Statusachsen bleiben getrennt
`quelltyp`, `bestaetigungsstatus`, `sicherheitsstatus`, `weltstatus`, Goal-Status, Grenzstatus und Raumreife werden nicht ineinander umgedeutet.

## Nachrichten statt Fremdschreiben
Sessions greifen nicht in fremde Ergebnisdateien ein. Hinweise gehen als eigene JSON-Nachricht nach `../kommunikation/inbox/<Empfaenger>/`.

## Maschinenvertrag
Feldtypen, Pflichtfelder, Kennungsmuster, Zeitformate und bedingte Invarianten stehen in `../maschinenvertrag/DATENSCHEMA.json`. Der Final-Auditor prüft zusätzlich Referenzintegrität und Beziehungen, die ein einzelnes JSON-Schema nicht vollständig beurteilen kann.
''')

# H2 Spawnhaus ownership.
w('gemeinsam/04_GOAL_SPAWNHAUS_REFERENZKOERPER.md','''# GOAL VORPHASE — SPAWNHAUS ALS REFERENZKÖRPER

## /goal
Bevor Möllenkotten als große Fläche in Godot wächst, wird Hauptstraße 151 als erster besonders dichter Referenzkörper vorbereitet. Außenwelt und Innenwelt bleiben quellenklar getrennt.

## Arbeitsweise und eigener Spielraum
Innerhalb dieses Goals wählst du selbst die sinnvollsten Such- und Prüfwege. Wenn ein vorgeschlagener Weg nicht funktioniert oder eine bessere Quelle auftaucht, dokumentiere kurz warum und nutze den besseren nachvollziehbaren Weg.

## Außenkörper
Öffentlich zugängliche Quellen können für Lage, Orientierung, äußere Gebäudekontur, Dachform, sichtbare Fassaden, Fenster- und Türanordnung, Grundstücksanschluss, Straßenbezug und öffentlich sichtbare Nebenkörper verwendet werden.

## Innenkörper
Die reale Innenstruktur wird nicht aus Außenbildern geraten. Primärquellen sind Daniels eigene Ortskenntnis, Erinnerung, Zeichnungen, Grundrisse und von Daniel bereitgestellte Fotos oder Bilder. Dafür existiert der Quelltyp `DANIEL_FOTO_ODER_BILD`.

Zielstruktur, soweit Daniel sie kennt:
- jede Etage
- Treppenhaus
- Lage und Zuschnitt der Wohnungen
- Keller
- Dachboden
- die besonders gut bekannte obere Wohnung möglichst maßhaltig

## Raumdaten
Außenkontur, bekannte Maße und von Daniel gelieferte Grundrisse werden nach `10_RAUM_ZEIT_UND_GODOT.md` strukturiert. Solange `../zustand/raumkalibrierung.json` nicht kalibriert ist, werden keine verbindlichen Godot-Koordinaten erfunden.

## Maßhaltigkeit
Bekannte Maße bleiben bekannte Maße. Schätzungen tragen Methode und Unsicherheit. Widersprüche zwischen Erinnerung, Zeichnung und äußerer Gebäudegeometrie bleiben sichtbar.

## Schutz vor Erfindung
Unbekannte private Innenräume bleiben unbekannt. Keine Session vervollständigt sie aus typischen Grundrissen, Immobilienlogik oder Außenfenstern.

## Eigentum und Mergeweg
Die beteiligten Fachsessions schreiben ihre Spawnhaus-Beiträge nur in ihre eigenen normalen Ausgabedateien und Ergebnisdateien. Sie schreiben keinen gemeinsamen Referenzstand.

Gravity ist der einzige Writer von `../zustand/SPAWNHAUS_REFERENZSTAND.md`. Gravity erzeugt oder aktualisiert diesen Referenzstand erst aus geprüften kanonischen Funden, Quellen und Objektkennungen. Damit gibt es keinen Mehrschreiber auf eine gemeinsame Spawnhaus-Datei.

## Verbindung zu den Fachsessions
- Session 02 prüft den äußeren Fassadenkörper.
- Session 05 prüft äußere Geometrie, Geschosse und Dach.
- Session 09 übernimmt die von Daniel freigegebene Innenraumrekonstruktion.
- Session 04 verbindet später Innenstufen, Geschosshöhen und Geländeanschluss.
- Session 03 kann reale Keller- oder Untergrundinformationen aufnehmen; erfundene Tiefe bleibt getrennt als Spielerfindung markiert.

## So prüfst du die Goal-Stufe
Prüfe die Kriterien einzeln als **Kriterium → Beleg → Ergebnis**. `SELBSTPRUEFUNG_BESTANDEN` ist keine Freigabe für ein anderes Goal.

## Klare Prüflinie
Die Vorphase ist fachlich bereit für Gravitys Synthese, wenn klar getrennt vorliegt, was außen belegt ist, was Daniel innen kennt, welche Maße bekannt oder geschätzt sind und welche Innenbereiche offen bleiben.
''')

# Create canonical spawnhouse state stub owned by Gravity.
w('zustand/SPAWNHAUS_REFERENZSTAND.md','''# SPAWNHAUS-REFERENZSTAND

**Status:** NOCH_NICHT_SYNTHETISIERT

Diese kanonische Datei wird ausschließlich von Gravity aus geprüften kanonischen Funden, Quellen und Objektkennungen aufgebaut. Fachsessions schreiben hier nicht direkt hinein.
''')

# H4/M7 route prose, object relationships.
w('gemeinsam/05_WEGE_UND_RANDSTATUS.md','''# WEGE- UND RANDSTATUS

## /goal
Alle Fachsessions sollen denselben räumlichen Forschungsfortschritt sehen. Offene Seitenwege und ungeklärte Anschlüsse bleiben sichtbar.

## Lokale und kanonische Wege
Eine Fachsession schreibt eigene Wegereignisse nur nach `sessions/<Session>/ausgabe/wege.jsonl`. Gravity prüft diese und übernimmt tragfähige Ereignisse append-only nach `../zustand/wegekarte.jsonl`.

## Maschinenlesbarer Wegabschnitt
`route_event` enthält mindestens:
- `wegabschnitt_id`, Start- und Endbezug und Verbindungstyp
- Geometrie und räumliche Genauigkeit
- `source_ids`
- `object_ids` und `related_fund_ids`
- bekannte und offene Abzweigungen
- Grenzereignis-Verknüpfungen
- linke und rechte Objektseite
- Sichtachsen als verknüpfte Fundkennungen
- strukturierte Maße für Breite, Höhe, Gefälle oder andere Messwerte
- offene Punkte
- `source_date`, `observed_at` und `valid_time`
- Sachstatus und Merge-Status

Damit können historische und aktuelle Wegzustände getrennt geführt werden.

## Offener Rand
Ein offener Rand ist eine belegte Verbindung, deren Fortsetzung noch nicht untersucht wurde. Er bleibt sichtbar, bis er untersucht, als nicht weiterführend belegt oder durch eine verifizierte Gebietsgrenze begrenzt wurde.

`known_branch_refs` verweist auf bereits bekannte Wegabschnittskennungen. `open_branch_refs` darf auch vorreservierte, noch nicht angelegte Wegabschnittskennungen enthalten und wird deshalb bei der Referenzintegrität anders behandelt.

## Räumliche Reihenfolge
Nahe offene Ränder rund um Hauptstraße 151 werden bevorzugt geschlossen. Weiter entfernte Sonderorte können fachlich vorgezogen werden, werden aber nicht als räumlich angeschlossen behandelt, solange die Verbindungskette fehlt.

## /goal-check
`SELBSTPRUEFUNG_BESTANDEN` für die Dokumentation eines Teilraums bedeutet: Alle bekannten Anschlüsse sind entweder untersucht oder ausdrücklich als offener Rand dokumentiert. Dieser Goal-Status ist kein Reifegrad des Teilraums.
''')

# Source types/object fields in human schema doc.
w('gemeinsam/07_FUNDKARTE_SCHEMA.md','''# FUNDKARTE — GEMEINSAMES SCHEMA

## /goal
Jeder Fund soll klein genug sein, dass ein anderer Forschungspartner ihn unabhängig nachvollziehen, räumlich einordnen und später korrigieren kann. Der verbindliche Maschinenvertrag ist `../maschinenvertrag/DATENSCHEMA.json` in Schema-Version 2.

## Fundereignis
Ein Fundereignis enthält unter anderem `schema_version`, `ereignis_id`, `fund_id`, Lifecycle-Aktion, `object_ids`, `source_ids`, getrennte Statusachsen, Geometrie, Maße, Zeitbezug, Verknüpfungen, Widersprüche, offene Punkte und Merge-Status.

`object_ids` verbindet fachübergreifende Funde mit denselben kanonischen Objekten aus `../zustand/objektregister.jsonl`.

## Quellen sind eigene Objekte
Eine Quelle besitzt `source_id`, `origin_key`, Quelltyp, Ableitungsbeziehungen und gegebenenfalls Snapshot-Provenienz. Kanonische Quellen verwenden Kennungen wie `QUELLE-MOELLENKOTTEN-KANON-000001`.

Erlaubte Quelltypen sind:
- `EXTERNE_ORIGINALQUELLE`
- `EXTERNE_SEKUNDAERQUELLE`
- `DANIEL_ORTSKENNTNIS`
- `DANIEL_ERINNERUNG`
- `DANIEL_GRUNDRISS_ODER_ZEICHNUNG`
- `DANIEL_FOTO_ODER_BILD`
- `EIGENE_BEOBACHTUNG`

## Bestätigung
- `NICHT_GEPRUEFT`
- `EINZELBELEG`
- `MEHRERE_NICHT_UNABHAENGIGE_BELEGE`
- `UNABHAENGIG_BESTAETIGT`
- `WIDERSPROCHEN`

## Sicherheit
- `BESTAETIGT`
- `WAHRSCHEINLICH`
- `OFFEN`
- `WIDERSPRUECHLICH`
- `VERWORFEN`

## Weltstatus
- `REALITAETSBEHAUPTUNG`
- `SPIELERFINDUNG`
- `UEBERGANG_REAL_ZU_SPIELERFINDUNG`

Ein bestätigter Realitätsfund ohne Quelle ist schemawidrig. `UNABHAENGIG_BESTAETIGT` verlangt mindestens zwei Quellen; der Final-Auditor prüft zusätzlich, ob deren `origin_key` tatsächlich verschieden ist.

## Lokale Ablage
Eine Fachsession schreibt `ausgabe/funde.jsonl`, `ausgabe/quellen.jsonl` und `ausgabe/wege.jsonl`. Korrekturen und Merge-Statuswechsel sind neue Lifecycle-Ereignisse und überschreiben keine alte Zeile.

## /goal-check
Eine Fundkarte ist verwendbar, wenn ein anderer Forschungspartner erkennen kann, was behauptet wird, auf welchen Quellen es beruht, welchem Objekt es gegebenenfalls zugeordnet ist, wo und wann es gilt und was offen bleibt.
''')

# M1/M2 time and geometry contract.
w('gemeinsam/10_RAUM_ZEIT_UND_GODOT.md','''# RAUM, ZEIT UND GODOT — MASCHINENBAUBARE WELTDATEN

## /goal
Räumliche Forschung soll nicht nur für Menschen verständlich, sondern später reproduzierbar in eine Spielwelt überführbar sein. Deshalb bleiben Geometrie, Genauigkeit, Maße, Zeit und Godot-Ableitung strukturiert.

## Geometrie
Geografische Ausgangsdaten werden, soweit möglich, in `EPSG:4326` gespeichert. Das Schema erlaubt `POINT`, `LINESTRING`, `POLYGON` und `NONE`.

Für reale Geometrien erzwingt der Maschinenvertrag numerische Koordinaten mit gültigen Längen- und Breitengradbereichen. Ein `POINT` ist genau ein Koordinatenpaar, eine `LINESTRING` besitzt mindestens zwei Punkte und ein `POLYGON` mindestens einen Ring mit mindestens vier Punkten. Der Final-Auditor prüft zusätzlich, dass Polygonringe geschlossen sind.

`NONE` bedeutet: räumlicher Bezug ist bekannt, aber noch nicht maschinenlesbar geometrisiert. Dann bleiben Koordinaten und Koordinatenreferenzsystem ausdrücklich `null`.

## Genauigkeit und Maße
`accuracy_m` ist die geschätzte räumliche Unsicherheit in Metern oder `null`, wenn keine seriöse Genauigkeit angegeben werden kann. Maße besitzen Bezeichnung, Wert, Einheit, Methode, Unsicherheit und Quellenkennungen.

## Zeitmodell
Zeitfelder verwenden ISO 8601. Ereigniszeitpunkte wie `retrieved_at`, `observed_at`, `issued_at`, `recorded_at` und `created_at` verwenden RFC 3339 mit Zeitzone. `source_date` und Grenzen von `valid_time` dürfen ein vollständiges ISO-Datum oder einen RFC-3339-Zeitpunkt tragen; unbekannte Zeit bleibt `null`.

Die Dateireihenfolge eines append-only Ereignislogs bleibt die Ereignisreihenfolge. Zeitfelder dürfen diese Reihenfolge nicht rückwirkend umsortieren.

## Bildperspektive
Bei Bildern können Blickrichtung, Kamerastandort, Bestimmungsmethode, räumliche Genauigkeit und verdeckte Bereiche als Funde und Maße gespeichert werden. Unbekannte Blickrichtung bleibt unbekannt.

## Godot-Kalibrierung
Die verbindliche Kalibrierung steht in `../zustand/raumkalibrierung.json`. Solange dort `status = NICHT_KALIBRIERT` steht, erzeugt keine Session verbindliche lokale Godot-Koordinaten.

Nach einer verifizierten Kalibrierung gilt grundsätzlich:
- Godot `x`: lokale Ostrichtung in Metern
- Godot `y`: Höhe in Metern relativ zum verifizierten Ursprung
- Godot `z`: negative lokale Nordrichtung in Metern

Der konkrete geografische Ursprung, seine Höhe, Transformationsmethode und Versionsnummer müssen in `raumkalibrierung.json` stehen, bevor diese Ableitung verbindlich wird.

## /goal-check
Räumliche Daten sind maschinenbaubar, wenn Geometrie oder bewusst `NONE`, räumliche Genauigkeit, relevante Maße und Zeitbezug explizit vorliegen und eine Godot-Ableitung nur bei vorhandener Kalibrierung erfolgt.
''')

# Communication schema v2 / constrained recipients.
w('gemeinsam/06_KOMMUNIKATION_UND_INBOX.md','''# KOMMUNIKATION UND INBOX

## /goal
Sessions sollen sich gegenseitig helfen können, ohne sich gegenseitig zu überschreiben. Hinweise bleiben konkret, begründet und als einzelne Nachrichten nachvollziehbar.

## Kanonischer Ort
Nachrichten liegen als einzelne JSON-Dateien unter `../kommunikation/inbox/<Empfaenger>/`. Jede Nachricht entspricht `$defs.message` aus `../maschinenvertrag/DATENSCHEMA.json` und trägt `schema_version = 2`.

## Empfängerkennungen
Erlaubt sind `S01` bis `S12`, `GRAVITY`, `REDTEAM01`, `REDTEAM02` und `STEUERUNG`. Sender und Empfänger werden vom Maschinenvertrag auf genau diese Kennungen begrenzt.

## Inhalt
Eine Nachricht enthält stabile Nachrichtenkennung, Absender, Empfänger, RFC-3339-Erstellungszeit, Betreff, betroffene Kennungen, Beobachtung, Relevanz, Belegkennungen und gewünschte Prüfung.

## Ton
Formuliere wie gegenüber einem kompetenten Forschungspartner. Eine Nachricht gibt Orientierung, nicht Gehorsamsbefehle.

## Zuständigkeit
Ein fachfremder Fund bleibt ein Hinweis. Die zuständige Session entscheidet, wie sie ihn prüft und einordnet. Niemand übernimmt fremde Aussagen ungeprüft in den gemeinsamen Beweiskörper.

## /goal-check
Kommunikation ist gelungen, wenn der Empfänger ohne Rückfrage versteht, worum es geht, warum es relevant ist und welche Prüfung noch fehlt.
''')

# Add object register to Gravity ownership text if not already explicit enough.
edit('gravity/00_GRAVITY.md','Du bist alleiniger fachlicher Schreiber von `../zustand/beweiskoerper.jsonl`, `../zustand/quellenregister.jsonl`, `../zustand/wegekarte.jsonl` und `../zustand/grenzstatus.jsonl`.','Du bist alleiniger fachlicher Schreiber von `../zustand/beweiskoerper.jsonl`, `../zustand/quellenregister.jsonl`, `../zustand/wegekarte.jsonl`, `../zustand/objektregister.jsonl`, `../zustand/grenzstatus.jsonl` und `../zustand/SPAWNHAUS_REFERENZSTAND.md`.')

# Grammar K1: neutral colon construction for all session cores.
for p in (ROOT/'sessions').glob('*/00_SESSIONKERN.md'):
    t=p.read_text(encoding='utf-8')
    t=t.replace('Dein Beitrag zum gemeinsamen Möllenkotten-Körper ist ', 'Dein Beitrag zum gemeinsamen Möllenkotten-Körper: ')
    p.write_text(t,encoding='utf-8')

# Historic audit interpretation note without modifying historic files.
hist=ROOT.parent/'2026-09-04_MOELLENKOTTEN_FORSCHUNG_REDTEAM8_AUDIT'
(hist/'00_AKTUELLE_EINORDNUNG_2026-09-05.md').write_text('''# AKTUELLE EINORDNUNG DES HISTORISCHEN ACHTFACH-AUDITS\n\nDie vorhandenen historischen Auditdateien in diesem Ordner bleiben unverändert. Formulierungen wie „608 Einzelprüfungen“ werden heute präziser eingeordnet: Belegt sind 608 Datei-Pass-Durchläufe eines deterministischen Transformationsskripts, nicht 608 unabhängige semantische Einzelprüfungen.\n\nDieser Hinweis ist zusätzlich angelegt worden, damit der historische Unterordner auch isoliert nicht mehr ohne die spätere Korrektur gelesen werden muss.\n''',encoding='utf-8')

print('semantic_contract_and_schema_fix_done')
