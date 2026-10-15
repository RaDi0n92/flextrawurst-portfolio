# BAU- UND TESTPROTOKOLL · 2026-09-02

## Ausgangslage

Die am 2026-08-19 gebaute Spiel-Werkstatt existierte am 2026-09-02 weiterhin real und lief als `flextrawurst-spiel-werkstatt.service` auf `127.0.0.1:18119`.

Die Godot-World-Bridge antwortete real auf `127.0.0.1:18092/health` mit Status `ok` und Cursor 78.

Der alte Spiel-`truth_engine` war nicht gesund und durfte deshalb nicht zur heutigen Wahrheitsautorität erhoben werden:

- Status: `degraded_last_good_preserved`
- letzte erfolgreiche Generation: 2026-07-26
- Fehler: Obsidian-Validierung
- Ursache im aktuellen Validator: alte/bereits gebrochene Wikilinks in Zeitstrom-/Validierungsreferenzen

Das Mandat `LEBENDES_SPIELGEDAECHTNIS` existiert weiterhin. Ein fertiger spezialisierter Spielgedächtnis-Gesamtkörper bzw. ein fertiger Multi-AI-Kontextinjektor wurde im Bestand nicht gefunden.

## Neu gebaut

### 1. Quellenregister

`CURRENT_CONTEXT_SOURCES.json`

Der erste Bestand umfasst 15 gezielt ausgewählte Quellen:

- 6 `AKTUELL`
- 6 `ARBEIT`
- 3 `HISTORISCH`

Jede Quelle besitzt ID, Titel, Schicht, Typ, Tags und echten Quellpfad. Die Werkstatt ergänzt live Dateiexistenz, Größe, mtime und SHA-256.

Wichtig: Ein Retrieval-Treffer wird **nicht** automatisch Kanon oder aktuelle Wahrheit.

### 2. Ausführbare Kontextnaht

Neu:

`/root/werkraum/engine/godot-vertical-slice/workshop_20260819/current_context.py`

Neue API:

`GET /api/context?q=<frage>&layer=<optional>&limit=<optional>`

Sie durchsucht das kuratierte Quellenregister **und den aktuell gespeicherten gemeinsamen Werkstatt-Spielkörper**. Registrierte Dateien werden nach Titel/Tags/Inhalt bewertet; gespeicherte Spielkörper nach aktueller ID, Titel, Typ und aktuellem Snapshot.

Ergebnisse tragen je nach Herkunft:

- Schicht
- Quelltyp
- Herkunftspfad + SHA-256 bei Dateien
- Objekt-ID + aktuelle Version + Snapshot-SHA + Speicher-Akteur bei Werkstatt-Spielkörpern
- Trefferbegriffe
- Score
- Kontextausschnitt

Offene Arbeitszustände und geschützte Entwürfe werden bewusst **nicht** automatisch eingespeist, weil sie laut Werkstattvertrag noch keine Weltwirkung besitzen.

Das ist die erste **ausführbare** Umsetzung des alten Kontextinjektor-Gedankens, bei der ein reales Werkstatt-Speichern direkt den später abrufbaren aktuellen Kontext verändern kann. Es ist ausdrücklich noch kein vollautomatisch an alle AI-Ströme angeschlossener Gesamtinjektor.

### 3. Aktuelle-Wahrheit-API

Neu:

`GET /api/current-truth`

Sie liefert live:

- Schichtdefinitionen `AKTUELL / ARBEIT / HISTORISCH`
- registrierte Quellen samt Hash/Existenz
- aktuellen Werkstattzustand
- Status des alten `truth_engine`
- Status des noch unfertigen Spielgedächtnis-Mandats
- Status der neuen Kontext-API
- Warnungen, insbesondere wenn der Alt-Truth-Engine degradiert ist

### 4. Werkstatt-Oberfläche

Die bestehende Werkstatt bekam **eine** neue Ansicht:

`Aktuelle Wahrheit`

Dort sind nun sichtbar:

- die drei Schichten
- Systemzustände
- Warnungen
- Quellen pro Schicht
- direkte Öffnung realer Quelldateien
- Kontextsuche über den kuratierten Bestand
- optionaler Filter auf eine einzelne Schicht

Es wurde bewusst kein zweiter Editor und kein konkurrierender neuer Wahrheitsapparat gebaut.

## Tests

### Syntax

- `python3 -m py_compile current_context.py server.py` → PASS
- `node --check app.js` → PASS

### Isolierter API-Test auf Port 18120

PASS.

Retrieval-Gegenproben:

- `Casino Zeit` → aktuelle Casino-Verträge **und** ARBEIT-Spielsprachen werden getrennt zurückgegeben.
- `Ghostwriter Flarum` → Ghostwriter-Quelle als `ARBEIT`.
- `v21 Prototypen` → Engine-/Prototypen-Archäologie als `HISTORISCH`.
- `layer=AKTUELL` → ausschließlich aktuelle Quellen.

### Bestehender Browser-Smoke

`test_ui_smoke.mjs`

Ergebnis:

