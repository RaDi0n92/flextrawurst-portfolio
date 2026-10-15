# BETRIEBSVERTRAG — SPEICHER, KENNUNGEN, MERGE UND SCHREIBRECHTE

## /goal
Dieser Vertrag legt fest, wo Daten liegen, wer sie schreiben darf und wie Korrekturen, Quellenidentität und Zusammenführungen funktionieren. Er soll Konflikte verhindern, nicht zusätzliche Bürokratie erzeugen.

## Kanonische gemeinsame Speicherorte
- `../zustand/beweiskoerper.jsonl` — geprüfte Fundereignisse
- `../zustand/quellenregister.jsonl` — geprüfte kanonische Quellenereignisse
- `../zustand/wegekarte.jsonl` — geprüfte Wegereignisse
- `../zustand/objektregister.jsonl` — kanonische Objektidentitäten
- `../zustand/grenzstatus.jsonl` — Grenzereignisse
- `../zustand/freigaben.jsonl` — Daniels manuelle Goal-Freigaben
- `../zustand/raumkalibrierung.json` — Koordinaten- und Godot-Kalibrierung
- `../zustand/SPAWNHAUS_REFERENZSTAND.md` — von Gravity erzeugte kanonische Spawnhaus-Synthese, sobald Material dafür reicht

`JSONL` bedeutet genau ein vollständiges JSON-Objekt pro Zeile. Ereignisdateien sind append-only.

## Schema-Version
Alle neuen Ereignisse tragen `schema_version = 3`. Da beim Übergang auf Version 3 alle Forschungs-JSONL weiterhin leer waren, existieren keine unveränderlichen Version-1-Ereignisse, die migriert werden müssten. Eine spätere Schemaänderung bekommt eine neue Versionsnummer; alte Ereignisse werden dann nach ihrer eigenen Version validiert oder durch einen ausdrücklich dokumentierten Migrationsschritt behandelt.

## Lokale Sessionausgabe
Jede Fachsession besitzt ihren eigenen Schreibraum:
- `sessions/<Session>/ausgabe/funde.jsonl`
- `sessions/<Session>/ausgabe/quellen.jsonl`
- `sessions/<Session>/ausgabe/wege.jsonl`
- `sessions/<Session>/snapshots/`
- ihre eigenen `ERGEBNIS_*.md`

Eine Fachsession schreibt nicht direkt in kanonische Zustandsdateien und nicht in die Ausgabe einer anderen Session.

## Schreibrechte
- Fachsessions: eigener Sessionordner, eigener Snapshot-Ordner und eigene Inbox-Nachrichten.
- Gravity: kanonischer Beweiskörper, Quellenregister, Wegekarte, Objektregister, Grenzstatus, kanonische Quellensnapshots, Spawnhaus-Referenzstand, aktueller `../zustand/skriptkoerper_status.json`, eigene Ergebnisse und Nachrichten.
- Red-Team: eigener Ergebnisbereich und Nachrichten; keine kanonischen Wahrheitsdateien.
- `STEUERUNG`: alleiniger Writer von `../zustand/freigaben.jsonl`.

## Append-only und Ereignis-Lifecycle
Bestehende Ereigniszeilen werden nicht verändert oder gelöscht.
- `ANLEGEN`: erstes Ereignis einer Sachkennung; `ersetzt_ereignis_id = null`.
- `INHALT_KORRIGIEREN`: inhaltliche Korrektur; verweist auf das ersetzte Ereignis.
- `MERGE_STATUS_AENDERN`: ausschließlich ein append-only Statusübergang wie `LOKAL` zu `ZUR_PRUEFUNG`; verweist auf das ersetzte Ereignis.
- `VERWERFEN`: verwirft einen früheren Stand; verweist auf das ersetzte Ereignis.

Grenzereignisse verwenden dieselbe Lifecycle-Semantik.

## Merge von Session zu Gravity
1. Die Fachsession legt lokal ein Ereignis mit `merge_status = LOKAL` an.
2. Nach eigener Prüfung erzeugt sie ein neues Ereignis mit `aktion = MERGE_STATUS_AENDERN`, `merge_status = ZUR_PRUEFUNG` und `ersetzt_ereignis_id` auf den lokalen Vorgänger.
3. Gravity prüft Quellenursprung, räumliche Logik, Statusachsen, Kennungen und Widersprüche.
4. Bei Annahme erzeugt Gravity im kanonischen Speicher ein neues `ANLEGEN`-Ereignis mit `merge_status = KANONISCH` und verweist über `origin_event_ids` auf die lokalen prüfreifen Ereignisse.
5. Bei Ablehnung bleibt der lokale Bestand erhalten; Gravity meldet den Grund über die Inbox.

