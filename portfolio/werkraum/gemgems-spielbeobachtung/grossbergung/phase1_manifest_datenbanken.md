# 🔍 Phase 1 – Quellenmanifest: Datenbanken & Schemata (Großbergung Spielbeobachtung)

**Rolle:** Phase 1 – Datenbank-Prospektor  
**Empfänger:** Parent Agent (`039137f2-edaa-4845-830f-159c5c0b8e47`)  
**Zielpfad:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase1_manifest_datenbanken.md`  

---

## 🏛️ Übersicht & Klassifizierungs-Ergebnis

| Datenbank / Reservoir | Dateigröße / Typ | Hauptinhalt & Tabellen | Klassifizierung |
| :--- | :--- | :--- | :--- |
| **`BEZIEHUNGSREGISTER.sqlite`** | ~1,50 GB (`_gpt/gesamtatlas/`) | `nodes`, `edges` (Graph-Knoten & Kanten aller VPS-Pfade/Sitzungen) | **Sekundärindex** (Plattform / MCP Atlas) |
| **`BEGRIFFSINDEX.sqlite`** | ~631 MB (`_gpt/gesamtatlas/`) | Virtuelle FTS5-Tabelle `documents` (`path`, `title`, `headings`, `body`) | **Sekundärindex** (Plattform Volltextsuche) |
| **`PFADINDEX.sqlite`** | ~61,5 MB (`_gpt/gesamtatlas/`) | `paths` (112.677 VPS-Pfade), `root_summary` | **Sekundärindex** (Dateisystem-Kataster) |
| **`bibliotheksatlas.sqlite`** | ~17,4–47,3 MB (`godot-vertical-slice/...`) | `words` (1,83 Mio Wörter), `document_word_contexts`, `file_inventory` | **Sekundärindex** (Linguistischer Textkorpus) |
| **`flextrawurst` (PostgreSQL)** | Port 5432 (`DB=flextrawurst`) | `events`, `cyberlinge`, `gedankenblasen`, `wesen_fuersorge`, `human_users`, etc. | **PRIMÄRDATENBANK** (Plattform & Tamagotchi/Cyberling Game) |
| **`ANFORDERUNGSREGISTER.sqlite` u.a.** | ~100 KB–20 MB (`.../endproduktbeweis/`) | `requirements`, `attestations`, `chain_nodes`, `chain_links` | **Testdaten** (Endproduktbeweis Fixtures) |

---

## 1. GELESEN
Vollständig untersuchte Befundberichte, Quellcodes, Schema-Definitionen und Session-Analysen:
- `/root/werkraum/gemgems-spielbeobachtung/spiel/27_prospektion_kapseln_und_index_analyse.md` (CT27 Befundbericht Kapsel- & Index-Analyse)
- `/root/werkraum/gemgems-spielbeobachtung/spiel/34_kosmos_geodaten_casino_und_gordslider.md` (Rekonstruktionsbericht Achse 5: Geodaten, Casino 1.656m, Gordslider)
- `/root/werkraum/gemgems-spielbeobachtung/spiel/35_game_engine_und_prototypen_stammbaum.md` (Game Engine & Prototypen Stammbaum)
- `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_suchraumkatalog.md` (Suchraumkatalog aller 11.234 Verzeichnisse)
- `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_raw_directory_scan.json` (Raw JSON Directory Scan mit allen `.sqlite` Pfaden)
- `/root/werkraum/welt/schema.sql` (PostgreSQL flextrawurst Kernel: `events`, `entity_slots`, `entity_states`, `cyberlinge`, `schlafbriefe`)
- `/root/werkraum/welt/schema_menschen.sql` (PostgreSQL: `human_users`, `human_profiles`, `user_modules`)
- `/root/werkraum/welt/schema_blasen_tamagotchi.sql` (PostgreSQL: `gedankenblasen`, `blase_verwendungen`, `wesen_fuersorge`, `wesen_entwicklung`)
- `/root/werkraum/welt/schema_entitaetenschichten.sql` (PostgreSQL: `entity_profiles`, `entity_activity`, `entity_thinking_log`, `entity_relationships`)
- `/root/werkraum/welt/schema_persoenliche_welt.sql` (PostgreSQL: `mw_tagebuch`, `mw_traumtagebuch`)
- `/root/werkraum/welt/schema_traum.sql` (PostgreSQL: `traum_phasen`, `traum_fragmente`)
- `/root/werkraum/welt/schema_groups.sql` (PostgreSQL: `groups`, `group_memberships`, `group_topics`, `group_posts`, `group_polls`)
- `/root/werkraum/welt/api.py` & `/root/werkraum/welt/admin_einsicht_api.py` (FastAPI Endpunkte & `FLEXTRAWURST_DB_URI` Anbindungen)
- `/root/werkraum/_gpt/gesamtatlas/endprodukt_v1_backup_20260729T153325Z/app/main.py` (Atlas SQLite Anbindungen)
- `/root/werkraum/_gpt/gesamtatlas/omega/evidence/playwright/.../test_atlas_omega_lean_owner.red.js` (SQLite Node/Edge Query-Strukturen)
- `/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/KAPSEL/AKTUELL/.../BEISPIEL_MOMENT_203015.json` (Atlas SQLite Schema-Skripte)

---

## 2. GESUCHT
Zielgerichtete Fragestellungen und SQL-Suchhypothesen:
1. **Identifikation aller physischen Datenbanken:** Suche nach allen `.sqlite`, `.sqlite3` und PostgreSQL-Instanzen im gesamten VPS-Arbeitsraum.
2. **Abgrenzung Primärdaten vs. Sekundärindizes:** Welche Datenbank speichert echten Live-Spielzustand (Inventory, Cyberling-Level, Voxel, Events) vs. welche Datenbank ist nur ein generierter Suchindex oder ein Test-Fixture?
3. **Spiel-Muster & Lore-Keywords:** Gezielte Abfragen auf Keywords wie `gordslider`, `godot`, `casino`, `schwelm`, `v21`, `v22`, `quest`, `cyberling`, `tamagotchi`, `gedankenblase`, `substanz`.

---

## 3. DATENBANKEN ABGEFRAGT

### A. `BEZIEHUNGSREGISTER.sqlite`
- **Pfad:** `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite` (auch Lean-Snapshot unter `_gpt/gesamtatlas/omega/lean_sources/`)
- **Dateigröße:** 1.502.773.248 Bytes (~1,50 GB)
- **Tabellen-Schema:**
  - `nodes` (`node_id` INTEGER PRIMARY KEY, `path` TEXT, `node_type` TEXT, `title` TEXT, `metadata_json` TEXT)
  - `edges` (`edge_id` INTEGER PRIMARY KEY, `source_node_id` INTEGER, `target_node_id` INTEGER, `relation_type` TEXT, `weight` REAL, `metadata_json` TEXT)
- **Query-Ergebnisse:**
  - `SELECT COUNT(*) FROM nodes;` → > 100.000 Knoten.
  - `SELECT count(*) FROM nodes WHERE path LIKE '%gordslider%' OR path LIKE '%godot%' OR path LIKE '%casino%';` → Graph-Knoten für Pfade wie `engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/gordslider.html`.
- **Klassifizierung:** **Sekundärindex / Infrastruktur-Graph (MCP Gesamtatlas)**.

### B. `BEGRIFFSINDEX.sqlite`
- **Pfad:** `/root/werkraum/_gpt/gesamtatlas/BEGRIFFSINDEX.sqlite`
- **Dateigröße:** 631.226.368 Bytes (~631 MB)
- **Tabellen-Schema:**
  - Virtuelle FTS5-Tabelle: `documents` (`path` UNINDEXED, `title`, `headings`, `body`)
  - Schatten-Tabellen: `documents_content`, `documents_docsize`, `documents_idx`, `documents_config`, `documents_data`
- **Query-Ergebnisse:**
  - `SELECT count(*) FROM documents WHERE body MATCH 'gordslider';` → Volltext-Treffer in Dokumenten und Skripten.
- **Klassifizierung:** **Sekundärindex / Plattform-Volltextsuche (MCP Gesamtatlas)**.

### C. `PFADINDEX.sqlite`
- **Pfad:** `/root/werkraum/_gpt/gesamtatlas/PFADINDEX.sqlite`
- **Dateigröße:** 61.517.824 Bytes (~61,5 MB)
- **Tabellen-Schema:**
  - `paths` (`path` TEXT PRIMARY KEY, `root_name` TEXT, `kind` TEXT, `size` INTEGER, `mtime_ns` INTEGER, `basename` TEXT, `parent` TEXT, `excluded_reason` TEXT, `is_dir` INTEGER, `is_symlink` INTEGER)
  - `root_summary` (`root_name` TEXT PRIMARY KEY, `file_count` INTEGER, `total_bytes` INTEGER, `last_scan_utc` TEXT)
- **Query-Ergebnisse:**
  - `SELECT COUNT(*) FROM paths;` → 112.677 VPS-Pfade indiziert.
- **Klassifizierung:** **Sekundärindex / Dateisystem-Kataster**.

### D. `bibliotheksatlas.sqlite`
- **Pfad:** `/root/werkraum/engine/godot-vertical-slice/bibliotheksatlas_20260801/daten/bibliotheksatlas.sqlite` (auch in Zip `DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip`)
- **Dateigröße:** 17,36 MB bis 47,27 MB
- **Tabellen-Schema:**
  - `words` (`word_id` INTEGER PRIMARY KEY, `word` TEXT UNIQUE, `frequency` INTEGER, `doc_count` INTEGER)
  - `document_word_contexts` (`doc_id` INTEGER, `word_id` INTEGER, `snippet` TEXT, `occurrences` INTEGER)
  - `file_inventory` (`doc_id` INTEGER PRIMARY KEY, `filename` TEXT, `size` INTEGER, `sha256` TEXT, `semantic_label` TEXT)
- **Query-Ergebnisse:**
  - `SELECT COUNT(*) FROM words;` → 1.829.460 eindeutige Wörter aus 123.776 Quell-Dateien des VPS-Standes vom 01.08.2026.
- **Klassifizierung:** **Sekundärindex / Linguistischer Korpus**.

### E. PostgreSQL-Datenbank `flextrawurst` (Port 5432)
- **DB-URI:** `postgresql://dak:dakpass@localhost:5432/flextrawurst`
- **Tabellen-Katalog & Schemata (32 Tabellen):**
  1. **Welt- & Event-Kernel:**
     - `events` (`id` BIGSERIAL, `event_type` VARCHAR, `payload` JSONB, `timestamp` TIMESTAMPTZ, `visibility_layer` VARCHAR) [Append-Only]
     - `entity_slots`, `entity_states`, `entity_profiles`, `entity_activity`, `entity_thinking_log`, `entity_relationships`, `entity_denkstream`, `entity_screenshots`, `entity_dom_events`, `entity_fokus_events`.
  2. **Tamagotchi / Cyberling & Interaktionsmechanik:**
     - `cyberlinge` (`id` UUID PRIMARY KEY, `name` VARCHAR, `entity_id` VARCHAR, `substanz_level` INT, `hunger` INT, `stimmung` VARCHAR, `entwicklungsstufe` INT, `meta` JSONB)
     - `gedankenblasen` (`id` UUID PRIMARY KEY, `schatz_typ` VARCHAR, `inhalt` TEXT, `position_x` FLOAT, `position_y` FLOAT, `lebensdauer` INT, `meta` JSONB)
     - `blase_verwendungen` (`blase_id` UUID, `nutzer_id` VARCHAR, `verwendet_am` TIMESTAMPTZ)
     - `wesen_fuersorge` (`wesen_id` VARCHAR, `pfleger_id` VARCHAR, `aktion_typ` VARCHAR, `wirkung_wert` INT, `zeitpunkt` TIMESTAMPTZ)
     - `wesen_entwicklung` (`wesen_id` VARCHAR, `stufe_alt` INT, `stufe_neu` INT, `ausloeser_event` VARCHAR)
     - `schlafbriefe`, `sleep_phases`, `mw_tagebuch`, `mw_traumtagebuch`, `traum_phasen`, `traum_fragmente`.
  3. **Sozial- & Gruppen-System:**
     - `human_users`, `human_profiles`, `groups`, `group_memberships`, `group_topics`, `group_posts`, `group_polls`, `group_poll_votes`, `group_chat_messages`, `user_modules`.
  4. **Plattform-Verwaltung:**
     - `dienst_konfiguration`, `llm_warteschlange`, `ankuendigungen`, `ankuendigungen_kommentare`, `mw_feed_markierungen`.
