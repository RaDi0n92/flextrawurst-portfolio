# CT-Scan 17: Godot-Provenienz & Session-Analyse (`godot_vertical_slice_001`)

**Erstellungsdatum:** 13.08.2026  
**Status:** Präzisiert & Belegt (Session-Rohtext, Git- & Port-Analyse)  
**Zielpfad für Speicherung:** `/root/werkraum/gemgems-spielbeobachtung/spiel/17_ct_scan_godot_provenienz_und_session_analyse.md`

---

## Executive Summary & Kernbefunde

| Frage | Exakte Antwort & Beleg |
| :--- | :--- |
| **1. Erster Auftritt (Wann, Autor, Erzeuger)?** | **25. Juli 2026, 08:21:50 UTC (10:21:50 CEST)**. Session `chatgpt-20260725T081538Z-00b7a2e74c94`. <br>**Git-Autor (tatsächlicher VPS-Commit):** `Daniel <daniel@local>`. <br>**Code-Erzeuger laut Session:** `GPT-5.6-sol-hoch` (ChatGPT) im Auftrag von Daniel (`RaDi0n92`). |
| **2. Daniel-Originalton vs. Spätere Paraphrase?** | **Daniel-Rohtext (25.07.2026):** *"gibts nix was ich nutzen kann unm ne echte gameengine zusammen an gpt zu kleben oder so... wichtig es muz zu catgpt wandern"* und *"we do that mthfker"*. <br>**Spätere ChatGPT-Paraphrase:** *"Kann man eine echte Game-Engine überhaupt an ChatGPT kleben?"*. |
| **3. Initialer Impuls vs. Spätere Architektur-Gründe?** | **Initialer Impuls:** Daniel reichte die reine Single-HTML-Perspektive nicht mehr aus; er wollte eine echte Game-Engine an ChatGPT ankoppeln. <br>**Spätere Architektur-Begründung:** Performance-Grenzen von Canvas 2D bei großen 3D-Räumen (1.656m Casino), schwache Laptops/Android und Headless-Linux-CI. |
| **4. GDScript vs. C++ Engine Unterscheidung?** | Der Projektcode von `godot_vertical_slice_001` wurde in **GDScript** geschrieben (`scripts/main.gd`, `scripts/world_bridge.gd`). Die unterliegende Godot-Engine 4.3 selbst ist in **C++** implementiert. |
| **5. Ausgangskörper v21 oder neuer Prototyp?** | **Eigenständiger neuer Nativer Engine-Prototyp (`slice_001`)**. Keinesfalls eine Codeportierung von v21. v21 war eine Canvas-2D Software-3D JavaScript-Engine und wurde als historisches Archiv gerettet. Godot entstand neu. |
| **6. Entstehung von Port 18092 (Kollision 8090/8091)?** | **Strikter Schutz von 8090 & 8091**. Port 8090 war belegt durch `flextrawurst-3d-mcp.service` (Blender Headless MCP) und 8091 durch frühe MCP-Dienste. High-Port **18092** wurde gewählt für `flextrawurst-godot-world-bridge.service` (`127.0.0.1:18092`). |

---

## 1. Erstes Auftauchen in Session-Notizen & Git-Commits

### 📅 Datierung & Originalton
- **Erst-Erstellung:** **25. Juli 2026, 08:15:38Z – 08:21:50Z UTC** (10:15:38 – 10:21:50 CEST).
- **Session-ID:** `chatgpt-20260725T081538Z-00b7a2e74c94`
- **Beleg-Dateien im Zeitstrom:**
  - `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/Zeitstrom/ereignisse/003c9068-1338-4f4b-9b34-b8106918980b.md`
  - Transkript-Archiv: `_gpt/ui_visible_conversations/alt/2026-08-02__REALSTATUS-Der-VPS-Einzugskörper-ist-fertig.../1zu1.md`
- **Daniels echter Rohtext aus der Session:**
  > *"gibts nix was ich nutzen kann unm ne echte gameengine zusammen an gpt zu kleben oder so... wichtig es muz zu catgpt wandern"*  
  > *"we do that mthfker"*

---

## 2. Git-Provenienz & Commit-Kette

- **Repository:** `RaDi0n92/flextrawurst-agent` (ursprünglich fälschlich in `RaDi0n92/Flextrawurst` angelegt und sofort korrigiert).
- **Branch:** `engine/godot-vertical-slice-001` (Draft PR #3).
- **Erster Dateierzeugungs-Commit (`asset_manifest.json`):** `2d38ec91d5e5ccfd90bdf108f11d8bd815ebb974`.
  - **Zeit-Anomalie (Provenienz-Kollision):** Das Git-Metadatum dieses Commits zeigt **07:30:05 UTC** (09:30:05 CEST). Der unabhängige MCP-Zeitstrom protokolliert den tatsächlichen `vps.write_file`-Vorgang für das Manifest jedoch um **08:21:50 UTC** (10:21:50 CEST) und bindet exakt diesen Commit-Hash (`git_commit: 2d38ec91...`) an das Event. Die Ursache dieser Abweichung von 51 Minuten ist ungeklärt. Der Zeitstrom gilt als direkter Ereignisbeleg für den Schreibvorgang; das Git-Datum bleibt als abweichende Metadatenzeit erhalten. Dieser Commit erzeugte **ausschließlich** `data/asset_manifest.json`.
- **Zweiter Rettungs-Commit (GDScript & Projektdatei):** `4255bd590e1550a0c72b7a451c701e360df5ab59` (25.07.2026, 14:06:55 UTC) – Dieser Backup-Commit ist die erste nachvollziehbare physische Git-Spur für `project.godot`, `main.tscn`, `scripts/main.gd`, `scripts/world_bridge.gd`.
- **Attributions-Trennung:** Der **Git-Autor** der Commits lautet auf `Daniel <daniel@local>`. Die logische Erstellung (Gesprächsprovenienz) geht auf die ChatGPT-Session zurück.

---

## 3. Verhältnis zu v21: Ausgangskörper oder Eigenständigkeit?

**Godot entstand als eigenständiger, neuer nativer Engine-Prototyp (`godot_vertical_slice_001` / Ring 001) und NICHT als Code-Portierung von v21.**

- **v21:** War ein reines HTML5 JavaScript-System auf Canvas 2D (`V21/src/renderer.js`). Es wurde als **v21-Historien-Archiv** unter `/root/werkraum/engine/flextrawurst-game/extracted_sources/` gerettet.
- **Godot `slice_001`:** Entstand von Grund auf neu in GDScript (`main.gd`) für die Godot-C++-Runtime mit `CharacterBody3D` (WASD/Pfeile, `move_and_slide()`), GLB-Loader (`test_cube.glb`) und eigener HTTP-Bridge.

---

## 4. Port-Entscheidung 18092

- **Port 8090:** Belegt durch `flextrawurst-3d-mcp.service` (Blender 4.0.2 Headless MCP Server).
- **Port 8091:** In frühen Entwürfen als MCP-Testport skizziert.
- **Port 18092:** Gewählt zur Vermeidung von Kollisionen mit bestehenden VPS-Diensten. Active Override in `data/world_seed.runtime.json` (`base_url: http://127.0.0.1:18092`, `sync_interval_seconds: 1.0`).
