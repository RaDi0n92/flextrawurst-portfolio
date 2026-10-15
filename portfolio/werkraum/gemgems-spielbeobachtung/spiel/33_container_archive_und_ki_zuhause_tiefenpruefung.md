# Tiefenprüfungs-Bericht: Container- & Archiv-Tiefenprüfer (Achse 7 & 8: ZIPs, Kapseln, KI-Zuhause-Archive)

**Prüfer-Identität:** Container- & Archiv-Tiefenprüfer (Achse 7 & 8)  
**Empfänger:** Parent Agent (`039137f2-edaa-4845-830f-159c5c0b8e47`)  
**Prüfobjekte:** Alle ZIP-Archive, Kapseln, KI-Zuhause-Archive (`_gpt/`, `_claude/`, `_codex/`, `_kimi/`, `_gemini/`), SQLite-Datenbanken, JSON-Manifeste, Screenshots und 3D-Game-Assets im Werkraum.

---

## 1. Vollständige Bestandsaufnahme aller ZIP-Archive & Kapseln

Es wurden **17 primäre ZIP-Archive und Kapseln** auf dem VPS identifiziert, klassifiziert und in ihren Extraktionszuständen auditiert:

### A. Bibliotheksatlas & Kapseln
1. **`DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip`** (461,23 MB)
   - *Pfad:* `/root/werkraum/engine/godot-vertical-slice/DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip`
   - *Inhalt:* Vollständiger Bibliotheksatlas bestehend aus genau 1.337 Markdown-Dateien, der zentralen SQLite-Datenbank `bibliotheksatlas.sqlite` sowie Wort-Häufigkeits- (TSV) und semantischen Dateinamen-Katalogen (CSV).
2. **Varianten des Bibliotheksatlas (Derivate):**
   - `DANIELS_BIBLIOTHEKSATLAS_NUR_1337_MDS_2026-08-01.zip` (3,53 MB) – Reine Markdown-Sammlung ohne SQLite.
   - `DANIELS_BIBLIOTHEKSATLAS_NUR_1337_MDS_LZMA_2026-08-01.zip` (3,41 MB) – LZMA-komprimiert.
   - `DANIELS_ECHTER_SEMANTISCHER_BIBLIOTHEKSKOERPER_1337MD_2026-08-01.zip` (2,56 MB) – Semantischer Kernkörper.
   - `DANIEL_L33T_OBSIDIAN_ATLAS_2026-08-01.zip` (88,8 KB) – Leichter Obsidian-Atlas.
3. **`GESAMTATLAS_KAPSEL_AKTUELL.zip`** (7,96 MB)
   - *Pfad:* `/root/werkraum/_gpt/gesamtatlas/GESAMTATLAS_KAPSEL_AKTUELL.zip`
   - *Inhalt:* Kapsel-Snapshot der Gesamtatlas-Struktur (Claimregister, Dienstregister, Knotenverträge, Systemregister, Begriffsindex-Analysen).

### B. Kimi- & KI-Zuhause-Archive
4. **`kimi.zip`** (53,9 KB)
   - *Pfad:* `/root/werkraum/gptspieleversuchzeigen/kimi-web/kimi.zip`
   - *Inhalt:* 3D-Stadt-Archäologe & 3D-Reconstructor Skills für Kimi, Manifest der 37 Kosmos-Regionen, Trockenlauf-Simulationen und Redteam-Sokrates-Schleifen.

### C. Historische Game- & Quest-Sammelarchive (v1 bis v22)
5. **`FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip`** (176,17 MB)
   - *Pfad:* `/root/werkraum/kosmos/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip`
   - *Inhalt:* Das historische Gesamtarchiv der Flextrawurst-Spiele-Iterationen v1 bis v22.
6. **`das neuuusteee(1).zip`** (29,26 MB)
   - *Pfad:* `/root/werkraum/gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/das neuuusteee(1).zip`
   - *Inhalt:* v22 Quest-Simulationen und Berichts-Payloads.
