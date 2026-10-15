# 🌌 Phase 1: Quellenmanifest Kosmos & Geografie — Flextrawurst Großbergung

**Erstellt am:** 2026-08-13 | **Prospektor:** Phase 1 – Kosmos & Geografie-Prospektor  
**Status:** VERIFIZIERT & STRIKT GETRENNT | **System-Anker (0,0,0):** Schwelm Hauptstraße 151 (Lat: 51.288200° N, Lon: 7.294100° E, 213.0m ü. NHN)

---

## 📌 1. STRIKTE KATEGORIEN-DETERMINATION (FUNF-SCHICHTEN-DOKTRIN)

In Übereinstimmung mit den Grundgesetzen von Flextrawurst unterscheidet dieses Manifest strikt zwischen realen Datenbeständen, synthetischen Generaten, Simulationen, mathematischen Geometrien und Rekonstruktionen:

### 🟢 1. Echte Geodaten (Real Geodata)
- **Ur-Anker Kataster-Vermessung Schwelm Hauptstraße 151:** Amtliche Katasterdaten (Flurstück 151, Flur 12, Gemarkung Schwelm) als geodätischer Nullpunkt (0.000, 0.000, 0.000) bei 213,0 m ü. NHN (`hauptstrasse_151_vermessung.md`).
- **OpenData NRW LoD2 ALKIS (3D-Gebäudemodelle):** Amtlicher 3D-Gebäudedatenbestand für 352 Quadranten des 298,5 km² Wupper-Ennepe-Kosmos (`schleife1_geodaten_verifikation.py`, `manifest_37_regionen.json`).
- **OpenData NRW DGM1 (Digitales Geländemodell 1m):** Höhenrasterdaten mit 1m Auflösung für Geländeprofile und Topografie.
- **OpenStreetMap (OSM) Overpass API Vektordaten:** Exakte Straßennetze, Gebäudegrundrisse und 5 Wandertrassen/Pilgerwege (58,4 km Gesamtnetz inkl. Schwelmer Jakobsweg und Beyenburger Wupperbogen) (`schleife2_osm_vektor_extraktion.py`).
- **Deklassifizierte CIA-Karten (RG 263 National Archives):** 22.000 historische & militärische Karten (UdSSR Kernwaffenlager, Metro-2-Netzwerk-Diagramme 1991) (`echte_assets_und_quellen.md`).
- **Phys.org / Istanbul Galata University Soundscape-Messungen:** Akustische und räumliche Daten der antiken Höhlenstadt Derinkuyu (`echte_assets_und_quellen.md`).

### 🟡 2. Synthetische Fallbacks (Synthetic Fallbacks)
- **OSM2World Extrusionen:** Prozedural aus 2D-OSM-Tags (`height`, `building:levels`, `material`) extrudierte 3D-Baukörper bei fehlenden Photogrammetrie-Scans.
- **LOD1 Voxel-Mesh Generator (50m Radius Limit):** Dynamisch prozedural erzeugte 1m-Voxel-Meshes und Fassaden strikt im 50m Sichtradius um die Spielerkoordinate zur Vermeidung von Browser/RAM OOM Crashes (`00_UEBERGABE_AN_CHATGPT_LIES_MICH.md`, `lod_grid_manager.py`).
- **Prozedurale Innenräume & Housing:** Prozedural generierte Grundrisse und Dungeonebenen (`gen3_schwelm_housing_interior.json`, `gen3_world_dungeons_interior.json`).
- **Blosm Terrain Addon Extrapolationen:** Prozedural aufgefüllte Höhendaten bei Lücken im Höhenmodell.

### 🔵 3. Simulation (Simulation)
- **RAM/OOM-Trockenlauf Simulation:** Mathematische Simulation zur Prüfung der Speicherauslastung bei 1m, 10m und 100m Voxel-Auflösung mit striktem <120 MB RAM-Limit (`kosmos_trockenlauf_simulation.py`, `kosmos_trockenlauf_results.json`).
- **Redteam Sokratische Audit-Loops (R1–R8):** 8-fache sokratische Prüfung auf physikalische Konsistenz, Mesh-Manifoldness und Sabine'sche Nachhallzeit-Akustikberechnung (`redteam_socrates_loop.md`, `socrates_redteam_wupper_ennepe_11111_ideen.md`).
- **LOD Grid Manager & Haversine Distance Engine:** Dynamische Entfernungssimulation zur kontinuierlichen Umschaltung zwischen LOD 1 (Detail 50m), LOD 2 (District 500m) und LOD 3 (Macro BBox) (`lod_grid_manager.py`).

