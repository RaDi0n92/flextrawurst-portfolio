# ⚡ TIEFENBERGUNG III — BERICHT 06: BACKEND-SKRIPTE PROVENIENZ-KLASSIFIKATION

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Provenienz-Auditor)  
**Status:** STRIKT AUDITIERT & AUS DEM SPIELATLAS AUSGESCHLOSSEN  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_3/06_backend_skripte_provenienz.md`

---

## 1. PHYSISCHES PROVENIENZ-AUDIT DER 4 BACKEND-SKRIPTE

Strenges Audit-Prinzip: **Keine direkte Spiel-Provenienz = Aus dem Spielatlas ausschließen.**

| Skript-Pfad | Dateigröße | Hauptfunktion | Klassifikation | Beleg & Begründung |
|---|---|---|---|---|
| `/root/werkraum/kosmos/skripte_77/93_wohnungstueren_und_schloesser.py` | 3.477 Bytes | ALKIS/GIS Gebäude-Extrakte für Wuppertaler Wohnungstüren. | **`PLATFORM_ADJACENT`** | Pure Python-Geodaten-Synthese. **0% HTML/JS Canvas UI, 0% Minispiel-Code**. (Kein Spielcode, aus Spielatlas ausgeschlossen). |
| `/root/werkraum/welt/splitter_daemon.py` | 16.307 Bytes | 60s-Takt-Daemon für Partikel-Decay in PostgreSQL. | **`PLATFORM_ADJACENT`** | Flextrawurst Server-Daemon für den Weltkern (Port 8787). **Kein Bestandteil des Canvas-Spiels**. |
| `/root/werkraum/welt/wesen_vault_splitter.py` | 4.808 Bytes | Obsidian-Vault Sampler der 6 Codewesen. | **`PLATFORM_ADJACENT`** | Entitäten-Ökosystem (Wesen-Vaults), **kein Spielcode**. |
| `/root/werkraum/welt/flarum_archiv_splitter.py` | 5.275 Bytes | Flarum-Post Sampler (~4.444 Posts). | **`PLATFORM_ADJACENT`** | Flarum-Vorwelt-Lore für Postgres SSE-Stream, **kein Spielcode**. |

---

## 2. FAZIT ZUR SPIELATLAS-ABGRENZUNG

Keines der 4 Skripte trägt das Prädikat `GAME_DIRECT`. Alle 4 Skripte werden **hiermit offiziell aus dem Flextrawurst-Spieleatlas ausgeschlossen** und der Flextrawurst-Plattforminfrastruktur (Port 8787 / SSE / Entitäten-Vaults) zugewiesen.
