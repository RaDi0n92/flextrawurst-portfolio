# 🔬 CT-SCAN ANALYSE: KOSMOS GEODATEN, HARVESTER-STRANG & PROSPEKTION VS. RUNTIME

**Berichtskategorie:** Spielbeobachtung & Geodaten-Prospektion  
**Zielpfad für Dokumentation:** `/root/werkraum/gemgems-spielbeobachtung/spiel/18_ct_scan_kosmos_geodaten_prospektion_vs_runtime.md`  
**Autor:** Kosmos-Geodaten- & Harvester-Prospektor  
**Datum:** 13.08.2026  
**Status:** Auditiert & Korrigiert (Chirurgische Datenprovenienz-Klassifikation)  

---

## 📜 EXECUTIONS-SUMMARY & CT-SCAN BEFUND

Der **Kosmos 300 km² Wupper-Ennepe Geodaten- & Harvester-Strang** wurde einer vollständigen CT-Scan-Analyse in `/root/werkraum/kosmos/` unterzogen. 

### Kern-Erkenntnisse auf einen Blick:
1. **Physischer Geodatenbestand (~68 MB):** Der Datenbestand gliedert sich in echte Overpass-OSM-Vektordaten und synthetische Fallback-Dateien.
2. **Chirurgische Datenprovenienz-Klassifikation:**
   - **Echte / Transformierte OSM-Daten (Hauptdateien):** 
     - `gebaeude_2d_3d.geojson` (14,86 MB Gebäude Schwelm) und `29_wuppertal_autobahnen_b7_stadtstrassen.json` (38,00 MB Straßennetz) enthalten reale WGS84-Polygon- und Vektorkoordinaten aus Overpass-Downloads.
     - `04_schwelm_eingaenge_tueren_tore.json` (1,32 MB): Enthält **3.591 echte OSM-Knoten** (`elem_254133695`, `entrance: yes`, `lat: 51.333704`, `lon: 7.0510672`) **ohne** `status: synthetisch_verifiziert`-Marker. Ein signifikanter Anteil der Daten zeigt Adressen aus Nachbarstädten (z.B. Velbert, `addr:city: Velbert`). **Befund:** Echte OSM-Nodes mit Velbert-Leak, Ursache (z.B. zu breiter Query-Raum, Pipeline-Merge) noch zu ermitteln.
   - **Synthetische Fallback-Dateien (`status: synthetisch_verifiziert`):** Skripte in `skripte_77/` erzeugen bei Overpass-API-Timeouts automatisch synthetische JSON-Strukturen (z.B. `02_schwelm_dachformen_und_traufen.json`, 11,96 MB), die das Marker-Tag `"status": "synthetisch_verifiziert"` tragen.
   - **Mischkörper:** Teildatensätze, die reale Grundrisse mit interpolierten Tag-Synthesen kombinieren.
3. **LoD2- & DGM1-Geodaten Realitäts-Check:** Es existieren **keine physischen CityGML 3D-Volumenkörper (`.gml`/`.obj`) oder LIDAR DGM1-Höhenraster (`.tif`/`.xyz`)** von OpenData NRW auf der Platte. Die "100% Verifikation" ist eine **mathematisch-metadatenbasierte Gitter-Prospektion**, die Gebäudeverläufe aus OSM-Höhentags (`building:levels`, `height`) interpoliert.
4. **Strikte Systemtrennung (v21 vs. v22):**
   - **v21 (Canvas 2D Runtime):** Nutzt 2,5D-Software-Rendering für Höhlen- & Raum-Polygonfaces, verarbeitet jedoch noch keine direkten WGS84-Geokoordinaten aus dem Kosmos-GeoJSON-Bestand.
   - **v22 (Offline Generator/Simulation):** Enthält keinen Canvas-Renderer, sondern verarbeitet universelle Geokoordinaten und Regions-IDs im SQLite-Questkatalog.

---

## 📦 DATENBESTÄNDE & PROVENIENZ-KLASSIFIKATION

| Daten-Kategorie | Pfad auf dem VPS | Dateigröße | Provenienz-Klasse / Inhalt |
| :--- | :--- | :--- | :--- |
| **Schwelm Building-Polygone** | `/root/werkraum/kosmos/geometrie/schwelm/gebaeude_2d_3d.geojson` | **14,86 MB** | 🟢 **Echte transformierte OSM-Polygone** |
| **Wuppertal Straßennetz & A46/B7** | `/root/werkraum/kosmos/geometrie/wuppertal/29_wuppertal_autobahnen_b7_stadtstrassen.json` | **38,00 MB** | 🟢 **Echte transformierte OSM-Vektoren** |
| **Wuppertal Nordbahntrasse** | `/root/werkraum/kosmos/geometrie/wuppertal/30_wuppertal_nordbahntrasse_bahnen.json` | **2,09 MB** | 🟢 **Echte transformierte OSM-Trassen** |
| **Schwelm Eingänge & Türen** | `/root/werkraum/kosmos/geometrie/schwelm/04_schwelm_eingaenge_tueren_tore.json` | **1,32 MB** | 🟢 **Echte OSM-Nodes (3.591 Nodes), Velbert-Leak (Ursache zu ermitteln)** |
| **Schwelm Dachformen-Metadaten** | `/root/werkraum/kosmos/geometrie/schwelm/02_schwelm_dachformen_und_traufen.json` | **11,96 MB** | 🟡 **Synthetischer Fallback (`synthetisch_verifiziert`)** |
| **Google Earth Snapshots** | `/root/werkraum/kosmos/raw_snapshots/moskau_zentrum_h*.png` | **~28,00 MB** | 🟢 **Echte Playwright-Screenshots (R2 Harvester)** |
| **OpenData NRW LoD2 3D-Meshes** | *(Keine `.gml`, `.obj` Dateien auf Festplatte)* | **0 Bytes** | ❌ **Keine binären LoD2 3D-Files** |
| **DGM1 LIDAR Höhendaten** | *(Keine `.tif`, `.las` Rasterdateien auf Festplatte)* | **0 Bytes** | ❌ **Keine binären DGM1 Höhenraster** |

---

## 🚪 DAS 100% BEGEHBARKEITS- & VOXEL-INTERIOR-SYSTEM

- **Grundsatz (`gesetz_der_absoluten_begehbarkeit.md`):** Jedes Gebäude besitzt einen prozeduralen Innenraum.
- **Voxel-Extrusion:** Die 2D-Polygone aus `gebaeude_2d_3d.geojson` bilden das Fundament. Aus `building:levels` errechnet der Code bei Annäherung ($< 50$ m) ein prozedurales 1m³ Voxel-Raster (`gen3_schwelm_housing_interior.json`).

---

## 🎮 SPIELANBINDUNG: PROSPEKTION VS. RUNTIME

- **Godot Engine Slice 001:** Besitzt den Seed-Vertrag (`world_seed.json`) für `region.schwelm.origin` und die HTTP-Bridge auf **Port 18092**, nutzt ingame aktuell den Platzhalter `test_cube.glb`. Die 68 MB Vektordaten sind noch nicht in Godot `.tscn`-Szenen umgewandelt.
- **v21 Runtime (Canvas 2D):** Nutzt eigene Raum-Arrays im JS-Software-Renderer, verarbeitet keine direkten Kosmos-GeoJSON-Files.
- **v22 Questkosmos (Generator):** Verknüpft Regions-IDs und WGS84-Anker in der SQLite-Datenbank.
