# WEITERGRABUNG 07: GEOGRAFIE & WELT-GRÄBER — BERICHT

## NEUE FUNDE (Außerhalb des bekannten /kosmos/-Ordners)

1. **Recherche- & Rekonstruktionsakte `gpt-wupper-ennepe-kosmosinterpretation` (Stand: 2026-08-13)**
   Unter `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/` existiert eine 8-teilige Quellensammlung (erstellt von ChatGPT / GPT-5.6 Sol via VPS-MCP-Connector):
   - **00_START_HIER.md:** Zweck, Vertragsregeln, Realitätskern und Wahrheitsklassen.
   - **01_QUELLENKATASTER.md:** Amtliche Geodatenquellen (NRW, Wuppertal, Ennepe-Ruhr-Kreis).
   - **02_DOWNLOAD_UND_INGEST.md:** Ingest-Befehle, Projections (EPSG:25832 UTM Zone 32N, Höhen EPSG:7837).
   - **03_REALACHSEN_UND_PRIORITAETEN.md:** Räumliche Präzisionsklassen (A: 1:1 Schwelm Kern, B: Verbindungskorridore, C: Großkörper Wupper/Schwebebahn/Trassen, D: Freier Rand).
   - **04_STADT_LAYER_VOLLSTAENDIGKEIT.md:** 13-Schichten-Matrix für Stadtvollständigkeit.
   - **05_UNTERGRUND_TUNNEL_BUNKER.md:** Dokumentierter öffentlicher/historischer Untergrund.
   - **06_FASSADEN_VEGETATION_SCHLEICHWEGE.md:** Detailhaut-Pipeline (Fassadenfarben, DOM-DGM Vegetationserfassung, Schleichwege).
   - **07_QUELLENSTATUS_UND_OFFENE_LUECKEN.md:** Statusmatrix (Bestätigt, Ableitbar, Offen).

2. **Genaue Systematik der Präzisionsklassen & Realachsen:**
   - **Klasse A (`DANIEL_SCHLAFWANDELTEST`):** 1:1-Rekonstruktion von Möllenkotten bis Schwelmer Fußgängerzone (Gebäude, Fassadenfarben, Dachformen, Straßenbreiten, Gehwege, Bäume, Hecken, Schleichwege, Treppen, Mauern, Sichtachsen).
   - **Klasse B (`REALER_VERBINDUNGSKORRIDOR`):** Reale Hauptachsen Schwelm -> Wuppertal:
     - *Untere Achse:* Schwelm -> B483/Talstraße -> Wuppertal -> Elberfeld/Kohlstraße.
     - *Obere Achse:* Schwelm Bahnhofstraße -> weiter geradeaus Richtung Wuppertal.
   - **Klasse C (`REALER_GROSSKOERPER`):** Wupper, Schwebebahn (13 km, 20 Stationen), Nordbahntrasse (~23 km, 5 beleuchtete Tunnel, ~2 km Gesamtlänge), Elberfelder Innenstadt.
   - **Realanker Casino:** Berufskolleg Kohlstraße 11, 42109 Wuppertal (`CASINO_STANDORT_REALITAETSVERTRAG.md` vom 2026-07-26).

3. **Amtliche Geodaten-Schnittstellen (auf dem VPS dokumentiert):**
   - **Wuppertal Open Data (Data License Germany Zero 2.0):** ALKIS Gebäude GeoJSON (`https://daten.wuppertal.de/Infrastruktur_Bauen_Wohnen/Gebaeude_EPSG25832_JSON.json`) und Shape. WMS-Gruppen (`maps.wuppertal.de/{karten,poi,planung,verkehr,umwelt,infra,immo,gebiet}`).
   - **Ennepe-Ruhr-Kreis WFS:** ALKIS Gebäude Schwelm GeoJSON/Shape (`https://geodaten.en-kreis.de/geoservice1/geobasis_flur_adr_geb/wfs...`).
   - **Geobasis NRW:** DGM1, DOM1, LoD2 3D-Gebäude, 3D-Mesh NRW, DOP/TrueDOP, LiDAR (EPSG:25832, Höhen EPSG:7837).
   - **Hydrographie & Vegetation:** Wupperverband WMS (Wupper/Nebenbäche), LANUK @LINFOS (Biotoptypen).

