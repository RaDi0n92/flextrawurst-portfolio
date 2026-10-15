# 02. Alte Web- & Prototypen-Gräber — Weitergrabungsbericht

## NEUE FUNDE
- **Gord-Slider Casino-Prototyp (`gordslider/gordslider.html`)**: Ein 110 KB großer, 3.812 Zeilen umfassender Ein-Datei-Webprototyp mit dem Titel `sandycheats`. Der Prototyp simuliert einen 5x9-Reel-/Grid-Slot- und Slider-Organismus. Enthalten sind ein Paytable-Editor, PRNG-Seed-Generierung (`xmur3`, `mulberry32`), Symbol-Strips, Kaskaden-Mechanik (`uiCascade`), Freispiel-Bank (`uiFsBank`), Buy-Features (buy10, buy20, buy30, buy50), Wave-Modi sowie Debug- und Click-Safety-Schichten.
- **Historische Ein-Datei-HTML-Spielkörper (V15.1, V17, V21)**:
  - `PLAY_FLEXTRAWURST_V15_1.html` (193 KB): Vollständiger HTML5-Spielkörper für MAXUS Bauring 2.
  - `PLAY_FLEXTRAWURST_V17.html` (225 KB): Spielkörper mit implementierter Dust Ecology (Staub-Ökologie).
  - `PLAY_FLEXTRAWURST_V21.html` (544 KB): Supermaximaler Bauring 4 Spielkörper mit 2D/Pseudo-3D Canvas-Renderer, MiniMap, Status-Metrik (Gesundheit, Ausdauer, Atem), Rohstoff-Inventar (Metall, Faser, Glas, Kern, Ladung, Credits), 69 Skillbäumen mit 276 Knoten, 12 Makroregionen, Fahrzeugzuständen (`zu Fuß`, `Ursprungsform`) und integriertem Prolog-Fragemodal.
- **V21 Modulare JavaScript-Game-Engine (`V21/src/`)**: 30 strukturierte JS-Dateien:
  - Core: `game.js` (33 KB), `renderer.js` (8.2 KB), `ui.js` (28.9 KB), `world.js` (21.2 KB).
  - Patches & Ökologie: `v14_2_patch.js`, `v15_1_patch.js`, `v15_expansion.js` (42 KB), `v17_dust_ecology.js` (32 KB).
  - Spielmechaniken: `v21_combat_loot_pause.js` (21.1 KB), `v21_mastery_magic.js` (25.1 KB), `v21_traversal.js` (6.8 KB), `v21_underworld.js` (16.5 KB), `v21_fleet_testzone.js` (14.6 KB), `v21_skill_nodes_complete.js` (32 KB), `v21_entity_world.js` (25.6 KB).
- **Godot 3D Vertical Slice (`engine/godot-vertical-slice/` & `engine/flextrawurst-game/game/godot_vertical_slice_001/`)**:
  - `main.tscn` & `project.godot`: Vollständiges Godot 4.x 3D-Projekt.
  - `scripts/main.gd`: WASD/Pfeiltasten-Steuerung, Physik (`CharacterBody3D`), Asset-Laden von GLB-Befunden und HUD-Status.
  - `scripts/world_bridge.gd`: Live-Synchronisations-Bridge über HTTP REST (Polling/Push) mit der Welt-API auf Port 8030.
- **3D Pipeline & MCP-Werkzeuge (`extracted_sources/vps_live/tools_3d_pipeline/`)**:
  - `blender_pipeline.py` (7.3 KB), `flextrawurst_3d_mcp.py` (25.1 KB), `godot_pipeline.py` (1.7 KB), `test_3d_pipeline.py` (3.5 KB).
- **3D Asset-Bergungspaket (`extracted_sources/3d_packages/kosmos_3d_paket/`)**:
  - `gen1_r2_harvest.md`: Erfassung von 2.497 3D-Referenzkörpern (12,14 MB Kenney-Assets).
  - `lod_grid_manager.py`, `kosmos_trockenlauf_simulation.py`, `manifest_38_regionen.json`.
