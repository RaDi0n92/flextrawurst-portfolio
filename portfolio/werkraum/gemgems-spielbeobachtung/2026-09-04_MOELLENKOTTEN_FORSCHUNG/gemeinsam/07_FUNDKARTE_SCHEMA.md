# FUNDKARTE — GEMEINSAMES SCHEMA

## /goal
Jeder Fund soll klein genug sein, dass ein anderer Forschungspartner ihn unabhängig nachvollziehen, räumlich einordnen und später korrigieren kann. Der verbindliche Maschinenvertrag ist `../maschinenvertrag/DATENSCHEMA.json` in Schema-Version 3.

## Fundereignis
Ein Fundereignis enthält unter anderem `schema_version`, `ereignis_id`, `fund_id`, Lifecycle-Aktion, `object_ids`, `source_ids`, getrennte Statusachsen, Geometrie, Maße, Zeitbezug, Verknüpfungen, Widersprüche, offene Punkte und Merge-Status.

`object_ids` verbindet fachübergreifende Funde mit denselben kanonischen Objekten aus `../zustand/objektregister.jsonl`.

## Quellen sind eigene Objekte
Eine Quelle besitzt `source_id`, `origin_key`, Quelltyp, Ableitungsbeziehungen und gegebenenfalls Snapshot-Provenienz. Kanonische Quellen verwenden Kennungen wie `QUELLE-MOELLENKOTTEN-KANON-000001`.

Erlaubte Quelltypen sind:
- `EXTERNE_ORIGINALQUELLE`
- `EXTERNE_SEKUNDAERQUELLE`
- `DANIEL_ORTSKENNTNIS`
- `DANIEL_ERINNERUNG`
- `DANIEL_GRUNDRISS_ODER_ZEICHNUNG`
- `DANIEL_FOTO_ODER_BILD`
- `EIGENE_BEOBACHTUNG`

## Bestätigung
- `NICHT_GEPRUEFT`
- `EINZELBELEG`
- `MEHRERE_NICHT_UNABHAENGIGE_BELEGE`
- `UNABHAENGIG_BESTAETIGT`
- `WIDERSPROCHEN`

## Sicherheit
- `BESTAETIGT`
- `WAHRSCHEINLICH`
- `OFFEN`
- `WIDERSPRUECHLICH`
- `VERWORFEN`

## Weltstatus
- `REALITAETSBEHAUPTUNG`
- `SPIELERFINDUNG`
- `UEBERGANG_REAL_ZU_SPIELERFINDUNG`

Ein bestätigter Realitätsfund ohne Quelle ist schemawidrig. `UNABHAENGIG_BESTAETIGT` verlangt mindestens zwei Quellen; der Final-Auditor prüft zusätzlich, ob deren `origin_key` tatsächlich verschieden ist.

## Lokale Ablage
Eine Fachsession schreibt `sessions/<Session>/ausgabe/funde.jsonl`, `sessions/<Session>/ausgabe/quellen.jsonl` und `sessions/<Session>/ausgabe/wege.jsonl`. Korrekturen und Merge-Statuswechsel sind neue Lifecycle-Ereignisse und überschreiben keine alte Zeile.

## /goal-check
Eine Fundkarte ist verwendbar, wenn ein anderer Forschungspartner erkennen kann, was behauptet wird, auf welchen Quellen es beruht, welchem Objekt es gegebenenfalls zugeordnet ist, wo und wann es gilt und was offen bleibt.
