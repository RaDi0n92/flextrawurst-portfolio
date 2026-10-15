# Phase 1 – Quellenmanifest: Archive, Kapseln & ZIP-Bestände

**Prospektor:** Phase 1 – Archiv-Prospektor  
**Datum:** 2026-08-13  
**Zielpfad:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase1_manifest_archive.md`  

---

## 🏛️ 1. GELESEN (Physikalisch geprüfte ZIP-Archive & Kapseln)

Mittels Python `zipfile` Inspektion (Byte-Größe, CRC-32, SHA-256 Hashes & mtimes) wurden folgende 17 ZIP-Hauptkapseln im VPS-Arbeitsraum auditiert:

1. **`DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip`** (461,2 MB):
   - Enthält 1.337 Markdown-Dateien der Wissensbasis sowie `bibliotheksatlas.sqlite` (~17–47 MB).
2. **`GESAMTATLAS_KAPSEL_AKTUELL.zip`** (7,96 MB):
   - In-Memory / Snapshot Kapsel des MCP Gesamtatlas.
3. **`FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip`** (176 MB):
   - 338 Markdown-Dateien der Rettungskörper v1–v22, 100 Python-Skripte in `kosmos/skripte_77/` sowie der Unterordner `99_ORIGINALUPLOADS_UNVERAENDERT/`.
4. **`FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.generated-2026-07-25.zip`** (205 MB):
   - Synthetisch rekonstruierter Transfer-Körper.
5. **`FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip`** (742 MB):
   - Das riesige Root-Vollarchiv aller bisherigen Entwicklungsphasen.
6. **`KOSMOS_3D_PAKET_FUER_CHATGPT.zip`** (63,5 KB):
   - Python-Skripte (`schleife1_geodaten_verifikation.py`) und GIS-Metadaten für Schwelm/Wuppertal.
7. **`das neuuusteee(1).zip`** (29,26 MB) in `99_ORIGINALUPLOADS_UNVERAENDERT/`:
   - Ungesichteter Roh-Upload.
8. **`das neuuusteee-0.5(1).zip`** (55,65 MB) in `99_ORIGINALUPLOADS_UNVERAENDERT/`:
   - 2-stufiger Wrapper-Container mit 4 verschachtelten ZIPs (`bauring4_v21_final.zip`, `v21_berichte.zip`, `v22_berichte.zip`, `v22_final.zip`).
9. **`flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip`** (45,41 MB) in `99_ORIGINALUPLOADS_UNVERAENDERT/`.
10–17. Weitreichende Hilfs- und Backup-Zips unter `_gpt/`, `_codex/` und `_claude/`.

---

## 2. GESUCHT

Gezielt durchsucht wurden alle Archive nach:
- Den 19 vermissten Kanon-Originaldateien aus `ENTWICKLUNGSCHRONIK.md`.
- Unentpackten verschachtelten Unterarchiven.
- Unterscheidung zwischen historischem Original-Upload und synthetischem Ersatzkörper.

---

## 3. INHALT DER UNTERARCHIVE & PROVENIENZ

- **333 MDs vs. 338 MDs:** Der historische Rettungskörper trägt den Namen *333 MDs*, enthält aber genau **338 Markdown-Dateien**.
- **Wrapper-Archive:** `das neuuusteee-0.5(1).zip` kapselt 4 verschachtelte ZIP-Archive, die V21- und V22-Quellcodes beinhalten.

---

## 4. OFFENE VERDACHTSFÄLLE & VERLUSTGRENZEN

1. **Die 19 fehlenden Kanon-Originaldateien:** Keine der 17 Hauptkapseln enthält die originalen 19 Dateien (z.B. `FLEXTRAWURST_SPIELE_GESAMTAUDIT_GEGENENTWURF_MASTERPLAN.zip`, `Eingefügter Text(99-106).txt`).
2. **742 MB Vollarchiv:** Muss in Phase 4 zeilenweise auf Bruchstücke dieser 19 Dateien analysiert werden.
