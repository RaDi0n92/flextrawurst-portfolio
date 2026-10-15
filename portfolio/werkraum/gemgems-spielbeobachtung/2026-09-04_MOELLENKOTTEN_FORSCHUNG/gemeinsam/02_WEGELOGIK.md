# GEMEINSAME WEGELOGIK — NICHT TELEPORTIEREN

## /goal
Alle Fachsessions sollen denselben räumlichen Körper untersuchen, auch wenn sie unterschiedliche Dinge darin sehen. Die Forschungsbewegung bleibt deshalb nachvollziehbar und räumlich verbunden.

## Startanker
Hauptstraße 151, 58332 Schwelm.

## Wegprinzip
Die Recherche führt vom Startanker über belegte reale Verbindungen nach außen. Jeder neue Straßenabschnitt, Fußweg, Durchgang oder erkennbare Pfad erzeugt einen offenen Rand, bis seine Fortsetzung untersucht oder begründet beendet wurde.

## Pro Wegabschnitt
Halte mindestens fest:
- stabile Wegabschnittskennung
- Startpunkt und Endpunkt oder offenes Ende
- Verbindungstyp
- Geometrie und räumliche Genauigkeit
- beide Wegseiten, soweit relevant
- Abzweigungen
- Höhenänderung und Messmethode, soweit bekannt
- Sichtachsen
- angrenzende Gebäude und Grünstrukturen
- Quellenkennungen
- offene Fragen

Das maschinenlesbare Format steht in `../maschinenvertrag/DATENSCHEMA.json` und `10_RAUM_ZEIT_UND_GODOT.md`.

## Abbiegen
Wenn eine reale Verbindung sichtbar oder belegt ist, kannst du von der aktuellen Route abbiegen. Dokumentiere die Abzweigung und kehre anschließend zum noch offenen Rand zurück. So verschwinden kleine Seitenwege nicht hinter bekannten Hauptstraßen.

## Sonderorte
Haus Martfeld, Klinikum und andere markante Orte können fachlich vorgezogen untersucht werden. Ihre Existenz ersetzt jedoch nicht die Verbindungskette vom Startanker dorthin.

## Nachbarschaftsgrenze
Bei `grenzstatus = ORIGINALVERIFIZIERT` endet die Vollaufnahme an der verifizierten Linie. Ist der Grenzstatus offen, erhalten Randfunde den Sachstatus `GRENZLAGE_UNGEKLAERT`; keine Session erfindet eine Linie.

## Raumstatus ist kein Goal-Status
Für einen Teilraum wird separat festgehalten, welche bekannten Anschlüsse untersucht und welche noch offen sind. Eine bestandene Selbstprüfung bedeutet nur, dass diese Dokumentation vollständig durchgeführt wurde.

## So prüfst du die Goal-Stufe
Prüfe jedes Kriterium im Format **Kriterium → Beleg → Ergebnis**. Wenn alle Kriterien erfüllt sind, setze `SELBSTPRUEFUNG_BESTANDEN`, sonst `SELBSTPRUEFUNG_NICHT_BESTANDEN`. Danach hältst du an; Daniels Freigabe bleibt separat.

## /goal-check
`SELBSTPRUEFUNG_BESTANDEN` setzt voraus, dass keine bekannte Abzweigung unmarkiert verschwunden ist und klar erkennbar bleibt, welche Forschungsränder noch offen sind. Das behauptet nicht, dass der Teilraum sachlich vollständig erforscht oder bereits baufähig ist.