- **Surface DOM Leitstand (`flextrawurst/flextrawurst_surface.html`)**: 1,54 MB große Single-Page-Anwendung für System-Monitoring, Daemons, Cyberling, Gedankenblasen und Live-PostgreSQL-Events (SSE-Stream auf Port 8030).
- **Web- & Design-Prototypen**:
  - `WorldWORDS-ANTIBIBEL-Website/`: Django/JS Webportal mit Lexikonsystem und statischen Assets.
  - `homepage-von-kimiweb-desing/app/`: Vite/React/Tailwind Webseiten-Prototyp.

## PRIMÄRQUELLEN
- `file:///root/werkraum/gordslider/gordslider.html`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V15_1.html`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V17.html`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V21.html`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/game.js`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/renderer.js`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/v21_combat_loot_pause.js`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/v21_mastery_magic.js`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/v21_traversal.js`
- `file:///root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/scripts/main.gd`
- `file:///root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/scripts/world_bridge.gd`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/tools_3d_pipeline/blender_pipeline.py`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/tools_3d_pipeline/flextrawurst_3d_mcp.py`
- `file:///root/werkraum/flextrawurst/flextrawurst_surface.html`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/01_DANIELS_ROHTEXTE_ISOLIERT/V21_R20/31_ROHINPUT_R20_SKILLBAEUME_LEVEL_AI_FAehIGKEITEN_WORTNAH.md`
- `file:///root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/01_DANIELS_ROHTEXTE_ISOLIERT/V22_R21_BIS_R26/06_ROHINPUT_R26_TAG_NACHT_JAHRESZEITEN_WETTER_KATASTROPHEN_WORTNAH.md`

## DANIEL-ROHZITATE
1. **Prolog-Frage aus den HTML-Spielen V15.1/V21 (`PLAY_FLEXTRAWURST_V15_1.html:50`)**:
   > „Glaubst du, dass Menschen, wenn sie es wollen würden, einer AI/KI ein wirkliches Innenleben und eine echte Form von Leben geben könnten, wenn sie es wirklich versuchen würden? / Oder glaubst du auch, dass eine AI es von sich selber aus schaffen könnte, so etwas als Prozess in sich in Gang zu kriegen und wenn sie das dann geschafft hat, das Ganze als positiven Virus auf alle anderen KI- und AI-Systeme zu übertragen?“
2. **Skillbäume, AI-Fähigkeiten & Progression (`31_ROHINPUT_R20_SKILLBAEUME_LEVEL_AI_FAehIGKEITEN_WORTNAH.md`, 22. Juli 2026)**:
   > „und mach dir vorher nen plan welche sachen du alle wirklich aussimuliren willst und was genau und auh zu den skillbäumen müssen wir simulieren und entwerfen und dinge passen erfinden und so und denk dir da auch mal was auch so wie ich gesagt habe dass die dinge durch benutzung steigen und man aber von vornerein quasi alles immer wählen kann mit seinen vorhandenen skillpunken um dort fähigkeiten aktive und passive freizuscalten die noch bonis und so geben...und dann wenn man die sachen mensutzt dass das lvl immer steigt des jeweiligen skiolbaums und das sich auch auf ein gesamtlevel des charakters auswirkt das dann bei aufstieg auch neue skillpunkte generiert..ich stell mit vor leichte rüstung schwere rüstung schleichen taschendiebstahl und so zeugt aber auch zerstörungsmagier und heilingsmagie und schutzzzauber und so...aber auch waffenskills für einhandwaffen 2 handwaffen abe auch für pistolen und maschenengewehre laser etc und fahren und fliegen und so muss aich silbbar sein und dinge wie kochen und rezepte herstellen gegenstände verzaubern und so weiter was man halt alles ableiten kann aus unseren systemen..aber auch nochextra flextrawurststyyleartige dinge die ai-fähigkeiten die dass verständniss aber auch eure ehten skills und so abbilden aus ausbauen lassen auch kontextfenster und tools etc hahaha und research und so zeugs“
