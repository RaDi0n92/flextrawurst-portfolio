# 📜 Tiefenbergung II – Bericht 08: Kosmos-Zahlen- & Geodaten-Wahrheitsmatrix

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Hauptagent-Synthese)  
**Status:** AUDITIERT & GEOMETRISCH BEWIESEN  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_2/08_kosmos_geodaten_wahrheitsmatrix.md`

---

## 1. KOSMOS-ZAHLEN WAHRHEITSMATRIX

| Kennzahl | Behauptung im Korpus | Mathematischer / Kartografischer Ursprung | Physischer Code-/Daten-Beweis | Wahrheit & Interpretation |
|---|---|---|---|---|
| **360,72 km²** | Brutto-Gesamtfläche | $0,15^\circ \text{ Lat} \times 0,31^\circ \text{ Lon}$ Rechteck-Bounding-Box | `systempromptkonzept_wupper_ennepe.md` (Lat 51.195-51.345, Lon 7.065-7.375) | Brutto-Hüllbox des Wupper-Ennepe-Grids. |
| **298,5 km²** | Netto-Territorium | Polygonzuschnitt der 5 Kommunalzonen (Schwelm, Wuppertal, Beyenburg, Gevelsberg, Ennepetal) | Summe der Gemeindegrenzen 294,4 km² + 4,1 km² Korridorpuffer = 298,5 km² | Effektives, story-physikalisch belegtes Territorium ($82,75\%$ der Hüllbox). |
| **352** | Quadranten-Anzahl | $1 \text{ km} \times 1 \text{ km}$ Kachel-Raster | $22 \text{ Spalten (Ost-West)} \times 16 \text{ Zeilen (Nord-Süd)} = 352$ Kacheln | Rasterung für LoD2-Building & DGM1 Höhendaten. |
| **37 vs. 38** | Regionen-Anzahl | Manifest-Dateiname vs. Manifest-Inhalt | `/root/werkraum/kosmos/manifest_37_regionen.json` (38 `region_id`-Blöcke) | Dateiname historisch 37; im JSON durch Trennung Wuppertaler Talbahn 38 Regionen. |
| **1.656 m** | Casino-Höhe | Vertikale Spezifikation des Casino-Organismus | `CASINO_ORGANISMUS_MASTER.md` & `casino_cell_builder.gd` (`casino_master_height_m = 1656`) | Symbolische & metadatenmäßige Gesamthöhe (doppelte Burj-Khalifa-Höhe). |

---

## 2. PHANTOM-HASH FORENSIK MATRIX (`e3b0c442...`)

| Manifest-Quelle | Claim / Behauptetes Artefakt | Behauptete Größe | Verifikations-Hash | Realer VPS-Zustand | Ergebnis |
|---|---|---|---|---|---|
| `gen1_city_bunker_alpha_harvest.json` | `berlin_bunker_v1.glb` | 14.589.000 Bytes | `e3b0c442...855` | Pfad `/kosmos/untergrund/berlin_bunker_v1.glb` existiert NICHT | **KI-Phantom-Claim** (Hash is SHA-256 of `""`). |
| `gen1_schwelm_alpha_harvest.json` | `ftw_schwelm_hauptstrasse_151_v1` | 1.425.000 Bytes | `e3b0c442...855` | Pfad-String ist leere Zeichenkette `""` | **Prosa-Platzhalter** |
| `ftw_schwelm_rathaus_v1_manifest.json` | `ftw_schwelm_rathaus_v1.geojson` | 452 Bytes | `e3b0c442...855` | `ftw_schwelm_rathaus_v1.geojson` existiert (794 Bytes) | **Realer 2D-Polygonkörper** mit falschem Manifest-Hash |
| `gen2_schwelm_beta_math_redteam.json` | `CERT-REDTEAM-GEN2-BETA-H151-001` | PASS Zertifikat | `e3b0c442...855` | JSON-Eintrag ohne externe Signatur | **Synthetisches Test-Zertifikat** |
| `3d_pipeline_prüfbericht.json` | `test_cube.obj` | Mock Artifact | `e3b0c442...855` | Quell-OBJ 0 Bytes oder Mock | **Pipeline Validation Mock** |
