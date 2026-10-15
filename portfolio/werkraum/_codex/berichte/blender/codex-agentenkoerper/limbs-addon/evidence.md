# Blender Evidence — Knubbelfüße und minimale Arme/Hände

EVIDENCE_VERSION: 1
TASK: Knubbelfüße sowie minimale Arme und Hände zum Codex-Agentenkörper ergänzen
INSTANCE: blender@5.0.1-2803fcb6
INSTANCE_ID: 2803fcb6-74bc-4141-b805-f8a40d957821
GATEWAY: http://127.0.0.1:9765/mcp

## Belegkette

- `baseline.png`: Vorherbild vor der Ergänzung.
- `after-feet.png`: unmittelbares Nachherbild nach den Füßen.
- `after-arms-hands.png`: unmittelbares Nachherbild nach Armen und Händen.
- `final.png`: Nachherbild nach dem finalen vollständigen Framing.
- `final-scene-info.json`: MCP-Szeneninventar nach der letzten Aktion.
- `final-world-readback.json`: strukturierter Readback nach der letzten Aktion.
- `../reference_manifest.yaml`: Referenzen und Provenienz des Grundkörpers.
- `comparison-matrix.md`: Kriterienprüfung dieser Ergänzung.

## Begrenzte Mutationseinheiten

1. `knubbelfuesse`: zwei Fußkörper und zwei Zehenknubbel ergänzt; Auswahl danach gelöst.
2. `minimal_signal_arms`: zwei kurze Kurvenarme, zwei Handflächen und vier Fingerknubbel ergänzt; Auswahl danach gelöst.
3. `frame_full_agent_with_limbs`: ausschließlich Viewport-Zentrum und Abstand angepasst, damit alle Anhänge sichtbar sind.

## Prüfmarker

- BLENDER-EYE-001: PASS — Vorher-/Nachherbilder für Füße, Arme/Hände und finales Framing vorhanden; die Operationen waren kurz und wurden unmittelbar visuell geprüft. Eine kontinuierliche 10-Hz-Trajektorie ist für den synchronen Kleinschritt nicht aufgezeichnet.
- BLENDER-REF-001: PASS — bestehender Referenzmanifest bleibt in-scope; die Ergänzungskriterien sind vollständig in der Vergleichsmatrix erfasst.
- BLENDER-READ-001: PASS — `get_scene_info` meldet 42 Objekte, darunter 8 neue Limb-Elemente; finaler World-Readback erfolgreich nach der letzten Aktion.
- BLENDER-ACT-001: PASS — Füße, Arme/Hände und Framing wurden als drei benannte, begrenzte MCP-Aktionen ausgeführt.
- BLENDER-QA-001: PASS — finale Sichtprüfung zeigt beide Füße, beide Arme und beide Hände vollständig; Stil und nicht-humanoide Silhouette bleiben erhalten.

OUTCOME: PASS — gewünschte Knubbelfüße und minimale Arme/Hände live ergänzt; `.blend` weiterhin absichtlich ungespeichert.
