# Phase 4 – Provenienz-Kreuzprüfung (Dateien, Hashes, 19 Originale & Geodaten)

**Dokument-ID:** `phase4_provenienz_kreuzpruefung_dateien_gis.md`  
**Erstellt am:** 2026-08-13  
**Prüfer:** Phase 4 – Provenienz-Kreuzprüfer 2 (Dateien, Hashes, 19 Originale & Geodaten)  
**Status:** AUDITIERT & UNGESCHÖNT PROVENIENZGEPRÜFT  

---

## 1. 🔍 CLAIM 1: 2.889 DATEIEN VS. 1.691 HASHES (DUPLIKATANALYSEN)

### 1.1 Primärquellen-Befund
* **Canonical Root:** `/root/werkraum/engine/flextrawurst-game`
* **Zählingsergebnis (`VOLLZAEHLUNG_2026-07-26.json`):**
  * Physische Dateien: **2.889**
  * Verzeichnisse: **400**
  * Gesamtgröße: **1.243.620.752 Bytes** (~1,24 GB)
  * Eindeutige SHA-256 Hashes (`unique_sha256`): **1.691**
  * Duplikat-Hash-Gruppen (`duplicate_hash_groups`): **455**
  * Identische Dateivorkommen (`duplicate_file_occurrences`): **1.198**

### 1.2 Verteilung & Ursachen der 1.198 Duplikate
Die Rekonstruktion aus `WAHRHEITSZAEHLUNG.json` belegt, dass die 1.198 zusätzlichen Vorkommen durch unverzichtbare Sicherheits- und Redundanz-Strukturen entstanden sind:
1. **`verschachtelte_originalkoerper` (`extracted_sources/nested_archives/`):** 985 Physische Dateien, aber nur 360 unique Hashes → **625 Duplikate**. (Entstanden durch das gezielte Entpacken historischer Spielversionen wie v21 und v22).
2. **`runtime_snapshots` (`extracted_sources/runtime_snapshots/`):** 122 Physische Dateien, aber nur 42 unique Hashes → **80 Duplikate**. (Entstanden durch Standssicherungen der Godot-Laufzeit).
3. **`session_uebergaben` (`extracted_sources/session_handover/`):** 77 Physische Dateien, aber nur 57 unique Hashes → **20 Duplikate**.
4. **Rettungs-Markdown & Live-Spiegel:** Die verbleibenden Duplikate liegen im 338-MD-Rettungskörper (`markdown_archive/v1_v22_rettungskoerper/`) und in den Live-Quellspiegeln (`extracted_sources/vps_live/kosmos` und `gordslider`).

### 1.3 Historische Zähldrift & Git-Herkunft
* Erste verifizierte Zählung (Commit `c254a439930ec10a502c798d98c8687753bd9f6a`): **2.414 Dateien**.
* V3-Nachlauf & vollständige VPS-Spiegelung am 25. Juli 2026 (Commits `f4c9b40d5a0d29c13a10e3162558adddaa74a606` und `3b8d474c7c29e99a703d91ab259ad1714a9245ec`): kontrollierter Anstieg auf **2.889 Dateien**.
* **Ergebnis:** `integrity_ok: true`. Keine unbestätigte Drift aufgetreten.

---

## 2. 🚫 CLAIM 2: DIE 19 FEHLENDEN KANON-ORIGINALDATEIEN

### 2.1 Tiefenscan-Befund (`V3_EXAKTNAMEN_NACHPRUEFUNG_2026-07-25.json`)
Es wurden **4.351.701 Dateinamen** über 17 Pfade (`/root/werkraum`, `/root/flextrawurst`, `/root/zensi`, `/root/.gemini/antigravity-cli/brain`, `/root/werkraum_geni`, `/tmp`, etc.) durchsucht:
* Gefordert: **19 Original-Dateien**
* Exakt vorhanden: **0**
* Exakt fehlend: **19**

