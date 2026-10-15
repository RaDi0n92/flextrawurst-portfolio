# B2 — Deterministischer In-Memory-Loopback-Kern

**Datum:** 2026-09-19  
**Neubaupfad:** `/root/werkraum/augen_haende_bridge/`  
**Kern:** `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/loopback.py`

## Nachgewiesene Kette

Der isolierte Kern führt für eine Anfrage genau diese erste Kette aus:

```text
action.requested
        ↓
Policy-Auswertung
        ↓
action.accepted oder action.denied
```

Der Kern dispatcht absichtlich noch keine Windows-, Linux-, Terminal-, Maus- oder Tastaturaktion.

## Ausgeführter Test

```text
cd /root/werkraum/augen_haende_bridge
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Ergebnis: **9 Tests, 9 bestanden, 0 Fehler.**

## Nachgewiesene Fälle

- Ein Linux-KDE-Target kann über die sichtbare Windows-Surface angesprochen werden.
- Die Auditspur enthält Anfrage und Policyentscheidung in deterministischer Reihenfolge.
- Ein akzeptierter Policy-Status erzeugt noch kein `action.dispatched`.
- Der Not-Aus wird selbst auditiert und blockiert nachfolgende Requests.
- B0/B1-Fälle bleiben grün.

## Gate

**B2-Core-Gate: PASS**

**B2-Playwright-Gate: PASS — `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B4_PLAYWRIGHT_EVIDENCE.md`**

**Graphify-Postschritt: BLOCKED — `graphify` ist in der Umgebung nicht verfügbar**

**B2 vollständig geschlossen:** Core und sichtbarer Playwright-Beweis sind grün.
