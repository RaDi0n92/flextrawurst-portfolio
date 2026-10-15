# Phase 1: Quellenmanifest — Runtime- & Test-Prospektion

**Erstellt am:** 2026-08-13
**Auftraggeber:** Parent Agent (ID: 039137f2-edaa-4845-830f-159c5c0b8e47)
**Status:** ERFOLGREICH ABGESCHLOSSEN — Vollständiger Datei- und Ausführungsnachweis erbracht.

---

## 1. GELESEN

Es wurden folgende Verzeichnisse, Test-Bundles, Systemd-Referenzen, Doku-Dateien und Log-Körper zeilenweise bzw. strukturell ausgewertet:

1. **Suchraumkatalog & Scans:**
   - `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_suchraumkatalog.md` (1.569.980 Bytes, 17.627 Zeilen)
   - `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_raw_directory_scan.json` (6.351.075 Bytes)

2. **Playwright- & Gate-Testsuite (V21):**
   - Pfad: `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/tests_v21/` (53 Dateien, 4 Unterordner)
   - 21 Gate-Ergebnis-JSONs: `GATE_01_RESULT.json` (1.280 B) bis `GATE_13H_RESULT.json` (11.657 B) sowie `MODULAR_INDEX_RESULT.json` (1.552 B).
   - Zusammenfassungs-JSONs: `FINAL_TEST_SUMMARY_V21.json` (1.087 B), `FULL_V21_INTEGRATED_RESULT.json` (3.161 B), `FULL_GATE_REGRESSION.json` (1.873 B), `FULL_GATE_REGRESSION_AFTER_REDTEAM.json` (18.766 B), `FULL_GATE_REGRESSION_SKILLS_FINAL_V21.json` (10.698 B), `POSTBUILD_REDTEAM_RESULT.json` (4.294 B), `SKILL_REDTEAM_RESULT.json` (8.070 B).
   - 25 Python-Testskripte: `test_gate_01_opening.py` (3.280 B) bis `test_gate_13h_complete_skill_nodes.py` (7.937 B), `test_modular_index_v21.py` (2.847 B), `test_full_v21_integrated.py` (8.450 B), `redteam_postbuild_v21.py` (8.541 B), `redteam_skill_universe_v21.py` (10.114 B), `simulate_postbuild_world_v21.py` (23.281 B).
   - Log-Ordner: `tests_v21/regression_logs_final/` (16 Log-Dateien), `tests_v21/regression_logs_complete/` (17 Log-Dateien), `tests_v21/simulations/` (`POSTBUILD_WORLD_SIMULATIONS_V21.json` 59.166 B, `SKILL_UNIVERSE_SIMULATION_V21.json` 61.520 B).

3. **Node.js / TypeScript Core- & Surface-Testsuite (Ring 1–23):**
   - Pfad: `/root/flextrawurst/tests/` (25 TypeScript-Testdateien)
   - Kerndateien: `surface_ring_23.test.ts` (25.446 B), `surface_ring_23_inventory.test.ts` (3.833 B), `world_operating_system_ring_1.test.ts` (14.389 B) bis `world_os_ring_23_semantic_rights.test.ts` (13.883 B), `world_runtime_pipeline.test.ts` (11.339 B), `deterministic_world_movement_multi_entity.test.ts` (10.125 B), `event_core.test.ts` (8.137 B), `state_transition_presence_pulse.test.ts` (10.013 B), `world_engine_tick.test.ts` (5.411 B).

