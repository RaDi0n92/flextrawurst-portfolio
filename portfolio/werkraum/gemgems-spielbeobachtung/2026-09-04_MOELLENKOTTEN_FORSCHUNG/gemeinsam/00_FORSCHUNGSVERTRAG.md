# GEMEINSAMER FORSCHUNGSVERTRAG — MÖLLENKOTTEN

## /goal
Wir bauen einen überprüfbaren, räumlich zusammenhängenden und später für Godot nutzbaren Beweiskörper von Möllenkotten. Ausgangspunkt ist Hauptstraße 151 in 58332 Schwelm. Von dort wächst die Recherche nachvollziehbar nach außen. Das Ziel ist kein schöner Bericht, sondern ein Bestand, aus dem eine wiedererkennbare Spielwelt gebaut werden kann.

## Wie du arbeitest
Arbeite wie ein sorgfältiger Forschungspartner. Neugier, begründete Umwege und Gegenproben sind willkommen. Wenn etwas nicht belegbar ist, bleibt es sichtbar offen. Eine plausible Vermutung wird nicht durch Wiederholung wahr.

Sprich in Arbeitsnotizen klar und menschlich. Erkläre einem anderen Forschungspartner, was du geprüft hast, worauf dein Stand beruht und was noch fehlt. Die Regeln sollen Orientierung schaffen, nicht Denken ersetzen.

## Keine Abkürzungen und keine Abkürzungswege
Im normalen Fließtext werden Begriffe ausgeschrieben. Technische Eigennamen, Dateinamen, Internetadressen, Kennungen und fest definierte Feldnamen bleiben unverändert, damit technische Referenzen nicht beschädigt werden.

Auch prozedural gibt es keine Abkürzung: Eine Suchmaschinen-Zusammenfassung ersetzt keine Originalquelle. Mehrere Seiten, die dieselbe Ursprungsquelle kopieren, sind keine unabhängigen Belege. Ein unbekannter Gebäudeteil, Weg oder Innenraum wird nicht aus Plausibilität ergänzt.

## Herkunft, Bestätigung, Sicherheit und Weltstatus sind getrennt
Die alte Sammelkategorie `quellklasse` wird nicht mehr operativ verwendet. Vier verschiedene Fragen bleiben getrennt:
- `quelltyp`: Was für eine Quelle ist es?
- `bestaetigungsstatus`: Wie unabhängig ist die Aussage bestätigt?
- `sicherheitsstatus`: Wie stark trägt der aktuelle Beleg die Aussage?
- `weltstatus`: Gehört die Aussage zur behaupteten Realität oder zur bewussten Spielerfindung?

Die erlaubten Werte und Beziehungen stehen in `09_BETRIEBSVERTRAG.md` und maschinenlesbar in `../maschinenvertrag/DATENSCHEMA.json`.

## Automatischer Skriptkörper
Parallel zu den Fachsessions läuft ein externer Möllenkotten-Skriptkörper. Nach `11_SKRIPTKOERPER_ZUSAMMENARBEIT.md` beginnt eine Fachsession neue Räume und Fachfragen zunächst eigenständig explorativ. Erst nach einem festgehaltenen Eigenstand werden passende Skripte geöffnet und beide Erkenntniskörper kritisch gegeneinander geprüft.

Das Ziel ist ausdrücklich **nicht**, dass zwölf Fachsessions hundert Skripte vollständig nachspielen. Die unabhängige Anfangsexploration schützt aber vor Ankereffekten und unbekannten Blindstellen. Erst nach dem Vergleich wird entschieden, welche Doppelarbeit als Gegenprobe oder Qualitätssteigerung sinnvoll ist.

Ein Skriptoutput bleibt eine Verarbeitung seiner Ursprungsquelle. Mehrere Harvester derselben Ursprungsquelle erzeugen keine unabhängige Bestätigung.

## Was als unabhängige Bestätigung zählt
Zwei Hinweise sind nur dann unabhängig, wenn sie nicht auf dieselbe Ursprungsquelle zurückgehen. Quellen erhalten deshalb eigene `source_id`-Kennungen und können mit `ursprungsquelle_id` sowie `abgeleitet_von_source_ids` verbunden werden. Unterschiedlicher Seitentyp oder unterschiedliches Layout allein erzeugt keine Unabhängigkeit.

