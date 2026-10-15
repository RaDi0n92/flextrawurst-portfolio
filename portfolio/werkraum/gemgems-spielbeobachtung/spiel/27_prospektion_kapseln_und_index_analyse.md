# CT27: Befundbericht Kapsel- & Index-Analyse (Wave 2)

**Autor:** Flash (Kapsel- & Index-Analyst, Wave 2)  
**Datum:** 13.08.2026  
**Zielpfad:** `/root/werkraum/gemgems-spielbeobachtung/spiel/27_prospektion_kapseln_und_index_analyse.md`  

---

## 1. Analyse der SQLite-Indexdatenbanken in `_gpt/gesamtatlas/`

### Untersuchungsobjekte & Dateigrößen:
- `/root/werkraum/_gpt/gesamtatlas/PFADINDEX.sqlite` (61.517.824 Bytes / ~61,5 MB)
- `/root/werkraum/_gpt/gesamtatlas/BEGRIFFSINDEX.sqlite` (631.226.368 Bytes / ~631 MB)
- `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite` (1.502.773.248 Bytes / ~1,5 GB)

### Architektur & Inhalt der Datenbanken:
- **`PFADINDEX.sqlite`:** Enthält die Tabelle `paths` (112.677 indizierte VPS-Pfade) und `root_summary`. Speichert Dateisystem-Metadaten (`path`, `root_name`, `kind`, `size`, `mtime_ns`, `basename`, `parent`, `excluded_reason`) über alle Scan-Wurzeln des VPS (`/root/werkraum`, `/root/flextrawurst`, `/root/.gemini`, etc.).
- **`BEGRIFFSINDEX.sqlite`:** Virtuelle FTS5-Volltext-Tabelle `documents` (`path`, `title`, `headings`, `body`). Speichert den lexikalischen Volltext-Suchindex aller im Werkraum vorhandenen Text- und Code-Dateien.
- **`BEZIEHUNGSREGISTER.sqlite`:** Speichert den strukturellen Beziehungsgraphen (Kanten zwischen Pfaden, Sitzungen, Commits, Claims, Brücken).

### Auswertung bezüglich Spiel-Code & Spiel-Lore:
- **Suchbegriffe (`spiel`, `godot`, `gordslider`, `v21`, `v22`, `quest`):** Treffer in `BEGRIFFSINDEX.sqlite` und `PFADINDEX.sqlite` entstehen dadurch, dass der Volltext-Index-Daemon (`mcp_atlas.py`) den gesamten VPS-Arbeitsraum scannt und sowohl Pfadnamen (z.B. `gordslider.html`, `main.gd`) als auch Volltext-Inhalte aus vorhandenen Dokumenten indiziert.
- **Harte Erkenntnis:** In den SQLite-Datenbanken selbst ist **KEIN NATIV ENGINE-CODE, KEIN SPIELE-LORE-SCHEMATA und KEINE NATIVE SPIEL-DATENBANK** abgelegt. Es handelt sich um generierte **Sekundär-Suchindizes** des MCP Gesamtatlas. Das bedeutet jedoch keineswegs, dass darin "keine archäologisch relevanten Spielinformationen" enthalten sind – sie sind als Suchreservoirs äußerst wertvoll, fungieren jedoch nicht als Primär-Spielkörper.

---

## 2. Analyse der Archiv-Container (.zip)

### A. `DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip` (461.225.586 Bytes / ~461 MB)
- **Quell- / Entpackungspfad:** `/root/werkraum/engine/godot-vertical-slice/bibliotheksatlas_20260801/`
- **Inhalts-Struktur:**
  - `README.md`: Dokumentiert den Bestand von 123.776 Dateien, 13,66 GiB Quellmaterial, 25.870.535 Nutzertokens und 1.829.460 eindeutigen Wörtern.
  - `md/` Ordner: Enthält exakt **1.337 Markdown-Dateien** (Wort-Index-Karten wie `0038_WORT_path.md`, `0063_WORT_das.md` sowie Methodik-Dokumente `001_METHODIK.md`, `002_PROVENIENZ.md`).
  - `daten/` Ordner: Enthält `bibliotheksatlas.sqlite` (SQLite-Token-Datenbank), `DATEI_INVENTAR.csv`, `DUPLIKATGRUPPEN.json`, `SEMANTISCHE_DATEINAMEN.csv`, `WORT_HAEUFIGKEIT.tsv`, `WORT_KONTEXTE.jsonl.gz`.
