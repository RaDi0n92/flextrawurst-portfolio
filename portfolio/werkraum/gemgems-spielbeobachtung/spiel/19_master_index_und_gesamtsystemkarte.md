# Master-Index & Verzweigte Gesamt-Anatomie des Flextrawurst-Spiels

**Erstellungsdatum:** 13.08.2026  
**Ablagepfad:** `/root/werkraum/gemgems-spielbeobachtung/spiel/19_master_index_und_gesamtsystemkarte.md`  
**Status:** ✅ Präzisiert & Korrigiert (Explizite relationale Entkopplung aller Säulen)

---

## 🏛️ Executive Summary: Das wahre Bild des Flextrawurst-Spiels

Die Ausgrabung aller geretteten Quellpakete, Session-Tagebücher, Git-Commits, Result-JSONs und Geodaten-Strukturen zeigt ein differenziertes Bild der Flextrawurst-Engine-Entwicklung:

1. **Keine lineare Code-Abstammung (v1 → v21 → v22 → Godot):**  
   Das Spiel entwickelte sich in **nicht-linearen, eigenständigen Stämmen**:
   - **v1–v20 (Prototypen & Fragmente):** Historische Web-Prototypen mit belegten Quellenlücken (v1–v7 und v20 nicht als isolierte Quellordner vorhanden).
   - **v21 (Canvas-2D Software-3D-Engine):** Der primäre, spielbare und Playwright-getestete Spielkörper mit 20 Baugates (Gate 01–12 & 13A–13H) und **285/285 bestandenen historischen Checks** (Stand: 25. Juli 2026).
   - **v22 (Questkosmos & Matrix-Simulation):** Ein reines offline-generiertes Questdesign- und Redteam-System (1.337 Zeilen Python-Code in `tools/`, 111.111 Questkeime, SQLite/CSV/JSONL), **ohne** neuen Canvas- oder GDScript-Laufzeitcode.
   - **Godot 4.3 `slice_001` (Nativer C++/GDScript Zielkörper):** Am **25. Juli 2026** eigenständig neu angelegt (Commit `2d38ec91d`, PR #3). Entstand aus Daniels Wunsch (*"ne echte gameengine zusammen an gpt zu kleben"*), nicht als Code-Portierung von v21.
   - **Kosmos 300 km² Wupper-Ennepe:** 68 MB Geodaten (reale OSM-Vektoren wie 3.591 Schwelmer Tür-Nodes mit Velbert-Geofence-Überschuss, vermischt mit `status: synthetisch_verifiziert` Fallback-Dateien) + prozedurale Voxel-Interior-Synthese.

---

## 🗺️ Typisiertes Beziehungs- & Verzweigungs-Diagramm (Keine Evolution)

```
[v1–v20 Prototypen] ──► [v21 Engine] 
(Quellenlücken v1-v7)   (Canvas 2D, 20 Gates, 285 Checks)
[Relation: Historie]          │
                              ├──────────────────────────────────────────────────────┐
                              ▼                                                      ▼
                   [v21 ↔ v22 Bezugnahme]                                 [Godot 4.3 Slice _001]
               (Historisch/Konzeptionell,                              (Am 25.07.2026 neu geboren,
                keine Runtime-Integration)                              GDScript / Port 18092)
                              │                                                      │
                              ▼                                                      ▼
                   [Kosmos 300 km² Geodaten]                             [Godot ↔ v22 / Kosmos]
               (OSM-Vektoren & Synthese-Fallbacks)                      (Geplante mögliche Integration,
                                                                         derzeit reine Transportbridge)
```

### Explosive Beziehungs-Klassifikation:
- `v21 ↔ v22`: **Historische/konzeptionelle Bezugnahme, keine Runtime-Integration** (v22 baut keinen v21-Code).
- `Godot ↔ v22`: **Geplante mögliche Datenintegration, derzeit nicht implementiert** (HTTP-Bridge lauscht, verarbeitet aber noch keinen v22-SQLite-Seed).
- `Godot ↔ Kosmos`: **Geplante Weltgeometrieintegration, derzeit Platzhalter** (Godot lädt `test_cube.glb`, noch keine GeoJSON-Szenen).

---

## 📜 Verzeichnis der Spezial-CT-Scan-Berichte

| Bericht | Thema & Inhalt | Kernerkenntnisse & Status |
| :--- | :--- | :--- |
| [`15_ct_scan_v21_gate_matrix_vollstaendig.md`](file:///root/werkraum/gemgems-spielbeobachtung/spiel/15_ct_scan_v21_gate_matrix_vollstaendig.md) | **Vollständiger v21 Gate-Komplex (Gate 01–12 & 13A–13H)** | 20 Gates, **285/285 PASS (Historisch)**. Strikte 3-Stufen-Bedientrennung (Code-UI vs Auto-Test vs FW_TEST API). |
| [`16_ct_scan_v22_questkosmos_generator_simulation.md`](file:///root/werkraum/gemgems-spielbeobachtung/spiel/16_ct_scan_v22_questkosmos_generator_simulation.md) | **v22 Questkosmos & Matrix-Simulation** | 1.337 Zeilen Python-Code. Pass B 0% gescheiterte Quests = Durchsetzung der programmierten Generator-Constraints (kein automatischer Playtest-Beweis). Typo gefixt, WebGL entfernt. |
| [`17_ct_scan_godot_provenienz_und_session_analyse.md`](file:///root/werkraum/gemgems-spielbeobachtung/spiel/17_ct_scan_godot_provenienz_und_session_analyse.md) | **Godot-Provenienz & Session-Analyse** | Geburtsurkunde: 25.07.2026 (Commit `2d38ec91d`). Daniels Rohtext (*"ne echte gameengine zusammen an gpt zu kleben"*) getrennt von ChatGPT-Paraphrase. GDScript (Projekt) vs C++ (Engine). |
| [`18_ct_scan_kosmos_geodaten_prospektion_vs_runtime.md`](file:///root/werkraum/gemgems-spielbeobachtung/spiel/18_ct_scan_kosmos_geodaten_prospektion_vs_runtime.md) | **Kosmos Geodaten, Harvester & Voxel-Interior** | 68 MB Datenbestand klassifiziert (3.591 reale Tür-Nodes mit Velbert-Geofence-Überschuss vs. `status: synthetisch_verifiziert` Fallbacks). v21 (Canvas) vs v22 (Generator) getrennt. |

---

## 📊 Typisierte Matrix aller Gameplay-Organe

| Gameplay-Organ | v21 Canvas Engine (Code & Tests) | v22 Questkosmos (Simulation) | Godot 4.3 Slice _001 (Native Engine) | Kosmos Geodaten (Prospektion) |
| :--- | :--- | :--- | :--- | :--- |
| **Spieler-Steuerung & 3D-Blick** | 🟢 Canvas 2D Perspective (`v21_traversal.js`, WASD) | 🔴 Kein Code | 🟢 Native GDScript (`CharacterBody3D`, WASD) | ⚪ Nicht betroffen |
| **Greifhaken & Fallschirm** | 🟢 Gate 02 (`fireGrapple`, `parachute`) | ⚪ Als Organ-Maske simuliert | 🔴 Nicht implementiert | ⚪ Nicht betroffen |
| **Taktische Pause & Heilung** | 🟢 Gate 09 (`Tab` stoppt Zeit, Pausen-UI) | ⚪ In Redteam-Checks geprüft | 🔴 Nicht implementiert | ⚪ Nicht betroffen |
| **Wesenrechte & Duell-Consent** | 🟢 Gate 09 (`consentDuel21`, Abbruch bei Nein) | 🟢 88.888 Wesen in DB verknüpft | 🟡 **Nur Transport-Bridge (Port 18092)**, keine Logik | 🟢 0% NPCs / 100% Wesen |
| **Untergrund & Mining** | 🟢 Gate 04 (Erzabbau, Tiefensteuerung) | ⚪ In 7-Akt-Ketten simuliert | 🔴 Nicht implementiert | 🟢 3 Dungeons definiert |
| **Fahrzeug-Werkstatt & Fleet** | 🟢 Gate 05 & 11 (16 Fahrzeuge, Modulmontage) | ⚪ In 99 Varianten simuliert | 🔴 Nicht implementiert | 🟢 Nordbahntrasse Vektoren |
| **69-Bäume Skill-System** | 🟢 Gate 13A–13H (276 Knoten, Handlungs-XP) | 🟢 69 Skills in Quests integriert | 🔴 Nicht implementiert | ⚪ Nicht betroffen |
| **Quests & Dialog-Epos** | 🟢 Gate 10 (5 Untergrund-Quests) | 🟢 111.111 Questkeime (SQLite DB) | 🟡 **Nur Transport-Bridge (Port 18092)**, keine Runtimeseed-Verarbeitung | 🟢 Schwelm/Wuppertal Orte |
| **100% Begehbarkeit & Interior** | ⚪ Räumliche Stollen-Polygonfaces | ⚪ 111 Checks | 🔴 Platzhalter `test_cube.glb` | 🟢 14,86 MB OSM-Polygone + Voxel-Grid |

---

## 🔮 Fazit

Das Flextrawurst-Spiel ruht auf **drei verschiedenen Säulen**:
1. **v21 Canvas-Engine:** Der bewiesene, ausführbare JavaScript-Spielkörper.
2. **v22 Questkosmos:** Das offline generierte SQLite-Questkatalog-Fundament.
3. **Godot 4.3 Slice _001:** Der C++/GDScript-Projektkörper mit Port 18092 Event-Bridge.

Der Master-Index verbindet diese drei Säulen ohne falsche Abstammungspfeile.
