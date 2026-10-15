# Lokaler Transport — Playwright-Beleg

EVIDENCE_VERSION: 1
STAGE: G01 transport foundation
DATE: 2026-09-19
OUTCOME: PASS

Scope: lokaler Relay auf `127.0.0.1`, zwei authentisierte Testteilnehmer,
Python-Testpeer plus echte Chromium-Seite. Das ist kein Windows-Overlay-,
VPS-, TLS- oder EXE-Beleg. Das Bild ist ausdrücklich `source=synthetic`.

- PW-TRANSPORT-01: PASS — Browser verbindet sich mit neuer Session- und Connection-Epoch.
- PW-TRANSPORT-02: PASS — Browser sendet Text; Python-Peer liest dieselbe Payload.
- PW-TRANSPORT-03: PASS — Empfang wird separat bestätigt; Sender erhält `forwarded` und danach `received`.
- PW-TRANSPORT-04: PASS — Browser überträgt synthetisches PNG; Python-Peer erhält SHA-256 und `metadata_verified=false`.
- PW-TRANSPORT-05: PASS — Python-Peer antwortet; Browser liest die Antwort und bestätigt den Empfang.
- PW-TRANSPORT-06: PASS — Fremdes `target_id` wird mit `grant_denied` abgewiesen und als Ereignis journalisiert.
- PW-TRANSPORT-07: PASS — Browser trennt; erneutes Verbinden erhält dieselbe Session-ID und eine neue Epoch.
- PW-TRANSPORT-08: PASS — SQLite-Ereignisjournal enthält connected, accepted, forwarded, received und denied.

Testbefehl:

```text
PYTHONPATH=src python3 tests/transport_playwright_proof.py
```

Screenshot: `/root/werkraum/augen_haende_bridge/tests/evidence/transport_local_playwright.png`.
