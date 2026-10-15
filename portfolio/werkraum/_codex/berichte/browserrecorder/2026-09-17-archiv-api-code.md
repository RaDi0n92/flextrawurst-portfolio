# Archiv-API-Zugangsschutz — Quellcode-Stufe

EVIDENCE_VERSION: 1

## Aktion

Zwölf Archiv-API-Routen in `/root/werkraum/welt/api.py` mit aktuellem Admin- oder bestehendem Schlüsselzugang geschützt. 18 zugehörige Aufrufe in `/vps_root/flextrawurst/scripts/build_surface.ts` verwenden einen auf dieselbe Origin und Archivpfade begrenzten Helfer.

## Sichtbar

Keine Browser-Abnahme. Kein Surface-Build, kein Dienstneustart und keine Live-Fetches mit Schlüsseln durchgeführt. Diese Stufe bewertet ausschließlich Quellcode und isolierte Tests.

## Rücklese

Fünf Backendtests in `/root/werkraum/tests/test_archive_access.py` und zwei Node-Tests in `/vps_root/flextrawurst/tests/archive_fetch.test.ts` bestanden. Helfer tatsächlich in isoliertem JS-Kontext ausgeführt: Header, Logout, Origin-/Pfadgrenze, Redirect-/Cache-Verhalten geprüft. Routendekoratoren für alle zwölf Endpunkte zurückgelesen. Kein Geheimnis in Testdaten.

- REC-GATE-001: PASS — Vertragsprüfung mit zehn Markern und zehn Skills erfolgreich; Stufe code-change.
- REC-BACKUP-001: PASS — Backend-Checkpoint e9124c57ef; Root-Checkpoint e0670d330ac bewahrt vorhandene Surface-Änderungen.
- REC-DOC-001: PASS — Aktion, sichtbarer Prüfungsumfang, Rücklese und offene Grenzen in diesem Bericht dokumentiert.

## Offen/Unbekannt

Live-HTTP, reale Anmeldung im Browser, Schlüsselrotation im laufenden System, Surface-Build und Aktivierung sind offen. Kein Live-/Fetch-Stufen-PASS behauptet. Vor gemeinsamer Aktivierung bleibt die Splitter-Policy zu klären, siehe `/root/werkraum/_codex/berichte/2026-09-16-sicherheitsfixes-umsetzung.md`.

OUTCOME: PASS