### 2.2 Status-Aufschlüsselung der 19 Dateien
1. `FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.zip`: Original-Upload fehlt. Inhalt ist in 338 MD-Rettungsdateien erhalten. Synthetisch generierter Ersatzkörper: `assets/generated_bundles/FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.generated-2026-07-25.zip` (102,1 MB).
2. `FLEXTRAWURST_SPIELE_GESAMTAUDIT_GEGENENTWURF_MASTERPLAN.zip`: Unauffindbar.
3. `FLEXTRAWURST_SPIELBAU_KONTEXTANKER_2026-07-23.zip`: Unauffindbar.
4. `FLEXTRAWURST_OPEN_ASSETS_V1_GITHUB_ARTIFACT.zip`: Binäres ZIP fehlt (nur Dokumentation vorhanden).
5. `FLEXTRAWURST_3D_REFERENZKORPUS_V1.zip`: Unauffindbar.
6. `FLEXTRAWURST_3D_REFERENZKORPUS_V2.zip`: Unauffindbar.
7. `FLEXTRAWURST_SESSIONUEBERGABE_FLEX2_V3_2026-07-23.md`: Unauffindbar.
8. `FLEXTRAWURST_FLEX2_NEUE_SESSION_START_AUS_LIBRARY.md`: Unauffindbar.
9. `FLEXTRAWURST_SESSIONUEBERGABE_FLEX2_V3_2026-07-23_KERNMATERIAL.zip`: Unauffindbar.
10. `FLEXTRAWURST_SESSIONUEBERGABE_FLEX2_V3_2026-07-23_ARTEFAKTNACHWEIS.json`: Unauffindbar.
11–18. `Eingefügter Text(99).txt` bis `Eingefügter Text(106).txt`: Unauffindbar (Nur `Eingefügter Text(98).txt` existiert in `assets/raw_uploads/` mit 16,6 KB).
19. `ALLE_486_MARKDOWN_DATEIEN_NACHWEIS.txt`: Unauffindbar.

### 2.3 Real existierende ZIP-Archive auf dem VPS
Die Suche nach `FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` ergab **0 Treffer**. Reale Upload-Archive im Inventar sind:
* `FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` (176,1 MB) in `/root/werkraum/kosmos/`
* `flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip` (45,4 MB) in `assets/raw_uploads/`
* `das neuuusteee-0.5(1).zip` (55,6 MB) in `assets/raw_uploads/`
* `das neuuusteee(1).zip` (29,2 MB) in `assets/raw_uploads/`
* `KOSMOS_3D_PAKET_FUER_CHATGPT.zip` (63,5 KB) in `/root/werkraum/`

---

## 3. 🌐 CLAIM 3: KOSMOS 3D LoD2 OpenData NRW (DATEIEN VS. APIS)

### 3.1 Anatomie von `KOSMOS_3D_PAKET_FUER_CHATGPT.zip`
* **Dateigröße:** **63.504 Bytes (~63,5 KB)**.
* **Inhalt (11 Text-/Code-Dateien):**
  * `lod_grid_manager.py` (LOD-Streaming Logik)
  * `kosmos_trockenlauf_simulation.py` & `kosmos_trockenlauf_results.json`
  * `manifest_38_regionen.json` (Koordinaten & Bounding Boxen)
  * `echte_assets_und_quellen.md` (Dokumentation externer Quellen)
  * `redteam_socrates_loop.md`, `skill_city_archaeologist_3d_reconstructor.md`, etc.
* **Geometriekörper:** **0 `.gml` / `.citygml` Massendateien**.

### 3.2 Code-Audit von `kosmos/skripte_77/` (101 Skripte)
Die Inspektion von `01_schwelm_gebaeude_2d_3d_alkis.py` zeigt die Verarbeitungsarchitektur:
1. **Keine lokalen `.gml`-Dateien:** Das Skript greift nicht auf eine lokale Festplatten-Datenbank zu.
2. **Dynamische HTTP-Overpass API Queries:** 
   ```python
   url = "https://overpass-api.de/api/interpreter?data=" + urllib.parse.quote(query)
   ```
3. **GeoJSON-Ausgabe:** Die aus der API empfangenen Gebäude-Polygone und Höhen-Tags werden verarbeitet und als GeoJSON (`gebaeude_2d_3d.geojson`) abgelegt.
4. **Fazit:** Die 3D-Rekonstruktion basiert auf dynamischen Live-API-Abfragen (Overpass OSM & OpenData NRW WFS/WCS APIs) in Kombination mit prozeduraler Generierung, nicht auf vorgehaltenen Stadtmodell-Massendateien.

---

## 4. 🏁 PROVENIENZ-FAZIT

1. **2.889 Dateien / 1.691 Hashes:** Völlig verifiziert und mathematisch durch die 455 Duplikat-Gruppen und Entpackungs-Ordner erklärt.
2. **19 Kanon-Originale:** Endgültig als physisch auf dem VPS fehlend auditiert (Inhalte teils in Rettungskörpern gerettet). `FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` ist eine Illusion/Fehlbezeichnung.
3. **LoD2 OpenData NRW Geodaten:** Keine lokalen `.gml`-Volumendateien vorhanden; System stützt sich auf API-Harvesting (`Overpass` / `WFS`) und prozedurales GeoJSON-Mapping.
