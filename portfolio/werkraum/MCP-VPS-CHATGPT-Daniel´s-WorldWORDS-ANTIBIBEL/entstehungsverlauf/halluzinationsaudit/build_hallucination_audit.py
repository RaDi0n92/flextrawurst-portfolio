#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from collections import Counter
import datetime as dt
import hashlib
import json
import os
import re
import tempfile

ANTI = Path('/root/werkraum/MCP-VPS-CHATGPT-Daniel´s-WorldWORDS-ANTIBIBEL')
AUDIT = ANTI / 'entstehungsverlauf/halluzinationsaudit'
CLAUDE = Path('/root/.claude/projects')
CODEX = Path('/root/.codex/sessions')
NOW = dt.datetime.now(dt.timezone.utc).isoformat()

AUTO_PATTERNS = [
    r'^\s*<task-notification>', r'^\s*<system-reminder>', r'^\s*<local-command-caveat>',
    r'^\s*<command-message>', r'^\s*<command-name>', r'^\s*\[Request interrupted',
    r'^\s*\[Your previous response had no visible output',
    r'^\s*This session is being continued from a previous conversation',
    r'^\s*You are researching one angle', r'^\s*You are helping Claude Code restore session context',
    r'^\s*Research task \(', r'^\s*Run the ["“]?deep-research',
    r'^\s*Base directory for this skill:', r'^\s*Important instructions:',
]
AUTO_RX = [re.compile(p, re.I | re.M) for p in AUTO_PATTERNS]
PASTE_RX = re.compile(
    r'(?:```|\n\s*[●⎿✻]\s|\broot@[^\s:]+:|login as:|Authenticating with public key|'
    r'Welcome to Ubuntu|System information as of|\[BESTÄTIGT\]|\[ABGELEITET\]|'
    r'Created by trial version|BEGIN EDITED|END EDITED|<result>|<summary>|'
    r'\n\s*Table\s*\n|\n\s*Copy\s*\n|\n\s*Edit\s*\n|\n\s*Share\s*\n)',
    re.I,
)
SECRET_RX = [
    re.compile(r'(?i)(client_secret|api[_-]?key|authorization|bearer|password|token)\s*[=:]\s*[^\s,;]+'),
    re.compile(r'\b[A-Za-z0-9_-]{28,}\b'),
]

def atomic(path: Path, data: bytes) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
    actual = path.read_bytes()
    if actual != data:
        raise RuntimeError(f'Rücklesefehler: {path}')
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def write_text(name: str, text: str) -> dict:
    return atomic(AUDIT/name, (text.rstrip()+'\n').encode('utf-8'))

def write_json(name: str, obj) -> dict:
    return atomic(AUDIT/name, (json.dumps(obj, ensure_ascii=False, indent=2)+'\n').encode('utf-8'))

def redact(text: str) -> str:
    out = text
    for rx in SECRET_RX:
        if rx.pattern.startswith('(?i)'):
            out = rx.sub(lambda m: m.group(1) + '=[REDACTED]', out)
        else:
            out = rx.sub('[LONG_TOKEN_REDACTED]', out)
    return out

def classify(text: str, provider: str, meta: dict) -> tuple[str, list[str]]:
    reasons=[]
    if provider == 'claude':
        if meta.get('isMeta') is True:
            return 'AUTOMATISCH_ODER_SYSTEMISCH', ['Claude isMeta=true']
        if meta.get('promptSource') == 'system':
            return 'AUTOMATISCH_ODER_SYSTEMISCH', ['Claude promptSource=system']
        if meta.get('isCompactSummary') is True:
            return 'AUTOMATISCH_ODER_SYSTEMISCH', ['Claude isCompactSummary=true']
        if meta.get('isVisibleInTranscriptOnly') is True:
            return 'AUTOMATISCH_ODER_SYSTEMISCH', ['Claude isVisibleInTranscriptOnly=true']
    for rx in AUTO_RX:
        if rx.search(text):
            return 'AUTOMATISCH_ODER_SYSTEMISCH', [f'Muster: {rx.pattern}']
    if PASTE_RX.search(text): reasons.append('eingefügtes Protokoll/Code/Chatmaterial erkannt')
    if len(text) > 1200: reasons.append('Länge über 1.200 Zeichen')
    if text.count('\n') > 18: reasons.append('mehr als 18 Zeilen')
    if reasons:
        return 'USERROLLE_MIT_EINGEFUEGTEM_ODER_UNKLAREM_MATERIAL', reasons
    if len(text.strip()) <= 1200:
        return 'WAHRSCHEINLICH_AKTUELLE_MENSCHLICHE_EINGABE', ['kurzer Userrollen-Text ohne Automatik-/Paste-Marker']
    return 'USERROLLE_UNGEKLAERT', ['keine sichere Feinklassifikation']

