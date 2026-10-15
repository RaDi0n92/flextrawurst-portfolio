# Stufe 0 umgesetzt: Koerper-Format (gkos.koerper.v1)

Nach dem gemeinsam erarbeiteten Plan (siehe Gespraech "Gemeinsame Arbeit & Betriebssystem - echter Aufbau statt Huelle") mit Stufe 0 begonnen: das eigenstaendige Koerper-Format, getrennt von state.objects/edges.

Umgesetzt in server/planner_api.py, nach demselben Muster wie die bestehenden sketch-element/replica-action-Ops:

- koerper-list (GET): scannt <container>/Koerper/*.json, liefert Kurzinfo fuer die Uebersicht (kein separates Index-File - direktes Scannen vermeidet eine zweite Datenquelle, die aus dem Takt geraten koennte, gleiche Lehre wie bei provenanceRequired weiter unten).
- koerper-load (GET): liest einen vollstaendigen Koerper per id.
- koerper-save (POST): legt neu an ODER ueberschreibt bei bekannter id dieselbe Datei - das ist der eigentliche Unterschied zu replica-action (das immer eine neue Datei anlegt) und die Grundlage fuer "gleicher Koerper nach Neuladen".

Kernstueck: _validate_koerper_sequence. Die Knoten-Reihenfolge wird IMMER aus dem Kantengraphen hergeleitet (Traversierung ab startNodeId), nie vom Client uebernommen - ein flacher Index waere bei einer Schleife irrefuehrend (welcher Knoten ist "0"? die Ruecklaufkante verschwindet, genau der Fund aus der Plan-Pruefung). sequence.type ist ein echter Struktur-Check statt Deko: "loop" nur bei echtem, alle Knoten umfassendem Zyklus, "linear" nur bei einem einzigen Pfad ohne Verzweigung, "freeform" ueberspringt die Pruefung bewusst. Bewusste Lehre aus diesem Codebase: replica_containers.json's format.provenanceRequired wird nirgends geprueft - genau dieses "Feld sieht aus wie ein Vertrag, ist aber nie validiert"-Muster wollten wir hier nicht wiederholen.

Koerper werden bewusst NICHT in state.objects/edges gespiegelt (anders als sketch-element/replica-action/note) - eigenstaendiges Format mit eigener Logik, kein Alias fuer das bestehende Objekt-Modell, wie von Daniel explizit gefordert.

Verifiziert: 10 Testfaelle fuer _validate_koerper_sequence isoliert (ohne Django-Kontext) ausgefuehrt - linear gueltig, linear-aber-schliesst-faelschlich, loop gueltig, loop-dead-end, loop-unvollstaendig, Verzweigung abgelehnt, freeform akzeptiert Verzweigung, unbekanntes Kantenziel abgelehnt, doppelte Knoten-IDs abgelehnt, Einzelknoten-Snapshot - alle zehn bestanden. py_compile fehlerfrei.

Noch offen: Live-Verifikation der drei neuen Endpunkte selbst steht aus. planner_api.py wird von einem laufenden Gunicorn-Prozess (worldwords-antibibel.service) importiert und laedt Code-Aenderungen nicht automatisch nach - braucht einen Dienst-Neustart. Bei Daniel angefragt, noch keine Antwort zum Zeitpunkt dieser Notiz.

Committet.