4. **Bestätigte Untergrund-, Stollen- und Tunnelkörper:**
   - *Tunnel Tesche* (Rheinische Bahnstrecke, Wuppertaler Denkmalliste).
   - *Tunnel Rott* (Rheinische Bahnstrecke, Wuppertaler Denkmalliste).
   - *Dorrenberg-Tunnel Portale* (Rheinische Bahnstrecke, Denkmalliste).
   - *Sadowastollen / Nützenberg* (Portal & Treppe eines historischen Wasserreservoirs 19. Jhdt., Denkmalliste).
   - *Burgholzkotten Wasserstollen / Untergraben* (Bodendenkmal Wasserkraft).
   - *Bahnhof Beyenburg Gleisunterführung* (Baudenkmal).
   - *Nordbahntrasse Tunnelkette* (5 beleuchtete Tunnel, 2 km).
   - *Kluterthöhle Ennepetal* (Höhlenkomplex).

5. **Gamifizierte Regional-Materialien & Loot-Matrix (`_gpt/DANIELS_LESETISCH_20260801/001_HAENGEN_GEBLIEBEN.md`):**
   - **Gevelsberg:** Bahntrasse zwischen Gevelsberg und Schwelm; regionaler Loot: *Amboss-Funken* und *Industrie-Hammer-Schlagstein*.
   - **Ennepetal:** *Kluterthöhlen-Kalkkristall*, *Heilstollen-Essenz*, *Riffkalk-Echo-Fossil*.
   - **Crafting-Rezept:** Schwelmer Altstadt-Messing + Ennepetaler Kalkkristall = *Meister-Dietrich* (knackt Stufe-5-Tresore).
   - **Schwelm:** Hauptstraße 151 als Ursprungsnullpunkt `(0,0,0)` mit 5 Ebenen (Dachboden, Schreibstube, Erdgeschoss, Gewölbekeller, Brauereistollen mit Ur-Anker-Kristall). Schwelm liefert *Altstadt-Messing*, *Hopfen-Harz*, *Pflaster-Pilger*.
   - **Wuppertal:** *Schwebebahn-Eisen*, *Textil-Seide*, *Kaiserwagen-Zahnrad*.
   - **Beyenburg:** *Kloster-Bienenwachs*, *Maria-Magdalena-Kirche Stimmgabel*.
   - **Kruiner Tunnel:** *Kruiner Ruß-Scheim* / Ruß-Schleim.

6. **Spuren von 3D-Meshes in der Godot-Engine:**
   - In `truth_engine/runtime/health.json`, `last_failed_run.json` und `watchdog_state.json`: Registrierte Versuche zur Einbindung von `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/assets/schwelm_buildings.obj` und `schwelm_buildings.provenance.json`.

---

## KATEGORISIERUNGSMATRIX

- **Idee (Idea):**
  - "Gesetz der absoluten Begehbarkeit" (Jedes Haus, jeder Keller, jeder Dachboden betretbar).
  - Regionale Loot-Matrix (Orte droppen spezifische historische Rohstoffe).
  - Flextrawurst Casino Insert am Berufskolleg Kohlstraße 11.
- **Echte Geodaten (Real Geo-data):**
  - ALKIS Gebäude & Flurstücke Wuppertal (Open Data GeoJSON EPSG:25832) & EN-Kreis WFS (Schwelm).
  - Geobasis NRW: DGM1 (Gelände), DOM1 (Oberfläche), LoD2 (3D-Gebäude), 3D-Mesh NRW, DOP/TrueDOP (Luftbilder).
  - Amtliche Denkmalliste Wuppertal (Tunnel Tesche, Rott, Dorrenberg, Sadowastollen, Burgholzkotten).
  - Wupperverband WMS (Wupper & Nebenbäche).
  - Referenzkoordinatensystem EPSG:25832 (ETRS89 / UTM Zone 32N), Höhen EPSG:7837.
- **Synthetischer Fallback (Synthetic Fallback):**
  - Höhendifferenz-Berechnung `DOM1 - DGM1` zur automatischen Vegetations- & Baumkronen-Extraktion, wo Baumkataster fehlen.
  - Fassadenfarbfamilien-Zuordnung aus Fotoclustern.
  - Korridor-Generierung (LineStrings) als Vorauswahl vor Daniels visueller Abnahme.
- **Simulation (Simulation):**
  - Geländekollision und Physik in Godot auf Basis von DGM1.
  - Sichtachsen-Analyse (`VIEW_SCHWELM_001`) zur Prüfung von Blickbeziehungen und Vegetationstiefe.
- **Game-Asset (Game Asset):**
  - `schwelm_buildings.obj` & `schwelm_buildings.provenance.json` (3D-Gebäudemesh für Schwelm).
  - `gen4_casino_gord_monument.json` (Architekturvertrag des Casino-Inserts).
- **Integrierte Runtime (Integrated Runtime):**
  - `godot_vertical_slice_001` mit `world_bridge` (Port 18092).
  - Ring 002 Wahrheitsvertrag: Wuppertal-Casino = `MODELLIERTER_REKONSTRUIERTER_WELTKÖRPER`.

---

## PRIMÄRQUELLEN

- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/00_START_HIER.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/01_QUELLENKATASTER.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/02_DOWNLOAD_UND_INGEST.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/03_REALACHSEN_UND_PRIORITAETEN.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/04_STADT_LAYER_VOLLSTAENDIGKEIT.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/05_UNTERGRUND_TUNNEL_BUNKER.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/06_FASSADEN_VEGETATION_SCHLEICHWEGE.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/07_QUELLENSTATUS_UND_OFFENE_LUECKEN.md`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/CASINO_STANDORT_REALITAETSVERTRAG.md`
- `/root/werkraum/kosmos/.design/wupper-ennepe-kosmos/DESIGN_BRIEF.md`
- `/root/werkraum/kosmos/roher_auftrag_wupper_ennepe.md`
- `/root/werkraum/kosmos/gesetz_der_absoluten_begehbarkeit.md`
- `/root/werkraum/kosmos/hauptstrasse_151_vermessung.md`
- `/root/werkraum/kosmos/dungeons_quests_materialien_wupper_ennepe.md`
- `/root/werkraum/_gpt/DANIELS_LESETISCH_20260801/001_HAENGEN_GEBLIEBEN.md`
- `/root/werkraum/_gpt/bibliotheksatlas_20260801_builder/build_semantic_atlas.py`
- Externe Geodaten-Endpoints:
  - Wuppertal Open Data: `https://daten.wuppertal.de/Infrastruktur_Bauen_Wohnen/Gebaeude_EPSG25832_JSON.json`
  - Wuppertal WMS: `https://maps.wuppertal.de/{karten,poi,planung,verkehr,umwelt,infra,immo,gebiet}`
  - EN-Kreis WFS: `https://geodaten.en-kreis.de/geoservice1/geobasis_flur_adr_geb/wfs`

---

## DANIEL-ROHZITATE

- „bis zum etzen schleichweg duch die wälder“ (Daniels Rohauftrag in `roher_auftrag_wupper_ennepe.md` / `001_HAENGEN_GEBLIEBEN.md` L5575)
- „die ganze Bundesstraße unten den Weg ... bis zur Kohlstraße“ (zitiert in `03_REALACHSEN_UND_PRIORITAETEN.md` L83)
- „den weg oben über bahnhofstraße und dann weiter geradeaus natürlich“ (zitiert in `03_REALACHSEN_UND_PRIORITAETEN.md` L106)
- „bei mir gehts immer um saubere korekte und ausführlichen output ...niemals um schnelligkeit.“ (Daniel in `GEMINI.md`)
- „alles so roh und ehrlich formuliert bleibt wie es hier im verlauf steht... alles andere ist scheisse.“ (Daniel in `GEMINI.md`)
- „nee denn du bist ja selbt de ganze zeit von beginn an un der kompoase gesen xD gg“ (Daniel in `001_HAENGEN_GEBLIEBEN.md` L5590)

---

## FRÜHESTE DATIERUNG

- **2026-07-25:** Erste Script-Spuren für ALKIS-Rekonstruktion (`01_schwelm_gebaeude_2d_3d_alkis.py`) und Objektversuche (`schwelm_buildings.obj`).
- **2026-07-26:** `CASINO_STANDORT_REALITAETSVERTRAG.md` legt Berufskolleg Kohlstraße 11, Wuppertal fest.
- **2026-08-01:** `DANIELS_LESETISCH_20260801/001_HAENGEN_GEBLIEBEN.md` fasst Daniels Ursprungsauftrag und die regionalen Materialzuweisungen zusammen.
- **2026-08-13:** `gpt-wupper-ennepe-kosmosinterpretation` etabliert die vollständige Geodaten-Quellenakte und Wahrheitsklassen.

---

## SPÄTERE MUTATIONEN

- **Mutation 1 (Erinnerung & Wunsch):** Daniels Wunsch nach vollständiger Belebtheit bekannter Wege (Möllenkotten, Schwelm, Wuppertal, Trassen).
- **Mutation 2 (AI-Dungeon-Gamifizierung):** Gemini übersetzt Adressen (Hauptstraße 151 Schwelm) in Level-000-Nullpunkte mit 5 Fantasy-Dungeon-Ebenen und Loot-Materialien (Messing-Dietrich, Ur-Anker-Kristall).
- **Mutation 3 (Asset-Pipeline-Versuch):** Versuche, aus 2D-ALKIS-Grundrissen 3D-OBJ-Dateien (`schwelm_buildings.obj`) für Godot zu generieren.
- **Mutation 4 (Strikter Geodaten-Ingest & Provenienzstandard):** Übergang zur 2026-08-13 ChatGPT/GPT-5.6 Sol Akte mit harten Wahrheitsklassen (`REAL_AMTLICH`, `REAL_OFFEN_EXTERN`, `QUELLENABGELEITET`, `DANIEL_ERINNERUNG`, `FLEXTRAWURST_INSERT`, `UNGEKLAERT`), um Erfundenes nie als amtlich zu deklarieren.

