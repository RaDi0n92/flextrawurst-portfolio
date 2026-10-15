# Getrennte Dienstschlüssel — live am 2026-09-18

Die zehn bestehenden Dienstidentitäten verwenden Ed25519-Schlüssel. 20 Erzeugerdateien wurden auf den separaten Signierer umgestellt. Die bisherigen DB-Grants und Herkunftsgrenzen bleiben bestehen. Alte HS256-Diensttokens werden nach abgeschlossenem Übergang zurückgewiesen.

## Implementierung und Betrieb

- Signierer: /root/werkraum/welt/service_tokens.py. Tokens gelten 300 Sekunden; feste Audience und Issuer, Service-Rolle, Zeitstempel, UUID-jti und kid.
- Prüfer: /root/werkraum/welt/service_token_verifier.py. Festes EdDSA, öffentliche Schlüssel, aktive Dienstregistrierung, aktive/nicht abgelaufene Schlüssel und aktuelle Grants bei jeder Prüfung; kein Berechtigungscache.
- Registry: /root/werkraum/welt/migrate_service_keys_20260918.sql. Separate Tabelle auth_service_keys mit mehreren Schlüsseln je Dienst; öffentliche Schlüssel ausschließlich. legacy_hs256_until ist für alle Dienste NULL.
- Schlüsselverwaltung: /root/werkraum/welt/service_key_admin.py. bootstrap, rotate und seal-legacy; Rotation veröffentlicht den neuen lokalen Zeiger erst nach Registrierung. Standardüberlappung 300 Sekunden, explizit 0–3600 Sekunden. Alte Dateien bleiben als Herkunft erhalten.
- Admin kann Schlüssel über POST /admin/auth/services/{name}/keys/{kid}/revoke sofort widerrufen. Registrierung, Rotation und Widerruf schreiben interne Events.
- Private Dateien: /root/werkraum/.agent/service-keys/ — Verzeichnisse 0700, Dateien 0600, Eigentümer root, keine Symlinks; Git ignoriert den vollständigen Baum. Keine privaten Schlüssel oder Tokens in diesem Bericht.
- Die Produktionsvenv war schreibgeschützt. Gepinnte Abhängigkeiten liegen separat unter /root/werkraum/welt/.service_crypto/; /root/werkraum/welt/requirements-service-crypto.txt hält cryptography 50.0.1, cffi 2.1.1 und pycparser 3.0 fest. Keine globale Pip-Änderung.
- welt-api.service und dak-gord-web.service wurden gezielt neu gestartet und sind aktiv. Keine umfassende Systemd-/Benutzermigration.

## Nachweise

1. /root/werkraum/tests/service_auth_database_check.py: 210 PostgreSQL-/HTTP-Assertions bestanden. Erfolgreiche Erstellung für alle zehn Dienste, tatsächliche Provenienz und Events, Admin-/Menschen-/Einsammelgrenzen, Legacy-Abschaltung, Bootstrap, Rotation, Widerruf und Schlüsselablauf. Gesamte Testtransaktion zurückgerollt; keine Testinhalte oder Test-Grants dauerhaft geschrieben.
2. Produktionsvenv: 38 Tests aus /root/werkraum/tests/test_auth_account_status.py, /root/werkraum/tests/test_service_token_permissions.py, /root/werkraum/tests/test_service_keys.py und den /root/werkraum/tests/test_group_chat*.py bestanden, keine übersprungen. Eine Warnung betrifft einen kurzen synthetischen HMAC-Testschlüssel.
3. Laufende API auf localhost:8030: 53 HTTP-Prüfungen bestanden. Für jeden Dienst neues Token + falsche Herkunft 403, altes korrekt signiertes HS256-Diensttoken 401, allgemeine Admin-/Menschenendpunkte 401. Menschlicher Admin: Dienstliste, Schlüsselliste und eigenes Profil 200. Keine Probe-Inhalte geschrieben.
4. Echte Rotation von codex-abwurf mit Überlappung 0: zuvor ausgestelltes Token 401, neuer Schlüssel wird geprüft und unzulässige Herkunft mit 403 abgelehnt. Kein API-Neustart für den Widerruf nötig.
5. Dateirechte und fehlende Git-Erfassung der privaten Schlüssel geprüft.
6. graphify update . versucht, aber Programm nicht installiert (Exit 127). Wissensgraph deshalb nicht aktualisiert.
7. `/root/werkraum/welt/api.py` repariert den alten Einsammel-Claimvertrag: `user_id` plus `role` entscheidet explizit zwischen Mensch und Wesen. Drei Unit-Tests und die Live-Matrix bestanden: Diensttoken 401, gültiger menschlicher Admin auf nicht existierendem Splitter 404, anonym 401. Kein Splitter wurde verändert.

## Grenzen und Wiederaufnahme

Dies trennt Signieridentitäten bei Verlust eines einzelnen Dienstschlüssels. Es isoliert keine gemeinsam als root laufenden Prozesse. Der gemeinsame menschliche/Wesen-HMAC-Vertrag besteht fort; Zugriff auf dessen Secret oder auf sämtliche privaten Dateien bleibt bei Root-Kompromittierung möglich. Weitere Unix-/Systemd- und DB-Rechtetrennung ist eigenständige Arbeit, hier nicht als erledigt behauptet.

Ein Absturz zwischen Registrierung und Veröffentlichung kann einen zusätzlichen registrierten Schlüssel zurücklassen; ein Fehler nach Veröffentlichung meldet ausdrücklich die fehlgeschlagene Ablaufbegrenzung alter Schlüssel. Dann Registry prüfen und alte Schlüssel gezielt widerrufen. Kein stiller Erfolg. Kein Downgrade auf den alten gemeinsamen Dienstsignierer als Standard-Rollback.

Der Einsammelpfad bleibt wegen seines bisherigen Claims-Vertrags fail-closed; diese Arbeit aktiviert ihn nicht. Keine Aussage, dass damit das gesamte Sicherheitsreview abgeschlossen wäre.

Der Einsammelpfad ist seit Commit `8a2f2f4eeb` repariert und live. Diensttokens bleiben dort ausgeschlossen; die Reparatur ergänzt keinen globalen `sub`-Claim.

Code-Commits: ecd9ee0b63 (Prüfer, Verwaltung, Migration und Tests), f8105a2a14 (Erzeuger). Sicherungspunkte: fe5bd7787d, 4d143cde13, 1c1d6ac1ee.

Technische Referenzen: https://pyjwt.readthedocs.io/en/stable/usage.html und https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/
