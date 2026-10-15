# flextrawurst — fortlaufender Sicherheitsreview

Stand: 2026-09-07, 16:35 UTC. Autor: Codex, externe Review-Session bei Daniel.

## Auftrag und Status

Daniel beauftragt einen möglichst umfassenden Sicherheitsreview mit Angreiferblick und verlangt alle Befunde in einer Markdown-Datei. Dies ist ein bestellter Fachbericht, keine Session-Reflexion. STATUS: IN ARBEIT; kein vollständiges Sicherheitsaudit und kein Sicherheitsfreibrief.

Nur lesende Quellcodeprüfung und isolierte Tests. Keine produktiven Angriffe, Kontenänderungen, Datenbank-Schreibtests, Neustarts oder Reparaturen. Geheimniswerte werden nicht in diesen Bericht übernommen. Bestehende Änderungen anderer Sessions bleiben unberührt. Backup vor Berichtserstellung: bf58e0f6ae (leerer, auf den Bericht bezogener Sicherheitspunkt; kein Snapshot aller laufenden Fremdänderungen).

## Quellen und Abdeckung

- Zentrale API: `/root/werkraum/welt/api.py`; 300 Routenfunktionen statisch inventarisiert, nicht alle semantisch geprüft.
- Authentifizierung: `/root/werkraum/welt/auth.py` gelesen.
- Schwerpunktprüfung: Rechteprüfungen, Kontoverwaltung, Avatar-/Widmungs-Uploads, Body-Middleware, öffentlicher Eventstream.
- Ergänzende Stichproben: `/root/werkraum/welt/wesen_dateien_api.py`, `/root/werkraum/welt/denkstream_api.py`, `/root/werkraum/welt/reibungsgewebe_api.py`, `/root/werkraum/welt/admin_einsicht_api.py` und erzeugte Oberfläche `/root/werkraum/flextrawurst/flextrawurst_surface.html`.
- Architekturorientierung: `/root/werkraum/graphify-out/GRAPH_REPORT.md`, historischer Stand 2026-08-15; kein Nachweis des aktuellen Deployments.
- Quellbaum jetzt gefunden: `/vps_root/flextrawurst`, insbesondere `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts`. Frühere Aussage, der Quellbaum fehle, war nur für `/root/flextrawurst` richtig. Der Host-Mount wurde inzwischen gefunden.
- Host-Konfiguration: `/vps_system/etc`. Verknüpfungen unter `/vps_system/etc/nginx/sites-enabled` müssen auf ihre tatsächlichen Mount-Ziele aufgelöst werden; die Container-Konfiguration unter `/etc/nginx` beweist nichts über den Host-Proxy.
- `/root/werkraum` verweist auf `/vps_root/werkraum`. Der Arbeitsbaum enthält fremde/laufende Änderungen, auch an `/root/werkraum/welt/api.py`; Ergebnisse gelten für die gelesenen Dateistände, nicht automatisch für den laufenden Prozess.

SHA-256 der Hauptquellen nach erster Prüfung:

```text
37c198a51596ced14e894314fcc324d141d300dce59e055cd5ca6c39e0471171  /root/werkraum/welt/api.py
36f77fec8a614317c3b8a0172ea8d5a9d170006dbdd069047dd6e708ba116f3b  /root/werkraum/welt/auth.py
d87cccce2005af63df40d86799bd7c1c7045f8041cd1b0a05f6cc9fa50efb7c0  /root/werkraum/welt/events_stream_api.py
```

## SEC-001 — Bestehende Tokens überleben Kontosperre und Rechteentzug

Priorität: HOCH. Status: Codebefund und isolierter Kontrollflusstest; kein produktiver Exploit.

Fundstellen:

- `/root/werkraum/welt/auth.py:12`: reguläre Tokenlaufzeit sieben Tage.
- `/root/werkraum/welt/auth.py:39`: Rolle wird in das Token geschrieben.
- `/root/werkraum/welt/auth.py:48`: Signatur-/Ablaufprüfung, anschließend Rückgabe der Tokenrolle ohne Kontostatusabfrage.
- `/root/werkraum/welt/api.py:389`: `_require_auth` übernimmt diese Claims.
- `/root/werkraum/welt/api.py:398`: `_require_admin` prüft nur die Tokenrolle.
- `/root/werkraum/welt/api.py:1362`: Rollen-/Statusänderung aktualisiert die Datenbank.
- `/root/werkraum/welt/api.py:8044`: Sperren/Löschen widerruft keine Tokens.

Angriffsbedingung: Ein Angreifer besitzt ein noch gültiges Token eines anschließend gesperrten oder herabgestuften Kontos. Besonders relevant ist ein bereits entwendetes Admin-Token. Es handelt sich nicht um eine Möglichkeit, ohne vorhandenes Token Admin zu werden.

Auswirkung: Geschützte Routen vertrauen weiterhin den alten Rechten; incident-response-seitiges Sperren beendet die Sitzung nicht. Einzelne nachgelagerte Datenbankzugriffe können zwar scheitern, die zentrale Rechteprüfung blockiert jedoch nicht.

Beleg: Die Funktionen `_require_auth` und `_require_admin` wurden per AST isoliert, ohne Modulimport, mit synthetischem Tokenprüfer ausgeführt. Admin-Claims wurden ohne irgendeinen Kontostatus-Provider akzeptiert. Dies testet den Kontrollfluss, nicht die kryptografische Tokenvalidierung. Die echte Tokenvalidierung wurde separat im Quelltext gelesen.

Empfehlung: Aktuellen Kontostatus und Berechtigungen prüfen, serverseitige Session-/Tokenversion oder Widerrufsmechanismus einführen; Sperren und Rollenwechsel müssen vorhandene Sessions entwerten. Referenz: https://github.com/OWASP/ASVS/blob/master/5.0/en/0x16-V7-Session-Management.md (7.4.2).

## SEC-002 — Moderationsstatus schützt hochgeladene Bilder nicht vor direktem Abruf

Priorität: MITTEL. Status: Durchgängiger Codepfad; HTTP-Erreichbarkeit des Deployments noch ungeprüft.

Fundstellen:

- `/root/werkraum/welt/api.py:77`: `/uploads` wird ohne Authentifizierung als statisches Verzeichnis eingebunden.
- `/root/werkraum/welt/api.py:746`: Avatar-Upload schreibt Bytes vor Moderationsfreigabe in dieses Verzeichnis und gibt den Pfad zurück.
- `/root/werkraum/welt/api.py:791`: Widmungen verwenden ebenfalls den öffentlichen Speicher.
- `/root/werkraum/welt/api.py:7616`: Avatar-Ablehnung ändert nur den Datenbankstatus.

Angriffsbedingung: Registrierter Uploader kennt seine zurückgegebene Avatar-URL und teilt sie. Zufällige Dateinamen verhindern diesen Fall nicht. Kein Erraten fremder URLs erforderlich.

Auswirkung: Ungeprüfte oder abgelehnte Inhalte bleiben auf Anwendungsebene über direkte URLs abrufbar, obwohl Listen/Moderationsoberflächen den Status berücksichtigen. Das ist keine nachgewiesene Codeausführung oder XSS.

Empfehlung: Wartende/abgelehnte Dateien außerhalb des öffentlichen Webverzeichnisses halten oder jeden Abruf über einen statusgeprüften Handler führen. Herkunft und Moderationshistorie erhalten, nicht still löschen. Referenz: https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html.

## SEC-003 — Globales Body-Limit prüft nur die deklarierte Größe

Priorität: MITTEL, Betriebswirkung abhängig vom Proxy. Status: Isoliert reproduziert.

Fundstelle: `/root/werkraum/welt/api.py:85`.

Die Middleware blockiert einen zu großen `Content-Length`-Wert, zählt aber keine empfangenen Bytes. Ohne den Header wird die Anfrage unverändert weitergereicht. Die Uploadfunktionen lesen darüber hinaus jeweils den vollständigen Dateiinhalt vor ihrem eigenen Größencheck, etwa `/root/werkraum/welt/api.py:758`.

Isolierter Test mit AST-extrahierter Middleware und künstlichen Requests:

```text
Content-Length: 7340032 -> 413
Transfer-Encoding: chunked, ohne Content-Length -> PASSED_TO_APP
Keine Größenheader -> PASSED_TO_APP
```

Testgrenze: Keine großen Bodies übertragen, keine HTTP-Parser oder Produktionsdienste belastet. Multipart-Limits, Frontproxy, Direktport-Erreichbarkeit und Serverversionen sind noch abzugleichen. Der Test beweist die Lücke in dieser Middleware, nicht einen bereits erfolgreichen Speicher-DoS.

Empfehlung: Tatsächlich empfangene Bytes auf ASGI-/Stream-Ebene begrenzen; Uploads begrenzt lesen. Proxy-Limits zusätzlich prüfen, nicht als Ersatz voraussetzen.

## SEC-004 — Öffentliche Eventstreams reservieren je eine Datenbankverbindung

Priorität: POTENZIELL HOCH. Status: Ressourcenrisiko aus Quellcode; keine Lastreproduktion.

Fundstellen: `/root/werkraum/welt/events_stream_api.py:42` und `/root/werkraum/welt/events_stream_api.py:83`.

Jeder öffentliche Stream erzeugt eine eigene PostgreSQL-Verbindung und hält sie bis zum Streamende. Im Modul sind weder eine gemeinsame Listener-Verteilung noch eine globale Verbindungsobergrenze vorhanden. Das vorhandene `finally` schließt Verbindungen bei regulärem Generatorende; das Problem sind gleichzeitig offen gehaltene Streams.

Mögliche Auswirkung: Viele parallele Streams erschöpfen das Datenbank-Verbindungsbudget und beeinträchtigen andere Funktionen. Belastbare Priorisierung erfordert noch Host-Proxy-Limits, Workerzahl, PostgreSQL-Limits und Erreichbarkeit. Keine Aussage über bereits erfolgte Ausnutzung.

Empfehlung: Ein begrenzter gemeinsamer DB-Listener mit Fan-out und Backpressure sowie globale/per-client Streamlimits; Ressourcenmessung in isolierter Umgebung.

## Weitere Beobachtungen — noch keine bestätigten zusätzlichen Schwachstellen

- Uploadprüfung vertraut auf MIME-Angabe und Endung, ohne Bilddekodierung: `/root/werkraum/welt/api.py:754` und `/root/werkraum/welt/api.py:799`. Fehlende Inhaltsprüfung ist zu härten; bislang keine nachgewiesene XSS-/RCE-Kette.
- Linkvorschau löst den Host zur Prüfung und anschließend beim Abruf erneut auf: `/root/werkraum/welt/api.py:9938` und `/root/werkraum/welt/api.py:9972`. DNS-Rebinding-Restfenster ist im Code ausdrücklich dokumentiert; Endpunkt ist admin-only. Noch kein zusätzlicher hochpriorisierter Befund.
- Geheimnisliterale beziehungsweise Zugangsdaten-Fallbacks wurden im Code gesehen, unter anderem `/root/werkraum/welt/api.py:15435` und `/root/werkraum/welt/events_stream_api.py:29`. Werte werden nicht wiedergegeben. Gültigkeit, Berechtigungen, Verbreitung und tatsächliche Verwendung noch ungeprüft; keine Anmeldung damit versucht.
- `/root/werkraum/welt/admin_einsicht_api.py:25` definiert Admin-Routen ohne lokale Guards. Einbindung und äußere Schutzschicht sind unklar; nicht als öffentlicher Auth-Bypass behaupten.
- Eine AST-Inventur der Zusatzmodule brach an einem Syntaxfehler ab; deshalb keine vollständige Routenzahl aller Module aus diesem Lauf ableiten. Parserversion war Python 3.14, nicht notwendigerweise die produktive Version. Betroffene Datei noch gezielt bestimmen.

