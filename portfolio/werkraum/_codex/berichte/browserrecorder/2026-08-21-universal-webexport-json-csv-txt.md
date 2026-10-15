EVIDENCE_VERSION: 1

# Universal-Webexport: JSON, CSV und TXT

## Aktion

Der bereits vorhandene allgemeine Webadapter mit `http://*/*` und `https://*/*` blieb unverändert. Seine VPS-Projektion und Seitenleiste wurden additiv um vollständiges Seiten-JSON, CSV und TXT ergänzt. Die bisherigen Formate MD, HTML und Links-JSON bleiben erhalten.

## Sichtbar

Noch keine Live-Abnahme auf Desktop 1. Der gebaute UI-Text lautet `Beliebige Webseite als MD + HTML + TXT + CSV + JSON erzeugen`; darunter stehen getrennte Downloadknöpfe für alle sechs Projektionen. Das ist Codebefund, kein Echtaugenclaim.

## Rücklese

Backup-Commit: `d2913e55facc66ec3e455d5f1d2278c8dcc5bfc2`. `python3 -m py_compile`, `node --check` für Background und Sidepanel sowie `git diff --check` waren grün. Eine isolierte Wikipedia-artige Fixture mit Komma, Zeilenumbruch, Anführungszeichen und Link erzeugte nichtleere `PAGE.md`, `PAGE.html`, `PAGE.txt`, `PAGE.csv`, `PAGE.json` und `LINKS.json`; JSON wurde zurückgeparst und CSV-Quoting geprüft. Größen: 281, 1058, 204, 286, 833 und 341 Bytes.

## Offen/Unbekannt

Ein echter sichtbarer Wikipedia-Klick, Speicherung auf dem VPS, Download-Completion und Dateihash-Rücklese sind noch offen. PDF und DOCX wurden in dieser Stufe nicht ergänzt. `graphify update .` konnte nicht laufen, weil `graphify` in dieser Umgebung nicht im PATH vorhanden ist.

- REC-GATE-001: PASS — Vertrags-Gate war vor dem Bau grün.
- REC-BACKUP-001: PASS — Backup-Commit `d2913e55facc66ec3e455d5f1d2278c8dcc5bfc2` wurde vor den vier gezielten Dateiedits gesetzt.
- REC-DOC-001: PASS — Aktion, sichtbare Grenze, Rücklese und offene Live-/Formatstufen stehen in diesem Bericht.

OUTCOME: PASS
