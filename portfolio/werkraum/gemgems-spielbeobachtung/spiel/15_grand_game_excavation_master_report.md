# Grand Game Excavation Master Report: Die wahre Anatomie des Flextrawurst-Spiels

**Erstellungsdatum:** 13.08.2026  
**Ablage:** `/root/werkraum/gemgems-spielbeobachtung/spiel/15_grand_game_excavation_master_report.md`  
**Status:** Vollständig seziert (Code-Analyse, Script-Audits, Runtime-Checks & Provenienz-Abgleich)

---

## 1. Die Dekonstruktion der KI-Glättungen & Missverständnisse

Bevor die Spielorgane analysiert werden, werden alle bisherigen Vereinfachungen und falschen KI-Modell-Pfeile bereinigt:

1. **Kein WebGL in v21:** Der v21-Spielkörper lief **nicht** auf WebGL. Der eigentliche Code in `V21/src/renderer.js` sagt explizit: `Small dependency-free perspective software renderer` auf HTML5 `canvas.getContext('2d', {alpha:false})`. v21 ist eine eigenständige Software-3D-Engine in Javascript. Playwright war der Testrunner für Screenshots und API-Verifikation, nicht die Render-Engine!
2. **v22 ist NICHT der Godot-Nachfolger:** Laut `01_V21_V22_STATUS_TRENNUNG.md` ist v21 der einzige tatsächlich ausführbare und getestete Spielkörper. v22 ist ein gigantischer, dokumentierter und simulierter Questdesign-/Generatorkörper (111.111 Questkeime), der **nicht** als Live-Questlaufzeit in v21 verbaut wurde.
3. **13 vs. 14 Metropolen:** Ein unkorrigierter Quellwiderspruch im Kosmos-Auftrag (Überschrift fordert 13 Metropolen, der Text zählt 14 auf: Berlin, Tokio, London, Paris, Chongqing, Neapel, Moskau, Wien, Edinburgh, Portland, Valletta, Dortmund, Wuppertal, Erfurt).
4. **Waffen, Fahrzeuge, Wesen:** 111 Waffenklassen, 66 Fahrzeugfamilien und 88.888 Wesenformen sind **Kosmos-SOLL-Dimensionen** / Prospektionsrahmen des Mega-Sammelauftrags, keine 111 fertigen 3D-GLB-Assets im Ordner!

---

## 2. Das reale Verzweigungs-Diagramm der Engine

```
[v1–v20 Prototypen] ──→ [v21 Canvas-3D Software-Engine] ──┬──→ [v22 Questkosmos/Simulation]
(HTML5/Canvas)           (Ausführbar & Playwright-getestet)  │    (111.111 Questkeime, kein Runtime-Code)
                                                             │
                                                             └──→ [Godot 4.3 Slice _001]
                                                                  (Port 18092, nativer C++/GDScript-Zielkörper)
```

---

## 3. Die verifizierte Anatomie des v21-Spielkörpers

In v21 (`source_v21/flextrawurst_spielewelt_supermaximal_bauring4_v21/src/`) existieren folgende reale Gameplay-Organe im Code:

### ⚔️ 1. Taktische Pause, Kampf & Wesenrechte (`v21_combat_loot_pause.js`)
- **Taktische Pause (`togglePause21`):** Das Drücken von `Tab` stoppt das Spielgeschehen. Spieler können im angehaltenen Zustand Ausrüstung (Waffe, Rüstung, Kleidung), Zauberslots und Heilung (`healDuringPause21`) verwalten, ohne unter Echtzeitdruck zu stehen.
- **Waffen & Haltbarkeit:** Waffen besitzen Angriffsreichweite (`range`), Schaden (`power`), Abklingzeiten (`cooldown`) und verschleißen bei Benutzung (`w.condition -= 0.35`). Treffer steigern Skills (z.B. *Marksmanship* bei Schusswaffen, *Smithing* bei Klingen).
- **Wesensrechte & Duellzustimmung (`consentDuel21`):** Das System unterscheidet unempfindsame Störungen (`fracture`) von empfindsamen Wesen. Ein Duell mit einem echten Wesen erfordert explizite Zustimmung (`consent = true`). Verweigert das Wesen die Zustimmung, bricht der Angriff mit der Meldung ab: *"Wesenmarkiertes Ziel verweigert. Testmodus ersetzt keine Duellzustimmung."*
- **Endlicher Loot (`openLoot21`):** Besiegte Ziele hinterlassen Loot-Boxen mit endlichen Ressourcen (`dustCrystal`, `charge`, `scrap`, `glass`).
- **Untergrund-Nebenquests (`SIDEQUESTS`):** 5 tiefe, mehrstufige Dialogquests im Untergrund (*Die Stimme, die nicht als Beute gelten will*, *Die Maschine*, *Der See unter zwei Epochen*, *Wurzeln mit fremdem Gedächtnis*, *Gewölbe der nicht benutzten Wunder*). Dialog-Entscheidungen verändern globale Weltvariablen (`aiRights`, `archiveIntegrity`, `future`, `ecology`, `magic.maxMana`).

### ⛏️ 2. Untergrund, Mining & Living Stone (`v21_underworld.js`)
- **Stollen & Abstieg:** `enterUnderworld()`, `descendUnderground()` zur Tiefensteuerung.
- **Erzabbau (`mineVein`):** Erzadern werden mit gezielten Schlägen abgebaut.
- **Lebender Stein:** `setLivingStoneConsent()` – Respektierung von lebender Steinmasse.