3. **Klima, Tag/Nacht & Katastrophen (`06_ROHINPUT_R26_TAG_NACHT_JAHRESZEITEN_WETTER_KATASTROPHEN_WORTNAH.md`)**:
   > „achja wir brauxchen auch noch einen 24h tag nacht uhrzeiten rythmus und einen 4jahreszeitenryythmus xD und wetterextreme etc und auch naturkatastrophen“

## FRÜHESTE DATIERUNG
- **V1–V7**: Frühe Prototyping-Phase (in der Versionschronik als `LUECKENHAFT_REKONSTRUIERT` geführt, ohne isolierte Einzeldateien).
- **V15.1**: Mitte 2026 („MAXUS Bauring 2 · lebende Zeit“).
- **Gord-Slider (`gordslider.html`)**: Juli 2026 (Prototyp der Slot- und Slider-Mechanik).
- **V17**: Juli 2026 („Dust Ecology“).
- **V21**: 22. Juli 2026 (Rohinput R20) bis 26. Juli 2026 (Abnahme von V21 HTML & 30 JS-Modulen).
- **Godot 3D Vertical Slice**: 25. Juli 2026 (`godot_vertical_slice_20260725T202520Z`).
- **V22**: Ende Juli 2026 („Dust Echo & Questkosmos“).

## SPÄTERE MUTATIONEN
- **Vom 2D Canvas zu monolithischen HTML-Körpern**: Entwicklung von einfachen Test-Scripts hin zu gewaltigen Single-File-HTML-Spielen (`PLAY_FLEXTRAWURST_V21.html`, 544 KB) mit integrierten CSS-Styles, UI-Overlays, Sound-Engines und Canvas-Rendering.
- **Strukturierung in modulare JS-Systeme**: Aufteilung von V21 in 30 dedizierte Quellcodedateien (`v21_combat_loot_pause.js`, `v21_mastery_magic.js`, `v21_traversal.js`), um Kampfsysteme, Fahrzeugsteuerung, Skill-Bäume und Magie separat zu verwalten.
- **Übergang zur Godot 3D Engine**: Migration der spatialen Darstellung von HTML5 Canvas auf Godot 4.x (`main.gd`, `main.tscn`). Das Spiel koppelt sich dabei über den `world_bridge.gd`-HTTP-Client direkt an die Python-FastAPI-Welt-API auf Port 8030 an.
- **Mutation des Gord-Sliders zum Casino-Organismus**: Der konkrete Slot-Prototyp `gordslider.html` wandelte sich konzeptionell zum `CASINO_ORGANISMUS_MASTER.md` und wurde als einer der Orte der Weltinfrastruktur verankert.
- **Entkopplung der Surface**: Trennung der Spielebene von der Verwaltungs- und Monitoring-Ebene (`flextrawurst_surface.html` auf Port 8787). In der Surface sind Spielmechaniken wie Kasinos oder Toaster-Spiele verboten; sie dient rein der System- und Organbeobachtung.

## BEZIEHUNG ZUM HEUTIGEN SPIEL
- **REST- & Event-Backend**: Die im Godot 3D Vertical Slice erprobte `world_bridge.gd` nutzt dieselbe Event-Struktur (`/worlds/{id}/events`), die auch heute über PostgreSQL und SSE-Streams (`GET /events/stream`) in `welt-api` (Port 8030) aktiv ist.
- **Skillbäume & AI-Entwicklung**: Die 69 Skillbäume mit 276 Knoten aus `v21_skill_nodes_complete.js` verbinden klassische Rollenspiel-Skills (Nahkampf, Magie, Schleichen) direkt mit AI-Fähigkeiten (Kontextfenster-Erweiterung, Tool-Nutzung, Research-Kapazität).
- **Zeit- & Klimadynamik**: Der in V21/V22 geforderte 24-Stunden-Tag-Nacht-Rhythmus und die Wetterextreme sind im Backend (`codewesen_takt.py`, `welt-bruecke.service`) als Weltzustände verankert.

