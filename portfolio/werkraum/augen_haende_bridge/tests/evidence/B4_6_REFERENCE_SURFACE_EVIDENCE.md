# B4.6 — Referenzgetriebene Bridge-Surface

> **Nachprüfung durch Codex, 2026-09-19:** Das folgende historische PASS gilt ausschließlich für die aufgeführten Browserprüfungen. Die damalige Gleichsetzung mit der fertigen räumlichen Windows-Bridge ist nicht belegt und wird zurückgenommen. Native Overlay-/EXE-Abnahme: OFFEN. Keine erneute Testausführung durch diese Anmerkung. Grundlage: `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md`.

EVIDENCE_VERSION: 1
STAGE: B4.6
OUTCOME: PASS

Die sichtbare Surface ist die räumliche Windows-Bridge aus der Referenz, nicht
eine Homepage. Das interne Proof-Panel bleibt ein separates Diagnosewerkzeug.

- PW-B4.6-01: PASS — Playwright öffnet `reference_surface` und liest
  `data-testid=reference-surface` sowie den Status `REFERENCE_SURFACE — kein Homepage-Modus`.
- PW-B4.6-02: PASS — Die Surface enthält vier Agenten-Rauten, vier Terminalflächen,
  die Ziel-/Bindungsschiene und die Regiefläche unten links.
- PW-B4.6-03: PASS — Playwright bindet sichtbar auf `Linux KDE Desktop 1` um und
  liest den ausgewählten Zielmodus aus dem DOM zurück.
- PW-B4.6-04: PASS — Ein individueller Mikrofon- und Kameraschalter wird über die
  Regiefläche betätigt und der Zustand im Surface-Readback bestätigt.
- PW-B4.6-05: PASS — Ein Regiespruch erzeugt eine sichtbare Toast-Antwort mit
  `Regiespruch`.
- PW-B4.6-06: PASS — Der Fensterscanner von Terminal (2) öffnet sein eigenes
  Menü; die Menüs bleiben terminalbezogen.
- PW-B4.6-07: PASS — Die Transparenz wird auf `0.48` gesetzt und im
  Surface-Readback als Aktion `set-opacity` rückgelesen.
- PW-B4.6-08: PASS — Eine Agenten-Raute wird über Pointer-Drag verschoben und
  die Aktion `move-node` im Surface-Readback rückgelesen.

Screenshots:

- `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_6_reference_surface.png`
- `/root/werkraum/augen_haende_bridge/tests/evidence/playwright_b4_6_reference_surface_interaction.png`

## Grenzen dieses Belegs

B4.6 beweist die sichtbare und interaktive Referenzschicht. Es beweist noch
keinen echten Windows-Capture-Adapter, keine MCP-Fassade und keine allgemeine
Fenster- oder Shell-Steuerung. Diese Fähigkeiten bleiben eigene Gates.
