# Blender Evidence — Daniel/Savage 3D Detailpass

EVIDENCE_VERSION: 1
TASK: Die gespeicherte Daniel/Savage-Referenz als editierbaren 3D-Low-Poly-Charakter in Blender weiterentwickeln
INSTANCE: blender@5.0.1-38f3eb55
INSTANCE_ID: 38f3eb55-808b-4e66-8d23-3259ba049abf
GATEWAY: http://127.0.0.1:9765/mcp
REFERENCE: `/config/Desktop/VPS_ROOT/werkraum/refferenzen/Schrottplatz/daniel.png`
SCENE: `/config/Desktop/VPS_ROOT/werkraum/_codex/berichte/blender/Codex-Agent-Daniel-Savage.blend`

## Belegkette

- `baseline-detailpass.png`: unmittelbares Vorherbild vor dem sichtbaren Detailpass.
- `after-detailpass04.png`: Tasse, Kaffee/Rand, Maskennaht und Brustöffnung.
- `after-detailpass06.png`: helle Augenkerne und Diamant-Innenfläche.
- `after-detailpass07.png`: Fellbesatz-Fortsetzung und Gürtelknoten.
- `clean-final.png`: gespeicherter, bereinigter Front-Viewport vor der letzten Silhouettenpassage.
- `clean-detailpass08.png`: aktueller gespeicherter Front-Viewport mit dichterer Flammenkrone und Robenfalten.
- `short-legs-feet-connected.png`: aktueller Front-Viewport mit kurzen, am Saum angeschlossenen Beinen und Knubbelfüßen.
- `phase-01-mask-after.png`: sichtbarer Maskenpass mit goldenen Brauen-/Wangenakzenten.
- `phase-02-glory-render.png`: Road-to-Glory-Präsentationsbild nach isolierter Renderprüfung.
- `/tmp/codex-left-road-glory-pass03-after-clean.png`: Nachher-Viewport nach Recovery und sauberer Entselektion.
- `/tmp/codex-hair-gap-final.png`: Front-Viewport nach dem Haaransatz-Pass; die Lücke über der Maske ist geschlossen.
- `/tmp/codex-hair-root-final-front.png`: finale Front-Viewport-Prüfung nach dem zusätzlichen Wurzelfacetten-Pass.
- `/tmp/codex-animation-final-frame01.png`: gespeicherter Startframe nach dem Animationspass.
- `/tmp/codex-animation-frame24.png`: sichtbarer Schritt-Keyframe mit angehobenem linkem Bein.
- `/tmp/codex-animation-frame60.png`: sichtbarer Schritt-Keyframe mit übernehmendem rechtem Bein.
- `/tmp/codex-animation-large-final-frame01.png`: groß gerahmter gespeicherter Startframe nach der vergrößerten Schrittweite.
- `/tmp/codex-animation-large-frame24.png`: groß gerahmter linker Schritt mit deutlich weiterem Ausholen.
- `/tmp/codex-animation-large-frame60.png`: groß gerahmter rechter Schritt mit deutlich weiterem Ausholen.
- `comparison-matrix-3d-detailpass.md`: expliziter Referenzvergleich.
- MCP-Rücklese `id 418`: aktuelle linke Blender-Instanz, Scene-Datei und Objektstruktur.

## Begrenzte Mutationseinheiten

1. `detailpass_04`: bestehendes Mug-Objekt aufgerichtet; neue Rand-/Kaffee-, Naht- und Brustobjekte ergänzt.
2. `detailpass_05`: Becherrand als Bevel und vertikales SAVAGE-Label innerhalb der Tasse lesbar gemacht.
3. `detailpass_06`: Augenkerne und Diamant-Innenfläche ergänzt.
4. `detailpass_07`: separaten Fellbesatz und Gürtelknoten ergänzt.
5. `detailpass_08`: sieben Zwischenflammen und vier tiefe Robenfalten ergänzt.
6. `detailpass_09`: zwei kurze Beine, zwei Füße und zwei kleine Zehenknubbel ergänzt.
7. `detailpass_11`: Beine und Füße direkt unter den Mantelsaum verschoben; Auswahl aufgehoben.
8. `clean_view`: Originalreferenz und flache Pixelpässe bleiben erhalten und verborgen.
9. `road_to_glory_13`: separate Präsentationssammlung mit Glory-Kamera, Backdrop und Licht-Rig ergänzt; Originalmaterialien nach dem Render wiederhergestellt.
10. `road_to_glory_03`: Render-Isolation um Referenz-/Pixel-Layer erweitert, damit Beschriftungen nicht in den Beauty-Shot leaken.
11. `recovery_2026-09-05`: linker Blender-Prozess nach sauberem Recovery-Save neu geöffnet; rechter Claude-Prozess unangetastet.
12. `hairline_gap_15`: facettierte blaue Haarbasis als neues Objekt ergänzt und direkt gegen die bestehende Maske geprüft.
13. `hair_root_polish_16`: fünf kleine, abwechselnd cyan-/blaue Haarwurzelfacetten ergänzt; der Ansatz wurde danach erneut frontal gerahmt und gerendert.
14. `step_animation_17`: 81 bestehende Blockout-Objekte mit direkten Welttransform-Keyframes für eine 96-Frame-Schrittfolge animiert; kein Parenting und keine Referenzmutation.
15. `step_animation_stride_17b`: dieselbe Schrittfolge aus dem neutralen Frame 1 mit größerem Körperweg bis ±0,07 und deutlich größeren Beinwinkeln bis 42°/45° neu aufgebaut; die vergrößerte Frontansicht wurde separat geprüft.

## Prüfmarker

- BLENDER-EYE-001: UNKNOWN — Vorher-/Nachherbilder liegen vor; eine durchgehende 10-Hz-Trajektorie mit Cadence-Drift wurde für diese kurzen Pässe nicht aufgezeichnet.
- BLENDER-REF-001: PASS — Originalreferenz ist manifestiert, unverändert geladen und bleibt als eigene Blender-Sammlung erhalten.
- BLENDER-READ-001: PASS — finale Rücklese bestätigt die linke Instanz `38f3eb55`, Szene-Datei, Startframe 1, Endframe 96, `scene_modified: false`, 136 Objekte und 117 Meshes; 81 Blockout-Objekte tragen Animation, es gibt keine Blockout-Parentings, und die Referenzsammlungen sind vorhanden.
- BLENDER-ACT-001: PASS — alle Ergänzungen wurden als benannte Objekte in `DANIEL_SAVAGE_3D_BLOCKOUT` ausgeführt; keine bestehenden Referenzobjekte wurden gelöscht.
- BLENDER-QA-001: PASS — der groß gerahmte Frame 1 zeigt die vollständige Ausgangsfigur; Frame 24 hebt das linke Bein mit deutlich sichtbarem Ausholen, Frame 60 übernimmt sichtbar das rechte. Kopf, Körper, Tasse und Details bleiben jeweils zusammen; der Glory-Render bleibt ohne Referenzbeschriftung.

OUTCOME: PASS — editierbarer 3D-Detailstand ist in der linken Blender-Instanz gespeichert; pixelidentische 2D-Referenz und vollständige Rundum-Geometrie bleiben getrennte, ausdrücklich nicht behauptete Ziele.
