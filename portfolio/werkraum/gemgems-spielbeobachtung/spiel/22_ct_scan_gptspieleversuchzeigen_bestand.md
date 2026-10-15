# Archäologischer CT-Scan: `gptspieleversuchzeigen` Bestand

## 1. Topografische Übersicht
Der Bestand `/root/werkraum/gptspieleversuchzeigen/` ist das monumentale Relikt der sogenannten "KI-Karnevals-Parade" (wie in `GEMINI.md` referenziert) – einer gigantischen Eruption von Subagenten-Output, Konzeptions-Loops und Weltbau-Träumen.
Er gliedert sich in drei Hauptausgrabungsstätten:
1. `input/` (Das tief gegliederte, aber flache Text- und Konzeptarchiv)
2. `gemini/` (Die Wahrheits- und Steuerungsviren für Gemini)
3. `kimi-web/` (Der Übergang zu echtem Code, Tooling und strukturierten Daten)

## 2. Spielkonzepte, Mechaniken & Agenten-Spuren
Der Bestand dokumentiert den umfassenden "Flextrawurst-Weltenkosmos", der von der Keimzelle "Schwelm (Hauptstraße 151)" auf einen globalen Maßstab skaliert:
- **Metropolen & Festungsstädte:** 13 GTA-artige Gegenwartsstädte (inkl. Untergrund-Katakomben, Geisterbahnhöfen) und 13 Skyrim-artige historische Festungen (z.B. Carcassonne, Derinkuyu).
- **Prospektierung & Redteam-Pipelines:** Agentengesteuerte Architektur-Scans (DGM1, OSM) und eine "1.337-Runden Redteam & Refinement Schleife" zur Sicherstellung mathematisch fehlerfreier 3D-Raumvolumina.
- **Weltenbau & Lore:** Ein Rocky-Horror-artiger Start des Spiels (Stromschlag, Zeitensprung), das "Dust-Echo-Quest-System", 8 Entitäten (z.B. Schorschel, dak+gord, GENI) und Fraktionen.
- **Agenten-Spuren:** Iterative Subagenten-Aufträge und Pläne (wie der "Tree of Truth" zur Variantenbewertung) manifestieren sich in Dateien wie `gen1_r2_harvest.md` und `redteam_socrates_loop.md`.

**Hervorzuheben (`flextrawustspielestylergemini.md`):**
Dieses Dokument dient als rigoroser "Prospektierungs-Architektur"-Anker und Regelwerk. Es normiert:
- Die 5 Wahrheitsgrade für Assets (z.B. `[BESTÄTIGT]`, `[LOKALE ERZÄHLUNG]`).
- Den harten Maßstab (1 Meter = 1 Block).
- Fundamentale Gameplay-Mechaniken: 100% Innenraum-Begehbarkeit aller Gebäude, voll nutzbare Verkehrsinfrastruktur, physisch interagierbare Objekte (inkl. Taschendiebstahl/Schlossknacken) sowie das legendäre *Wuppertal Super-Mega-Duper-Casino*.

## 3. Trennung: Flacher Text/Prompt vs. Strukturelle Daten/Code

### A. Flacher Text / Prompts / Lore (Zuckerwatte & Konzepte)
*Diese Schicht ist konzeptuell tief, fungiert aber rein als prompt-gerichtetes Narrativ (Markdown).*
- **Der gesamte `input/` Ordner:** Ein textlicher Ozean. Enthält 17 thematische Kapitel (die durch Zip-Entpackung in der Verzeichnisstruktur ein 8.3-Format wie `01_PLA~1` bis `16_QUE~1` erhielten, im `MANIFEST.json` jedoch voll ausgeschrieben sind). Darin liegen hunderte Markdown-Dateien zu "Spielidentität", "Welt_Geografie", "Skills_Masteries", "Redteam_Loops" sowie "Daniels_Rohtexte_isoliert". Ein `INDEX.html` navigiert diesen Sumpf aus Ideen.
- **Der `gemini/` Ordner:** Beherbergt `FLEXTRAWURST_LORE_VIRUS_FUER_GEMINI_v1.md` und `flextrawustspielestylergemini.md`. Dies sind hochentwickelte Meta-Prompts, die die wilde Lore für zukünftige AI-Ströme zähmen und als verbindliche Grundpfeiler setzen.
- **In `kimi-web/` (Textanteile):** Strategiepapiere und Ernteberichte wie `echte_assets_und_quellen.md`, `skill_city_archaeologist_3d_reconstructor.md`, `redteam_socrates_loop.md` und `gen1_r2_harvest.md`.

### B. Strukturelle Daten & Code (Das maschinenlesbare Fundament)
*Hier endet das Konzept und harte Assets / echte Logik beginnen.*
- **Strukturelle Daten (JSON):**
  - `kimi-web/kosmos_regions_manifest.json`: Reale, strukturierte Bounding-Definitionen für 36 Ausgrabungsregionen.
  - `kimi-web/kosmos_trockenlauf_results.json`: Eine detaillierte Volumen- und RAM-Simulation (dokumentiert 3,8 Billionen LOD0 Voxel).
- **Code (Python):**
  - `kimi-web/kosmos_datenquellen_scan.py`: Ein ausführbares Skript, das über die Overpass-API reale Geometrien (Gebäude, Wasserwege, Straßen) abgreift.
  - `kimi-web/kosmos_trockenlauf_simulation.py`: Der Simulator zur Berechnung von Chunkgrößen und Voxelauflösungen auf dem Dateisystem.
- **Archive:**
  - `kimi-web/kimi.zip` (Mutmaßlich das Roharchiv, das die verkürzten Ordner in `input/` hervorgebracht hat).
