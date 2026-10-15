# B3 — VisionSession, Frame-Ring und Audience-Sichtbarkeit

**Datum:** 2026-09-19  
**Neubaupfad:** `/root/werkraum/augen_haende_bridge/`  
**Kern:** `/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/vision.py`

## Nachgewiesene Fähigkeiten

- Session-Lebenszyklus `start -> pause -> resume -> stop`.
- Frames werden nur im Zustand `running` angenommen.
- Der Frame-Ring ist begrenzt und schiebt ältere Einträge kontrolliert heraus.
- `daniel`, `shared_gate`, einzelner `agent` und `local_only` sind getrennte Sichtbarkeiten.
- Ein `shared_gate`-Frame wird nicht automatisch zu Daniels privater Sicht.
- `scrub()` erzeugt einen neuen pausierten Branch mit `parent_session_id` und `branched_from_frame_id`.

## Ausgeführter Test

```text
cd /root/werkraum/augen_haende_bridge
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Ergebnis: **12 Tests, 12 bestanden, 0 Fehler.**

## Gate

**B3-Core-Gate: PASS**

**B3-Playwright-Gate: PASS — `/root/werkraum/augen_haende_bridge/tests/evidence/B0_B4_PLAYWRIGHT_EVIDENCE.md`**

**Graphify-Postschritt: BLOCKED — `graphify` ist in der Umgebung nicht verfügbar**

**B3 vollständig geschlossen:** Core und sichtbarer Playwright-Beweis sind grün.
