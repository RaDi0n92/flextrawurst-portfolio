# Sicherheitsfixes — Umsetzungsstand

Auftrag: Daniels „dann mach das“ nach Priorisierung und Erklärung der Bedienfolgen. Öffentliche Leseansichten, bestehende Wesen-Funktionen und Provenienz sollen erhalten bleiben. Kein pauschales Abschalten, keine eigenmächtigen Dienstneustarts.

## Umgesetzt: Container-Admin-Pfadgrenze (SEC-008)

- Datei: `/root/werkraum/codewesen_container.py`.
- Neue gemeinsame Pfadprüfung ausschließlich für `admin_schreibe` und `admin_entferne`; die normalen Wesen-Schreibfunktionen bleiben unverändert.
- Wesen muss ein vorhandenes direktes Verzeichnis unter der vorgesehenen Wurzel sein. Elternkomponenten, absolute Wesenpfade und Symlink-Orte werden zurückgewiesen.
- Containerbasis und Container dürfen nicht über Symlinks ausweichen. Löschdateinamen müssen einzelne Komponenten sein; absolute Namen, Separatoren, NUL und Symlink-Dateien werden zurückgewiesen.
- Schutz der Beschreibungsdatei bleibt bestehen; gültige Eintragslöschung funktioniert weiterhin. Keine produktive Datei gelöscht oder Testreaktion geschrieben.
- Dies behebt die Pfadprüfung, **nicht** die fehlende HTTP-Authentifizierung (SEC-007). Keine Garantie gegen einen konkurrierenden, bereits lokal schreibberechtigten Angreifer, der zwischen Pfadprüfung und Dateizugriff Verzeichnisse austauscht.

## Tests und Sicherung

- Vorheriger Backup-Commit im Werkraum: `138f9f31b2`.
- Implementierung und Tests gesichert: `e430121cdb`.
- Regression: `/root/werkraum/tests/test_container_admin_path_security.py`.
- Befehl: `python3 -B -m unittest discover -s tests -p test_container_admin_path_security.py -v`, Arbeitsverzeichnis `/root/werkraum`.
- Ergebnis: vier Tests bestanden. Geprüft wurden gültige Löschung/Beschreibungsschutz, Pfadkomponenten, unbekannte/ausbrechende Wesen-IDs und Datei-/Verzeichnissymlinks. Originalfunktionen AST-isoliert, nur temporäre synthetische Dateien, keine produktiven Import-Nebenwirkungen.
- `git diff --check` für den Änderungsscope ohne Fehler.
- Angeforderter Graphabgleich `graphify update .` im Werkraum scheiterte mit Exit 127: Werkzeug in dieser Umgebung nicht verfügbar. Kein erfolgreicher Graphabgleich behauptet.

## Blockiert: zentraler Node-Verwaltungszugriffsschutz

- Betroffene Datei: `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts`; zuständiges Repository ist `/vps_root`, nicht ein eigenständiges Frontend-Repository.
- Eigene Frontend-Aufrufer für Wizard und Wesenchat wurden untersucht: sie senden bislang keine Plattform-Bearer-Anmeldung. Ein neuer Guard allein würde diese Bedienwege blockieren; der passende Anmeldeweg muss mitgeführt werden.
- Die bestehende Konfiguration `/vps_root/flextrawurst/.env.preview` enthält eine nichtleere Werkraum-Passwortzuweisung. Nur Vorhandensein geprüft, kein Geheimnis im Bericht.
- Vorgeschriebener Backup-Commit scheitert an `/vps_root/.git/index.lock`. Dateizeitstempel: 2026-09-06 22:10:30 +0200, Größe 0. Im Container kein passender Git-Prozess gefunden; das beweist nicht, dass auf dem Host keiner läuft.
- Sperre nicht entfernt und nicht durch einen anderen Index umgangen. Daniel wurde gefragt, ob nach weiterer Prüfung eine **nachweislich verwaiste** Sperre entfernt werden darf.
- Deshalb noch keine Node-Guard-, Frontend-Anmelde- oder Proxyänderung. SEC-005/007 bleiben offen.

## Recorder-Vertrag und Aktivierungsgrenze

Für die geplante zentrale Guard-Änderung (betrifft auch den Eintritt vor Anhangsrouten) wurden `/root/werkraum/_codex/skills/recorder-integritaets-gate/SKILL.md`, `/root/werkraum/_codex/skills/recorder-backup-vor-aenderung/SKILL.md`, `/root/werkraum/_codex/skills/recorder-audit-dokumentation/SKILL.md` und `/root/werkraum/_codex/skills/recorder-security-inputs/SKILL.md` gelesen. Vertragsprüfung: bestanden, zehn Marker/Skills. Die Änderung wurde wegen des fehlenden Backup-Checkpoints noch nicht begonnen; keine Code-/Security-/Live-Stufe als PASS abgenommen.

Keine Dienste neugestartet. Der Container-Admin-CLI importiert die Python-Datei bei neuen Aufrufen; deshalb kann der gespeicherte Pfadfix bei einem späteren legitimen Aufruf bereits greifen, obwohl kein Dienstneustart erfolgte. Das wurde absichtlich nicht durch eine produktive Löschung ausprobiert. Bereits laufende Python-Prozesse können weiterhin den alten importierten Stand halten.

Weitere priorisierte Fixgruppen (Privatsphäre, Profil-HTML, URL-Netzgrenzen, Token-/Sitzungswiderruf, WebSocket-Widerruf) sind noch nicht umgesetzt. Dieser Zwischenstand bedeutet ausdrücklich nicht „System abgesichert“.

## Fortsetzung am 2026-09-17 — Node-Zugriffsschutz vorbereitet

Daniel hat die Entfernung einer nachweislich verwaisten Git-Sperre erlaubt. Erneute Prüfung über `/vps_system/proc`: keine Git-/Graphify-Prozesse, keine offenen Dateideskriptoren auf Git-Indexsperren, keine unlesbaren Prozess-/FD-Verzeichnisse in der Erhebung. Wiederholte Dateiprüfung unverändert, auch `fuser` fand keinen Nutzer. Die vorgefundene Sperre hatte inzwischen den Zeitstempel 2026-09-17 06:03:30 +0200; es wurde ausdrücklich nicht nur auf den alten Zeitstempel vertraut. Zur Wiederherstellbarkeit nach `/vps_root/.git/index.lock.verwaist-20260917` verschoben statt gelöscht.

Backup-Commit `/vps_root`: `68775b3bbd0`. Er enthält auch 158 bereits vorher vorhandene ergänzte Zeilen im Node-Server, die nicht von diesem Sicherheitsfix stammen und erhalten bleiben. Git-Autoridentität nur für diesen Befehl als Codex gesetzt; keine globale Konfigurationsänderung.

Codeänderungen:

