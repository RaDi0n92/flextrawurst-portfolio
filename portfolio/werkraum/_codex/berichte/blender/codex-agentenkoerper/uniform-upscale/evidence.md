# Blender Evidence — gleichmäßige Vergrößerung

EVIDENCE_VERSION: 1
TASK: Gesamten Codex-Agentenkörper inklusive Füße, Arme und Hände vergrößern
INSTANCE: blender@5.0.1-2803fcb6
INSTANCE_ID: 2803fcb6-74bc-4141-b805-f8a40d957821
GATEWAY: http://127.0.0.1:9765/mcp
MUTATION: `uniform_upscale_all` — 39 Objekte in `CODEX_AGENTENKOERPER`, Faktor 1.25, Welt-Pivot `(0, 0, 3.35)`

## Belegkette

- `baseline.png`: unmittelbares Vorherbild vor der Skalierung.
- `final.png`: unmittelbares Nachherbild nach der Skalierung; visuell geprüft.
- `after-state-response.json`: MCP-Rückgabe mit 42 Objekten nach der Aktion und finalem Viewport-Capture.
- `final-world-readback.json`: strukturierter Readback nach der letzten Mutation; Kernmaße steigen z. B. von `2.3 × 1.85 × 2.75` auf `2.875 × 2.3125 × 3.4375`.
- `../reference_manifest.yaml`: Referenz-Provenienz des Grundkörpers.
- `comparison-matrix.md`: Kriterienprüfung gegen die Referenz.

## Prüfmarker

- BLENDER-EYE-001: PASS — unmittelbares Vorher-/Nachherbild vorhanden und visuell geprüft; die synchrone Skalierung war ein kurzer Einzelschritt, eine kontinuierliche 10-Hz-Trajektorie wurde nicht benötigt/aufgezeichnet.
- BLENDER-REF-001: PASS — bestehender Referenzmanifest bleibt in-scope; Silhouette, Proportionen, Palette, negative humanoide Lesart und Framing sind verglichen.
- BLENDER-READ-001: PASS — finaler strukturierter World-Readback erfolgreich nach der Mutation; 42 Objekte, davon 39 im Codex-Körper.
- BLENDER-ACT-001: PASS — genau eine benannte Mutationseinheit `uniform_upscale_all` ausgeführt.
- BLENDER-QA-001: PASS — finaler Viewport zeigt den gesamten vergrößerten Körper samt Füßen, Armen und Händen vollständig; Materialien und Datenkörper-Stil bleiben erhalten.

OUTCOME: PASS — kompletter Codex-Agentenkörper live um 25% vergrößert; `.blend` weiterhin absichtlich ungespeichert.
