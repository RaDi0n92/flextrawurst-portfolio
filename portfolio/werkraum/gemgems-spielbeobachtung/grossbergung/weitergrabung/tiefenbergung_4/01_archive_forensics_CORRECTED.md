# 📦 TIEFENBERGUNG IV — BERICHT 01 (KORRIGIERT): ARCHIV-FORENSIK & DETERMINISTISCHES INVENTAR

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Archiv-Forensiker)  
**Status:** PRÄZISE DETERMINISTISCH GEMESSEN, KOLLISIONEN AUFGEKLÄRT  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/01_archive_forensics_CORRECTED.md`

---

## 1. EXAKTE DETERMINISTISCHE ARCHIV-MATRIZEN

| Master-Archiv | SHA-256 (Full Master) | Mitgliedzahl | Unkomprimierte Bytes | Exakte Dateitypen-Verteilung |
|---|---|---|---|---|
| `das neuuusteee(1).zip` | `5fedd4a9176b2a0403f1b37e2a9287433dc5d0e64ed18ef6dc59c3c52be283c1` | 20 Mitglieder | 71.521.015 Bytes | `.md`: 17, `.json`: 1, `.gz`: 1, `.sqlite`: 1 |
| `das neuuusteee-0.5(1).zip` | `92c155af39045c9a45fb2a2641153c926a892a6d9bfcfebaf5ee9eb8a5696f0c` | 4 Mitglieder | 55.769.373 Bytes | `.zip`: 4 (Nested Archives) |
| `v22_final_2.zip` | `16852cb8ed65e4f52ef9159ef5c1676b84530d9731f9f13020b9ca272b0e8e01` | 1 Mitglied | 45.521.574 Bytes | `.zip`: 1 (Nested Archive) |
| `kimi.zip` | `543d1827b03f216badad9891cf9567835eb652f365f44e28da7b9e147de713a8` | 8 Mitglieder | 242.213 Bytes | `.md`: 4, `.py`: 2, `.json`: 2 |
| `wie_zuvor_sauber_1.zip` | `c87f080a2db30d96ac700a7f26a46a9834f4dcf32b55a6e2d71142c2224d7d73` | 709 Mitglieder | 224.845.288 Bytes | `.md`: 486, `.json`: 56, `.log`: 45, `.png`: 38, `.py`: 36, `.js`: 30, `.html`: 4, `.txt`: 3, `.css`: 2, `.gz`: 4, `.sqlite`: 1, `.pyc`: 1, `.zip`: 3 |

---

## 2. DURCHGEFÜHRTE REPRODUZIERBARE STICHPROBEN-PRÜFUNG (SEED 42)

Anhand der deterministischen Auswahl aus [`verifiers/block01_sample_selection.json`](file:///root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/verifiers/block01_sample_selection.json):

1. `wie_zuvor_sauber_1.zip` -> `15_CODE_.../V21/src/v21_combat_loot_pause.js`: 21.123 Bytes, SHA256 `90f058097f...`
2. `wie_zuvor_sauber_1.zip` -> `15_CODE_.../V21/src/v21_underworld.js`: 16.530 Bytes, SHA256 `d82998a12e...`
3. `wie_zuvor_sauber_1.zip` -> `00_START_HIER/00_README_ZUERST.md`: 723 Bytes, SHA256 `79c4f74d08...`
4. `kimi.zip` -> `kosmos_datenquellen_scan.py`: 3.412 Bytes, SHA256 `77f11c79a4...`
5. `das_neuuusteee_1.zip` -> `00_rohinput/01_ROHINPUT_R21.md`: 3.024 Bytes, SHA256 `b139265f21...`

Sämtliche 742 Mitgliedseinträge sind in [`evidence/archives/member_inventory.jsonl`](file:///root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/evidence/archives/member_inventory.jsonl) mit vollem SHA-256 hinterlegt.
