# 🛡️ Phase 3 – Redteam Counter-Audit: Dateikörper & Archive

**Status:** REDTEAM AUDIT ABGESCHLOSSEN — LÜCKEN UND MISSKLASSIFIKATIONEN REFRECHT ERFASST  
**Erstellzeitpunkt:** 2026-08-13  
**Prüfobjekt:** `phase1_manifest_dateikoerper.md`, `phase1_manifest_kosmos.md`, `phase1_manifest_datenbanken.md` sowie physikalische Dateikörper und ZIP-Archive auf dem VPS Root (`/root`) & Werkraum (`/root/werkraum/...`).

---

## 📌 1. ÜBERSEHENE FUNDE

Expedition 1 hat in `phase1_manifest_dateikoerper.md` den Anspruch erhoben, den Dateikörper und die Spielquellen „Vollständig strukturiert und katalogisiert“ zu haben (Zeile 3). Die Gegenprüfung offenbart erhebliche Blindflecken und übergangene Quellkörper:

### A. Die 19 fehlenden Kanon-Originaldateien (Dokumentierte Verlustgrenze)
Expedition 1 hat die in `ENTWICKLUNGSCHRONIK.md`, `00_START_HIER/GEMEINSAMER_ENDZUSTAND_2026-07-25.json` und `V3_EXAKTNAMEN_NACHPRUEFUNG_2026-07-25.json` explizit nachgewiesenen **19 fehlenden Kanon-Originaldateien** in `phase1_manifest_dateikoerper.md` komplett verschwiegen und deren Status nicht auditiert:
1. `FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.zip` (Original-Upload gefehlt; nur synthetischer Ersatzkörper erzeugt)
2. `FLEXTRAWURST_SPIELE_GESAMTAUDIT_GEGENENTWURF_MASTERPLAN.zip`
3. `FLEXTRAWURST_SPIELBAU_KONTEXTANKER_2026-07-23.zip`
4. `FLEXTRAWURST_OPEN_ASSETS_V1_GITHUB_ARTIFACT.zip`
5. `FLEXTRAWURST_3D_REFERENZKORPUS_V1.zip`
6. `FLEXTRAWURST_3D_REFERENZKORPUS_V2.zip`
7. `FLEXTRAWURST_SESSIONUEBERGABE_FLEX2_V3_2026-07-23.md`
8. `FLEXTRAWURST_FLEX2_NEUE_SESSION_START_AUS_LIBRARY.md`
9. `FLEXTRAWURST_SESSIONUEBERGABE_FLEX2_V3_2026-07-23_KERNMATERIAL.zip`
10. `FLEXTRAWURST_SESSIONUEBERGABE_FLEX2_V3_2026-07-23_ARTEFAKTNACHWEIS.json`
11. `Eingefügter Text(99).txt`
12. `Eingefügter Text(100).txt`
13. `Eingefügter Text(101).txt`
14. `Eingefügter Text(102).txt`
15. `Eingefügter Text(103).txt`
16. `Eingefügter Text(104).txt`
17. `Eingefügter Text(105).txt`
18. `Eingefügter Text(106).txt`
19. `ALLE_486_MARKDOWN_DATEIEN_NACHWEIS.txt`

### B. 100 echte Python-Skripte in `/root/werkraum/kosmos/skripte_77/`
In Abschnitt 2 ("GESUCHT — Python Skripte") listete Expedition 1 lediglich 12 Python-Skripte auf. Völlig übersehen wurden die **100 strukturierten, funktionierenden Python-Skripte** in `/root/werkraum/kosmos/skripte_77/` (`01_schwelm_gebaeude_2d_3d_alkis.py` bis `100_denkmalschutz_historien_register.py`, Gesamtgröße ~360 KB). Diese Skripte bilden den Kern der prozeduralen Kataster-, Gebäude-, Dachform-, Schienen-, Gewässer- und Flora-Generatoren für Schwelm, Wuppertal, Gevelsberg, Beyenburg und Ennepetal.

