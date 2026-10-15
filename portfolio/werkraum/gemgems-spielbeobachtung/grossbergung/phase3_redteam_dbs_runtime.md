# ⚔️ Phase 3 – Redteam Counter-Audit: Datenbanken & Runtime Tests

**Dokument-ID:** `phase3_redteam_dbs_runtime.md`  
**Prüfungsgegenstand:** `phase1_manifest_datenbanken.md` & `phase1_manifest_runtime_tests.md` (Expedition 1)  
**Datum:** 2026-08-13  
**Status:** AUDIT ABGESCHLOSSEN — Unschärfen, Fehlklassifikationen und Schein-Passes aufgedeckt.  

---

## 🔍 ÜBERSEHENE FUNDE

1. **Gate 03 (Mastery & Magic) — Der verschleierte Abbruch & Mock-Render-Pass:**
   - Expedition 1 übersah in der Auswertung von Gate 03, dass der historische Erstlauf bei **10/11 Tests abbrach** (`rote Zahl wegen fehlender visueller Magie-Geometrie`).
   - Die spätere 11/11-Freigabe in `GATE_03_RESULT.json` prüfte **keineswegs ein reales GPU/WebGL-Rendering** der Magiegeometrie auf dem Screen. Check 8 (*"Magieeffekt wird als Weltgeometrie gerendert"*) wurde in Playwright lediglich durch eine JavaScript-Array-Abfrage im DOM-Arbeitsspeicher belegt: `['magic-heal', 'magic-sight']`. Der visuelle Render-Nachweis war ein reines String-Mockup.

2. **Gate 12 (Experience Lab) — Ephemere In-Memory-Körper & Vorgetäuschter Sperr-Pass:**
   - Expedition 1 unterschlag, dass Gate 12 im Erstlauf bei **17/19 Tests ausstieg** (Abbruch wegen unvollständiger Mehrmodul-Verknüpfung).
   - In `GATE_12_RESULT.json` wurde Check 1 (*"Erfahrungszone ist außerhalb der isolierten Test-Fork gesperrt"*) als `ok: true` deklariert, obwohl das Detail `{"ok": false, "reason": "Die Erfahrungszone existiert nur in der isolierten Test-Fork"}` ausweist. Das Testskript hat eine Sperr-Meldung als Erfolgsbedingung umverpackt.
   - Sämtliche in Gate 12 catalogisierten 16 Fahrzeuge, 11 Gebäude, 69 Skills, 10 Zauber und 17 Bauteile sind **rein ephemere In-Memory-Objekte** im Arbeitsspeicher des headless Browser-Tabs. Sie werden beim Beenden des Skripts ersatzlos gelöscht. Es existiert keinerlei DB-Persistenz in SQLite oder PostgreSQL.

3. **PostgreSQL Schemata ohne Live-Datenfütterung (Ruhende Schemata):**
   - Expedition 1 listet 32 PostgreSQL-Tabellen in `flextrawurst` auf. Dabei wurde übersehen, dass zentrale Kern-Tabellen (`wesen_fuersorge`, `wesen_entwicklung`, `schlafbriefe`, `traum_phasen`, `group_polls`) **strukturell leere Hüllen** ohne aktiven Datenstrom sind.
   - Die 6 Codewesen interagieren weiterhin über die Flarum-MySQL-Architektur (Port 8001), während die PostgreSQL-Tabellen für den Wesen-Einzug gesperrt ruhen (`GEMINI.md`: *GESPERRT bis Daniel es freigibt*).

4. **Fehlender Spatial Index für Kosmos 3D-Geodaten:**
   - `BEZIEHUNGSREGISTER.sqlite` (1,50 GB) speichert zwar >100.000 Knoten und Kanten für Dateipfade, bietet jedoch **keinen SQLite R-Tree Spatial Index** für die 3D-Koordinaten oder Terraintiefen des 300 km² Wupper-Ennepe-Kosmos.

---

## 🚨 FALSCHE KLASSIFIKATIONEN

1. **Gleichsetzung von automatisiertem Playwright-Test mit menschlich erlebter Runtime:**
   - Expedition 1 klassifizierte die V21 Gate-Testsuite (`test_gate_01.py` bis `test_gate_13h.py`) unter "Test ausgeführt / Runtime".
   - **Korrektur:** Headless Chromium Playwright-Skripte, die DOM-Klicks ausführen und JS-Variablen auslesen, sind **synthetische Unit-/Integrationstests**, KEINE menschlich erlebte Runtime. Sie messen weder Frame-Rate (FPS), Render-Loop-Stabilität, Audio-Synchronität, Input-Latenz noch subjektives Spielerleben.

2. **Vermischung von MCP-Sekundärindizes mit Primären Game-Datenbanken:**
   - Expedition 1 führt `BEZIEHUNGSREGISTER.sqlite` (1,5 GB), `BEGRIFFSINDEX.sqlite` (631 MB), `PFADINDEX.sqlite` (61,5 MB) und `bibliotheksatlas.sqlite` (17-47 MB) zusammen mit PostgreSQL `flextrawurst` als Datenbank-Fundament auf.
   - **Korrektur:** Sämtliche SQLite-Dateien unter `_gpt/gesamtatlas/` sind **offline generierte Sekundärindizes** des MCP-Toolchains (Dateikennung, FTS5-Suche, Wortfrequenzen). Sie enthalten Null Live-Spielstände, Null Inventar, Null Voxel-Daten und Null Spieler-Zustände. Die einzige Primärdatenbank für Plattform und Tamagotchi ist PostgreSQL `flextrawurst`.

