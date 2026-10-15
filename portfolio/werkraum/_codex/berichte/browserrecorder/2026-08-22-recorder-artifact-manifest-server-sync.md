EVIDENCE_VERSION: 1

# Artefaktmanifest-Sync — 2026-08-22

## Aktion

Der Collection-Workspace synchronisiert nach einer expliziten Exportaktion das
Artefaktmanifest additiv zum Recorder-Server. Der Server speichert ausschließlich
bounded JSON-Metadaten in einer deduplizierten JSONL-Datei; Exportbytes bleiben
im lokalen IndexedDB-/Browserpfad. Zusätzlich gibt es einen authentifizierten
GET-Readback-Endpunkt.

## Sichtbar

Kein neuer Live-Browserlauf in dieser Teilstufe; der UI-Status unterscheidet nun
`Servermanifest synchronisiert` von `Servermanifest offen (...)`. Die URL ist im
Code als `https://flextrawurst.de/chatgpt-browser-recorder/api/v1/collections`
konfiguriert. Ein sichtbarer Serverlauf ist wegen fehlender FastAPI-Abhängigkeit
in dieser Shell nicht behauptet.

## Rücklese

- `python3 -m py_compile tools/action_history/browser_capture.py tools/chatgpt_browser_recorder/app.py` — PASS.
- `node --check` für `background.js`, `collection_workspace.js` und `config.js` — PASS.
- Isolierter Temp-Store-Test: `persisted` → erneute Sendung `already_present`, GET-Readback 1 Manifest; SHA-256/Bytes-Konflikt und `data_url`/Rohbytes wurden abgewiesen.
- Route/Auth-Test blieb offen: `fastapi` ist in dieser Entwicklungs-Shell nicht installiert; kein HTTP-Erfolg wurde daraus abgeleitet.

## Offen/Unbekannt

Die Live-Serverroute und der Tokenpfad müssen auf dem Recorder-Host mit dessen
Produktionsumgebung sichtbar getestet werden. Ohne gesetzten Recorder-Token bleibt
der lokale Export erfolgreich, aber der Serverstatus explizit `unavailable`.

- REC-GATE-001: PASS — Vertragsprüfung `check_recorder_skill_gates.py contracts` (10 Marker).
- REC-BACKUP-001: PASS — Backup-Checkpoint `ecd8ea95f` vor der Implementierung; zusätzlicher Dokumentations-Checkpoint `b168f9182`.
- REC-FETCH-001: PASS — POST/GET sind owner/purpose-bounded, `fetchJsonBounded` nutzt 15-s-Abort und 512-KiB-Responsegrenze; kein automatischer Load-Fetch.
- REC-SEC-001: PASS — Server lehnt Rohbytes/Data-URLs, ungültige SHA-256-Werte, übergroße Manifeste und Fingerabdruckkonflikte ab; Collectionpfad erhält zusätzlich einen Hash-Suffix.
- REC-DOC-001: PASS — diese Rücklese, Grenzen und die fehlende FastAPI-Liveprobe sind dokumentiert.

OUTCOME: PASS