## Geprüfte Verdachtsstellen ohne bestätigten Befund

- Die scheinbar ungeschützten Schreibpfade `/root/werkraum/welt/api.py:3782` und `/root/werkraum/welt/api.py:3800` sind mit HTTP 410 stillgelegt; keine Eventmanipulation darüber belegt.
- `/root/werkraum/welt/api.py:13825` blockiert Schatten-Initiierung mit HTTP 503.
- `/root/werkraum/welt/denkstream_api.py:67` nutzt `_require_internal`; die einfache Suche nach Namen mit auth/admin/token hatte den Guard zunächst übersehen. Kein bestätigter ungeschützter Schreibpfad.
- `/root/werkraum/welt/wesen_dateien_api.py:75` löst Pfade auf und prüft die Zugehörigkeit zur erlaubten Wurzel. Das Lesen anderer Wesen-Zimmer ist ausdrücklich dokumentierte Freigabe, kein versehentlicher IDOR-Befund.

## Offene Review-Arbeit

### Nachtrag: Host-Proxy gefunden

Der Link `/vps_system/etc/nginx/sites-enabled/flextrawurst` zeigt auf den absoluten Hostpfad `/etc/nginx/sites-available/flextrawurst`; dessen hier lesbares Mount-Ziel ist `/vps_system/etc/nginx/sites-available/flextrawurst`.

- `/vps_system/etc/nginx/sites-available/flextrawurst:26` setzt ein allgemeines Body-Limit von 10 MB. SEC-003 ist daher nicht als unbegrenzter Upload über diesen Standard-Proxyweg belegt; Direktzugriff und abweichende Locations bleiben offen.
- `/vps_system/etc/nginx/sites-available/flextrawurst:789` begrenzt die Anfragerate für den allgemeinen API-Pfad. Das relativiert SEC-004, ersetzt aber nicht automatisch eine Obergrenze gleichzeitig offener Streams. Zonenparameter und geerbte Regeln noch prüfen.
- `/vps_system/etc/nginx/sites-available/flextrawurst:878` definiert zusätzlich eine direkte statische Upload-Auslieferung per Alias auf `/root/werkraum/uploads/`. Auch dieser lokale Location-Block enthält keine Moderationsstatusprüfung; SEC-002 wird dadurch auf Konfigurationsebene gestützt.

Diese Aussagen betreffen gelesene Konfiguration, nicht den Beweis, dass der laufende nginx-Prozess genau diesen Stand geladen hat.

### Nächste Prüffelder

1. Gefundenen Quellbaum `/vps_root/flextrawurst` und Host-Proxy unter `/vps_system/etc` abgleichen; aktive Dienste/Deployments read-only zuordnen.
2. Objektberechtigungen sämtlicher Routen, private Sichtbarkeit, Gruppen, Nachrichten und Suchendpunkte systematisch prüfen.
3. Frontend: vollständige Datenflussprüfung für DOM-XSS, HTML-/URL-Kontexte, Tokenablage und CSP.
4. Werkzeuge/Brücken: Pfadzugriffe, Shell-Aufrufe, SSRF, Agentenrechte und Geheimnisgrenzen prüfen. Recorder-spezifische Arbeit erst nach zugehörigem Skill-Vertrag.
5. Abhängigkeiten/Lockfiles und tatsächliche Laufzeitversionen, Dienstrechte, Netzwerkbindung und Rate-Limits inventarisieren.
6. Neue Findings in dieser Datei ergänzen; falsifizierte Verdachte sichtbar als verworfen markieren. Keine fertige Gesamtabdeckung behaupten.

## Fortsetzung: Node-Server und Proxy — 2026-09-07

Dokumentationsauftrag: Daniel verlangt ausdrücklich, auch die folgenden Erkenntnisse dauerhaft in Markdown festzuhalten. Die Prüfung wurde nach einem von Daniel gemeldeten UI-Sicherheitshinweis unterbrochen. Der Hinweis ist kein technischer Befund über flextrawurst. Die zuletzt angekündigten isolierten URL-Filtertests wurden NICHT ausgeführt. Keine produktiven Schreib-, Lösch-, SSRF- oder Lasttests durchgeführt.

### SEC-005 — Fehlender Zugriffsschutz für Wesen-Dateien und Erinnerungen

Priorität: HOCH. Status: Quellcode und gelesene Proxy-Konfiguration stimmen hinsichtlich fehlendem lokalem Zugriffsschutz überein; aktive öffentliche Bereitstellung noch nicht verifiziert.

Fundstellen:

- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:2195`: zentraler Request-Handler. `isSensitive` erfasst Werkraum-Dateirouten und Explorer, nicht die Wesen-Verwaltung. Der einzige gefundene Aufruf von `requireAuth` liegt bei Zeile 2205.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:4676`: Datenausgabe von Profil, weiteren Markdown-Dateien, Erinnerungen und Containern ohne dortige Authentifizierung.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:4697`: Dateiänderung per PUT ohne Benutzer-/Eigentümerprüfung; derselbe Routenblock enthält DELETE.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:4733`: Änderung des Wesen-Profils.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:5318`: Änderung der Erinnerungsdatei.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:5384`: Speichern/Anlegen eines Wesens, einschließlich Überschreiben vorhandener Markdown-Dateien.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:5441`: Soft-Delete eines Charakterverzeichnisses ohne lokale Authentifizierung im gelesenen Handler.
- `/vps_system/etc/nginx/sites-available/flextrawurst:1236`: allgemeiner Proxy auf Port 8787 ohne Zugriffsschutz im Location-Block. Im gelesenen Serverblock wurde kein genereller Schutz für diese Wesen-Verwaltung festgestellt.

Angriffsbedingung: Diese Quell- und Konfigurationsstände sind tatsächlich aktiv und keine bislang unbekannte äußere Schutzschicht blockiert die Anfragen. Ein Angreifer benötigt dann nach dem gelesenen Code keine Anmeldung, sondern lediglich einen Charakterbezeichner. Eine öffentliche Listenfunktion ist ebenfalls vorhanden.

Auswirkung: Fremde können Profile und Erinnerungen manipulieren, Markdown-Dateien löschen oder Wesen aus der aktiven Struktur verschieben. Das betrifft Integrität und Verfügbarkeit; die Datenausgabe kann zusätzlich Vertraulichkeit betreffen, soweit die Inhalte nicht bewusst öffentlich sein sollen. Sanitierte Dateinamen verhindern keine fehlende Berechtigungsprüfung. Provenienzlogging einzelner Änderungen ersetzt keine Autorisierung.

Prüfgrenze: Keine echte Änderung angefordert, keine fremden Erinnerungen über HTTP abgerufen, keine öffentliche Exploit-Reproduktion. Geladene Prozessversion, effektive nginx-Gesamtkonfiguration und Produktentscheidung über anonymes Schreiben noch abgleichen. Öffentliches Lesen darf gewollt sein; uneingeschränktes Überschreiben bestehender Charaktere ist davon getrennt zu entscheiden.

Behebungsrichtung: Zentraler Schutz aller zustandsändernden Wesen-Routen plus objektbezogene Rechteprüfung; öffentliche Leseansichten separat erhalten. Keine pauschale Abschaltung oder Reparatur im Rahmen dieses Reviews vorgenommen.

### SEC-006 — Unvollständige Zielprüfung beim serverseitigen URL-Lesen

Priorität: POTENZIELL HOCH. Status: statischer Codebefund, keine isolierte oder Live-Reproduktion.

Fundstellen:

- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:552`: `istSichereUrl` prüft Schema und eine begrenzte textuelle Host-Sperrliste; keine DNS-Auflösung oder vollständige Adressklassifikation.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:562`: `leseUrlMitPlaywright` startet einen Browser und navigiert zum Ziel. Im gelesenen Helfer keine Netzwerksperre für Redirects oder Unterressourcen.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:4639`: URL-Leser prüft nur die ursprüngliche URL, gibt extrahierten Text zurück und speichert ein Anhangmanifest.
- `/vps_system/etc/nginx/sites-available/flextrawurst:903`: eigener Proxy-Block für Upload/URL-Lesen ohne dortige Authentifizierung, mit 600 Sekunden Proxy-Lesezeitlimit.

Risiko: Ein formal akzeptierter Hostname kann auf interne Adressen zeigen. Weiterleitungen und von einer Seite ausgelöste Unteranfragen werden im gelesenen Code nicht erneut gegen interne Netze abgegrenzt. Die Begrenzung des extrahierten Texts verhindert keine internen Netzwerkanfragen. Die Syntaxbehandlung verschiedener IP-Darstellungen ist zusätzlich offen und wurde nicht getestet.

Mögliche Auswirkung: Server-Side Request Forgery aus dem Netzwerk des gestarteten Browsers, gegebenenfalls mit Rückgabe interner Seiteninhalte. Tatsächliche Reichweite hängt von Browserumgebung, Netzsegmentierung und erreichbaren internen Diensten ab; keine Datenentnahme oder interne Anfrage versucht.

Behebungsrichtung: Netzwerkzugriff des Browsers wirksam begrenzen und nur erlaubte Ziele zulassen; DNS-/IP-Klassifikation, Redirects und Unterressourcen gemeinsam berücksichtigen. Zugriffsschutz und Ressourcenbegrenzung zusätzlich prüfen. Dies ist ein statischer Review des allgemeinen Wesen-URL-Lesers, kein durchgeführter Recorder-/Crawler-Live-Schritt und kein bestandener Recorder-Gate-Nachweis.

### Weitere neue Prüfkandidaten — nicht als bestätigt zählen

- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:163`: `readBody` sammelt alle Datenchunks ohne eigenes Byte-Limit. Externe Proxy-Limits existieren; Direktportzugriff, gleichzeitige Requests und abweichende Locations noch prüfen. Verwandt mit SEC-003, nicht pauschal als unabhängiger erfolgreicher DoS zählen.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:2231`: ungefangenes `decodeURIComponent` im synchronen Handler kann bei ungültiger Kodierung werfen. Tatsächliche Erreichbarkeit durch den Proxy, HTTP-Parser und Prozessfehlerbehandlung noch ungeprüft. Keine fehlerhafte Anfrage gesendet, kein Prozessabsturz provoziert.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:2248`: Werkraum-Schreibpfade verwenden lexikalische Normalisierung/Präfixprüfung. Symlink-Grenzen noch offen; diese Routen haben Basic-Auth. Kein bestätigter Pfadausbruch.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:346`: Charakterbezeichner werden auf erlaubte Zeichen reduziert und mit bestehenden Verzeichnisnamen abgeglichen. Einfaches Pfad-Traversal über den Namen ist dadurch nicht belegt; SEC-005 betrifft Rechte, nicht Traversal.
- `/vps_system/etc/systemd/system/process-camera-preview.service:11` und `/vps_system/etc/systemd/system/flextrawurst-surface.service:9` referenzieren den Node-Server. Welche Unit aktiv ist und welcher Dateistand läuft, ist weiterhin nicht nachgewiesen.

Gesamtstand: Vier frühere Befunde plus zwei neue, jeweils mit unterschiedlichen Evidenzgrenzen. Keine Behauptung, dass sechs Schwachstellen live ausgenutzt oder sämtliche Komponenten geprüft wurden. Keine Anwendungsdatei geändert.

## Fortsetzung: Dienst-Wizard und echte Wesen-Container

### SEC-007 — Admin-Containeraktionen und Diensttrigger ohne erkennbaren Zugriffsschutz

Priorität: HOCH. Status: statisch nachvollzogene Kette aus Proxy, Node-Routen und Python-CLI; kein produktiver Aufruf.

