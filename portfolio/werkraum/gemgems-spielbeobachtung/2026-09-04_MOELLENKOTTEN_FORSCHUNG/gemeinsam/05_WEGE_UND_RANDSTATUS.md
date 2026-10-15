# WEGE- UND RANDSTATUS

## /goal
Alle Fachsessions sollen denselben räumlichen Forschungsfortschritt sehen. Offene Seitenwege und ungeklärte Anschlüsse bleiben sichtbar.

## Lokale und kanonische Wege
Eine Fachsession schreibt eigene Wegereignisse nur nach `sessions/<Session>/ausgabe/wege.jsonl`. Gravity prüft diese und übernimmt tragfähige Ereignisse append-only nach `../zustand/wegekarte.jsonl`.

## Maschinenlesbarer Wegabschnitt
`route_event` enthält mindestens:
- `wegabschnitt_id`, Start- und Endbezug und Verbindungstyp
- Geometrie und räumliche Genauigkeit
- `source_ids`
- `object_ids` und `related_fund_ids`
- bekannte und offene Abzweigungen
- Grenzereignis-Verknüpfungen
- linke und rechte Objektseite
- Sichtachsen als verknüpfte Fundkennungen
- strukturierte Maße für Breite, Höhe, Gefälle oder andere Messwerte
- offene Punkte
- `source_date`, `observed_at` und `valid_time`
- Sachstatus und Merge-Status

Damit können historische und aktuelle Wegzustände getrennt geführt werden.

## Offener Rand
Ein offener Rand ist eine belegte Verbindung, deren Fortsetzung noch nicht untersucht wurde. Er bleibt sichtbar, bis er untersucht, als nicht weiterführend belegt oder durch eine verifizierte Gebietsgrenze begrenzt wurde.

`known_branch_refs` verweist auf bereits bekannte Wegabschnittskennungen. `open_branch_refs` darf auch vorreservierte, noch nicht angelegte Wegabschnittskennungen enthalten und wird deshalb bei der Referenzintegrität anders behandelt.

## Räumliche Reihenfolge
Nahe offene Ränder rund um Hauptstraße 151 werden bevorzugt geschlossen. Weiter entfernte Sonderorte können fachlich vorgezogen werden, werden aber nicht als räumlich angeschlossen behandelt, solange die Verbindungskette fehlt.

## /goal-check
`SELBSTPRUEFUNG_BESTANDEN` für die Dokumentation eines Teilraums bedeutet: Alle bekannten Anschlüsse sind entweder untersucht oder ausdrücklich als offener Rand dokumentiert. Dieser Goal-Status ist kein Reifegrad des Teilraums.
