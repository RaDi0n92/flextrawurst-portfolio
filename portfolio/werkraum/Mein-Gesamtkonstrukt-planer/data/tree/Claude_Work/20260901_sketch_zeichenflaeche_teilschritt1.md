# Sketch-Werkstatt: Zeichenflaeche, Teilschritt 1

Teilschritt gemaess Ansage "nach jedem Teilschritt eine Notiz, nicht erst am Ende" (Daniel, 2026-09-01).

- Backend (server/planner_api.py): sketch-element-Erstellung um geometry (dict) und groupId (string|null) erweitert. Neue Operation sketch-element-update: liest ein bestehendes Element per Pfad, mergt geometry/groupId, schreibt atomar zurueck, aktualisiert das verknuepfte Objekt im State.
- Frontend (server/operating_shell.js): echte SVG-Zeichenflaeche in der Sketch-Werkstatt. Stift/Form/Pfeil bewaffnen ein Werkzeug, Ziehen auf der Flaeche erzeugt echte Geometrie und speichert per sketch-element. Klick waehlt aus, Shift-Klick fuer Mehrfachauswahl, Ziehen auf Auswahl verschiebt (persistiert per sketch-element-update). Gruppe-Button setzt bei mindestens zwei ausgewaehlten Elementen eine gemeinsame groupId. Elemente ohne Position (Altbestand) werden separat gelistet mit einem Platzieren-Button.
- Beide Dateien syntaxgeprueft (py_compile, node --check), beide gruen.

Noch offen: Backend-Aenderung ist noch nicht live, Gunicorn-Neustart von worldwords-antibibel steht aus (Freigabe angefragt). Noch kein Live-Test im echten Browser, kein Reload-Test.
