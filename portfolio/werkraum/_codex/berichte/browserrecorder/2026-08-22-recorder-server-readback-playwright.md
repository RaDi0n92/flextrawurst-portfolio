EVIDENCE_VERSION: 1

# Playwright-Beleg — Servermanifest-Readback

## Sichtbarer Lauf

- Ausführung in sichtbarem Chromium (`headless: false`, `DISPLAY=:1`) mit Playwright.
- URL: `http://127.0.0.1:8765/collection_workspace.html?collection_id=collection-playwright-readback-v3`
- Fixture: 8 gespeicherte Snapshots und 10 Arbeits-Tabs; die Extension-Runtime ist für diesen isolierten UI-Lauf ausdrücklich gemockt.
- Der Lauf hat die eindeutigen Scroll-Container einzeln ermittelt und jeden tatsächlichen Schritt als Screenshot festgehalten:
  - `document.scrollingElement`: `0 → 620`
  - `#worktabList`: `0 → 208 → 373`
- Vor dem Klick wurde `#parityServerRead` sichtbar in den Viewport gescrollt und fotografiert. Danach wurde der Button mit Playwright geklickt.

## Sichtbare Rücklese

- Nach dem Klick stand im DOM sichtbar: `Servermanifest-Readback offen: HTTP 404 Not Found`.
- Der amberfarbene Status ist im Screenshot `2026-08-22-server-readback-playwright-v4/07-after-server-readback-404.png` sichtbar.
- Die vollständige, schrittweise Rücklese liegt in `2026-08-22-server-readback-playwright-v4/evidence.json` (URL, Titel, Container, Positionen, Screenshots, Runtime-Nachrichten).
- Runtime-Nachrichten belegen die sichtbare Kette: `workspace_status`, `workspace_snapshot`, `workspace_export`, danach `artifact_server_list`.
- Das ist kein „grüner Test“: Der Beleg ist der sichtbare Chromium-Zustand plus DOM-Rücklese. Der 404 bleibt offen und wird nicht als Erfolg umetikettiert.

## Externer Gegencheck

- Der separate Produktionsprobe gegen `https://flextrawurst.de/chatgpt-browser-recorder/api/v1/health` antwortete mit Version `1.3.2`; der neue Manifest-Endpunkt antwortete dort mit HTTP 404.
- Damit ist der lokale UI-Lauf nachgewiesen, die VPS-Deployment-Lücke aber weiterhin sichtbar offen.

- REC-GATE-001: PASS — `python3 /root/werkraum/_codex/tools/check_recorder_skill_gates.py contracts` meldete 10 geprüfte Marker/Skills.
- REC-EYE-001: PASS — headful Chromium/Playwright, sichtbarer Button, sichtbarer Status und sieben Einzelscreenshots aus realen Scrollpositionen.
- REC-BACKUP-001: PASS — Backup-Commits `503a5120373`, `d68d18f384a` und `bdb4f8100bc` vor Script-, Trace- und Berichtänderungen.
- REC-FETCH-001: PASS — Server-Readback wurde als eigener Runtime-Schritt ausgeführt; HTTP-404 wurde sichtbar rückgelesen und als offen markiert.
- REC-SEC-001: PASS — isolierte lokale Fixture, kein Roh-HTML- oder Daten-URL-Fetch; Produktionsprobe nur gegen den festgelegten Health-/API-Pfad.
- REC-DOC-001: PASS — `evidence.json`, Screenshotpfade, URL, Titel, Containerpositionen und offene Deployment-Grenze sind dokumentiert.

OUTCOME: PASS