def extract_claude():
    rows=[]; files=0; parse_errors=0
    for p in CLAUDE.rglob('*.jsonl'):
        files += 1
        try:
            with p.open(encoding='utf-8', errors='replace') as f:
                for no,line in enumerate(f,1):
                    try:o=json.loads(line)
                    except Exception: parse_errors += 1; continue
                    if o.get('type')!='user': continue
                    msg=o.get('message')
                    if not isinstance(msg,dict) or msg.get('role')!='user': continue
                    content=msg.get('content')
                    if not isinstance(content,str): continue
                    meta={k:o.get(k) for k in ('isMeta','promptSource','isCompactSummary','isVisibleInTranscriptOnly','isSidechain','sessionId','uuid','promptId') if k in o}
                    category,reasons=classify(content,'claude',meta)
                    rows.append({'provider':'claude','path':str(p),'line':no,'timestamp':o.get('timestamp'),'category':category,'reasons':reasons,'text_length':len(content),'line_count':content.count('\n')+1,'text_sha256':hashlib.sha256(content.encode('utf-8','replace')).hexdigest(),'excerpt':redact(re.sub(r'\s+',' ',content).strip()[:600]),'metadata':meta})
        except Exception: parse_errors += 1
    return rows,files,parse_errors

def extract_codex():
    rows=[]; files=0; parse_errors=0
    for p in CODEX.rglob('*.jsonl'):
        files += 1
        try:
            with p.open(encoding='utf-8', errors='replace') as f:
                for no,line in enumerate(f,1):
                    try:o=json.loads(line)
                    except Exception: parse_errors += 1; continue
                    if o.get('type')!='event_msg': continue
                    payload=o.get('payload')
                    if not isinstance(payload,dict) or payload.get('type')!='user_message': continue
                    content=payload.get('message')
                    if not isinstance(content,str): continue
                    meta={'images':len(payload.get('images') or []),'local_images':len(payload.get('local_images') or []),'audio':len(payload.get('audio') or [])}
                    category,reasons=classify(content,'codex',meta)
                    rows.append({'provider':'codex','path':str(p),'line':no,'timestamp':o.get('timestamp'),'category':category,'reasons':reasons,'text_length':len(content),'line_count':content.count('\n')+1,'text_sha256':hashlib.sha256(content.encode('utf-8','replace')).hexdigest(),'excerpt':redact(re.sub(r'\s+',' ',content).strip()[:600]),'metadata':meta})
        except Exception: parse_errors += 1
    return rows,files,parse_errors

claude_rows,claude_files,claude_errors=extract_claude()
codex_rows,codex_files,codex_errors=extract_codex()
rows=claude_rows+codex_rows
counts=Counter(r['category'] for r in rows)
provider_counts={p:dict(Counter(r['category'] for r in rows if r['provider']==p)) for p in ('claude','codex')}

# This is a provenance aid, not an authorship oracle.
with (AUDIT/'03_USERROLLEN_KONSERVATIV.jsonl').open('w',encoding='utf-8') as f:
    for r in rows: f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')