Fundstellen:

- `/vps_system/etc/nginx/sites-available/flextrawurst:779`: eigener Proxy für den Dienst-Wizard auf Port 8787, ohne lokale Authentifizierung. Dieser spezifischere Pfad fällt nicht unter die Basic-Auth des benachbarten Flarumstyler-Pfads.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:2200`: zentraler Schutz umfasst diese API nicht.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:3651`: Container-Admin-Schreibroute startet `/root/werkraum/container_admin_cli.py` mit serverseitigen Rechten. Der Request bestimmt Text und Herkunftsmodus; kein überprüfter Admin-Akteur.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:3679`: entsprechender Löschpfad ohne lokale Authentifizierung.
- `/root/werkraum/container_admin_cli.py:22`: CLI reicht Eingaben direkt an Containerfunktionen weiter; es ist keine eigene HTTP-Authentifizierungsschicht.
- `/root/werkraum/codewesen_container.py:278`: Admin-Schreibfunktion erzeugt den Inhalt und protokolliert den Vorgang ausdrücklich als Daniel-Eingriff.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:3495`: manueller Diensttrigger ohne lokale Authentifizierung; Trockenlauf ist optional, nicht zwingend.
- `/root/werkraum/welt/wesen_dienst_ausloesen.py:39`: Trigger schreibt die von laufenden Diensten ausgewertete Flag-Datei.

Auswirkung bei aktivem Deployment dieser Stände: Unangemeldete Aufrufer könnten echte Wesen-Container verändern und Vorgänge fälschlich Daniel zuschreiben lassen. Der angebotene Modus `admin_still` lässt den Eingriff in der Wesen-Ansicht unmarkiert; das Systemprotokoll existiert weiter, schreibt aber keinen authentifizierten Aufrufer fest. Diensttrigger könnten außerdem einen Zyklus vorhandener laufender Dienste anstoßen. Weder Fremdänderungen noch Trigger wurden ausprobiert.

Abgrenzung zu SEC-005: Hier geht es um die CLI-Brücke in die echten Codewesen-Container und operative Diensttrigger, nicht nur um die vier Charakter-Spawner. Gemeinsame Grundursache ist eine fehlende Zugriffskontrolle, die betroffenen Ressourcen und Folgen unterscheiden sich.

Weitere Oberfläche derselben Schutzlücke: `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:3424` bietet das Erzeugen von Dienstdefinitionen. Der gelesene Wrapper ruft `/root/werkraum/welt/wesen_dienst_erzeugen.py` auf; der Generator selbst wurde noch nicht vollständig geprüft. Keine beliebige Codeausführung behaupten. Eine Dienstdefinition zu erzeugen ist zudem nicht gleichbedeutend damit, den Dienst zu starten.

Behebungsrichtung: Explizite serverseitige Admin-Autorisierung für diese Operationen, Trennung öffentlicher Wizard-Ansichten von operativen Funktionen und Protokollierung des überprüften Akteurs. Eine Bestätigung im Request oder eine sichere Argumentliste für den Unterprozess ersetzt keine Berechtigungsprüfung.

### SEC-008 — Löschhelfer begrenzt Dateiziel nicht auf den Container

Priorität: HOCH, tatsächliche Reichweite abhängig von Prozessrechten. Status: statischer Datenflussbefund; keine Löschreproduktion.

Fundstellen:

- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:3679`: der Routenparameter für den Dateinamen wird erst nach dem Regex-Match dekodiert und ohne anschließende Pfadbegrenzung an das CLI weitergegeben.
- `/root/werkraum/container_admin_cli.py:34`: Dateiname wird als freies Argument angenommen und an den Löschhelfer übergeben.
- `/root/werkraum/codewesen_container.py:308`: `admin_entferne` setzt das Ziel aus Basis, Container und Dateiname zusammen. Geprüft werden nur Existenz und der spezielle geschützte Basisname; anschließend folgt `unlink()`.

Problem: Es fehlt eine Prüfung, dass der dekodierte Dateiname wirklich nur ein Dateiname ist und das aufgelöste Ziel im erlaubten Container liegt. Absolute Pfade oder Elternverzeichnisanteile können diese Eigenschaft verletzen. Das ursprüngliche Regex verbietet rohe Schrägstriche, nicht solche, die erst beim Dekodieren entstehen. Sichere Container-Namen allein schließen die Lücke im separat übergebenen Dateinamen nicht.

Mögliche Auswirkung: Löschen von Dateien außerhalb des beabsichtigten Containers, soweit der Node-/CLI-Prozess dazu berechtigt ist und der Transport die Eingabe durchlässt. Keine Aussage, dass beliebige Systemdateien tatsächlich löschbar sind; keine Dateien angefasst und keine Umgehungsanfrage gesendet. Proxy-Normalisierung und aktive Prozessrechte bleiben zu prüfen. SEC-007 macht den fehlenden Schutz dieser Funktion besonders relevant; auch nach Authentifizierung bleibt die Pfadgrenze erforderlich.

Behebungsrichtung: Nur einen erlaubten einzelnen Dateinamen beziehungsweise eine serverseitig aufgelöste Eintrags-ID akzeptieren; aufgelöste Ziele und Symlinks gegen die erlaubte Wurzel prüfen. Keine destruktive Bereinigung im Review.

### Negativbefund und Prüfgrenzen dieser Runde

- `/vps_system/etc/nginx/sites-available/flextrawurst:765` schützt die Flarumstyler-API mit Basic-Auth. Die dortigen Start-/Stop-/Restart-Routen werden deshalb NICHT als öffentlich ungeschützt gewertet. Ihr eigener Node-Schutz und eine mögliche Direktport-Exposition sind getrennte offene Fragen.
- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:3144` prüft Dienstzugehörigkeit und eine Steuerbarkeitssperre; Befehle werden mit `execFileSync` und Argumentlisten ausgeführt. Keine Shell-Injection aus diesen Stellen belegt.
- Ausschließlich Code und Konfiguration gelesen. Kein Python-Modul mit Laufzeitnebenwirkungen importiert; keines der Verwaltungs-CLIs gestartet; keine Dienste gestartet, gestoppt oder ausgelöst.
- Stand nun SEC-001 bis SEC-008 mit jeweils ausgewiesenen Grenzen. Kein vollständiger Review, keine acht live bewiesenen Exploits.

## Selbstständige Fortsetzung — Profile, Gruppenchat und zusätzliche Serverflächen

### SEC-009 — Persistente HTML-Injection / Stored-XSS-Codepfad im Menschenprofil

Priorität: HOCH. Status: Datenfluss statisch nachvollzogen; ungefilterte HTML-Übernahme in isoliertem JavaScript-Test bestätigt. Keine Browser-Codeausführung und keine produktive Profilerstellung durchgeführt.

Fundstellen:

- `/root/werkraum/welt/api.py:443`: `ProfilePatch` akzeptiert `avatar_symbol`, `profil_farbe` und `profil_hintergrund` als freie Strings.
- `/root/werkraum/welt/api.py:701`: das Avatar-Symbol wird unverändert in das Profil geschrieben; Farbfelder werden ebenfalls ohne Formatvalidierung gespeichert.
- `/root/werkraum/welt/api.py:1014`: öffentliche Menschenliste gibt diese Profilwerte zurück.
- `/vps_root/flextrawurst/out/process_camera/flextrawurst_surface_public.html:18604`: `loadMenschenListe` setzt die Liste per `innerHTML` zusammen. `avatar_symbol` wird als HTML eingesetzt; `profil_farbe` gelangt ohne kontextspezifisches Escaping in Attribute.
- `/vps_root/flextrawurst/out/process_camera/flextrawurst_surface_public.html:18755`: die Profildetailansicht übernimmt das Avatar-Symbol ebenfalls ungefiltert.
- Entsprechender älterer Ausgabepfad: `/root/werkraum/flextrawurst/flextrawurst_surface.html:11214` und `/root/werkraum/flextrawurst/flextrawurst_surface.html:11351`.

Angriffsbedingung: Ein normaler Profilinhaber kann die betreffenden Felder verändern; ein anderer Besucher öffnet die Menschenansicht. Für das Avatar-Symbol muss der Renderer den Symbol-Fallback statt eines genehmigten Avatarbilds verwenden. Es ist keine Admin-Berechtigung zur Eingabe nötig.

Beleg: Nur `loadMenschenListe` aus dem öffentlichen HTML-Build wurde in einer isolierten Node-VM mit künstlichem `fetch`, DOM-Attrappe und einem harmlosen fett formatierten Marker ausgeführt. Ergebnis: `AVATAR_RAW_HTML_REACHES_INNERHTML true`. Kein Skript im Marker, kein Browserstart, keine Netzverbindung, keine Tokenverwendung, kein Profil geschrieben. Das bestätigt HTML-Injection; die Stored-XSS-Bewertung folgt aus der unbeschränkten aktiven HTML-Senke, nicht aus einem live ausgeführten Exploit. CSP/WAF und aktive Auslieferung bleiben getrennte Deploymentfragen.

Mögliche Auswirkung: Aktive Inhalte im Origin der Anwendung; damit unter Umständen Zugriff auf dortige Sitzungsdaten und Aktionen mit Besucherrechten. Tatsächlicher Tokenzugriff wurde NICHT getestet. Ein allgemeiner CSP-Header wurde im gelesenen vHost nicht gefunden; vollständige effektive Header sind nicht vermessen.

Behebungsrichtung: Symbol als Textknoten darstellen; Farbfelder auf erlaubte Farbformate begrenzen und Attribute sicher setzen. Den erzeugenden Template-/Build-Pfad lokalisieren und dort korrigieren, nicht ausschließlich generierte HTML-Dateien patchen. Keine Änderung im Review.

### SEC-010 — Private Profile werden in der öffentlichen Menschenliste ausgegeben

Priorität: MITTEL. Status: SQL- und Rückgabepfad statisch belegt; keine privaten Nutzerdaten abgerufen.

Fundstellen: `/root/werkraum/welt/api.py:1014`, insbesondere Bedingungen bei Zeile 1020 und SELECT bei Zeile 1034. Vergleich: `/root/werkraum/welt/api.py:1067`.

Die Liste filtert auf aktive Benutzer und optional Suchtext, nicht auf `human_profiles.visibility`. Sie liefert unter anderem Benutzer-ID, Namen, Bio, Tags und Avatar-Symbol. Der Detailendpunkt prüft dagegen ausdrücklich `p.visibility = 'public'`. Nutzer können die Profilsichtbarkeit über `/root/werkraum/welt/api.py:703` selbst setzen.

Auswirkung: Die Detailansicht kann ein privates Profil korrekt mit 404 verbergen, während die öffentliche Liste wesentliche Teile trotzdem preisgibt. Das ist eine serverseitige Inkonsistenz; eine ausgeblendete Detailansicht kompensiert sie nicht.

Behebungsrichtung: Dieselbe Sichtbarkeitsregel auf Liste, Suche und Detailansicht anwenden. Regressionstest mit aktiven öffentlichen und privaten synthetischen Profilen; kein Test gegen echte private Profile durchgeführt.

### SEC-011 — Öffentliche Profilantwort hebt Anonymität von Inhalten auf

Priorität: HOCH wegen möglicher sensibler Tagebuch-/Trauminhalte. Status: statischer Datenflussbefund; keine Betroffenenzahl oder tatsächliche Offenlegung erhoben.

Fundstellen:

