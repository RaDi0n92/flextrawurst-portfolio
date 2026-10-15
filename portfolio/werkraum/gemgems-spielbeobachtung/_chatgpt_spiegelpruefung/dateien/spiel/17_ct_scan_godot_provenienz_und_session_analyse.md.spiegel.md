# Spiegelprüfung — `spiel/17_ct_scan_godot_provenienz_und_session_analyse.md`

## Quellenidentität

- Original: `/root/werkraum/gemgems-spielbeobachtung/spiel/17_ct_scan_godot_provenienz_und_session_analyse.md`
- Snapshot-SHA256: `09280834e432dbeb81966c18ccb62ba04ce8a9232998a4f87ce16deae32dcf9a`
- Bytes: 5543
- Zeilen: 60
- Snapshot-mtime: `2026-08-13T07:43:24.336612+00:00`

## Prüfstatus

- ORIGINAL UNVERÄNDERT: JA
- SEMANTISCHE PRÜFUNG DURCH CHATGPT: ABGESCHLOSSEN
- BIS EOF SEMANTISCH GEPRÜFT: JA
- AUSSAGENREGISTER: AUSGEFÜLLT
- PROVENIENZPRÜFUNG: AUSGEFÜLLT
- WIDERSPRÜCHE/UNSICHERHEITEN: AUSGEFÜLLT

## Leseabdeckung / Chunk-Fingerprints

- Zeilen 1–60: `51bdf66f9cf529b14d84c02b32c3a7cdaa7f2da6181fa88dd9a46f38cf5e9da7` | semantisch: GEPRÜFT

## Was die Datei tatsächlich aussagt

- Rekonstruiert Godot-Entstehung über Session, Zeitstrom, Git und Portbelegung.
- Trennt Daniels Rohinput vom späteren ChatGPT-Paraphrasieren. Daniels zitierter Impuls: eine echte Game-Engine an GPT/ChatGPT ankoppeln; zusätzlich `we do that mthfker`.
- Datierung: Session `chatgpt-20260725T081538Z-00b7a2e74c94`; Schreibereignis für `asset_manifest.json` laut Zeitstrom 25.07.2026 08:21:50 UTC.
- Trennt Git-Autor `Daniel <daniel@local>` von logischer Code-Erzeugung durch GPT-5.6-sol-hoch.
- Dokumentiert eine 51-Minuten-Kollision: Commit `2d38ec91...` trägt 07:30:05 UTC, derselbe Commit wird vom MCP-Zeitstrom an einen tatsächlichen Schreibvorgang um 08:21:50 UTC gebunden. Ursache offen.
- Stellt klar: dieser erste Commit erzeugte nur `data/asset_manifest.json`; `project.godot`, `main.tscn`, `main.gd`, `world_bridge.gd` werden erstmals im Backup-Commit `4255bd...` um 14:06:55 UTC sichtbar.
- Beschreibt Godot als eigenständigen neuen GDScript-Prototyp, nicht als Portierung von v21.
- Erklärt Port 18092 als kollisionsfreien High-Port neben 8090/8091.

## Wichtige Rohformulierungen / Zahlen / Pfade / Daten

- Daniel-Rohtext: `gibts nix was ich nutzen kann unm ne echte gameengine zusammen an gpt zu kleben ... wichtig es muz zu catgpt wandern`.
- Zeitkollision: 09:30:05 CEST Git-Metadatum vs. 10:21:50 CEST MCP-Schreibereignis.

## Provenienzklasse

Gemini-Provenienzbericht vom 13.08.2026 mit direkter Session-/Zeitstrom-/Git-Referenzierung.

## Widersprüche / Unsicherheiten / Nicht bewiesene Sprünge

- Der Bericht unterscheidet korrekt Git-Erstauftreten und logische Sessionprovenienz.
- Der Backup-Commit ist nur die erste nachvollziehbare Git-Spur der Projektdateien, nicht zwingend deren physischer Erstellungszeitpunkt.
- Die Ursache der 51-Minuten-Anomalie ist ausdrücklich ungeklärt und darf nicht harmonisiert werden.
- `Godot 4.3` beschreibt Ziel/Projektkontext; installierte Engineversion historischer Läufe ist eine separate Frage.

## Abschlussmarker

`SPIEGEL_SEMANTISCH_ABGESCHLOSSEN = JA`
