# Blender Evidence — Daniel/Savage-Pixelmatch

EVIDENCE_VERSION: 1
TASK: Daniels hochgeladene Referenz als pixelgenaue Zielansicht in Blender einrichten
INSTANCE: blender@5.0.1-2803fcb6
INSTANCE_ID: 2803fcb6-74bc-4141-b805-f8a40d957821
GATEWAY: http://127.0.0.1:9765/mcp
REFERENCE: `/config/Desktop/VPS_ROOT/werkraum/refferenzen/Schrottplatz/daniel.png`

## Belegkette

- `reference_manifest.yaml`: Originalquelle, Provenienz, Priorität und Toleranzen.
- `baseline.png`: unmittelbares Vorherbild des bisherigen Codex-Viewports.
- `final-viewport.png`: unmittelbares Nachherbild der kamerafesten Pixelmatch-Ansicht.
- `daniel-pixelmatch-render.png`: Blender-Render in exakt 1024×1536.
- `baseline-state-response.json`: Szenenzustand vor der Anlage.
- `final-scene-info-and-viewport-response.json`: MCP-Rücklese nach der Anlage und dem finalen Viewport-Capture.
- `final-world-readback.json`: strukturierter World-Readback nach der letzten Mutation.
- `comparison-matrix.md`: Referenzvergleich mit expliziten `UNKNOWN`-Grenzen.

## Begrenzte Mutationseinheiten

1. `create_pixelmatch_reference`: separate Sammlung mit unveränderter Bildfläche, Emission-Material und orthografischer Kamera angelegt; bisherige Sammlungen nur für diese Ansicht ausgeblendet.
2. `frame_pixelmatch_view`: aktive Viewport-Fläche auf die Pixelmatch-Kamera gesetzt und maximiert.
3. `clean_pixelmatch_view`: Auswahlkante und Overlays entfernt, ohne Geometrie zu löschen.
4. `render_pixelmatch`: 1024×1536-Render aus der Pixelmatch-Kamera erzeugt.

## Prüfmarker

- BLENDER-EYE-001: UNKNOWN — unmittelbare Vorher-/Nachherbilder und finaler Render sind vorhanden; für die 13-Sekunden-Rendertransition wurde keine vollständige 10-Hz-Trajektorie mit Cadence-Drift aufgezeichnet.
- BLENDER-REF-001: PASS — die von Daniel gelieferte Originalreferenz ist manifestiert und jedes relevante Vergleichskriterium hat einen Status.
- BLENDER-READ-001: PASS — finaler `get_scene_info`-Readback und World-Readback nach der letzten sichtbaren Aktion; 44 Objekte, aktive Kamera `Daniel__Savage__PixelmatchCamera`.
- BLENDER-ACT-001: PASS — Referenzfläche, Framing, Bereinigung und Render wurden als benannte, begrenzte Aktionen ausgeführt.
- BLENDER-QA-001: PASS — die finale Ansicht und der 1024×1536-Render zeigen die Referenz visuell vollständig; Byte-identische Renderwerte und eine rundum-3D-Rekonstruktion bleiben ausdrücklich `UNKNOWN`.

OUTCOME: PASS — pixelgenaue kamerafeste Referenzansicht live in der linken Blender-Instanz eingerichtet; `.blend` absichtlich noch nicht gespeichert.
