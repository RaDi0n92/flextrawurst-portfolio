# 01 · Realitätsbefund · was heute wirklich da ist

Stand: 2026-09-04 · **datierter Snapshot, keine dauerhaft aktuelle Wahrheit.** Zahlen, Dienste, Sessions und UI-Zustände vor späterer Verwendung neu prüfen.

Die hier genannten Streamoptionen/Labels beschreiben an mehreren Stellen nur die **damals sichtbare UI/Registry**, nicht automatisch echte Stromidentitäten. Insbesondere Gemgem ≠ Gravityy und Claude Code ≠ Anthropic_Claude ≠ Haiku.

## Bestätigt · Live-Planer über Playwright/CDP

Echte laufende URL: `https://flextrawurst.de/Mein-Gesamtkonstrukt-planer/`

Playwright hing sich read-only an den bereits offenen Chromium über CDP `127.0.0.1:9222` und las den echten vorhandenen Planer-Tab. Kein statischer HTML-Ersatz.

Live-Befund bei Viewport `932 × 471`:

- Titel: `Mein Gesamtkonstrukt · Server`
- Serverstand sichtbar: `SERVER · einzige Wahrheit · Stand s791`
- Arbeitsrevision: `r5`
- 53 Objekte
- 44 Kanten
- 0 Vorschläge
- 73 Rückmeldungen im eingebetteten Arbeitsstand
- aktiver Stream im Dropdown: Claude Code
- Streamoptionen: Claude Code, ChatGPT / Codex, Gemini, GLM
- klassische Hauptansichten: Start, Canvas, Netz, Plan, Zeitspur, Replicas
- zusätzliche Arbeitsöffner: Notiz hier, Ordner & Dateien, Gemeinsame Arbeit, Betriebssystem, Telefon prüfen, Start hier, Echte Pfade
- Arbeitsobjekt-Typen reichen von Gesamtkonstrukt/Aufgabe/System/Dienst/Ablauf/Automation bis Agent/LLM/Mensch/Werkzeug/Dokument/Prompt usw.
- Zustandsfilter aktuell nur grob: vorhanden/bestätigt, Modell/Darstellung, noch nicht gebaut, kommt nicht weiter.

### Sichtbarer UI-Druck

Bei 932px Viewport lagen Buttons der oberen Werkzeugreihe laut DOM-Geometrie bis über `x=2111`. Mehrere Bedienelemente existieren also real weit außerhalb des sichtbaren Viewports. Das ist kein moralischer Fehler, sondern ein guter Beleg für den gewachsenen Bedienpultcharakter: viele echte Fähigkeiten sind vorhanden, aber sie konkurrieren um dieselbe flache Oberfläche.

**Designfolgerung, nicht Tatsachenbehauptung:** Der Schrottplatz darf diese Funktionen nicht einfach als dieselben Buttons auf braunem Blech nachbauen. Er muss räumliche Nähe, Zustand, Handlung und Bedeutung benutzen, um Informationsdruck abzubauen.

Playwright-Spuren:
- `../01_zelt_spuren/planer_live_20260904.png`
- `../01_zelt_spuren/planer_live_20260904.json`

## Bestätigt · vorhandene Graph-/Arbeitskörper

`server/replica_registry.js` unterscheidet bereits mehrere Schichten statt eines einzigen Graphbreis:

- Struktur
- Beziehungen
- Abläufe
- Ereignisse
- Vorschläge
- Annotationen

`relations` und `containment` sind bereits getrennte Bedeutungen. Das ist wichtig: rote Fäden müssen nicht dieselbe Sache sein wie räumliches/strukturelles Enthaltensein.

Die 17 Replica-Werkstätten existieren bereits als unterscheidbare Funktionskörper. Für den Schrottplatz sind sie laut aktueller Vision **kein Haufen je Werkstatt**, sondern kleines Material / Zähne / Arbeitsweisen zwischen großen Haufen.

### Reales `current.json` am 04.09.2026

Direkt geparst, nicht aus UI-Zähltext geraten:

