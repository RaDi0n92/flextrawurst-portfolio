# Stufe 2 + Stufe 3 umgesetzt: Koerper auf alle Werkstaetten generalisiert, echter Fenster-Manager

Nach Stufe 0 (Koerper-Format) und Stufe 1 (Posteingaenge) aus dem Plan "Gemeinsame Arbeit & Betriebssystem - echter Aufbau statt Huelle" jetzt Stufe 2 und Stufe 3 fertiggestellt und live im Browser verifiziert.

## Stufe 2: Koerper-Persistenz fuer alle 16 Nicht-Skizze-Werkstaetten

koerperSectionMarkup() nimmt jetzt einen posteingang-Parameter und zeigt fuer normale Werkstaetten "Körper"/"Öffnen" statt "Posteingang"/"Als Bauauftrag öffnen" - gleicher Mechanismus (Stufe-0-Ops koerper-save/-list/-load), nur andere Sprache je Kontext.

workbenchMarkup() zeigt die Koerper-Sektion fuer alle Replica-Typen ausser sketch (behaelt seine eigene Zeichenflaeche). Kein Backend-Schema noetig, da die Ops schon generisch ueber containerId+replicaId arbeiten.

Live getestet fuer zwei bisher nie genutzte Typen: cluster (Ideenraum, linear, 2 Knoten) und code (VS Code, echter Loop, 3 Knoten) - beide nach Speichern+Reload+erneutem Oeffnen exakt identisch (gleiche id). Regressionscheck bestanden: sketch unveraendert, Posteingaenge behalten ihre eigene Sprache.

## Stufe 3: echter Fenster-Manager

GKWindows (in workspace.js, laedt vor operating_shell.js/streams.js - kein neuer Backend-Restart noetig) ersetzt die drei "position:fixed;inset:0"-Vollbild-Overlays (Betriebssystem, Ordner & Dateien, Gemeinsame Arbeit) durch echte, an document.body gehaengte Fenster mit Titelleiste, Schliessen-Knopf, Ziehen per Maus, z-index-Fokusverwaltung. Ruehrt nie an nativen React-Elementen.

Behebt den seit der Plan-Pruefung bekannten Bug: das Betriebssystem-Overlay (z-index 100500) verdeckte die native Toolbar komplett, darunter auch den "Gemeinsame Arbeit"-Knopf. Jetzt bleibt die Toolbar immer erreichbar, alle drei Werkzeuge koennen gleichzeitig offen sein.

Live verifiziert: alle drei Fenster gleichzeitig offen ohne gegenseitige Verdeckung, Fokus-Wechsel per Titelleiste ODER per erneutem Klick auf den urspruenglichen Toolbar-Knopf (funktioniert wie eine Taskleiste), Ziehen verschiebt ein Fenster korrekt, Wechsel zwischen nativen Tabs bei offenen Fenstern loest keinen React-Absturz aus.

Damit sind alle vier Stufen des Plans umgesetzt.