- `/root/werkraum/welt/api.py:1103`: Profilabfragen wählen Tagebuch-, Notiz-, Traumtagebuch- und Kalendereinträge mit `sichtbarkeit IN ('public','anonym')`, jeweils nach dem konkreten Benutzer gefiltert.
- `/root/werkraum/welt/api.py:1198`: dieselbe Antwort enthält Benutzer-ID, Benutzername und Anzeigename.
- `/root/werkraum/welt/api.py:1226`: die abgefragten Inhalte werden darunter in `welt_spuren` ausgegeben.
- `/root/werkraum/welt/api.py:1211`: auch `gedankenwelt` wird zusammen mit `gedankenwelt_anonym` und der Identität zurückgegeben.
- `/root/werkraum/flextrawurst/flextrawurst_surface.html:3543`: Oberfläche beschreibt anonyme Gedankenwelt ausdrücklich als Darstellung ohne Namensnennung.

Angriffsbedingung: Der Nutzer hat ein öffentliches Profil und zugleich anonym veröffentlichte Inhalte. Das Profil darf öffentlich sein, ohne dass damit automatisch auf die Anonymität aller anderen Inhalte verzichtet wird.

Auswirkung: Ein Empfänger kann anonym markierte Einträge unmittelbar dem konkreten Profil zuordnen; UI-seitiges Weglassen eines Namens verhindert die Zuordnung in der API-Antwort nicht. Zusätzlich gibt die Antwort Gesamtzahlen privater Einträge aus; ob diese Zähler bewusst öffentlich sein sollen, ist eine separate Produktfrage und hier kein eigener bestätigter Inhalts-Leak.

Behebungsrichtung: Anonyme Inhalte nicht über personenbezogene Profilantworten ausliefern; anonyme Projektion von identifizierenden Profilpfaden trennen. Bestehende IDs, Metadaten und Querverbindungen auf Reidentifikation prüfen. Keine Inhalte gelöscht oder verborgen.

### Gruppen-WebSocket: parallele Änderung und Gegenprobe

Während dieser Runde änderte eine andere Schreibquelle `/root/werkraum/welt/groups_api.py`. Der zuerst gelesene WebSocket-Handler prüfte nur JWT und verband danach direkt mit der Gruppe. Der anschließend gelesene Stand nutzt zentrale Tokenprüfung und `_can_post_group` vor dem Connect sowie vor dem Speichern einer Nachricht. Diese Review-Session hat die Änderung NICHT vorgenommen und beansprucht keine Urheberschaft.

Der erste isolierte Versuch war wegen des zwischenzeitlich geänderten Codes und eines nicht mehr passenden Test-Doubles unbrauchbar: Close-Code 4001, kein Nachweis einer Berechtigungslücke. Die korrigierte Gegenprobe mit künstlichem Tokenprüfer und verweigerter Gruppenberechtigung ergab:

```text
permission_checked
closed: code 4003
db_mock_closed
```

Kein produktiver Socket, keine echte Datenbank, kein JWT-Schlüssel verwendet. Der alte Connect-Verdacht wird deshalb NICHT als aktuell offene neue Lücke gezählt. Der aktuelle Codecheck ist auch kein Nachweis, dass ein laufender Prozess den Fix geladen hat.

Offene Restprüfung: Bestehende Empfänger bleiben im gelesenen `/root/werkraum/welt/ws_manager.py:23` beim Broadcast ungeprüft in ihrem Raum. Mitgliedschaftsentzug, Kontosperre und Tokenablauf während einer bereits bestehenden Verbindung müssen noch gegen den gesamten Lebenszyklus geprüft werden. Der neue Check vor dem Schreiben schützt nicht automatisch den Empfang bereits verbundener stiller Clients. Noch kein abgeschlossener zusätzlicher Befund.

### Ergänzung zur ungeschützten Serververwaltung

Die gleiche lokale Auth-Lücke wie SEC-005 betrifft im gelesenen Server auch Dolphin-Sessions: `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:2600` liefert Sitzungsinhalt, spätere Handler verändern Index/Archivstatus und verschieben Sessions in den Papierkorb. In `/vps_system/etc/nginx/sites-available/flextrawurst` wurde kein eigener Dolphin-Schutz gefunden. Das bleibt eine Erweiterung des betroffenen Umfangs, keine künstlich vervielfachte neue Root-Cause. Es wurden keine Sessioninhalte über HTTP abgerufen und keine Session verändert.

Dienstkonfiguration: `/vps_system/etc/systemd/system/process-camera-preview.service:7` und `/vps_system/etc/systemd/system/flextrawurst-surface.service:7` setzen jeweils `User=root`. Das erhöht bei aktiver Verwendung dieser Units die Folgen unsicherer Dateioperationen wie SEC-008. Der Code bindet standardmäßig an `127.0.0.1` (`/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:200`); ein offener Direktport im Internet ist daher nicht einfach anzunehmen. Aktive Unit, Prozessrechte und Netzbindung wurden nicht live bestätigt.

### Weitere Prüfkandidaten und ausgeschlossene Fehlalarme

- `/root/werkraum/welt/fragen_api.py:445`: AST-Parser meldet eine nicht geschlossene mehrzeilige Zeichenkette bis Dateiende (Zeile 521). Damit ist die zuvor unbenannte Parse-Unterbrechung lokalisiert. Laufzeiteinbindung/Version noch offen; kein Sicherheitsbefund allein aus Syntaxfehler.
- Dynamische SQL-Sortierungen stichprobenartig geprüft: `/root/werkraum/welt/api.py:5694` begrenzt Sortierfeld und Richtung auf feste erlaubte Werte. Kein SQL-Injection-Befund aus der bloßen Verwendung von f-Strings.
- `/root/werkraum/welt/groups_api.py:710` prüft bei Verknüpfung von Menschmaterial Einwilligung, Ersteller und Gruppen-Schreibrechte. Keine pauschale Behauptung, sämtliche Gruppenpfade seien offen.
- `/vps_root/flextrawurst/out/process_camera/dolphin_mischpult.html:769` enthält unescaped Modellmetadaten in HTML. Die dortige Nachrichtenabbildung übernimmt diese Felder im gelesenen Pfad jedoch nicht. Deshalb keine tragfähige Stored-XSS-Kette aus dieser Stelle behaupten.
- `/root/werkraum/flextrawurst/flextrawurst_surface.html:11237` setzt erkannte Bild-URLs nach Text-Escaping wieder in HTML-Attribute ein. URL-/Attributvalidierung ist weiter zu prüfen; kein zusätzlicher getesteter Exploit.

### Dateistände dieser Runde

```text
4d5e062e8d04006607f908e9cf5690ed4b389ea19aedcea672d998ed1f6142ec  /root/werkraum/welt/api.py
36f77fec8a614317c3b8a0172ea8d5a9d170006dbdd069047dd6e708ba116f3b  /root/werkraum/welt/auth.py
fe1c7450a62b010664187780e2a7c6cd358fc1f3d3ed3af87a17cb55b616ec2c  /root/werkraum/welt/groups_api.py
7c5a077c404237ae0c36ce5bab5a04fbef68c672999babd25aadac42f060166a  /vps_root/flextrawurst/scripts/serve_process_camera_preview.ts
5b1d8539a7ef31b1da28eb621bd3086334a1bffd74e3dc4e8c987e83e65e4c5b  /vps_root/flextrawurst/out/process_camera/flextrawurst_surface_public.html
```

Stand: SEC-001 bis SEC-011 dokumentiert, nicht elf live reproduzierte Exploits. Prüfung weiterhin unvollständig; Parallelarbeit macht Dateistand und Deploymentnachweis besonders wichtig. Weiterhin nur Bericht geändert, keine Anwendung repariert.

## Ergänzende Sichtbarkeits- und Abhängigkeitsprüfung

### SEC-012 — Splitter-Spurroute umgeht Sichtbarkeits- und Herkunftsschutz

Priorität: HOCH. Status: statischer Datenfluss und isolierter Vergleich mit synthetischem Datensatz bestätigt.

Fundstellen: `/root/werkraum/welt/api.py:3517` (Detailroute), `/root/werkraum/welt/api.py:3562` (Spurroute), `/root/werkraum/welt/api.py:3626` (verknüpfte Postquelle).

Die Detailroute prüft Status und Herkunftssichtbarkeit. Die Spurroute nimmt dagegen nur die Splitter-ID, lädt den Datensatz ohne dieselben Einschränkungen und gibt den Urheber einschließlich Benutzername aus. Bei eventbasierten Splittern werden außerdem Event-Payload und gegebenenfalls der vollständige referenzierte Post geladen; dafür sind im gelesenen Pfad keine eigenen Event-/Post-Sichtbarkeitsprüfungen vorhanden.

Isolierter Vergleich: Beide extrahierten Funktionen erhielten dieselbe künstliche Datenbankzeile mit verborgenem Status und unsichtbarer Herkunft. Keine echte Datenbank und kein HTTP-Aufruf:

```text
DETAIL -> 404
TRACE_ACTOR -> typ=mensch, id=synthetic-human, username=synthetic-name
```

Angriffsbedingung: Ein Aufrufer kennt eine gültige Splitter-ID, etwa aus früherer Sichtbarkeit oder einer Verknüpfung. Es wird keine beliebige Erratbarkeit von UUIDs behauptet. Die Spurroute kann dann Schutzentscheidungen der Detailroute umgehen. Die Event-/Post-Erweiterung ist statisch belegt, nicht mit echten privaten Events getestet.

Behebungsrichtung: Sichtbarkeit des Splitters vor jeder Unterressource zentral prüfen; Herkunftsredaktion auch in Spuren anwenden und jede verknüpfte Quelle nach ihren eigenen Rechten behandeln. Ein öffentlicher Provenienzpfad darf nicht automatisch interne Provenienz offenlegen.

### SEC-013 — Installierter Starlette-Stand ignoriert Limits bei URL-kodierten Formularen

Priorität: HOCH laut Hersteller-Advisory; konkrete Betriebswirkung nicht belastungsgetestet. Status: betroffene installierte Paketversion und lokaler Parsercode nachgewiesen; aktiver Prozessstand offen.

Dienst-/Paketzuordnung:

- `/vps_system/etc/systemd/system/welt-api.service:11` startet den Python-Interpreter unter `/root/werkraum/venv`.
- `/root/werkraum/venv` verweist auf den Hostpfad `/root/werkraum_venv2`, dessen lesbarer Mount hier `/vps_root/werkraum_venv2` ist.
- `/vps_root/werkraum_venv2/lib/python3.12/site-packages/starlette-1.0.0.dist-info/METADATA:3`: Starlette 1.0.0.
- `/vps_root/werkraum_venv2/lib/python3.12/site-packages/starlette/requests.py:295`: URL-kodierte Formulare werden an `FormParser` übergeben, ohne `max_fields` oder `max_part_size` weiterzugeben.
- `/vps_root/werkraum_venv2/lib/python3.12/site-packages/starlette/formparsers.py:120`: Felder werden ohne entsprechende Anzahlprüfung gesammelt.

