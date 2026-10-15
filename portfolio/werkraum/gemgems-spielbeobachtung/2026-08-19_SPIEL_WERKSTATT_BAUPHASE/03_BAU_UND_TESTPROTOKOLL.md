# Bau- und Testprotokoll · Spiel-Werkstatt · 2026-08-19

## Gebauter Körper

Pfad:
`/root/werkraum/engine/godot-vertical-slice/workshop_20260819/`

Runtime-Daten:
`/root/werkraum/engine_runtime/godot-vertical-slice/workshop_20260819/`

Dienst:
`flextrawurst-spiel-werkstatt.service`

Lokaler Bind:
`127.0.0.1:18119`

Der Körper ist bewusst als neue isolierte Schicht angelegt; bestehende Godot-Glue-/Runtime-Dateien wurden für diesen Bau nicht überschrieben.

## Bereits ausführbar

- Browseroberfläche mit frei wechselbaren Ansichten ohne feste Mitte.
- Aktuelle Spielkörper-Auswahl folgt zwischen Ansichten.
- Mehrere Kontexte können im Browser angepinnt werden.
- Hierarchische reale Erstidentitäten: Casino → Gordslider-Keimkammer → Gordslider.
- Reale zugehörige Quellpfade können aus der Werkstatt gelesen werden.
- Vorhandene Verkörperungen werden pro Identität angezeigt.
- Historische Versionen können angezeigt und angepinnt werden.
- Historische Ansicht ist ausdrücklich als alt/schreibgeschützt markiert.
- Eigener Arbeitszustand pro Akteur.
- Bewusst gemeinsamer Arbeitszustand (`shared=true`) mit mehreren Akteuren.
- Änderungen in Arbeitszuständen besitzen noch keine Weltwirkung.
- Explizites Speichern erzeugt eine neue Version und erhält die Vorversion.
- Speicherung schreibt Akteur, Zeitpunkt, Herkunft, Nachricht, Parent-Version, Changed-Fields und Snapshot-Hash.
- Wenn der gemeinsame Spielkörper seit Eröffnung des Arbeitszustands unabhängig verändert wurde, werden unabhängige Top-Level-Änderungen automatisch gemerged.
- Kollidieren beide Arbeitsstände auf demselben Feld mit verschiedenen Werten, wird ein persistenter Konflikt erzeugt und Save mit HTTP 409 abgebrochen. Kein Last-Write-Wins.
- Geschützte Entwürfe werden separat persistent gespeichert mit `protected=true` und `world_effect=false`.
- Append-only Werkstatt-Änderungsereignisse liegen in `events.jsonl`.
- 3D-Ansicht zeigt reale bekannte Godot-Verkörperungen und behauptet ausdrücklich keinen Webexport, solange keiner existiert.

## Initial eingezogene belegte Identitäten

1. `ORT_WUPPERTAL_CASINO_0001`
2. `GORDSLIDER_KEIMKAMMER_0001`
3. `OBJEKT_GORDSLIDER_0001`

Sie sind Einstiegspunkte, keine Behauptung, der gesamte Altbestand sei bereits als Werkstatt-Identitätsgraph migriert.

## Technische Tests

### Python-Syntax

`python3 -m py_compile workshop_20260819/server.py`

Ergebnis: PASS.

### JavaScript-Syntax

Erster Lauf fand real einen Fehler: ungeescapte Backticks im 3D-Statustext verursachten `SyntaxError: Unexpected token '.'`.

Fehler wurde gezielt korrigiert.

Danach:

`node --check workshop_20260819/app.js`

Ergebnis: PASS.

### API-/Persistenz-Roundtrip in isolierter Test-Runtime

Testdatei:
`workshop_20260819/test_roundtrip.py`

Geprüft:
1. Arbeitszustand ändern → aktuelle Welt bleibt unverändert.
2. Explizit speichern → neue Version entsteht, Vorversion bleibt.
3. Zwei Arbeitszustände auf gleicher Basis ändern unabhängige Felder → automatischer Merge.
4. Zwei Arbeitszustände ändern dasselbe Feld verschieden → HTTP 409 `real_conflict`, keine stille Entscheidung.
5. Geschützter Entwurf → `world_effect=false`, Weltversion unverändert.

Ergebnis:
`PASS workshop roundtrip: workstate/save/version/merge/conflict/protected-draft`

### Browser-Smoke mit Playwright

Testdatei:
`workshop_20260819/test_ui_smoke.mjs`

Geprüft:
- Seite lädt real im Chromium,
- aktuelle Auswahl funktioniert,
- Wechsel auf Eigenschaften,
- Arbeitszustand über UI erzeugen,
- Arbeitszustand über UI verwerfen,
- Dateiansicht enthält reale Quellen,
- 3D-Ansicht zeigt vorhandene Godot-Verkörperung,
- 3D-Ansicht markiert ehrlich, dass aktuell kein `.html/.wasm`-Webexport vorliegt.

Ergebnis:
`PASS UI smoke: selection/tabs/workspace/discard/files/3D-truth-status`

## Aktueller Dienststatus

Am 2026-08-19 21:24 CEST:
- `flextrawurst-spiel-werkstatt.service` enabled,
- active/running,
- Python-Prozess,
- etwa 10–11 MB RAM beim Start,
- `/api/health` antwortet `status=ok`.

## Bewusst noch nicht behauptet

- Kein Godot-Webexport gebaut.
- Keine browserfähige Ersatz-/Erweiterungsbridge für 18092 gebaut.
- Noch kein vollständiger Import aller Spielobjekte/Dateien/Quellen in stabile Identitäten.
- Kontextinjektor für alle AI-Ströme ist noch nicht als ausführbares Gesamtsystem verdrahtet.
- Noch keine fertige öffentliche/authentifizierte Browserroute für die neue Werkstatt dokumentiert.

Diese Punkte bleiben real offen und dürfen nicht durch UI-Text als fertig erscheinen.