### 🟣 4. Geometrie (Geometry)
- **Casino-Organismus Master-Geometrie (`CASINO_ORGANISMUS_MASTER.md`):**
  - **Höhenmaßstab:** 1.656 Meter architektonische Höhe (exakt 2x Burj Khalifa 828m).
  - **Horizontales Wachstumsgesetz (44m → 88m Gesetz):** Basis-Durchmesser beginnt mit 44 Metern (22m Radius). Nach genau 44 Metern vertikaler Höhe weitet sich der Gebäudekörper einmalig auf 88 Meter Durchmesser (44m Radius) auf.
  - **22 Organ-Systeme:** Rhythmisches Verbundsystem aus Herz, Nervensystem, Lungen, Haut, Gedächtnis, Immunsystem, Erlebnisparks (Achterbahnen, Freier Fall), Mental-Health-Schutzräumen etc.
- **Ring-002 Gord-Slider Keimkammer:** Keimzelle `OBJEKT_GORDSLIDER_0001` in `ORT_WUPPERTAL_CASINO_0001` als erster begehbarer Interaktionskreislauf.
- **Sketchfab Photogrammetrie Meshes:** Edinburgh City Centre (2,1 Mio. Dreiecke) und Berlin City Mesh (1:20.000) (`echte_assets_und_quellen.md`).

### 🔴 5. Heutige Rekonstruktion (Today's Reconstruction)
- **Hauptstraße 151 (5 Vermessungs-Ebenen):** Rekonstruierter Anker-Komplex (Ebene +2 Dachboden +7,5m mit Jakobs-Muschelnadel; Ebene +1 Schreibstube +3,5m; Ebene 0 Erdgeschoss 0,0m; Ebene -1 Gewölbekeller -4,0m; Ebene -2 Brauereistollen -12,0m mit Panzerschrank) (`hauptstrasse_151_vermessung.md`).
- **Stadtarchäologische Rekonstruktion (Schwelmer Rathaus & Altstadt):** Rekonstruktion historischer Fassaden und Baukörper aus Akten und 2D-Katastern (`skill_city_archaeologist_3d_reconstructor.md`, `ftw_schwelm_rathaus_v1_Amtliches_Rathaus_Schwelm_3D_Geometrie.md`).
- **Nordschleife Replica:** Digitale Rennstrecken-Rekonstruktion der Nürburgring Nordschleife (`gen4_nordschleife_replica.json`).
- **Dungeon- & Stollen-Rekonstruktionen:** Kluterthöhle Ennepetal, Kruiner Tunnel und Schwelmer Brauereistollen (`dungeons_quests_materialien_wupper_ennepe.md`).

---

## 📖 2. GELESEN

Folgende Kernakten, Kataster, Manifeste und Spezifikationen wurden zeilenweise gesichtet und evaluiert:

