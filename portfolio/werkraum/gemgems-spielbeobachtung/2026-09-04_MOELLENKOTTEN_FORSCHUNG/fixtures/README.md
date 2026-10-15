# Fixtures

`workflow_valid.json` bildet einen kleinen zusammenhängenden Version-2-Workflow aus lokalen Quellen, Merge-Statuswechseln, kanonischen Quellen, Objekt, Fund, Route, Grenze, Freigabe und Inbox-Nachricht ab.

`schema_invalid_cases.json` enthält absichtlich ungültige Einzelereignisse. Der Final-Auditor muss den gültigen Workflow akzeptieren und jeden ungültigen Fall ablehnen. Zusätzlich erzeugt der Auditor semantische Mutationen des gültigen Workflows für gebrochene Referenzen, doppelte Ereigniskennungen, falsche Quellenunabhängigkeit, ungeschlossene Polygone und Snapshotfehler.

Der gültige Workflow referenziert außerdem `sessions/01_STRASSEN_UND_GEWEGE/snapshots/FIXTURE_ONLY_SNAPSHOT.txt` mit echter SHA256-Prüfung. Damit wird ein positiver Snapshot im realen Session-Namespace geprüft, nicht nur `null` oder Negativfälle.
