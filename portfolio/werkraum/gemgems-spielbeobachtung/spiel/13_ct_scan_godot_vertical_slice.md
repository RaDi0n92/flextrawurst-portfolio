# CT-Scan 13: Der Godot-Vertikalschnitt `godot_vertical_slice_001` & Port 18092

**Erstellungsdatum:** 13.08.2026  
**Status:** Vollständig seziert (Code- & Architektur-Analyse)  
**Ablage:** `/root/werkraum/gemgems-spielbeobachtung/spiel/13_ct_scan_godot_vertical_slice.md`

---

## 1. Übersicht & Godot 4.3 Projektstruktur

Der physisch lauffähige Godot-Spielekörper befindet sich unter:  
`/root/werkraum/engine/flextrawurst-game/game/godot_vertical_slice_001/`

- **Godot-Version:** `4.3.stable.official.77dcf97d8` (Projektdatei `project.godot`).
- **Hauptszene:** `main.tscn` (Node3D).
- **Hauptskript:** `scripts/main.gd` (187 Zeilen GDScript 2.0).
- **Weltbrücke:** `scripts/world_bridge.gd` (107 Zeilen GDScript 2.0).

---

## 2. Der Code-Befund im Detail

### 🏃 1. 3D Character Controller (`main.gd`)
- **Node-Typ:** `CharacterBody3D` (`$Player`).
- **Steuerung:** WASD & Pfeiltasten (dynamisch per `InputMap.add_action()` auf `KEY_W`, `KEY_A`, `KEY_S`, `KEY_D` & Pfeiltasten gemappt).
- **Physik-Werte:** 
  - `MOVE_SPEED = 7.0`
  - `GRAVITY = 24.0`
  - Abfrage per `Input.get_vector()` und Ausführung via `player.move_and_slide()`.

### 🌍 2. Weltseed & HUD-Anzeige (`world_seed.json`)
- Liest `res://data/world_seed.json` und blendet ggf. `res://data/world_seed.runtime.json` drüber.
- **HUD (`$HUD/Panel/Status`):** Zeigt Welt-ID, Region und Truth-Status an (z.B. `"Welt-ID: ..., Region: ... · Status: ..."`).
- **Spawn-Point:** Setzt den Spieler auf die Koordinaten `Vector3(spawn.x, spawn.y, spawn.z)`.

### 🧊 3. 3D Asset Loading & Provenienz-Objekt
- **Asset:** `test_cube.glb` (1.476 Bytes) oder Fallback via `test_cube.glb.b64`.
- **Loader:** Lädt die GLB-Datei per `ResourceLoader` oder decodiert den Base64-Puffer via `GLTFDocument` & `GLTFState`.
- **Objekt-Spawning:** Platziert das 3D-Objekt als `AlleswisserProvenanceAsset` in der Szene an der Position `Vector3(0.0, 1.25, -8.0)` mit der Skalierung `Vector3(2, 2, 2)` und speichert `alleswisser_id` & `truth_status` als Metadaten am Node.

### 🌐 4. Die Weltbrücke (`world_bridge.gd` & Port 18092)
- **HTTP Node:** Erstellt autonom ein `HTTPRequest`-Child-Node (`WorldBridgeHTTP`).
- **Port & Config-Override:** 
  - Im Grundseed `world_seed.json` steht `enabled: false` und `sync_interval_seconds: 5.0`.
  - Im vorhandenen VPS-Runtime-Override `world_seed.runtime.json` steht `enabled: true`, `base_url: http://127.0.0.1:18092`, `proof_event_on_start: true` und **`sync_interval_seconds: 1.0`** (Taktet im 1-Sekunden-Takt!).
- **Funktionalität:**
  - **Pull:** `GET /worlds/{world_id}/events?after={cursor}` im 1-Sekunden-Takt.
  - **Push:** `POST /worlds/{world_id}/events` schickt `pending_events` an den Server.
  - **Startup Proof:** Sendet beim Start automatisch `GODOT_ENGINE_SLICE_STARTED` mit Spieler-Position und `asset_id` an die Brücke.

---

## 3. Zusammenfassendes Beweis-Urteil

| Komponente | Code-Befund | Status |
| :--- | :--- | :--- |
| **3D-Spielfigur & Physik** | `CharacterBody3D`, WASD/Pfeile, `move_and_slide()` | 🟢 **Direkt belegt** |
| **3D GLB Asset Spawning** | `GLTFDocument` Puffer-Loader & `ResourceLoader` | 🟢 **Direkt belegt** |
| **HUD & Seed-System** | Dynamic JSON Merge & UI Status Label | 🟢 **Direkt belegt** |
| **Port 18092 Python-Bridge-Server** | Server lauscht auf 18092, empfängt GET/POST | 🟢 **Direkt belegt** (Prozess lauscht) |
| **1s Takt & Startup-Event** | `world_seed.runtime.json` Override aktiviert | 🟢 **Direkt belegt** |
| **Aktuell laufender Godot-Client** | Client-Prozess läuft zur Minute nicht aktiv | ⚪ **Nicht belegt** (Test-Historie belegt) |
| **Vollständiges Open-World-Game** | Erst 1 Test-Würfel & 1 Minimal-Szene vorhanden | 🔴 **Nicht belegt / Minimaler Slice** |