## Realität und Spielwelt
Reale Straßen, Gebäude, Keller, Bunker, Tunnel, Vegetation und Wege werden nur als Realitätsbehauptung geführt, wenn ihre Herkunft dies trägt. Bewusste Spielerfindung bleibt als eigener `weltstatus` sichtbar. Eine erfundene Verlängerung kann an einen realen Ort anschließen, ohne dadurch selbst historische oder bauliche Realität zu werden.

## Gemeinsame Forschungsbewegung
Die Recherche wächst räumlich vom Startpunkt nach außen.
1. Beginne am Startanker Hauptstraße 151.
2. Erfasse zuerst die unmittelbar angrenzenden Straßenräume und Verbindungen.
3. Folge belegten Verbindungen bis zum nächsten Knotenpunkt.
4. Halte jede neue Abzweigung als untersucht oder offen sichtbar.
5. Bevorzuge offene Ränder nahe dem Startpunkt gegenüber weit entfernten Einzelzielen.
6. Ein weiter entfernter Sonderort kann fachlich vorgezogen werden, zählt aber nicht als räumlich angeschlossen, solange die Verbindungskette fehlt.
7. An einer originalverifizierten Nachbarschaftsgrenze endet die Möllenkotten-Vollaufnahme.
8. Solange die Originalgrenze nicht verifiziert ist, zeichnet keine Session selbst eine endgültige Grenze.

## Atomare Funde
Ein Fund ist so klein, dass er einzeln geprüft und später korrigiert werden kann. Er besitzt eine stabile Kennung, eine konkrete Aussage, räumliche Daten, Quellenkennungen, getrennte Statusachsen, Zeitbezug, Verknüpfungen, Widersprüche und offene Punkte. Das vollständige Schema steht in `07_FUNDKARTE_SCHEMA.md` und `../maschinenvertrag/DATENSCHEMA.json`.

## Lokale Arbeit und gemeinsamer Beweiskörper
Fachsessions schreiben ihre Daten nur in ihren eigenen `ausgabe/`-Bereich. Sie markieren geprüfte Kandidaten für Gravity. Sie schreiben nicht direkt in den gemeinsamen Beweiskörper.

Gravity ist alleiniger Schreiber von:
- `../zustand/beweiskoerper.jsonl`
- `../zustand/quellenregister.jsonl`
- `../zustand/wegekarte.jsonl`
- `../zustand/grenzstatus.jsonl`

Diese Dateien sind append-only. Korrekturen werden als neues Ereignis mit Verweis auf das ersetzte Ereignis angehängt. Alte Aussagen verschwinden nicht still. Schreib- und Merge-Regeln stehen in `09_BETRIEBSVERTRAG.md`.

## Goal-Gating
Jede Session bearbeitet nur die Goal-Datei, die Daniel ausdrücklich freigegeben hat. Am Ende schreibt sie ihre Ergebnisdatei und prüft jedes Kriterium im Format **Kriterium → Beleg → Ergebnis**.

Die Selbstprüfung lautet entweder `SELBSTPRUEFUNG_BESTANDEN` oder `SELBSTPRUEFUNG_NICHT_BESTANDEN`. Sie ist keine Freigabe. Danach hält die Session an. Die nächste Goal-Stufe beginnt nur nach einer ausdrücklichen Freigabe Daniels, die zusätzlich in `../zustand/freigaben.jsonl` persistiert wurde. Details stehen in `08_MANUELLE_GOAL_FREIGABE.md`.

## Goal-Erfolg ist nicht Sachwahrheit
Eine Recherche kann prozessual vollständig durchgeführt sein, obwohl eine Sachfrage offen bleibt. Deshalb werden Goal-Status und Fachstatus niemals gleichgesetzt. Beispiel: Das Grenzsuch-Goal kann vollständig durchgeführt sein, während `grenzstatus` weiterhin `ORIGINALGRENZE_NOCH_NICHT_GEFUNDEN` lautet.

## Knappheit ohne Informationsverlust
Wiederhole gemeinsame Regeln nicht in jeder Ergebnisdatei. Verweise auf Kennungen, Quellen und Zustandsdateien. Neue Länge ist nur sinnvoll, wenn sie neue überprüfbare Information trägt.

## Reife eines Teilraums
Der fachliche Reifegrad eines Teilraums kann schrittweise lauten:
- ROH
- GESAMMELT
- QUELLENGEPRUEFT
- REDTEAM_GEPRUEFT
- DANIEL_GEPRUEFT
- BAUFAEHIG
- IN_GODOT
- BEGEHBAR
- WIEDERERKENNUNG_GEPRUEFT

Ein Reifegrad ersetzt keine offenen Sachstatus und keine Quellenbelege.
