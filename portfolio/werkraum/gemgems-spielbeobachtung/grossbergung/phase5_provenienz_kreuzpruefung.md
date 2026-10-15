# Phase 5 – Provenienz-Kreuzprüfung (Konvergenz-Register)

**Dokument-ID:** `phase5_provenienz_kreuzpruefung.md`  
**Erstellt am:** 2026-08-13 (Überarbeitet nach Phase-4-Primärquellentest)  
**Status:** PRIMÄRQUELLENVERIFIZIERT & STRUKTURELL AUDITIERT  
**Eingangsdaten:** Phase 1 Manifeste $\cap$ Phase 3 Redteam $\cap$ Phase 4 Primärquellen-Kreuzprüfung  

---

## 🏛️ KERN-KONVERGENZ (Unzweifelhaft verifizierter Bestand)

Nach der unzerstörbaren Fünf-Schichten-Doktrin existieren folgende **fünf Kern-Schichten** auf dem VPS, die durch Phase 1, Phase 3 und Phase 4 konvergent an Primärdateien nachgewiesen sind:

---

### Schicht 1: Entwurf / Spezifikation (Draft / Spec)
- **18 MAXUS Pflichtfragen & Ontologie:** Markdown-Spezifikationen in `v21/docs/` und `markdown_archive/`.
- **12 Vorbild-Spiele Synthese:** Disco Elysium, RimWorld, Kenshi, Skyrim etc. als Entwurfsvorgaben verankert.
- **Casino Organismus Master (`CASINO_ORGANISMUS_MASTER.md`):** Reine Prosatext-Spezifikation (221 Zeilen Markdown). Exakt **0 3D-GLTF/OBJ Meshes** auf dem VPS.
- **DUST 88.888 Wesen & Questkosmos:** Python-Generator `build_v22_questkosmos.py` berechnet Kombinatorik im Arbeitsspeicher.

---

### Schicht 2: Prototyp / Code (Prototypes & Codebases)
- **HTML/JS Browser-Prototypen (v1–v21):** Single-Page Browser-Interfaces (`PLAY_FLEXTRAWURST_V21.html`).
- **Headless Playwright Integrationstests:** 13 Integrationstests (`test_gate_01.py` bis `test_gate_13h.py`) testen JS-Arrays im Browser-DOM (`FW_GAME.renderer.faces`) und mocken `localStorage` über flüchtige JS-Objekte.
- **Godot 4.3 Vertikalschnitt (Ring 001 & Ring 002):** Godot C#/GDScript Engine-Code (`engine/godot-vertical-slice/`). Ring 002 nutzt Godot-Primitive-Meshes (`BoxMesh`, `QuadMesh`) belegt mit 2D PNG-Texturen (`marquee_gordslider.png`, `reels_base.png`).
- **Python-Skript-Reservoir:** 101 prozedurale Skripte in `kosmos/skripte_77/`.

---

### Schicht 3: Realwelt-Geografie (Real Geodata & Spatial)
- **System-Anker (0,0,0):** Schwelm Hauptstraße 151 (Lat: 51.2882° N, Lon: 7.2941° E, 213m ü. NHN).
- **DGM1 Höhendaten:** 1m Terrainnetz der 300 km² Wupper-Ennepe-Region.
- **OpenData NRW ALKIS 3D LoD2 / OSM:** `KOSMOS_3D_PAKET_FUER_CHATGPT.zip` (63,5 KB) enthält 0 Geometriedateien. Die 101 Skripte senden dynamische HTTP-Overpass API Queries (`https://overpass-api.de/`) und verarbeiten Gebäude als GeoJSON.

---

### Schicht 4: Tamagotchi / Plattform-Kernel (Live Infrastructure)
- **PostgreSQL Kernel (`DB=flextrawurst`, Port 5432):** Append-Only `events` Tabelle mit SSE-Stream (`GET /events/stream`, Port 8030). Tabellen für Wesen existieren als ruhende Zielstrukturen.
- **Surface Leitstand (`flextrawurst_surface.html`, Port 8787):** Zweisprachige UI zur Monitoring-Einsicht.

---

### Schicht 5: AI-Strom & Werkraum-Geschichte (Provenance & History)
- **Urknall:** `/root/^c` (22./23.03.2026) & 4-Gewinnt Partie gegen `GPT-5.6-sol-hoch`.
- **AI-Zuhause:** Read-Only Mirroring unter `_claude/`, `_gpt/`, `_codex/`, `_kimi/`, `_gemini/`, `_claudeweb/`.

---

## 🛑 AN PRIMÄRQUELLEN GEPRÜFTE VERATIONEN

1. **1.337 Loops:** `LOOP_BEWEISE.jsonl` enthält konstant identische Hashes (`rag_a_sha256`, `rag_b_sha256`, `synthesis_sha256`). Zwischenschritte 1–1336 wurden gelöscht (`readable_intermediates: 0`). Loop 1337 ist identisch mit `GESAMTBESCHREIBUNG.md`.
2. **2.889 Dateien vs. 1.691 Hashes:** In `VOLLZAEHLUNG_2026-07-26.json` verifiziert. 1.198 Duplikate durch verschachtelte Archiv-Entpackung (`nested_archives` & `runtime_snapshots`).
3. **19 Missing Originale:** Scan über 4,35 Mio. Dateinamen bestätigt 19 exakt fehlende Original-Uploads. `FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` existiert nicht auf dem VPS.
