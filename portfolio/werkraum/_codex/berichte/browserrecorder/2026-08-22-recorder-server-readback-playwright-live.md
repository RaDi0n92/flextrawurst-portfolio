EVIDENCE_VERSION: 1

# Live-Playwright-Beleg — Servermanifest-Readback

## Sichtbarer Lauf

- Chromium lief sichtbar (`headless: false`, `DISPLAY=:1`) mit Playwright.
- Workspace-URL: `http://127.0.0.1:8765/collection_workspace.html?collection_id=playwright-live-readback-20260822T101539Z`
- Die Extension-Runtime hatte Fixture-Daten für 8 Snapshots/10 Arbeits-Tabs; der Server-Readback wurde dagegen über den echten HTTPS-Endpunkt ausgeführt.
- Eindeutige Scroll-Container und echte Einzelschritte:
  - `document.scrollingElement`: `0 → 620`
  - `#worktabList`: `0 → 208 → 373`
- Vor dem Klick wurde `#parityServerRead` in den sichtbaren Viewport gescrollt und fotografiert. Danach erfolgte der echte Playwright-Klick.

## Live-Rücklese

- Der Browser führte den echten GET aus:
  `https://flextrawurst.de/chatgpt-browser-recorder/api/v1/collections/playwright-live-readback-20260822T101539Z/artifact-manifests?limit=100`
- Serverantwort: HTTP `200`, `status: read_back`, `1 Manifest(e)`.
- Das DOM zeigte danach sichtbar: `Live HTTPS Readback: HTTP 200 · 1 Manifest(e) · Serverantwort sichtbar rückgelesen`.
- Das sichtbare Ergebnis liegt in `2026-08-22-server-readback-playwright-live-v5/07-after-server-readback.png`.
- Die vollständige Rücklese mit Response-Body, Artifact-ID, SHA-256, URL, Titel, Scrollpositionen und Runtime-Nachrichten liegt in `2026-08-22-server-readback-playwright-live-v5/evidence.json`.
- Der Serverjournal-Beleg bestätigt zusätzlich OPTIONS/GET `200 OK`; Health meldet nach dem Neustart Version `1.3.3`.

## Bewusste Race-Grenze

Die Workspace-Runtime schreibt beim Rendern den allgemeinen `Live · 8 Snapshots`-Status zurück. Deshalb wurde der erfolgreiche Live-GET nach dem sichtbaren Button-Klick zusätzlich direkt im Playwright-DOM als eigener Readback-Satz festgehalten. Der Bericht behauptet nicht, ein kurz sichtbarer UI-Status sei allein ausreichend.

- REC-GATE-001: PASS — Vertragsgate meldet alle 10 Recorder-Marker/Skills vollständig.
- REC-EYE-001: PASS — headful Chromium, sichtbarer Button, zwei eindeutige Container, fünf echte Positionen und sieben Einzelscreenshots.
- REC-BACKUP-001: PASS — Backup-Commits `9cead5d2c`, `5509bef85`, `fc40a0127` und `ba8b9e744` vor Dienst-/Scriptänderungen.
- REC-FETCH-001: PASS — echter HTTPS-GET im Browser, HTTP-Status und JSON-Body im Playwright-Readback rückgelesen.
- REC-SEC-001: PASS — Token nur zur Laufzeit aus dem VPS-Environment eingespeist; kein Token im Bericht, Screenshot oder `evidence.json`.
- REC-DOC-001: PASS — Lauf, Endpoint, DOM-Text, Serverjournal-Gegenbeleg und offene Race-Grenze dokumentiert.

OUTCOME: PASS
