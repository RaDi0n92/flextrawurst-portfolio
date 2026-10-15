# Playwright Guardian — Browser-/Core-Gate

EVIDENCE_VERSION: 1
STAGE: guardian-playwright
RUN: `PYTHONPATH=src python3 tests/playwright_guardian.py`

## Belege

- `PW-GUARDIAN-01: PASS —` die Prüfung startet die tatsächliche Proof-Surface in einem isolierten Playwright-Kontext.
- `PW-GUARDIAN-02: PASS —` die Mutation `Inspect Linux KDE 1` läuft über den sichtbaren Button und nicht über einen direkten POST aus dem Witness.
- `PW-GUARDIAN-03: PASS —` DOM-Projektion und `/api/state` werden für Surface, Proof-Modus, Target, Verfügbarkeit, Harness-Zustand, Scannerquelle, `scan_id` und `frame_hash` verglichen.
- `PW-GUARDIAN-04: PASS —` der Guardian akzeptiert den aktuellen Zustand nur als `unavailable`, weil der KDE-Adapter nicht gebaut ist; `accepted` der Policy wird nicht zu `observed` umgelogen.
- `PW-GUARDIAN-05: PASS —` fehlende Auditspur ist im Core-Unit-Test `blocked`, nicht grün.
- `PW-GUARDIAN-06: PASS —` fehlender nativer Plattformzeuge bleibt im Witness `unknown`.
- `PW-GUARDIAN-07: PASS —` Playwright-Trace wurde unter `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_guardian_trace.zip` geschrieben.
- `PW-GUARDIAN-08: PASS —` Screenshots wurden unter `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_guardian_initial.png` und `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_guardian_blocked_action.png` geschrieben.

## Grenzen

Dieser Bericht beweist keinen nativen Windows-Start, keinen Win32-/Tk-Hit-Test,
keine echte Windows-Eingabe und keinen nativen Windows-Fensterscanner. Der
synthetische Scanner trägt sichtbar `synthetic.proof-surface`.

OUTCOME: PASS

