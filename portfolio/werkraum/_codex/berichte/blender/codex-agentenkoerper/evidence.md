# Blender Evidence — Codex-Agentenkörper

EVIDENCE_VERSION: 1
TASK: Nicht-humanoides Abbild der Agentenfigur für ein agentic OS im Flextrawurst-Stil
INSTANCE: blender@5.0.1-2803fcb6
INSTANCE_ID: 2803fcb6-74bc-4141-b805-f8a40d957821
GATEWAY: http://127.0.0.1:9765/mcp

## Belegkette

- `baseline-viewport.png`: Vorherbild der unveränderten Blender-Standardszene.
- `final-viewport.png`: Nachherbild nach der letzten Marker-Korrektur; visuell geprüft.
- `final-scene-info.json`: MCP-Szeneninventar nach der letzten Mutation.
- `final-world-readback.json`: strukturierter Transform-, Bounding-Box- und Material-Readback nach der letzten Mutation.
- `reference_manifest.yaml`: Referenzen, Provenienz, Prioritäten und Toleranzen.
- `comparison-matrix.md`: Kriterienprüfung gegen die Referenz.

## Begrenzte Mutationseinheiten

1. `core`: `Codex__Agentenkern__DEMO` und `Codex__InnererPuls__LIVE` in `CODEX_AGENTENKOERPER` angelegt.
2. `membrane`: drei geneigte Membranringe und zehn lokale Signalpunkte ergänzt.
3. `signal_skin`: drei Datenströme, sechs Signal-Knoten und zwei Herkunftsmarker ergänzt.
4. `data_shell`: äußere Drahtmembran als feines Datenraster ergänzt.
5. `frame_agent_view`: Auswahl gelöst, Viewport auf den Körper zentriert und Default-Kollektion nur im Viewport ausgeblendet.
6. `align_labels_to_view` / `restore_visible_labels`: Marker zur sichtbaren Ansicht ausgerichtet und nach Rücklese minimal korrigiert.

## Prüfmarker

- BLENDER-EYE-001: UNKNOWN — unmittelbares Vorher-/Nachherbild pro Bauabschnitt ist vorhanden; eine separate 10-Hz-Trajektorie mit Cadence-Drift wurde für diesen synchronen Aufbau nicht aufgezeichnet.
- BLENDER-REF-001: PASS — alle drei in-scope Referenzen sind im Manifest erfasst und jedes relevante Kriterium hat einen Vergleichsstatus.
- BLENDER-READ-001: PASS — `get_scene_info` und strukturierter World-Readback wurden nach der letzten Mutation erfolgreich ausgeführt.
- BLENDER-ACT-001: PASS — jede Geometrie-/Ansichtsänderung wurde als benannte, begrenzte MCP-Skriptaktion ausgeführt.
- BLENDER-QA-001: UNKNOWN — die Form liegt innerhalb der aus den Referenzen abgeleiteten Kriterien; eine konkrete Figurenreferenz oder Daniels abschließende Stilabnahme liegt noch nicht vor.

OUTCOME: PASS — erster verwendbarer Codex-Agentenkörper live in der linken Blender-Instanz; `.blend` absichtlich noch nicht gespeichert.