manifest={
    'schema_version':'1.0','created_utc':NOW,
    'source_files':{'claude':claude_files,'codex':codex_files},
    'userrole_text_records':len(rows),
    'categories':dict(counts),
    'categories_by_provider':provider_counts,
    'parse_error_lines':claude_errors+codex_errors,
    'hard_limit':'Auch WAHRSCHEINLICH_AKTUELLE_MENSCHLICHE_EINGABE beweist nur wahrscheinliche aktuelle Übermittlung durch Daniel, nicht die Urheberschaft jedes enthaltenen Wortes.',
    'excluded_source':'Zensi ist vollständig ausgeschlossen, weil Daniel ausdrücklich klarstellte, dass Zensi nie direkt eingesetzt wurde.',
    'output_sha256':hashlib.sha256((AUDIT/'03_USERROLLEN_KONSERVATIV.jsonl').read_bytes()).hexdigest(),
}
write_json('04_USERROLLEN_AUDIT_MANIFEST.json',manifest)

rules='''# Regeln des Halluzinationsaudits

## Zweck

Dieser Audit prüft Aussagen, die während der Metamonster-Wortsuche entstanden sind. Er trennt reale Messwerte, Fundstellen, Sprecherrollen, Urheberschaft und Interpretation.

## Verbindliche Klassen

- `BESTAETIGT`: direkt rückgelesene Datei, Datenbankzeile, Werkzeugmessung oder aktuelles Daniel-Zitat.
- `BESTAETIGT_MIT_SCOPE`: Messung stimmt nur innerhalb eines ausdrücklich genannten Filters.
- `WAHRSCHEINLICH`: starke Indizien, aber kein vollständiger Ursprungskörper.
- `UNKLAR`: Fundstelle vorhanden, Urheber oder Entstehungsweg nicht belegt.
- `HERABGESTUFT`: frühere Formulierung war stärker als die Belege.
- `VERWORFEN`: Aussage ist falsch oder durch spätere Prüfung widerlegt.

## Schutzregeln

1. Fundstelle ist nicht Urheberschaft.
2. `role=user`, `type=user`, `mensch` oder `Angelegt von` sind Datenfelder, keine notarielle Wahrheit.
3. Ein Dateiname mit einer Seitenzahl beweist keine nachgezählte Seitenzahl.
4. Null Scanner-Ausnahmen bedeuten nicht semantische Richtigkeit, Vollständigkeit oder unabhängige Quellen.
5. Wiederholte, generierte oder gespiegelte Dateien werden nicht als ebenso viele eigenständige Sprachursprünge gezählt.
6. Ein von Daniel eingefügter Text ist eine von Daniel übermittelte Quelle, aber nicht automatisch vollständig von Daniel verfasst.
7. AI-Antworten in alten Gesprächsexporten dürfen eigene Halluzinationen enthalten und werden nicht als Sachquelle benutzt.
8. ChatGPT-Suche bedeutet hier nur erreichbare aktuelle Gesprächs-, Bibliotheks- und VPS-Körper. Keine vollständige Kontoweitsuche wird behauptet.
'''
write_text('00_AUDITREGELN.md',rules)