- `/vps_root/flextrawurst/scripts/admin_route_guard.ts`: zentrale Einstufung aller Nicht-GET/HEAD/OPTIONS-Aufrufe unter `/wesen`, `/api/wesen-dienst-wizard`, `/api/flarumstyler`, `/dolphin`, `/aufgabenchats`. Fremde oder undurchsichtige Browser-Origin und fremde Fetch-Metadata werden abgelehnt. Kein Localhost-Freibrief.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts`: Prüfung vor Routen, Body-Verarbeitung und Unterprozessen; wiederverwendet die vorhandene fail-closed Werkraum-Basic-Anmeldung. Öffentliche Leseaufrufe und normale Plattform-API bleiben unverändert.
- Neue Anmeldeseite `/verwaltung-anmelden`: top-level Basic-Challenge, anschließend statische Bestätigung mit Links. Passwort wird nicht in JavaScript gespeichert. Diese Anmeldung ist **getrennt** von der Menschenprofil-/JWT-Anmeldung; noch keine fein abgestufte Benutzer-/Entity-Rechteverwaltung.
- Bedienfolge nach Aktivierung: Daniel muss sich gegebenenfalls einmal mit den bestehenden Werkraum-Zugangsdaten anmelden. Programme, die geschützte HTTP-Schreibwege bisher anonym nutzten, benötigen diese Authentifizierung; direkt arbeitende Python-/CLI-Wege werden davon nicht automatisch erfasst. Es wurde keine vollständige Inventur sämtlicher externer Aufrufer behauptet. Insbesondere Chat-/Anhangsschreiben innerhalb der genannten Verwaltungsbereiche ist jetzt ebenfalls geschützt; reine Leseansichten bleiben offen.

Tests: `/vps_root/flextrawurst/tests/admin_route_guard.test.ts`, fünf Tests bestanden; Node-Syntaxprüfung des Servers bestanden. Zusätzlich sieben isolierte VM-Gegenproben mit dem aus dem Originalserver extrahierten Guard und `requireAuth`: anonym 401, fehlendes Serverpasswort 503, falsches Passwort 401, korrektes Passwort bis zur synthetischen Dispatcher-Marke 204, öffentlicher GET bis 204, fremde Origin trotz korrekter Zugangsdaten 403, Login-Challenge 401. Keine produktiven Zugangsdaten oder Live-Schreibaufrufe verwendet. 204 ist hier nur die Testmarke, nicht die Antwort einer echten Verwaltungsaktion.

Der Code ist vorbereitet, **nicht live aktiviert**. Kein Serverneustart und keine Browser-End-to-End-Abnahme. Der Auth-Guard begrenzt auch den Zugang zum URL-Leser, behebt aber nicht dessen eigentliche SSRF-Netzwerkgrenze. Öffentliche Leselecks bleiben ebenfalls offen. Graphify bleibt in dieser Umgebung nicht verfügbar (Exit 127).

Code-Stufenbeleg: `/root/werkraum/_codex/berichte/browserrecorder/2026-09-17-node-admin-guard-code.md`. Keine Recorder-Live-, Download- oder Gesamt-Security-Abnahme daraus ableiten.

## Korrektur nach Daniels Klarstellung: normale Anmeldung aller Admin-Konten

Daniel kannte die separate Werkraum-Passwortanmeldung nicht und hat ausdrücklich alle Admin-Konten über die normale Plattform-Anmeldung verlangt. Die zuvor vorbereitete Basic-Lösung für die neuen Verwaltungsguards wurde deshalb vor Live-Aktivierung durch einen JWT-Kontocheck ersetzt. Alte Beschreibungen oben sind historisch, nicht der aktuelle Zielzustand.

### Implementiert, noch nicht aktiviert

- `/root/werkraum/welt/api.py`: zusätzlicher GET `/auth/admin-check` verifiziert das vorhandene JWT durch den normalen Auth-Guard und prüft anschließend `human_users.role` und `is_active` aktuell aus der Datenbank. Kein bestimmter Adminname bevorzugt. Herabgestufte/gesperrte/fehlende Konten werden trotz altem Token abgelehnt; Entity-Tokens sind kein Admin-Konto. Keine Änderung an globalem JWT-Widerruf anderer API-Routen behaupten.
- `/vps_root/flextrawurst/scripts/admin_route_guard.ts`: Bearer-Prüfung ausschließlich über den festen lokalen Verifier auf Port 8030; Timeout drei Sekunden, keine Weiterleitungen, keine Basic-Ausnahme, bei Fehlern gesperrt. Ohne Token 401, ohne aktuelle Adminrechte 403, nicht erreichbare/alte Verifier-API 503.
- `/vps_root/flextrawurst/scripts/admin_auth_client.js`: vorhandenen `ftw_token` bei betroffenen gleichursprünglichen Verwaltungsaufrufen mitsenden. Keine Weitergabe an fremde Origins, keine automatische Weiterleitung geschützter Fetch-Aufrufe, bestehende explizite Header bleiben erhalten. Token wird bei jedem Aufruf erneut gelesen, also kein eigener Anmelde-/Logoutzustand. Bei 401/403/503 Texthinweis mit Link zur Surface und normalem Einloggen.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts`: Clienthelfer vor bestehenden Skripten in neun Verwaltungs-HTML-Ausgaben eingebunden; keine generierten Dateien überschrieben. `/verwaltung-anmelden` führt nur noch zur Surface zurück, keine separate Passwortabfrage. Die bereits vorher existierende Basic-Absicherung der Werkraum-Dateirouten wurde nicht angefasst.
- Flarumstyler-Sonderfall: der vorhandene nginx-Basic-Block würde Bearer-Anmeldungen abweisen. Node schützt deshalb jetzt auch sämtliche Flarumstyler-API-Leseaufrufe, einschließlich `/api/flarumstyler_verlauf`, bevor die alte Proxysperre wegfallen darf. Diese Lesedaten waren schon zuvor nicht öffentlich; andere öffentliche Lesewege bleiben offen.

### Proxy-Übergang nur vorbereitet

Aktive Konfiguration `/vps_system/etc/nginx/sites-available/flextrawurst` **nicht geändert oder neu geladen**. Exakte Sicherung `/root/werkraum/_codex/backups/2026-09-17-nginx-flextrawurst-before-admin-jwt.conf`, beide SHA-256 `116184a45fc463e75e127c23f49b8b655a3aacc32cfd7ad3d8e7f2099e8b0f13`, gesichert in Commit `8d81d48fad`.

Vorbereiteter Patch: `/root/werkraum/_codex/berichte/2026-09-17-nginx-admin-jwt.patch`. `git apply --check` im Konfigurationsverzeichnis bestanden; Patch nicht angewendet. Noch kein `nginx -t` gegen eine gepatchte effektive Konfiguration und keine Live-Abnahme.

Erforderliche Aktivierungsreihenfolge nach expliziter Neustartfreigabe:

1. Aktuellen Code-/Konfigurationsstand und laufende Dienste erneut abgleichen, keine parallelen Änderungen überschreiben.
2. Welt-API laden und neuen Verifier negativ sowie mit gültiger Admin-Anmeldung prüfen.
3. Node-Server laden, anonyme und nichtadministrative Zugriffe vor jeder Nebenwirkung abgewiesen prüfen; gültige Admin-Leseprobe und normale öffentliche Leseansichten prüfen.
4. Erst danach den kleinen nginx-Patch anwenden, effektive Konfiguration testen und kontrolliert neu laden. Bei fehlgeschlagenem Schritt alte Proxysperre beibehalten. Ein Rollback auf den alten Node darf nicht mit deaktivierter Proxysperre kombiniert werden.
5. Browser-End-to-End-Abnahme mit normalem Login/Logout und mindestens zwei Admin-Konten, gewöhnlichem Nutzer sowie deaktiviertem Konto. Keine Produktivkonten allein für einen Test eigenmächtig ändern.

