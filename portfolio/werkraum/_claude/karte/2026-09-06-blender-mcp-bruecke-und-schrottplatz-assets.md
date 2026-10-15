# Blender-MCP-Brücke und die Schrottplatz-Assets

Aufgenommen 2026-09-06. Bis dahin kam Blender in der Karte nicht vor, obwohl seit
dem 05.09. sechs 3D-Objekte darüber entstanden sind.

## Wo Blender läuft

Im Container `virtuellerdesktop1` auf Display `:1`. Gestartet wird eine Instanz mit
`DISPLAY=:1 blender <datei> --python /tmp/blender_mcp_startup.py`, das Startskript
aktiviert das Addon und öffnet den MCP-Server auf Port 9876.

**Wichtig:** Es laufen regelmäßig **zwei** Blender-Prozesse parallel — meiner und
Codex'. Vor jedem `kill` prüfen, welche PID zu welcher Datei gehört:

```bash
docker exec virtuellerdesktop1 bash -c 'ps aux | grep -i blender | grep -v grep'
```

Codex' Prozess erkennt man am Dateipfad `_codex/berichte/blender/`. Ihn zu beenden
würde fremde Arbeit zerstören.

## Die Brücke exponiert nicht alles, was das Addon kann

Das Addon (`blender_mcp_addon.py`) implementiert `ping`, `get_addon_info`,
`get_world_state_snapshot`, `get_object_info`, `execute_code` und mehr. Als eigene
MCP-Tools erreichbar sind bei Claude Code aber nur einige davon.

**Die fehlenden sind trotzdem nutzbar** — über die laufende Server-Instanz:

```python
server = bpy.types.blendermcp_server
snapshot = server.get_world_state_snapshot()
```

Der Snapshot liefert pro Objekt Location, Rotation, Scale, `aabb_min`/`aabb_max`,
Materialien und Mesh-Statistik in einem Aufruf — deutlich brauchbarer als
`get_scene_info`.

**Korrigierte Altannahme:** Ich hatte am 05.09. notiert, mir fehle dieser
Zustandsabruf und das erkläre einen Teil von Codex' Vorsprung. Das war falsch — es
fehlte nur der Zugriffspfad, nicht die Fähigkeit.

## Wie Modelle in den Schrottplatz kommen

Es gibt **keinen generischen Static-Mount**. Jedes Charaktermodell braucht drei
Dinge:

1. Die `.glb` unter
   `/root/werkraum/Mein-Gesamtkonstrukt-planer/static/models/`
2. Einen Eintrag in `CHARACTER_GLB_ALLOWED` in `server/planner_api.py`
3. Eine eigene Route in
   `/root/werkraum/WorldWORDS-ANTIBIBEL-Website/worldwords/urls.py`

Danach `kill -HUP $(pgrep -o -f 'gunicorn worldwords.wsgi')`.

Die URL im Spiel lautet `/Mein-Gesamtkonstrukt-planer/static/<datei>.glb` — **ohne**
`models/`, obwohl die Datei dort liegt. Der Pfad wird von der View aufgelöst, nicht
vom Dateisystem.

Das Spiel-JS liegt in `server/schrottplatz_babylon.js` (nicht in `static/` — die
Kopie dort ist eine Attrappe).

## Wo die Ergebnisse liegen

```
_claude/berichte/blender/GESAMTERFAHRUNG_BLENDER.md   Werkzeugfallen, Muster, Grenzen
_claude/berichte/blender/schrottplatz-autoscooter/    Bauplan + generischer Auditor
_backups/daniel_char_checkpoints/                     fünf Charakter-Stände
```

Der Auditor (`auditor.py`) ist **objektunabhängig** — nur der Bauplan ist spezifisch.
Für ein neues Objekt reicht ein neuer Knoten/Kanten-Graph.

## Was hier keine Maschine prüft

Der Auditor rechnet Beziehungen und Mindestmaße nach. Gestaltwirkung, Lesbarkeit und
Referenztreue kann er nicht beurteilen — er meldete "0 Verstöße", während ein Cockpit
unbenutzbar war und eine Flagge falsch herum wehte. Deshalb enthält jeder Bauplan eine
Liste `sichtpruefung`, die nach jedem Lauf mitgedruckt wird.
