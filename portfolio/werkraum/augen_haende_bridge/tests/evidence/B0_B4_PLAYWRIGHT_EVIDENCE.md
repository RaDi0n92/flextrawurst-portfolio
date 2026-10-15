# B0–B4 — Playwright-Beweisgate der Greenfield-Proof-Surface

**Datum:** 2026-09-19  
**Neubaupfad:** `/root/werkraum/augen_haende_bridge/`  
**Proof-Code:** `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/proof_surface.py`  
**Playwright-Test:** `/root/werkraum/augen_haende_bridge/tests/playwright_proof.py`  
**Browser:** Chromium über `/usr/local/bin/chromium`

## Ausgeführter sichtbarer Test

```text
cd /root/werkraum/augen_haende_bridge
PYTHONPATH=src python3 tests/playwright_proof.py
```

Ergebnis: **Playwright beendet sich mit Exit-Code 0.**

## Marker

- `PW-B0-01: PASS` — Proof-Surface zeigt ausdrücklich `CORE_PROOF_ONLY` und `surface:windows:bridge`.
- `PW-B0-02: PASS` — DOM zeigt `windows.desktop`, `linux.kde.desktop` und `linux.terminal` als aktuelle Targets.
- `PW-B1-01: PASS` — Playwright klickt `Inspect Linux KDE 1` und liest eine akzeptierte Policyantwort zurück.
- `PW-B2-01: PASS` — DOM-/Audit-Rücklese zeigt die echte Kette `action.requested` → `action.accepted`.
- `PW-B3-01: PASS` — Playwright pausiert und resumiert die VisionSession; der DOM-Zustand wechselt sichtbar.
- `PW-B3-02: PASS` — Playwright erzeugt einen Scrub-Branch und liest `branched_from_frame_id: f-shared` zurück.
- `PW-B4-01: PASS` — Input innerhalb des Target-Cages wird als bereit für Adapter-Dispatch angezeigt.
- `PW-B4-02: PASS` — Input außerhalb des Target-Cages wird mit `outside_target_cage` abgewiesen.
- `PW-B4-03: PASS` — Emergency Stop wird angezeigt; die Folgeaktion wird mit `emergency_stop_active` abgewiesen.

## Screenshots

- `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b0_surface.png`
- `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b1_b2_inspect_audit.png`
- `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b3_session_branch.png`
- `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_arbitrator.png`

## Beweisgrenze

Dies ist ein echter Playwright-Beweis gegen die neue, aus dem Greenfield-Kern gespeiste Proof-Surface. Er beweist noch keine reale Windows-Eingabe, keinen echten KDE-Capture-Stream und keinen MCP-Transport. Diese Grenzen bleiben sichtbar und werden erst in den jeweiligen Adapter-Etappen mit neuen Playwright-/Plattformbelegen geschlossen.

**PLAYWRIGHT OUTCOME: PASS**