### Prüfungen und Grenzen

11 Node-Tests bestanden: `/vps_root/flextrawurst/tests/admin_route_guard.test.ts` und `/vps_root/flextrawurst/tests/admin_auth_client.test.ts`. Drei AST-isolierte Backendtests bestanden: `/root/werkraum/tests/test_admin_session_check.py`. Node-/Client-Syntaxprüfung und scoped Diff-Prüfung bestanden. Ausschließlich synthetische Tokens/DB-Antworten, kein Serverstart und keine echten Verwaltungsaktionen. Graphify weiterhin nicht verfügbar, Exit 127.

Backups vor Änderung: Werkraum `232d91235a`, Root `1e027643f8d`; Zwischenstand Backend `45cc2d87d5`, Node `503e5c5cde1`; vor ergänzender Flarum-Grenze Root `fdffb866ce3`. Weitere Review-Fixgruppen bleiben offen. Kein Ersatz einer echten Live-/Browserabnahme durch Unit-Tests.

Neuer Code-Stufenbeleg: `/root/werkraum/_codex/berichte/browserrecorder/2026-09-17-admin-jwt-code.md`.

## Live-Aktivierung am 2026-09-17 nach ausdrücklicher Freigabe

Daniel hat Neustarts und Proxy-Umschaltung mit „jojo“ freigegeben und anschließend „weiter“ verlangt. Aktuelle Dateihashes wurden vor Aktivierung gegen den geprüften Stand abgeglichen. Backups: `c80ed2a661` vor Dienstaktivierung, `1ca673b398` vor Proxy-Umschaltung, `b33d24bc6e` vor diesem Bericht.

### Tatsächlich ausgeführt

1. `welt-api.service` kontrolliert neu gestartet, aktiv seit 2026-09-17 16:00:37 CEST (14:00:37 UTC), PID 779679. Health 200, neuer Admin-Verifier anonym 401.
2. Verifier mit kurzlebigen, lokal signierten Prüftokens auf zwei bestehende aktive Admin-Konten getestet: jeweils 200. Unbekanntes Konto 403, abgelaufener Token 401, Entity-Token 403. Ein vorhandenes gewöhnliches Konto blieb selbst bei signierter Admin-Rollenbehauptung 403, weil die aktuelle DB-Rolle zählt.
3. `process-camera-preview.service` kontrolliert neu gestartet, aktiv seit 16:01:57 CEST (14:01:57 UTC), PID 781947. Unmittelbare erste Verbindungsversuche trafen die kurze Startphase (connection refused); anschließende Status-/HTTP-Prüfungen erfolgreich. Root-Seite 200, Helper 200, geschützte API anonym 401, öffentliche Wizard-Metadaten 200.
4. Erst nach positivem Node-Guard-Test den exakt vorbereiteten Block unter `/vps_system/etc/nginx/sites-available/flextrawurst` mit `apply_patch` umgestellt: Flarumstyler-Basic deaktiviert, Authorization an den bereits aktiven JWT-Guard weitergegeben. Auch die bisherigen privaten GET-/Verlaufspfade bleiben am Node geschützt.
5. Direkter `nginx -t` aus der eingeschränkten Host-Werkzeugumgebung meldete zunächst „syntax is ok“, scheiterte aber beim Öffnen der Logdatei wegen read-only Dateisystem. Deshalb **kein erfolgreicher separater nginx-Test behauptet**. Der normale freigegebene systemd-Reload über den tatsächlichen nginx-Dienst gelang danach; dessen ExecReload verwendet `nginx -s reload`. `ReloadResult=success`, alle drei Dienste active. Bestehende Warnungen über doppelte HTML-MIME-Typen wurden nicht als Nebenauftrag verändert.

Nginx-Konfigurationshash danach: `e9fcd0ae5765e32e8bc33e2dc3eae7fc44731eb0417fdbb1dfdfa009297e3622`. Vorherige Konfiguration unverändert gesichert unter `/root/werkraum/_codex/backups/2026-09-17-nginx-flextrawurst-before-admin-jwt.conf`.

### Über die öffentliche HTTPS-Adresse nachgeprüft

- Surface 200; öffentliche Wizard-Metadaten 200.
- Anonymer GET auf einen absichtlich nicht vorhandenen Flarumstyler-Unterpfad: 401 statt Durchlass.
- Anonymer POST auf einen absichtlich nicht vorhandenen Wizard-Unterpfad: 401; keine echte Verwaltungsaktion ausgelöst.
- Zwei aktive Admin-Konten passieren den Guard am nicht vorhandenen Flarumstyler-Unterpfad und erhalten dort die erwartete nachgelagerte **404**. 404 bedeutet hier bewusst „Guard passiert, keine echte Aktion/kein Inhalt“, nicht „Admin-Login fehlgeschlagen“.
- Unbekanntes Konto, Entity-Token und normales Konto mit Admin-Claim jeweils 403; abgelaufener Token 401. Dieselben Prüfungen wurden vorher direkt am Node ausgeführt.
- Ausgeliefertes `/admin-auth-client.js` bytegleich mit `/vps_root/flextrawurst/scripts/admin_auth_client.js`, SHA-256 `a505a1304d9ea908ce5ae7e0a233e43d1ade22d7b3bb2e98352497c4c411b02a`.
- Ausgelieferte Wizard-/Solarius-HTML-Antworten enthalten den festen Clienthelfer; `/verwaltung-anmelden` führt per 303 auf `/`, ohne neue Passwortabfrage.

### Ehrliche Prüfgrenzen

Prüftokens wurden nur im Arbeitsspeicher erzeugt, maximal 60 Sekunden gültig, nicht ausgegeben oder gespeichert. Verwendet wurde die vorhandene Signaturkonfiguration. Datenbankzugriff ausschließlich read-only auf Konto-ID/Rolle/Aktivität; keine Konten erstellt, umgestuft oder deaktiviert. Es wurden keine privaten Inhalte ausgelesen und keine echten Verwaltungsaktionen durchgeführt.

Diese Prüfung bestätigt den live laufenden HTTP-/Rollen-/Proxyweg. Sie ersetzt **nicht** den echten Passwortlogin im Browser, die sichtbare Bedienung einer erfolgreichen Verwaltungsaktion oder eine Recorder-Echtaugen-Abnahme. Deaktivierte Konten wurden isoliert getestet, kein Produktivkonto dafür verändert. Live-Browser-/Login-/Logout-Abnahme bleibt offen; kein entsprechendes Gate-PASS behauptet.