- 53 Objekte
- 44 Kanten
- 120 Ereignisse
- 73 Feedback-Einträge
- 6 Versionen
- 0 Vorschläge

Aktuell tatsächlich benutzte Objekt-`kind`s:
- `document` 35
- `artifact` 7
- `idea` 4
- `automation` 2
- `output` 2
- `project` 1
- `workflow` 1
- `marker` 1

Die Settings kennen deutlich mehr mögliche Typen als derzeit real benutzt werden, u.a. `task`, `reference`, `system`, `service`, `agent`, `llm`, `human`, `tool`, `concept`, `prompt`, `decision`, `question`. Das ist wichtig: **konfigurierbarer Typbestand ≠ tatsächlich vorhandene Weltpopulation.**

Aktuelle Truth-Verteilung:
- `real` 42
- `geplant` 10
- `modelliert` 1

Aktuelle Work-Verteilung:
- `roh` 50
- `entwurf` 2
- `aktiv` 1

Die Settings kennen zusätzlich `bereit` und `archiv`; `blockiert` existiert als Truth-State. Diese groben Felder reichen nicht, um Lauf-/Warte-/Review-/Delegationszustände auszudrücken.

### Reale Kantentypen im jetzigen Bestand

- `enthält` 27
- `hat Skizzenelement` 7
- `hat Werkstattoperation` 6
- `hat Notiz` 2
- `wird geprüft durch` 1
- `wartet auf Freigabe nach` 1

Besonders wichtig: **Review und Freigabeabhängigkeit existieren also bereits als echte semantische Kanten**, nicht nur als neue Theorie dieses Dokuments.

Konkrete Beispiele:
- Ablaufkörper `Ablauf entwerfen · Mein Gesamtkonstrukt` → `wird geprüft durch` → `Browser Test`
- Automation `Regel · Datei-Umzug braucht Freigabe` → `wartet auf Freigabe nach` → `Browser Test`

### Reale Events sind mengenmäßig da, semantisch aber flach

Alle 120 aktuellen `state.events` sind vom Typ `workspace.file` und Quelle `werkraum`.

Beispielstruktur:
```json
{
  "id": "...",
  "at": "...",
  "type": "workspace.file",
  "title": "Werkraum: Datei angelegt: ...",
  "source": "werkraum"
}
```

Das reicht als Aktivitätschronik für Dateioperationen, aber nicht als allgemeine Weltaktion: Akteur, Goal, Zielkonstrukt, Zwischenphase, Wartegrund, Resultat und Belegbezug fehlen.

### Feedback ist bereits eigener Zustandsträger

73 Feedbacks:
- 39 `open`
- 34 `resolved`

Typen:
- `unklar` 43
- `fehlt` 18
- `kaputt` 8
- `zu_viel` 3
- `falsch` 1

Das ist relevant für Review: **Kritik/Prüfung muss nicht als neues Universalformat erfunden werden.** Ein Teil davon existiert bereits als eigener Körper, nur noch nicht sauber in Goal-/Run-/Eventphysik eingebunden.

## Bestätigt · Ereignisloch am 04.09. teilweise geschlossen

`server/planner_events_stream.py` liefert weiterhin bewusst nur:

```json
{"serverRevision": N}
```

Das bleibt der **Klingeldraht**. `server/live_stream.js` muss nicht den gesamten semantischen Vorgang über SSE transportieren.

Neu gebaut:
- `server/world_state.py`
- kanonische `worldEvents` als bounded Ring im bestehenden `current.json`
- gleiche `.state.lock`-Transaktionsgrenze wie der Planer
- atomarer Statewrite + Hash + genau ein `serverRevision`-Schritt pro kanonischer Weltmutation
- optionales NDJSON als rebuildbare Zusatzprovenienz, nicht zweite Wahrheit

Neu erzeugbare semantische Weltpulse u.a.:
- `run.created`
- `run.transitioned`
- `world.connection.added/removed`
- `approval.requested/stale/approved/rejected`
- `effect.confirmed/failed`

Damit schreibt `real_fs_api.py` seine dauerhaften Approval-/Effect-Folgen inzwischen **in denselben Welt-Takt**, während der native Pending-/Backupkörper seine eigene Detailwahrheit behält.

