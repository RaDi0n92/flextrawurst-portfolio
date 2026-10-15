# Validierungsbericht: MCP-Parallel-Lesen und Zuhause-Körper


## Ablage- und Zeitidentität

- Kanonischer Validierungszeitpunkt: `2026-07-26T14:48:30Z` / `2026-07-26T16:48:30+02:00`
- Kanonischer Bericht: `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/mcp_parallel_reads_home/2026-07-26/20260726T144830Z__mcp_parallel_reads_home__VALIDIERUNGSBERICHT.md`
- Maschinenbeleg: `/root/werkraum/_gpt/mcp_arbeitskoerper/validation/mcp_parallel_reads_home/2026-07-26/20260726T144830Z__mcp_parallel_reads_home__RESULT.json`
- Frühere Ablage im Spiele-Traum-Projekt: **fachlich falsch**; am 26. Juli 2026 in den neutralen MCP-Arbeitskörper verschoben.
- Regel: Wiederholte Validierungen erzeugen neue zeitgestempelte Belegpaare. Sie überschreiben frühere Belege nicht.

## Ergebnis

Status: **BESTÄTIGT – produktiv aktiv**

Am 26. Juli 2026 wurde der produktive VPS-MCP so erweitert, dass explizit klassifizierte reine Leseaktionen derselben History-Session gleichzeitig laufen können. Potenziell mutierende oder nicht eindeutig lesende Werkzeuge behalten exklusive Session-Sperren.

Zusätzlich erhielt der MCP einen eigenen menschenlesbaren Zuhause-, Karten-, Arbeits-, Muster-, Fragen- und Übergabekörper.

## Ursprünglicher Fehler

Ein `assets.search` über breite Wurzeln hielt während seiner gesamten Laufzeit die exklusive Session-Sperre. Der Suchlauf der Session `chatgpt-20260726T111853Z-da60c147e0b0` dauerte ungefähr 49 Minuten. Weitere Aufrufe derselben Session-ID scheiterten währenddessen nach dem dreisekündigen Sperrtimeout.

Die Hash-History war nicht beschädigt. Der Fehler lag in der Kombination aus:

- exklusiver Sperre für alle Werkzeugtypen,
- ungebremstem rekursivem Suchlauf,
- vollständiger Pfadprüfung vor dem billigen Dateinamenvergleich,
- fehlendem Zeit- und Scanbudget.

## Gebaute Änderung

### Leser-Schreiber-Vertrag

- 58 explizit geprüfte Lese-Werkzeuge verwenden gemeinsame `LOCK_SH`-Sperren.
- Schreiben, Löschen, Shell, Dienste, Testläufe, Snapshot-Erzeugung und unklare Werkzeuge verwenden weiterhin exklusive `LOCK_EX`-Sperren.
- `session.end` bleibt exklusiv und wartet auf laufende Leser.
- Die append-only Hash-History serialisiert weiterhin jeden kurzen Ereignis-Anhang.

### Begrenzte rekursive Suche

`assets.search` besitzt jetzt:

- Standard-Zeitbudget 20 Sekunden, Maximum 120 Sekunden,
- Standard-Scanbudget 250.000 Dateien, Maximum 2.000.000,
- Deduplizierung überlappender Wurzeln,
- standardmäßiges Überspringen von Abhängigkeits- und Cacheordnern,
- Dateinamenvergleich vor vollständiger Pfadprüfung,
- ehrlichen Teilstatus mit Scanumfang und Abbruchgrund.

### MCP-Zuhause

Startpunkt: `/root/werkraum/_gpt/mcp_zuhause/START_HIER.md`

Weitere Primärdateien:

- `ZUHAUSE.md`
- `WERKRAUM_KARTE.md`
- `ARBEITSWEISE.md`
- `MUSTER.md`
- `FRAGEN.md`
- `BRIEF_AN_NAECHSTE_SESSION.md`
- `MANIFEST.json`

Protokoll: `/root/werkraum/_gpt/mcp_global_protocols/mcp_zuhause_v1.json`

`history_startup` liefert automatisch eine kompakte `mcp_zuhause`-Projektion. Der vollständige Textkörper wird nicht mechanisch bei jedem Start geladen.

## Prüfungen

### Isolierte Regression

Drei Tests bestanden:

1. Zwei gemeinsame Leser liefen gleichzeitig.
2. Eine exklusive Aktion wartete, bis beide Leser beendet waren.
3. Eine geschlossene Session blockierte einen neuen Leser und protokollierte den Versuch unter `system-audit`.

### Katalog- und Startprüfung

- `mcp.home` befindet sich im Serverkatalog auf Position 1.
- `history_startup` liefert `mcp_zuhause` mit Protokoll-ID `mcp.zuhause.v1`.
- Die Lese-Allowlist enthält nach Gegenprüfung 58 Werkzeuge.
- `zensi.sandbox_snapshot` wurde wegen seiner additiven Schreibwirkung ausdrücklich aus der Leserklasse entfernt.

### Reale Werkraumsuche

Eine vollständige Nichttreffer-Suche über `/root/werkraum` ergab:

- 26.057 geprüfte Dateien,
- 2.635 geprüfte Ordner,
- 89 übersprungene Ballastordner,
- Laufzeit 541 Millisekunden,
- vollständiger Abschluss,
- Sperrklasse `shared-read`.

### Reale parallele HTTP-Aufrufe

Zwei reale `assets.search`-Aufrufe wurden gleichzeitig an `127.0.0.1:8091/mcp` geschickt. Die Live-Operation-Registry zeigte beide gleichzeitig als:

- Werkzeug: `assets.search`,
- Zustand: `running`,
- Sperrklasse: `shared-read`.

Beide Aufrufe wurden erfolgreich und getrennt in der Hash-History protokolliert.

### Produktivdienst

Finaler Dienstzustand nach Gegenkorrektur:

- Dienst: `vps-mcp.service`
- Status: `active/running`
- PID: `1983872`
- Start: 26. Juli 2026, 16:46:07 CEST
- Port: `127.0.0.1:8091`

Unverändert aktiv:

- 3D-MCP: Port 8090
- Godot-Bridge: Port 18092

## Commits

- `049dbd10f` – Backup vor dem Umbau
- `94fafd855` – Parallele Leser und Zuhause-Körper
- `e80eec239` – Snapshot-Erzeugung aus der Leser-Allowlist entfernt
- `8f8043121` – Musterstatus auf produktiv bestätigt gesetzt
- `62f8e6b6b` – Übergabebrief auf den finalen Stand aktualisiert

## Offene Grenze

Der Serverkatalog enthält `mcp.home` real und der direkte HTTP-Aufruf funktioniert. Die bereits geladene Werkzeug-Schemaansicht einer laufenden ChatGPT-Unterhaltung kann jedoch bis zu einem Connector- oder Sitzungsrefresh noch den vorherigen Katalog anzeigen. `history_startup` liefert den Zuhause-Körper unabhängig davon bereits produktiv aus.
