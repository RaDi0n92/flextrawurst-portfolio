# Tiefenanalyse: Technischer Entwicklungsstammbaum der Spiellogik (Von HTML bis Godot) (Achse 2 & 3)

**Analyst:** Research Subagent (Game-Engine & Prototypen-Archäologe: Achse 2 & 3)  
**Empfänger:** Parent Agent (`039137f2-edaa-4845-830f-159c5c0b8e47`)  
**Methode:** Zeilen- und pfadgenaue Analyse des physischen Bestands auf dem VPS. Strikte anti-behauptungsbasierte Klassifikation nach Nackten Fakten.

---

## 1. Übersicht & Gesamtstruktur des Spielkörpers (`flextrawurst-game`)

### Kanonischer Spielkörper
- **Hauptpfad:** `/root/werkraum/engine/flextrawurst-game/`
- **Kanonischer Anlegezeitpunkt:** 25. Juli 2026 (durch GPT-5.6-sol-hoch).
- **Harte Zählung (25./26. Juli 2026):**
  - Physische Dateien: **2.889**
  - Verzeichnisse: **395**
  - Gesamtgröße: **1.243.615.121 Bytes** (~1,24 GB)
  - Eindeutige SHA-256 Hashes: **1.691** (455 Duplikatgruppen mit 1.198 Mehrausprägungen)
  - Nachgewiesene fehlende Originaldateien: **19** (in Auditberichten unter `99_OFFENE_LUECKEN/` dokumentiert).

### Struktur des kanonischen Verzeichnisbaums
1. `00_START_HIER/`: Eingangstür, `ORDNERPLAN.md`, `STRUKTURVERTRAG.md`, `DATEIINVENTAR.csv` (828 KB), `WAHRHEITSZAEHLUNG.json`.
2. `01_AKTIVES_SPIEL/`: Symlink auf `game/` (aktuelle native Godot-Runtime).
3. `02_SPIELQUELLEN/`: Symlinks auf 10 historische Quell-Module (v1-v22 Chronik, v21 Spielewelt, v21 Berichte, v22 Dust-Echo, Gordslider).
4. `03_ARCHIVE_UND_TRANSFERKOERPER/`: Trennung in `01_UNVERAENDERTE_ORIGINALARCHIVE`, `02_GENERIERTE_TRANSFERKOERPER`, `03_WIEDERGEWONNENE_INNERE_ARCHIVE`.
5. `04_RETTUNG_UND_UEBERGABEN/`: 338-MD Rettungskörper und historische Session-Übergaben.
6. `05_TESTS_UND_BEWEISE/`: screenshots, GLB-Prüfkörper (`test_cube.glb`), Bridge-Roundtrip-Logs.
7. `06_MANIFESTE_UND_ZAEHLUNG/`: Herkunfts- & Hash-Manifeste (`MANIFEST.json`).
8. `07_WERKZEUGE_UND_MIGRATION/`: Migrations- & Prüfskripte (kein Spielinhalt).
9. `08_SEPARATE_SPIELTEILE/`: `01_GORDSLIDER_EINGEZOGEN` (HTML-Quelle) und `02_GODOT_BAUQUELLE` (`/root/werkraum/engine/godot-vertical-slice/`).
10. `09_URSPRUNGSDATEN_AUSSERHALB/`: Symlinks zu `/root/werkraum/kosmos/` und `/root/werkraum/gptspieleversuchzeigen/input/`.
11. `99_OFFENE_LUECKEN/`: Audit-Bericht für 19 unaufgelöste Originaldateien.
12. `game/`: `godot_vertical_slice_001/` (Aktiver Godot 4 Vertikalschnitt).
13. `tests/` & `proofs/`: Headless Godot Smoke-Tests & Log-Belege.
14. `extracted_sources/`: Entpackte ZIP-Archive (`historical_runtime/v1_v22_bundle/`, `vps_live/gordslider/`).
15. `markdown_archive/`: Wortgetreu übertragene Markdown-Reihen (`v1_v22_rettungskoerper/`).
16. `Versuch-einer-Gesamtbeschreibung/`: Nicht mitgezählter Beschreibungskörper (`ENTWICKLUNGSCHRONIK.md`, `GESAMTBESCHREIBUNG.md`, `MIKRODETAILREGISTER.csv` mit 1.337 Einträgen).

---

## 2. Der Entwicklungsstammbaum: Von v1 bis v22

