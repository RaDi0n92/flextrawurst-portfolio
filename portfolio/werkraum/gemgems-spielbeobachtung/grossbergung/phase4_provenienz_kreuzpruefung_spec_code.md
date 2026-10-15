# Phase 4 – Provenienz-Kreuzprüfung (Spec, Code, 1337 Loops & Engine)

**Prüfer:** Phase 4 – Provenienz-Kreuzprüfer 1 (Spec, Code, 1337 Loops & Engine)  
**Datum:** 2026-08-13  
**Prüfbasis:** Primärquellen auf der VPS-Festplatte (`/root/werkraum/`)  
**Ziel-Berichtsdatei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/phase4_provenienz_kreuzpruefung_spec_code.md`

---

## Executive Summary / Synthese-Ergebnis

| Claim | Geprüfte Primärdateien | Ergebnis | Exakter Datei-Beweis / Befund |
|---|---|---|---|
| **1. 1.337 Loops Claim** | `LOOP_BEWEISE.jsonl`<br>`MANIFEST.json`<br>`GESAMTBESCHREIBUNG.md` | **Statische Hashes / Synthetische Kette** | `rag_a_sha256`, `rag_b_sha256` und `synthesis_sha256` sind über alle 1.337 Zeilen identisch. Zwischenversionen (Loops 1–1336) existieren nicht auf Disk (`readable_intermediates: 0`). Loop 1337 matcht `GESAMTBESCHREIBUNG.md` exakt. |
| **2. Gate 03 & 12 Mockup Claim** | `test_gate_03_mastery_magic.py`<br>`test_gate_12_experience_lab.py`<br>`GATE_03_RESULT.json`<br>`GATE_12_RESULT.json` | **In-Memory DOM/JS-Mockup** | Keine GPU/WebGL-Abfrage, sondern Evaluierung von JS-Arrays (`FW_GAME.renderer.faces`). Vorlesung/Speicherung nutzt ein ephemeres JS-Objekt (`const m={}` in `init_script`). Keine DB-Persistenz. |
| **3. Casino Prosa vs. 3D Claim** | `CASINO_ORGANISMUS_MASTER.md`<br>Gesamtes VPS (`.glb`, `.gltf`, `.obj`, `.blend`) | **Reine Markdown-Spezifikation** | 0 3D-Meshes für das 1.656m Casino auf dem VPS vorhanden. Das Casino existiert ausschließlich als Prosatext (221 Zeilen Markdown). |
| **4. Ring 002 PNG-Overlay Claim** | `ring_002_interaktionskreislauf/`<br>`ring_002.tscn`<br>`FILE_LIST.txt` | **Ausschließlich PNG/JPG + Procedural Primitives** | 0 3D-Mesh-Dateien in Ring 002. Geometrie besteht aus Godot-Primitive-Nodes (`BoxMesh`, `QuadMesh`, `CylinderMesh`), belegt mit 2D-PNG-Overlay-Texturen. |

---

## 1. Detaillierte Prüfung: 1.337 Loops Claim

### 1.1 Primärquellen
- `LOOP_BEWEISE.jsonl`: `/root/werkraum/engine/flextrawurst-game/Versuch-einer-Gesamtbeschreibung/00_START_HIER/20_1337_LOOPS/PROOFS/LOOP_BEWEISE.jsonl` (1.338 Zeilen, 1.017.576 Bytes)
- `MANIFEST.json`: `/root/werkraum/engine/flextrawurst-game/Versuch-einer-Gesamtbeschreibung/00_START_HIER/20_1337_LOOPS/FINAL/MANIFEST.json` (54 Zeilen, 1.922 Bytes)
- `STATUS.json`: `/root/werkraum/engine/flextrawurst-game/Versuch-einer-Gesamtbeschreibung/00_START_HIER/20_1337_LOOPS/STATUS.json` (10 Zeilen, 499 Bytes)
- `GESAMTBESCHREIBUNG.md`: `/root/werkraum/engine/flextrawurst-game/Versuch-einer-Gesamtbeschreibung/00_START_HIER/20_1337_LOOPS/FINAL/GESAMTBESCHREIBUNG.md` (281.076 Bytes)
- `MIKRODETAILREGISTER.csv`: `/root/werkraum/engine/flextrawurst-game/Versuch-einer-Gesamtbeschreibung/00_START_HIER/20_1337_LOOPS/FINAL/MIKRODETAILREGISTER.csv` (681.346 Bytes)

### 1.2 Zeilenweise Hash-Analyse von `LOOP_BEWEISE.jsonl`
Prüfung der SHA256-Felder über alle 1.337 JSON-Einträge:
- `rag_a_sha256`: `726183df2ec6ad38b1ae1aa915cb3ff2c441c0e41db9d1d8bed55e5d1331ea11`  
  -> **Vollständig konstant** von Zeile 1 bis Zeile 1337. Dies ist der exakte SHA256-Hash der Datei `RAG_A_CHRONOLOGIE_PROVENIENZ.sqlite`.
- `rag_b_sha256`: `8906b6eecbd5e8b48320faf345e3ee0e7e88b60469997ccd608a49e40435a201`  
  -> **Vollständig konstant** von Zeile 1 bis Zeile 1337. Dies ist der exakte SHA256-Hash der Datei `RAG_B_BEDEUTUNGSGEWEBE.sqlite`.
- `synthesis_sha256`: `455fe9aceebb1755abc782f3e58f97ee47becdead565caae4bee1b2d5cc36e19`  
  -> **Vollständig konstant** von Zeile 1 bis Zeile 1337.

### 1.3 Vergleichende Befunde
1. **Hash-Kette (Draft-Chaining):** Was sich von Zeile zu Zeile ändert, ist `previous_draft_sha256` -> `draft_sha256`, `matrix_ideas_sha256` sowie der Zähler `unique_microthemes_selected` (+22 pro Loop bis 1.337).
2. **Intermediate Retention:** `STATUS.json` meldet `"readable_intermediates": 0` und `MANIFEST.json` meldet `"readable_intermediate_versions_retained": 0`. Es existieren **keinerlei physikalische Text-Dateien** für die Iterationen 1 bis 1336 auf der Festplatte.
3. **Kanonischer Abgleich:** Line 1337 in `LOOP_BEWEISE.jsonl` weist folgenden `draft_sha256` auf:  
   `"066e05129a914ea21b6cb7e168a0f815ea47da6b7568e5eaee16aa02c3421506"`  
   In `MANIFEST.json` ist `GESAMTBESCHREIBUNG.md` eingetragen mit SHA256 `066e05129a914ea21b6cb7e168a0f815ea47da6b7568e5eaee16aa02c3421506`. Die Hashes stimmen exakt überein.

**Befund 1:** Die RAG-Eingabehashes sind statische Konstanten. Die 1.337 Loops stellen eine deterministische Hash-Kette dar, aus der ausschließlich das Endergebnis (Loop 1337: `GESAMTBESCHREIBUNG.md`) als Textkörper auf der Platte aufbewahrt wurde.

---

## 2. Detaillierte Prüfung: Gate 03 & Gate 12 Mockup Claim

### 2.1 Primärquellen
Ordner: `/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/tests_v21/`
- `test_gate_03_mastery_magic.py` (5.223 Bytes, 55 Zeilen)
- `test_gate_12_experience_lab.py` (9.226 Bytes, 96 Zeilen)
- `GATE_03_RESULT.json` (5.540 Bytes, 64 Zeilen)
- `GATE_12_RESULT.json` (10.483 Bytes)

### 2.2 Abfrage-Mechanismus: DOM/JS-Arrays vs. GPU/WebGL
- **Playwright Browser-Setup:** In beiden Testskripten wird Chromium headless ohne GPU-Hardware-Kontext gestartet:
  `b = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])`
- **Render-Verifikation in `test_gate_03_mastery_magic.py` (Zeile 40):**
  `ck('Magieeffekt wird als Weltgeometrie gerendert', page.evaluate('FW_GAME.renderer.faces.some(f=>String(f.tag||"").startsWith("magic-"))'), str(page.evaluate('Array.from(new Set(FW_GAME.renderer.faces.map(f=>f.tag))).filter(x=>String(x).includes("magic"))')))`
- **Render-Verifikation in `test_gate_12_experience_lab.py` (Zeile 30–31):**
  `tags = page.evaluate('Array.from(new Set(FW_GAME.renderer.faces.map(f=>f.tag)))')`  
  `ck('Material-, Familien- und Systemkörper werden räumlich gerendert', all(x in tags for x in ['lab-material-sample','lab-family-sample','lab-system-ring']), ...)`
- **Befund GPU/WebGL:** Es werden keine WebGL-Shader, GPU-Kontexte, Draw-Calls oder Canvas-Pixel abgefragt. Die Prüfungen analysieren ausschließlich in JavaScript-Speicher-Arrays (`FW_GAME.renderer.faces`) liegende JS-Objekte im Browser-DOM.

### 2.3 Persistenz-Mechanismus: DB vs. Ephemeres In-Memory-Objekt
- **Storage-Mocking:** In Zeile 16 beider Skripte (`test_gate_03_mastery_magic.py` & `test_gate_12_experience_lab.py`) wird vor Seitenladen per Playwright `add_init_script` Folgendes ausgeführt:
  ```javascript
  (() => {
    const m = {};
    const s = {
      getItem: k => m[k] ?? null,
      setItem: (k, v) => m[k] = String(v),
      removeItem: k => delete m[k],
      clear: () => Object.keys(m).forEach(k => delete m[k])
    };
    Object.defineProperty(window, 'localStorage', { value: s, configurable: true });
  })();
  ```
- **Save/Load-Test (Zeile 46 in Gate 03, Zeile 81 in Gate 12):**  
  `page.evaluate('FW_GAME.save(); FW_GAME.state.mastery21.inventory=[]; FW_GAME.load("test")')`
- **Befund Persistenz:** `window.localStorage` wird durch das flüchtige JS-Objekt `m` ersetzt. Speichern und Laden liest/schreibt ausschließlich in das flüchtige JavaScript-RAM der aktuellen Playwright-Browserseite. Es existiert **keine Datenbank-Persistenz** (PostgreSQL / SQLite / REST-API-Backend).

---

## 3. Detaillierte Prüfung: Casino Prosa vs. 3D-Baukörper Claim

### 3.1 Primärquellen
- `CASINO_ORGANISMUS_MASTER.md`: `/root/werkraum/MCP-VPS-CHATGPT-Spiel-schritfürschritt-aufbau-3d-spieewelt-traum/CASINO_ORGANISMUS_MASTER.md` (12.322 Bytes, 221 Zeilen)
- Analysedokument: `/root/werkraum/CLAUDE-NEUGIRIGER-REPORT/03_casino_organismus_1656m.md` (6.904 Bytes)

### 3.2 Suche nach 3D-Meshes (.glb, .gltf, .obj, .blend)
- Exakte Prüfung der VPS-Dateibestände nach 3D-Format-Dateiendungen:
  - `.glb` Dateifund in `/root/werkraum/engine/godot-vertical-slice/assets/test_cube.glb` (1.476 Bytes) -> ein generischer 1-Meter Testwürfel.
  - **Zero 3D Mesh Dateifunde** (`.glb`, `.gltf`, `.obj`, `.blend`) für das 1.656m Casino auf dem gesamten VPS.

### 3.3 Befund
Der Casino-Organismus (1.656 Meter Höhe = doppelte Burj-Khalifa-Höhe, 44m -> 88m Durchmesser-Aufweitung, 20 Organkategorien inklusive Herz, Lungen, Nervensystem, Immunsystem) existiert **ausschließlich als prosaisches Markdown-Spezifikationsdokument** (`CASINO_ORGANISMUS_MASTER.md`). Es existieren keinerlei 3D-Baukörper oder Meshes für dieses Bauwerk auf der VPS-Festplatte.

---

## 4. Detaillierte Prüfung: Ring 002 PNG-Overlay Claim

### 4.1 Primärquellen
Verzeichnis: `/root/werkraum/engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/`
- Scene-Datei: `ring_002.tscn` (8.484 Bytes, 264 Zeilen)
- Asset-Protokolle: `assets/FILE_LIST.txt` (7.135 Bytes, 51 Eintragszeilen), `assets/SHA256SUMS.txt`
- Skripte: `scripts/casino_cell_builder.gd`, `scripts/gordslider_interactable.gd`, `scripts/ring_002_main.gd`

### 4.2 Asset-Analytik von `assets/FILE_LIST.txt`
100% aller Grafik- und Visual-Assets in `ring_002_interaktionskreislauf/assets/` sind 2D-Bilddateien (`.png`, `.jpg`) oder Textdateien (`.json`, `.html`, `.txt`):
- `derived/marquee_gordslider.png` (231.580 Bytes)
- `derived/ring_002_floor_medallion.png` (38.744 Bytes)
- `derived/gord_trinity_mural.png` (500.256 Bytes)
- `derived/casino_cascade_carpet.png` (78.614 Bytes)
- `derived/reels_base.png` (878.165 Bytes)
- `derived/reels_activated.png` (919.442 Bytes)
- Zahlreiche 140x180 JPG/PNG Slot-Symbole in `source/gordslider/bilder/...`

### 4.3 Geometrie-Analytik von `ring_002.tscn`
In `ring_002.tscn` wird die 3D-Welt ausschließlich über prozedurale Godot-Primitive-Mesh-Nodes aufgebaut:
- `BoxMesh_unit` (Zeile 38): `size = Vector3(1, 1, 1)`
- `QuadMesh_screen` (Zeile 41): `size = Vector2(2.68, 2.12)`
- `QuadMesh_marquee` (Zeile 44): `material = SubResource("Material_marquee")`, belegt mit PNG `marquee_gordslider.png`
- `CylinderMesh_button` (Zeile 48): `top_radius = 0.22, bottom_radius = 0.26, height = 0.18`
- `SphereMesh_beacon` (Zeile 55): `radius = 0.24, height = 0.48`
- `CapsuleMesh_player` (Zeile 61): `radius = 0.45, height = 1.8`

### 4.4 Befund
In Ring 002 existieren **keine 3D-Mesh-Dateien** (`.glb`, `.gltf`, `.obj`). Die 3D-Szene setzt sich exklusiv aus prozeduralen Godot-Standard-Mesh-Primitiven (`BoxMesh`, `QuadMesh`, `CylinderMesh`, `CapsuleMesh`) zusammen, auf die 2D-PNG/JPG-Grafiken als Texturen gelegt sind.

---

## Abschließendes Urteil des Provenienz-Kreuzprüfers

Sämtliche vier Claims wurden durch Zeilen- und Dateianalyse der Primärdateien auf der VPS-Festplatte verifiziert:
1. **1.337 Loops:** Statische RAG-Eingabe-Hashes; Zwischenschritte 1–1336 wurden gelöscht/nicht gerettet (`readable_intermediates: 0`). Loop 1337 ist identisch mit `GESAMTBESCHREIBUNG.md`.
2. **Gate 03 & 12 Tests:** Nutzen reine In-Memory-Array-Abfragen (`FW_GAME.renderer.faces`) und mocken `localStorage` über ein flüchtiges JS-Objekt (`const m={}`). Keine WebGL/GPU-Drawcalls, keine DB-Backend-Persistenz.
3. **1.656m Casino:** Pure Markdown-Prosa in `CASINO_ORGANISMUS_MASTER.md`. 0 3D-Modelldateien auf dem VPS.
4. **Ring 002:** Basiert zu 100% auf prozeduralen Godot-Primitive-Meshes mit PNG-Texturoverlays. 0 externe 3D-Meshes.
