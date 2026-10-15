# Beitragen

## Der kürzeste Weg

1. Öffne ein Issue mit der Vorlage **Neuer Begriff**.
2. Trage die Rohform exakt ein. Nicht korrigieren.
3. Nenne Einreicher, mutmaßlichen Urheber und Unsicherheiten getrennt.
4. Füge Datum, Kontext, Originalwortlaut und eine veröffentlichbare Quelle hinzu.
5. Erkläre den Begriff auf Deutsch, Englisch oder Spanisch. Weitere Sprachen sind willkommen.
6. Markiere ausdrücklich, was der Begriff nicht bedeutet.
7. Reiche einen Pull Request mit einer Datei unter `data/proposals/` ein.

## Mindestfelder

- `id`
- `raw_form`
- `submitted_by`
- `authorship_status`
- `first_seen`
- `exact_input`
- `source_ref`
- `definitions`
- `status: submitted`

## Was danach passiert

Technische Prüfungen kontrollieren Schema, IDs, Quellenfelder, Datumsformat und versehentliche Geheimnisse. Anschließend kann Herkunftsarbeit folgen. Erst Daniel kann den Status für das offizielle Register auf `accepted` setzen und den zugehörigen Entscheidungsbeleg anlegen.

## Korrekturen

Bitte alte Herkunftsangaben nicht einfach ersetzen. Reiche ein neues Provenienzereignis mit `event_type: correction` ein und verweise auf das fehlerhafte Ereignis.

## Übersetzungen

Übersetze Erklärungen, Grenzen und Beispiele. Die Rohform bleibt erhalten. Eine neue Wortform in einer anderen Sprache ist ein eigener Vorschlag, keine gewöhnliche Übersetzung.

## Rechte

Mit einem Beitrag bestätigst du, dass du ihn unter den im Repository genannten Lizenzen veröffentlichen darfst. Vollständige fremde Chatverläufe, Bücher, Artikel oder private Nachrichten ohne Erlaubnis gehören nicht hier hinein.