7. **`das neuuusteee-0.5(1).zip`** (55,65 MB)
   - *Pfad:* `/root/werkraum/gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/das neuuusteee-0.5(1).zip`
   - *Inhalt:* Wrapper-Archive für v21/v22 Originale (enthält verschachtelte ZIPs).
8. **`flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip`** (45,41 MB)
   - *Pfad:* `/root/werkraum/gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/`
   - *Inhalt:* v22 Finaler Questkosmos & Redteam-Belege.
9. **Extrahierte verschachtelte Archivkörper (unter `/root/werkraum/engine/flextrawurst-game/extracted_sources/wrappers/`):**
   - `flextrawurst_spielewelt_supermaximal_bauring4_v21_final.zip`
   - `flextrawurst_v21_berichte_belege_screenshots_outro.zip`
   - `flextrawurst_dust_echo_questkosmos_v22_berichte_redteam_belege.zip`
   - `flextrawurst_dust_echo_questkosmos_v22_final.zip`

### D. Wurzel- & Vollarchiv-Container
10. **`FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip`** (742,18 MB) – Root-Vollcontainer.
11. **`KOSMOS_GESAMT_ALLE_DATEIEN.zip`** (205,61 MB) & **`KOSMOS_VOLLSTAENDIG_ALLE_91_DATEIEN.zip`** (205,62 MB).
12. **`KOSMOS_3D_PAKET_FUER_CHATGPT.zip`** (63,5 KB) & **`WUPPER_ENNEPE_KOSMOS_VOLLSTAENDIG.zip`** (28,3 KB).
13. **`vollexportv2.zip`** (1,33 MB) – Flarum/System-Vollexport v2.

---

## 2. Tiefenprüfung der KI-Zuhause-Bestände

Die Untersuchung der KI-Zuhause-Ordner (`_gpt/`, `_claude/`, `_codex/`, `_kimi/`, `_gemini/`) ergab folgende verstreute Quellen:

- **`_gpt/gesamtatlas/`**:
  - Central Mega-SQLite Databases:
    - `BEZIEHUNGSREGISTER.sqlite` (1,50 GB)
    - `BEGRIFFSINDEX.sqlite` (631,22 MB)
    - `PFADINDEX.sqlite` (61,51 MB)
  - Globale JSON-Register: `PROJEKTREGISTER.json` (38,45 MB), `AENDERUNGSSTROM.jsonl` (25,78 MB), `SESSIONREGISTER.json` (687 KB).
  - Screenshots: `_screenshot_megavault.png` (108 KB).
- **`_gpt/mcp_arbeitskoerper/`**:
  - `omega_monsterlabor/`: Versteckte Schema- und Entitätsbestände für Monster-/Wesen-Generierung.
- **`_kimi/` & `gptspieleversuchzeigen/kimi-web/`**:
  - `kimi.zip` mit 37-Regionen-Manifest (`kosmos_regions_manifest.json`, 50,4 KB) und `kosmos_trockenlauf_simulation.py`.
- **`_claude/`, `_codex/`, `_gemini/`**:
  - Spiegel, Resonanzfelder (`RESONANZFELD.md`), Grundriss-Spiegelungen (`_import_*_grundriss`), Obsidian-Karten und Flarum-Analysen (`codex_claude_flarum_analyse`).

---

## 3. Verstreute Spiel-Assets, SQLite-Datenbanken & Manifeste

### A. Aktiver Godot-Vertikalschnitt & unified Game Body
- **Godot 4.3 Engine Project:** `/root/werkraum/engine/godot-vertical-slice/` (`project.godot`, `main.tscn`, `assets/`, `scripts/`, `rings/`, `deploy/`).
- **Kanonischer Flextrawurst-Game-Strukturkörper:** `/root/werkraum/engine/flextrawurst-game/` (enthält `extracted_sources/`, `game/`, `proofs/`, `manifests/`).
- **HTTP-World-Bridge:** Godot-Bridge auf Port `18092` (getestet und verifiziert via append-only JSONL event stream).