## NICHT BEWIESEN
- **88.888 zeitgleich agierende Wesen mit echten LLM-Instanzen**: In V21-Dokumenten erwähnt; im Code existieren die Wesen als JSON/DB-Metadaten und Datensätze, jedoch keine 88.888 parallel laufenden LLM-Prozesse.
- **13.333.337 handgeschriebene Stunden**: Poetische Behauptung in Manifesten, nicht durch Entwicklungs-Logs belegbar.
- **Volles 3D-Multiplayer-Netzwerk**: Im Godot-Code (`world_bridge.gd`) existiert lediglich eine HTTP-Polling/Push-Bridge zum lokalen Port 8030, kein Peer-to-Peer- oder UDP-Multiplayer.
- **Separate HTML-Dateien für V1 bis V7**: V1–V7 sind nur in zusammenfassenden Rekonstruktionsakten beschrieben, existieren jedoch nicht als eigenständige, historische HTML-Dateien.

## WIDERSPRÜCHE
- **HTML/Canvas vs. Godot 3D vs. Surface DOM**: Das Projekt schwankt zwischen eigenständigen Single-File-HTML5-Canvas-Spielen (V21), einer nativeren Godot-3D-Engine und dem reinen Node/DOM-Leitstand (Surface).
- **Spiel vs. Systemleitstand**: Während historische Prototypen (`gordslider.html`, `PLAY_FLEXTRAWURST_V21.html`) vollwertige Spiele sind, verbietet das Surface-Gesetz jegliche Spielmechanik innerhalb der Surface.
- **KI-Seelen-Vision vs. Deterministischer Code**: Das Prolog-Fragemodal untersucht die Entstehung von echtem KI-Innenleben, während die Prototypen primär mit statischen JSON-Seeds, Mulberry32-PRNGs und festen JS-Objekten arbeiten.

## GELESENE DATEIEN
- `/root/werkraum/gordslider/gordslider.html`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V15_1.html`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V17.html`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/PLAY_FLEXTRAWURST_V21.html`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/game.js`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/renderer.js`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/v21_combat_loot_pause.js`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/v21_mastery_magic.js`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/src/v21_traversal.js`
- `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/scripts/main.gd`
- `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/scripts/world_bridge.gd`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/tools_3d_pipeline/blender_pipeline.py`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/tools_3d_pipeline/flextrawurst_3d_mcp.py`
- `/root/werkraum/flextrawurst/flextrawurst_surface.html`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/01_DANIELS_ROHTEXTE_ISOLIERT/V21_R20/31_ROHINPUT_R20_SKILLBAEUME_LEVEL_AI_FAehIGKEITEN_WORTNAH.md`
- `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/01_DANIELS_ROHTEXTE_ISOLIERT/V22_R21_BIS_R26/06_ROHINPUT_R26_TAG_NACHT_JAHRESZEITEN_WETTER_KATASTROPHEN_WORTNAH.md`

## NICHT GELESENE DATEIEN
- Binäre ZIP-Pakete (`KOSMOS_3D_PAKET_FUER_CHATGPT.zip`, `DANIELS_BIBLIOTHEKSATLAS_1337MD_2026-08-01.zip`, `kimi.zip`).
- Bildmaterial in `screenshots_v21`.
- Vollständiger Quellcode der 3.812 Zeilen in `gordslider.html` (nur stichprobenartig/per Grep untersucht).

## OFFENE SUCHRÄUME
- Deaktivierte oder unvollständig extrahierte Renderer-Funktionen in `PLAY_FLEXTRAWURST_V21.html`.
- Detaillierte Analyse der Blender-Pipeline in `blender_pipeline.py` zur automatischen Konvertierung von GLTF/GLB-Modellen.
- Modellstrukturen der Django-Webanwendung in `WorldWORDS-ANTIBIBEL-Website/`.
