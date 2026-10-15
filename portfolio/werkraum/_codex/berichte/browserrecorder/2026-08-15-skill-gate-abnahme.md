# Abnahme: verbindliche Recorder-Skills und Marker-Gate

Datum: 2026-08-15 14:27 +0200  
Stufe: `code-change`  
EVIDENCE_VERSION: 1

## Aktion

Die Recorder-Integritätsregeln wurden in zehn getrennte Skills mit je einem
Marker aufgeteilt. Dazu kamen der maschinenlesbare Katalog
`_codex/skills/registry.json`, der Prüfer
`_codex/tools/check_recorder_skill_gates.py` und die Pflichtverankerung in
`/root/AGENTS.md`.

## Sichtbar

Im Terminal waren alle zehn Skill-Verzeichnisse vorhanden. Der
Skill-Creator-Validator meldete zehnmal `Skill is valid!`. Der Vertrags-Gate-
Aufruf meldete `{"ok": true, "mode": "contracts", "markers": 10,
"skills": 10}`. Es wurde in dieser Stufe kein Browserklick als Live-Beleg
behauptet.

## Rücklese

Die persistierten Quellen wurden aus Git und vom Checker erneut gelesen. Die
Skill-Schicht ist in `b85f9ed85`, Katalog und Checker in `c0cc6e5bf`, der
Vorher-Sicherungspunkt in `c32814553` und die Startvertrags-Verankerung im
Root-Repository in `f2380a6503e` enthalten.

## Offen / unbekannt

Diese Abnahme beweist nur die Durchsetzung der Vertrags- und Berichtsschicht.
Sie beweist noch keine Reparatur der 32 fachlichen Recorder-/Crawler-Befunde,
keinen neuen Live-Klick und keinen fertigen Download. Dafür müssen die jeweils
passenden Stufenberichte mit Echtaugen-, Persistenz- und Datei-Rücklese folgen.

- REC-GATE-001: PASS — Vertragschecker liest Registry und zehn Skills ohne Fehler
- REC-BACKUP-001: PASS — Backup-Commits `c32814553`, `b85f9ed85`, `c0cc6e5bf` und Root-Commit `f2380a6503e` rücklesbar
- REC-DOC-001: PASS — dieser Bericht enthält Aktion, Sichtbar, Rücklese und Offen/Unbekannt

OUTCOME: PASS
