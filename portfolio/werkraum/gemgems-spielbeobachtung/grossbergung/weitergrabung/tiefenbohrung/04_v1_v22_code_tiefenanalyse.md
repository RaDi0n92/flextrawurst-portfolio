# TIEFENBOHRUNG 04: V1-V22 CODE- & GORDSLIDER-TIEFENANALYSE

**Erstellt von:** Tiefenbohrung Subagent 4 (Read-Only Code & Engine Gräber)
**Zielpfad für Festplatte:** `/root/werkraum/gemgems-spielbeobachtung/grossbergung/weitergrabung/tiefenbohrung/04_v1_v22_code_tiefenanalyse.md`

---

## GELESENE PROTOTYPEN & CODEPFADE

1. **`/root/werkraum/gordslider/gordslider.html`** (3.812 Zeilen HTML/JS, 110.240 Bytes)
   - Vollständiger, eigenständiger HTML5 Canvas/DOM Slot-Engine Prototyp ("sandycheats").
   - PRNG Implementation (`xmur3` MurmurHash3 + `mulberry32` 32-Bit Generator).
   - Multi-Spielfeld Mechanik (3×5 / 6×5 / 9×5 Active Window), Kaskaden-Mathematik (K1–K8+), Dynamic Paytable Editor mit LocalStorage Backup (`GORDSLIDER_PAYLIVE_v1`), Waves-Stimmungs-System (COLD / HOT / COOLDOWN).

2. **`/root/werkraum/engine/flextrawurst-game/extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/`**
   - **`03_VERSIONENCHRONIK_V01_BIS_V22/`**: 29 Akten-Dateien (`V01_GESAMTAKTE.md` bis `V22_GESAMTAKTE.md` inkl. Teilversionen V14.1, V14.2, V15.1, V19.1–V19.3).
   - **`15_CODE_TESTS_DATENBANKEN_SCREENSHOTS_UND_SPIELKOERPER/V21/`**:
     - `PLAY_FLEXTRAWURST_V15_1.html` (193.104 Bytes)
     - `PLAY_FLEXTRAWURST_V17.html` (225.476 Bytes)
     - `PLAY_FLEXTRAWURST_V21.html` (544.712 Bytes)
   - **`15_.../V22/`**: `PACKAGE_AUDIT.json`, `01_audit`, `05_redteam` (R21-R26).

3. **`/root/werkraum/WorldWORDS-ANTIBIBEL-Website/`**
   - Django 5.2 / PostgreSQL Offenes Begriffsregister mit Daniel als Gründungskurator. Append-Only Provenienzereignisse, CC BY-SA 4.0 / MIT.

4. **`/root/werkraum/engine/flextrawurst-game/extracted_sources/vps_live/tools_3d_pipeline/blender_pipeline.py`**
   - Headless Blender 4.0.2 Automation Engine (`-b --python`) für Format-Konvertierung (FBX, OBJ, STL, GLB) und Studio-PNG Renders.

---

## EXAKTE GORDSLIDER-CODE-ANATOMIE

### 1. PRNG-Kaskade (`xmur3` + `mulberry32`)
- **`xmur3(str)` (Zeile 734-745):** Murmur3-basierter Hash-Generator. Wandelt Seed-Strings (z.B. `"666"`) in einen 32-Bit-U-Integer State um:
  `h = Math.imul(h ^ str.charCodeAt(i), 3432918353);`
- **`mulberry32(a)` (Zeile 747-754):** Erzeugt eine deterministische Pseudo-Zufallszahl `[0, 1)`:
  `t = a += 0x6D2B79F5;`
- **Seed-Verwaltung:** `setSeedCore(seedStr)` initialisiert den Zustand, setzt Budget auf `666666` zurück.

### 2. Grid-Modi & Active Windows
- **`gridMode` (3 | 6 | 9):**
  - Mode 3: 3×5 Spielfeld (Zeilen 6..8 active, Wager-Multiplikator ×1)
  - Mode 6: 6×5 Spielfeld (Zeilen 3..8 active, Multiplikator ×2)
  - Mode 9: 9×5 Spielfeld (Zeilen 0..8 active, Multiplikator ×3)
- **`isRowOHG(r)`:** Zeilen oberhalb des aktiven Fensters fungieren als "Overhead-Grid" (OHG) für Vorlauf/Priming.

### 3. Kaskaden-Mathematik & Farbschema
- **`cascadeColor(level)` (Zeilen 1328-1339):**
  - K1: `#ff2d2d` (Rot)
  - K2: `#ff8a00` (Orange)
  - K3: `#ffd400` (Gelb)
  - K4: `#00d46a` (Grün)
  - K5: `#2f7bff` (Hellblau)
  - K6: `#3f51ff` (Dunkelblau)
  - K7: `#a64cff` (Violett)
  - K8+: `#ffffff` (Weiß/Alternierend Schwarz)
- **Freispiel-Staffelung durch Kaskaden:**
  - K1: 3 FS | K2: 2 FS | K3: 1 FS | K4: +10 FS | K5: +20 FS | K6: +30 FS | K7: +40 FS | K8+: +50 FS.