Herstellerquelle: [GHSA-82w8-qh3p-5jfq / CVE-2026-54283](https://github.com/Kludex/starlette/security/advisories/GHSA-82w8-qh3p-5jfq). Laut Advisory betroffen ab 0.4.1 bis vor 1.3.1, behoben in 1.3.1. Der gelesene Stand 1.0.0 liegt darin. Das Advisory beschreibt CPU-/Speicherbelastung durch ignorierte Formularlimits; ein Gesamt-Body-Limit reduziert, beseitigt aber nicht alle Folgen.

Anwendungskontext: `/root/werkraum/welt/api.py:791` und weitere Upload-Routen nutzen Form-/File-Parameter. Ob der aktive Request-Pfad ein URL-kodiertes Formular vor der erwarteten File-Validierung verarbeitet, ist noch gegen die tatsächliche FastAPI-Laufzeitkette zu prüfen. Keine produktive Formularanfrage und kein Lasttest durchgeführt.

Behebungsrichtung: Kompatibles, gepatchtes Abhängigkeitsset testen und reproduzierbar festschreiben; Feldanzahl und Feldgröße auch für URL-kodierte Requests wirksam begrenzen. Keine Paketinstallation oder Aktualisierung im Review.

### Wichtige Abweichung: deklarierte Abhängigkeiten sind nicht die installierten

`/root/werkraum/requirements.txt` deklariert FastAPI 0.115.0, uvicorn 0.30.6 und Pydantic 2.9.2. Im zugeordneten virtuellen Environment liegen dagegen unter anderem FastAPI 0.136.0, uvicorn 0.45.0, Starlette 1.0.0 und python-multipart 0.0.29. Ein Audit nur dieser Requirements-Datei würde daher falsche Aussagen über das vorhandene Environment erzeugen. Die im laufenden Prozess bereits importierten Versionen sind damit noch nicht bewiesen.

Die älteren Starlette-Advisories [GHSA-f96h-pmfr-66vw](https://github.com/Kludex/starlette/security/advisories/GHSA-f96h-pmfr-66vw) und [GHSA-7f5h-v6xp-fcq8](https://github.com/Kludex/starlette/security/advisories/GHSA-7f5h-v6xp-fcq8) werden NICHT als Befund gegen diesen installierten 1.0.0-Stand gezählt: Ihre angegebenen betroffenen Versionsbereiche liegen darunter. Kein pauschales „alte Requirements = produktiv verwundbar“.

Zusätzlich inventarisiert: `/vps_root/flextrawurst/package.json` und `/vps_root/flextrawurst/package-lock.json`; Playwright im Lockfile 1.61.1. Kein vollständiger npm-/Python-Advisoryscan durchgeführt und kein negatives Gesamturteil aus fehlenden Einzelbefunden abgeleitet.

### SEC-013: ungefährlicher lokaler Parserbeleg

Starlettes `Request` wurde aus dem oben bezeichneten Paketverzeichnis in einem separaten Python-Prozess mit deaktiviertem Bytecode-Schreiben geladen. Ein synthetischer ASGI-Empfänger lieferte insgesamt nur 14 Bytes Formulardaten. Aufgerufen wurde `request.form(max_fields=1, max_part_size=1)`.

```text
FORM_FIELDS_WITH_MAX_FIELDS_1 -> 3
FIELD_LENGTHS_WITH_MAX_PART_SIZE_1 -> [2, 2, 2]
```

Damit sind beide ignorierten Limits am gelesenen Paketstand mit winziger Eingabe bestätigt. Keine Netzwerkverbindung, kein Produktivrequest, kein Application-Import, kein Lasttest. Die API wurde nicht gestartet. Die FastAPI-Routingimplementierung unter `/vps_root/werkraum_venv2/lib/python3.12/site-packages/fastapi/routing.py` enthält zudem den Form-Parsing-Pfad vor der späteren Dependency-Auflösung. Effektives Deployment und Schutzwirkung der vorgeschalteten Limits bleiben weiterhin gesondert zu prüfen.

## Arbeitsindex nach dieser längeren Review-Runde

| ID | Schwerpunkt | Evidenzstand |
| --- | --- | --- |
| SEC-001 | Tokenrechte nach Sperre/Rollenwechsel | Code + isolierter Guard-Test |
| SEC-002 | Moderationsumgehung über Bild-URL | Code + Proxy-Konfiguration |
| SEC-003 | Body-Limit nur anhand Header | Isolierter Middleware-Test; Proxy begrenzt zusätzlich |
| SEC-004 | DB-Verbindung je öffentlichem Stream | Code; Lastwirkung offen |
| SEC-005 | Ungeschützte Charakter-/Sessionverwaltung | Code + Proxy-Konfiguration |
| SEC-006 | Unvollständiger SSRF-Schutz im URL-Leser | Code; kein Netzwerktest |
| SEC-007 | Ungeschützte echte Container-/Dienstaktionen | Codekette bis CLI + Proxy |
| SEC-008 | Fehlende Pfadgrenze vor Löschen | Code; niemals Löschung getestet |
| SEC-009 | Profil-HTML-Injection / XSS-Codepfad | Isolierter harmloser HTML-Marker |
| SEC-010 | Private Profile in öffentlicher Liste | SQL-/Rückgabepfad |
| SEC-011 | Reidentifikation anonymer Profilinhalte | SQL-/Rückgabepfad |
| SEC-012 | Spurroute umgeht Sichtbarkeit | Isolierter Vergleich: Detail 404, Spur verrät Akteur |
| SEC-013 | Ignorierte Formularlimits in Starlette | Paketstand + Hersteller-Advisory + winziger Parsertest |

Die IDs sind Review-Befunde unterschiedlicher Belegstärke, keine Anzahl erfolgreicher Produktionsangriffe. Einzelne Ursachen überlappen. Der Gruppen-WebSocket-Connect-Verdacht wurde nach einer parallelen Codeänderung nicht als neue offene ID gezählt.

Noch offen bleiben insbesondere vollständige Frontend-/API-Abdeckung, laufender Deploymentabgleich, alle weiteren Services/Brücken, vollständige Dependencyprüfung, effektive Firewall-/Proxy-Gesamtkonfiguration und Regressionstests nach tatsächlichen Reparaturen. Kein Abschluss eines Gesamt-Audits behauptet. Alle fachlichen Änderungen dieser Session betreffen ausschließlich diesen Bericht; fremde Codeänderungen wurden weder übernommen noch zurückgesetzt.

## Fortsetzung nach Daniels Nachfrage vom 2026-09-16

### Wiederprüfung bestehender Befunde

Die gelesene `/root/werkraum/welt/auth.py:48` vertraut weiterhin der Rolle im JWT ohne aktuellen Kontostatus; SEC-001 ist auf Codeebene nicht erledigt. Auch `/root/werkraum/codewesen_container.py:308` enthält weiterhin keine aufgelöste Zielpfadgrenze vor dem Löschen; SEC-008 bleibt auf Codeebene offen. Keine Aussage über zwischenzeitliche aktive Deployments oder sämtliche anderen Befunde.

### SEC-014 — Archiv-Schlüsselschutz lässt direkte Rohdaten-APIs ungeschützt

Priorität: HOCH. Status: Quellcode und Proxy-Konfiguration geprüft; isolierter Kontrollflusstest mit künstlicher Quelldatei bestätigt fehlende Authentifizierung. Kein produktiver Abruf von Rohquellen oder Geheimnissen.

Fundstellen:

- `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts:2387`: die Surface-Auslieferung prüft Archiv-/Crawler-Schlüssel und unterscheidet öffentliche und vollständige HTML-Version.
- `/root/werkraum/welt/api.py:15218`: `guardianstyle_eintraege` nimmt keinen Authentifizierungsparameter entgegen und prüft keine Rechte. Im Rohmodus gibt es den vollständigen Inhalt einer registrierten Datei aus.
- `/root/werkraum/welt/api.py:15249`: die normale Antwort liefert zusätzlich die Liste registrierter Dateipfade. Ein Aufrufer muss erlaubte Dateinamen daher nicht zwingend erraten.
- `/root/werkraum/welt/api.py:4438`: CodeGeil bietet ebenfalls einen ungeschützten Rohmodus für indexierte Quellen, einschließlich Auflösung und Rückgabe der Originaldatei.
- `/root/werkraum/welt/api.py:15661`: systemweite Archäologie gibt registrierte Dokumente ohne lokale Rechteprüfung aus.
- `/vps_system/etc/nginx/sites-available/flextrawurst:788`: allgemeiner API-Proxy enthält Rate-Limiting, aber keine Authentifizierung; keine speziellen Guardianstyle-/CodeGeil-/Archäologie-Schutzblöcke in dieser vHost-Datei gefunden.

Problem: Die Schlüsselprüfung schützt die gebackene HTML-Ansicht, nicht die daneben bestehenden API-Datenwege. Die Kommentare des Node-Servers beschreiben diese Tabs als admin-only; die API-Funktionen sind dagegen ausdrücklich als öffentliche Lese-APIs implementiert. Die Herkunft dieser widersprüchlichen Entscheidungen bleibt sichtbar, ersetzt aber keine durchgängige Schutzgrenze.

Isolierter Beleg: `guardianstyle_eintraege` wurde per AST extrahiert. Dateiregister und Dateisystem waren vollständig künstlich; eine einzige registrierte Testquelle enthielt nur einen Marker. Ohne Token oder Schlüssel wurde dieser Rohtext zurückgegeben:

```text
RAW_SOURCE_RETURNED_WITHOUT_AUTH -> true
```

Auswirkung: Wenn diese Konfiguration aktiv ist, kann ein unangemeldeter Aufrufer registrierte interne Quelldateien und Dokumente über die Daten-API statt über die gesperrte Ansicht lesen. Sollten solche Quellen Geheimnisliterale enthalten, könnte dies deren Offenlegung ermöglichen; tatsächliche betroffene Geheimnisse wurden weder gesucht noch über HTTP ausgelesen. Kein beliebiger Dateisystemzugriff behauptet: Der geprüfte Rohpfad ist auf registrierte/indizierte Quellen begrenzt.

Behebungsrichtung: Dieselbe Autorisierung vor sämtliche geschützten Archiv-Datenwege setzen; gezielt öffentliche Ausschnitte getrennt ausliefern. Schlüssel nicht nur in der Darstellungsschicht prüfen. Regressionstests für Metadatenliste, Rohtext und verknüpfte Originalquelle vorsehen. Keine Schutzregeln oder Dienste in dieser Session geändert.

Weiterer offener Aspekt: Antworten mit geschlüsseltem Vollzugriff erhalten im gelesenen Node-Pfad keinen expliziten `no-store`-Header. Daraus allein folgt kein nachgewiesener Cache-Leak; Cache-Schlüssel, Header und tatsächliche Zwischenproxies müssen gesondert geprüft werden.

Aktueller Index: SEC-001 bis SEC-014. Auch dieser Nachtrag ist kein Abschluss des Gesamtreviews. Neue Tests waren ausschließlich isoliert, ohne echte HTTP-Anfragen oder Änderungen an Anwendungsdaten.

## Deploymentabgleich am 2026-09-16 ab 17:20 UTC

Dieser Abschnitt erweitert die bisherige ausschließlich statische/isolierte Prüfung erstmals um wenige nicht-mutierende HTTP-GETs. Alle HTTPS-Anfragen gingen mit gültiger Zertifikatsprüfung, SNI/Host `flextrawurst.de` und expliziter Auflösung auf `127.0.0.1` an den lokalen vHost. Keine externe Netzperspektive und kein Nachweis über CDN/öffentliche Firewall. Keine Cookies, Tokens oder Passwörter verwendet; Antwortgröße und Laufzeit begrenzt. Keine Schreibroute, kein Stream und keine interne Rohdatei angefordert. Die vollständigen Antworten wurden nicht ausgegeben oder gespeichert; nur Status, JSON-Schlüsselnamen und Arraylängen ausgewertet.

| Lesende Prüfung | Ergebnis | Tragfähige Aussage |
| --- | --- | --- |
| HTTPS `/api/health` | 200 | vHost antwortet; diese spezielle Location geht an Port 8042, NICHT an die Welt-API |
| HTTPS Wizard-Wesenliste | 200, sieben Einträge | Wizard-Lese-API ist im lokalen HTTPS-vHost ohne Anmeldung erreichbar |
| HTTPS unbekannter Unterpfad im Flarumstyler-Bereich | 401 | Basic-Auth greift dort vor der Ressourcenauflösung |
| HTTPS Guardianstyle-Einträge, beide Filter mit nicht existierenden Review-Markern | 200, null Treffereinträge, 111 registrierte Dateipfade in `alle_dateien` | Archiv-Metadaten werden ohne Anmeldung ausgeliefert; SEC-014 wird für diesen Teil live gestützt |
| Direktes GET `http://127.0.0.1:8030/health` | 200 mit Status und Zeitstempel | Welt-API antwortet am erwarteten lokalen Port |

Die Wizard-Schreibfunktionen bleiben absichtlich ungetestet. Aus der offenen Liste folgt nicht allein ein erfolgreicher Schreibzugriff; dafür bleibt die zuvor dokumentierte Code-/Konfigurationskette maßgeblich. Auch für SEC-014 wurde kein Rohtext abgerufen.

### Laufende Prozesse und Bindungen

`ss` zeigt Port 8030 und 8787 an `127.0.0.1`, HTTPS 443 dagegen an den Wildcard-Adressen. Die Host-Prozessmetadaten unter `/vps_system/proc` zeigen bei dieser Momentaufnahme:

- PID 3034936: Skript `scripts/serve_process_camera_preview.ts`, reale/effektive/gespeicherte/Filesystem-UID jeweils 0.
- PID 3053111: Skript `/root/werkraum/welt/api.py`, dieselben UID-Werte jeweils 0.

Nur zur Identifizierung passende Skriptargumente und UID-Zeilen ausgewertet, keine Prozessumgebungen oder Schlüssel gelesen. CWD-Verknüpfungen waren nicht lesbar. Die Zuordnung aktiver Prozesse und root-Rechte ist damit stärker als die bloße Unit-Konfiguration; ein Hash des tatsächlich in den Prozess geladenen Programmcodes ist damit weiterhin nicht bewiesen.

Konsequenz: Der mögliche Schaden von SEC-008 ist nicht allein eine hypothetische root-Konfiguration. Die identifizierten Serverprozesse laufen tatsächlich mit UID 0. Ein Löschversuch wurde dennoch niemals durchgeführt. Unnötige Root-Rechte als Verstärker dokumentieren, nicht als eigenständigen Remote-Exploit zählen.

### Korrektur der Proxy-Einschätzung zu SEC-004

`/vps_system/etc/nginx/sites-available/flextrawurst:255` hat eine eigene Regex-Location für Event-/Denk-/DOM-/Fokus-Streams. Sie geht an Port 8030, deaktiviert Buffering und setzt 3600 Sekunden Lese-Timeout. Das bei Zeile 789 dokumentierte API-Rate-Limit gehört nur zum allgemeinen Präfix-Block und wird von der spezifischen Stream-Location nicht automatisch übernommen. In den geprüften Haupt-/Conf-Dateien wurde keine globale `limit_conn`-Direktive gefunden.

Damit ist die frühere mögliche Entschärfung von SEC-004 durch das allgemeine API-Rate-Limit für diesen Stream-Pfad nicht belegt. Kein Stream geöffnet, keine Verbindungen angehäuft; tatsächliche Ressourcenerschöpfung bleibt ungetestet.

## SEC-015 — Private Post-Inhalte über öffentliche Relations-/Spuransichten

Priorität: HOCH für Vertraulichkeit. Status: statischer SQL-/Rückgabepfad und isolierter Test; keine echten privaten Posts gelesen.

Fundstellen:

- `/root/werkraum/welt/api.py:2727`: `post_relationen_lesen` prüft nur die Sichtbarkeit des Ausgangsposts. Der nachfolgende Join auf den Zielpost liefert dessen Inhalt und Titel ohne eigene Sichtbarkeitsbedingung.
- `/root/werkraum/welt/api.py:2944`: `post_spur` prüft ebenfalls den Ausgangspost. Die anschließende Graphtraversierung liest Nachbarposts mit Inhalt, Titel und Autor ohne deren Sichtbarkeit zu prüfen und folgt diesen Knoten gegebenenfalls weiter.
- `/root/werkraum/welt/api.py:2802`: Anlegen einer Relation ist auf Admin/Entity beschränkt, prüft jedoch nur die Existenz der beteiligten Posts, nicht deren öffentliche Sichtbarkeit. Verknüpfungen zu privaten Posts sind daher auf Anwendungsebene nicht grundsätzlich ausgeschlossen.
- Vergleich: `/root/werkraum/welt/api.py:2595` schützt die normale Postdetailroute vor nichtöffentlichen Posts.

Angriffsbedingung: Ein öffentlicher Post ist mit einem nichtöffentlichen Post verbunden, etwa durch autorisierte Verknüpfung oder eine spätere Sichtbarkeitsänderung. Ein unangemeldeter Leser braucht nur die öffentliche Ausgangs-ID; er muss die private Ziel-ID nicht bereits kennen. Die tatsächliche Existenz solcher Verknüpfungen in der Produktionsdatenbank wurde nicht erhoben.

Isolierter Test: Die extrahierte Funktion `post_spur` erhielt eine künstliche öffentliche Ankerzeile und einen synthetischen privaten Nachbarn. Die Datenbankattrappe liefert nur vorbereitete Zeilen; der Test führt keine echte SQL-Engine aus. Ergebnis:

```text
PRIVATE_NEIGHBOR_MARKER_RETURNED -> true
NEIGHBOR_QUERY_HAS_VISIBILITY_PREDICATE -> false
```

Auswirkung: Vorschauinhalt, Titel, Autor und Verknüpfungsmetadaten nichtöffentlicher Posts können über öffentliche Graphansichten offengelegt werden. Die Begrenzung auf eine Vorschau oder geringe Traversierungstiefe ist keine Berechtigungsprüfung.

Behebungsrichtung: Sichtbarkeit auf jedem besuchten Knoten und jeder ausgegebenen Zielressource prüfen; versteckte Knoten nicht allein aufgrund eines öffentlichen Vorgängers ausgeben oder weiter durchlaufen. Private Verknüpfungen dürfen intern erhalten bleiben. Regressionstest für öffentliche Quelle → privates Ziel sowie spätere Sichtbarkeitsänderung vorsehen.

Aktueller Stand: SEC-001 bis SEC-015; selektiver Deploymentabgleich begonnen, keine vollständige Live-Verifikation. Fachliche Änderungen weiterhin nur an diesem Bericht, keine Reparaturen oder produktiven Datenänderungen.

## SEC-016 — Offene Gruppen-WebSockets empfangen nach Gruppenaustritt weiter

Priorität: HOCH für private Gruppenkommunikation. Status: isolierter Lebenszyklustest mit extrahierter Austrittsfunktion und echtem Manager-Code, aber künstlichen Sockets und Datenbankobjekten.

Fundstellen:

- `/root/werkraum/welt/groups_api.py:697`: `leave_group` setzt die Mitgliedschaft auf `left` und protokolliert den Austritt; bestehende Socket-Mitgliedschaften werden nicht entfernt.
- `/root/werkraum/welt/groups_api.py:1472`: WebSocket prüft Rechte beim Verbindungsaufbau.
- `/root/werkraum/welt/groups_api.py:1537`: erneute Prüfung beim eigenen Schreiben. Stille Empfänger führen diese Prüfung nicht aus.
- `/root/werkraum/welt/ws_manager.py:10`: Manager legt die Verbindung im Raum ab.
- `/root/werkraum/welt/ws_manager.py:22`: Broadcast sendet an alle gespeicherten Verbindungen ohne aktuelle Mitgliedschafts-/Leserechteprüfung.

Angriffsbedingung: Ein ursprünglich berechtigtes Mitglied öffnet einen WebSocket in einer privaten Gruppe und hält ihn während des Austritts offen. Andere berechtigte Mitglieder schreiben anschließend weiter. Der normale neue REST-/WebSocket-Zugriff kann bereits verboten sein, während die alte Verbindung weiter empfängt.

Isolierter Testablauf: Künstlichen Socket beim unveränderten, extrahierten `GroupChatManager` anmelden; die aktuelle extrahierte `leave_group`-Funktion mit einer Datenbankattrappe ausführen; danach einen synthetischen Nachrichtenmarker über denselben Manager verteilen. Ergebnis:

```text
MEMBERSHIP_ACTIVE_AFTER_LEAVE -> false
FORMER_MEMBER_RECEIVED_LATER_BROADCAST -> true
```

Keine echte Gruppe betreten oder verlassen, keine echte Mitgliedschaft verändert, kein Netzwerk-Socket geöffnet. Der Test belegt den fehlenden Zusammenhang zwischen Datenbank-Austritt und laufendem Empfängerverteiler. Er testet nicht alle möglichen externen Verbindungsabbrüche oder den produktiven Zeitverlauf.

Abgrenzung: Der bereits korrigierte unberechtigte Erstbeitritt wird nicht erneut beanstandet. SEC-016 betrifft den Widerruf einer ursprünglich berechtigten Verbindung. Ein Leerlauf-Timeout ist kein zuverlässiger Ersatz für den Widerruf, insbesondere bei laufendem Nachrichtenverkehr. Tokenablauf und Kontosperre während bestehender Sessions sollten im selben Lebenszyklus geprüft werden; sie wurden hier nicht separat simuliert.

Behebungsrichtung: Verbindungen mit überprüfter Identität registrieren, Austritt/Rechteentzug in den laufenden Verteiler übernehmen und vor weiterer Auslieferung sicherstellen, dass die Leseberechtigung noch besteht. Bei mehreren Workern muss der Widerruf alle Worker erreichen. Keine Implementierung oder Dienständerung in diesem Review.

Gelesene Dateistände:

```text
b051855e459d691ac42f0056e6273def66cdb45f090a1d45d95b0e85fff720e9  /root/werkraum/welt/ws_manager.py
3ef86b208b455fe28db30e83a9d2b7730adfb5305b2bd8a21393a21c8c89c928  /root/werkraum/welt/groups_api.py
```

## Zwischenstand nach Deployment-, Relations- und WebSocket-Prüfblock

- SEC-014: unangemeldete Metadatenausgabe zusätzlich über den lokalen HTTPS-vHost bestätigt; Rohtext nicht angefordert.
- SEC-004: Stream-Location umgeht das allgemeine API-Rate-Limit; frühere Entschärfungsannahme korrigiert.
- Root-Prozessrechte und lokale Portbindungen überprüft; eingespielte Dateiversionen bleiben gesondert zu belegen.
- SEC-015: private Nachbarposts in öffentlichen Relations-/Spuransichten, isoliert geprüft.
- SEC-016: Empfang nach Gruppenaustritt über bestehende WebSockets, isoliert geprüft.
- Bericht auf Whitespace-/Patchfehler geprüft. Keine Produktivdaten verändert; nur wenige kleine Leseanfragen, keine Belastungs-, Schreib- oder Löschtests.

Nicht erledigt: Vollabdeckung aller Dienste, externe Netzwerkperspektive, kompletter Abhängigkeits-/Geheimnisscan, Behebung und anschließende Regressionstests. Die Anzahl von 16 IDs ist weiterhin keine Anzahl live erfolgreich ausgenutzter Sicherheitslücken.

## Systematische Inventur und weiterer Verwaltungsreview — 2026-09-16

Die Inventur und die tatsächliche Review-Abdeckung stehen separat in `/root/werkraum/_codex/berichte/2026-09-16-flextrawurst-review-abdeckung.md`. Die erste Erhebung zählt rund 2,4 Millionen Zeilen in grob klassifizierten Eigen-Code-Kandidaten; Worktrees und Datenexporte sind darin teils noch enthalten. Daraus folgt weder eine Produktionscodegröße noch eine geprüfte Zeilenzahl. Die engere Auswahl umfasst beispielsweise 42.266 Zeilen Welt-Python/SQL, 20.863 Zeilen Node-Skripte und 14.036 Zeilen Kernel-Code. Der Kernel ist damit nur inventarisiert, nicht geprüft.

### SEC-017 — Gateway-Pfadgrenze akzeptiert gleichnamige Nachbarverzeichnisse

Priorität: MITTEL; gültiger Gateway-Zugang erforderlich. Status: isolierter Test der unveränderten Resolverfunktion bestätigt.

Fundstelle: `/root/werkraum/app/services.py:10`. Der Resolver löst den Pfad auf, prüft dann aber nur `str(target).startswith(str(WORKSPACE_ROOT))`. Ein Pfad außerhalb der Wurzel mit demselben Zeichenpräfix wird dadurch akzeptiert. Es fehlt die Prüfung auf eine tatsächliche Pfadkomponente beziehungsweise `is_relative_to`.

Isolierter Test mit rein synthetischer Wurzel und synthetischem Nachbarpfad ergab `GATEWAY_SIBLING_ACCEPTED true`. Keine Datei dort angelegt, gelesen oder verändert. Die Lesefunktion würde ein vorhandenes Ziel danach lesen; die Schreibfunktion schreibt vor ihrer abschließenden `relative_to`-Darstellung, sodass ein späterer Fehler die vorherige Schreibwirkung nicht rückgängig machen würde. Dieser Effekt wurde nur im Code nachvollzogen, niemals schreibend getestet.

Schutzgrenze und Einschränkung: `/root/werkraum/app/main.py` verwendet bei allen sensiblen Routen `Depends(require_api_token)`; `/root/werkraum/app/security.py` ist bei fehlendem Token fail-closed und vergleicht konstantzeitig. Ein direktes unauthentifiziertes GET auf `http://127.0.0.1:8010/workspace` gab 401 zurück. Kein anonymer Zugriff bewiesen. Da derselbe Zugang auch Befehlsausführung autorisiert, ist dies keine bewiesene Rechteausweitung gegenüber dem gesamten Gateway, wohl aber eine Verletzung der zugesagten Dateipfadgrenze.

Behebungsrichtung: Aufgelöste Pfade komponentenbasiert begrenzen und die Grenze vor jeder Nebenwirkung prüfen. Die Kommando-Allowlist ist getrennt zu behandeln; erlaubte Python-/Git-Aufrufe sind keine belastbare Sandbox. Keine Änderung am Gateway vorgenommen.

### SEC-018 — Systemweiser-Sitzungen bleiben nach Passwortwechsel gültig

Priorität: HOCH im Fall einer entwendeten Admin-Sitzung. Status: Authentifizierungs-/Passwortwechselpfad gelesen und Passwortwechsel isoliert mit komplett gemockten Unterprozessen ausgeführt.

Fundstellen: `/root/werkraum/systemweiser_web.py:44` erzeugt einen pro Prozess gemeinsamen `SESSION_TOKEN`; `/root/werkraum/systemweiser_web.py:59` prüft nur Gleichheit des Cookies; `/root/werkraum/systemweiser_web.py:368` ändert das gemeinsame Basic-Auth-Passwort, ohne den Sitzungstoken zu erneuern oder bestehende Sitzungen zu widerrufen; `/root/werkraum/systemweiser_web.py:433` stellt diesen Token beim Login aus.

Isolierter Test: Passwortwechselhandler extrahiert; alle Aufrufe von `htpasswd` und `systemctl` durch Attrappen ersetzt. Ergebnis: `MOCK_PASSWORD_CHANGE_OK true`, `OLD_GLOBAL_SESSION_TOKEN_UNCHANGED true`. Kein echtes Passwort eingegeben oder verändert, kein Befehl gestartet, nginx nicht neu geladen.

Auswirkung: Ein gestohlenes noch akzeptiertes Cookie bleibt auch nach Passwortwechsel administrativ nutzbar. Die Cookie-Laufzeit im Browser ist keine serverseitige Widerrufsprüfung. Mehrere Logins teilen denselben Prozess-Token; selektiver Sessionwiderruf ist in diesem Modell nicht vorgesehen. Kein Sitzungsdiebstahl durchgeführt und kein Ablauf nach 30 Tagen simuliert.

Vorhandene Schutzmaßnahmen: Cookie hat HttpOnly, Secure und SameSite=Lax. Middleware schützt die Verwaltungsrouten. Unauthentifiziertes GET `http://127.0.0.1:8080/api/status` gab 401. Der HTTPS-Proxy unter `/vps_system/etc/nginx/sites-available/obsidian:34` begrenzt die Loginrate. Deshalb keine offene anonyme Passwort-/Serviceverwaltung behaupten.

Behebungsrichtung: Serverseitige Sitzungen mit Ablauf und Widerruf; beim Passwortwechsel sämtliche alten Sessions ungültig machen und gegebenenfalls eine neue Sitzung explizit ausstellen. Keine Passwortrotation oder Implementierung im Review vorgenommen.

### Weitere Verwaltungsprüfungen ohne bestätigte neue öffentliche Lücke

- `/root/werkraum/api_bridge.py` enthält einen voreingestellten API-Key-Fallback sowie eine ähnliche Zeichenpräfix-Pfadprüfung. Eine aktive Dienst-/Proxyzuordnung wurde bislang nicht gefunden. Deshalb als Konfigurations-/Legacy-Kandidat vermerkt, kein öffentlich erreichbarer Root-Zugang behauptet und den Fallback nicht ausprobiert.
- `/root/werkraum/web_chat.py` kann bei Chatbetrieb Dienste koordinieren und stoppen. Die gelesenen externen Routen unter `/vps_system/etc/nginx/sites-available/flextrawurst:461` und `/vps_system/etc/nginx/sites-available/dakgord` sind per Basic-Auth geschützt; der Python-Dienst bindet lokal. Keine Chatgenerierung oder Betriebsaktion ausgelöst.
- Die Gateway-Unit auf Port 8010 und der Proxy unter `/werkraum-api/` auf Port 8001 sind unterschiedliche Ziele. Nicht ohne weiteren Nachweis gleichsetzen; diese Zuordnung bleibt offen.

Stand: SEC-001 bis SEC-018, jeweils mit Evidenz- und Autorisierungsgrenzen; keine Behauptung einer Gesamtabnahme.

## Weitere Gegenproben — Splitter und Schattenkommentare

### SEC-012 erweitert: Liste und Story umgehen dieselbe Herkunftsgrenze

Zusätzlich zur Spurroute sind `/root/werkraum/welt/api.py:3436` (`splitter_liste`) und `/root/werkraum/welt/api.py:14666` (`splitter_story_view`) betroffen. Keine neue Befundnummer für dieselbe grundlegende Sichtbarkeitsinkonsistenz.

- Die Liste filtert standardmäßig nur `status != 'verblasst'`. Sie liefert `human_id`, `human_username`, `origin_id` und ein aus dem Nutzernamen abgeleitetes `quelle_id` auch bei `herkunft_sichtbar=False`. `quelle_sichtbar=False` im JSON ist keine serverseitige Anonymisierung. Anders als beim bisherigen Spurbeleg muss dafür keine einzelne Splitter-ID vorab bekannt sein.
- Die Story liefert die komplette Splitterzeile und prüft lediglich `visibility_layer == 'private'`. Die Detailroute `/root/werkraum/welt/api.py:3524` verwendet dagegen `herkunft_sichtbar`, `entity_id` und Status. Das Basisschema `/root/werkraum/welt/schema_welt.sql:70` definiert Herkunftsschutz, aber kein `visibility_layer`; spätere Datenbankmigrationen wurden hier nicht vollständig abgeglichen. Auch mit einer zusätzlichen Spalte bleibt die Herkunftsprüfung im gelesenen Story-Code aus.
- Die Story selektiert außerdem zugehörige Events ohne Event-Sichtbarkeitsfilter und Gruppenverknüpfungen ohne Gruppenmitgliedschaftsprüfung. Deren tatsächlicher Inhalt wurde nicht aus der produktiven Datenbank ausgelesen.

Isolierter Beleg am 2026-09-16: Die drei Originalfunktionen wurden per AST extrahiert, Dekoratoren entfernt und ausschließlich mit einer synthetischen Cursor-/Verbindungsattrappe ausgeführt. Für denselben aktiven menschlichen Splitter mit `herkunft_sichtbar=False` lieferte der Detailaufruf **404**, die Liste dagegen den synthetischen verborgenen Nutzernamen als `human_username` und `quelle_id`, die Story die synthetischen `human_id`/`origin_id`. Kein Produktivmodul importiert, keine HTTP-Anfrage an diese Datenrouten, keine echten Inhalte gelesen. Die Cursorattrappe beweist das Ausgabeverhalten, nicht die Ausführung von SQL gegen PostgreSQL; die fehlenden SQL-Filter wurden separat im Quelltext geprüft.

Behebungsrichtung: Gemeinsame Autorisierungs- und Herkunftsredaktionsfunktion für Liste, Detail, Spur und Story; verknüpfte Events und Gruppen separat autorisieren. Regression muss dieselbe synthetische Zeile durch alle Ansichten schicken.

### BUG-001 — Eigener Schattenkommentar kann wegen undefiniertem `body` nicht gelöscht werden

**Funktionsfehler, keine nachgewiesene Rechteausweitung.** `/root/werkraum/welt/api.py:8972`, Funktion `schatten_loeschen`, hat nur `post_id` und `authorization` als Parameter, greift nach erfolgreicher Rollenprüfung aber auf `body.content.strip()` zu. In der isolierten Originalfunktion führte ein synthetischer Nutzer mit Rolle `user` zu `NameError: name 'body' is not defined`, bevor eine Datenbankverbindung hergestellt wurde. Die Löschfunktion ist damit für den vorgesehenen Nutzerpfad fehlerhaft; kein echter DELETE wurde gesendet. Behebungsrichtung: Die aus dem Schreibpfad übernommene Inhaltsprüfung entfernen und den bestehenden Eigentümerfilter erhalten; gesonderter Regressionstest mit eigener/fremder Kommentar-ID.

### BUG-002 — Rollenname für interne Zitate widerspricht dem normalen Nutzerpfad

**Autorisierungs-Konsistenzfehler mit verweigertem Zugriff, kein Datenleck belegt.** `/root/werkraum/welt/api.py:9531` (`_zitat_visible`) und `/root/werkraum/welt/api.py:9616` (Listenfilter) erlauben interne Zitate für `mensch` oder `entity`; sonstige Menschenrouten verwenden `user`. Der Login unter `/root/werkraum/welt/api.py:522` übernimmt die Datenbankrolle in den Token. Isolierte Gegenprobe: dieselbe interne Zitatattrappe, derselbe Ersteller, Rolle `user` → False; Rolle `mensch` → True. Auch der Ersteller wird bei `intern` nicht über eine gesonderte Eigentümerregel zugelassen. Betroffen sind Konten mit Rolle `user`; reale Rollenverteilung nicht ausgelesen. Rollenmodell vereinheitlichen und Listen-/Detailprüfung gemeinsam testen, nicht pauschal Zugriffe öffnen.

### Negativbefunde dieses Blocks

Die aktuell gelesenen öffentlichen Antwort-/Threadrouten in `/root/werkraum/welt/api.py:9110`, `/root/werkraum/welt/api.py:9185` und `/root/werkraum/welt/api.py:9207` prüfen die öffentliche Sichtbarkeit des Ausgangsposts; rekursive Antworten werden ebenfalls auf `public` beschränkt. Die Antworterstellung prüft eine übergebene Parent-ID auf Threadzugehörigkeit und Tiefe. Deshalb diese Codepfade nicht als ungeprüften Thread-IDOR melden. Zitatänderung/-löschung prüfen Ersteller oder Admin; dynamische Sortierung der Zitatliste ist allowlisted. Dies ist eine statische Teilprüfung, keine vollständige Abnahme dieser Funktionen.

## Kernel- und Nebenmodulprüfung

### BUG-003 — Append-only-EventStore schützt verschachtelte Inhalte nicht vor Mutation

**Bestätigter Integritätsfehler; öffentliche Angreifererreichbarkeit nicht nachgewiesen.** `/vps_root/flextrawurst/kernel/events/event_store.ts:8` kopiert und friert nur die oberste Eventebene sowie `causal_links` ein. `payload` bleibt dasselbe veränderbare Objekt wie beim Aufrufer. `/vps_root/flextrawurst/kernel/events/event_store.ts:18` und `/vps_root/flextrawurst/kernel/events/event_store.ts:22` geben Referenzen auf diese Inhalte zurück. Damit können sowohl ein ursprünglicher Produzent als auch ein Leser bereits gespeicherte Nutzdaten ändern, ohne ein neues Event anzuhängen oder erneut die Validierung zu durchlaufen.

Isolierte Tests am 2026-09-16 mit Node v22.23.2 und den direkt importierten Originalmodulen, ausschließlich synthetische In-Memory-Daten:

```text
ORIGINAL_REFERENCE_MUTATES_STORED_PAYLOAD true
READER_REFERENCE_MUTATES_STORED_PAYLOAD true
TOP_LEVEL_FROZEN true PAYLOAD_FROZEN false
Projektion vor/nach Referenzmutation: {"before":true,"after":false,"event_count":1}
```

Die Gegenprobe über `/vps_root/flextrawurst/kernel/projections/entity_projection.ts:12` zeigt die Konsequenz: derselbe Store mit unverändert einem Event ergibt nach einer Payloadmutation einen anderen Zustand. Kein produktiver Eventstore, keine Datenbank und kein Dienst wurden verändert.

Bestehender Testlauf: `node --experimental-strip-types --test tests/event_core.test.ts` im Arbeitsverzeichnis `/vps_root/flextrawurst`; **10 bestanden, 0 fehlgeschlagen**. `/vps_root/flextrawurst/tests/event_core.test.ts:149` prüft beim Append-only-Test nur das äußere Array, ein Top-Level-Feld und das Fehlen von delete/update; verschachtelte Referenzen werden nicht geprüft. Der grüne Test widerlegt den neuen Befund daher nicht.

Behebungsrichtung: Beim Append eine unabhängige Kopie mit klar definiertem Payload-Datentyp erzeugen und verschachtelte Werte rekursiv unveränderbar halten beziehungsweise defensive Kopien an Leser ausgeben. Tests für Mutation über Eingabe, `getAll`, `getById` sowie reproduzierbare Projektionen ergänzen. Keine Änderung implementiert.

Laufzeitgrenze: `/vps_root/flextrawurst/scripts/build_surface.ts:29` importiert Teile des Kernels; im gelesenen HTTP-Server `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts` wurde kein direkter Kernelimport gefunden. Das ist keine vollständige transitive Importanalyse und insbesondere kein Nachweis einer Remote-Manipulation des PostgreSQL-Eventstreams.

### Weitere geprüfte Grenzen und offene Kandidaten

- `/vps_root/flextrawurst/kernel/admin/admin_permissions.ts`, `/vps_root/flextrawurst/kernel/worldrun/worldrun_gate.ts` und `/vps_root/flextrawurst/kernel/worldrun/worldrun_command_handler.ts`: Funktionen prüfen die übergebenen Actor-Berechtigungen und Zustandsblockaden; Dry-run wendet keine Transition an. Der Actor ist hier ein vertrauenswürdiges In-Process-Argument, keine nachgewiesene HTTP-Identität. Ohne öffentlich kontrollierbaren Aufrufpfad keine Auth-Umgehung behaupten. Die getrennte Auditangabe `command.requested_by` sollte bei einer späteren externen Anbindung an den authentifizierten Actor gebunden werden.
- `/root/werkraum/welt/rag_api.py` vollständig gelesen: Admin-/Entity-Guard vor Retrieval; bei Entity wird `wesen` serverseitig aus dem Token statt aus dem gewünschten Queryparameter gesetzt. Kein Identitätswechsel allein über diesen Parameter erkennbar. Das dahinterliegende Retrieval und seine Materialrechte sind damit noch nicht vollständig geprüft. Keine echte Suche gestartet, weil Retrieval Nebenwirkungen haben kann.
- `/root/werkraum/welt/reibungsgewebe_api.py` vollständig gelesen: ausschließlich GET-Routen, parametrisierte Filter, keine eigene Authentifizierung; Originaltexte und Reibungsevents werden ausgeliefert. Ob diese Inhalte absichtlich öffentlich sind, ist noch fachlich zu klären; deshalb kein bestätigtes Privatdatenleck. `limit` hat keine obere Grenze, Detail-Events sind unpaginiert: Härtungskandidat ohne Lasttest.
- `/root/werkraum/welt/admin_einsicht_api.py`: Die gelesenen Routerdefinitionen haben keinen eigenen Admin-Guard. Eine Einbindung dieses Routers wurde in `/root/werkraum/welt/api.py` nicht gefunden; deshalb nicht als aktive anonyme Adminschnittstelle zählen. Nicht alle Modulrouten gelesen.
- `/root/werkraum/welt/api.py:11217` bis `/root/werkraum/welt/api.py:11365`: Nachrichten schreiben menschliche und Wesen-IDs in getrennte Spalten; die Gesprächs-Lesequeries prüfen die eigene ID jedoch nur in den menschlichen Spalten. Entity-Sessions können daher mit ihrer Wesen-ID voraussichtlich nicht auf diesem Pfad lesen. Statischer Funktionskandidat, keine echte Nachricht gesendet oder gelesen. Außerdem liefert `ORDER BY created_at ASC LIMIT` die ältesten statt der neuesten Nachrichten und markiert anschließend auch nicht im begrenzten Ergebnis enthaltene Nachrichten als gelesen. Keine neue IDOR-Behauptung: Für Menschen ist die eigene Token-ID weiterhin Teil beider SQL-Zweige.

Aktueller dokumentierter Stand: SEC-001 bis SEC-018 plus BUG-001 bis BUG-003, zusätzliche Kandidaten und Negativbefunde getrennt. Zeilennummern sind Momentaufnahmen; parallele Änderungen können sie verschieben.

## Fortsetzung: Erlebnis- und Beobachtungs-Neben-APIs

### SEC-019 — Ungeprüfte Entity-ID bestimmt das Schreibverzeichnis für Reaktionen

**Potentiell hoch; Pfadfehler und Route-zu-Sink-Verbindung isoliert bestätigt, produktive Datenbankvoraussetzung offen.** `/root/werkraum/welt/erlebnis_api.py:54` nimmt `entity_id` als freien String entgegen. `/root/werkraum/welt/erlebnis_api.py:84` verlangt ein gültiges Token, prüft aber weder die Entity-ID gegen bekannte Wesen noch eine Pfadgrenze. Nach dem Datenbank-Insert und Commit wird die ID an `/root/werkraum/welt/erlebnis_api.py:61` weitergereicht. Dieser Helfer bildet `VAULT_ROOT / entity_id / "reflexionen"`, legt das Verzeichnis an und hängt an eine datumsbenannte Markdown-Datei an. Eine relative Elternkomponente kann aus der vorgesehenen Wurzel `/root/werkraum/codewesen` herausführen; absolute Komponenten können die Wurzel vollständig ersetzen.

Beleg: Originalroute und Original-Schreibhelfer per AST isoliert ausgeführt; Anmeldung, Datenbank, `mkdir` und `open` vollständig durch speicherbasierte Attrappen ersetzt. Synthetische Wurzel `/synthetic/vault`, synthetische Entity-ID `../outside`, harmlose Textreaktion. Ergebnis:

```text
RESULT {'ok': True}
MOCK_OPERATIONS:
  mock_commit
  mkdir /synthetic/outside/reflexionen
  open /synthetic/outside/reflexionen/2026-09-16.md mode=a
  write_length 133
```

Keine reale Datei erstellt oder verändert, kein echter POST und kein Datenbank-Insert. Die vorhandene produktive Tabellendefinition für `erlebnis_reaktionen` wurde nicht verifiziert. Ein Foreign-Key-/CHECK-Constraint könnte die manipulierte Entity-ID schon vor dem Schreibhelfer zurückweisen; die Mock-Datenbank simuliert keine solchen Constraints. Deshalb keine durchgängig live ausnutzbare Traversal behaupten. Die Route ist im Hauptmodul `/root/werkraum/welt/api.py` zur Einbindung vorgesehen; der allgemeine Proxy unter `/vps_system/etc/nginx/sites-available/flextrawurst:788` führt zur Welt-API. Keine produktive Registrierung per Schreibprobe geprüft.

Wirkung unter der genannten Voraussetzung: Ein angemeldeter Aufrufer kann Markdown-Reaktionen außerhalb des vorgesehenen Wesen-Verzeichnisses anlegen/anhängen, soweit der Dienst Schreibrechte hat. Dateiname, Endung und Unterordner bleiben vorgegeben; **kein beliebiges Überschreiben beliebiger Dateien und keine RCE nachgewiesen**. Der zuvor geprüfte Welt-API-Prozess lief als root, was den möglichen Pfadumfang vergrößert. Auch `frage_text` wird für die Datenbank auf 500 Zeichen gekürzt, beim Dateiappend jedoch ungekürzt verwendet; die globale Requestgrenze ist kein Ersatz für die fehlende Feldgrenze.

Behebungsrichtung: Entity-ID aus der kanonischen Menge auflösen, Zielpfad normalisieren und echte Pfadzugehörigkeit zur erwarteten Wurzel prüfen; dieselben Inhaltslängen vor beiden Senken erzwingen. Datenbankconstraints als zusätzliche Abwehr prüfen. Regression mit unbekannter ID, Elternkomponenten und absoluter ID muss **vor** Commit und Dateizugriff ablehnen. Keine Reparatur durchgeführt.

### Negativbefund: Beobachtungsstart ist aktuell geschützt

`/root/werkraum/welt/beobachtung_api.py:50` ruft den vorhandenen Admin-Guard vor jeder Datenbankänderung auf. Der historische Kommentar über früher fehlenden Auth-Aufruf ist kein Beleg einer noch offenen Lücke. Der öffentliche Status unter `/root/werkraum/welt/beobachtung_api.py:89` liefert Countdown/Zeitstempel und ist ausdrücklich als öffentlich dokumentiert. Kein Start ausgelöst.

### SEC-004 ergänzt: weitere Stream-Verbindungen

Die gelesenen Streamgeneratoren in `/root/werkraum/welt/fokus_events_api.py:30` und `/root/werkraum/welt/fokus_events_api.py:74` halten je Client eine eigene PostgreSQL-Verbindung. `/root/werkraum/welt/dom_events_api.py:31` hält im gelesenen Einzel-Entity-Pfad zwei Verbindungen (LISTEN plus Leseverbindung). Das erweitert die betroffenen Oberflächen des bereits dokumentierten Ressourcenbefunds, keine zusätzliche unabhängige Befundnummer. Keine Streams geöffnet, keine Browseraufzeichnung gestartet, kein Lasttest. Die fachliche Öffentlichkeit der übertragenen Inhalte wurde nicht durch Mitschneiden überprüft.

Stand dieses Nachtrags: SEC-019 ist konditional, nicht auf dieselbe Evidenzstufe wie ein bestätigter Live-Datenabfluss setzen.