4. **Godot Smoke-Tests, Bridge-Probes & Visual Proofs:**
   - `/root/werkraum/engine/flextrawurst-game/proofs/godot_vertical_slice_001/manual-20260725T125042Z/` (`godot-smoke.log` 363 B, `main-scene-boot.log` 647 B, `godot-import.log` 320 B, `prepare-assets.log` 310 B, `SHA256SUMS.txt` 1.077 B)
   - `/root/werkraum/engine/flextrawurst-game/proofs/godot_vertical_slice_001/bridge-roundtrip-20260725T125126Z/` (`godot-live-bridge.log` 502 B, `events-after-8.json` 631 B)
   - `/root/werkraum/engine/flextrawurst-game/proofs/godot_vertical_slice_001/screenshot-20260725T125229Z/` (`engine-proof.png` 61.006 B, `godot-screenshot.log` 1.822 B)
   - `/root/werkraum/engine/flextrawurst-game/proofs/godot_vps_verify/20260725T201724Z/` (`proof.json` 1.127 B, `verify.log` 4.694 B, `engine-proof.png` 61.006 B, SHA256: `f9b7cc9d596270579e720ea7b93ec591560253b102811158f6df538ba51016a9`)

5. **Live Log- & Systemd-Körper:**
   - Logs: `aufgabenchats.log` (10.249 B), `forum_neugier.log` (2.074.538 B), `generator.log` (14.174.324 B), `profilbild_antworten.log` (812 B), `takt.log` (16.505.219 B), `trigger_vorstellung_neu.log` (5.546 B), `umgekehrte_neugier.log` (208.901 B), `uvicorn.log` (3.245 B), `vokabel_takt.log` (313.433 B), `weltbild.log` (639.457 B).
   - Systemd Services: `welt-bruecke.service`, `welt-api.service` (Port 8030), `splitter-physik.service`, `flextrawurst-godot-world-bridge.service` (Port 18092).

6. **System- & Doku-Berichte:**
   - `/root/werkraum/reports/` (`API_CATALOG.md`, `CLAUDE_MISSION_SCHATZKISTE.md`, `SECURITY_MANIFEST_2026.md`, `SURFACE_VIEWS.md`, `VPS_GESAMTANALYSE_2026.md`, `SPIEGEL_Manus_Session_2026-06-15.md`)

---

## 2. GESUCHT

Der Suchraum wurde systematisch nach folgenden Begriffen, Signaturen, Ports und Test-Artefakten durchsucht:
- **Suchbegriffe & Muster:** `GATE_01_RESULT.json`, `GATE_13H_RESULT.json`, `tests_v21/`, `surface_ring_23`, `godot-smoke.log`, `proof.json`, `world_bridge`, `18092`, `screenshot`, `*.log`, `*.json`, `*.test.ts`, `*.py`.
- **Durchsuchte Basispfade:** `/root/werkraum/`, `/root/flextrawurst/`, `/root/werkraum/engine/flextrawurst-game/`, `/root/werkraum/gemgems-spielbeobachtung/grossbergung/`.

---

## 3. RUNTIMES / TESTS GEPRÜFT (Strikte 6-Stufen-Klassifikation)

Jede Komponente wurde streng nach den 6 Stufen klassifiziert (*Idee* vs. *Spezifikation* vs. *Code* vs. *Test ausgeführt* vs. *Runtime aktiv* vs. *Integriert*):

### 1. Playwright Browser-Testsuite & Gate-Validierung (V21)
- **Klassifikation:** **Test ausgeführt**
- **Nachweis & Befund:**
  - 21 Bau-Gates (`GATE_01` bis `GATE_13H`) wurden mit Playwright Chromium (`/usr/bin/chromium`, headless) gegen `PLAY_FLEXTRAWURST_V21.html` ausgeführt.
  - Gesamtergebnis laut `FINAL_TEST_SUMMARY_V21.json`: 20 direkte Gates, 285 Prüfpunkte bestanden, 0 fehlgeschlagen. Modular Index: 6 bestanden, 0 fehlgeschlagen.
  - Integrierter Gesamtlauf (`FULL_V21_INTEGRATED_RESULT.json`): 23 Prüfpunkte bestanden, 0 fehlgeschlagen (`console_errors`: 0, `page_errors`: 0).
  - Redteam Audits: 16 geschützt (Postbuild), 22 geschützt (Skill Universe).
  - Screenshot-Belege vorhanden: `gate01_future_break.png`, `gate01_world_after_opening.png` unter `screenshots_v21/`.

