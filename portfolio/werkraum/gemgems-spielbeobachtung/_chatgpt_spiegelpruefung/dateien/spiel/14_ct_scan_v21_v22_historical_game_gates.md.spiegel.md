# Spiegelprüfung — `spiel/14_ct_scan_v21_v22_historical_game_gates.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/spiel/14_ct_scan_v21_v22_historical_game_gates.md`
- Snapshot-SHA256: `1e070f69b0f1ddf0a7c4009ee276f93247174204753c74666cd3921d8b27fa9d`
- Bytes: 3562
- Zeilen: 49
- Snapshot-mtime: `2026-08-13T05:32:50.831820+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–49: `0f0fce0143faeed3aa9d0e9a7b5eaa30d6b559c0c4967d8cc6415292c67519ef` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Trennt v21 als Canvas-2D-basierten eigenen Software-3D-Renderer von v22 als Quest-/Simulationszweig und Godot als separaten nativen Zielkörper.
- Betont ausdrücklich: v21 ist kein WebGL-Spiel; Playwright ist Testrunner, nicht Engine.
- Hebt Gate 04 (14/14) und Gate 09 (17/17) als Beispiele hervor.
- Sagt, v21 sei ausführbarer/getesteter Spielkörper, v22 dagegen dokumentierter/simulierter Quest-/Generatorkörper ohne Integration als neue v21-Runtime.
- Wiederholt Bridge live / Godot-Client nicht dauerhaft laufend.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Stammbaumgrafik: v1–v20 → v21, danach Verzweigung v22 und Godot.

## Provenienzklasse

Gemini-Sekundärbericht vom 13.08.2026 über historischen v21/v22-Bestand und Godot-Abzweigung.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Interner Widerspruch: Abschnitt 3 sagt korrekt `kein WebGL`, die Schlussmatrix bezeichnet v21 dennoch als `Playwright WebGL / Screenshot-Runner`.
- Der dargestellte saubere Stammbaum v1–v20 → v21 → Zweige ist eine Synthese und braucht separate Provenienzbelege für jede Kante.
- `v1–v20 ... historisch belegt (Code in /flextrawurst/)` ist pauschaler als die in dieser Datei gezeigte Detailprüfung.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