## Kennungsräume
### Sessionlokal
- Fund: `FUND-MOELLENKOTTEN-S01-000001`
- Quelle: `QUELLE-MOELLENKOTTEN-S01-000001`
- Wegabschnitt: `WEGABSCHNITT-MOELLENKOTTEN-S01-000001`

Die Sessionnummer wird entsprechend angepasst. Der sechsstellige Zähler einer Sachkennung wird innerhalb einer Session nicht für einen anderen Sachgegenstand wiederverwendet. Mehrere Lifecycle-Ereignisse dürfen dieselbe Sachkennung tragen, aber jedes `ereignis_id` ist global eindeutig.

### Kanonisch durch Gravity
- Objekt: `OBJEKT-MOELLENKOTTEN-000001`
- Quelle: `QUELLE-MOELLENKOTTEN-KANON-000001`
- Grenze: `GRENZE-MOELLENKOTTEN-000001`

Gravity vergibt kanonische Objektkennungen früh, sobald mehrere Fachsessions dieselbe reale Entität referenzieren müssen. Funde tragen dafür `object_ids`. Das Objekt selbst wird append-only in `../zustand/objektregister.jsonl` geführt.

## Quellenidentität und Deduplizierung
Jede Quelle besitzt zusätzlich `origin_key`. Dieser beschreibt den tatsächlichen Ursprung unabhängig von lokaler Sessionkennung, beispielsweise eine normalisierte Originaladresse oder eine stabile Kennung für Daniels bereitgestelltes Material.

Beim Merge prüft Gravity `origin_key` gegen das kanonische Quellenregister. Existiert derselbe Ursprung bereits, wird keine zweite kanonische Quelle erfunden. Stattdessen wird die vorhandene kanonische `source_id` wiederverwendet und die lokale Quellenkennung über `alias_source_ids` nachvollziehbar verbunden.

`ursprungsquelle_id` und `abgeleitet_von_source_ids` halten Ableitungsbeziehungen fest. Unterschiedliche Seiten mit derselben Ursprungsquelle zählen nicht als unabhängige Bestätigung.

## Snapshots
Lokale Sessions speichern gesicherte Quellenkopien ausschließlich unter ihrem echten Sessionordner `sessions/<voller Sessionordner>/snapshots/`. Die Zuordnung von `S01` bis `S12` zu diesen Ordnern steht kanonisch in `../maschinenvertrag/SESSIONEN.json`. Gravity kann beim kanonischen Merge eine geprüfte Kopie nach `../zustand/quellen_snapshots/` übernehmen.

`snapshot_path` ist relativ zum Forschungsroot und darf nur in diesen vorgesehenen Snapshot-Wurzeln liegen. Wenn `snapshot_sha256` gesetzt ist, müssen Datei und Hash zusammenpassen. Nach Pfadauflösung muss der Snapshot weiterhin innerhalb genau der für diese Quelle erlaubten Snapshotwurzel liegen; `../..` darf diese Wurzel nicht verlassen. Der Final-Auditor prüft Existenz, Pfadsicherheit und Prüfsumme.

## Statusachsen bleiben getrennt
`quelltyp`, `bestaetigungsstatus`, `sicherheitsstatus`, `weltstatus`, Goal-Status, Grenzstatus und Raumreife werden nicht ineinander umgedeutet.

## Nachrichten statt Fremdschreiben
Sessions greifen nicht in fremde Ergebnisdateien ein. Hinweise gehen als eigene JSON-Nachricht nach `../kommunikation/inbox/<Empfaenger>/`.

## Maschinenvertrag
Feldtypen, Pflichtfelder, Kennungsmuster, Zeitformate und bedingte Invarianten stehen in `../maschinenvertrag/DATENSCHEMA.json`. Der Final-Auditor prüft zusätzlich Referenzintegrität und Beziehungen, die ein einzelnes JSON-Schema nicht vollständig beurteilen kann.