### 4. Symbol-Strips & Harten Regeln
- **Low:** `9`, `10`, `J`, `Q`
- **Mid:** `K`, `A`
- **High:** `Blitzwand`, `Magicboots`, `Magicwand`
- **Top:** `Schloss`
- **Gord-Symbole:** `GORD1`, `GORD2`, `GORD3`
- **HARTE REGEL (`GORD_ALLOWED_COLS = [1, 2, 3]`):** Gord-Symbole dürfen NIEMALS in Spalte 0 oder Spalte 4 erscheinen.

### 5. Freispiel-Kauf-Banken (FS Buy)
- **Buy 10 FS:** `bet * wagerMult() * 88`
- **Buy 20 FS:** `bet * wagerMult() * 166`
- **Buy 30 FS:** `bet * wagerMult() * 352`
- **Buy 50 FS:** `bet * wagerMult() * 666`

### 6. Dynamic Paytable & LocalStorage
- **Storage-Key:** `GORDSLIDER_PAYLIVE_v1`
- **Paytable Editor (Zeilen 3535-3736):** Erlaubt Justierung aller Multiplikatoren (1..500 in 0,5er Schritten).

---

## V1-V20 CANVAS-PROTOTYPEN-AHLENREIHE

1. **V01 bis V07:** Status `NICHT EINZELN REKONSTRUIERBAR` / `LUECKENHAFT_REKONSTRUIERT`. Frühe Prototyping-Phase ohne separate HTML-Dateien im Upload-Bundle.
2. **V08 bis V14:** Konsolidierung der Kernregeln, Kaskaden und Wager-Mathematik. Einführung der Teilversionen V14.1 und V14.2.
3. **V15 (V15.1):** Erster voll lauffähiger historischer Single-File-Engine-Körper (`PLAY_FLEXTRAWURST_V15_1.html`, 193 KB). Canvas-Slot mit Grundsymbolen.
4. **V17:** Erweiterte Runtime (`PLAY_FLEXTRAWURST_V17.html`, 225 KB) mit integriertem Audit-Logging.
5. **V21 & V22:** Voll ausgebauter 544 KB Standalone-HTML-Codekörper (`PLAY_FLEXTRAWURST_V21.html`) mit Dust/Maxus-Vertragsintegration und Quest-Kosmos.

---

## DANIEL-ROHZITATE

- **Zur Geschwindigkeits- und Qualitätsphilosophie:**
  > *„bei mir gehts immer um saubere korekte und ausführlichen output ...niemals um schnelligkeit.“*
- **Zur Rohheit und Textur:**
  > *„alles so roh und ehrlich formuliert bleibt wie es hier im verlauf steht... alles andere ist scheisse.“*
- **Zu Live-Updates auf Flextrawurst:**
  > *„ab sofort immer alles sofort am besten live aktualisiert und geupdatet ist auf ganz flextrawurst nicht immer erst bei f5.“*

---

## FRÜHESTE DATIERUNG

- **Gordslider:** Enthält Log-Einträge und Snapshot-Mechaniken aus Mitte 2026.
- **V1-V22 Bundle:** Rekonstruiert historische Stufen bis zur Quelleneinzugs-Manifestierung vom **25.07.2026** und Handover-Berichten vom **23.07.2026**.

---

## SPÄTERE MUTATIONEN

- Evolution von einfachen 3×5 Standard-Slots zu variablen Grid-Fenstern (3×5 / 6×5 / 9×5).
- Integration von Stimmungs-Zustandsmaschinen (`WAVES`: Cold -> Hot -> Cooldown).
- Ersetzung von statischen Paytables durch dynamisch anpassbare In-Game Paytable-Editoren.
- Einbettung von Gord-Spezialregeln (Gord nur auf Innenwalzen 1..3).

---

## BEZIEHUNG ZUM HEUTIGEN SPIEL

- **Gordslider HTML** ist der direkte Vorläufer- und Erprobungskörper für die slot- und kaskadenbasierten Spielorgane im Flextrawurst-Universum.
- Die im Gordslider erprobte Kaskaden-Farbskala (K1-K8) und PRNG-Determinismus dienen als Vorlage für die Godot/Canvas-Engine-Komponenten im Welt-System.

---

## NICHT BEWIESEN

- Es gibt keine physisch isolierten `.html` Dateien für V1 bis V7 im Upload-Archiv (nur spätere Gesamtakten und Audits).
- Eine direkte Verknüpfung der WorldWORDS-Django-Datenbank mit den Gordslider-Paytables im Produktivbetrieb ist im Code nicht hart verdrahtet.

---

## WIDERSPRÜCHE

- **Paytable vs. Dynamic Overlay:** Der HTML-Code definiert `PAY_DEFAULT`, lädt jedoch dynamisch Bilddateien `gordslider-paytable.jpg` und überschreibt Pay-Values via LocalStorage `GORDSLIDER_PAYLIVE_v1`.

---

## OFFENE SUCHRÄUME

- Deep-Scan der komprimierten `.zip` Archive in `99_ORIGINALUPLOADS_UNVERAENDERT` (`das neuuusteee(1).zip`, 29 MB & `das neuuusteee-0.5(1).zip`, 55 MB) nach Roh-Commits von V1-V7.
- Abgleich der Blender 3D-Symbolrenders (`blender_pipeline.py`) mit den in `PATH` gelisteten Symbolbildern (`bilder/high/140x180/slot/...`).

---
*Tiefenanalyse abgeschlossen und bereit zur Ablage.*