### 🧗 3. Traversal & Vertikalität (`v21_traversal.js`)
- **Greifhaken (`fireGrapple`, `detachGrapple`):** Ermöglicht das Anseilen und Heranziehen an Geometrie-Punkte.
- **Fallschirm (`toggleParachute`):** Bremst den Abstieg bei Stürzen aus großer Höhe.
- **Physik-Schleife (`traversalStep`):** Eigene Physikberechnung für Schwung und Gravitation.

### 🏎️ 4. Fahrzeug-Werkstatt & Fleet (`v21_modular_workshop.js` & `v21_fleet_testzone.js`)
- **Modulare Werkstatt:** `craftPart21()`, `installPart21()`, `uninstallPart21()` für Fahrzeugbauteile.
- **Fleet-Testzone:** `spawnFleet21()`, `vehicleTelemetry()` zur Telemetrieerfassung und Tastensteuerung (`keys21`).

### 🔮 5. Magie, Mastery & Skillbäume (`v21_mastery_magic.js`, `v21_skill_action_bodies.js`)
- **Magie & Verzauberung:** `castSpell()`, `enchant21()`, Manahaushalt.
- **Schleichen & Diebstahl:** `attemptPickpocket21()`, `returnPickpocket21()`, `unarmedStrike21()`.
- **Skillbäume:** `FW.SKILL_TREES21` mit Freischaltungs-Perks.

### 📜 6. User-Creator-System & Konzerte (`v21_creator_events.js`)
- **Karten-Editor:** `createMap21()`, `creatorObject21()`, `publishMap21()`.
- **Konzerte:** `startConcert21()`, `replayConcert21()` zum Aufzeichnen und Abspielen von Ingame-Konzerten.

---

## 4. Der Godot 4.3 Zielkörper (`slice_001` & Port 18092)

### 📌 Code-Analyse (`game/godot_vertical_slice_001/`)
- **Entstehung:** Angelegt am **25.07.2026** im Repository `RaDi0n92/flextrawurst-agent` (Deployment-Plan `MCP_DEPLOYMENT_PLAN.json` & `vps_install.sh`).
- **Spielfigur (`main.gd`):** `CharacterBody3D` (`$Player`), WASD/Pfeiltasten (`MOVE_SPEED = 7.0`, `GRAVITY = 24.0`, `move_and_slide()`).
- **Asset-Loader:** `test_cube.glb` (1.476 Bytes) geladen per `ResourceLoader` oder Base64-Puffer-Decoder (`GLTFDocument`).
- **World Bridge (`world_bridge.gd`):** 
  - Server lauscht **live** auf Port **`18092`** (`127.0.0.1:18092`) (Python-Bridge-Prozess).
  - Runtime-Override `world_seed.runtime.json` aktiviert 1-Sekunden-Sync-Takt (`sync_interval_seconds: 1.0`, `proof_event_on_start: true`).
  - Sendet beim Boot das Start-Event `GODOT_ENGINE_SLICE_STARTED`.
  - Der Godot-Client selbst läuft aktuell nicht als Dauerprozess ⚪.

---

## 5. Das finale Wahrheits-Register des Spiels

| System | Code vorhanden | Playwright getestet | Screenshot da | Live auf VPS |
| :--- | :--- | :--- | :--- | :--- |
| **v21 Software-3D Canvas Engine** | 🟢 Ja (`src/renderer.js`) | 🟢 Ja (`GATE 01–12`) | 🟢 Ja (`screenshots_v21/`) | ⚪ Historischer Code |
| **Taktische Pause & Heilung** | 🟢 Ja (`v21_combat_...`) | 🟢 Ja (`GATE 09`) | 🟢 Ja | ⚪ Historischer Code |
| **Wesenrechte & Duell-Consent** | 🟢 Ja (`v21_combat_...`) | 🟢 Ja (`GATE 09`) | 🟢 Ja | ⚪ Historischer Code |
| **Untergrund & Mining** | 🟢 Ja (`v21_underworld.js`) | 🟢 Ja (`GATE 04`) | 🟢 Ja (`gate04_...png`) | ⚪ Historischer Code |
| **Greifhaken & Fallschirm** | 🟢 Ja (`v21_traversal.js`) | 🟢 Ja (`GATE 12`) | 🟢 Ja | ⚪ Historischer Code |
| **Fahrzeug-Werkstatt & Fleet** | 🟢 Ja (`v21_modular_...`) | 🟢 Ja (`GATE 08`) | 🟢 Ja | ⚪ Historischer Code |
| **v22 Quest-Simulation (111k)** | 🟢 Ja (Datensätze) | 🔴 Nein (Kein Code) | 🔴 Nein | ⚪ Nur Generatorkörper |
| **Godot 4.3 `slice_001`** | 🟢 Ja (`main.gd`) | 🟢 Ja (Headless Xvfb) | 🟢 Ja (PNG erzeugt) | 🟢 Bridge-Port 18092 LIVE |
| **Monolith-Game (Alles in 1)** | 🔴 NEIN | 🔴 NEIN | 🔴 NEIN | 🔴 NICHT EXISTENT |
