# Data model / Datenmodell / Modelo de datos

## Deutsch

`terms/` enthält nur Daniels offizielles Register. `proposals/` enthält öffentlich sichtbare, noch nicht aufgenommene Beiträge. `approvals/` enthält Daniels datierte Entscheidungen. `provenance/events.jsonl` ist append-only: Korrekturen erzeugen neue Ereignisse, statt alte Herkunft unsichtbar zu überschreiben. Jede Sprachfassung besitzt eigene Übersetzungsprovenienz.

## English

`terms/` contains only Daniel’s official registry. `proposals/` contains public contributions not yet admitted. `approvals/` stores Daniel’s dated decisions. `provenance/events.jsonl` is append-only: corrections create new events instead of silently overwriting origin history. Every language version carries separate translation provenance.

## Español

`terms/` contiene únicamente el registro oficial de Daniel. `proposals/` contiene contribuciones públicas todavía no admitidas. `approvals/` guarda las decisiones fechadas de Daniel. `provenance/events.jsonl` es append-only: las correcciones crean eventos nuevos en vez de sobrescribir silenciosamente la historia. Cada versión lingüística incluye su propia procedencia de traducción.
