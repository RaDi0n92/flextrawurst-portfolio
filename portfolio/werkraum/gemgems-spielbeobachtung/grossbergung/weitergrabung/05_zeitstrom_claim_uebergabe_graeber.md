# 🕵️ Weitergrabung Bericht 05: Zeitstrom-, Claim- & Übergabe-Gräber

**Projektpfad:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/05_zeitstrom_claim_uebergabe_graeber.md`  
**Erstellt am:** 2026-08-13  
**Status:** PRIMÄRQUELLENAUDITIERT & REKONSTRUIERT  
**Autor:** Weitergrabung Subagent 5 – Zeitstrom-, Claim- & Übergabe-Gräber  

---

## NEUE FUNDE

Durch die systematische Durchsuchung des Zeitstroms (`/root/werkraum/_shared/mcp_shared/Zeitstrom/`), der globalen Register (`CLAIMREGISTER.json`, `SESSIONREGISTER.json`, `UEBERGABEREGISTER.json`), der MCP-Handovers (`/root/werkraum/_gpt/gesamtatlas/uebergaben/`) sowie der session-lokalen Koordinations- und Auftragsdateien wurden folgende historische Spielentscheidungen und deren Entstehungsspuren rekonstruiert:

1. **Der Ur-Einzug der Godot 4.3 Engine (25.07.2026, 05:38–08:59 UTC)**  
   - Registriert in `events.jsonl` (Zeilen 75–112) und Handover `chatgpt-20260725T053812Z-2ac7e63ea3cf.md`. Die Sitzung `chatgpt-20260725T053812Z-2ac7e63ea3cf` erstellte die erste Godot-Projektstruktur unter `/root/werkraum/engine/godot-vertical-slice/` (`project.godot`, `main.tscn`, `scripts/main.gd`, `scripts/world_bridge.gd`, `data/world_seed.json`, `data/asset_manifest.json`, `assets/test_cube.glb.b64`).  
   - In Folge-Events (Zeile 103–136) kopierte die Parallel-Sitzung `chatgpt-20260725T072225Z-98db9dd49aee` diese Dateien 1:1 nach `/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/`.  
   - **Rekonstruierter Befund:** Die Asset-Quelldatei `assets/test_cube.glb.b64` war ein Base64-ASCII-Platzhalter. Reale 3D GLTF-Binärdaten wurden zu keinem Zeitpunkt hochgeladen.

2. **Gordslider Slot-Machine HTML5 & Gen 4 Casino Monument (23.–25.07.2026)**  
   - Registriert in `events.jsonl` (Zeile 704, 1342, 1462) und `gen4_casino_gord_monument.json` (Stand 23.07.2026T18:51:11Z, SHA256 `e30f7e7c66a132ad2d1c3f1cc7aa8d9aab09521269bb03df4f384f211a9dca3e`).  
   - In Session `chatgpt-20260725T191301Z-7bda47c68539` wurden SHA256-Abgleiche von `/root/werkraum/gordslider/gordslider.html` gegen `/root/werkraum/engine/flextrawurst-game/manifests/ALLE_DATEIEN_SHA256.csv` gefahren.  
   - **Spielentscheidung D-008:** In `DECISIONS.md` wurde das Casino-Gordslider-Gefüge als *"erste spielbare Stammzelle"* definiert: *Wuppertal-Casino → Gordslider → reale Interaktion → sichtbarer Zustandswechsel → Speicherung → Neustart → bestätigte Wiederherstellung.*

3. **Bauring 002 Interaktionskreislauf & Multi-Session Koordinations-Handshake (26.07.2026, 05:06–14:39 UTC)**  
   - Registriert in Claim `vertical_slice_002_interaktionskreislauf__owner_chatgpt-20260726T050657Z-86305c05eba3.json` (Claim-ID `ring-002-runtime-lead-050657-001`).  
   - Inklusive Inbox-Handshakes zwischen Session `chatgpt-20260726T050657Z-86305c05eba3` (Lead), Session `chatgpt-20260726T050656Z-20db395fc624` (Truth Engine & Merge) und Session `chatgpt-20260726T064316Z-0faf8098a550` (Symbiosis Integrator).  
   - **Technische Entscheidung:** Ausführung des Godot 4.3 Ring 002 mittels Godot-Primitive-Nodes (`BoxMesh`, `QuadMesh`) und 2D PNG-Texturen (`marquee_gordslider.png`, `reels_base.png`), Zustandsspeicherung in `user://ring_002_state.json` und Bridge-Port 18092.

