# Normale Admin-Kontoanmeldung — Code-Stufe, keine Live-Freigabe

EVIDENCE_VERSION: 1

## Aktion

Vorbereitete Basic-Authentifizierung der Verwaltungswege durch normale Plattform-JWT-Anmeldung plus aktuelle Admin-/Aktivitätsprüfung ersetzt. Alle aktiven Admin-Konten, kein einzelner Benutzer bevorzugt. Betroffene Anhangswege ändern nur ihren vorgeschalteten Zugang; keine Fetch-/Upload-Inhalte verändert.

## Sichtbar

Keine Browseroberfläche geöffnet, keine sichtbare Login-End-to-End-Abnahme. Der feste Texthinweis/Surface-Link ist implementiert, aber noch nicht im laufenden Browser belegt. Stufe ausschließlich code-change, keine live-click/security-Gesamtabnahme.

## Rücklese

11 Node-Tests und drei isolierte Backendtests bestanden. Syntaxprüfungen bestanden. Proxy-Patch per `git apply --check` geprüft, nicht angewendet. Bytegleiche ursprüngliche Proxy-Konfiguration gesichert; Hash und Rolloutreihenfolge unter `/root/werkraum/_codex/berichte/2026-09-16-sicherheitsfixes-umsetzung.md`.

Dateihashes SHA-256:

- `/root/werkraum/welt/api.py`: `476898acc3ba51b84e4486c14a90d0e62cd3df9741064d311c3fc5084b1ce0b3`
- `/vps_root/flextrawurst/scripts/admin_route_guard.ts`: `9880f4cc1a22a46ae93e5599b010c6608ec5a667ae1a7d173c32b33e987a6687`
- `/vps_root/flextrawurst/scripts/admin_auth_client.js`: `a505a1304d9ea908ce5ae7e0a233e43d1ade22d7b3bb2e98352497c4c411b02a`
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts`: `5417fb93995cf1d2d5b0b0d2a6952f6c01e647a3f4067f6f52e24474dec619c8`

## Offen/Unbekannt

Dienstneustarts nicht freigegeben/ausgeführt; effektive Proxy-Umstellung, reale Konto-Proben und Browserabnahme fehlen. Bestehende Werkraum-Datei-Basic-Sperren bleiben unabhängig bestehen. Keine Behauptung, dass globale JWT-Sessions, SSRF oder übrige Reviewbefunde damit behoben sind. Graphify-Werkzeug fehlt.

- REC-GATE-001: PASS — Vertragsprüfung vor Änderung erfolgreich; code-change als einzige Abnahmestufe gewählt.
- REC-BACKUP-001: PASS — Root `1e027643f8d`/`fdffb866ce3`, Werkraum `232d91235a`; Proxy-Snapshot `8d81d48fad` vor etwaiger späterer Proxyänderung. Keine aktive Konfiguration verändert.
- REC-DOC-001: PASS — vierteiliger Bericht mit konkreten Tests, Dateihashes und offenen Live-Grenzen; Umsetzungsbericht aktualisiert.

OUTCOME: PASS

Nur Code-Stufe. Live-Aktivierung und Benutzerabnahme ausdrücklich ausstehend.
