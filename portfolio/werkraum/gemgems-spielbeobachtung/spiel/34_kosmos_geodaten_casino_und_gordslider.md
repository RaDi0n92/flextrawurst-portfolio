# 🏗️ Rekonstruktionsbericht: Kosmos-Geodaten, Casino & Gordslider (Achse 5)

**Analyst:** Research Subagent (Achse 5: Kosmos-Geodaten, Casino & Gordslider Rekonstrukteur)  
**Empfänger:** Parent Agent (`039137f2-edaa-4845-830f-159c5c0b8e47`)  
**Untersuchte Primärquellen:**
1. `/root/werkraum/kosmos/KOSMOS_INVENTAR_UND_DOKUMENTATION.md`
2. `/root/werkraum/engine/flextrawurst-game/extracted_sources/3d_packages/kosmos_3d_paket/` (`manifest_38_regionen.json`, `lod_grid_manager.py`)
3. `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/` (`CASINO_ORGANISMUS_MASTER.md`, `CASINO_STANDORT_REALITAETSVERTRAG.md`)
4. `/root/werkraum/engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/` (`ring_002.tscn`, `casino_cell_builder.gd`, `gordslider_interactable.gd`, `gordslider.html`)

---

## 📐 1. Real-Geografie & Territorium (300 km² Wupper-Ennepe-Kosmos)

### 🗺️ Master-Grid & Origin (0,0,0)
* **Story-Ursprung (0,0,0):** Schwelm Hauptstraße 151 (`Lat: 51.2882° N, Lon: 7.2941° E`, 213m ü. NHN).
* **Flächen-Territorium:** 21,6 km × 16,7 km = **298,5 km²** (352 Quadranten à 1 km²).
* **Die 5 Zonen:** Schwelm Altstadt, Wuppertal Metropol-Achse, Beyenburg Wupperbogen, Gevelsberg Stadtgebiet, Ennepetal & Kluterthöhle.

### 🏛️ Amtliche Geodaten-Schichten
1. **LoD2 3D-Gebäudemodelle (Geobasis NRW / ALKIS):** Amtliche Gebäudegrundrisse mit echten Dachformen (Giebel-, Walm-, Pult-, Flachdächer), First- und Traufhöhen.
2. **DGM1 (Digitales Geländemodell 1m):** Hochpräzises Höhennetz der Topografie für Hanglagen, Wuppertal-Talzug und Höhlensysteme.
3. **OSM-Vektor-Trassen (58,4 km Gesamtnetz):** 5 Wandertrassen & Wege inklusive Jakobsweg Schwelm, Nordbahntrasse, Wupper-Wanderwege und Viadukte.
4. **Untergrund & 0% NPC Engine:** Spatial Indexing über 3 reale Untergrund-Dungeons (Kluterthöhle Ennepetal, Kruiner Tunnel, Schwelmer Stollen).

---

## 🚀 2. 3D-Weltraum-Architektur & Streaming-Engine (`KOSMOS_3D_PAKET`)

### 📦 Paket-Inhalt (`KOSMOS_3D_PAKET_FUER_CHATGPT.zip`)
Extrahiert in `/root/werkraum/engine/flextrawurst-game/extracted_sources/3d_packages/kosmos_3d_paket/`:
* `manifest_38_regionen.json` (38 Regionen von Schwelm/Wuppertal bis Berlin/Nordschleife).
* `lod_grid_manager.py` (Fertiges Python/JS-Streaming-Modul).
* `skill_city_archaeologist_3d_reconstructor.md` & `redteam_socrates_loop.md`.

### ⚡ 3-Stufen Level-of-Detail (LOD) Streaming-Gesetz
Um OOM-Crashes im Browser/Engine zu verhindern, gilt das streng auditiertes RAM-Limit (< 120 MB):
1. **LOD 3 (Macro):** Topographie-Bounding-Boxen (100m – 1km Radius). Speicheraufwand < 100 KB.
2. **LOD 2 (District):** Straßenachsen & Gebäudegrundrisse (10m – 50m Vektor) im 500m Umkreis.
3. **LOD 1 (Detail/Voxel):** 1m Voxel-Mesh & 3D-Fassaden **ausschließlich im 50m Sichtradius** um die aktuelle Spieler-Koordinate.

---

## 🏰 3. Der 1.656m Casino-Organismus

### 📜 Master-Leitsätze (`CASINO_ORGANISMUS_MASTER.md`)
* **Architektonische Höhe:** **1.656 Meter** (exakt die doppelte Höhe des Burj Khalifa mit 828m).
* **Vertikaler Körper:** Bewohnte, funktionale, vertikale Megastadt – kein hohler Turm.

### 📐 44m → 88m Durchmesser-Gesetz
* **Start:** Unterer Kernkörper beginnt mit **44 Metern Durchmesser** (22m Radius).
* **Aufweitung:** Nach exakt **44 Metern vertikaler Höhe** weitet sich der Gebäudekörper einmalig auf **88 Meter Durchmesser** (44m Radius) auf.
* **Kanonische Grenze:** Jede weitere Expansion oberhalb der 88m-Stufe ist bis zur Sichtung durch Daniel als `MODELLIERTE_VARIANTE_NICHT_KANONISCH` deklariert.

