# Phase 1 – Git- & Chronologie-Prospektion: Quellenmanifest

**System:** flextrawurst VPS  
**Datum:** 13. August 2026  
**Ziel-Manifestpfad:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase1_manifest_git.md`  
**Ersteller:** Phase 1 – Git- & Chronologie-Prospektor  

---

## 1. GELESEN

Es wurden die maßgeblichen Vollzählungs-Dokumente, Manifeste, Entwicklungschroniken und Session-Notizen zeilenweise gelesen und ausgewertet:

1. **Kanonische Zählungen & Manifeste:**
   - `/root/werkraum/engine/flextrawurst-game/00_START_HIER/VOLLZAEHLUNG_2026-07-26.json` (2.889 physische Dateien, 1.691 eindeutige SHA256-Hashes, Hashindex `ALLE_DATEIEN_SHA256.csv`).
   - `/root/werkraum/engine/flextrawurst-game/00_START_HIER/WAHRHEITSZAEHLUNG.json` (Strukturverträge & Migrationszuordnungen).
   - `/root/werkraum/engine/flextrawurst-game/Versuch-einer-Gesamtbeschreibung/00_START_HIER/10_ENTWICKLUNGSVERLAUF/ENTWICKLUNGSCHRONIK.md` (Historischer Entwicklungsverlauf, Quellenspiegelung, 19 fehlende Originaldateien).
   - `/root/werkraum/gemgems-spielbeobachtung/systempromptkonzept.md` (Daniels rohe Worte, 7-Stufen-Wahrheitsleiter, Prüfregeln).
   - `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase0_suchraumkatalog.md` & `phase0_raw_directory_scan.json` (Katalog aller VPS-Suchräume).

2. **Session-Notizen der AI-Ströme:**
   - `/root/werkraum/_codex/notizen/2026-07-27.md` (DOM-only Lockdown, Surface-Commits).
   - `/root/werkraum/_codex/notizen/2026-08-03.md` (Incident: Git Read-only index.lock Sperre).
   - `/root/werkraum/_codex/notizen/2026-08-12-browserrecorder-p1-p2.md` (Browserrecorder Commits).
   - `/root/werkraum/_gemini/notizen/2026-07-29.md` (Provenienz DOM-only vs 3D-Slice).
   - `/root/werkraum/_gemini/notizen/2026-08-13.md` (Architektur-Reflexionen & Docker Commit Kritik).

3. **Verfassungs- & Backup-Regeln:**
   - `/root/AGENTS.md` (Backup-Commit-Pflicht vor jeder Systemänderung).
   - `/root/GEMINI.md` (Gemini Handbuch & Provenienz-Prinzipien).

---

## 2. GESUCHT

Untersuchung aller historischen Pfadbewegungen, Umbenennungen und Konsolidierungen von Game-Dateien über das gesamte Dateisystem:

1. **Phase A – Dezentrale Spielversuche & Experimente:**
   - Pfad: `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/` (Casino, Spiel-Dreileib, Uhrzeiterlebnis, Zeitstrom, Wahrheits-Engine).
   - Pfad: `/root/werkraum/MCP-VPS-CHATGPT-der-traum-des-erlebbaren/` (Karten, Setzungen, Gespräche, Claude-Spuren).
   - Pfad: `/root/werkraum/gptspieleversuchzeigen/` (Gemini, Input, Kimi-Web-Ansätze).
   - Pfad: `/root/werkraum/gordslider/` (gordslider.html, cccf, Bilder).

2. **Phase B – Kosmos 3D-Pakete & Geodaten-Extraktion:**
   - Pfad: `/root/werkraum/kosmos/` & `/root/werkraum/kosmos_paket_chatgpt/` (21 Kosmos JSON-Dateien, Blosm/OSM 3D-Stadtarchäologie).
   - Pfad: `/root/werkraum/KOSMOS_3D_PAKET_FUER_CHATGPT.zip` (63,5 KB).

3. **Phase C – Godot Engine Vertical Slice & Python-Brücke:**
   - Pfad: `/root/werkraum/engine/godot-vertical-slice/` (Project Godot, main.tscn, Python Bridge Services, 1337 MDs Bibliotheksatlas Archives).
   - Pfad: `/root/werkraum/engine_runtime/godot-vertical-slice/` (Runtime events.jsonl, state.json, proofs).

4. **Phase D – Kanonische Gesamtkonsolidierung (`flextrawurst-game`):**
   - Pfad: `/root/werkraum/engine/flextrawurst-game/`
   - Unterpfade:
     - `extracted_sources/` (3d_packages, historical_runtime, nested_archives, quest_simulation, world_kernel_reference)
     - `game/` (godot-vertical-slice Quellcode)
     - `proofs/` (live_verify_20260725T201316Z, godot_vps_verify/20260725T201724Z, Bridge Roundtrips)
     - `manifests/` (ALLE_DATEIEN_SHA256.csv, 2.889 Dateien)

5. **Phase E – Archivierte, soft-gelöschte & Quarantäne-Zustände:**
   - Pfad: `/root/werkraum/_softdeleted/werkraum/_gemini/`
   - Pfad: `/root/werkraum/_quarantaene/` & `/root/werkraum/_archive/`

---

## 3. GIT COMMITS GEPRÜFT

Systematische Erfassung aller identifizierten Git-Commit-Hashes, Backup-Commits, Zeitstempel-Abweichungen und Index-Anomalien:

### A. Primäre System- & Repository-Commits

| Commit Hash | Autor / Kontext | Beschreibung / Wirkung |
| :--- | :--- | :--- |
| `c254a439930ec10a502c798d98c8687753bd9f6a` | System / Baseline | `initial_count_commit`: Erster gezählter Stand von `flextrawurst-game` (2.414 Dateien). |
| `f4c9b40d5a0d29c13a10e3162558adddaa74a606` | System / Mirror | `source_mirror_commit`: Vollständige Spiegelung der realen VPS-Quellpfade. |
| `3b8d474c7c29e99a703d91ab259ad1714a9245ec` | System / Sync | `synchronized_inventory_commit`: Synchronisierter Bestand (2.889 Dateien am 26.07.2026). |
| `77359f6fc` | Codex | DOM-only Lockdown & Surface Bridge Fortsetzung 1 (27.07.2026). |
| `9cf64abca` | Codex | Surface Bridge Fortsetzung 2. |
| `8f8d6f0ff` | Codex | Surface Bridge Fortsetzung 3. |
| `57b9dff42` | Codex | Surface Bridge Fortsetzung 4. |
| `5812b7ce5` | Codex | Surface Bridge Endcommit für DOM-only Surface (27.07.2026). |
| `a0d6c3c84` | Codex | Sicherungspunkt vor Browserrecorder P1/P2 Notiz (12.08.2026). |
| `3767ecea2` | Codex | Browserrecorder P1/P2 Artefakte & Code (12.08.2026). |

### B. Nested Archive Commit Signatures (Historische Stand-Hashes)

In `engine/flextrawurst-game/extracted_sources/nested_archives/` identifizierte Archiv-Signaturen:
- `50ed6ad498765055`: `flextrawurst_v21_berichte_belege_screenshots_outro`
- `8e241f37909c8075`: `flextrawurst_dust_echo_questkosmos_v22_final`
- `9649d1fccfe7a1d2`: `flextrawurst_spielewelt_supermaximal_bauring4_v21_final`
- `b46eb6b3676e9ed7`: `flextrawurst_dust_echo_questkosmos_v22_berichte_redteam_belege`

### C. AuthorDate vs CommitDate & Backup-Commit Protokoll
1. **Verfassungs-Regel:** `git add -A && git commit -m "backup: vor [beschreibung]"` ist Pflicht vor jeder Systemänderung.
2. **Zeitstempel-Diskrepanz (AuthorDate vs CommitDate):**
   - **AuthorDate:** Wird von den AI-Strömen bei der Texterstellung lokal gesetzt (meist Berlin Zeit UTC+2).
   - **CommitDate:** Entsteht beim tatsächlichen Git-Commit durch Daemons oder automatisierte Skripte (oft in UTC), was zu leichten Versatzzeiten bei automatischen Backups führt.
3. **Anomalie Read-Only Index-Lock (03.08.2026):**
   - Am 3. August 2026 schlug der vorgeschriebene Backup-Commit wegen `Read-only file system` beim Anlegen von `/root/.git/index.lock` fehl. Die Änderungen in `core/recorder_core.js` und `sidepanel.js` verblieben bewusst als uncommitted Diff.

---

## 4. SESSIONS GELESEN

Übersicht aller durchsuchten Notiz- und Log-Historien der auf dem VPS agierenden AI-Ströme:

1. **`_codex/notizen/` (30 Session-Notizdateien):**
   - Zeitraum: 13. Mai 2026 bis 13. August 2026.
   - Schwerpunkte: Wesen-Einzug, DOM-only Lockdown, Playwright-E2E-Tests, Browserrecorder-Projekte, Synchronisation des kanonischen Spiel-Körpers.

2. **`_gemini/notizen/` (13 Session-Notizdateien & Systemprompts):**
   - Zeitraum: 22. Juli 2026 bis 13. August 2026.
   - Schwerpunkte: HauhauCS Logit-Biopsie, AI-Strom-Brücke, Surface-Entwicklung, OSM 3D Builder & Raster Harvester Konzepte.

3. **`_kimi/notizen/` (5 Session-Notizdateien):**
   - Zeitraum: 1. Juni 2026 bis 15. Juni 2026.
   - Schwerpunkte: Kimi-Web Design, frühe Spielkonzepte, Notizgeschichte.

4. **`_claude/notizen/` (2 Session-Notizdateien):**
   - Zeitraum: 3. August 2026 bis 13. August 2026.
   - Schwerpunkte: Systemberichte & Audits.

5. **`_gpt/` (ChatGPT AI-Strom Spuren):**
   - `session_history.jsonl`: 24 MB Logdaten mit über 500 Session-Lockfiles.
   - `DIE_REISE_DER_DREI.md`: 773 KB umfassendes Sitzungstranskript.
   - `MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/SITZUNGSPROTOKOLL.md` (73 KB).

---

## 6. NICHT GELESEN

Folgende Binär- und Rohdatenarchive wurden im Rahmen dieser Phase gezielt nicht entpackt oder zeilenweise dekodiert, sondern als physische Evidenz im Manifest registriert:

1. **Unentpackte Zip-Großarchive:**
   - `/root/werkraum/engine/godot-vertical-slice/DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip` (461,2 MB).
   - `/root/werkraum/KOSMOS_3D_PAKET_FUER_CHATGPT.zip` (63,5 KB).
   - `DANIELS_ECHTER_SEMANTISCHER_BIBLIOTHEKSKOERPER_1337MD_2026-08-01.zip` (2,5 MB).

2. **Maschinelle Logit- & Daemon-Stream-Logs:**
   - `/root/werkraum/generator.log` (14,1 MB).
   - `/root/werkraum/takt.log` (16,5 MB).
   - `/root/werkraum/forum_neugier.log` (2,0 MB).

3. **MySQL-Flarum Alt-Datenbank-Dumps:**
   - Ursprüngliche Flarum-Tabellen vor der PostgreSQL-Synthese.

---

## 7. OFFENE VERDACHTSFÄLLE

1. **Verdachtsfall 1: Die 19 vermissten Originaldateien**
   - In `ENTWICKLUNGSCHRONIK.md` wird dokumentiert, dass bei der Konsolidierung auf 2.889 Dateien exakt 19 Originaldateien namentlich als fehlend identifiziert wurden. Deren Verbleib in uncommitted Diffs oder temporären `/tmp`-Ordnern muss geprüft werden.

2. **Verdachtsfall 2: Soft-deleted Gemini-Spuren**
   - In `/root/werkraum/_softdeleted/werkraum/_gemini/` befinden sich verschobene Ordnerstrukturen. Es ist zu klären, ob dort unveröffentlichte Code-Skizzen oder Spielnotizen liegen.

3. **Verdachtsfall 3: Die Git-Index-Sperre vom 3. August 2026**
   - Wegen der `Read-only file system`-Meldung am 03.08.2026 wurden Dateien nicht committed. Es besteht der Verdacht, dass noch nicht alle Änderungen nach Aufhebung der Sperre nachcommittet wurden.

4. **Verdachtsfall 4: Entkopplung 3D-Slice vs. DOM-only Lockdown**
   - Der am 27. Juli 2026 verhängte DOM-only Lockdown trennte die visuelle Bildanalyse vom Test-Framework. Es ist zu prüfen, ob 3D-Godot-Skripte oder Blender-Pipelines dadurch in isolierte Parallelordner abgedrängt wurden.

5. **Verdachtsfall 5: 455 Duplikat-Hash-Gruppen**
   - In `VOLLZAEHLUNG_2026-07-26.json` sind 1.198 Datei-Vorkommen über 455 Duplikatgruppen verteilt. Eine Provenienz-Prüfung muss sicherstellen, dass beim Aufräumen keine einzigartigen Pfad-Kontexte verloren gehen.