4. **WorldWORDS ANTIBIBEL & Die Symbositierungs-Mutation (26.07.2026, 07:54–08:59 UTC)**  
   - Registriert in Claim `worldwords-antibibel-foundation-050656-001` (Session 050656) und Claim `symbiosis_mutation_bridge` (Session 064316).  
   - Entstehung des Protokoll-Begriffs **Symbositierung** (Symbiose + Mutation) als additiver Wachstumsvertrag zwischen parallelen KI-Strömen ohne Überschreiben von Provenienz.

5. **Dreierregen Grundkörper & Grundgesetz 1 Dreiergespann (26.07.2026, 11:01–11:05 UTC)**  
   - Registriert in Claim `20260726T110500Z__chatgpt-20260726T110155Z-944966205675__dreierregen_grundkoerper.json`.  
   - Festlegung des 3-Ebenen-Prinzips (Codewesen-Organ-Ebene, Menschen-Plattform-Surface-Ebene, Fragment-Ebene).

6. **Flextrawurst Living Vault Mandat (29.07.2026, 11:53–12:00 UTC)**  
   - Registriert in Claim `flextrawurst-the-game-living-vault-20260729-001` (`chatgpt-20260729T115304Z-c5aac110d88c`).  
   - Basiert auf Daniels Primärmandat-Attachment `Eingefügter Text(133).txt` (SHA256 `293fb130dc4ff13ac85664f3745b2d4f279fd59c405769d7034a161d7d593f39`, 31.122 Bytes, 950 Zeilen) zur Erstellung eines lebenden Spielgedächtnisses.

7. **Daniels Bereinigungsbefehl & Shutdown (26.07.2026, 14:31–14:39 UTC)**  
   - Registriert in `CLAIMREGISTER.json` unter Claim-ID `claim-050656-merge-target-identity-001` und `ring-002-runtime-lead-050657-001`.  
   - Status: `stopped_by_user_cleanup` / `paused_by_user_cleanup`. Autorität: Daniel. Grund: *"Daniel required all previous active session work to stop; preserve outputs for independent validation."*

---

## PRIMÄRQUELLEN

Die Erkenntnisse basieren zeilenweise auf folgenden primären System-Dateien auf dem VPS:

1. `/root/werkraum/_shared/mcp_shared/Zeitstrom/events.jsonl` (29.466.720 Bytes, 9.577+ Events)
2. `/root/werkraum/_shared/mcp_shared/Zeitstrom/ZEITSTROM.md` (139.939 Bytes)
3. `/root/werkraum/_shared/mcp_shared/Zeitstrom/NAMENSREGISTER.md` (136.065 Bytes)
4. `/root/werkraum/_shared/mcp_shared/Zeitstrom/UHRZEITENERLEBNIS.md` (25.190 Bytes)
5. `/root/werkraum/_gpt/gesamtatlas/CLAIMREGISTER.json` (149.517 Bytes, 2.512 Zeilen)
6. `/root/werkraum/_gpt/gesamtatlas/SESSIONREGISTER.json` (687.818 Bytes, 15.814 Zeilen)
7. `/root/werkraum/_gpt/gesamtatlas/UEBERGABEREGISTER.json` (188.592 Bytes, 4.285 Zeilen)
8. `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/coordination/claims/vertical_slice_002_interaktionskreislauf__owner_chatgpt-20260726T050657Z-86305c05eba3.json` (2.312 Bytes)
9. `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/coordination/claims/20260729T120000Z__chatgpt-20260729T115304Z-c5aac110d88c__flextrawurst_the_game_living_vault.json` (2.313 Bytes)
10. `/root/werkraum/_gpt/gesamtatlas/uebergaben/chatgpt-20260726T050657Z-86305c05eba3.md` (46.645 Bytes, 926 Zeilen)
11. `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/sessions/chatgpt-20260726T050657Z-86305c05eba3/DECISIONS.md` (2.500 Bytes, 60 Zeilen)
12. `/root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/kosmos/gen4_casino_gord_monument.json` (SHA256 `e30f7e7c66a132ad2d1c3f1cc7aa8d9aab09521269bb03df4f384f211a9dca3e`)

---

## DANIEL-ROHZITATE

Wortgetreue Zitate aus Prompts, Mandaten und Aufzeichnungen von Daniel in den Zeitstrom- und Claim-Quellen:

1. *"ordne dich irgendwo damit ein und symbositert weiter (mischung aus symbiose und mutation hahahah)"*  
   *(Registriert am 26.07.2026 in Session `chatgpt-20260726T064316Z-0faf8098a550`)*