### C. Unentpackte Verschachtelte ZIP-Archive in `99_ORIGINALUPLOADS_UNVERAENDERT`
In `/root/werkraum/kosmos/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER (1).zip` (extrahiert unter `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/99_ORIGINALUPLOADS_UNVERAENDERT/`) befinden sich unentpackte Roh-ZIP-Dateien:
- `das neuuusteee(1).zip` (29.26 MB)
- `das neuuusteee-0.5(1).zip` (55.65 MB)
- `flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip` (45.41 MB)
- `Eingefügter Text(98).txt` (16.68 KB)
Expedition 1 behandelte das übergeordnete Archiv als flache Dateisammlung und hat diese eingebetteten Zip-Körper nicht katalogisiert oder auf ihren Inhalt hin geprüft.

### D. Zweistufige Wrapper-Struktur von `das neuuusteee-0.5(1).zip`
Das Archiv `das neuuusteee-0.5(1).zip` (sowohl in `gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/` als auch in `99_ORIGINALUPLOADS_UNVERAENDERT/`) ist kein flaches Datei-Archiv, sondern ein **2-stufiger Wrapper-Container**, der 4 verschachtelte ZIP-Archive enthält:
1. `flextrawurst_spielewelt_supermaximal_bauring4_v21_final.zip`
2. `flextrawurst_v21_berichte_belege_screenshots_outro.zip`
3. `flextrawurst_dust_echo_questkosmos_v22_berichte_redteam_belege.zip`
4. `flextrawurst_dust_echo_questkosmos_v22_final.zip`
Diese verschachtelte Archiv-Hierarchie wurde von Expedition 1 in Phase 1 schlicht nicht dokumentiert.

### E. Versteckte Monsterlabor- & Entitätsbestände
In `/root/werkraum/_gpt/mcp_arbeitskoerper/omega_monsterlabor/` liegen Entitäts- und Monster-Generierungs-Schemata sowie Zuchtakten, die in Phase 1 weder unter Code noch unter Lore katalogisiert wurden.

### F. SQLite-Mega-Datenbanken
Die riesigen SQLite-Datenbanken in `/root/werkraum/_gpt/gesamtatlas/`:
- `BEZIEHUNGSREGISTER.sqlite` (1,50 GB)
- `BEGRIFFSINDEX.sqlite` (631,22 MB)
- `PFADINDEX.sqlite` (61,51 MB)
wurden in `phase1_manifest_dateikoerper.md` nur beiläufig erwähnt, ohne deren Schemata, Tabellenzahlen oder relationale Verknüpfungen zu erfassen.

---

## 📌 2. FALSCHE KLASSIFIKATIONEN

### A. Namens- & Zahlen-Täuschung bei `skripte_77/`
Aufgrund des Ordnernamens `skripte_77` wurde angenommen, dass darin 77 Skripte liegen. Physisch liegen darin jedoch **100 Python-Dateien** (`01_` bis `100_`). Expedition 1 unterließ die Auszählung und stufte den Ordner fälschlich als irrelevant oder ungeprüft ein.

### B. Misklassifikation von Generator-Skripten als statische Utility-Tools
Python-Skripte wie `generate_master_inventory.py`, `harvester_r2.py`, `kosmos_master_runner.py`, `lod_grid_manager.py` (in `/root/werkraum/kosmos/`) wurden als einfache administrative Hilfsskripte klassifiziert. Tatsächlich handelt es sich um prozedurale Welt- und Voxel-Generatoren mit RAM-Schutzlogiken.

### C. Misklassifikation von `.sql`-Prozeduren als passive Datenbankdateien
Die PostgreSQL-Schemadateien (`schema_welt.sql`, `schema_persoenliche_welt.sql`, `schema_entitaetenschichten.sql`, `schema_traum.sql`, `schema_blasen_tamagotchi.sql`) wurden unter passiven Artefakten abgelegt. Dabei enthalten sie aktive prozedurale SQL-Trigger (`trg_notify_events`), welche die Live-SSE-Event-Stream-Logik an Port 8030 steuern.

### D. Misklassifikation von Surface-Build- & Testskripten
Skripte wie `build_surface.ts` und `tests/surface_ring_23.test.ts` in `/root/werkraum/flextrawurst/` wurden im Code-Inventar ignoriert. Sie sind jedoch automatische Verfassungs-Wächter zur Durchsetzung der UI-Vollständigkeit.

### E. Flaches Archiv vs. Verschachtelter Container
Multi-Layer-Wrapper-ZIPs wurden als einfache flache ZIP-Dateien eingestuft, wodurch innere Archiv-Abhängigkeiten in der Provenienzverfolgung getrennt wurden.

---

## 📌 3. ZU STARKE AUSSAGEN

