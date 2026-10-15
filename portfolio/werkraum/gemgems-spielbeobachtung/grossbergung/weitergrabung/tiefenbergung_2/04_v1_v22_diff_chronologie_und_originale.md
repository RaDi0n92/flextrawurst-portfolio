# Tiefenbergung II – Prüfbericht 04: V1-V22 Code-Diff-Chronologie & V1-V7 Suche

**Datum:** 2026-08-14  
**Analyst:** Tiefenbergung II Subagent 4 (V1-V22 Code-Diff-Chronologie & V1-V7 Suche)  
**Empfänger:** Parent Agent (`38688430-4327-4a7a-bacf-4bd3e496948c`)  
**Prüfmethode:** Zeilen- und hashgenaue Nackte-Fakten-Analyse aller HTML-, Markdown-, JSON- und Zip-Dateien im VPS-Bestand. Strikte Befolgung des Anti-Behauptungs-Prinzips.

---

## 1. Physischer Bestand & Detailanalyse der HTML-Spielekörper

Im gesamten Dateisystem des VPS existieren exakt **3 physische Standalone-HTML-Spielekörper** für `PLAY_FLEXTRAWURST` sowie **1 interaktiver UI-Prototyp (`gordslider.html`)**.

### Matrix der physischen HTML-Dateien

| Dateiname | Pfad (Kanonisch/Extrahiert) | Größe (Bytes) | Zeilen | SHA-256 Hash | Technical Stack / Renderer |
|---|---|---|---|---|---|
| `PLAY_FLEXTRAWURST_V15_1.html` | `.../V21/PLAY_FLEXTRAWURST_V15_1.html` | 193.104 | 1.539 | `94fb66db776d180643a9c657fa01bd439461f58ffca43163682d283f8af98e79` | HTML5 Canvas 2D + Vanilla JS (`window.FW` v14.1.0) |
| `PLAY_FLEXTRAWURST_V17.html` | `.../V21/PLAY_FLEXTRAWURST_V17.html` | 225.476 | 1.737 | `4ff876c637d09ea2c8c45cc6fa58b3684a594eab26310c45ebef6edda8964fa5` | HTML5 Canvas 2D + Dustökologie 88.888 UI |
| `PLAY_FLEXTRAWURST_V21.html` | `.../V21/PLAY_FLEXTRAWURST_V21.html` | 544.712 | 3.299 | `7b15da11e4d2eee2d087f73cbaf7528642396a23f7b6f7af9fc3bf49604c021c` | Canvas 2D + `#futureShock` Overlay Canvas + 12 Gates |
| `gordslider.html` | `/root/werkraum/gordslider/gordslider.html` | 110.240 | 3.812 | `bbcd4f7394f9c49da2070304f6a623c0400904198724864543145f651cb64552` | HTML5/CSS3 DOM Slot-Machine Prototyp ("sandycheats") |

---

### Detaillierter Befund der einzelnen Runtimes

#### 1. `PLAY_FLEXTRAWURST_V15_1.html`
- **Code-Struktur:** Single-File HTML5 mit eingebetteten Styles (`<style>`), DOM-Elementen (`#topHud`, `#objective`, `#prompt`, `#quickbar`, `#toasts`, `#prologue`) und getrenntem Data- & Controller-Skript (`window.FW`).
- **Renderer:** Canvas 2D Top-Down / Isometrische Rendering-Engine (`<canvas id="world">`) sowie Minimap (`<canvas id="miniMap">`).
- **Game Loop:** `requestAnimationFrame`-basierter Render- & Update-Loop. Verarbeitet Positionen, Geschwindigkeiten (`MOVE_SPEED = 7.0`), Kollisionsgrenzen und Tag/Nacht-Lichtfarben.
- **Mechaniken:** WASD-Steuerung, 6 begehbare Regionen (Faltstadt, Materialgärten, Spiegelhafen, Kieselarchiv, Himmelsbruch, Fernfeld), 5 Zeit-Epochen (Gegenwart, Vergangenheit, Zukunft +333, alternative Zukunft, Fernfeld), Überlebensmeter (Gesundheit, Ausdauer, Atem), Ressourcensammeln (Metall, Faser, Glas, Kern, Charge, Credits). Prolog-Frage „3:33“ als Einstiegs-Overlay.
- **Testhooks:** Debug-Banner `#testBanner`, Tastaturkürzel `F10` schaltet isolierten Testmodus ein, `FW.SAVE_NORMAL='fw_maxus_v14_normal'` / `FW.SAVE_TEST='fw_maxus_v14_test'`.
- **Datenbestände:** Fest inlined in JavaScript (`FW.REGIONS`, `FW.AI`, `FW.ERAS`).

