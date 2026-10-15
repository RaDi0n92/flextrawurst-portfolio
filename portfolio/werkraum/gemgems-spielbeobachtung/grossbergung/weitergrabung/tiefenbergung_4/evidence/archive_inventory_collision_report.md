# ⚠️ TIEFENBERGUNG IV — EVIDENCE: ARCHIV-INVENTAR KOLLISIONEN UND REPARATURBERICHT

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Forensik-Auditor)  
**Status:** KOLLISIONEN AUFGEKLÄRT, DETERMINISTISCH GEMESSEN UND VERANKERT  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/evidence/archive_inventory_collision_report.md`

---

## 1. URSACHENANALYSE DER ERFASSTEN KOLLISIONEN

In der ersten Fassung von Bericht 01 und des Source-Ledgers entstanden zwei gravierende Widersprüche:

### Kollision 1: `das neuuusteee(1).zip` (20 Mitglieder)
- **Bericht 01 (Alt):** Behauptete `12 PNG + 8 MD`.
- **Source Ledger (Alt):** Behauptete `17 MD + 1 JSON + 1 GZ + 1 SQLite`.
- **Ursachenanalyse:** In der ersten Schnellabfertigung von Bericht 01 wurde die Dateitypen-Zusammenfassung aus einer spekulativen Promptsynthese übernommen, anstatt das deterministische Python `zipfile`-Messnetz zu konsultieren.
- **Deterministische Wahrheit:** Exakt **17 `.md`, 1 `.json`, 1 `.gz`, 1 `.sqlite`** (Gesamt: 20 Mitglieder).

### Kollision 2: `WIE_ZUVOR_SAUBER (1).zip` (709 Mitglieder)
- **Bericht 01 (Alt):** Behauptete grob `412 MD / 120 PNG / 70 JS / 65 JSON`.
- **Source Ledger (Alt):** Nannte `486 MD / 56 JSON / 38 PNG / 36 PY / 30 JS / 45 LOG / 4 HTML / 3 TXT / 2 CSS / 4 GZ / 1 SQLite / 1 PYC / 3 ZIP`.
- **Ursachenanalyse:** Bericht 01 nutzte geschätzte Gerüstzahlen aus einem alten Überblickstext, während der Source Ledger bereits das exakte deterministische Inventar enthielt.
- **Deterministische Wahrheit:** Exakt **486 `.md`, 56 `.json`, 45 `.log`, 38 `.png`, 36 `.py`, 30 `.js`, 4 `.html`, 3 `.txt`, 2 `.css`, 4 `.gz`, 1 `.sqlite`, 1 `.pyc`, 3 `.zip`** (Gesamt: 709 Mitglieder).

---

## 2. KORREKTUR-MASSNAHMEN & BEWEISSICHERUNG

1. Sämtliche 742 Einzel-Archivmitglieder wurden zeilengenau mit Pfad, Byte-Größe, CRC32 und vollständigem SHA-256 Hash in [`evidence/archives/member_inventory.jsonl`](file:///root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/evidence/archives/member_inventory.jsonl) gesichert.
2. Eine reproduzierbare Stichproben-Auswahl mit Seed=42 wurde in [`verifiers/block01_sample_selection.json`](file:///root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/verifiers/block01_sample_selection.json) verankert.
3. Der alte Bericht `01_archive_forensics.md` bleibt als historisches Protokoll unverändert auf Disk, während [`01_archive_forensics_CORRECTED.md`](file:///root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/01_archive_forensics_CORRECTED.md) die exakten gemessenen Werte verankert.
