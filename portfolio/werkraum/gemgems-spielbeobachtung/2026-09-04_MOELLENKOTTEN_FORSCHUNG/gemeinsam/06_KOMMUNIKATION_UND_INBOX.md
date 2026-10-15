# KOMMUNIKATION UND INBOX

## /goal
Sessions sollen sich gegenseitig helfen können, ohne sich gegenseitig zu überschreiben. Hinweise bleiben konkret, begründet und als einzelne Nachrichten nachvollziehbar.

## Kanonischer Ort
Nachrichten liegen als einzelne JSON-Dateien unter `../kommunikation/inbox/<Empfaenger>/`. Jede Nachricht entspricht `$defs.message` aus `../maschinenvertrag/DATENSCHEMA.json` und trägt `schema_version = 3`.

## Empfängerkennungen
Erlaubt sind `S01` bis `S12`, `GRAVITY`, `REDTEAM01`, `REDTEAM02` und `STEUERUNG`. Sender und Empfänger werden vom Maschinenvertrag auf genau diese Kennungen begrenzt.

## Inhalt
Eine Nachricht enthält stabile Nachrichtenkennung, Absender, Empfänger, RFC-3339-Erstellungszeit, Betreff, betroffene Kennungen, Beobachtung, Relevanz, Belegkennungen und gewünschte Prüfung.

## Ton
Formuliere wie gegenüber einem kompetenten Forschungspartner. Eine Nachricht gibt Orientierung, nicht Gehorsamsbefehle.

## Zuständigkeit
Ein fachfremder Fund bleibt ein Hinweis. Die zuständige Session entscheidet, wie sie ihn prüft und einordnet. Niemand übernimmt fremde Aussagen ungeprüft in den gemeinsamen Beweiskörper.

## /goal-check
Kommunikation ist gelungen, wenn der Empfänger ohne Rückfrage versteht, worum es geht, warum es relevant ist und welche Prüfung noch fehlt.