#### 2. `PLAY_FLEXTRAWURST_V17.html`
- **Code-Struktur:** Weiterentwicklung von V15_1. Erweitert die HTML/CSS/JS-Basis um 198 Zeilen spezifischen Code für die 88.888 Dustökologie.
- **Renderer:** Canvas 2D Top-Down Engine mit erweiterter Partikel-Rendering-Schicht für Dust-Reaktionen.
- **Game Loop:** Identisch mit V15_1, ergänzt um autonome Begegnungs- und Reaktivitäts-Updates der Dust-Entitäten.
- **Mechaniken:** Behält alle V15_1-Mechaniken bei und integriert den Schnellzugriff `O` (Lokale Dustökologie 88.888), Begegungsarchiv (`.dust-entry`) und Dust-Eigenschafts-Inspektor.
- **Testhooks:** Identisch mit V15_1 (`F10`-Testmodus, `test-banner`).
- **Datenbestände:** Inlined Dustökologie-Index und 88.888 Wesen-Attribute.

#### 3. `PLAY_FLEXTRAWURST_V21.html`
- **Code-Struktur:** Supermaximal-Bauring 4 HTML5 Monolith. 3.299 Zeilen hochkomprimierter JavaScript- und UI-Code.
- **Renderer:** Zweistufiger Renderer: 2D Canvas für die Hauptwelt + separater `#futureShock canvas` für cinematische Zeitreisen und Shocks.
- **Game Loop:** Multi-Phase Loop: World Loop, Tactical Pause State, Underworld Mining Loop, FutureShock Render Pipeline.
- **Mechaniken:** Enthält 12 Abnahme-Gates:
  - Gate 01: Prolog & 3:33 Zeitreise
  - Gate 02: Luftfahrzeuge & Versorgungsnetze
  - Gate 03: Mastery, Skillbäume, Crafting, Magie
  - Gate 04: Untergrund, Erze, vertikales Bauen
  - Gate 05: Flotten-Testzone (Straße, Wasser, Schiene, Flugring)
  - Gate 06: 88.888 AI-Wesen & Abspaltungen
  - Gate 07: Zeitkörper (-3.333j / +333j)
  - Gate 08: Creator Events & Karten-Editor
  - Gate 09: Skyrim-Kampfsystem, Taktische Pause, Zauber & Loot
  - Gate 10: Großgeografie (Wüste, Berge, Gletscher, Stadt, Küste)
  - Gate 11: Modularer Workshop & Objektbiografien
  - Gate 12: Erlebnislabor & Cheat-Zone
- **Testhooks:** Unter `tests_v21/` liegen 20 Playwright-Testskripte (`test_gate_01_opening.py` bis `test_gate_13h_...py`), die 285 Gate-Checks und 418 Prüfpunkte automatisiert ausführen.
- **Datenbestände:** Monolithischer Inlined-Datenkörper (Skillbäume, 88.888 Wesen, Item-Matrizen, Quest-Keime).

