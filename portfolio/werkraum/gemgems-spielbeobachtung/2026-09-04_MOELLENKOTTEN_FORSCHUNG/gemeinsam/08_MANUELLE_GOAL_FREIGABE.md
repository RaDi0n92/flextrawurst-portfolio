# MANUELLE GOAL-FREIGABE

## /goal
Goal-Stufen werden niemals autonom freigeschaltet. Eine Session prüft ihre eigene Arbeit, dokumentiert den Prüfstand und hält danach an. Der nächste Goal-Abschnitt beginnt erst nach einer ausdrücklichen Freigabe durch Daniel und deren persistenter Eintragung in `../zustand/freigaben.jsonl`.

## Selbstprüfung
Die Session schreibt `SELBSTPRUEFUNG_BESTANDEN` oder `SELBSTPRUEFUNG_NICHT_BESTANDEN`. Diese Einschätzung schaltet nichts frei.

## Einziger Writer der Freigabeliste
`STEUERUNG` ist der einzige Writer von `../zustand/freigaben.jsonl`. Die praktische Rolle und der Aufrufweg stehen in `../steuerung/00_STEUERUNG.md` und `../werkzeuge/freigabe_schreiben.py`. Fachsessions, Gravity und Red-Team schreiben diese Datei nicht.

Für eine neue `FREIGEGEBEN`-Entscheidung muss vorher ein konkreter Startvorschlag in `../zustand/startvorschlag.json` stehen. Er benennt exakt Session und Goal. Daniels Zustimmung muss sich eindeutig auf diesen Vorschlag beziehen. Ein allgemeines „go“, das genauso gut einen Audit, Umbau oder anderen Arbeitsauftrag meinen kann, ist **keine** Goal-Freigabe.

`NICHT_FREIGEGEBEN` und `ZURUECKGENOMMEN` benötigen keinen Startvorschlag. Erst nachdem `STEUERUNG` die Entscheidung erfolgreich append-only persistiert hat, gilt sie für den Forschungsbetrieb als dauerhaft registriert.

Ein Freigabeereignis enthält `schema_version = 3`, `freigabe_id`, `session`, `goal_id`, `entscheidung`, `issued_by = DANIEL`, `persisted_by = STEUERUNG`, `issued_at`, `recorded_at` und `reference`.

## Aktueller Freigabestand
Die Dateireihenfolge in `../zustand/freigaben.jsonl` ist die verbindliche Reihenfolge. Für dieselbe Kombination aus Session und Goal gilt das letzte schema-valide Ereignis in der Datei. `issued_at` und `recorded_at` müssen RFC-3339-Zeitstempel sein, werden aber nicht benutzt, um die append-only Reihenfolge umzuschreiben.

Ohne ein aktuell wirksames `FREIGEGEBEN` beginnt die Session das Goal nicht.

## Gravity und Red-Team
Gravity und Red-Team können Prüfung, Nacharbeit oder Freigabe empfehlen. Sie persistieren keine Freigabe im Namen Daniels.

## Wenn Daniel nicht freigibt
Die Session bleibt beim aktuellen Goal und bearbeitet nur ausdrücklich angeforderte Nachprüfung, neue Belege oder Korrekturen dieses Goals. Sie beginnt keine Inhalte des nächsten Goals vorab.

## /goal-check
Die Goal-Stufe ist fachlich bereit zur Vorlage, wenn die Selbstprüfung vollständig dokumentiert ist. Der tatsächliche Übergang ergibt sich ausschließlich aus dem von `STEUERUNG` geführten `../zustand/freigaben.jsonl`.