- **Harte Erkenntnis:** Der 461 MB Bibliotheksatlas ist ein **reiner linguistischer Text- & Token-Korpus** von Daniels VPS-Arbeitsraumstand vom 01.08.2026. Er enthält **NULL Spiel-Code, NULL 3D-Assets und NULL Spiel-Engine-Körper**.

### B. `KOSMOS_3D_PAKET_FUER_CHATGPT.zip` (63.504 Bytes / ~63,5 KB)
- **Quell- / Entpackungspfad:** `/root/werkraum/kosmos_paket_chatgpt/`
- **Inhalts-Struktur (11 Dateien):**
  1. `00_UEBERGABE_AN_CHATGPT_LIES_MICH.md`: Master-Anleitung mit einem **JavaScript / Three.js Referenz-Codeblock** (ab Zeile 62) zur späteren Portierung auf ein JS-Game-Frontend. *(Hinweis: Die Zip enthält keine eigenständige .js Datei).*
  2. `manifest_38_regionen.json` (52.682 Bytes): JSON-Manifest aller 38 Kosmos-Regionen (Schwelm, Wuppertal, Berlin, Nordschleife etc.) mit Geokoordinaten, Bounding-Boxen, Flächen und Layern.
  3. `lod_grid_manager.py` (5.059 Bytes): Python-Referenzklasse für dynamisches 3-Stufen LOD-Streaming (LOD 1: 50m Voxel-Radius, LOD 2: 500m Stadtteil-Vektor, LOD 3: Makro-BBox).
  4. `kosmos_trockenlauf_simulation.py` (11.619 Bytes) & `kosmos_trockenlauf_results.json` (70.588 Bytes): Rechnerische Simulation der Voxel-Mengen & RAM-Limits.
  5. `redteam_socrates_loop.md` (40.721 Bytes): 8-facher Sokratischer Audit-Bericht (3D-Akustik, Sabine-Formel, Manifoldness, Raumschichten).
  6. `skill_city_archaeologist_3d_reconstructor.md` (17.878 Bytes): Stadtarchäologischer Leitfaden zur 3D-Voxel-Reconstruction aus 2D-Grundrissen.
  7. `echte_assets_und_quellen.md` (7.438 Bytes): Analyse realer 3D-Datenquellen (OSM, Sketchfab, Google 3D Tiles).
  8. `kosmos_datenquellen_scan.py`, `gen1_r2_harvest.md`, `2026-07-24_gemini_session.md`.
- **Harte Erkenntnis:** Das Kosmos-3D-Paket ist ein **KONKRETES SPIEL-ARCHITEKTUR- & SPEZIFIKATIONS-PAKET**. Es enthält reale Raum-Manifeste (`manifest_38_regionen.json`), funktionale LOD-Streaming-Algorithmen (`lod_grid_manager.py`) und JS/Three.js-Spezifikationen. *(Hinweis: Binäre 3D-Meshes wie `.glb` sind in dieser Zip nicht enthalten, da diese prozedural gestreamt werden).*

---

## 3. Gesamtevaluierung: Konkrete Spiel-Artefakte vs. Allgemeine Infrastruktur- & Dokumentationsmasse

| Reservoir / Kapsel | Dateigröße | Hauptinhalt | Klassifizierung |
| :--- | :--- | :--- | :--- |
| `BEGRIFFSINDEX.sqlite` | 631 MB | FTS5 Volltextindex `documents` aller Arbeitsraum-Dateien | **Infrastruktur / Plattform-Suchindex** |
| `BEZIEHUNGSREGISTER.sqlite` | 1,5 GB | Graph-Beziehungen aller Pfade, Sitzungen, Commits | **Infrastruktur / Plattform-Suchindex** |
| `PFADINDEX.sqlite` | 61,5 MB | Pfadregister `paths` (112.677 Pfade) aller VPS-Wurzeln | **Infrastruktur / Plattform-Suchindex** |
| `DANIELS_BIBLIOTHEKSATLAS_...zip` | 461 MB | 1.337 Wort-Index MDs + SQLite Token-Statistiken | **Linguistische Dokumentationsmasse** |
| `KOSMOS_3D_PAKET_FUER_CHATGPT.zip` | 63,5 KB | 38-Regionen Manifest, LOD Manager, Three.js Client-Code | **Konkretes Spiel-Artefakt (3D Kosmos Spec & Streaming Code)** |