---

## BEZIEHUNG ZUM HEUTIGEN SPIEL

- Das Berufskolleg Kohlstraße 11 in Wuppertal steht als fixer Ankerpunkt für den Übergang zwischen realer Stadt und Casino-Insert.
- Die Achse Möllenkotten -> Fußgängerzone Schwelm bildet das Testfeld (Klasse A) für die 1:1-Abnahme durch Daniels Schlafwandeltest.
- In der Godot-Runtime existieren Vorbereitungen für Raumachsen und Interaktionsobjekte, während automatisierte Building-Meshes (`schwelm_buildings.obj`) als Provenienz-Assets registriert sind.

---

## NICHT BEWIESEN

- Keine vollständige amtliche Inventarliste historischer WW2-Luftschutzbunker/-stollen für Schwelm und Wuppertal gefunden.
- Exakte Koordinaten-Polygonfläche von "Möllenkotten" und Schwelmer Fußgängerzone noch nicht von Daniel per Koordinaten markiert.
- Genaue Grundstücksgrenze, wo reale Kohlstraße in den fantastischen Casino-Insert übergeht.
- Vollständige Vektor-3D-Geometrie des Schwebebahn-Traggerüsts.

---

## WIDERSPRÜCHE

- **Lizenzkonflikt EN-Kreis Geoportal:** Portal-Startseite nennt *Datenlizenz Deutschland Zero 2.0*, einzelne WFS-Ressourcenseiten listen jedoch *No License Provided*.
- **Vermessungskataster vs. Fantasy:** In `hauptstrasse_151_vermessung.md` stehen reale ALKIS-Grundbuchdaten direkt neben erfundenen 5-stöckigen Brauereistollen und Ur-Anker-Kristallen, ohne getrennte Wahrheits-Tags.
- **NPC-Verbot vs. Loot-Drops:** Die Kosmos-Regeln verbieten dumme NPCs, behandeln Wesen (Quellgeist, Pflaster-Pilger) aber im selben Atemzug als Material-Lieferanten für Crafting-Rezepte.

---

## GELESENE DATEIEN

- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/00_START_HIER.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/01_QUELLENKATASTER.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/02_DOWNLOAD_UND_INGEST.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/03_REALACHSEN_UND_PRIORITAETEN.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/04_STADT_LAYER_VOLLSTAENDIGKEIT.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/05_UNTERGRUND_TUNNEL_BUNKER.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/06_FASSADEN_VEGETATION_SCHLEICHWEGE.md`
- `/root/werkraum/gpt-wupper-ennepe-kosmosinterpretation/07_QUELLENSTATUS_UND_OFFENE_LUECKEN.md`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/Zeitstrom/ereignisse/21368f86-eb55-4da7-a0e2-9011609aace7.md`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/truth_engine/runtime/health.json`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/truth_engine/runtime/last_failed_run.json`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/truth_engine/runtime/watchdog_state.json`
- `/root/werkraum/_gpt/DANIELS_LESETISCH_20260801/001_HAENGEN_GEBLIEBEN.md`
- `/root/werkraum/_gpt/bibliotheksatlas_20260801_builder/build_semantic_atlas.py`
- `/root/werkraum/_gpt/session_history.jsonl`
- `/root/werkraum/_gpt/gesamtatlas/omega/lean_sources/AENDERUNGSSTROM.snapshot.jsonl`
- `/root/werkraum/_shared/mcp_shared/Zeitstrom/events.jsonl`

---

## NICHT GELESENE DATEIEN

- `/root/KOSMOS_GESAMT_ALLE_DATEIEN.zip` (205 MB Archive)
- `/root/KOSMOS_VOLLSTAENDIG_ALLE_91_DATEIEN.zip` (205 MB Archive)
- `/root/FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` (742 MB Archive)
- `/root/WUPPER_ENNEPE_KOSMOS_VOLLSTAENDIG.zip` (28 KB Zip)
- `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/.godot/` (Binary Meshes)

---

## OFFENE SUCHRÄUME

- Stadtarchiv Wuppertal & Stadtarchiv Schwelm (für historische Luftschutz- & Bunkerbauakten).
- Geologischer Dienst NRW (für 3D-Untergrund-Geologiemodelle des Kalksteins in Ennepetal/Kluterthöhle).
- Vor-Ort-Fotoreferenz-Sammlung für Schwelm Möllenkotten bis Fußgängerzone (Fassaden & Micro-Vegetation).
