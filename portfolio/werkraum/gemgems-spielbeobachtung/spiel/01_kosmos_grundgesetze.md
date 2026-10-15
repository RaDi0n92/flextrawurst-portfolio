---
datum: 2026-08-13
themen: [Begehbarkeit, Weltgröße, Wupper-Ennepe]
quelle: /root/werkraum/kosmos/gesetz_der_absoluten_begehbarkeit.md, /root/werkraum/kosmos/systempromptkonzept_wupper_ennepe.md
status: BACKEND-IMPLEMENTIERT (Nicht im Frontend Port 8787 sichtbar)
---

> [!NOTE]
> **AUSBAUSTUFE:** Diese Mechanik ist im Frontend (Port 8787) noch nicht sichtbar (wie der Skeptiker per Playwright bewies). **ABER:** Sie ist keine Fiktion. Im Backend existieren Python-Skripte (`lod_grid_manager.py`, `harvester_r2.py`) und geerntete JSON-Files, welche die Karte und das Raster physisch auf der Festplatte belegen.

# Spielmechanik 01: Die Wupper-Ennepe-Welt & Absolute Begehbarkeit

## 1. Die Welt-Dimension (Der Kosmos)
Das Spiel spielt im **Wupper-Ennepe-Kosmos**, einem exakt abgesteckten 300 km² großen Territorium in NRW.
- **Nullpunkt (0,0,0):** Schwelm, Hauptstraße 151.
- **Größe:** 352 Kacheln (1x1 km).
- **Fünf Zonen:** Schwelm Altstadt, Wuppertal Metropol-Achse, Wuppertal-Beyenburg, Gevelsberg, Ennepetal & Höhlensystem.

## 2. Die Mechanik der Absoluten Begehbarkeit
Es gibt keine statischen Kulissen. Jedes Gebäude in diesem 300 km² Areal ist begehbar.
- **Procedural Interior:** Innenräume werden aus LoD2-Außenhüllen prozedural generiert (inklusive Keller und Dachböden).
- **Diebes-Mechaniken:** 
  - **Lockpicking:** Türen erfordern Dietrich-Werkzeuge (aus Altstadt-Messing).
  - **Pickpocketing:** NPCs/Bewohner können unbemerkt bestohlen werden.
  - **Stealth:** Licht und Akustik bestimmen den Erfolg beim Schleichen.
- **Loot-Gradient:** Je tiefer im Gebäude (Stollen) oder höher (Dachboden), desto seltener ist der Loot (z.B. historische Münzen, Tresor-Dokumente) und die anzutreffenden Wesen.

## 3. Technische Hürden (RAM-Budget)
Das Spiel operiert unter striktem RAM-Budget: Maximal 120 MB Arbeitsspeicher pro aktiver Zone. Dies wird durch 3-stufiges LOD-Management (Level of Detail: 50m / 2km / 22km) erreicht.