`PASS UI smoke: selection/tabs/workspace/discard/files/3D-truth-status`

Dieser Test erzeugt absichtlich einen Arbeitszustand und verwirft ihn wieder; die Auditspur bleibt im Werkstatt-Ereignisstrom erhalten.

### Neuer Browser-Test

`test_truth_context.mjs`

Geprüft:

1. Seite lädt in Chromium.
2. `Aktuelle Wahrheit` ist real bedienbar.
3. `AKTUELL`, `ARBEIT`, `HISTORISCH` erscheinen.
4. degradierter Alt-Truth-Engine wird sichtbar und nicht versteckt.
5. Ghostwriter-Suche liefert `ARBEIT`.
6. v21-Suche liefert `HISTORISCH`.
7. Eine registrierte Quelle wird über die UI real geöffnet und gelesen.
8. `Gordslider` wird zusätzlich als aktuell gespeicherter Werkstatt-Spielkörper gefunden.
9. Der Kontexttreffer springt direkt zurück in dieselbe Objekt-ID `OBJEKT_GORDSLIDER_0001`.

Ergebnis:

`PASS truth/context UI: layers/live-warning/retrieval/source-open/current-object-open`

### Kontextzyklus Save → nächster Abruf

Isolierter Test mit eigener Test-Runtime unter dem ignorierten Werkstatt-Tempbaum:

1. Arbeitszustand erhält eindeutigen neuen Wert `KONTEXTZYKLUS_9F31A7`.
2. Vor dem Speichern liefert `/api/context` **keinen** aktuellen Werkstatt-Spielkörper für diesen Wert.
3. Explizites Speichern erzeugt Version 2 im isolierten Spielkörper.
4. Unmittelbar danach liefert `/api/context` denselben Spielkörper als `AKTUELL` mit Objekt-ID, Version, Speicher-Akteur und Snapshot-SHA.
5. Ein geschützter Entwurf mit eigenem eindeutigen Marker bleibt aus dem Kontextabruf ausgeschlossen.

Ergebnis:

`PASS context cycle: unsaved hidden -> save searchable -> protected draft excluded`

Damit ist erstmals real bewiesen:

`Werkstatt-Arbeitszustand → bewusst speichern → aktueller gemeinsamer Spielkörper → ohne manuelles Reindexieren im Kontextabruf sichtbar`

### Legacy-Watchdog von UI-Testmüll entkoppelt

Der alte Truth-Watchdog beobachtete vorher den gesamten Godot-Baum und reagierte dadurch auch auf Chromium-/Playwright-Cache- und LevelDB-Dateien unter der Werkstatt-Test-Runtime.

In der bereits vorhandenen `ignored_prefixes`-Konfiguration wurde deshalb **nur** folgender ephemerer Pfad ergänzt:

`/root/werkraum/engine/godot-vertical-slice/workshop_20260819/runtime/tmp`

Echte Werkstatt-Quelldateien wie `server.py` bleiben ausdrücklich beobachtbar.

Prüfung der Ignore-Grenze:

`PASS ignore boundary: True False`

Danach wurde `flextrawurst-3d-truth-watchdog.service` neu gestartet. Ein echtes Testfile wurde im ignorierten Tempbaum erzeugt und wieder gelöscht. Anzahl der Pipeline-Aufrufe vorher/nachher:

`265 → 265`

Ergebnis:

`PASS: ignored temp create/delete caused no pipeline invocation`

Der Legacy-Truth-Engine bleibt unabhängig davon wegen seiner alten Obsidian-Wikilinkfehler degradiert. Diese Entkopplung behebt nur den sinnlosen Testdatei-Trigger und behauptet keine Reparatur des alten Wahrheitskörpers.

## Produktionsumschaltung

`flextrawurst-spiel-werkstatt.service` wurde nach erfolgreichen Syntax-/Isoliertests neu gestartet.

Nach Neustart:

- `active (running)`
- neuer Prozess nutzt Werkstattserver v0.2
- `/api/current-truth` antwortet HTTP 200
- 15 registrierte Quellen vorhanden (`6 AKTUELL / 6 ARBEIT / 3 HISTORISCH`)
- gespeicherte Werkstatt-Spielkörper werden zusätzlich dynamisch als `AKTUELL` in `/api/context` einbezogen
- einzige aktuelle Registerwarnung: degradierter alter `truth_engine`

## Offene Grenze

Noch **nicht** gebaut/behauptet:

- kein vollständiger automatischer Multi-AI-Kontextinjektor
- keine automatische Supersession-Entscheidung zwischen widersprüchlichen Quellen
- keine vollständige Migration sämtlicher Spielbestände in Werkstatt-Identitäten
- kein neuer Godot-Webexport
- alte Truth-Engine-Wikilinkfehler noch nicht repariert

Der heutige Fortschritt ist die reale Verbindung:

`Werkstatt → Schichtentrennung → echte Quellen + gespeicherter aktueller Spielkörper → Kontextabruf → Herkunft/Version/Hash → zurück zur selben Spielidentität`

und nicht ein weiterer Plantext über diese Verbindung.