Bedienung: normale Surface öffnen, dort „Einloggen“ mit einem aktiven Admin-Konto; bereits offene Verwaltungsseiten neu laden, damit sie den neuen Helper laden. Keine zusätzliche Werkraum-Passwortanmeldung für diese neuen Verwaltungswege. Die älteren getrennten Werkraum-Dateirouten behalten ihre bestehende Absicherung.

Aktivierungsbeleg mit offenen UI-Grenzen: `/root/werkraum/_codex/berichte/browserrecorder/2026-09-17-admin-jwt-aktivierung.md`. Die übrigen Reviewbefunde sind dadurch nicht automatisch behoben.

## 2026-09-17 — Profil-Privatsphäre: Code korrigiert, noch nicht aktiviert

Betroffen: `/root/werkraum/welt/api.py`, Funktionen `menschen_liste` und `public_profile` (SEC-010/SEC-011 sowie profilbezogener Teil von SEC-012).

- Das öffentliche Menschenverzeichnis verlangt jetzt ausdrücklich `human_profiles.visibility = 'public'`; aktive Konten allein reichen nicht.
- Identitätsgebundene Profile zeigen und zählen nur Einträge mit `sichtbarkeit = 'public'`. Anonyme Tagebuch-, Notiz-, Traum- und Kalendereinträge werden dort nicht mehr einem Namen zugeordnet. Private Aktivität wird auch nicht über Gesamtzähler verraten. Bestehende Antwortschlüssel bleiben erhalten; die bisherigen Gesamtzähler bedeuten hier jetzt öffentlich zuordenbare Einträge.
- Bei `gedankenwelt_anonym` liefert das identifizierte Profil `gedankenwelt: null`. Der Anonymitäts-Schalter bleibt erhalten; gespeicherter Inhalt und separate Feeds bleiben unverändert.
- Splitter-Zähler und jüngste Splitter auf Profilen sowie Verzeichnis-Zähler verlangen `herkunft_sichtbar IS TRUE` und Status `aktiv`, `aufgenommen` oder `verarbeitet`.
- Keine Inhalte gelöscht, keine Sichtbarkeit in der Datenbank geändert, keine Änderungen an persönlichen oder Admin-Endpunkten.

Prüfung: `/root/werkraum/tests/test_public_profile_privacy.py` enthält fünf bestandene isolierte Regressionstests mit synthetischen Daten. Die echten Funktionen werden AST-isoliert ausgeführt; Tests prüfen SQL-Verträge, Gedankenwelt-Ausgabe, 404-Abbruch und Verbindungsschließung. Das ist **kein** PostgreSQL-Integrationstest und keine Browser-Abnahme. Zusätzlich drei Admin-Verifier-Tests und vier Container-Pfadtests bestanden, insgesamt zwölf Tests. `git diff --check` ohne Fehler. Backup vor Codeänderung: `753ac60e35`.

`graphify update .` versucht, aber ausführbares Programm fehlt; Graph nicht aktualisiert. Kein Dienst neu gestartet: Die Profilkorrektur ist noch **nicht als live bestätigt**. Für Aktivierung ist ein freigegebener Neustart von `welt-api.service` mit anschließender Prüfung nötig.

Weiterhin offen: allgemeine Splitter-Liste, Spur- und Story-Ausgabe (SEC-012) sowie Archiv-APIs (SEC-014). Die vorgefundenen Post-Relations-/Spurabfragen enthalten bereits Public-Filter für Quell- und Zielposts; diese vorhandene Änderung wurde nicht überschrieben und wird nicht als eigene Reparatur oder vollständig verifizierter Abschluss von SEC-015 beansprucht.

## 2026-09-17 — Splitter-Privatsphäre: Code korrigiert, noch nicht aktiviert

Betroffen: `/root/werkraum/welt/api.py`, öffentliche Zwischenraum-/KompOase-Splitter-Lesewege und davon gespeiste Such-/Feed-Ansichten (SEC-012).

- Eine gemeinsame Public-Policy verlangt jetzt für nichtadministrative Antworten `herkunft_sichtbar IS TRUE`, einen veröffentlichbaren Status (`aktiv`, `aufgenommen` oder `verarbeitet`) und bei menschlicher Herkunft ein tatsächlich öffentliches `human_profiles`-Profil.
- Das gilt für `/zwischenraum/splitter`, beide Detail-/Spurvarianten, `/kompoase/splitter`, die Story-Ansicht, `/entities/{entity_id}/splitter`, `/suche`, `/search/global`, `/mw/feed` und `/api/splitter-aufnahmen`.
- Öffentliche Antworten geben menschliche Konto-UUIDs nicht mehr als `human_id`/Akteur-ID aus. Öffentliche Spuren erlauben nur notwendige Eventfelder (`post_ref`, `post_source`, `emojis`); Event-Actor-IDs und interne Payloads bleiben draußen.
- Event-Spuren verlangen `visibility_layer IN ('public','world')`; verknüpfte Posts verlangen `ftw_posts.sichtbarkeit = 'public'`. Story-Gruppen werden auf öffentliche/aktive Gruppen und nicht-private Links begrenzt; Verbindungen zeigen nur, wenn beide Splitter öffentlich sind. Roh-`meta` wird aus öffentlichen Storys entfernt.
- Admin-Ausnahmen in diesen Lesewegen laufen jetzt über den datenbankgestützten `/auth/admin-check`-Pfad; ein altes oder gefälschtes `role=admin`-Claim reicht nicht. Die zugrunde liegenden Splitter, Events, Aufnahmen und Gruppenlinks wurden nicht gelöscht oder verändert.

Prüfung: `/root/werkraum/tests/test_splitter_privacy.py` enthält sechs bestandene isolierte Regressionstests mit synthetischen Zeilen und Allowlist-Prüfung. Zusätzlich fünf Profiltests, drei Admin-Verifier-Tests und vier Container-Pfadtests bestanden; zusammen 18 Tests in diesem Lauf. `python3 -m py_compile /root/werkraum/welt/api.py` und `git diff --check` bestanden. Zwei repräsentative PostgreSQL-`EXPLAIN`-Abfragen (Public-Splitter-Filter und öffentliche Verbindungen) liefen gegen die Live-Datenbank ohne SQL-Fehler. Kein Dienstneustart und keine Inhaltsänderung.

Backup vor dem Block: `883cd1e1c8`; Code-Commits: `ee66bde459` und `4ffc2d1885`; Dokumentations-Checkpoint: `76e1b55311`. `graphify update .` bleibt nicht ausführbar (Programm fehlt, Exit 127). Die laufende API enthält diese Korrektur noch nicht; Aktivierung braucht einen kontrollierten Neustart von `welt-api.service` nach Freigabe und anschließende HTTP-/Negativprüfungen.

Archiv-APIs (SEC-014), allgemeine JWT-Altpfade außerhalb dieser Lesestrecke (SEC-001), Upload-/SSE-/Form-Limits und die übrigen Reviewbefunde bleiben offen. Vor der nächsten ungeklärten Rechteentscheidung gilt die vereinbarte Modellampel: **Jetzt besser Astra**.

## 2026-09-17 — Astra-Gegenprüfung: Splitter noch nicht freigegeben; Archivschutz vorbereitet