#### 4. `gordslider.html`
- **Code-Struktur:** Single-File HTML5/CSS/JS Casino-Slot-Machine ("sandycheats").
- **Renderer:** 2D DOM / CSS-Transformationen + Canvas Reel Animation.
- **Game Loop:** Event-basierter Spin- und Symbol-Evaluierungs-Loop.
- **Mechaniken:** 3 Walzen Slot-Machine, Bet-Sheet Overlay, Paytable-Grafiknachlader (`gordslider-paytable.jpg`), Free-Spins-Modus (`--fsbg`), Gewinnberechnung.
- **Testhooks:** Sandycheats Debug-Overlay, Reel-Force Override, LocalStorage Status-Speicher.
- **Datenbestände:** Bild-Verweise (`bilder/gord/`, `high/`, `low/`, `mid/`), Paytable-Gewinntabelle.

---

## 2. Untersuchung & Befund zu V1-V7 Originalen

### Pruefverfahren & Suchraum
Es wurden folgende Pfade zeilen- und hashgenau abgesucht:
1. `99_ORIGINALUPLOADS_UNVERAENDERT/` in `extracted_sources/historical_runtime/v1_v22_bundle/FLEXTRAWURST_SPIELE_V1_BIS_V22_WIE_ZUVOR_SAUBER/`
2. Raw Uploads unter `assets/raw_uploads/`
3. Die verschachtelten ZIP-Archive:
   - `das neuuusteee(1).zip` (SHA-256 `5fedd4a9176b2a0403f1b37e2a9287433dc5d0e64ed18ef6dc59c3c52be283c1`, 29.262.058 Bytes)
   - `das neuuusteee-0.5(1).zip` (SHA-256 `92c155af39045c9a45fb2a2641153c926a892a6d9bfcfebaf5ee9eb8a5696f0c`, 55.654.475 Bytes)
   - `flextrawurst_dust_echo_questkosmos_v22_final_2(das neuste-1.0.zip` (SHA-256 `16852cb8ed65e4f52ef9159ef5c1676b84530d9731f9f13020b9ca272b0e8e01`, 45.408.264 Bytes)

### Ergebnis der V1-V7 Suche
- **Harter Befund:** **In KEINEM der Archive und in KEINEM Upload-Verzeichnis existieren physische `.html`-Originaldateien für V1, V2, V3, V4, V5, V6 oder V7.**
- **Erhaltungsklassifikation:** V1 bis V7 existieren im Dateisystem ausschließlich als **Markdown-Rettungskörper / Versionskarten** (`markdown_archive/v1_v22_rettungskoerper/03_SES~1/FW-VERSION-01__VERSIONSKARTE_V1.md` bis `FW-VERSION-07__VERSIONSKARTE_V7.md`).
- **Original-Textauszug aus der Versionskarte `FW-VERSION-01`:**
  > *Status: REKONSTRUIERT. Die Version wird in erhaltenen späteren Dokumenten ausdrücklich genannt, ihr vollständiger eigener Paketkörper liegt hier jedoch nicht separat vor. Fehlende Originalkörper bleiben fehlend. Eine Versionsnummer ersetzt keinen Quelltext.*

---

## 3. Lückenlose Versions-Diff-Chronologie (V1 bis V22)

