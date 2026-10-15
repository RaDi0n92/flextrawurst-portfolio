# Admin-JWT — freigegebene Aktivierung und HTTP-Prüfung

EVIDENCE_VERSION: 1

## Aktion

Nach ausdrücklicher Nutzerfreigabe Welt-API und Node-Frontend neu gestartet; nach erfolgreicher Rollenprüfung nginx-Flarumstyler-Block kontrolliert auf den bereits aktiven JWT-Guard umgestellt und nginx per systemd neu geladen. Details, Uhrzeiten, PIDs und Backup-Commits unter `/root/werkraum/_codex/berichte/2026-09-16-sicherheitsfixes-umsetzung.md`.

## Sichtbar

Keine Browser-Screenshots und keine sichtbare Verwaltungsaktion aufgenommen. Reale HTTPS-Antworten geprüft, aber keinen echten Benutzer-Passwortlogin durchgeführt. Keine Behauptung einer vollständigen Browser-/Recorder-Live-Abnahme.

## Rücklese

Alle drei Dienste active; nginx ReloadResult success. HTTPS Surface und öffentliche Metadaten 200; anonyme Verwaltungsproben 401. Zwei bestehende aktive Admin-Konten passieren mit maximal 60 Sekunden gültigen signierten Prüftokens den Guard (404 nur vom absichtlich nicht vorhandenen Ziel). Normales Konto trotz Admin-Claim, Entity und unbekanntes Konto 403; abgelaufener Token 401. Keine Geschäftsdaten verändert. Öffentliche Helper-Datei bytegleich mit Quellstand; feste Helper-Einbindung in gelieferten HTML-Antworten bestätigt.

Proxydatei `/vps_system/etc/nginx/sites-available/flextrawurst`, SHA-256 `e9fcd0ae5765e32e8bc33e2dc3eae7fc44731eb0417fdbb1dfdfa009297e3622`. Direkter nginx-Konfigurationstest aus Werkzeugumgebung war wegen read-only Logpfad nicht vollständig erfolgreich; tatsächlicher systemd-Reload und nachfolgender HTTPS-Rollenabgleich waren erfolgreich.

## Offen/Unbekannt

Echte normale Browser-Anmeldung, sichtbare autorisierte Verwaltungsaktion und Login-/Logout-/Kontowechsel im Browser noch nicht abgenommen. Deshalb **kein** REC-EYE-001 PASS, kein live-click-Gate-PASS und keine umfassende Security-/Recorder-Abnahme. Bestehender code-change-Beleg bleibt unter `/root/werkraum/_codex/berichte/browserrecorder/2026-09-17-admin-jwt-code.md` getrennt erhalten.

OUTCOME: PARTIAL

Bedeutung: Deployment und HTTP-Autorisierungsproben erfolgreich; sichtbare Benutzerabnahme weiterhin offen. Diesen Bericht nicht als bestandenen live-click-Gate-Bericht verwenden.
