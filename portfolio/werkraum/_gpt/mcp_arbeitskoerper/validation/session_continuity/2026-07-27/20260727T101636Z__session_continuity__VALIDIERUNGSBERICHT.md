# Validierungsbericht: Globale MCP-Session-Kontinuität

## Status

**BESTANDEN.**

Der alte Altvertrag „history_startup erzeugt bei Bedarf eine neue Session-ID“ wurde ersetzt. Jeder UI-Chat und Arbeitsfaden behält nun seine eigene kanonische MCP-Session über erneute Einwahl, F5 und Zeitabstand hinweg.

## Produktivbeweis

- kanonische Session: `chatgpt-20260726T143158Z-8232ef805b68`
- sichtbarer Marker: `[SESSION-KONTINUITAET: FORTGESETZT chatgpt-20260726T143158Z-8232ef805b68]`
- `generated_session_id`: **false**
- versehentliche Kurzsession geschlossen: `chatgpt-20260727T095030Z-8b10e5e7b65a`
- Schließereignis: `422c6b67-29ad-4a47-a827-f46b60c9af4d`
- produktiver VPS-MCP: `active/running`
- Werkzeuge: **148**
- Schemas im produktiven `tools/list`: **korrekt**

## Harte Regeln

- Fortsetzung ist Standard.
- Ohne bekannte kanonische ID wird keine neue Session erfunden.
- Neue Arbeitslinie nur mit `session_intent="new"` und `new_session_reason`.
- Geschlossene Sessions werden nicht still ersetzt.
- Parallele UI-Chats behalten getrennte IDs.
- Die global zuletzt aktive Session wird nie automatisch als Ersatz gewählt.
- `history_begin_session` ist kein Hintereingang mehr; der Grund ist Pflicht.

## Tests

- **32 Tests bestanden**
- isolierter produktiver Katalogtest bestanden
- Lifecycle-Rennverschluss bestanden
- systemd-Unitprüfung bestanden
- produktive Wiederaufnahme derselben ID bestanden

## Herkunft

- Commit: `30bc3b9600316e00ac0e39074f05ffce95d37c25`
- Vertrag: `/root/werkraum/_gpt/mcp_global_protocols/session_continuity_v1.json`
- Vertragshash: `6db30d08ece967709b4e3996cbc2cac9977d76baf407493d8b035f24af75942a`