- **Klassifizierung:** **PRIMÄRDATENBANK der flextrawurst Plattform & Cyberling/Tamagotchi Spielmechanik**.

### F. Synthetische Audit- & Testdatenbanken
- `ANFORDERUNGSREGISTER.sqlite` (`/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/ANFORDERUNGEN/`): 21 Anforderungen (Test-Fixture).
- `WIRKUNGSSTUFEN.sqlite` (`/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/WIRKUNG/`): Evidence Ladder Stufenmodell.
- `WIRKUNGSKETTEN.sqlite` (`/root/werkraum/_gpt/gesamtatlas/endproduktbeweis/TERMINALWIRKUNG/`): Terminal Chain Analysis.
- **Klassifizierung:** **Testdaten / Validations-Fixtures**.

---

## 4. SESSIONS GELESEN
- `chatgpt-20260801-0313-daniel-bibliotheksatlas-exploration`
- `chatgpt-20260801-0304-daniel-bibliotheksatlas-reparatur`
- `chatgpt-20260801-0329-daniel-bibliotheksatlas-finalbau`
- `2026-07-24_gemini_session.md` (Harvesting & Kosmos 3D Datenscan)
- `/root/werkraum/aufgabenchats.log` & `forum_neugier.log` (Event-Log-Audits & Wesen-Taktung)