Die vorherige Aussage „Splitter-Block fachlich abgeschlossen“ war zu weitgehend. Die sechs Tests prüften überwiegend Quelltextmerkmale; zwei EXPLAINs bestätigten SQL-Planbarkeit, keine vollständige Rechteentscheidung und keine Browserfunktion.

Bestätigtes Restleck korrigiert in `/root/werkraum/welt/api.py`: Die öffentliche Story erlaubte interne Gruppen, während `/root/werkraum/welt/groups_api.py` dafür eine Anmeldung verlangt. Sie fordert jetzt für nichtadministrative Zugriffe ausdrücklich öffentliche Gruppen und öffentliche Materiallinks. Rechte-/Herkunftssnapshots, Ersteller-ID und beliebige Link-Metadaten werden aus der öffentlichen Antwort entfernt. Der ergänzte Test in `/root/werkraum/tests/test_splitter_privacy.py` führt die echte Story-Funktion mit synthetischen Antworten aus und prüft öffentliche Redaktion und vollständige Admin-Ausgabe. Sieben Splittertests bestanden. Commit `de0e4f1bcb`, Backup `02fd65487c`.

**Offene Splitterfragen vor Aktivierung:** `herkunft_sichtbar=False` wird aktuell vollständig ausgeblendet, obwohl die Freigabefunktionen auch nicht zitierbares Material als Splitter freigeben können. Ebenso ist die zusätzliche Bindung einer Materialfreigabe an ein öffentliches Menschenprofil eine Produktentscheidung. Anonyme Veröffentlichung und Herkunftsschutz dürfen nicht verwechselt werden. Daniel wurde zur gewünschten anonymen Veröffentlichung gefragt. Weitere rohe `meta`-/Begründungsfelder in Detail-/Aufnahmeantworten sowie abgeleitete Essenzen aus privaten Quellen benötigen gezielte Gegenproben. SEC-012 bleibt deshalb teilweise offen.

**Archivvertrag aus bestehendem Code rekonstruiert:** `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts` dokumentiert Daniels Freigabe „serverseitig richtig sperren — aber mit key verfügbar“. Aktuelle Admin-Anmeldung oder einer der zwei unabhängig rotierbaren Schlüssel bleiben gültige Zugangswege.

In `/root/werkraum/welt/api.py` tragen nun alle zwölf GET-Routen der vier Archivfamilien eine gemeinsame FastAPI-Abhängigkeit. Sie prüft aktuelle Admin-Rechte oder Archiv-/Crawlschlüssel, auch per `X-Archive-Key`/`X-Crawl-Key`, mit längenbegrenztem, konstantzeitlichem Vergleich. Fehlende/leere/falsche/rotierte Schlüssel gewähren keinen Zugang. Erfolgreiche Antworten erhalten `private, no-store`; Ablehnungen 403 und `no-store`. Geheimnisse wurden weder gelesen noch protokolliert. Backend-Commit `c3afeec280`, Backup `e9124c57ef`.

In `/vps_root/flextrawurst/scripts/build_surface.ts` verwenden die 18 vorhandenen Archivaufrufe jetzt einen begrenzten `archiveFetch`-Helfer: aktuelles `ftw_token`, bestehende Query-Schlüssel als Header, nur dieselbe Origin und die vier Archivpfade, keine Redirects, kein Cache. Vorhandene fremde Änderungen wurden unter `e0670d330ac` gesichert und erhalten. Keine neue globale Fetch-Überschreibung.

Prüfungen: fünf Tests in `/root/werkraum/tests/test_archive_access.py` bestanden (fehlende Rechte, aktuelle Adminrolle, beide Schlüsselwege, Rotation, Unicode-/Längenfälle, alle zwölf Routendekoratoren); zwei Node-Tests in `/vps_root/flextrawurst/tests/archive_fetch.test.ts` bestanden (tatsächliche Helferausführung, Logout, fremde Origin, fremder Pfad, alle 18 Aufrufe). Syntax- und gezielte Diff-Prüfung bestanden. Das sind isolierte Tests, keine vollständigen HTTP-/Browsernachweise.

**Aktivierung ausstehend:** Surface-Build noch nicht ausgeführt, weil er direkt ausgelieferte HTML-Dateien überschreibt; Backend-Dienst nicht neu gestartet. API und Surface müssen gemeinsam aktiviert werden. Vorher Splitterentscheidungen klären und deren Tests erweitern. Sonst würde der Neustart gleichzeitig den noch nicht freigegebenen Splitterstand laden. SEC-014 ist im Quellcode vorbereitet, nicht live geschlossen. Graphify bleibt mangels ausführbarem Programm offen.

Modellabsprache: Bei offenen Rechte-/Anonymitätsentscheidungen Astra beibehalten; erst nach konkreter Policy und belastbaren Regressionstests wieder Luna für die abgegrenzte Aktivierung empfehlen.

## 2026-09-17 — Daniels Herkunftsvorgabe umgesetzt und aktiviert

Daniel stellte klar: zunächst keine anonyme Herkunft, weder bei AI-Strömen noch bei Menschen; bestehende anonyme Veröffentlichungen ausdrücklich veröffentlichen und die Defaults entsprechend setzen. Dies löst die vorherige offene Produktentscheidung. Private Originale ohne Freigabe und als gelöscht markierte Einträge waren nicht Gegenstand einer Wiederveröffentlichung.

### Code und Daten

- `/root/werkraum/welt/api.py`: Standard für fehlendes `zitierbar_standard` ist true; API-Fallback für Notiz-/Schatten-Anonymität false. Explizite spätere Abweichungen bleiben als bestehende Einstellmöglichkeit erhalten. Freigegebene Splitter sind unabhängig von der Sichtbarkeit ihres Menschenprofils lesbar; Ursprung-IDs in Listen, Details, Spuren und Story werden wieder ausgegeben. Ein privates Profil wird dadurch selbst nicht öffentlich.
- `/root/werkraum/welt/splitter_daemon.py`: Schattenkommentar-Splitter erhalten standardmäßig sichtbare Herkunft. Andere Erzeugungswege mit expliziten Einwilligungsregeln bleiben erhalten; bestehende Material-Einwilligungen werden nicht erfunden.
- `/root/werkraum/welt/schema_blasen_tamagotchi.sql` und `/root/werkraum/welt/schema_persoenliche_welt.sql`: neue Installationen erhalten nichtanonyme Voreinstellungen und zitierbare persönliche Einträge. Ein neuer persönlicher Eintrag erzeugt dadurch noch keinen freigegebenen Splitter; dafür bleibt die Freigabeaktion erforderlich.
- `/root/werkraum/welt/migrate_attributed_defaults_20260917.sql`: transaktionale, wiederholungssichere Migration mit Lock-Timeout. Zuerst vollständig mit ROLLBACK ausgeführt, danach mit COMMIT. Vorwerte samt bisherigen Spaltendefaults liegen in PostgreSQL unter `codex_security_backup.attribution_20260917`, Schema und Tabelle ohne PUBLIC-Berechtigung. Keine Inhalte in Toolausgaben ausgegeben.
- Bestand vor Migration: 13.771 Splitter, davon genau einer mit verborgener Herkunft und Status `verblasst`. Dieser wurde mit Herkunft veröffentlicht und auf `aktiv` gesetzt; Energie mindestens 0,5 und Kontaktzeit erneuert, damit er wieder als aktiver Splitter aufgenommen wird. Die normale Physik darf ihn anschließend wieder altern lassen. Elf Profilpräferenzen und eine Sichtbarkeitseinstellung wurden auf zuordenbar/zitierbar gesetzt. Vorhandene private Inhalte blieben privat.
- Der zunächst gezählte anonyme Kalendereintrag war soft-gelöscht. Er wurde ausdrücklich **nicht** wiederbelebt: Kalenderbestand weiter ein gelöschter anonymer Eintrag und vier private Einträge. Keine aktiven anonymen Kalenderinhalte zur Umstellung vorhanden. Frühere Zwischenmeldung über zwei Veröffentlichungen damit präzisiert: tatsächlich nur ein Splitter veröffentlicht.

