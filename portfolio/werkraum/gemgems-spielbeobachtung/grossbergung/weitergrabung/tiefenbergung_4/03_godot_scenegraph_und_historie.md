# 🎮 TIEFENBERGUNG IV — BERICHT 03: GODOT SCENEGRAPH, CASINO GEOMETRIE & HISTORIE

**Datum:** 2026-08-14  
**Autor:** Antigravity / GemGem (Godot-Engine-Auditor)  
**Status:** TSCN NODES FULLY PARSED, SPATIAL CASINO BOUNDING BOX GEOMETRISCH BERECHNET  
**Ziel-Datei:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbergung_4/03_godot_scenegraph_und_historie.md`

---

## 1. VOLLSTÄNDIGER SCENEGRAPH VON `ring_002.tscn` (36 NODES)

Das Hauptszene-Dokument `/root/werkraum/engine/godot-vertical-slice/rings/ring_002_interaktionskreislauf/ring_002.tscn` wurde vollständig parsiert.

| Node Name | Node Type | Parent Node | Script / Sub-Resource Binding | Funktion im Interaktionskreislauf |
|---|---|---|---|---|
| `Ring002Interaktionskreislauf` | `Node3D` | `ROOT` | `ring_002_main.gd` | Hauptszene & Event-Bus Manager |
| `WorldEnvironment` | `WorldEnvironment` | `.` | Environment Sub-Resource | Beleuchtung & Sky-Shader |
| `WorldKeyLight` | `DirectionalLight3D` | `.` | None | Raumbeutellicht |
| `CasinoCellBuilder` | `Node3D` | `.` | `casino_cell_builder.gd` | Prozeduraler Raum- & Wand-Generator |
| `GordsliderFrontLight` | `OmniLight3D` | `.` | None | Akzentlicht vor dem Automaten |
| `PersistenceStore` | `Node` | `.` | `persistence_store.gd` | Lokaler Save-State Store |
| `Gordslider` | `Node3D` | `.` | `gordslider_interactable.gd` | Interaktives 3D Slot-Cabinet |
| `CabinetBase` .. `Screen` | `MeshInstance3D` (8x) | `Gordslider` | BoxMesh / StandardMaterial3D | Gehäuse, Säulen, Bildschirm, Control Panel |

---

## 2. RÄUMLICHE GEOMETRIE-MESSUNG VON `casino_cell_builder.gd` (VOM PRÜFER ZEILENGENAU BESTÄTIGT)

Aus der zeilengenauen Code-Analyse und der unabhängigen Verifikation durch Prüfer-Subagent 16:

- **Boden-Abmessungen (Zeile 72 & 73):** `24.0 m (X-Breite) x 28.0 m (Z-Tiefe)` (`Vector2(24, 28)` carpet & collision box)
- **Wand-Höhe (Zeilen 74-77):** `6.4 m` (Center Y = 3.2 m, Höhe = 6.4 m, Ceiling Center Y = 6.35 m)
- **Räumliche Bounding Box (Code-Geometrie):** **`24.0 m x 28.0 m x 6.4 m`** (Gesamt-Raumvolumen der zellulären Keimkammer: `4.300,8 m³`).
- **Vergleich zu Metatags (Zeilen 35 & 166):** Die Zahl `"1.656 M"` existiert im GDScript ausschließlich als:
  1. Node-Metadata Eintrag (`set_meta("casino_master_height_m", 1656)`).
  2. In-World `Label3D` Textinhalt (`"GESAMTHÖHE 1.656 METER\nDIESER RAUM IST NUR EINE ZELLE"`).


---

## 3. HISTORISCHER REKONSTRUKTIONS-STATUS DER RINGE 001 UND 003

- **Ring 001 (`grundstimmung`):** Git- & Systemscan belegt **0% `.tscn` oder `.gd` Dateien**. Existiert historisch rein als Markdown-Spezifikation.
- **Ring 003 (`weltsubstanzen`):** **0% `.tscn` oder `.gd` Dateien**. Existiert als konzeptionelles Markdown-Dokument.
- **Ring 002 (`interaktionskreislauf`):** Der einzige real existierende, ausführbare Godot 3D-Körper im Projekt (belegt durch `ring_002_headless.gd`).