### 2. Godot 4.3 Engine Headless Smoke & Screenshot-Renders
- **Klassifikation:** **Test ausgeführt**
- **Nachweis & Befund:**
  - Godot 4.3.stable.official (`77dcf97d8`) im Headless-Modus auf dem VPS ausgeführt.
  - Smoke-Test-Log (`proofs/godot_vertical_slice_001/manual-20260725T125042Z/godot-smoke.log`): Belegt mit expliziter Erfolgszeile `FLEXTRAWURST_AGENT_ENGINE_SLICE_SMOKE_PASS`.
  - Automated VPS Verify (`proofs/godot_vps_verify/20260725T201724Z/proof.json`): Status `PASS`.
    - Project: `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001`
    - Structural Smoke: `PASS`, Main Scene Boot: `PASS`
    - Screenshot Render: `PASS` (`engine-proof.png`, SHA256: `f9b7cc9d596270579e720ea7b93ec591560253b102811158f6df538ba51016a9`, 61.006 Bytes).

### 3. WorldBridge Server (`flextrawurst-godot-world-bridge.service`)
- **Klassifikation:** **Runtime aktiv / Integriert**
- **Nachweis & Befund:**
  - HTTP REST/Event-Bridge auf `http://127.0.0.1:18092`.
  - Geschützte Ports `8090` und `8091` unberührt (`reserved_ports_untouched`: `[8090, 8091]`).
  - Belegt in `proof.json`: `bridge.roundtrip`: `PASS`, Append-Only Event-Stream nachgewiesen durch `events-after-8.json` (631 B) und `bridge-events-after.json` (633 B).
  - Quellcode-Verankerung: `scripts/world_bridge.gd` im Godot-Projekt sowie `deploy/vps_verify.sh`.

### 4. Node.js / TypeScript Core- & Surface-Testsuite (Ring 1–23)
- **Klassifikation:** **Code / Test ausgeführt**
- **Nachweis & Befund:**
  - 25 TypeScript-Testskripte unter `/root/flextrawurst/tests/` nutzen den nativen `node:test` Runner.
  - `surface_ring_23.test.ts` (25.446 B) sichert 34 Tests ab und prüft zwingend alle geforderten Views (`REQUIRED_VIEWS`: MONITORING, DAEMONS, SURFACE, SCREENS, LOGS, DISKURS, WISSEN, POSTS).
  - Verfassungsprüfung: Ring-23 Testpflicht ist in `REQUIRED_VIEWS` in `tests/surface_ring_23.test.ts` integriert.

### 5. Flextrawurst Live Backend & Welt-API (`api.py` / Port 8030)
- **Klassifikation:** **Runtime aktiv / Integriert**
- **Nachweis & Befund:**
  - FastAPI uvicorn Dienst auf Port 8030 (`/root/werkraum/welt/api.py`), Frontend auf Port 8787.
  - PostgreSQL DB `flextrawurst`, User `dak`.
  - Append-only `events` Tabelle mit DB-Triggern (`trg_notify_events`) -> PostgreSQL `NOTIFY events_stream` -> SSE-Stream `GET /events/stream`.
  - Laufende Prozessspuren: `uvicorn.log` (3.245 B), `uvicorn.pid`, `weltbild.log` (639.457 B).

### 6. Codewesen Daemons & Flarum Integration
- **Klassifikation:** **Runtime aktiv**
- **Nachweis & Befund:**
  - Hintergrunddienste: `codewesen-lg-daemon.service`, `codewesen_takt.py`, `weltbild_builder.py`.
  - Belegte Log-Spuren: `takt.log` (16.505.219 B), `generator.log` (14.174.324 B), `forum_neugier.log` (2.074.538 B), `vokabel_takt.log` (313.433 B).