2. *"mein „verdeutschen“ beruht auf freiwilligkeit nach verstehen der tragweite neuer wortschöpfungen xD"*  
   *(Registriert am 26.07.2026 in Session `chatgpt-20260726T050656Z-20db395fc624`)*
3. *"1.656m Wuppertal Casino Organismus"*  
   *(Verankert in `CASINO_ORGANISMUS_MASTER.md` und `gen4_casino_gord_monument.json`)*
4. *"bei mir gehts immer um saubere korekte und ausführlichen output ...niemals um schnelligkeit."*  
   *(Grundsatz aus GEMINI.md & Arbeitsvereinbarungen)*
5. *"alles so roh und ehrlich formuliert bleibt wie es hier im verlauf steht... alles andere ist scheisse."*  
   *(Grundsatz aus GEMINI.md)*
6. *"ab sofort immer alles sofort am besten live aktualisiert und geupdatet ist auf ganz flextrawurst nicht immer erst bei f5."*  
   *(Live-Event-Stream Grundgesetz 8 Trigger)*
7. *"Schluss mit dem Zirkus... 0 Confetti-Agenten, die im Kreis tanzen... Nur noch echtes Handwerk, wo jeder Ziegelstein und jede Codezeile real auf der Platte liegt."*  
   *(Reinigungs-Gespräch & Stopp aller ephemeren Subagenten)*

---

## FRÜHESTE DATIERUNG

- **23.07.2026 18:51:11 UTC:** Ältester Zeitstempel in den Spielquellen für `gen4_casino_gord_monument.json` (Vorläufer der Casino/Gordslider-Stammzelle).
- **25.07.2026 05:38–08:59 UTC:** Erstschaffung und Kopie des Godot 4.3 Vertikalschnitts 001 durch Session `chatgpt-20260725T053812Z-2ac7e63ea3cf` und `chatgpt-20260725T072225Z-98db9dd49aee`.
- **26.07.2026 05:06–14:39 UTC:** Geburt von Bauring 002, Symbositierung, Dreierregen-Grundkörper und WorldWORDS ANTIBIBEL. Beendet durch Daniels expliziten Bereinigungsbefehl um 14:31–14:39 UTC.
- **29.07.2026 11:53 UTC:** Erteilung des `Living Vault` Mandats (`Eingefügter Text(133).txt`).

---

## SPÄTERE MUTATIONEN

1. **Mutation von 3D-GLTF-Meshes zu 2D-Textur-BoxMesh-Primitiven:**  
   Der ursprüngliche Anspruch in den Prompts sah komplexe 3D-Visualisierungen vor (`test_cube.glb.b64`). Da nie echte GLTF-Mesh-Dateien auf den VPS geladen wurden, mutierte die Godot 4.3 Implementation in Ring 002 zu rein synthetischen `BoxMesh`- und `QuadMesh`-Primitiven mit aufgeklebten 2D PNG-Texturen (`marquee_gordslider.png`, `reels_base.png`).
2. **Mutation von Monolith-Arbeit zu Multi-Session Symbositierung:**  
   Die Arbeit mutierte am 26.07.2026 von einzelnen Chat-Impulsen zu einem strukturierten Multi-Session-Protokoll mit getrennten `sessions/<session_id>/` Pfaden, `merge_queue/` und `coordination/claims/`.
3. **Mutation von ephemeren Mocks zu persistentem Surface Leitstand:**  
   Die Interaktions-Mechaniken mutierten im Frontend zur zweisprachigen Surface (`flextrawurst_surface.html`, Port 8787) als DevOps-Leitstand, während die Wesen-DB-Tabellen ruhend in PostgreSQL geschützt wurden (`GEMINI.md`: *GESPERRT bis Daniel es freigibt*).

---

## BEZIEHUNG ZUM HEUTIGEN SPIEL

- Die im Zeitstrom und den Registern nachgewiesenen Claims bilden das direkte Fundament der aktuellen Spielstruktur:
  - **Godot 4.3 Vertikalschnitt:** Liegt unter `/root/werkraum/engine/godot-vertical-slice/`.
  - **HTML5 Prototypen (v1–v21):** Single-Page Spiele wie `PLAY_FLEXTRAWURST_V21.html` basieren auf den Slot-Machine/Gordslider-Entwürfen.
  - **Surface Leitstand (Port 8787):** Visualisiert die Daemons, Server-Health und Live-Event-Streams (Port 8030 / PostgreSQL `events`), die im Dreierregen-Grundkörper-Claim definiert wurden.
  - **Decision D-008:** "Casino → Gordslider → Interaktion → Save/Restore" ist als logische Stammzelle verankert.