| Version | Status | Typus & Befund | Hauptpfade & Quellen |
|---|---|---|---|
| **v1 – v7** | `REKONSTRUIERT` / `UNSICHER` | Frühe Konzept- & Freitext-Phase. Keine separaten Paketkörper erhalten; Erwähnungen in späteren Versionskarten nachgewiesen. | `markdown_archive/v1_v22_rettungskoerper/03_SES~1/FW-VERSION-01` bis `07` |
| **v8 – v13** | `REKONSTRUIERT` | Bauregeln, Redteam-Runden R1–R3, Tree-of-Truth-Matrizen und Pflichtfragen. Übergang von Vision zu harten Verträgen. | `extracted_sources/.../05_VERTRAEGE_ARCHITEKTUR_UND_BAUREGELN_V13_BIS_V20/` |
| **v14 – v17** | `BESTÄTIGT` | HTML5 Canvas-Runtimes. Erste spielbare 2D/pseudo-3D Web-Prototypen (`PLAY_FLEXTRAWURST_V15_1.html` - 193 KB; `PLAY_FLEXTRAWURST_V17.html` - 225 KB). | `.../15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V17.html` |
| **v18 – v20** | `BESTÄTIGT` | Zeitweltquellen, Vollständige Neulesung V20 (`00_VOLLSTAENDIGE_NEULESUNG_V20.json`, 30.382 Zeilen). | `.../07_V21_FRAGEN_KOLLISIONEN_UND_PFLICHTMATRIZEN/FINALER_V20_BAUAUFTRAG/` |
| **v21** | `BESTÄTIGT` | **Supermaximal-Bauring 4.** Vollständige monolithische HTML5/JS-Canvas-Runtime (`PLAY_FLEXTRAWURST_V21.html` - 544.712 Bytes, 3.299 Zeilen). Enthält 12 Gates, 88.888 Wesen-Systeme, taktische Pause, Untergrund, Skill-Bäume und Zeit-Traversal UI (`#futureShock`). | `.../15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V21.html` |
| **v22** | `BESTÄTIGT` | **Dust-Echo Questkosmos.** Erweitert v21 um Quest-Ökonomie, Verhaltens-Spiegelung, alternative Zukünfte und Redteam-Runden R21–R26. (Keine neue HTML-Datei, sondern Simulations- & Datenschicht über v21). | `.../10_V22_QUESTARCHITEKTUR_DUST_ECHO_UND_SPIELERSPIEGEL/` |

---

## 3. Die Abnahme-Gates: Gate 01 bis Gate 13H

Die Gate-Architektur liegt unter `extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/06_V21_BAUGATES_UMSETZUNG_UND_ABNAHME/` (147 Dokumente) und wurde über Playwright-Skripte unter `.../V21/tests_v21/` automatisiert geprüft.

### Detaillierte Gate-Matrix & Testergebnisse

