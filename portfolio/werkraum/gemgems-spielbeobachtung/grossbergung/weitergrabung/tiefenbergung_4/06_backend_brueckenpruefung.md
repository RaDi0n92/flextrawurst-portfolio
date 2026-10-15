# ⚡ TIEFENBERGUNG IV — BERICHT 06: BACKEND-BRÜCKENPRÜFUNG & SYSTEMD/SSE DEPENDENCY MATRIX

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Backend-Brücken-Auditor)  
**Status:** BIDIREKTIONALE SUCHE ÜBER 537 CODE-DATEIEN DURCHGEFÜHRT  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/06_backend_brueckenpruefung.md`

---

## 1. BIDIREKTIONALE REFERENZANALYSE DES CODEBASIS-SCANS (537 DATEIEN)

Jedes Skript wurde auf vorwärts- und rückwärtsgerichtete Imports, Systemd-Units, API-Routen und Shared-Table-Zugriffe geprüft:

| Skript-Pfad | Externe Referenzen in der Codebasis | Systemd / Service Anbindung | Shared DB Tables | Klassifikation |
|---|---|---|---|---|
| `/root/werkraum/kosmos/skripte_77/93_wohnungstueren_und_schloesser.py` | `scaffold_100_skripte.py` | Keine | None | **`PLATFORM_ADJACENT`** |
| `/root/werkraum/welt/splitter_daemon.py` | `browser_agent.py`, `weltfutter.py` | `splitter-physik.service` | `events` (decay) | **`PLATFORM_ADJACENT`** |
| `/root/werkraum/welt/wesen_vault_splitter.py` | `zweitgehirn.py`, `fragen_api.py`, `api.py`, `obsidian_vault_agent.py` | `welt-api.service` | `splitters` | **`PLATFORM_ADJACENT`** |
| `/root/werkraum/welt/flarum_archiv_splitter.py` | Keine (0 Referenzen) | Single-Run Script | `splitters` | **`PLATFORM_ADJACENT`** |

---

## 2. SPIELATLAS-ABGRENZUNGS-BEWEIS

Keines der 4 Backend-Skripte besitzt eine direkte Quellcode- oder Event-Verbindung zu den HTML Canvas-Spielen (`PLAY_FLEXTRAWURST_V21.html` oder `gordslider.html`). Alle 4 gehören zur **Flextrawurst Plattform- & Ökosystem-Infrastruktur**.
