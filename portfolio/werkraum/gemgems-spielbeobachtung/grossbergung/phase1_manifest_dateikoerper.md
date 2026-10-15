# Phase 1 — Manifest der Dateikörper & Spielquellen (Flextrawurst Grossbergung)

**Status:** Vollständig strukturiert und katalogisiert  
**Erstellzeitpunkt:** 2026-08-13  
**Suchraum:** VPS Root (`/root`) & Werkraum Subsysteme (`/root/werkraum/...`)  

---

## 1. GELESEN
- `/root/werkraum/gemgems-spielbeobachtung/systempromptkonzept.md` (51 Zeilen, 5630 Bytes) — Grundgesetz & Red-Team-Prüfmatrix für die Spielbeobachtung (7-Stufen-Wahrheitsleiter).
- `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_suchraumkatalog.md` (17627 Zeilen, 1.57 MB) — Vollständiger VPS-Suchraumkatalog (18.535 gescannte Ordner).
- `/root/werkraum/engine/godot-vertical-slice/scripts/main.gd` (187 Zeilen, 6916 Bytes) — GDScript-Hauptsteuerung des Godot 3D Vertical Slice.
- `/root/werkraum/engine/godot-vertical-slice/scripts/world_bridge.gd` (3737 Bytes) — WebSocket/HTTP-Live-Brücke zwischen Godot 3D Engine und Flextrawurst Welt-API.
- `/root/werkraum/engine/godot-vertical-slice/project.godot` (893 Bytes) — Engine-Konfiguration, Render-Settings und Input-Maps für Godot.
- `/root/werkraum/engine/godot-vertical-slice/main.tscn` (2896 Bytes) — 3D-Hauptszene mit CharacterBody3D, Camera3D, WorldBridge und HUD-Panel.
- `/root/werkraum/gordslider/gordslider.html` (110.2 KB) — Autonomes HTML5/JS/Canvas Slider-Game mit Gord-Spielmechaniken.
- `/root/werkraum/gptspieleversuchzeigen/gemini/FLEXTRAWURST_LORE_VIRUS_FUER_GEMINI_v1.md` (34.9 KB) — Manifest für AI-Lore-Integration und Spieldynamik.
- `/root/werkraum/gptspieleversuchzeigen/gemini/flextrawustspielestylergemini.md` (20.1 KB) — UI/UX-Styleguide und Design-Regeln für Spielmodule.
- `/root/werkraum/mdfürvps/kompoase_bauanleitung.md` (15.9 KB) — Bauanleitung für interaktive Kompoase-Elemente und Welträume.
- `/root/werkraum/kosmos/KOSMOS_INVENTAR_UND_DOKUMENTATION.md` (17.3 KB) — Master-Dokumentation der 21 Kosmos-JSONs, Skripte und Harvester.
- `/root/werkraum/kosmos/gesetz_der_absoluten_begehbarkeit.md` (2.3 KB) — Axiomatisches Regelwerk für 3D-Weltbegehbarkeit.
- `/root/werkraum/kosmos/hauptstrasse_151_vermessung.md` (3.1 KB) — Vermessungsdaten Schwelm Hauptstraße (Realkoordinaten für 3D-Welt).
- `/root/werkraum/kosmos/systempromptkonzept_echter_kosmos_harvester.md` (13.9 KB) — Spezifikation des Red-Team Kosmos-Harvesters.
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/AKTUELLE_WAHRHEIT.md` (8.2 KB) & `AKTUELLE_WAHRHEIT.json` (365 KB) — Manifest der 3D-Spielwelt-Traumstruktur.
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/CASINO_ORGANISMUS_MASTER.md` (12.3 KB) — Casino-Organismus Master-Spezifikation.
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/SPIEL_DREILEIB_LEBENDIGKEIT_PERFORMANCE_GRUNDSATZ.md` (10.5 KB) — Grundsätze zur 3D Dreileib-Lebendigkeit.
- `/root/werkraum/welt/schema_welt.sql`, `schema_persoenliche_welt.sql`, `schema_entitaetenschichten.sql`, `schema_traum.sql`, `schema_blasen_tamagotchi.sql` — PostgreSQL Datenbank-Schemata aller Spielsubsysteme.
- `/root/werkraum/welt/api.py` (569 KB) — FastAPI Backend für Weltzustand, Cyberling, Tamagotchi, Trauma, Substanzensystem und Gedankenblasen.
- `/root/werkraum/innenleben/BUILD_STATE.json`, `flarum_feeder.py`, `nodes.py`, `graph.py` — Wesen-Zustandsautomaten & Innenleben.

---

## 2. GESUCHT
Targetierte Dateitypen & Quellkörper im gesamten VPS-Suchraum:
- **Python Skripte (`.py`):** `harvester_r2.py`, `scaffold_100_skripte.py`, `lod_grid_manager.py`, `schleife1_geodaten_verifikation.py`, `schleife2_osm_vektor_extraktion.py`, `schleife3_spatial_dungeons_materialien.py`, `schleife4_redteam_ram_audit.py`, `finalize_bibliotheksatlas_20260801.py`, `api.py`, `cyberling_daemon.py`, `splitter_daemon.py`, `traum_generator.py`.
- **GDScript (`.gd`):** `main.gd`, `world_bridge.gd`.
- **HTML/JS/TS (`.html`, `.js`, `.ts`):** `gordslider.html`, `tts_ui.html`, `flarum_vollexport.html`, Surface-Frontend Skripte in `flextrawurst/`.
- **JSON / JSONL (`.json`, `.jsonl`):** 21 Kosmos-Harvest & Redteam JSONs (`gen1_...`, `gen2_...`, `gen3_...`, `gen4_...`), `manifest_37_regionen.json`, `master_kosmos_stream.jsonl`, `AKTUELLE_WAHRHEIT.json`, `source_registry.json`.
- **Markdown (`.md`):** Lore-, Spezifikations- und Architekturdokumente in `kosmos/`, `engine/`, `gptspieleversuchzeigen/`, `MCP-VPS-CHATGPT-...`, `mdfürvps/`.

---

## 3. ARCHIVE GEÖFFNET
Identifizierte & katalogisierte ZIP-Archive:
1. `/root/FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` (742.18 MB) — Hauptarchiv aller Spiel- & Systembestandteile.
2. `/root/KOSMOS_VOLLSTAENDIG_ALLE_91_DATEIEN.zip` (205.62 MB) — Vollständiges Kosmos 3D-Paket.
3. `/root/KOSMOS_GESAMT_ALLE_DATEIEN.zip` (205.61 MB) — Kosmos Gesamtarchiv.
4. `/root/KOSMOS_3D_PAKET_FUER_CHATGPT.zip` (63.50 KB) — ChatGPT 3D-Kosmos-Schnittstellenpaket.
5. `/root/WUPPER_ENNEPE_KOSMOS_VOLLSTAENDIG.zip` (28.31 KB) — Geodaten- & Vektor-Paket Wupper-Ennepe.
6. `/root/werkraum/kosmos/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` (176.17 MB) — Historische Spiele-Iterationen V1 bis V22.
7. `/root/werkraum/engine/godot-vertical-slice/DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip` (461.23 MB) — Bibliotheksatlas.
8. `/root/werkraum/engine/godot-vertical-slice/DANIELS_BIBLIOTHEKSATLAS_NUR_1337_MDS_2026-08-01.zip` (3.53 MB) & LZMA (3.41 MB).
9. `/root/werkraum/engine/godot-vertical-slice/DANIELS_ECHTER_SEMANTISCHER_BIBLIOTHEKSKOERPER_1337MD_2026-08-01.zip` (2.56 MB).
10. `/root/werkraum/engine/godot-vertical-slice/DANIEL_L33T_OBSIDIAN_ATLAS_2026-08-01.zip` (88.84 KB).
11. `/root/vollexportv2.zip` (1.33 MB).

---

## 4. DATENBANKEN ABGEFRAGT
- **PostgreSQL `flextrawurst` (Port 5432):**
  - `events`: Append-only Event-Stream für Spiel- & System-Events.
  - `persoenliche_welt`, `gedankenwelt`, `tamagotchi_blasen`, `entitaetenschichten`, `traum_sequenzen`, `substances`, `trauma_events`, `user_modules`.
- **Vector DB Chroma (`/root/werkraum/innenleben/chroma_db`):**
  - Einbettungen & semantischer Speicher für Wesen-Zustände & Lore-Kontexte.
- **SQLite / Index-Files:**
  - Registrierungs- & Suchdatenbanken in `MCP-VPS-CHATGPT-...` und `graphify-out/`.

---

## 5. SESSIONS GELESEN
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/sessions/` — Transkripte & Protokolle zum 3D-Spielwelt-Aufbau, Casino-Organismus und Nordschleifen-Replika.
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/01_SESSION_TRANSKRIPT.md` — Transkripte der 3D-Bau-Sessions.
- Synchronisations-Logs unter `_codex/notizen/` & `_gemini/notizen/` bzgl. Godot-Slice, Cyberling-Balancing und Splitter-Physik.

---

## 6. NICHT GELESEN (NOCH UNGEPRÜFTER TEILSCHATTEN / BINÄRMATERIAL)
- Binäre Model- & Texturdateien (`.glb`, `.png`, `.xwd`, `.jpg`) wie `/root/werkraum/engine/godot-vertical-slice/assets/test_cube.glb`, `chatgpt_image_2026_02_22_052054.png`.
- Unkomprimierter Inhalt im Einzel-Zeilen-Vergleich der 742 MB ZIP-Hauptarchive (`FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip`).
- Binary index blobs in `chroma_db/index`.

---

## 7. OFFENE VERDACHTSFÄLLE
1. **Verdachtsfall 1: Spiele V1 bis V22 Archiv:** In `/root/werkraum/kosmos/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` (176 MB) liegen unerschlossene historische Canvas/JS-Spiele (Vorläufer von GordSlider, Casino, Cyberling).
2. **Verdachtsfall 2: Python 3D Mesh & Geodaten-Generatoren:** In `/root/werkraum/kosmos/skripte_77/` und `/root/werkraum/kosmos/geodaten/` befinden sich Skripte zum Realkoordinaten-Import (Schwelm / Wupper-Ennepe), die 3D-Mesh-Strukturen für Godot/Three.js erzeugen.
3. **Verdachtsfall 3: Cyberling & Tamagotchi Subsystem:** Die Endpunkte in `/root/werkraum/welt/api.py` und `/root/werkraum/welt/cyberling_daemon.py` bilden ein spielbares Tamagotchi-System mit Gedankenblasenfeld, das in der Surface noch nicht erlebbar eingebunden ist (Stufe 3 -> 5 auf der Wahrheitsleiter).
