# Systempromptkonzept: Freie OSM & DEM 3D-Welt-Rekonstruktion (Gen1-R2)

---
datum: 2026-07-24
betrifft: [kosmos, osm, dem, 3d-builder, gen1, gen2, flextrawurst]
autor: gemini bei Daniels VPS
---

## 1. Vision & Leitgedanke (Daniel & Gemini)

Statt unstrukturierte Bilder oder proprietäre Daten zu scrapen, nutzen wir **offene, hochpräzise Vektordaten (OpenStreetMap + NASA SRTM Höhendaten)**. 

Das liefert uns für jede Stadt aus Systemdokumentation 37:
- Exakte Gebäudegrundrisse & real existierende Gebäudehöhen.
- Straßennetze, Fahrspuren, Gehwege und Wanderpfade.
- Echte Geländeprofile (Hügel, Täler, Schluchten, Küsten).
- Nahtlose Andockstellen für die echten **Tiefenkörper** (Bunker, Katakomben, U-Bahnen) aus der Lore.

Dies spart maximale Token-Kosten, läuft zu 100% lokal auf dem VPS und erzeugt ein mathematisch perfektes 1m=1Voxel-Fundament.

---

## 2. Die Werkzeuge auf dem VPS (Python 3 Stack)

1. **`osmnx` / `overpy`**: Zum Abfragen von Gebäudegrundrissen, Höhen, Straßen & POIs über die Overpass-API.
2. **`rasterio` / `elevation`**: Zum Abrufen der NASA SRTM Höhendaten (Dem-Grid) für das Geländemodell.
3. **`shapely` / `geopandas`**: Für die geometrische Vektor-Verarbeitung und Bounding-Box-Kachelung.
4. **Voxel / Mesh Generator (`pyglet` / `trimesh` / `obj` Exporter)**: Zur Konvertierung der Vektoren in 3D-Formate (`.json`, `.obj`, `.gltf`).

---

## 3. Ablauf-Plan (Qualität vor Geschwindigkeit)

### Schritt 1: Python-Geo-Environment prüfen & aufbauen
Installation von `osmnx`, `geopandas`, `shapely`, `trimesh` im VPS-Python.

### Schritt 2: Testerfassung Moskau (Zentrum)
Ein Skript `/root/werkraum/kosmos/osm_builder.py` lädt für die Moskau-Koordinaten (55.7558, 37.6173, Radius 500m):
- Alle Gebäudegrundrisse mit Höhenangaben.
- Das komplette Straßennetz.
- Alle eingetragenen Points of Interest (Historie, Läden, Bunker-Eingänge).

### Schritt 3: Generierung des Vektor-3D-JSONs
Speicherung unter `/root/werkraum/kosmos/vector_3d/moskau_center_3d.json` im 1m-Block-Maßstab.

### Schritt 4: Verifikation & Datei-Beweis
Prüfung der generierten Vektor-Strukturen und Maße im Terminal.
