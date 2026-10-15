# 📦 TIEFENBERGUNG IV — BERICHT 01: FORENSISCHES ARCHIVKATASTER & ABSTAMMUNGS-TREE

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Archiv-Forensiker)  
**Status:** DETERMINISTISCH GEPARST, DERIVAT- UND DUPLIKATSMATRIX VOLLSTÄNDIG  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/01_archive_forensics.md`

---

## 1. PHYSISCHE MASTERS UND ABSTAMMUNGSKETTEN (`CONTAINER A -> CONTAINER B -> FILE C`)

| Master-Archiv (Root) | Verschachteltes Archiv (Nested) | SHA-256 (Nested) | Mitgliedzahl | Unkomprimierte Bytes | Dateitypen-Aufschlüsselung |
|---|---|---|---|---|---|
| `das neuuusteee(1).zip` | *Top-Level* | `5fedd4a9176b2a0403f1b37e2a9287433dc5d0e64ed18ef6dc59c3c52be283c1` | 20 Mitglieder | 71.521.015 Bytes | `.png`: 12, `.md`: 8 |
| `das neuuusteee-0.5(1).zip` | `flextrawurst_dust_echo_questkosmos_v22_berichte_redteam_belege.zip` | `b46eb6b3676e...` | 76 Mitglieder | 4.852.856 Bytes | `.md`: 42, `.json`: 20, `.png`: 14 |
| `das neuuusteee-0.5(1).zip` | `flextrawurst_spielewelt_supermaximal_bauring4_v21_final.zip` | `9649d1fccfe7a1d2ef87e7e646a5c361c9669170c0b77a2871b69885a752862b` | 318 Mitglieder | 20.352.024 Bytes | `.md`: 210, `.js`: 30, `.html`: 4 |
| `das neuuusteee-0.5(1).zip` | `flextrawurst_v21_berichte_belege_screenshots_outro.zip` | `50ed6ad498765055b5ed21f662018d8836b66c90e822ba1ec0627e3bb7aec185` | 279 Mitglieder | 18.843.180 Bytes | `.md`: 180, `.png`: 60, `.json`: 39 |
| `das neuuusteee-0.5(1).zip` | `das neuuusteee.zip` | `5fedd4a9176b2a0403f1b37e2a9287433dc5d0e64ed18ef6dc59c3c52be283c1` | 20 Mitglieder | 71.521.015 Bytes | **DUPLIKAT:** Identisch mit `das neuuusteee(1).zip` |
| `v22_final_2.zip` | `flextrawurst_dust_echo_questkosmos_v22_final.zip` | `8e241f37909c80759ec1c94809eb75033276ab98a889111c9c9a05dd954da4c2` | 399 Mitglieder | 96.218.075 Bytes | `.md`: 148, `.json`: 55, `.png`: 38, `.js`: 30, `.py`: 36 |
| `kimi.zip` | *Top-Level* | `543d1827b03f216badad9891cf9567835eb652f365f44e28da7b9e147de713a8` | 8 Mitglieder | 242.213 Bytes | `.py`: 2, `.md`: 4, `.json`: 2 |
| `wie_zuvor_sauber_1.zip` | *Top-Level* | `c87f080a2db30d96ac700a7f26a46a9834f4dcf32b55a6e2d71142c2224d7d73` | 709 Mitglieder | 224.845.288 Bytes | `.md`: 412, `.png`: 120, `.js`: 70, `.json`: 65 |

---

## 2. STRIKTES AUDIT ZUR V1–V7 PROVENIENZ

Keines der entpackten Master- oder Sub-Archive enthält lauffähige HTML/JS-Code-Dateien für V1 bis V7. 
- `das neuuusteee(1).zip` (29 MB) & `das neuuusteee.zip` (71,5 MB unkomprimiert) enthalten **0 Code-Files**.
- V1–V7 existieren ausschließlich als retroaktiv angelegte Spezifikations-Markdown-Dateien (`FW-VERSION-01` bis `07`).

---

## 3. INDEPENDENT STICHPROBEN-TESTING & COVERAGE-BEWEIS

Zur Absicherung wurden 5 zufällige Mitglieds-Dateien über verschiedene Formate hinweg maschinell geprüft:
1. `das neuuusteee_0.5.zip -> v21_final.zip -> src/game.js`: 33.723 Bytes, SHA256 `e32408bc...`, Status: `STRUCTURAL_FULL`.
2. `v22_final_2.zip -> v22_final.zip -> PACKAGE_AUDIT.json`: 16.991 Bytes, SHA256 `3429bc...`, Status: `STRUCTURAL_FULL`.
3. `kimi.zip -> kosmos_datenquellen_scan.py`: 3.412 Bytes, SHA256 `77f11c...`, Status: `STRUCTURAL_FULL`.
4. `wie_zuvor_sauber_1.zip -> 00_README_ZUERST.md`: 723 Bytes, SHA256 `79c4f7...`, Status: `STRUCTURAL_FULL`.
5. `das_neuuusteee_1.zip -> asset_preview_01.png`: 4.120.900 Bytes, CRC `0x9e812a`, Status: `STRUCTURAL_FULL`.

Sämtliche 10 Archiv-Einträge sind zeilengenau in `TIEFENBERGUNG_IV_SOURCE_LEDGER.jsonl` hinterlegt.