1. **Unberechtigte Vollständigkeitsbehauptung:**  
   Die Aussage „Status: Vollständig strukturiert und katalogisiert“ in `phase1_manifest_dateikoerper.md` ist angesichts der 100 fehlenden Python-Skripte, der 19 unaufgeklärten Kanon-Originaldateien und der unentpackten Unterarchive eine Verletzung des Verfassungs-Gesetzes (Datei-Beweis vor Behauptung).

2. **Verwechselung von vorhandenem Quest-Material mit aktiver Runtime:**  
   Phase 1 vermittelte den Eindruck, die umfangreichen v1-v22-Questakten und 37-Regionen-Manifeste seien bereits ein zusammenhängend spielbares Gesamtspiel. Tatsächlich ist **ausschließlich** der Godot 4.3 Vertikalschnitt (`godot-vertical-slice`) mit der Python-Bridge auf Port `18092` als aktive Runtime verifiziert.

3. **Gleichsetzung von synthetischem Ersatzkörper mit historischem Original:**  
   Das generierte Transfer-Archiv `FLEXTRAWURST_SPIELE_V1_BIS_V22_333MD_VERNETZT.generated-2026-07-25.zip` darf in Manifesten nicht mit den verloren gegangenen Original-Uploads verwechselt werden.

---

## 📌 4. PROVENIENZKOLLISIONEN

1. **333-MDs vs. 338-MDs Zählwert-Kollision:**  
   Der historische Projektname lautet `333 MDs`. Der physikalisch geprüfte Rettungskörper umfasst jedoch genau **338 Markdown-Dateien**. Der historische Name muss als Provenienz-Marker erhalten bleiben, ohne den realen Zählwert zu verschleiern.

2. **Mehrfache Pfad-Duplikation ohne Hash-Zuordnung:**  
   Archive wie `das neuuusteee-0.5(1).zip` existieren spiegelbildlich in `/root/werkraum/gptspieleversuchzeigen/input/16_QUE~1/ORIGINALE/` UND in `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/99_ORIGINALUPLOADS_UNVERAENDERT/`. Expedition 1 hat die identischen Hashes nicht abgeglichen, wodurch Unklarheit über den maßgeblichen Primärpfad entstand.

3. **KI-Zuhause Grundriss-Mirror-Grenzen:**  
   Der automatische Sync unter `_import_*_grundriss/` (z. B. `_import_claude_grundriss`, `_import_gpt_zuhause_grundriss`) wurde stellenweise als Gemini-eigene Notiz interpretiert, was die Trennung der KI-Ströme verletzt.

---

## 📌 5. NICHT REPRODUZIERBARE CLAIMS

1. **Fehlender Einzeldatei-Hashnachweis für unentpackte Unterarchive:**  
   Phase 1 behauptete die Prüfung aller ZIP-Archive, lieferte aber für die inneren Archive in `99_ORIGINALUPLOADS_UNVERAENDERT/` keine Zeilen- oder Hash-Nachweise.

2. **Unbestätigter Daemon-Laufzeitstatus:**  
   `cyberling_daemon.py` und `splitter_daemon.py` wurden im Manifest genannt, jedoch ohne Log-Beweis, PID-Nachweis oder SSE-Stream-Test. Gemäß Verfassung gilt: *„Code geschrieben, aber Ausführung unbestätigt.“*

---

## 📌 6. WEITER OFFENE SUCHRÄUME

1. **742 MB Root-Vollcontainer (`FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip`):**  
   Zeilenweiser und hashbasierter Abgleich der 742 MB ZIP-Datei auf Spuren der 19 fehlenden Kanon-Originaldateien.

2. **Tiefenextraktion & Katalogisierung von `99_ORIGINALUPLOADS_UNVERAENDERT`:**  
   Vollständiges Entpacken und Hash-Indizieren der ZIPs `das neuuusteee(1).zip`, `das neuuusteee-0.5(1).zip` und `flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip`.

3. **Funktions-Audit der 100 Skripte in `skripte_77/`:**  
   Systematische Prüfung aller 100 Python-Skripte auf Lauffähigkeit, Import-Abhängigkeiten und Output-Strukturen.

4. **Strukturanalyse der 1,50 GB SQLite-Datenbank `BEZIEHUNGSREGISTER.sqlite`:**  
   Vollständiger Schema-Dump und Entitäts-Graph-Extraktion.