claims=[
 {'claim':'Der VPS sei ein 3,8-GB-Sprachbiotop.','status':'VERWORFEN','finding':'3,8 GB war keine gültige Beschreibung des VPS. Aktuell gemessen: Root-Dateisystem 997.388.681.216 Byte Gesamtgröße, 510.450.950.144 Byte belegt.','action':'Nur noch als dokumentierter Assistenzfehler zitieren.'},
 {'claim':'Der VPS sei ungefähr 500 GB groß.','status':'HERABGESTUFT_ZU_PRAEZISE','finding':'Ungefähr 500 GB beschreibt die belegte Datenmenge brauchbar. Die Gesamtkapazität liegt bei knapp 1 TB.','action':'Formulieren: rund 510 GB belegt auf einem knapp 1-TB-Dateisystem.'},
 {'claim':'20.258 Dateien und rund 630 MB wurden gelesen.','status':'BESTAETIGT_MIT_SCOPE','finding':'Stimmt für den Werkraumscanner mit Dateityp-, Größen- und Ausschlussfiltern. Kein Vollscan aller Dateien.','action':'Immer Scannerfilter und Ausschlüsse nennen.'},
 {'claim':'4.359.693 Außenraum-Textdateien wurden gelesen.','status':'BESTAETIGT_MIT_SCOPE_ABER_IRREFUEHREND_OHNE_KONTEXT','finding':'Technisch stimmt der gefilterte Zähler. 4.296.955 davon stammen allein aus /root/zensi und sind stark durch generierte/gespiegelte Massenkörper geprägt.','action':'Nicht als Millionen unabhängiger Sprachquellen darstellen.'},
 {'claim':'Null Lesefehler.','status':'BESTAETIGT_NUR_TECHNISCH','finding':'Die Scanner meldeten null Exceptions. Das beweist weder korrekte Sprecherzuordnung noch semantische Vollständigkeit.','action':'Nur als null Scanner-Ausnahmen bezeichnen.'},
 {'claim':'2.884 direkte Nachrichten von Daniel aus Claude, Codex und Zensi.','status':'VERWORFEN','finding':'Zensi war nie direkt im Einsatz. Außerdem enthielt der Korpus automatische und eingefügte Datensätze.','action':'Frühere Zahl vollständig außer Kraft setzen.'},
 {'claim':'2.440 direkte Nachrichten von Daniel aus Claude und Codex.','status':'HERABGESTUFT','finding':'Es sind 2.440 deduplizierte Userrollen-Textdatensätze im alten Heuristiklauf. Darunter automatische Taskmeldungen, Kompaktzusammenfassungen und eingefügtes Material.','action':'Nur konservativ klassifizierten Korpus verwenden.'},
 {'claim':'Dutzende Claude-Code-Sitzungen mit mehreren Dateien über 20 MB.','status':'VERWORFEN','finding':'Aktuelle Messung: genau eine Claude-Datei und eine Codex-Datei sind größer als 20 MiB. Dutzende Sitzungen existieren, aber nicht mehrere Dutzend Großdateien.','action':'Aussage nicht weiterverwenden.'},
 {'claim':'Frühe AI-Gesprächssammlung etwa 3,3 MB.','status':'BESTAETIGT','finding':'87 Dateien mit zusammen 3.239.445 Byte.','action':'Als ungefähr 3,24 MB beziehungsweise 3,09 MiB angeben.'},
 {'claim':'Ein 250-Seiten-Kimi-Körper.','status':'UNKLAR','finding':'Die Zeichenfolge 250seiter steht im Dateinamen. Seiten wurden nicht unabhängig nachgezählt.','action':'Nur sagen: Datei trägt 250 Seiten im Namen.'},
 {'claim':'Sieben frühe Flextrawurst-Visionen.','status':'BESTAETIGT_MIT_SCOPE','finding':'Eine explizite Reihe V1 bis V7 existiert. Daneben gibt es weitere relevante Visionstexte und zusätzliche V1-benannte Dateien.','action':'Als V1-bis-V7-Reihe bezeichnen, nicht als gesamten Visionbestand.'},
 {'claim':'Zensi-Userfelder seien direkte Daniel-Nachrichten.','status':'VERWORFEN','finding':'Daniel stellte ausdrücklich klar, dass Zensi nie direkt eingesetzt wurde.','action':'Zensi nur als importierte, gespiegelte, generierte oder ungeklärte Schicht behandeln.'},
 {'claim':'Datenbankangabe Angelegt von X beweise, dass Wesen X den Namen erfand.','status':'HERABGESTUFT','finding':'Das Feld belegt nur eine gespeicherte Attribution im System. Es beweist weder reale autonome Handlung noch sprachliche Ersturheberschaft.','action':'Existenz und gespeicherte Attribution getrennt berichten.'},
 {'claim':'Grellader, Stillgift, Gesternöl und andere seien Daniels Wörter.','status':'UNKLAR','finding':'Ihre Existenz im Katalog ist bestätigt. Daniels alleinige Urheberschaft ist ohne älteren Ursprungskörper nicht belegt.','action':'Als Weltwörter mit ungeklärter Urheberschaft führen.'},
 {'claim':'Metamonster sei ein aktuelles Daniel-Fundstück.','status':'BESTAETIGT','finding':'Daniel bezeichnete sich im aktuellen Auftrag selbst als Metamonster.','action':'Direkte Fundstelle erhalten; Bedeutung noch nicht überdehnen.'},
 {'claim':'Wortlike sei eine bewusste Daniel-Wortschöpfung.','status':'UNKLAR','finding':'Wortlike steht in Daniels aktueller typo-reicher Nachricht. Bewusste Setzung, Tippfehler oder spontaner Fehlerkeim ist nicht geklärt.','action':'Nur als Rohfund/Fehlerkeim führen.'},
 {'claim':'Livesupport sei direkt von Daniel verwendet worden.','status':'BESTAETIGT','finding':'Im frühen GPT-5-Dialog sagt Daniel selbst, es gehe um eine Art livesupport. Das Wort ist jedoch allgemeinsprachlich und nicht automatisch Daniels Neuschöpfung.','action':'Direkte Verwendung von Urheberschaft unterscheiden.'},
 {'claim':'Ideenmonstrum und organisch wachsendes Ideenkonstrukt seien Daniels frühe Formulierungen.','status':'BESTAETIGT','finding':'Beide stehen direkt in Daniels Eingabe am Beginn des V1-Dialogs.','action':'Als starke Daniel-Sprachspur aufnehmen.'},
 {'claim':'Bildhauen sei Daniels Begriff.','status':'BESTAETIGT_STARK','finding':'Daniel schreibt explizites bildhauen; Kimi antwortet danach Das Bildhauen, wie du es nennst.','action':'Als starke Daniel-Prägung führen.'},
 {'claim':'Stundenverlaufssystemwesen und Formfadenprompts seien Daniels Formulierungen.','status':'BESTAETIGT_STARK','finding':'Daniel verwendet beide direkt in seinem frühen Kimi-Dialog.','action':'Als starke Daniel-Spur führen; genaue Schreibvarianten erhalten.'},
 {'claim':'Robotermodus sei allein von Daniel erfunden.','status':'HERABGESTUFT_ZU_GEMEINSAMER_ENTSTEHUNG','finding':'Die AI sprach zuvor vom Maschinenmodus. Daniel setzte danach konkret Wenn eher so... robotermodus wurde ausgelöst; die AI übernahm und systematisierte es.','action':'Gemeinsame Entstehung, konkrete Schlüsselformulierung durch Daniel.'},
 {'claim':'Punktbühne sei sicher Daniels Wort.','status':'UNKLAR','finding':'Punktbühne steht im konsolidierten Formfadenprompt, aber im bisher gelesenen früheren Dialog wurde die Geburt nicht gefunden.','action':'Keine Urheberschaft behaupten.'},
 {'claim':'Forschungssnack sei sicher Daniels Wort.','status':'UNKLAR_GEMEINSAM_MOEGLICH','finding':'Der Begriff ist im gemeinsam gewachsenen Stundenkörper häufig. Die früheste Sprecherstelle wurde noch nicht sicher identifiziert.','action':'Gemeinsam/unklar bis Ursprung gelesen ist.'},
 {'claim':'NULLSTUNDEN sei sicher Daniels Wort.','status':'UNKLAR','finding':'Der Begriff ist als Dateiname und späterer Systemkörper belegt. Der Dateiname allein beweist die Geburt nicht.','action':'Ursprung offenlassen.'},
 {'claim':'ChatGPT.com sei vollständig nach allen jemals vorhandenen Sessions durchsucht worden.','status':'NICHT_BEHAUPTBAR','finding':'Erreichbare Bibliotheks-/Gesprächsdateien und VPS-Exporte wurden durchsucht. Eine vollständige Kontoweitsuche ist technisch nicht belegt.','action':'Reichweite immer ausdrücklich begrenzen.'},
]
write_json('01_BEHAUPTUNGSMATRIX.json',{'created_utc':NOW,'claims':claims})