### Aktivierung und Nachweise

Backend-Codecommit `6fa894a75f`, Backup `faac933a42`, vor Neustarts `0b49c0606a`. Surface-Backup `e2c9956d314` bewahrt vorherige erzeugte Ausgaben und Sitemap. Beim Prüfen des echten Login-Codes fiel auf, dass `ftw_token` bereits `Bearer ` enthalten kann; der neue Archiv-Helfer erhält dieses Präfix statt es zu verdoppeln. Zusätzlicher Node-Test dafür bestanden.

Surface gebaut mit `node --experimental-strip-types /vps_root/flextrawurst/scripts/build_surface.ts` aus `/vps_root/flextrawurst`: erfolgreich. Das bevorzugte lokale `npx --no-install tsx` war mangels installiertem tsx nicht ausführbar; keine Installation vorgenommen. Der Host-Tool-Aufruf aus `/root/flextrawurst` wurde wegen nicht freigegebenem Arbeitsordner abgewiesen; keine Umgehung, Build stattdessen regulär in der verfügbaren lokalen Mount-Umgebung.

116 Surface-Tests bestanden im Build-Lauf; acht Splitter-/Defaulttests, fünf Profiltests, fünf Archivtests, drei Admin-Verifier-Tests und zwei Archiv-Clienttests bestanden. Python-Syntax und gezielte Diff-Prüfung bestanden. `welt-api.service` und `splitter-physik.service` kontrolliert neu gestartet, beide active. Node-/nginx-Neustart nicht nötig.

Live-HTTP: Health 200; alle vier Archivfamilien anonym 403; existierender Archivschlüssel 200 mit `Cache-Control: private, no-store`; öffentliche HTTPS-Surface 200 und neuer Archiv-Helfer im ausgelieferten HTML vorhanden. Detail und Spur des tatsächlich freigegebenen Splitters je 200, Herkunft in beiden Antworten vorhanden. Schlüssel und Ursprung-ID nicht protokolliert. Neue Datenbankabfrage: null Splitter mit verborgener Herkunft. Vollständiger Browserlogin/-klicktest weiterhin nicht durchgeführt; keine Recorder-Live-Stufe als PASS behauptet.

Noch offene Sicherheitsbefunde bleiben offen, insbesondere weitere rohe Metadaten-/Quellenpfade und globale JWT-Altpunkte. Diese Aktivierung ist keine vollständige Sicherheitsabnahme. Der neue Default ist keine allgemeine Veröffentlichung privater Tagebücher, Notizen oder interner Events.

### Abschlussprüfung und Build-Einschränkung

HTTPS-Gegenprobe mit kurzlebigem, lokal signiertem Token eines tatsächlich aktiven Admin-Kontos: Archivgruppen 200, `/api/me/zitierbarkeit` 200 mit `zitierbar_standard=true`, `/api/me/sichtbarkeit` 200 mit Zitierbarkeit true und allen drei Anonymitätswerten false. Dies prüft den Token-/Rollenpfad, nicht einen Browser-Passwortlogin. Keine Token oder Schlüssel protokolliert.

Frontend-Commit `cb1bcb71fc0` enthält den Archiv-Helfer und die erzeugten Varianten. Abschlussvergleich gegen `e2c9956d314` zeigte zusätzlich einen unbeabsichtigten Verlust des vorgerenderten Guardianstyle-Blocks: Der lokale Build findet die nur auf dem Host liegende `/root/.claude/.guardianstyle_banner_state.json` nicht. Nach Backup `6edb7169827` wurde ausschließlich dieser Block aus dem vorherigen Stand in `/vps_root/flextrawurst/out/surface/flextrawurst_surface.html` und `/vps_root/flextrawurst/out/process_camera/flextrawurst_surface.html` erhalten. Die öffentlichen Varianten bleiben ohne Archivtexte, der neue Archiv-Helfer bleibt in allen vier Varianten vorhanden. Bytegleicher Blockvergleich bestanden. Andere gleichzeitig veränderte Chat-/Spawner-Ausgaben wurden nicht angefasst.

Wichtig für spätere Builds: In dieser lokalen Mount-Umgebung nicht erneut blind bauen; sonst fehlt der vorgerenderte Host-Archivblock wieder. Der Live-API-Ladeweg bleibt vorhanden. Die Host-Datei wurde nicht verändert.

Der zunächst fehlschlagende Surface-Test suchte das erste `const views` im gesamten HTML und traf ein historisches Codezitat im erhaltenen Archivblock. In `/vps_root/flextrawurst/tests/surface_ring_23.test.ts` prüft er nun ausschließlich echte `<script>`-Blöcke und die `switchView`-Funktion. Der kombinierte Lauf aus Surface- und Archiv-Clienttests ergibt danach **118/118 bestanden**; kein Tab wurde entfernt und der Test wurde nicht abgeschwächt. Browser-E2E und Graphify-Aktualisierung bleiben ohne Nachweis.
## 2026-09-18 — SEC-001: menschliche Konten bei jeder Tokenprüfung aktualisieren

Der zentrale Prüfer in `/root/werkraum/welt/auth.py` kontrolliert nach erfolgreicher JWT-Prüfung für menschliche UUID-Identitäten den aktuellen Datensatz in `human_users`. Fehlende/inaktive Konten werden abgewiesen, die aktuelle Datenbankrolle ersetzt das alte Rollenclaim. Keine Zwischenspeicherung; Datenbankfehler geben keine alten Rechte frei. Die Datenbankkonfiguration stammt aus derselben Umgebungsvariablen wie bei der Welt-API. Pro Prüfung entsteht eine zusätzliche kurze Datenbankverbindung; keine Lastmessung durchgeführt.

Die bestehende Trennung ist beachtet: Entity-Tokens und benannte interne Dienstidentitäten sind von diesem menschlichen Kontocheck ausgenommen. Insbesondere `/root/werkraum/welt/weltfutter.py`, `/root/werkraum/welt/wesen_vault_splitter.py` und `/root/werkraum/welt/flarum_archiv_splitter.py` erzeugen benannte Admin-Diensttokens. Deren Berechtigungen und Widerruf bleiben eine offene Teilaufgabe; sie wurden nicht durch eine neue Allowlist als sicher erklärt. Menschliche Konten haben laut `/root/werkraum/welt/schema_menschen.sql` UUID-Primärschlüssel.

