# Spiegelprüfung — `spiel/16_ct_scan_v22_questkosmos_generator_simulation.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/spiel/16_ct_scan_v22_questkosmos_generator_simulation.md`
- Snapshot-SHA256: `039d404c0518d0ec54ee87c63dc0e7cee394494cbf58e8b120ffaa30c736039a`
- Bytes: 7482
- Zeilen: 89
- Snapshot-mtime: `2026-08-13T07:21:03.288810+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–89: `4e26afded2d125a612d23d70997ce4ddec7d7c5988ea1046b1ea5cefaee45c13` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Beschreibt v22 ausdrücklich als Questdesign-, Generator-, Redteam- und deterministischen Simulationskörper, nicht als neue Spielruntime.
- Inventarisiert zwei Python-Werkzeuge: `build_v22_questkosmos.py` (1.225 Zeilen) und `audit_prior_simulations.py` (112 Zeilen).
- Trennt v21 als ausführbaren/testbaren Spielkörper von v22 als Offline-Generator ohne JS/GDScript/Game-Loop.
- Erklärt Pass A vs. Pass B: Pass A hatte 4,9% formale Constraint-Verstöße; Pass B erzwingt Regeln im Generator und erreicht dadurch 0 formale Fehlschläge.
- Betont ausdrücklich, dass 0 Fehlschläge kein menschlicher Playtest- oder Qualitätsbeweis sind.
- Trennt 64-Bit Rolling Hash von SHA-256.
- Nennt physische Ergebnisartefakte: `quest_catalog.sqlite` mit 111.111 Einträgen, CSV.gz, 333 repräsentative JSONL-Spuren und `09_PROOF_OF_RUN.json` vom 25.07.2026.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Gesamtcodezeilen der zwei Tools: 1.225 + 112 = 1.337.
- v22-Struktur nennt 15.873 7-Akt-Ketten, 37 Foci, 69 Skills, 12 Spielorgane, 777 Fragen, 111 Checks, 99 Varianten.

## Provenienzklasse

Gemini-Code-/Daten-Audit vom 13.08.2026 über den historischen v22-Generatorbestand.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- `funktionierende Python-Matrix-Generierung` ist durch vorhandenen Generator + historische Proofs gestützt, aber die Datei berichtet keine aktuelle vollständige Re-Execution.
- 0% Pass-B-Fehler sind Selbstkonsistenz des Generators gegen eigene Constraints, keine unabhängige Spielqualitätsprüfung.
- `umfassendste Expansionsstufe` ist interpretative Wertung, keine messbare Provenienzbehauptung.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
