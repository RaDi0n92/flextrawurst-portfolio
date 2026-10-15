# Spiegelprüfung — `spiel/13_ct_scan_godot_vertical_slice.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/spiel/13_ct_scan_godot_vertical_slice.md`
- Snapshot-SHA256: `522bab749ae7d18fb343a5fa1f1b2c794b460f5030c32e195479e2f3497444f7`
- Bytes: 3752
- Zeilen: 63
- Snapshot-mtime: `2026-08-13T05:18:37.889743+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–63: `bed291fa1024a607d5a01723ee7294eec19cfcf1bcf9aff1a39952560e2c668a` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Seziert den Code des Godot-Minimalschnitts: `project.godot`, `main.tscn`, `main.gd`, `world_bridge.gd`.
- Beschreibt `CharacterBody3D`, WASD/Pfeile, MOVE_SPEED 7, GRAVITY 24, Seed-/HUD-Logik und Spawnposition.
- Beschreibt Laden/Spawnen von `test_cube.glb` bzw. Base64-Fallback inklusive Provenienz-Metadaten.
- Dokumentiert WorldBridge-Konfiguration: Grundseed disabled/5s, Runtime-Override enabled, `127.0.0.1:18092`, Startup-Proof und 1s Sync.
- Schlussmatrix sagt: Bridge-Server lauscht, Godot-Client läuft aktuell nicht, vollständiges Open-World-Game nicht belegt.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Hauptskript laut Datei 187 Zeilen; Bridge 107 Zeilen; Testasset 1.476 Bytes; Assetposition `(0,1.25,-8)`, Skalierung `(2,2,2)`.

## Provenienzklasse

Gemini-Code-/Architektur-Sekundärbericht vom 13.08.2026 über einen konkreten Godot-Slice plus behaupteten Prozessstatus.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Vorhandener `world_seed.runtime.json`-Override beweist Konfiguration, aber bei nicht laufendem Godot-Client keine aktive 1s-Synchronisation des Clients.
- `Port 18092`-Listener beweist die Bridge, nicht die Spielclient-Laufzeit.
- Projektmetadaten `4.3` sind nicht automatisch Beleg für jede tatsächlich verwendete/installierte Godot-Binärversion.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
