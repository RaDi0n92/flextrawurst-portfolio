# FINAL-AUDIT V3 — MÖLLENKOTTEN

**Stand UTC:** 2026-09-18T09:06:05.268717+00:00
**Forschungsroot:** `/root/werkraum/gemgems-spielbeobachtung/2026-09-04_MOELLENKOTTEN_FORSCHUNG`
**Dateien:** 161
**Schema-Version:** 3
**Korpus-SHA256:** `ba1d17d7eb22e19e0ed241ea7f7f642ef3cd3c1f47ebc982726ff5bed770eee9`

## Prüftiefe
Der Audit prüft Schema, reale Speicherorte und Writer, Session-Kennungsräume, linearen append-only Lifecycle, kanonische Merge-Ursprünge, aktive Evidenz, Quellen-Ahnen-Graph, Snapshot-Wurzel und Hash, Objekt-/Fund-/Routen-/Grenz-/Freigabereferenzen, Zeitrelationen, Kalibriervertrag, Goal-Vorlagen und Paket-relevante Pflichtverzeichnisse.

## Ergebnisse
- **OK — Session-Mapping:** 12 eindeutige Code↔Ordner-Zuordnungen
- **OK — Gesamtfingerprint:** ba1d17d7eb22e19e0ed241ea7f7f642ef3cd3c1f47ebc982726ff5bed770eee9
- **OK — Dateizahl:** 161
- **OK — DATENSCHEMA:** Draft 2020-12 gültig, Version 3
- **OK — JSONL-Ereignisse:** 8
- **OK — Raumkalibrierung:** schema-valid: NICHT_KALIBRIERT
- **OK — Semantische Integrität:** 8 Live-Ereignisse und 0 Inbox-Nachrichten ohne erkannte Verletzung
- **OK — Sessionordner:** exakt die 12 gemappten Sessions
- **OK — Pflichtverzeichnisse:** 30 vorhanden
- **OK — Goal-Vorlagenparität:** 48/48 bytegleich
- **OK — Skriptkörper-Statusschema:** 100 Skripte im gespeicherten Snapshot
- **OK — Skriptkörper-Sessionmapping:** 12/12 Fachsessions vorhanden
- **OK — Skriptkörper-Sessionkerne:** 12/12 exploration-first, Live-Vergleich, Unknown-Output und Read-only verdrahtet
- **OK — Skriptkörper-Goalvorlagen:** 4/4 exploration→freeze→compare→deepen; Goal03 mit Unknown-unknown-Pass
- **OK — Skriptkörper-Zuständigkeit:** 100% mit Fachzuständigkeit oder expliziter Oversight-Rolle
- **OK — Skriptkörper-Gravity:** Statusaufsicht und Grenztrennung vorhanden
- **OK — Skriptkörper-RedTeam:** beide Red-Teams greifen Automatisierungsblindstellen an
- **OK — Gravity-Betriebszyklus:** Aufsicht/Staffelprüfung/Empfehlung sind wiederverwendbare, freigabegesteuerte Zyklen
- **OK — Startvorschlag-Schema:** state=NONE; proposal=None
- **OK — Freigabe-Guard:** FREIGEGEBEN benötigt passenden persistenten Startvorschlag
- **OK — Leitstellenstatus:** Freigaben, Startvorschlag und Skriptstatus konsistent abgeleitet
- **OK — Skriptreife-Trennung:** semantische Reife bleibt ohne SHA-Manifest UNKNOWN
- **OK — Skriptlauf-Trennung:** Laufstatus bleibt ohne Maschinenmanifest UNKNOWN
- **OK — Aktive Freigabe-Provenienz:** alle aktuell wirksamen FREIGEGEBEN-Zustände sind Proposal-gebunden; derzeit 0
- **OK — Exploration-first Regression:** keine alte script-first-Arbeitsanweisung in den zentralen Verträgen
- **FEHLER — Markdown-Referenzen:** steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> freigabe_schreiben.py; steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> leitstellenstatus.json; steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> werkzeuge/leitstelle_status.py; steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> zustand/leitstellenstatus.json
- **OK — Historische Audit-Einordnung:** im Forschungsroot vorhanden
- **OK — Fixture gültiger Workflow:** 16 zusammenhängende Ereignisse akzeptiert
- **OK — Fixture ungültige Schemafälle:** 10/10 abgelehnt
- **OK — Fixture semantische Negativtests:** 15/15 absichtliche Semantik-/Speicherfehler erkannt
- **OK — Fixture Kalibrierung:** positiver KALIBRIERT-Zustand schema-valid
- **OK — Python-Syntax:** alle Python-Werkzeuge parsebar

## Fehler
- Markdown-Referenzen: steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> freigabe_schreiben.py; steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> leitstellenstatus.json; steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> werkzeuge/leitstelle_status.py; steuerung/03_META_PREMORTEM_REDTEAM_REVIVE_2026-09-18.md -> zustand/leitstellenstatus.json

## Warnungen
Keine.

## Grenze
Leere Live-JSONL bleiben eine reale Grenze: Der Betriebsvertrag ist technisch und adversarial getestet, aber ein echter Forschungsdurchlauf mit realer Quelle, Snapshot, Korrektur, ZUR_PRUEFUNG, Gravity-Merge, Inbox und Daniels persistierter Freigabe ist der nächste empirische Beweis.