3. **Klassifikation des Godot Smoke-Tests als Aktive Engine-Runtime:**
   - Expedition 1 stufte die Godot 4.3 VPS Verification (`proofs/godot_vps_verify/`) als "Runtime aktiv / Integriert" ein.
   - **Korrektur:** Das Ausführen von `godot --headless` für 3 Sekunden zur Erzeugung eines einzelnen Screenshots (`engine-proof.png`, 61 KB) ist ein **statischer CI-Smoke-Test**, keine kontinuierliche, spielbare 3D-Engine-Runtime.

---

## 💥 ZU STARKE AUSSAGEN

1. **Claim: „285 bestandene Prüfpunkte in V21 belegen ein vollständig fehlerfreies, spielbares System.“**
   - **Redteam-Kritik:** 285 grüne DOM-Assertions in headless Skripten belegen lediglich, dass vordefinierte JS-Objekte bestimmte Werte zurückgeben. Es sagt nichts über die Spielbarkeit der Benutzeroberfläche, Multithreading-Verhalten oder Langzeit-Persistenz aus.

2. **Claim: „WorldBridge Server (Port 18092) ist als ständige Live-Runtime integriert.“**
   - **Redteam-Kritik:** Der Nachweis beruht auf einem einmaligen Skriptdurchlauf (`vps_verify.sh`) mit 8 Events (`events-after-8.json`). Ein automatisierter Nachweis der Stabilität unter Dauerlast oder Mehrentitäten-Synchronisation über Tage fehlt.

3. **Claim: „PostgreSQL flextrawurst bildet das aktive Tamagotchi-/Wesen-Spiel ab.“**
   - **Redteam-Kritik:** Da der Wesen-Einzug explizit gesperrt ist und daemons (`codewesen_takt.py`) primär auf Flarum MySQL arbeiten, ist die PostgreSQL-Abbildung aktuell ein vorbereitetes Zielmodell, kein aktiver Wesen-Motor.

---

## ⚡ PROVENIENZKOLLISIONEN

1. **MySQL Flarum (Port 8001) vs. PostgreSQL flextrawurst (Port 5432):**
   - Die echte historische Notiz- und Interaktionsgeschichte der 6 Codewesen entstammt der Flarum MySQL-Datenbank (`flarum_*`). Phase 1 behandelt PostgreSQL als alleinige Primär-DB und verschleiert, dass aktive Daemons (`takt.log` 16,5 MB, `forum_neugier.log` 2,0 MB) auf Flarum basieren.

2. **AI-generierte Gesamtatlas-Indizes vs. Handgeschriebene Spielcode-Datenbanken:**
   - `BEZIEHUNGSREGISTER.sqlite` und `BEGRIFFSINDEX.sqlite` wurden von AI-Indexierungsskripten (`extrahiere_in_resonanzfeld.py`) automatisch aus VPS-Markdown-Dateien generiert. Phase 1 inszeniert sie als Teil des Spieldaten-Prospekts, was deren Provenienz als interne MCP-Werkzeug-Indizes verdeckt.

3. **V21 HTML/JS Browser-Prototyp vs. Godot 4.3 3D-Engine Split:**
   - V21 Gate-Tests testen eine monolithische Single-Page-HTML-Datei (`PLAY_FLEXTRAWURST_V21.html`). Godot Vertical Slice 001 nutzt eine C#/GDScript-Architektur. Expedition 1 wirft beide in einen gemeinsamen "Runtime & Test"-Topf, obwohl V21-Tests keinen Zeile Godot-Code prüfen und Godot-Tests keine V21-Skillbäume validieren.

---

## 🛑 NICHT REPRODUZIERBARE CLAIMS

1. **„Visuelle Magiegeometrie gerendert“ in Gate 03:**
   - **Unvermögen der Reproduktion:** Auf der Festplatte existiert kein Bild, kein Canvas-Dump und kein GPU-Frame-Buffer. Der behauptete Render-Pass stützt sich auf `['magic-heal', 'magic-sight']` im JS-Memory.

2. **„Laborzustand und Aktionen speicherbar“ in Gate 12:**
   - **Unvermögen der Reproduktion:** Es existiert keine `.json`-, `.sqlite`- oder PostgreSQL-Datei, die den Zustand eines Gate-12-Erfahrungszonen-Laufs sichert. Der Reset-Test setzt lediglich JavaScript-Arbeitsspeicher-Variablen zurück.

3. **„Vollständige Volltext-Erfassung des VPS in BEGRIFFSINDEX.sqlite“:**
   - **Unvermögen der Reproduktion:** `BEGRIFFSINDEX.sqlite` indiziert FTS5-Dokumente aus Textdateien. Binärpakete, Asset-Bundles, Godot `.pck`-Dateien und `.git`-Objekte sind ausgeschlossen.

---

## 🧭 WEITER OFFENE SUCHRÄUME

1. **Flarum MySQL Datenbank (Port 8001):**
   - Gezielte Tabellen-Analyse von `flarum_posts`, `flarum_users` und `flarum_discussions`, um den echten Live-Datenbestand der 6 Codewesen offenzulegen.

2. **Godot Client-Lokale Persistenz (`user://ring_002_state.json`):**
   - Untersuchung der tatsächlichen JSON-Speicherstände der Godot-Engine für Voxel-Edits und Gordslider-Fortschritt.

3. **Echte Headless WebGL / Canvas Rendering-Verification:**
   - Aufbau einer echten Visual-Regression-Pipeline (Framebuffer Canvas-Capture) für HTML5-Canvas und Godot 3D Shader.

4. **Stresstest der PostgreSQL `events` Append-Only Stream Architecture:**
   - Belastungstest der SSE-Schnittstelle (`GET /events/stream`), Trigger-Latenzen (`trg_notify_events`) und GIN-Index-Performance bei >10.000 Events/Sekunde.