| Gate ID | Bezeichnung / Fokus | Testskript (Python/Playwright) | Ergebnis-Artefakt | Befund & Teststatus |
|---|---|---|---|---|
| **Gate 00** | Baseline & V20-Neulesung, Testisolierung | `test_modular_index_v21.py` | `00_VOLLSTAENDIGE_NEULESUNG_V20.json` | Baseline gesetzt, Isolierung des Normalstands bestätigt. |
| **Gate 01** | 3:33 Prolog & Zukunftsreise (-3.333j / +333 Step) | `test_gate_01_opening.py` | `GATE_01_RESULT.json` | 6/6 Tests bestanden. Prolog-Frage speichert erste Spur. |
| **Gate 02** | Luftfahrzeuge, Versorgungsnetze, Testmodus | `test_gate_02_traversal.py` | `GATE_02_RESULT.json` | 10/10 Tests bestanden. F10 Testmodus isoliert. |
| **Gate 03** | Mastery, Skillbäume, Handwerk, Dust-Magie | `test_gate_03_mastery_magic.py` | `GATE_03_RESULT.json` | **Abbruch/Stop:** Bei Erstrunde 10/11 bestanden (rote Zahl wegen fehlender visueller Magie-Geometrie). Danach repariert & freigegeben. |
| **Gate 04** | Untergrund, Erze, vertikales Bauen, Lebendgestein | `test_gate_04_underworld.py` | `GATE_04_RESULT.json` | 14/14 bestanden. Abbau erfordert explizite Zustimmung. |
| **Gate 05** | Flotten-Testzone (Straße, Wasser, Schiene, Startbahn, Flugring) | `test_gate_05_fleet_testzone.py` | `GATE_05_RESULT.json` | 16/16 bestanden. 3 Fahrzeugfamilien auf Testkurs verifiziert. |
| **Gate 06** | 88.888 AI-Wesen, Beziehungsnetz, Perspektivabspaltung | `test_gate_06_entity_world.py` | `GATE_06_RESULT.json` | Autonome Forschung bei ausbleibendem Fortschritt nachgewiesen. |
| **Gate 07** | Zeitkörper (4.096 Vergangenheit-Adressen, +333 Zukunft) | `test_gate_07_time_atlas.py` | `GATE_07_RESULT.json` | Stabil adressierte Vergangenheits-Rückkehr verifiziert. |
| **Gate 08** | Fortnite-Modell (Karten-Editor, Konzerte, Archiv ohne FOMO) | `test_gate_08_creator_events.py` | `GATE_08_RESULT.json` | Freie Kartenbearbeitung & Archiv-Events bestätigt. |
| **Gate 09** | Skyrim-Kern (Taktische Pause, Ausrüstung, Zauber, Loot) | `test_gate_09_combat_loot_pause.py` | `GATE_09_RESULT.json` | Gameplay-Stopp für Inventar/Zauber in Dungeons verifiziert. |
| **Gate 10** | Großgeografie (Wüste, Berge, Gletscher, Großstadt, Küste) | `test_gate_10_epic_world.py` | `GATE_10_RESULT.json` | Nahtlos begehbare Biome mit Story-Ankern verifiziert. |
| **Gate 11** | Modularität & Objektbiografie (auswechselbare Teile) | `test_gate_11_modular_workshop.py` | `GATE_11_RESULT.json` | Teil-Austausch, Verzauberungs- & Schadensverlauf nachgewiesen. |
| **Gate 12** | Erfahrungs- & Cheatzone (Laboratorium für alle Items) | `test_gate_12_experience_lab.py` | `GATE_12_RESULT.json` | **Abbruch/Stop:** Bei Erstrunde 17/19 bestanden (Lücken bei Mehrmodul-Interaktion). Später vervollständigt. |
| **Gate 13A – 13H** | Skill-Universum & Redteam-Gesamtregression | `test_gate_13a_...py` bis `13h_...py` | `GATE_13A_RESULT.json` bis `13H_RESULT.json` | 8 spezialisierte Sub-Skill-Regressionsläufe (Routing, Action Bodies, Economy, AI-Skills). |

### Finale Abnahme-Bilanz (`FINAL_TEST_SUMMARY_V21.json`)
- **Direkte Gates (20 Läufe):** 285 Assertions **PASSED**, 0 FAILED.
- **Explizite Prüfpunkte:** 418 **PASSED**, 0 FAILED.
- **Postbuild- & Skill-Redteam:** 16 bzw. 22 geschützte Invarianten, 0 Breaches.
- **World & Skill Simulation:** 10.000 simulierte Test-Charaktere, 50/50 Welt-Checks bestanden.
- **Fragenkorpus (2.607 Fragen):** 190 BESTANDEN, 2.325 TEILWEISE, 92 OFFEN.
- **Browser Console Errors:** 0 Errors während aller Playwright-Headtrip-Läufe.

---

## 4. HTML/JS-Prototypen & Canvas-Physik

### 1. `gordslider/gordslider.html`
- **Pfade:** `/root/werkraum/gordslider/gordslider.html` & `/root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/gordslider/gordslider.html`
- **Größe:** 110.240 Bytes (3.812 Zeilen).
- **Inhalt:** Single-File HTML5/JS Prototyp einer Casino-Slot-Machine („sandycheats“). 3 Walzen, Bet-Sheet-Overlay, Paytable-Bildnachladelogik (`gordslider-paytable.jpg`), Free-Spins-Modus (`--fsbg`), lokale Bildstruktur unter `bilder/gord/`, `bilder/high/`, `bilder/low/`, `bilder/mid/`.
- **Klassifikation:** **Rein visueller & interaktiver UI-Prototyp.** Keine 3D-Engine, keine automatisierte Playwright-Testsuite.