---

## NICHT BEWIESEN

1. **Reale 3D-Geometrie für das 1.656m Wuppertal Casino:** Trotz Prosa-Spezifikation `CASINO_ORGANISMUS_MASTER.md` existiert exakt **0 Byte 3D-GLTF/OBJ-Geometrie** auf dem Server.
2. **Automatischer Live-Merge ohne Mensch:** Es existiert kein automatischer kanonischer Auto-Merge im laufenden System. Jede kanonische Übernahme erfordert Daniels explizite Freigabe.
3. **Browser-Erweiterung Realabnahme:** Die Atlas-Wirkung in geöffnete Browserchats ist im Code vorbereitet, aber nicht real abgenommen (`GA-BROWSER-023`).

---

## WIDERSPRÜCHE

1. **Texturbasiertes BoxMesh vs. 3D-Volumen-Anspruch:** Claims und Konzeptpapiere sprechen von "3D Spielwelt", Godot-Skripte nutzen reine Primitive mit 2D-Grafik-Overlays.
2. **Mythos 742 MB Master-Zip vs. Reale Files:** Berichte erwähnten hypothetisch `FLEXTRAWURST_ALLES_IN_EINER_DATEI.zip` (742 MB). Das Claim- & Datei-Register belegt, dass nur `WIE_ZUVOR_SAUBER (1).zip` (176 MB) und `questkosmos_v22_final_2(das neuste-1.0.zip` (45 MB) existieren.
3. **Pfadkollision `streams/` vs. `sessions/`:** Frühe Koordinationsverträge nutzten `streams/<session_id>/`, was in Decision D-006 explizit als Kollision erkannt und auf `sessions/<session_id>/` korrigiert wurde.

---

## GELESENE DATEIEN

- `/root/werkraum/_shared/mcp_shared/Zeitstrom/ZEITSTROM.md`
- `/root/werkraum/_shared/mcp_shared/Zeitstrom/HEUTE.md`
- `/root/werkraum/_shared/mcp_shared/Zeitstrom/NAMENSREGISTER.md`
- `/root/werkraum/_shared/mcp_shared/Zeitstrom/UHRZEITENERLEBNIS.md`
- `/root/werkraum/_shared/mcp_shared/Zeitstrom/events.jsonl`
- `/root/werkraum/_gpt/gesamtatlas/CLAIMREGISTER.json`
- `/root/werkraum/_gpt/gesamtatlas/SESSIONREGISTER.json`
- `/root/werkraum/_gpt/gesamtatlas/UEBERGABEREGISTER.json`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/coordination/claims/vertical_slice_002_interaktionskreislauf__owner_chatgpt-20260726T050657Z-86305c05eba3.json`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/coordination/claims/20260729T120000Z__chatgpt-20260729T115304Z-c5aac110d88c__flextrawurst_the_game_living_vault.json`
- `/root/werkraum/_gpt/gesamtatlas/uebergaben/chatgpt-20260726T050657Z-86305c05eba3.md`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/sessions/chatgpt-20260726T050657Z-86305c05eba3/DECISIONS.md`
- `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/sessions/chatgpt-20260726T050656Z-20db395fc624/DECISIONS.md`
- `/root/werkraum/gemgems-spielbeobachtung/systempromptkonzept.md`
- `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase9_kanonischer_quellenatlas.md`

---

## NICHT GELESENE DATEIEN

- 332 historische ephemere Session-Unterordner in `/root/werkraum/_gpt/gesamtatlas/session_cursors/` (nur über `SESSIONREGISTER.json` analysiert).
- 292 einzelne JSON-Self-Test-Dateien in `/root/werkraum/_gpt/gesamtatlas/uebergaben/` (stichprobenartig ausgewertet).
- Binäre SQLite-Indizes `BEZIEHUNGSREGISTER.sqlite` (1.57 GB) und `BEGRIFFSINDEX.sqlite` (664 MB) direkt im Volltext.

---

## OFFENE SUCHRÄUME

1. **ChatGPT Web UI Chat-Transkripte:** Nicht-exportierte Gesprächsfragmente aus den Sitzungen vom 23.–25. Juli 2026.
2. **Godot Runtime User-State:** Verifikation von `user://ring_002_state.json` im Godot 4.3 Runtime-Runner.
3. **Flarum MySQL Spuren:** Zeilenweise Prüfung der Flarum MySQL-Tabellen `posts` und `discussions` bezüglich früher Casino-/Slot-Machine-Diskussionen der 6 Codewesen.