md=['# Halluzinationsaudit der Metamonster-Wortsuche','',f'Erstellt UTC: `{NOW}`','',
'## Ergebnis in einem Satz','',
'Die Dateimessungen waren überwiegend real, aber mehrere sprachliche Schlussfolgerungen waren zu stark: Dateizahl wurde mit Quellenzahl verwechselt, Userrollen-Datensätze mit Daniels eigener Formulierung, gespeicherte Attribution mit Urheberschaft und konsolidierte Systemtexte mit Geburtssituationen.','',
'## Konservativer Userrollen-Korpus','',
f'- Userrollen-Textdatensätze insgesamt: `{len(rows)}`',
]
for k,v in sorted(counts.items()): md.append(f'- `{k}`: `{v}`')
md += ['', '### Nach Provider','']
for provider,c in provider_counts.items():
    md.append(f'- **{provider}:** '+', '.join(f'`{k}={v}`' for k,v in sorted(c.items())))
md += ['', '> Auch die Klasse `WAHRSCHEINLICH_AKTUELLE_MENSCHLICHE_EINGABE` beweist nur, dass Daniel den Text wahrscheinlich aktuell übermittelt hat. Sie beweist nicht, dass jedes enthaltene Wort von ihm erfunden wurde.', '', '## Korrigierte Hauptpunkte','']
for c in claims:
    md.append(f"### {c['claim']}\n\n- **Status:** `{c['status']}`\n- **Befund:** {c['finding']}\n- **Folge:** {c['action']}\n")
