EVIDENCE_VERSION: 1

# Servermanifest-Readback — 2026-08-22

## Aktion

Der Collection-Workspace hat jetzt eine sichtbare, explizite Aktion
`Servermanifeste lesen`. Sie ruft den authentifizierten GET-Endpunkt ab und
übernimmt die zurückgelesenen Metadaten erst danach lokal in IndexedDB.

## Sichtbar

Die Schaltfläche liegt direkt neben dem Export im Parity-Layer. Bei einem offenen
oder nicht erreichbaren Server wird `Servermanifest-Readback offen: ...` gezeigt;
bei Erfolg wird Anzahl der gelesenen Manifeste und die lokale Ergänzung angezeigt.

## Rücklese

- `node --check background.js collection_workspace.js` — PASS.
- `python3 -m py_compile browser_capture.py app.py` — PASS.
- Vertragsgate — PASS (10 Marker).
- Echter HTTPS-Probe gegen `https://flextrawurst.de/chatgpt-browser-recorder/api/v1/collections/test-collection/artifact-manifests` mit ungültigem Testtoken: HTTP 404, Body `{"detail":"Not Found"}`.
- Gesundheitsprobe derselben Domain: HTTP 200, aber Serverversion `1.3.2`; der lokale Quellstand mit Readback ist dort noch nicht deployed.

## Offen/Unbekannt

Der Live-Server muss noch auf den lokalen Quellstand aktualisiert und danach mit
einem echten, nicht im Report sichtbaren Recorder-Token getestet werden. Kein
Server-Readback-Erfolg wird aus dem lokalen UI-Code abgeleitet.

- REC-GATE-001: PASS — `check_recorder_skill_gates.py contracts` grün.
- REC-BACKUP-001: PASS — Checkpoint `d58a167d6` vor der Readback-UI-Änderung; `765f53c58` vor diesem Bericht.
- REC-FETCH-001: PASS — Readback nutzt den bestehenden `fetchJsonBounded`-Pfad mit 15-s-Abort und 512-KiB-Responsegrenze; nur expliziter Button, kein Load-Fetch.
- REC-SEC-001: PASS — Token bleibt im Header, Rohbytes werden nicht gelesen, Serverantwort wird auf `ok` und Manifestliste geprüft.
- REC-DOC-001: PASS — sichtbare UI-Wirkung, HTTP-404-Gegenbeweis und Deployment-Lücke sind getrennt dokumentiert.

OUTCOME: PASS