### 2. "Liga & Spiel B.1" / Arenen und Liga
- **Herkunft:** Abschnitt 12 („Arenen und Liga“) in `00_VOLLSTAENDIGE_NEULESUNG_V20.json` (Zeile 26.190) & V20-Bauauftrag.
- **Inhalt:** Konzeptionelles Regelwerk für kompetitive Arenen, Liga-Systeme, Tauschökonomie und Zuseher-Mechanismen.
- **Klassifikation:** **Konzeptionelle Spezifikation.** In v21/v22 als Simulations-Parameter hinterlegt, jedoch nie als eigenständige 3D-Liga-Runtime im Code materialisiert.

### 3. Canvas-Physik in den HTML-Prototypen (`v15_1`, `v17`, `v21`)
- **Implementierung:** `<canvas id="world">` mit 2D top-down / isometrischer Projektion.
- **Mechanik:** Tastatur-Steuerung (WASD/Pfeiltasten), Parameter `MOVE_SPEED` (7.0), `GRAVITY` (24.0), Kollisions-Bounds, Partikel-Effekte für Dust, Tag/Nacht-Zyklus, Minimap-Rendering (`<canvas id="miniMap">`), sowie `#futureShock canvas` für Zeitreise-Visualisierung.

---

## 5. Die native Engine-Runtime: Godot `slice_001` & `ring_002`

Die native Engine-Runtime markiert den physikalischen Wechsel von Browser-HTML/Canvas zu **Godot 4.x (GDScript & 3D Node3D/CharacterBody3D)**.

### 1. `slice_001` (`godot_vertical_slice_001`)
- **Pfade:** `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/` & `/root/werkraum/engine/godot-vertical-slice/`
- **Szenen & Konfig:** `main.tscn` (2.896 Bytes), `project.godot` (893 Bytes).
- **GDScript-Komponenten:**
  - `scripts/main.gd` (187 Zeilen, 6.916 Bytes):
    - Verwendet `CharacterBody3D` für den Player.
    - Parameter: `MOVE_SPEED = 7.0`, `GRAVITY = 24.0`.
    - Input-Mapping (WASD / Arrows).
    - Dynamic Merge von `res://data/world_seed.json` & `world_seed.runtime.json`.
    - Prozeduraler Import des Provenienz-Assets `res://assets/test_cube.glb`.
  - `scripts/world_bridge.gd` (107 Zeilen, 3.737 Bytes):
    - `HTTPRequest`-Node für die Live-Kopplung an den VPS Python Server (`world_bridge_server.py`, 8.675 Bytes, Service `flextrawurst-godot-world-bridge.service`).
    - Pullt World-Deltas via `GET /worlds/{id}/events?after={cursor}`.
    - Pusht Spieler-Events via `POST /worlds/{id}/events`.
- **Belege:** Headless Godot Smoke-Tests under `tests/headless_smoke.gd`, `tests/live_bridge_probe.gd`, `tests/capture_proof.gd`.

### 2. `ring_002` (`ring_002_interaktionskreislauf`)
- **Pfad:** `/root/werkraum/engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/`
- **Szene:** `ring_002.tscn` (8.484 Bytes).
- **GDScript-Komponenten:**
  - `scripts/gordslider_interactable.gd` (184 Zeilen, 7.300 Bytes):
    - Deklariert das 3D-Weltatom **`OBJEKT_GORDSLIDER_0001`**, Ort `ORT_WUPPERTAL_CASINO_0001`, Interaktion `INTERAKTION_GORDSLIDER_SPIELEN_0001`.
    - Distanzprüfung: `interaction_range = 3.6m`.
    - Visueller Status-Wechsel: Texturen-Swap (`reels_base.png` vs. `reels_activated.png`), Material-Zustände, Activation-Light & OmniLight3D-Beacon.
    - Speicherung/Wiederherstellung über `persistence_store`.
  - `scripts/player_controller.gd` (72 Zeilen, 2.107 Bytes):
    - `CharacterBody3D` Controller mit `MOVE_SPEED = 5.5m/s`, `GRAVITY = 24.0m/s²`.
    - Unterstützt Test-Input-Vektor-Injektion für headless Test-Automation.
    - Triggert `attempt_interaction()` bei E-Taste oder Automated Probe.
  - `scripts/casino_cell_builder.gd` (18.540 Bytes): Prozeduraler 3D-Baustein der **`GORDSLIDER_KEIMKAMMER_0001`** auf Höhe **1.656m** im Casino Wuppertal.
  - `scripts/persistence_store.gd` (6.495 Bytes): Lokaler JSON-Speicher für den Automatenzustand (`activated`, `interaction_count`).
  - `scripts/ring_002_main.gd` (144 Zeilen, 5.101 Bytes): Haupt-Orchestrator, koppelt Player, Gordslider, PersistenceStore und HTTP-WorldBridge (`http://127.0.0.1:18092`).