### B. 3D Kosmos-Assets & Harvester-Daten (`/root/werkraum/kosmos/`)
- Kenney 3D Baukörper (12,14 MB), 66 Fahrzeug-Skripte (`fahrzeuge_66/`), 111 Waffen-Definitionen (`waffen_111/`), 88.888 Wesen-Entitäten (`wesen_88888/`), Biome, Dungeons, Materialien, Geodaten.
- Harvest-JSONs: `gen1_audio_alpha_harvest.json`, `gen1_city_bunker_alpha_harvest.json`, `gen1_gta_metropolen_runde2_harvest.json`, `gen1_schwelm_alpha_harvest.json`.
- Redteam-JSONs: `gen2_casino_gord_math_redteam.json`, `gen2_city_dungeons_math_redteam.json`, `gen2_schwelm_math_redteam.json`.
- Interior & Replica-JSONs: `gen3_schwelm_housing_interior.json`, `gen4_casino_gord_monument.json`, `gen4_nordschleife_replica.json`.
- Regionen-Manifest: `manifest_37_regionen.json` (52,6 KB).

### C. SQLite-Datenbanken im Werkraum
1. `BEZIEHUNGSREGISTER.sqlite` (1,50 GB) in `_gpt/gesamtatlas/`
2. `BEGRIFFSINDEX.sqlite` (631,22 MB) in `_gpt/gesamtatlas/`
3. `PFADINDEX.sqlite` (61,51 MB) in `_gpt/gesamtatlas/`
4. `bibliotheksatlas.sqlite` in `DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip` / `bibliotheksatlas_20260801/daten/`

### D. Bild- & Screenshot-Nachweise
- Godot Headless Boot Screenshot: `proofs/godot_vertical_slice_001/screenshot-20260725T125229Z/screenshot.png` (Xvfb/OpenGL 3D-Beweis).
- Megavault Screenshot: `/root/werkraum/_gpt/gesamtatlas/_screenshot_megavault.png`
- Playwright-Megasuche-Screenshots: `megasuche_all_9_features.png`, `megasuche_unwidertreibbarer_beweis.png` (1,68 MB), `megasuche_v3_geni_query.png`, `megasuche_v3_sqlite_inspector.png`.
- Obsidian GUI Screenshots: `obs_front.jpg`, `obs_jetzt.jpg`, `obs_nach_fix.jpg`, `obs_picker.jpg`, `obs_raised.jpg`, `obs_swiftshader.jpg`.

---

## 4. Abgleich: Primärquellen vs. Sekundärindizes (Wahrheits-Audit)

Gemäß Verfassung und Prüfauftrag wurde der Bestand an Primärquellen (ZIPs, GLBs, Code-Skripte) gegen Sekundärindizes (`GAME_MANIFEST.json`, `GEBAUT_VS_SIMULIERT_VS_GEPLANT.md`, `QUELLEN_UND_HERKUNFT.md`) geprüft:

1. **Echt gebaut & ausgeführt vs. simuliert:**
   - **Bestätigt:** Ein funktionsfähiger, startbarer Godot 4.3 Vertikalschnitt mit lokaler Python-Bridge auf Port `18092` ist real vorhanden, lauffähig und durch Xvfb-Screenshots belegt.
   - **Simuliert / Datensatz:** Die umfangreichen v1-v22 Questketten, 37 Regionen, Nordschleifen-Replik, Casino Gord, Monsterlabor und GTA-Metropolen existieren als physische JSON-Harvests und ZIP-Archive, sind aber **noch nicht in ein einziges zusammenhängendes Godot-Gesamtspiel integriert**.
2. **Archiv-Integrität:**
   - Alle extrahierten Archive in `extracted_sources/` wurden via CRC-32 und SHA-256 verifiziert.
   - Der abgeleitete 333-MD-Transferkörper (`FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.generated-2026-07-25.zip`) ist in den Manifesten korrekt als `generated` klassifiziert und wird nicht fälschlich als Original-Upload ausgegeben.