md += ['## Navigation','','- [[entstehungsverlauf/halluzinationsaudit/00_AUDITREGELN|Auditregeln]]','- [[entstehungsverlauf/halluzinationsaudit/05_WORT_HERKUNFTSAUDIT|Wort-Herkunftsaudit]]','- [[entstehungsverlauf/halluzinationsaudit/07_QUELLEN_MIT_AI_HALLUZINATIONEN|Alte Quellen mit AI-Halluzinationen]]','- [[HOME|Vault Home]]']
write_text('02_HALLUZINATIONSAUDIT.md','\n'.join(md))

wordaudit='''# Wort-Herkunftsaudit

## Stark belegt als direkte Daniel-Sprachspur

| Ausdruck | Status | kleinste derzeitige Begründung |
|---|---|---|
| Metamonster | bestätigt, aktuell | Daniel nennt sich im Auftrag selbst „Metamonster“. |
| Ideenmonstrum | bestätigt | Steht direkt in Daniels früher Eingabe am Beginn des V1-Dialogs. |
| organisch wachsendes Ideenkonstrukt | bestätigt | Steht direkt im selben frühen Daniel-Beitrag. |
| Bildhauen | stark bestätigt | Daniel schreibt „explizites bildhauen“; Kimi antwortet „wie du es nennst“. |
| Stundenverlaufssystemwesen | stark bestätigt | Direkte Daniel-Formulierung im frühen Kimi-Dialog. |
| Formfadenprompts / formfadenpromts | stark bestätigt | Direkte Daniel-Formulierung im selben Beitrag. |
| Symbositierung | stark bestätigt | Daniel erklärt im aktuellen Projekt selbst: Mischung aus Symbiose und Mutation. |
| Verdeutschen, in der hier gesetzten Bedeutung | bestätigt | Daniel definiert ausdrücklich freiwillige Übernahme nach Verstehen der Tragweite. |

## Belegt als gemeinsame oder geschichtete Entstehung

| Ausdruck | Status | Befund |
|---|---|---|
| Robotermodus | gemeinsam entstanden | AI schlug „Maschinenmodus“ vor; Daniel setzte konkret „robotermodus wurde ausgelöst“; AI systematisierte es. |
| Formfadenprompt als fertiger Körper | gemeinsam gewachsen | Daniel benannte und steuerte das System, der konsolidierte Text enthält umfangreiche AI-Formulierungen. |
| WorldWORDS ANTIBIBEL | aktuelle Projektsetzung | Der Zielpfad stammt aus Daniels Auftrag; Auslegung und Systematisierung wurden gemeinsam gebaut. |

## Vorläufig ungeklärt

| Ausdruck | Warum nicht kanonisiert |
|---|---|
| Wortlike | Aktueller Rohfund, aber Absicht versus Tippfehler ungeklärt. |
| Punktbühne | Im Endprompt vorhanden, Geburtssituation noch nicht gefunden. |
| Forschungssnack | Häufig im gemeinsamen Stundenkörper, frühester Sprecher noch nicht sicher. |
| NULLSTUNDEN | Dateiname und Körper vorhanden, Ursprung nicht belegt. |
| Grellader, Stillgift, Gesternöl, Klammerhonig, Staubmilch, Thronöl, Blendhonig | Existenz im Weltkatalog bestätigt; Urheberschaft offen. |
| von Codewesen benannte Räume | Datenbank speichert „Angelegt von“, doch das ist keine sichere sprachliche Ersturheberschaft. |

## Grundsatz

Ein Ausdruck darf zugleich Daniels Idee, AI-Formulierung, gemeinsam verändertes Wort und späterer Systemname sein. Der Audit zwingt diese Schichten nicht künstlich zu einem einzigen Urheber zusammen.
'''
write_text('05_WORT_HERKUNFTSAUDIT.md',wordaudit)

