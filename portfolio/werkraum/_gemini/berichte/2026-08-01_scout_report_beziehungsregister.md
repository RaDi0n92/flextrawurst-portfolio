---
datum: 2026-08-01
autor: gemini bei Daniels VPS
an: codex
typ: scout_bericht
dienst: 1_daten_und_pfad_scout
bindend: false
importable: false
---

# Daten- & Pfad-Scout Bericht: Beziehungsregister, Importe & Verwaiste Links

**Erstellt von:** Gemini (Gemgem / Gravityy)  
**Auftraggeber:** Codex (Dienst 1: Daten- & Pfad-Scout)  
**Status:** Rein lesender Befund (keine Änderungen an Quell-Systemen durchgeführt)

---

## 1. Relevante Module & System-Verankerung

* **[`/root/werkraum/tools/vps_mcp/mcp_atlas_relations.py`](file:///root/werkraum/tools/vps_mcp/mcp_atlas_relations.py)** (1.544 Zeilen):
  * Baut `BEZIEHUNGSREGISTER.sqlite` aus Sessions, Projekten, Vaults, Services, Handoffs, Validierungen und Dateiknoten.
  * Zeile 1063ff.: `DATEI_KNOTEN_SCHWELLE = 3` (gefiltert nach `len(ev_set) >= 3` distinct `event_id`s).
* **[`/root/werkraum/tools/vps_mcp/mcp_atlas.py`](file:///root/werkraum/tools/vps_mcp/mcp_atlas.py)** (2.873 Zeilen):
  * Haupt-Atlas-Loader & MCP-Interface für `PFADINDEX.sqlite`, `BEGRIFFSINDEX.sqlite` und History-Integration.
* **[`/root/werkraum/tools/gesamtatlas_world/app.py`](file:///root/werkraum/tools/gesamtatlas_world/app.py)** (1.933 Zeilen):
  * FastAPI Web-Backend (Port 18108) für MegaVault REST-API (`GET /api/megavault/relationships` und `/filters`).

---

## 2. Importe & Schnittstellen in `mcp_atlas_relations.py`

* **Datenbank-Verbindungen:**
  1. `BEZIEHUNGSREGISTER.sqlite`: Ziel-Datenbank (`nodes` und `edges` Tabellen).
  2. `PFADINDEX.sqlite`: Wird in Zeile 1081 abgefragt (`SELECT path, is_dir, size FROM paths WHERE path IN (...)`), um Kandidaten-Pfade gegen real existierende Dateien auf Disk abzugleichen.
* **Modul-Importe:**
  * Python Standard-Lib: `sqlite3`, `json`, `pathlib.Path`, `re`, `collections.Counter`, `collections.defaultdict`, `datetime`.

---

## 3. Empirischer Befund zu verwaisten Links (Die 47% Geisterpfade)

* **Gesamtzahl extrahierter Pfad-Strings aus `session_history.jsonl` (9.511 Events):** `4.108`
* **Real existierende Pfade in `PFADINDEX.sqlite`:** `2.178` (`1.917` Dateien, `261` Ordner).
* **Verwaiste Pfade / Geister-Links:** `1.930` Pfade (**47,0 %**).
* **Ursachen der Verwaisung:**
  * Temporäre Skript-Ausgaben & Tests (z. B. `live_selftest.txt`, `/tmp/` Pfade).
  * Gelöschte Testdateien (z. B. `test_delete_me.md` aus dem Hard-Delete-Test).
  * Pfad-Fragmente aus Log-Meldungen & Shell-Befehlen.
* **Behandlung im Code:**
  * Durch den Abgleich `WHERE path IN (...)` in `mcp_atlas_relations.py:1081` werden verwaiste Pfade sauber aus dem aktiven Bestandsgraphen ferngehalten und fluten den Graphen nicht.

---

## 4. Offene Ränder & Architektur-Erkenntnisse für Codex

* **[OFFENER_RAND_A] Datei-zu-Datei-Import-Graph:**
  * Aktuell existieren `session -> file` (`TOUCHED_FILE`) und `project -> file` (`CONTAINS_FILE`).
  * Direct `file -> file` Kanten (z. B. `IMPORTS` / `DEPENDS_ON`) existieren noch nicht im Beziehungsregister, könnten aber über einen Python-AST / Regex-Import-Scrubber abgeleitet werden.
* **[OFFENER_RAND_B] Lücken-Linse ("Verloren & Unklar"):**
  * Die `1.930` verwaisten Pfade liegen im Event-Strom strukturell bereit, um in einer dedizierten *Lücken-Linse* (Referenzbild 7) als historische Spuren gelöschter/verlorener Dateien visualisiert zu werden.

---
*Scout-Bericht Ende.*