Weiter offen ist die breite Adapterseite: Claude/Codex/Antigravity/GPT/Atlas/Prozesse sind noch nicht automatisch als gemeinsame semantische Weltaktionen normalisiert.

## Bestätigt · reale Wartezustände sind jetzt feiner als `pending → approved`

`real_fs` trägt heute getrennt:

```text
approvalStatus = pending | approved | rejected
effectStatus   = not_started | running | stale | confirmed | failed | unknown
```

Dazu kommt optional die Korrelation zu Run/Node/Goal.

Die Lauf-Linse projiziert korrelierte offene Freigaben als **action-level Warten**. Der ganze Run wird dadurch absichtlich **nicht** automatisch auf `waiting` gesetzt.

Das ist die erste real gebaute Instanz der Regel:

> Wartezustand braucht Scope.

## Bestätigt · mehrere Spurkörper existieren bereits und haben verschiedene Aufgaben

### `data/ai_spuren.json` · interpretierte Arbeits-/Reviewspuren

Stand 02.09.2026:
- SchemaVersion 1
- 36 Einträge
- Felder: `id, at, author, kind, title, note, objectIds, filePaths, status`
- Autoren: 20× Claude Code, 10× Codex, 3× ChatGPT, 3× Codex · VPS-Desktop
- Arten: 22× Entscheidung, 5× `pruefung`, 3× Beobachtung, 2× Frage, je 1× `prüfung`, Folgepunkt, `übergabe`, `uebergabe`
- alle 36 aktuell `status = offen`
- 27/36 verlinken mindestens eine Datei; nur 5/36 mindestens eine Planerobjekt-ID

Das ist also **kein Eventlog und kein fertiger Lifecycle**. Es ist ein bestehender, menschenlesbarer Interpretations-/Entscheidungs-/Prüfkörper mit realen Quellenverweisen. Die doppelten Schreibweisen `pruefung/prüfung`, `uebergabe/übergabe` und `alles offen` zeigen: Semantik ist organisch gewachsen und noch nicht normalisiert.

Wichtiger realer Korrekturfall darin:
Ein Prüfeintrag hatte wegen falschem Feldnamen zunächst **keinen Objektbezug**; der nächste Eintrag korrigiert genau diese verlorene Herkunft und hängt denselben Test bewusst an den realen Dokumentknoten. Das ist ein hervorragendes Beispiel dafür, dass auch Provenienz selbst korrigierbar/prüfbar sein muss.

### `BAULOG.ndjson` · revisionsgebundener Fahrtenschreiber

Stand 02.09.2026:
- 214 NDJSON-Zeilen
- jede Zeile: `at, serverRevision, action, details`
- aktuell `details` in den geprüften Einträgen leer
- Beginn bei Serverrevision 218, letzter Eintrag bei 791

Es protokolliert u.a.:
- Arbeitsobjekt übernehmen
- Dateien/Ordner anlegen
- Werkstattoperationen
- Gemeinsame-Arbeit-Einträge
- UI-/SSE-Tests

Das BAULOG ist damit ein **guter revisionsgebundener Fahrtenschreiber**, aber semantisch noch flach: Akteur, Goal, Zielkörper, Phase, Wartegrund und Beleg sind meist nur im `action`-Text indirekt oder gar nicht enthalten.

### `events/YYYY-MM-DD.ndjson` · Serverzustands-Snapshots als Ereignisse

`_append_event` schreibt bei gespeichertem Planerzustand zusätzlich ein strukturiertes `planner.state.saved` mit:
- Serverrevision + Vorgängerrevision
- State-Revision
- SHA256 des Zustands
- Objekt-/Kantenzahl
- offene/erledigte Feedbackzahl

Das ist stärker als der SSE-Stream, aber es beschreibt **den gespeicherten Gesamtzustand**, nicht die semantische Handlung, die ihn erzeugt hat.

### `state.events` · eingebettete Kurzchronik

`_store_workspace_state` erzeugt parallel einen `workspace.file`-Eintrag im aktuellen State und behält nur die letzten 120.