| Version | Typus / Körper-Klasse | Physische Quelldatei | Status & Befund |
|---|---|---|---|
| **V1** | Spezifikation / Konzept | `FW-VERSION-01__VERSIONSKARTE_V1.md` | `REKONSTRUIERT` (Dust-Ontologie & Dwarf Fortress Prinzipien) |
| **V2** | Spezifikation / Konzept | `FW-VERSION-02__VERSIONSKARTE_V2.md` | `REKONSTRUIERT` (Systemkeim & Zeitregeln) |
| **V3** | Spezifikation / Konzept | `FW-VERSION-03__VERSIONSKARTE_V3.md` | `REKONSTRUIERT` (Ideen-Redteam & 3:33-Frage) |
| **V4** | Spezifikation / Konzept | `FW-VERSION-04__VERSIONSKARTE_V4.md` | `REKONSTRUIERT` (Regionen & Materialgärten) |
| **V5** | Spezifikation / Konzept | `FW-VERSION-05__VERSIONSKARTE_V5.md` | `REKONSTRUIERT` (AI-Plattform & Wesen-Begriffe) |
| **V6** | Spezifikation / Konzept | `FW-VERSION-06__VERSIONSKARTE_V6.md` | `REKONSTRUIERT` (Vertragsmatrizen & Bauring 1) |
| **V7** | Spezifikation / Konzept | `FW-VERSION-07__VERSIONSKARTE_V7.md` | `REKONSTRUIERT` (Supermaximal-Prompt & Ontologie) |
| **V8** | Bauregeln / Verträge | `FW-VERSION-08__VERSIONSKARTE_V8.md` | `REKONSTRUIERT` (Tree-of-Truth Matrizen) |
| **V9** | Bauregeln / Verträge | `FW-VERSION-09__VERSIONSKARTE_V9.md` | `REKONSTRUIERT` (Redteam-Runden R1–R3) |
| **V10** | Bauregeln / Verträge | `FW-VERSION-10__VERSIONSKARTE_V10.md` | `REKONSTRUIERT` (13 Pflichtfragen & Architektur) |
| **V11** | Bauregeln / Verträge | `FW-VERSION-11__VERSIONSKARTE_V11.md` | `REKONSTRUIERT` (Prozedurale Generierung & Seed 13333337) |
| **V12** | Bauregeln / Verträge | `FW-VERSION-12__VERSIONSKARTE_V12.md` | `REKONSTRUIERT` (Fahrzeug- & Flugring-Regeln) |
| **V13** | Bauregeln / Verträge | `FW-VERSION-13__VERSIONSKARTE_V13.md` | `REKONSTRUIERT` (Bauverträge MAXUS) |
| **V14** | Prototyp-Spezifikation | `FW-VERSION-14__VERSIONSKARTE_V14.md` | `BESTÄTIGT` (Vorbereitung HTML5 Canvas Engine) |
| **V15** | **Vollkörper HTML5 2D** | `PLAY_FLEXTRAWURST_V15_1.html` (193 KB) | **`BESTÄTIGT`** (MAXUS Bauring 2, 6 Regionen, 5 Epochen, WASD Canvas Loop) |
| **V16** | Zwischen-Spezifikation | `FW-VERSION-16__VERSIONSKARTE_V16.md` | `REKONSTRUIERT` (Vorbereitung Dustökologie) |
| **V17** | **Vollkörper HTML5 2D** | `PLAY_FLEXTRAWURST_V17.html` (225 KB) | **`BESTÄTIGT`** (MAXUS Bauring 3, 88.888 Dustökologie & Begegnungsarchiv) |
| **V18** | Spezifikation / Zeitwelt | `FW-VERSION-18__VERSIONSKARTE_V18.md` | `BESTÄTIGT` (Zeitweltquellen & Schacht 0) |
| **V19** | Spezifikation / Zeitwelt | `FW-VERSION-19__VERSIONSKARTE_V19.md` | `BESTÄTIGT` (Kieselarchiv & Stimmengewebe) |
| **V20** | Neulesungs-Datenkörper | `00_VOLLSTAENDIGE_NEULESUNG_V20.json` | **`BESTÄTIGT`** (30.382 Zeilen Spezifikation & Finaler Bauauftrag) |
| **V21** | **Supermaximal-Vollkörper**| `PLAY_FLEXTRAWURST_V21.html` (544 KB) | **`BESTÄTIGT`** (Supermaximal-Bauring 4 Canvas Monolith, 12 Gates, 88.888 Wesen) |
| **V22** | Simulations- & Questschicht| `02_PRIOR_SIMULATION_REDTEAM...md` | **`BESTÄTIGT`** (Dust-Echo Questkosmos & Redteam R21–R26 über V21) |
