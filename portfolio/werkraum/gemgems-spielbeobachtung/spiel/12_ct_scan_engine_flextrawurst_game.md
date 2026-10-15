# CT-Scan 12: Der Echte Game-Körper (`engine/flextrawurst-game/`)

**Erstellungsdatum:** 13.08.2026  
**Status:** Top-Level-Wahrheitsklassifikation des Game-Zielkörpers durchgeführt (High-Level-Manifest-Schnitt, keine vollständige Durchleuchtung aller Hunderter Alt-Dateien)  
**Ablage:** `/root/werkraum/gemgems-spielbeobachtung/spiel/12_ct_scan_engine_flextrawurst_game.md`

---

## 1. Die Methodische Einordnung & Grundsatz-Klarstellung

In diesem CT-Scan sezieren wir die kanonische Engine-Quelle unter `/root/werkraum/engine/flextrawurst-game/` (geprüfter Stand: **25.07.2026**, Manifest v2.0.0, erstellt von GPT-5.6-sol-hoch).

**Widerlegung früherer KI-Glättungen:**
1. **13 vs. 14 GTA-Metropolen:** In den Kosmos-Dokumenten existiert ein manifester Text-Widerspruch. Die Überschrift fordert 13 Metropolen, der Text listet jedoch 14 auf (Berlin, Tokio, London, Paris, Chongqing, Neapel, Moskau, Wien, Edinburgh, Portland, Valletta, Dortmund, Wuppertal, Erfurt). Dies wurde in früheren Berichten fälschlicherweise als "13+14" zusammengeklebt.
2. **Waffen, Fahrzeuge, Wesen:** 111 Waffenklassen, 66 Fahrzeugfamilien und mindestens 88.888 Wesenformen sind **Kosmos-SOLL-Dimensionen** aus dem Sammelauftrag. Sie sind Belege für Planungs- und Generierungsrahmen, **keine** 111 fertigen 3D-GLB-Dateien im Asset-Ordner!

---

## 2. Der Status-Befund nach `GEBAUT_VS_SIMULIERT_VS_GEPLANT.md`

### 🟢 1. Real gebaut und auf dem VPS ausgeführt (Lauffähige Runtime)
- **Godot 4.3 Vertikalschnitt:** Gefunden unter `game/godot_vertical_slice_001/` (Godot Version `4.3.stable.official.77dcf97d8`).
- **Verifizierte Runtime-Tests:**
  - Headless Smoke-Test für Szene, Spielfigur, Kamera, HUD, Weltseed & Assetmanifest.
  - Headless-Rendering via **Xvfb / OpenGL** mit real erzeugten PNG-Screenshots.
  - Physisches 3D-Asset: `game/godot_vertical_slice_001/assets/test_cube.glb` (1.476 Bytes, GLTF 2.0 validiert, SHA256 `ca481b86...`).
- **Die Godot-Weltbrücke:** 
  - Eigener lokaler Port **`18092`** (`127.0.0.1:18092`).
  - **Live-Status verifiziert:** Port 18092 lauscht aktuell aktiv auf `127.0.0.1:18092` (Python-Bridge-Prozess aktiv).
  - Produktiver HTTP-POST-Roundtrip und append-only Event-Logik verifiziert.
  - Harte Portgrenze: Ports 8090 und 8091 blieben unberührt!

### 🟡 2. Real als Materialkörper vorhanden, aber NICHT zu einem Gesamtspiel montiert
- **v1 bis v22 Rettungskörper:** 338 Markdown-Dateien aus den historischen Entwicklungsstufen (v1 bis v22) wurden als Archivkörper eingezogen.
- **Gate-Belege:** Gate 04 (Untergrund/Erze/Dungeons), Gate 06 (88.888 Wesen/Beziehungen), Gate 07 (Zeitgewebe), Gate 08 (Creator/Konzerte), Gate 09 (Pause/Kampf/Loot/Nebenquests), Gate 12 (Erfahrungs-Testzone) liegen als historische Berichte und Gate-Dateien vor.
- **v21 / v22 Runtimeteile & Dust-Echo:** Eingezogen und dokumentiert, laufen jedoch nicht als ein einziges integriertes Gesamtspiel.

### 🟡 3. Simuliert oder als Datensatz vorhanden (Prospektion)
- **300 km² Wupper-Ennepe-Kosmos Grid:** 352 Quadranten Kataster (Schwelm, Wuppertal, Ennepetal etc.) basierend auf NRW LoD2/DGM1 Geodaten.
- **Harvest- & Interior-Datensätze:** 4-Generationen-Pipeline (Gen 1 Harvester, Gen 2 Math/Voxel, Gen 3 Interior, Gen 4 Surface).

### 🔴 4. Weiterhin geplant oder unbewiesen (Was NICHT existiert!)
- ❌ **Kein einziges fertiges 3D-Gesamtspiel:** Es gibt **kein** fertiges, großes 3D-Open-World-Spiel in Godot, in dem GTA-Metropolen, Skyrim-Festungen, Kampf, Fahrzeuge, Crafting, Skilltrees und Dungeons in einem einzigen ausführbaren Binärspiel zusammenlaufen.
- ❌ **Kein großer 3D-Modellbestand:** Ausser kleinen GLB-Testkörpern (wie `test_cube.glb`) existiert kein vollständiges 3D-Asset-Paket für alle 111 Waffen oder 66 Fahrzeuge im aktiven Godot-Ordner.

---

## 3. Gesamt-Bewertung der Spielarchäologie Matrix

| Ebene | Befund | Beweis-Urteil |
| :--- | :--- | :--- |
| **Godot 4.3 Vertikalschnitt (`slice_001`)** | Headless-Boot, Kamera, HUD, Test-Cube GLB | 🟢 **Direkt belegt** (Port 18092 live) |
| **Godot-Weltbrücke (18092)** | Localhost Roundtrip, append-only Eventlog | 🟢 **Direkt belegt** |
| **Historisches v1–v22 Archiv** | 338 Rettungs-MDs, Gates 01–12 | 🟢 **Direkt belegt** (als Dokumentations- & Belegkörper) |
| **300 km² Wupper-Ennepe-Kosmos** | LoD2/DGM1 Geodaten, 352 Quadranten | 🟡 **Starke Indizien** (als Datensatz vorhanden) |
| **Fertiges Open-World GTA+Skyrim 3D-Spiel** | Integration aller Zonen & Mechaniken in Godot | 🔴 **Nicht belegt / Geplant** |