### Was daraus folgt

Eine einzige heutige Handlung kann bereits mehrere Artefakte hinterlassen:

```text
Gemeinsame Arbeit speichern
→ ai_spur (Interpretation/Entscheidung/Prüfung)
→ current.json state.events (kurze UI-Chronik)
→ planner.state.saved NDJSON (Zustandsbeweis + Hash/Revision)
→ BAULOG (menschlich lesbarer Fahrtenschreiber + Revision)
```

Diese Körper sind **nicht einfach Duplikate**. Die neue Weltphysik sollte sie über Referenzen/Correlation verbinden, statt einen fünften Log zu bauen und alles hineinzukopieren.

Arbeitsunterscheidung:
- **Ereignis** = was real passiert/umgeschaltet/ausgeführt wurde
- **Spur** = was ein Mensch/Strom darüber beobachtet, entschieden, gefragt, geprüft oder übergeben hat
- **Beleg** = welche reale Quelle die Behauptung stützt
- **State-Snapshot** = wie der kanonische Planerzustand danach aussah
- **Fahrtenschreiber** = welche revisionsgebundene Bauaktion gespeichert wurde

## Bestätigt · `gkos.koerper.v1` ist schon ein realer Ablaufkörper, nicht nur eine Idee

Der Code behandelt `gkos.koerper.v1` ausdrücklich als **eigenständiges Format mit eigener Logik**, absichtlich nicht als Alias für `state.objects/edges`.

Schema trägt heute:
- persistente `koerper-UUID`
- Titel
- Container-ID
- Replica-ID
- created/updated time
- `sequence.type = freeform | linear | loop`
- Startnode
- interne Nodes mit `id, kind, title, body, data, index`
- interne Edges mit `from, to, type`

Der Server validiert `linear` als echten unverzweigten Pfad und `loop` als echten, alle Nodes umfassenden geschlossenen Zyklus. `freeform` darf bewusst ohne Ablaufsinn existieren.

Sechs reale Körper existieren aktuell im gemeinsamen Baum, darunter:

**`Code-Loop-Test Stufe 2`**
```text
Schreiben → Testen → Reviewen
   ↑_____________________|
```
als echter `type=loop`.

Dazu existieren u.a.:
- linearer Ideenraum-Test
- freeform Organisations-Regressionskörper
- drei Körper im Claude-Posteingang, darunter ein echter Loop-Test

### Bestätigt · die Lauf-Lücke ist am 04.09. erstmals **separat** angebaut worden

`gkos.koerper.v1` modelliert weiterhin absichtlich nur **Strecke / Struktur**. Kein Runtime-Brei wurde in den Körper geschrieben.

Neu gebaut:
- `server/run_state.py`
- Schema `gkos.run.v0`
- `server/run_api.py`
- GET/POST `/api/runs/`
- POST `/api/runs/transition/`
- URL-Routing im echten Django-Projekt

Ein Run trägt aktuell u.a.:
- eigene persistente Run-ID + Run-Version
- `koerperRef`
- optional `goalRef`
- `scopeRefs`
- Actor/Instanz/Rolle, wenn tatsächlich gesetzt
- Phase `prepared | running | waiting | review | completed | failed | cancelled`
- `currentNodeRef`
- Iteration
- scoped `wait`
- Evidence-/native Event-Refs
- Handoff-Ref
- Zeitstempel

Wichtige geprüfte Regeln:
- gleicher Körper kann mehrere Runs haben
- stale Run-Version → `409` / keine Mutation
- terminaler Run startet nicht still wieder
- `waiting` braucht einen Grund
- unbekannte Zukunftsfelder im `current.json` überleben Run-Mutationen
- jeder kanonische Runübergang erhöht `serverRevision` exakt einmal

Aktueller Teststand dieses Durchgangs: **18 grüne Tests** über Weltzustand, Run-API, Real-FS-Store und Real-FS-HTTP-Lifecycle.

### Bestätigt · erste Lauf-Linse im Betriebssystem gebaut