1. `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/CASINO_ORGANISMUS_MASTER.md` (12.322 Bytes, 221 Zeilen, von Daniel am 2026-07-26 versiegelt)
2. `/root/werkraum/kosmos/hauptstrasse_151_vermessung.md` (3.148 Bytes, Origin 0,0,0, 5 Etagen-Profile)
3. `/root/werkraum/kosmos/KOSMOS_INVENTAR_UND_DOKUMENTATION.md` (17.325 Bytes, 91 Projekt-Dateien, 300 km² Territorium)
4. `/root/werkraum/kosmos_paket_chatgpt/00_UEBERGABE_AN_CHATGPT_LIES_MICH.md` (5.405 Bytes, LOD1/2/3 Architecture)
5. `/root/werkraum/kosmos_paket_chatgpt/echte_assets_und_quellen.md` (7.438 Bytes, Ehrlicher Asset-Status von Kimi)
6. `/root/werkraum/kosmos/systempromptkonzept_echter_kosmos_harvester.md` (13.956 Bytes)
7. `/root/werkraum/kosmos/systempromptkonzept_wupper_ennepe.md` (3.209 Bytes)
8. `/root/werkraum/kosmos/socrates_redteam_wupper_ennepe_11111_ideen.md` (5.961 Bytes)
9. `/root/werkraum/kosmos/gesetz_der_absoluten_begehbarkeit.md` (2.358 Bytes)
10. `/root/werkraum/kosmos/dungeons_quests_materialien_wupper_ennepe.md` (3.546 Bytes)
11. `/root/werkraum/kosmos/jakobsweg_schwelm_netzwerk.md` (2.531 Bytes)
12. `/root/werkraum/kosmos/manifest_37_regionen.json` (52.682 Bytes)
13. `/root/werkraum/kosmos/manifest_wupper_ennepe_kosmos.json` (3.499 Bytes)
14. `/root/werkraum/kosmos_paket_chatgpt/manifest_38_regionen.json` (52.682 Bytes)
15. `/root/werkraum/kosmos_paket_chatgpt/kosmos_trockenlauf_results.json` (70.588 Bytes)
16. `/root/werkraum/kosmos_paket_chatgpt/redteam_socrates_loop.md` (40.721 Bytes)
17. `/root/werkraum/kosmos_paket_chatgpt/skill_city_archaeologist_3d_reconstructor.md` (17.878 Bytes)
18. `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_suchraumkatalog.md` (1.569.980 Bytes, 18.535 gescannte Ordner)
19. `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_raw_directory_scan.json` (6.351.075 Bytes)
20. `/root/werkraum/gemgems-spielbeobachtung/systempromptkonzept.md` (5.630 Bytes)

---

## 🔍 3. GESUCHT

Gezielte Durchsuchung folgender Suchräume und Datenkörper:
- **Schwelm 0,0,0 Origin & Katasterdaten:** Hauptstraße 151, Flur 12, Flurstück 151.
- **LoD2 ALKIS 3D-Gebäudemodelle NRW:** Amtliche Gebäudekörper der Städte Schwelm, Wuppertal, Gevelsberg, Ennepetal.
- **DGM1 Digitales Geländemodell 1m NRW:** Hochauflösende Rasterhöhendaten.
- **OpenStreetMap Vektordaten:** Overpass API Abfragen für Straßennetze, Wandertrassen und Gebäudegrundrisse.
- **`KOSMOS_3D_PAKET_FUER_CHATGPT.zip`:** 63.504 Bytes großes Archiv im Werkraum-Wurzelverzeichnis.
- **`kosmos/` Verzeichnis:** 20 Unterordner, 48 Hauptdateien, 91 Projekt-Dateien insgesamt.
- **`kosmos_paket_chatgpt/` Verzeichnis:** 11 Dokumentations- und Simulationsdateien.
- **`CASINO_ORGANISMUS_MASTER.md`:** 1.656m Höhe, 44m → 88m Wachstumsgesetz, 22 Organe, Ring-002 Gord-Slider Keimkammer.

---

## 📦 4. ARCHIVE GEÖFFNET

Folgende komprimierte Pakete und Exporte wurden inventarisiert und analysiert:
1. `/root/werkraum/KOSMOS_3D_PAKET_FUER_CHATGPT.zip` (63,5 KB — ChatGPT Übergabepaket).
2. `/root/werkraum/kosmos/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` (176,1 MB — Vollständiges Spiele-Archiv V1–V22).
3. `/root/werkraum/flarum-export` & `/root/werkraum/flarum_vollexport.html` (1,14 MB HTML-Vollexport der Flarum-Wesen-Vorgeschichte).
4. **National Archives RG 263 Dataset Reference:** Deklassifizierte CIA-Kartensammlungen (22.000 Einheiten).
5. **Sketchfab Repositories:** Edinburgh Photogrammetry Scan & Berlin 1:20.000 Mesh.

---