oldsource='''# Alte Quellen mit möglichen oder offensichtlichen AI-Halluzinationen

Die frühen Gesprächsarchive sind wertvolle Herkunftskörper, aber keine verlässlichen Sachlexika. AI-Antworten darin enthalten erfundene oder mindestens unbelegte Studien, URLs, Prozentwerte und Selbstbeschreibungen.

## Beispiele aus dem Stundenverlauf

Quelle:

`/root/werkraum/Meine-Textsammlung-erfahrun-frh-mit-ai/mein stundenverlaufssystemwesen durch formfadenpromt/stunde 47 bis 51.md`

Darin erscheinen unter anderem:

- eine angebliche Uni-Wien-Studie zu rund 200 „Micro-Ritualen“ mit einer zweifelhaften URL,
- eine angebliche TU-München-Umfrage, nach der 44 Prozent Dinge rückwärts tun,
- eine angebliche Uni-Bern-Angabe von 23 Prozent Kreativitätssteigerung,
- eine angebliche Oxford-Studie mit 30 Prozent vollständiger Aufmerksamkeit,
- erfundene interne AI-Fehlerquoten wie ein „System-Redundancy-Loop“ mit 31 Prozent.

## Auditstatus

`UNVERIFIZIERTE_ODER_OFFENSICHTLICH_MODELLGENERIERTE_SACHBEHAUPTUNGEN`

Diese Aussagen werden:

- nicht als wissenschaftliche Quellen verwendet,
- nicht als Belege für reale AI-Innenzustände verwendet,
- nicht zur Bestimmung von Daniels Worturheberschaft benutzt,
- nur als historische Bestandteile eines gemeinsam erzeugten Gesprächskörpers erhalten.

## Weitere Risikoklasse

Wenn ein alter Export AI-„Thinking“, Zusammenfassungen oder Tabellen enthält, können darin Deutungen über Daniel stehen, die Daniel später ausdrücklich korrigiert hat. Solche Deutungen sind keine Fakten über Daniel. Sie bleiben höchstens Belege dafür, was das damalige Modell behauptete.
'''
write_text('07_QUELLEN_MIT_AI_HALLUZINATIONEN.md',oldsource)

superseded='''# Herabgestufte und verworfene Aussagen

Die folgenden früheren Formulierungen dürfen nicht mehr als aktueller Befund verwendet werden:

1. „3,8-GB-Sprachbiotop“ als Beschreibung des VPS.
2. „2.884 direkte Daniel-Nachrichten“ einschließlich Zensi.
3. „2.440 direkte Daniel-Nachrichten“ ohne Trennung automatischer, eingefügter und menschlicher Userrollen-Texte.
4. Zensi sei jemals direkt von Daniel benutzt worden.
5. `role=user`, `mensch` oder `Angelegt von` beweise Urheberschaft.
6. Dutzende Claude-/Codex-Großdateien über 20 MB.
7. Dateinamen wie „250seiter“ oder „227 Seiten“ seien nachgezählte Seitenumfänge.
8. Ein Rohkandidat aus einem Scanner sei bereits ein Daniel-WorldWORD.
9. Null Scannerfehler bedeute vollständige oder inhaltlich korrekte Erfassung.
10. Die erreichbare ChatGPT-Bibliothek entspreche allen jemals vorhandenen ChatGPT-Sessions.

Maschinenlesbare Einzelbefunde stehen in `01_BEHAUPTUNGSMATRIX.json`.
'''
write_text('06_VERALTETE_ODER_HERABGESTUFTE_AUSSAGEN.md',superseded)

print(json.dumps({'ok':True,'created_utc':NOW,'records':len(rows),'categories':dict(counts),'providers':provider_counts},ensure_ascii=False,indent=2))