`operating_shell.js` besitzt jetzt eine eigene `Läufe`-Linse:
- zeigt offene und historische Runs
- Körper / Goal / Node / Iteration
- aktuelle Akteursbindung oder ausdrücklich `keine Instanz gebunden`
- Run-Wartegrund
- Evidence-/native Spuranzahl
- Handoff
- korrelierte action-level Real-FS-Freigaben

In der Körperliste wird pro Körper die Zahl offener Runs gezeigt.

`Run vorbereiten` erzeugt nur einen `prepared`-Run:
- Startnode kommt aus dem **echten `gkos.koerper.v1.startNodeId`**, falls vorhanden
- kein AI-Akteur wird aus dem lokalen Browser-Streamdropdown erfunden
- die lokale Dropdownauswahl wird nur als `Bedienperspektive`, ausdrücklich nicht als Provenienz angezeigt

Der reale `Code-Loop-Test Stufe 2` liefert in der Körperliste nun bestätigt `startNodeId = n1`.

Produktionszustand blieb bei der serverseitigen Prüfung bewusst unverschmutzt: `serverRevision = 791`, `runs = 0`. Die neuen Runs in Tests existierten ausschließlich in Tempkopien.

## Bestätigt · Registry-Aktion ist heute oft nur **Vertrag**, nicht echte Capability

`server/replica_registry.js` beschreibt für jede der 17 Werkstätten sinnvolle Inputs, Aktionen, Outputs und Schichten. Das ist als Ziel-/Werkstattvertrag wertvoll.

Aber der aktuelle `runAction()` in `operating_shell.js` zeigt eine wichtige Wirklichkeitsgrenze:

- Sketch hat echte Sondersemantik für `Stift`, `Form`, `Pfeil` und `Gruppe`.
- nahezu alle anderen Registry-Aktionen laufen aktuell durch denselben generischen `replica-action`-Pfad.
- dieser legt eine Werkstattoperationsdatei an und schreibt u.a. sinngemäß, dass die Aktion bewusst ausgelöst wurde und ihre **konkrete Semantik schrittweise weitergebaut wird**.
- daraus entstehen Datei/Objekt/Kante, aber z.B. `Code → Ausführen` bedeutet heute dadurch **nicht automatisch, dass realer Code ausgeführt wurde**.

Das ist eine zentrale Abnahmeregel für `Möglichkeit`:

```text
Aktion im Registry-Vertrag
!= Button sichtbar
!= Handler vorhanden
!= semantische Kernhandlung implementiert
!= Handlung für diesen Akteur jetzt erlaubt
!= echte Wirkung eingetreten
```

Eine Welt darf deshalb nur das als tatsächlich benutzbare Liane darstellen, dessen Ausführungspfad und Wirkungstyp real belegt sind. Zielaktionen ohne echte Semantik dürfen als **geplant / im Bau / nur als Vertragszahn vorhanden** sichtbar sein, aber nicht als funktionierende Fähigkeit.

## Bestätigt · Arbeitsloop ist schon älter als der Schrottplatz

Im alten aktiven Arbeitskörper stand bereits sinngemäß die feste Folge:

`offen → live nachvollzogen → Fix gebaut → Playwright geprüft → Reload geprüft → 3× Redteam → Folgefeedback gespeichert → erledigt`

Der Bauauftrag verlangte nach echtem Fix zusätzlich die Frage nach natürlichen Konsequenzen: Zusammenhänge, Zustände, Regeln, Übergänge, Bedingungen und Weiterentwicklungen. Das ist bereits ein Proto-Agentic-Loop und keine neue Erfindung vom 04.09.

## Bestätigt · heutige Oberfläche und gewünschte Welt sind nicht identisch

Aktuell existieren Fenster, Tabs, Dropdowns, Objektlisten, Filter, Werkstatt-/Metadaten-/Verlauf-/Feedbackflächen und GKWindows. Sie sind wertvoll als direkte technische Bedienform.

Der Schrottplatz soll daneben denselben realen Unterbau anders erfahrbar machen. Er darf also **nicht** zum Skin des aktuellen Planers degenerieren.
