EVIDENCE_VERSION: 1

# Readback-Race-Fix — sichtbare Abnahme

## Fix

`collection_workspace.js` hält den letzten Server-Readback jetzt als `state.parity.serverReadback`. `renderStatus()` darf diesen expliziten Zustand bei Polling und Reload nicht mehr überschreiben. Ein neuer anderer UI-Status löscht ihn bewusst wieder.

## Playwright-Beleg

- Headful Chromium, `DISPLAY=:1`, lokaler Workspace mit echtem HTTPS-Readback.
- Eindeutige Container: `document.scrollingElement` (`0 → 620`) und `#worktabList` (`0 → 208 → 373`).
- Sichtbarer Klick auf `#parityServerRead`.
- Der Zwischen-Screenshot direkt nach dem Runtime-Readback zeigt jetzt dauerhaft: `Servermanifest-Readback abgeschlossen · 1 Manifest(e) vom VPS gelesen · lokale IndexedDB ergänzt.`
- Der zusätzliche direkte Browser-GET bestätigt danach sichtbar `HTTP 200 · 1 Manifest(e)`.
- Belegdateien: `2026-08-22-server-readback-playwright-live-v7/07-after-runtime-server-readback.png`, `08-after-server-readback.png` und `evidence.json`.
- `evidence.json` enthält `runtime_status_before_direct_readback` mit dem gefixten App-Status sowie den echten HTTP-200-Response-Body.

- REC-GATE-001: PASS — Vertragsgate vollständig.
- REC-EYE-001: PASS — Playwright-Schritttrace und zwei sichtbare Readback-Zustände.
- REC-BACKUP-001: PASS — Backup-Commits `7f96ba2d9`, `ef20a3b46` und `6acd1b136` vor Fix, Screenshot und Bericht.
- REC-FETCH-001: PASS — echter HTTPS-GET mit HTTP 200 und Manifest-Body.
- REC-SEC-001: PASS — Token nicht in Screenshot, JSON oder Bericht geschrieben.
- REC-DOC-001: PASS — Race-Ursache, Fix und Zwischenzustand dokumentiert.

OUTCOME: PASS
