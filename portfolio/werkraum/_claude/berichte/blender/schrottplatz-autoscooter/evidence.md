# Evidence — Autoscooter v1 (echter Codex-Skill-1:1-Durchlauf)

Diesmal tatsaechlich mit den in SKILL.md genannten Tools gearbeitet, nicht nur
mit dem Vokabular. Zugriff auf `ping`/`get_addon_info`/`get_world_state_snapshot`
ueber `bpy.types.blendermcp_server` direkt aus `execute_blender_code` (Fund vom
2026-09-06, siehe `/config/.claude/skills/blender-live-reference-qa/CLAUDE-BRIDGE-NOTIZ.md`).

BLENDER-EYE-001: PASS — nach jeder Baugruppe (Wanne+Ring, Sitz, Lenkrad, Grill+
Scheinwerfer, Ruecklichter+Mast) ein Screenshot gezogen, keine Luecke.
BLENDER-REF-001: PASS — `reference-manifest.yaml` vor dem ersten Bauschritt
committet, alle Kriterien mit Status.
BLENDER-READ-001: PASS — nach jeder Mutation `server.get_world_state_snapshot()`
aufgerufen und `aabb_min`/`aabb_max` der neuen Objekte gegen die erwartete
Position geprueft, nicht nur Screenshot vertraut.
BLENDER-ACT-001: PASS — jede Baugruppe einzeln, keine Batch-Skripte mit
mehreren unabhaengigen Anbauteilen in einem Aufruf.
BLENDER-QA-001: UNKNOWN — bisher kein einzelner struktureller Bug im Bauprozess
selbst aufgetreten (anders als beim Bagger), daher noch kein "echter Fund"
dieser Session zu berichten. Wird nachgetragen falls einer auftritt.

## Handshake (Skill-Schritt 1, wirklich ausgefuehrt)

```
ping -> {'status': 'ok'}
get_addon_info -> {'name': 'MCP for Blender', 'addon_version': [1, 6],
                    'protocol_version': 5,
                    'capabilities': ['drain_human_activity', 'execute_code',
                    'get_addon_info', 'get_object_info', 'get_scene_info',
                    'get_telemetry_consent', 'get_viewport_screenshot',
                    'get_world_state_snapshot', 'set_telemetry_consent'],
                    'blender_version': '5.0.1'}
get_scene_info (leere szene) -> {'object_count': 0}
```

## Vergleichsmatrix

| Kriterium | Referenzfakt | Beobachtung | Delta | Status | naechste Aktion |
|---|---|---|---|---|---|
| Ovale Wanne auf Stossring | Durchgehender Gummiring, Wanne sitzt direkt darauf | Torus (Ring) + skalierter Zylinder (Wanne), aabb bestaetigt: Wanne-Boden Z=0.18 = Ring-Oberkante Z=0.18, kein Spalt | keins | PASS | — |
| Ledersitz + Lehne, seitlich versetzt | Sitz nimmt ca. 40% der Laenge ein, nicht exakt zentral | Sitzbasis+Lehne bei X=-0.15 bis -0.55, auf Wannenoberkante (Z=0.53) aufsitzend | keins strukturell | PASS | — |
| Lenkrad vorne-mittig | Torus-Lenkrad mit Saeule, leicht geneigt | Saeule+Lenkrad bei X=0.32-0.58, Neigung 0.9rad, per Seitenscreenshot bestaetigt sichtbar ueber der Wanne | keins | PASS | — |
| Front-Grill mit 2 Scheinwerfern | Gittergrill, 2 runde warme Lichter symmetrisch | Grill-Platte + 2 Scheinwerfer-Zylinder (Emission), symmetrisch Y=+-0.3, per Screenshot warmes Gelblicht sichtbar | keine Gitter-Textur, nur Platte | PASS (Form+Licht) / UNKNOWN (Gitter-Textur) | Gitter-Struktur als Detailschritt |
| 2 rote Ruecklichter am Heck | Runde Rotlicht-Elemente symmetrisch am Heck | 2 Zylinder mit rotem Emission-Material, symmetrisch Y=+-0.32, Heck-X bestaetigt | keins | PASS | — |
| Fahnenmast + Flagge am Heck | Hoher duenner Mast mit rechteckiger schwarzer Flagge, Totenkopf-Aufdruck | Mast (Zylinder, Hoehe bis Z=1.63) + Flagge (duenne schwarze Platte) am Mast-Oberende | Kein Totenkopf-Aufdruck/Text (Textur fehlt) | PASS (Form) / UNKNOWN (Aufdruck) | Text/Bild-Textur auf Flagge als eigener Schritt |
| SCHROTTPLATZ KING Schriftzug | Auf der Seitenflanke der Wanne, lesbar von aussen | Text-Objekt ergaenzt, nach mehreren Rotationsversuchen rechtsherum stehend und von aussen (Welt +Y, ueber BACK-Achsenansicht bestaetigt) sichtbar | Position/Ausrichtung PASS. Ob die Buchstaben spiegelverkehrt sind, konnte ich per Screenshot bei dieser Aufloesung NICHT sicher beurteilen -- ehrlich als offen markiert statt geraten | PASS (Position/Aufrecht) / UNKNOWN (Spiegelung) | Naeher heranzoomen oder Rendertest mit groesserer Aufloesung fuer eindeutige Spiegel-Pruefung |
| Rostiges Blech-Finish | Durchgehend verwittert, genietet, keine glatten Flaechen | Basis-Rostbraun-Material gesetzt, aber einheitliche Flachfarbe ohne Verwitterungs-Variation/Nieten | Grundfarbe PASS, Textur/Detail fehlt | PASS (Grundfarbe) / UNKNOWN (Verwitterung/Nieten) | Normal-Map/Bump oder manuelle Nietendetails spaeter |
| Rundum-Silhouette (Front/Heck/Seite/Oben) | 8 Referenzwinkel vorgegeben | Alle 4 Hauptachsen gegengeprueft: RIGHT=Front (2 Scheinwerfer symmetrisch), LEFT=Heck (2 Ruecklichter symmetrisch + Mast), TOP=Draufsicht (korrekte Symmetrie beider Lichtreihen + Lenkrad/Sitz-Position bestaetigt). Fund: Blender-Achsen FRONT/BACK zeigen bei diesem Fahrzeug (Laengsachse=X) eine Seitenansicht, nicht Front/Heck -- RIGHT/LEFT muessen fuer echte Front/Heck-Ansicht verwendet werden. | keins mehr (Achsenverwechslung war rein visuell, keine Geometrie betroffen) | PASS | — |

## Nicht getan (bewusst offen, kein Auftrag)

- Kein Export/Deploy in den laufenden Schrottplatz.
- Kein Gittertextur/Nieten-Detailpass.
- Kein Textaufdruck (SCHROTTPLATZ KING, Flaggentext) umgesetzt -- reine Formen bisher.
- Ruecken- und Draufsicht noch nicht einzeln mit dem Referenzbild abgeglichen.