## 🗄️ 5. DATENBANKEN ABGEFRAGT

1. **PostgreSQL Datenbank `flextrawurst` (Port 5432, DB: `flextrawurst`, User: `dak`):**
   - Tabellen: `events` (append-only), `user_modules`, `users`.
   - Live-Dienste: `welt-api.service` (Port 8030), `welt-bruecke.service`, `splitter-physik.service`.
2. **Overpass API / OpenStreetMap Endpunkte:**
   - Vektordaten-Extraktion für 38 Regionen und 5 Wander/Pilger-Trassen (58,4 km Netz).
3. **OpenData NRW WFS/WCS Geodienste:**
   - Abfrageparameter für LoD2 ALKIS 3D-Gebäude und DGM1 1m Höhengitter.
4. **Google 3D Tiles API:**
   - 3D Tiles Katalog (2.500+ Städte, Draco/glTF Format).
5. **Flarum MySQL Datenbank:**
   - Vorgeschichte der 6 Codewesen (schreibgeschützt gemäß Grundgesetz 6 & 7).

---

## 📅 6. SESSIONS GELESEN

Chronologische Auswertung der verzeichneten Session-Notizen und Bau-Protokolle:
1. `2026-07-24_gemini_session.md` (VPS-Sessionnotiz: Verifikation der 3D-Datenquellen, RAM-Trockenlauf, Haversine LOD-Manager).
2. `2026-07-25` Session (Versiegelung der humanlesbaren Gesamtdokumentation `KOSMOS_INVENTAR_UND_DOKUMENTATION.md`).
3. `2026-07-26` Session (Daniel-Bestätigung & Versiegelung des `CASINO_ORGANISMUS_MASTER.md` mit 1.656m Höhe & 44m→88m Wachstumsgesetz).
4. `2026-08-13` Sessions (Phase 0 Suchraumkatalog-Erstellung & Phase 1 Kosmos Prospektion).

---

## 🛑 7. NICHT GELESEN

Folgende Binär- und Rohdatenströme wurden bewusst aus Performance- und Kontextgründen nicht zeilenweise gecrawlt:
1. **176,1 MB ZIP-Binärdaten** in `FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` (ungeöffnete Roh-Archive).
2. **3,6 MB PNG-Snapshot-Binärdateien** (`raw_snapshots/moskau_zentrum_h0_t60.png` etc.).
3. **MySQL Flarum Tabellen-Rohdaten** (strikter Schutz nach Grundgesetz 6/7).
4. **Exzessive Daemon-Logfiles:** `generator.log` (14,1 MB) und `takt.log` (16,5 MB).

---

## ⚠️ 8. OFFENE VERDACHTSFÄLLE & UNGEKLÄRTE DECKUNGEN

1. **Lokale Caching-Prüfung von NRW ALKIS LoD2 `.gml` Dateien:**
   Die Metadaten und Schemas von LoD2 sind in `manifest_37_regionen.json` verifiziert. Die physischen `.gml` / `.citygml` Rohdateien für Schwelm Flur 12 werden über `schleife1_geodaten_verifikation.py` dynamisch gestreamt; eine dauerhafte lokale Kopie muss im Caching-Ordner geprüft werden.
2. **Google 3D Tiles API EU-Billing-Sperre:**
   Nach den Google-Richtlinien vom 8. Juli 2025 sind neue 3D Tiles API-Projekte für EU/EEA-Rechnungsadressen gesperrt. Für den Produktivbetrieb muss entweder eine Nicht-EU-Billing-Adresse verwendet oder vollständig auf OSM2World + NRW OpenData LoD2 zurückgegriffen werden (`echte_assets_und_quellen.md`).
3. **Militärische Bunker-Baupläne (Berlin / Moskau Metro-2):**
   Reale exakte Baupläne von unterirdischen Militärbunkern existieren nicht in öffentlichen Archiven (`echte_assets_und_quellen.md`). Sämtliche unterirdischen Komplexe (außer Kluterthöhle und Schwelmer Stollen) bleiben als *synthetische Fallbacks* oder *heutige Rekonstruktionen* zu deklarieren.
