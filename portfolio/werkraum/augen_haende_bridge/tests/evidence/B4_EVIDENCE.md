# B4 — Input-Arbitrator-Core und Playwright-Gate

**Datum:** 2026-09-19  
**Neubaupfad:** `/root/werkraum/augen_haende_bridge/`  
**Kern:** `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/arbitrator.py`

## Core-Beweis

```text
cd /root/werkraum/augen_haende_bridge
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Ergebnis: **18 Tests, 18 bestanden, 0 Fehler.**

Nachgewiesen sind Target-Cage, Leaseprüfung, menschlicher Override pro Target, globaler menschlicher Override und Emergency Stop. Der Arbitrator dispatcht keine reale Eingabe.

## Playwright-Beweis

Der sichtbare Beleg liegt in `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B4_PLAYWRIGHT_EVIDENCE.md`.

- `PW-B4-01: PASS` — innerhalb des Käfigs erlaubt.
- `PW-B4-02: PASS` — außerhalb des Käfigs blockiert.
- `PW-B4-03: PASS` — Not-Aus blockiert Folgeaktion.

**B4-Core-Gate: PASS**  
**B4-Playwright-Gate: PASS**  
**B4-Plattformdispatch: noch nicht implementiert**