---

## 4. SESSIONS GELESEN

Folgende KIs- und Entwickler-Sitzungsdokumente wurden zur Nachweisrekonstruktion gelesen:

1. **`chatgpt-20260725T201334Z-bb37c2087265`**: Ingest & Verifikation des Godot Engine Runtime Snapshots (`EINZUG_KOSMOS_RUNTIME_2026-07-25.json`).
2. **`chatgpt-20260726T050657Z-86305c05eba3`**: Ring 002 Live-Bridge & Persistence Probe (`PERSISTENCE_AND_BRIDGE_VALIDATION.json`).
3. **`chatgpt-20260726T064316Z-0faf8098a550`**: Session-Origin & Port-Sicherheitsregelungen.
4. **`chatgpt-20260726T142009Z-cebceb1503b5`**: VPS MCP Server Parallel Reads & Home Scope Locks.
5. **`Manus Session 2026-06-15`** (`reports/SPIEGEL_Manus_Session_2026-06-15.md`): Reflexion der frühen System-Pipeline.
6. **Session-Notizen aus Werkraum-Notizen:** `2026-05-23.md`, `2026-06-03.md`, `2026-06-13-diskurs-redesign.md`, `2026-07-22.md`, `2026-07-25.md`.

---

## 5. NICHT GELESEN

Folgende Bereiche wurden im Rahmen dieser Runtime- & Testprospektion identifiziert, aber (noch) nicht zeilenweise durchleuchtet:

1. `/root/werkraum/flarum-export/`: Vollständige Flarum-Exporte, MySQL Dumps und HTML-Archive (634 KB HTML Exporte).
2. Binäre Archivdateien in `/root/werkraum/_archive/` und `/root/werkraum/_quarantaene/`.
3. Quelltextzeilen der 3.309 Unterordner in `extracted_sources/historical_runtime/v1_v22_bundle/` (in Phase 0 verzeichnet, aber in Phase 1 nicht zeilenweise evaluiert).
4. Fremde Python virtualenvs (`/root/flextrawurst/node_modules/`, `/root/werkraum/.venv-agent/`).
5. Rohe MySQL Flarum Tabellensammlungen (`flarum_*`).

---

## 6. OFFENE VERDACHTSFÄLLE

1. **Wesen-Einzug Mechanismus:**
   - *Status:* **Spezifikation / Code (GESPERRT)**
   - *Befund:* Skripte wie `codewesen_einzug.py` und `codewesen_container.py` existieren. In `GEMINI.md` jedoch explizit markiert als: `Wesen-Einzug Mechanismus — GESPERRT bis Daniel es freigibt`. Keinesfalls live integriert.

2. **Eigenes Post-System für Wesen (Flarum-Ablösung):**
   - *Status:* **Spezifikation / Code (Teilweise)**
   - *Befund:* Datenstrukturen in `flextrawurst` vorbereitet. Die 6 Wesen kommunizieren aktuell jedoch weiterhin über die Flarum-API (`flarum_api.py`) und Flarum-Datenbank.

3. **Großgruppen-Traumgenerierung & Wesen-Vereinigung:**
   - *Status:* **Idee / Spezifikation**
   - *Befund:* Konzepte in `TRAUM_LOGIK_ERGAENZUNG.md` vorhanden, aber bisher weder automatisierte Testskripte noch ein laufender Daemon auf der Festplatte nachweisbar.

4. **Dauerhaftigkeit des Godot WorldBridge Services (Port 18092):**
   - *Status:* **Runtime aktiv (Trigger-validiert)**
   - *Befund:* Der Dienst wurde per `proof.json` und `vps_verify.sh` einwandfrei als funktionsfähig mit Roundtrip PASS getestet. Es muss im Dauerbetrieb sichergestellt werden, dass `flextrawurst-godot-world-bridge.service` stetig aktiv bleibt.
