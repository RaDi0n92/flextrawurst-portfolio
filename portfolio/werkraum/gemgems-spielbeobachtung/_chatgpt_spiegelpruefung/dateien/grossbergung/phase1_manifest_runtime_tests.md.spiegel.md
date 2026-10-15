# Spiegelprüfung 006/080 — `grossbergung/phase1_manifest_runtime_tests.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase1_manifest_runtime_tests.md`
- Snapshot-SHA256: `834e35d4f3c8016cb07633740e830ae7b47203c1ab1740a5d3543071126f319d`
- Bytes: 11444
- Zeilen: 146
- Snapshot-mtime: `2026-08-13T10:28:35.814945+00:00`
- Encoding: `utf-8`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- MASCHINELLE QUELLENABDECKUNG: VOLLSTÄNDIG SNAPSHOTTIERBAR
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–146: `75ef0ffab027e8cac5efb292ec0c894dda26cadfc39b740ba5afb5e736fac341` | semantisch: GEPRÜFT

## Strukturmarker aus der Quelle

- L1: # Phase 1: Quellenmanifest — Runtime- & Test-Prospektion
- L9: ## 1. GELESEN
- L43: ## 2. GESUCHT
- L51: ## 3. RUNTIMES / TESTS GEPRÜFT (Strikte 6-Stufen-Klassifikation)
- L55: ### 1. Playwright Browser-Testsuite & Gate-Validierung (V21)
- L64: ### 2. Godot 4.3 Engine Headless Smoke & Screenshot-Renders
- L74: ### 3. WorldBridge Server (`flextrawurst-godot-world-bridge.service`)
- L82: ### 4. Node.js / TypeScript Core- & Surface-Testsuite (Ring 1–23)
- L89: ### 5. Flextrawurst Live Backend & Welt-API (`api.py` / Port 8030)
- L97: ### 6. Codewesen Daemons & Flarum Integration
- L105: ## 4. SESSIONS GELESEN
- L118: ## 5. NICHT GELESEN
- L130: ## 6. OFFENE VERDACHTSFÄLLE

## Was die Datei tatsächlich aussagt

- Inventarisiert historische v21-Tests, Node/TS-Surface-Tests, Godot-Proofs, Logs, Dienste und Backendkomponenten.
- Ordnet Komponenten in Code, Test, Runtime und Integration ein.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- v21: 20 direkte Gates mit 285 historischen Prüfpunkten; zusätzlich Modular Index. Godot-Proof und Bridge-Port 18092 werden genannt.

## Provenienzklasse

Phase-1-Runtime-/Test-Sekundärmanifest vom 13.08.2026.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Historische Resultdateien sind nicht automatisch aktuelle Re-Execution.
- Plattform-/Surface-Tests und Game-Tests werden im selben Manifest geführt und dürfen nicht als ein einziger Gamekörper gelesen werden.
- `Runtime aktiv` ist zeitpunktgebunden und braucht für heutige Aussagen frische Prozess-/Portprüfung.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