### 🫀 Die 6 Biologischen Organe
1. **Herz:** Rhythmatischer Verbund aus Spielhallen, Slot-Maschinen, Banken & Risiko-Archiven.
2. **Nervensystem:** Reagierende Aufzüge, Seilbahnen, Lichtvektoren & magische Portale.
3. **Lungen:** Wälder, vertikale Gärten, Gewächshäuser, Wasserfälle, Nebelkammern & Höhlen.
4. **Haut:** Dynamisch reagierende Fassade auf Wetter, Besucherströme & Weltzustände.
5. **Gedächtnis:** Archive für Spielhistorien, Traum-Trajektorien & Raum-Provenienz.
6. **Immunsystem (Mental Health & Schutz):** Stille Rückzugsräume, reizarme Pfade, Cool-down-Sperren, Wellness & Ausstiegsunterstützung (ohne bevormundende Entkernung).

### 🚪 Standort-Realitätsvertrag (`CASINO_STANDORT_REALITAETSVERTRAG.md`)
* **Real-Welt-Anker:** Berufskolleg Kohlstraße (Kohlstraße 11, 42109 Wuppertal-Elberfeld / Mirker Hain).
* **Türschwellen-Gesetz:** 
  * *Innerhalb der Türschwelle:* Frei modellierter 1.656m Casino-Organismus.
  * *Ab äußerer Türschwelle:* Strikter 1:1 Realitätsbezug. Keine erfundene Nachbarschaft (`BLOCKIERT_BIS_REFERENZPAKET_VERIFIZIERT`).

---

## 🎰 4. Der Gordslider & Godot 3D-Kabinett (`ring_002`)

### 🎲 Stochastik & Math-Engine (`gordslider.html`)
* **PRNG-Duo:** `xmur3` (32-Bit String-Hash Seed-Generator) gekoppelt mit `mulberry32` (deterministischer 32-Bit Pseudozufallsgenerator).
* **5x9 Grid Architecture:** 5 Spalten × 9 Zeilen Matrix mit 3 frei wählbaren Modi:
  * Mode 3: 3 aktive Zeilen (1× Einsatz)
  * Mode 6: 6 aktive Zeilen (2× Einsatz)
  * Mode 9: 9 aktive Zeilen (3× Einsatz)
* **150h Tuning Meter (`WAVES`):** Dynamische Stimmungsanzeige (COLD / HOT / COOLDOWN), die durch ruhige Phase und Kaskaden aufgeladen und durch Megawins entladen wird.

### 🕋 Ring 002: Gordslider-Keimkammer (`ring_002_interaktionskreislauf`)
* **Identität:** `GORDSLIDER_KEIMKAMMER_0001` (`OBJEKT_GORDSLIDER_0001` at `ORT_WUPPERTAL_CASINO_0001`).
* **Rolle:** Die erste Begehbare 3D-Stammzelle des 1.656m Casino-Organismus.
* **3D-Raumkonstruktion (`casino_cell_builder.gd`):** 24m × 28m Saal mit pulsierenden Adern, Carpet-Texturen, Trinity-Wandbildern und zwei biologischen Hauptadern:
  * **Reizader (Stimulus Artery):** Kaskaden-, Puff- und Freispiel-Fokus (Weinrot/Gold).
  * **Ruheader (Quiet Artery):** Pause, Wellness & Ausstiegspool mit leuchtenden Cyan-Sporen.
* **Persistenz & VPS-Bridge:** Verankert in Godot (`user://ring_002_state.json`) und synchronisiert per `WorldBridge` (`http://127.0.0.1:18092`).

---

## 🔗 5. Die exakte Synthese: Reale Geografie → Casino-Hochhaus → Gordslider

```
+-------------------------------------------------------------------------------+
| REAL-GEOGRAFIE (300 km² Wupper-Ennepe-Kosmos)                                 |
| Origin (0,0,0): Schwelm Hauptstraße 151 (Lat 51.2882, Lon 7.2941, 213m ü.NHN) |
| Real-Standort: Wuppertal, Kohlstraße 11 (DGM1 + LoD2 ALKIS Geodaten)         |
+----------------------------------+--------------------------------------------+
                                   |
                                   v (Türschwellen-Übergang)
+----------------------------------+--------------------------------------------+
| CASINO-ORGANISMUS (Vertikalkörper Achse 5)                                    |
| Höhe: 1.656 Meter (Vertikale Stadt, 6 Organe)                                |
| Durchmesser-Gesetz: 44m Kern -> Aufweitung auf 88m bei 44m Gebäudehöhe        |
+----------------------------------+--------------------------------------------+
                                   |
                                   v (Zell-Gliederung)
+----------------------------------+--------------------------------------------+
| GORDSLIDER-KEIMKAMMER (Ring 002 / Sovereign Hall: X=0, Y=100, Z=2.5)          |
| 3D-Stammzelle (24m x 28m Saal mit Reizader & Ruheader)                        |
+----------------------------------+--------------------------------------------+
                                   |
                                   v (Stochastischer Kern)
+----------------------------------+--------------------------------------------+
| GORDSLIDER AUTOMAT (Math-Engine)                                              |
| xmur3 + mulberry32 PRNG | 5x9 Grid | 150h WAVES-Tuning | Godot/Bridge State     |
+-------------------------------------------------------------------------------+
```

1. **Geografie verankert die Basis:** Die realen NRW-Geodaten geben den exakten Geländekoordinaten-Anker in Wuppertal (Kohlstraße 11).
2. **Casino baut in die Höhe:** An der Türschwelle beginnt der 1.656m hohe Organismus, der sich nach 44m Höhe von 44m auf 88m Durchmesser aufweitet und 6 biologische Organe beherbergt.
3. **Gordslider als stochastisches Herz:** In der Sovereign Hall bildet die `GORDSLIDER_KEIMKAMMER_0001` (Ring 002) die erste funktionale Zelle, deren `xmur3`/`mulberry32` PRNG-Algorithmus den stochastischen Puls des gesamten Casino-Herzens antreibt.
