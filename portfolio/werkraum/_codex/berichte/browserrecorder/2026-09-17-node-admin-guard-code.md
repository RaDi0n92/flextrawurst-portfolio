# Node-Verwaltungszugriffsschutz — ausschließlich Code-Stufe

EVIDENCE_VERSION: 1

## Aktion

Zentraler Eintrittsschutz vor Verwaltungs-Schreibaufrufen, einschließlich Eintritt vor Anhangsrouten. Kein Umbau des Upload-/Fetch-Inhalts, keine Browsernavigation, kein Live-Schreibaufruf. Bestehende Werkraum-Basic-Anmeldung wiederverwendet, öffentliche GET-Lesewege erhalten. Dateien: `/vps_root/flextrawurst/scripts/admin_route_guard.ts`, `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts`, `/vps_root/flextrawurst/tests/admin_route_guard.test.ts`.

## Sichtbar

Keine Browseroberfläche geöffnet oder abgenommen. Neue statische Bestätigungsseite im Quellcode unter `/verwaltung-anmelden`; ihre tatsächliche Live-Darstellung und die Browser-Anmeldespeicherung sind noch nicht abgenommen. Für diese reine Backend-Code-Stufe wurde kein Screenshot als Beleg behauptet.

## Rücklese

Fünf Node-Tests bestanden; sieben isolierte Originalcode-VM-Gegenproben bestanden (401/503/403 und synthetische Freigabemarke 204). Syntaxprüfung des Servers bestanden. SHA-256 nach Dateirücklese:

- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts`: `fc8238bc87d06e69159a8f53ae8542cba1a67a35c66b995b202fdb26cd5c0b65`
- `/vps_root/flextrawurst/scripts/admin_route_guard.ts`: `9f97ca515d4b99b7ba19fc687e4bab8db05e5ba61ad0d3bc03d44c59890594b3`
- `/vps_root/flextrawurst/tests/admin_route_guard.test.ts`: `a612fd7d6116188d7a593611d403bb5738e46e5748fde7ab2fa5ec85412ff819`

## Offen/Unbekannt

Live-Aktivierung, Browser-Anmeldefluss und vollständige Kompatibilität aller Automationen offen. Netzwerk-/Upload-Sicherheitsprüfung nicht durch einen Auth-Guard ersetzt. Kein PASS für die Stufen live-click, fetch, download oder security. Graphify nicht verfügbar. Andere Reviewbefunde nicht geschlossen.

- REC-GATE-001: PASS — Vertragsprüfung vor Codeänderung erfolgreich (10 Marker/10 Skills); ausschließlich Stufe code-change gewählt.
- REC-BACKUP-001: PASS — `/vps_root` Backup `68775b3bbd0` vor Codeänderung; Werkraum-Dokumentationscheckpoint `a1dad29cf3`; fremde Änderungen erhalten, kein breites git add.
- REC-DOC-001: PASS — Aktion, Sichtbar, Rücklese und offene Grenzen in diesem Bericht; zusätzlicher Umsetzungsstand `/root/werkraum/_codex/berichte/2026-09-16-sicherheitsfixes-umsetzung.md`.

OUTCOME: PASS

Dieses Ergebnis gilt ausschließlich für die dokumentierte Code-Stufe, nicht für die noch ausstehende Live-Freigabe.