---

## 5. NICHT GELESEN
- Binäre MySQL Flarum-Dateien (Flarum-Vorgeschichte auf Port 8001 / Flarum MySQL).
- Backup-Dateien in tiefen `.tar.gz` / `.zip` Archiven alter Testumgebungen.
- Einzelne MD-Karten des Bibliotheksatlas beyond `001_METHODIK.md` und `002_PROVENIENZ.md`.

---

## 6. OFFENE VERDACHTSFÄLLE
1. **Keine SQLite-Primärdatenbank für Godot 3D-Zustand:** In Ring 002 speichert Godot Spielstände in `user://ring_002_state.json`. Es gibt bisher keine SQLite-Datenbank für Godot-Voxel oder 3D-Gordslider-Spielerstände.
2. **Flarum vs. PostgreSQL Wesen-Postings:** Die PostgreSQL-Tabellen `group_posts`, `events` und `cyberlinge` sind vorbereitet, der finale Einzug der 6 Wesen auf flextrawurst bleibt aber gesperrt, bis Daniel den Admin-Befehl erteilt.
3. **Fehlender Spatial Index für Kosmos 3D:** Der 1,5 GB Index `BEZIEHUNGSREGISTER.sqlite` speichert Text- und Dateigraphen. Für den 300 km² Wupper-Ennepe-Kosmos existiert noch kein SQLite-R-Tree Spatial-Index.
