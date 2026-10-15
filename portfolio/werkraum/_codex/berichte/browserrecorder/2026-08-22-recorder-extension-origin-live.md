# Echte Extension-Origin-Prüfung — Desktop 1

EVIDENCE_VERSION: 1
DATE_UTC: 2026-08-22
STAGE: live-click + fetch
OUTCOME: PASS

## Gegenstand

Die Referenz-Erweiterung `AI UI Recorder für dak` wurde mit Playwright in einem sichtbaren Chromium auf `DISPLAY=:1` geladen. Der Lauf verwendete einen frischen temporären Chromium-Profilordner und die echte Extension-Origin:

`chrome-extension://molhhdlenmhokfibmbojpapccaidfepi/collection_workspace.html`

Die Seite `http://127.0.0.1:8766/flextrawurst/flextrawurst_surface.html#uber` wurde als sichtbare Quelle verwendet. Es wurden zwei ausdrücklich geklickte Snapshots in derselben Sammlung erzeugt. Kein automatischer URL-Follow und kein automatischer Scroll wurde verwendet.

## Sichtbare Belegkette

- REC-GATE-001: PASS — contracts gate meldete ok=true mit 10 Markern und 10 Skills.
- REC-EYE-001: PASS — Playwright headful auf DISPLAY=:1; zwei sichtbare Snapshot-Klicks; Screenshots liegen bei [after-extension-crawl.png](after-extension-crawl.png) und [after-extension-readback.png](after-extension-readback.png).
- REC-BACKUP-001: PASS — Backup-Commits a68776d2f und feb6f6ee0 wurden vor der jeweiligen Änderung gesetzt.
- REC-FETCH-001: PASS — sichtbarer Klick auf `Servermanifeste lesen`; UI zeigte `Servermanifest-Readback abgeschlossen · 1 Manifest(e) vom VPS gelesen · lokale IndexedDB ergänzt.`.
- REC-SEC-001: PASS — Zugangsschlüssel wurde nur im temporären Chromium-Profil gesetzt; kein Schlüssel steht in diesem Bericht oder Screenshot-Text.
- REC-DOC-001: PASS — echte Extension-Origin, Sammlung-ID, Artefaktgröße und SHA-256 wurden aus der laufenden UI rückgelesen.

## Rückgelesene Zustände

- Sammlung: `collection-2026-08-22T130959206Z-6b855162`
- Snapshots: `2`, beide `complete`
- Artefakt: `MD`, `25448 Bytes`
- Artefakt-SHA-256: `5d0553d69255ff8fa2777c236e93bfd0c22cd808575c4000ccbd9e2894ff558d`
- Vor Rücklese: `Server: persisted`
- Nach Rücklese: `Server: read_back`
- Workspace-Status blieb nach Polling sichtbar: `Servermanifest-Readback abgeschlossen · 1 Manifest(e) vom VPS gelesen · lokale IndexedDB ergänzt.`

## Fix, der durch den echten Lauf nötig wurde

`collection_workspace.js` behandelt bei der Parity-Aufbereitung nun fehlende Snapshot-Seiten mit optionalem Zugriff (`page?.captured_utc`). Dadurch bleibt ein kurzzeitig noch nicht materialisierter Snapshot offen, statt den gesamten Workspace beim ersten Rendern mit `Cannot read properties of null` zu markieren.

OUTCOME: PASS