Zusätzlich verifiziert `/root/werkraum/welt/groups_api.py` vor jeder eingehenden Chataktion das Token erneut und verwendet die aktuelle Rolle für Gruppenrechte. Gesperrte/abgelaufene Sitzungen schließen mit 4001, weggefallene Gruppenrechte mit 4003. Die Prüfung läuft außerhalb des Eventloops im Executor. Das betrifft Schreiben und Tippanzeige; eine bereits verbundene, nur passiv empfangende Sitzung wird damit noch nicht aktiv bei einer Kontosperre aus dem Broadcast-Verteiler entfernt. Diese Empfangsgrenze bleibt offen.

Prüfung: zehn neue Tests in `/root/werkraum/tests/test_auth_account_status.py` und `/root/werkraum/tests/test_group_chat_account_status.py` bestanden. Sie führen echte isolierte Funktionen mit synthetischen JWT-/DB-/Socket-Abhängigkeiten aus: Rollenentzug, Sperre, Löschung, DB-Ausfall, ungültige Signatur, Legacy-user_id, unveränderte Dienst-/Entity-Verträge, erneute Prüfung offener Chats und zulässige Tippanzeige. Dazu bestehende drei Admin-, fünf Archiv- und acht Splittertests bestanden. Gezieltes `git diff --check` bestanden. Graphify weiterhin nicht installiert (Exit 127).

Produktionsabgleich ohne Datenänderung: aktueller Admin mit signiertem altem Mensch-Claim erhält HTTP 200; aktiver Nichtadmin mit signiertem altem Admin-Claim erhält HTTP 403 bei `/auth/admin-check`; sein normaler `/me`-Zugriff bleibt 200; fehlende UUID erhält 401. Health 200 und anonymer Archivzugriff 403. Testtokens mit 30 Sekunden Laufzeit wurden nur im Prozess gehalten und nicht ausgegeben. Kein vorhandenes inaktives Menschenkonto: dessen HTTP-Fall nicht ausgeführt, Sperre deshalb durch isolierten Test belegt. Kein Browserlogin und kein echter Gruppenchat verändert. Ein erster Shell-Test scheiterte am veralteten DB-Standardzugang; danach gezielt die relevante Konfiguration des laufenden Dienstes im Speicher übernommen, keine Secrets protokolliert.

Codecommits `dfeaed8dfa` und `c4cec447da`; Backups `f25841b8a1`, `963eacb3b2`, `09fc548732`, `ba895ae1c7`. Welt-API nach beiden Schritten neu geladen. Abschließender HTTPS-Abgleich auch gegen die reguläre Verwaltungsroute `/admin/users`: tatsächlicher Nichtadmin mit altem Admin-Claim 403, tatsächlicher Admin mit altem Mensch-Claim 200; Health 200. Andere Services nicht neu gestartet. SEC-001 damit für neu geprüfte menschliche Sitzungen repariert, insgesamt **teilweise offen**: Dienst-/Entity-Lebenszyklus, passive Streams, nichtzentral prüfende Prozesse und Passwortwechsel-/Einzelsitzungswiderruf sind nicht als erledigt ausgewiesen.

## 2026-09-18 — Wiederaufnahme: Gruppenchat-Empfangswiderruf live

Anschluss aus `/config/.codex/sessions/2026/09/07/rollout-2026-09-07T18-21-47-01a07cac-fefe-70f2-b28a-b8c5c1810be0.jsonl`: Der letzte Auftrag war die Untersuchung der Diensttokens und passiver Verbindungen. Das Log endet am 17. September um 23:46 UTC mit `usage_limit_exceeded`, während ausschließlich gelesen wurde. Die separate Blender-Arbeit gehört nicht zu dieser Fortsetzung.

In `/root/werkraum/welt/ws_manager.py` benötigt jede Verbindung nun einen Rechteprüfer. Jede Nachricht, Tippanzeige, Präsenzmeldung und Senderbestätigung wird erst nach dessen erneuter Prüfung ausgeliefert. Entfernte Verbindungen werden auch nach wartender Prüfung nicht wieder bedient; Broadcasts iterieren über einen Snapshot, damit paralleles Trennen keinen Mengenänderungsfehler erzeugt. `/root/werkraum/welt/groups_api.py` prüft aktuelle Tokenidentität und die bestehenden `_can_post_group`-Rechte. Stille Verbindungen werden nach jeweils 30 Sekunden Empfangswarten erneut geprüft. Es gibt keinen Berechtigungscache. Codes: ungültiges Token/Identitätswechsel 4001, verlorenes Gruppenrecht 4003, sonstiger Prüfungsfehler 1011. Vorhandene Chat-Zugangsregeln wurden nicht erweitert.

Nachweise:
- Sieben neue Tests in `/root/werkraum/tests/test_group_chat_receive_revocation.py`: passive Kontosperre, Rollen-/Mitgliedschaftsentzug, Identitätswechsel, DB-Ausfall, stiller Empfang, andere weiterhin berechtigte Empfänger, Entfernung während wartender Prüfung.
- Zwei neue Tests in `/root/werkraum/tests/test_group_chat_asgi.py`: echte FastAPI/Starlette-TestClient-WebSockets mit echtem Manager und echter extrahierter Routenfunktion, synthetischer Auth/DB. Empfang nach Rechteentzug geschlossen mit 4003; stilles Socket nach Kontosperre mit 4001. Ausschließlich im Test ist das 30-Sekunden-Intervall auf 50 ms verkürzt.
- Zusammen mit den drei bisherigen Chataktionstests: **12/12 auf dem Host mit `/root/werkraum/venv/bin/python3` bestanden**. Außerdem sieben Kontostatus-, fünf Archiv- und acht Splittertests lokal bestanden; insgesamt 32 unterschiedliche Tests.
- Backup `6d78448fbd`, Codecommit `8fe3c1e191`, Aktivierungs-/Dokumentationsbackup `247cf763c8`. Nur `welt-api.service` neu gestartet. HTTPS danach: `/api/health` 200, anonymes Archiv 403, anonymes `/api/admin/users` 401.

Grenzen: Die WebSocket-Gegenproben laufen über ASGI im Testprozess, nicht gegen produktive Kontosperren oder einen Browser. Produktive Gruppen/Konten/Inhalte wurden nicht verändert. Die 30 Sekunden sind das Empfangswartungsintervall, keine harte Frist einschließlich Datenbank- und Netzwerklatenz. Zusätzliche Datenbankabfragen pro Empfänger und Auslieferung sind nicht lastvermessen. Bereits vor einer Sperre ausgelieferte Daten können nicht zurückgerufen werden. Andere Stream-Arten bleiben ungeprüft. `graphify update .` erneut versucht: Programm fehlt (Exit 127).

### Diensttokens: konkrete Bestandsaufnahme, noch keine Rechteumstellung

Neun benannte Admin-Identitäten in den untersuchten aktiven Python-Aufrufern gefunden:

