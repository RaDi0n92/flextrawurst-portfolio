# CT-Scan 14: Die v21/v22 Baugates & Der historische Evolutionspfad des Spiels

**Erstellungsdatum:** 13.08.2026  
**Status:** Vollständig seziert (Code- & Belegkörper-Analyse)  
**Ablage:** `/root/werkraum/gemgems-spielbeobachtung/spiel/14_ct_scan_v21_v22_historical_game_gates.md`

---

## 1. Präzisierung des Runtime-Status für Option A (Godot)

Bevor wir in die v21/v22 Baugates eintauchen, wird der Runtime-Status des Godot-Schnitts chirurgisch korrigiert:

- **Der Python-Bridge-Prozess (Port 18092):** Lauscht **live** auf `127.0.0.1:18092` 🟢.
- **Taktintervall:** `world_seed.json` nennt standardmäßig `5.0s` (mit `enabled: false`). Im aktiven Runtime-Override `world_seed.runtime.json` ist jedoch `enabled: true`, `proof_event_on_start: true` und **`sync_interval_seconds: 1.0`** (1-Sekunden-Takt!) konfiguriert 🟢.
- **Laufender Godot-Client:** Der Python-Server lauscht, aber aktuell läuft **keine** aktive Headless-Godot-Client-Instanz als Dauerprozess ⚪.

---

## 2. Die historische 3-Phasen-Evolution & Verzweigung der Game-Engine

Durch die Untersuchung von `/root/werkraum/engine/flextrawurst-game/extracted_sources/` lässt sich die reale Verzweigung des Spiels wie folgt abbilden:

```
[v1–v20 Prototypen] ──→ [v21 Canvas-3D-Spielkörper] ──┬──→ [v22 Questkosmos/Simulation] (111.111 Questkeime, keine neue Runtime)
                        (Eigener Software-3D-Renderer  │
                         auf HTML5 Canvas 2D,         └──→ [Godot 4.3 Slice] (Port 18092, separater nativer Zielkörper)
                         Playwright-automatisiert)
```

---

## 3. Die v21 Baugates im Detail (Software-3D auf Canvas 2D)

In der v21-Epoche war das Spiel **kein WebGL-Spiel**, sondern nutzte einen eigenen, abhängigkeitsfreien perspektivischen Software-3D-Renderer auf `canvas.getContext('2d', {alpha:false})` (`V21/src/renderer.js`). Playwright diente als Testskript-Prüfer (Screenshot- & API-Runner), nicht als Game-Engine.

- **GATE 04 (Untergrund / Erze / Dungeons):** 14/14 Checks grün. Begehbarer Untergrund, Höhlen/Adern/Räume, Erzabbau mit mehreren Schlägen, Tiefenfortschritt, Dungeon-Dialoge, einmalige Beute, Wiederbesuch ohne Loot-Duplizierung, Untergrund-Bauen, Vertikalität, Save/Load. (Beleg: `tests_v21/GATE_04_RESULT.json` & `gate04_underworld_dungeon.png`).
- **GATE 09 (Pause / Kampf / Loot / Nebenquests):** 17/17 Checks grün. Ausrüstbare Waffen/Rüstungen, taktische Pause, Heilzauber, Trefferfolgen, Weapon-Mastery durch Treffer, endlicher Loot mit Herkunft, Duell-Mechanik, mehrstufige Dungeon-Nebenquest, Save/Load. (Beleg: `tests_v21/GATE_09_RESULT.json`).
- **v21 vs. v22 Status-Trennung:** Laut `01_V21_V22_STATUS_TRENNUNG.md` ist v21 der einzige vollständig ausführbare/getestete Spielkörper. v22 ist ein dokumentierter/simulierter Quest- & Generatorkörper (111.111 Questkeime), der noch nicht als neue Quest-Runtime in v21 verbaut wurde!

---

## 4. Zusammenfassende Truth-Matrix: Spiel-Runtime vs. Archiv

| Epoche / System | Medium / Runtime | Status |
| :--- | :--- | :--- |
| **v1–v20 Prototypen** | HTML5 / Canvas / Node.js (Port 8787) | 🟢 **Historisch belegt** (Code in `/flextrawurst/`) |
| **v21 Baugates (01–12)** | Playwright WebGL / Screenshot-Runner | 🟢 **Historisch belegt** (JSON & PNG Belege) |
| **Godot 4.3 Slice (`slice_001`)** | Native C++/GDScript Engine (Port 18092) | 🟢 **Aktueller Ziel-Code** (Headless verifiziert) |
| **Integrites Monolith-Game** | Ein einziges fertiges 3D Open-World Game | 🔴 **Nicht belegt / Geplant** |