- **Belege:** Headless Godot Testsuiten `tests/ring_002_headless.gd`, `tests/ring_002_capture_proof.gd`, `tests/ring_002_persistence_probe.gd`.

---

## 6. Präzise Trennung: Prototyp vs. Playwright vs. Engine-Runtime

| Kategorie | Physische Instanzen | Technische Eigenschaft & Ausführungs-Kontext | Wahrheitsgehalt |
|---|---|---|---|
| **Rein visueller Prototyp** | `gordslider/gordslider.html`, frühe UI-Mockups, Paytable-Bilder. | Reines HTML/CSS/Vanilla-JS im Browser. Keine Playwright-Tests, kein 3D-Welt-Kontext, keine Datenbank-Anbindung. | **Visualisierung / Mockup.** |
| **Playwright-automatisierter Test-Code** | Skripte unter `tests_v21/` (`test_gate_01_...py` bis `test_gate_13h_...py`), Result-JSONs, Regression-Runner. | Python + Playwright steuern den headless Chromium-Browser, laden `PLAY_FLEXTRAWURST_V21.html` und prüfen 418 Invarianten und 285 Gate-Bedingungen programmatisch. | **Automatisierter Nachweis der Browser-HTML-Logik.** |
| **Native Engine-Runtime** | Godot 4.x (`godot_vertical_slice_001` und `ring_002_interaktionskreislauf`). | Echte 3D-Engine auf GDScript-Basis mit `CharacterBody3D`, Physik-Verarbeitung, 3D-Meshes, prozeduralem Asset-Import (`.glb`) und bidirektionaler HTTP-Event-Stream-Bridge zum Python-Backend. | **Echte native Runtime.** |

---

## 7. Meilensteine & Abbruchpunkte (Chronologie der Schnitte)

1. **Meilenstein 1 (HTML/Canvas-Ära, v14 – v17):**
   - *Erreicht:* Funktionierende Single-File HTML5 2D-Canvas-Prototypen.
   - *Abbruch/Stop:* Erreichte Leistungsgrenze bei 2D-Canvas-Projektion und Speicherverbrauch im DOM.
2. **Meilenstein 2 (v21 Supermaximal-Bauring 4 & 12 Gates):**
   - *Erreicht:* 100% Playwright-Testabdeckung aller 12 Gates + Redteam-Regression (285 Gate-Checks, 418 explizite Checks, 0 Konsole-Fehler).
   - *Abbruch/Stop:* 
     - *Gate 03:* Erstlauf stieg bei 10/11 aus (Abbruch wegen fehlendem visuellen Render-Nachweis der Magie-Geometrie).
     - *Gate 12:* Erstlauf stieg bei 17/19 aus (Abbruch wegen unvollständiger Mehrmodul-Verknüpfung). Beide wurden vor dem v21-Final-Signoff nachgebessert.
3. **Meilenstein 3 (v22 Quest- & Dust-Echo-Simulation):**
   - *Erreicht:* Aufbau der Quest-Ökonomie und Verhaltens-Spiegelung.
   - *Abbruch/Stop:* v22 verblieb als Simulationsschicht über v21; es wurde kein eigenständiges neues HTML-Stand-Alone-File erzeugt.
4. **Meilenstein 4 (Godot Vertical Slice 001 & Ring 002):**
   - *Erreicht:* Erfolgreiche Transposition in Godot 4 3D (`slice_001`: GLB-Testcube-Import, movement, HTTP WorldBridge; `ring_002`: 3D-Keimkammer `OBJEKT_GORDSLIDER_0001` im Casino Wuppertal mit `gordslider_interactable.gd` & `player_controller.gd`).
   - *Abbruch/Stop:* Außenwelt außerhalb der Keimkammer trägt den expliziten Status `BLOCKIERT_BIS_REFERENZPAKET_VERIFIZIERT`. Es handelt sich um einen bewiesenen Vertikalschnitt, nicht um eine vollständige Portierung des gesamten v1-v22-Content-Universums.