| Identität | Nachgewiesener Erzeuger / Verbraucher | Beobachtete API-Nutzung |
|---|---|---|
| `weltfutter` | `/root/werkraum/welt/weltfutter.py` | Splitter erstellen |
| `wesen-vault-sampler` | `/root/werkraum/welt/wesen_vault_splitter.py` | Splitter erstellen |
| `flarum-archiv-sampler` | `/root/werkraum/welt/flarum_archiv_splitter.py` | Splitter erstellen |
| `codex-abwurf` | `/root/werkraum/_codex/tools/codex_abwurf.py`, `/root/werkraum/_codex/tools/spiegel_abwurf.py`, `/root/werkraum/_codex/tools/codex_zwischenraum.py`, `/root/werkraum/_codex/tools/codex_zwischenraum_scan.py` | Erstellen; Liste lesen und Einsammeln anfordern |
| `kimi-abwurf` | `/root/werkraum/_kimi/tools/kimi_abwurf.py`, `/root/werkraum/_kimi/tools/spiegel_abwurf.py`, `/root/werkraum/_kimi/tools/kimi_zwischenraum.py`, `/root/werkraum/_kimi/tools/kimi_zwischenraum_scan.py` | Admin-Tokenausgabe nachgewiesen; Endpunktmatrix noch vollständig prüfen |
| `claude-abwurf` | `/root/werkraum/_claude/tools/claude_abwurf.py`, `/root/werkraum/_claude/tools/spiegel_abwurf.py`, `/root/werkraum/_claude/tools/claude_zwischenraum.py`, `/root/werkraum/_claude/tools/claude_zwischenraum_scan.py` | Admin-Tokenausgabe nachgewiesen; Endpunktmatrix noch vollständig prüfen |
| `dak-abwurf` | `/root/werkraum/_shared/tools/dak_abwurf.py` | Admin-Tokenausgabe nachgewiesen; Endpunktmatrix noch vollständig prüfen |
| `system-abwurf` | `/root/werkraum/codewesen_abwurf.py` | Erstellen; öffentliche Liste und Einsammeln |
| `dakgord-abwurf` | `/root/werkraum/web_chat.py` | Splitter erstellen |

Die bestehenden Tokens besitzen weiterhin allgemeine Adminrechte; weder ihre Aussteller noch Signierschlüssel oder Lebenszyklen wurden verändert. Eine bloße Namens-Allowlist wäre keine Begrenzung auf tatsächlich benötigte Aktionen. Nächster Dienstblock: vollständige Endpunktmatrix, eng begrenzte serverseitige Dienstrechte und Widerruf mit Negativtests für sonstige Adminrouten; erst danach gemeinsam migrieren. Ein gemeinsamer Signierschlüssel bleibt dabei eine eigene Vertrauensgrenze.

Zusätzlicher statischer Befund in `/root/werkraum/welt/api.py`: `splitter_einsammeln` erwartet `claims.get("sub")` und `human_id`, aber `/root/werkraum/welt/auth.py` liefert `user_id`, `role`, `username`. Die untersuchten Einsammel-Aufrufer erhalten nach diesem Codepfad 401 statt einer identifizierten Sammlung. Keine produktive Einsammlung zum Beweis ausgelöst. Nicht durch pauschales Ergänzen eines `sub`-Claims reparieren: Das würde bisher abgewiesene Schreibaktionen aktivieren und braucht vorher einen eigenen Identitäts-/Herkunftsvertrag und Regressionstests.

## 2026-09-18 — Dienstrechte umgesetzt und live geprüft

Die Dienstrechte-Migration aus `/root/werkraum/welt/migrate_service_principals_20260918.sql` wurde nach Vorprüfung committed ausgeführt. `auth_service_principals` enthält zehn aktive Einträge: `weltfutter`, `wesen-vault-sampler`, `flarum-archiv-sampler`, `codex-abwurf`, `claude-abwurf`, `kimi-abwurf`, `gemini-abwurf`, `dak-abwurf`, `dakgord-abwurf` und `system-abwurf`. Die Migration schreibt ein internes Ereignis `auth.service_policy_migrated`; ein erneuter Lauf reaktiviert keine deaktivierten Einträge und überschreibt keine bestehende Richtlinie.

`/root/werkraum/welt/auth.py` lehnt benannte Diensttokens in allen normalen Prüfpunkten ab. Nur der explizite Splitter-Erzeugerpfad darf mit `allow_service=True` prüfen; er lädt `is_active` und `grants` bei jeder Anfrage aus `auth_service_principals`, verlangt `splitter:create`, bindet `origin_type` und `entity_id`, verbietet `human_id` und schreibt Dienstherkunft in `splitter.meta` sowie ein internes `splitter.service_created`-Event. `/root/werkraum/welt/service_auth.py` stellt Admin-Liste und Änderung mit Suche, Pagination und Sortierung bereit; Diensttokens selbst dürfen diese Verwaltung nicht benutzen.

Nachweise: 120 PostgreSQL-/HTTP-Assertions liefen in einer vollständig zurückgerollten Transaktion. Danach wurden die zehn aktiven Richtlinien committed und die Welt-API neu gestartet. Über HTTPS: alle zehn alten Diensttokens erhalten bei `/admin/users`, `/me` und `/admin/auth/services` 401; ein Dienstversuch mit fremder Herkunft erhält 403; die normale Admin-Anmeldung erhält 200 bei `/admin/users` und `/admin/auth/services`; `/health` bleibt 200; anonymes Archiv bleibt 403. 45 Regressionstests einschließlich zehn neuer Diensttoken-Tests bestanden. Keine Test-Splitter oder Test-Events wurden committed. Codecommit `78c697908a`; Aktivierungsbackup `13034290d9`; Dokumentationsbackup `30cafa6bd9`.

Historische Vertrauensgrenze dieser Stufe: Menschliche und Diensttokens nutzten weiterhin denselben HS256-Schlüssel aus `WELT_JWT_SECRET` beziehungsweise `/root/werkraum/welt/.jwt_secret`. Die DB-Grants begrenzten bereits ausgestellte Tokens; Zugriff auf den gemeinsamen Signaturschlüssel erlaubte weiterhin fremde Identitäten. Dieser damalige Stand ist durch die folgende Stufe überholt. Der Einsammelpfad bleibt für Diensttokens gesperrt; der `sub`/`user_id`-Vertragsfehler ist unverändert offen.

## Nachtrag 2026-09-18: Dienstschlüssel live getrennt

Alle zehn Dienste verwenden nun eigene Ed25519-Schlüssel; 20 Erzeugerdateien sind umgestellt. Alte HS256-Diensttokens werden zurückgewiesen, der menschliche/Wesen-Vertrag bleibt bestehen. 210 PostgreSQL-/HTTP-Assertions mit Rollback, 38 Regressionstests, 53 Live-HTTP-Prüfungen und eine tatsächliche Rotation bestanden. Vollständige Evidenz, Betriebsdetails und Grenzen: /root/werkraum/_codex/berichte/2026-09-18-dienstschluessel-live.md. Gemeinsame Root-Rechte bleiben offen; diese Änderung behauptet keine Unix-Prozessisolation.
