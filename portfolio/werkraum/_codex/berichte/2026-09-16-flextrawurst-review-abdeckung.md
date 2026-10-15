# flextrawurst — Inventur und Review-Abdeckung

Stand: 2026-09-16. Autor: Codex. Zugehöriger Befundbericht: `/root/werkraum/_codex/berichte/2026-09-07-flextrawurst-sicherheitsreview.md`.

## Bedeutung dieser Inventur

Gezählt ist nicht geprüft. Es handelt sich um eine Dateisysteminventur und eine Arbeitskarte, nicht um eine Liste ausschließlich aktiven Produktionscodes. Die behaupteten 20 Millionen Zeilen sind damit weder bestätigt noch widerlegt: Weitere Host-Verzeichnisse, Symlink-Ziele und Dateitypen fehlen. Archiv-, Abhängigkeits- und Exportdateien wurden nicht gelöscht oder umsortiert.

Breite Erhebung: `rg --files --hidden --no-ignore`, ohne Git-Inhalte, für Python, TypeScript/TSX, JavaScript/JSX, HTML, SQL, Shell und PHP. Symlink-Verzeichnisse wurden nicht rekursiv verfolgt. Pfadheuristiken unterscheiden Abhängigkeiten, Archive/Referenzen, generierte Ausgaben, Tests und verbleibende Eigen-Code-Kandidaten. Nur für die letzte Kategorie wurden physische Zeilen gezählt, höchstens 8 MB pro Datei. Darin verbleiben bekannte Fehlklassifikationen wie Worktrees, HTML-Webarchive und SQL-Dumps. Das ist ausdrücklich keine verlässliche Produktionscode-Zahl.

## Breite Dateikategorien

| Wurzel / Kategorie | Dateien | Bytes | Gezählt: Kandidatenzeilen |
| --- | ---: | ---: | ---: |
| /vps_root/flextrawurst :: first_party_candidate | 185 | 3960040 | 40891 |
| /vps_root/flextrawurst :: tests | 25 | 511205 | nicht gezählt |
| /vps_root/flextrawurst :: generated_candidate | 25 | 6700581 | nicht gezählt |
| /vps_root/flextrawurst :: archive_reference_candidate | 1 | 1809 | nicht gezählt |
| /vps_root/flextrawurst :: dependencies | 5313 | 84765533 | nicht gezählt |
| /root/werkraum :: first_party_candidate | 3520 | 262616196 | 2370370 |
| /root/werkraum :: tests | 1033 | 11344948 | nicht gezählt |
| /root/werkraum :: dependencies | 38097 | 472107079 | nicht gezählt |
| /root/werkraum :: archive_reference_candidate | 1372 | 53995632 | nicht gezählt |
| /root/werkraum :: generated_candidate | 62 | 2554134 | nicht gezählt |

Die verbleibenden Kandidaten ergeben zusammen 2.411.261 gezählte Zeilen, aber nicht 2.411.261 Zeilen geprüften oder aktiven Anwendungscodes. Fünf Dateien über der Größenschwelle blieben ohne Zeilenzählung; keine Dateilesefehler in dieser Erhebung.

## Engere, reproduzierbare Arbeitsbereiche

Zweite Erhebung mit `rg`-Standard-Ignoreregeln, expliziten Sprachfiltern und Ausschlüssen für Abhängigkeiten/Referenz-/Release-/Modellordner. Die Zeilenzahlen sind deshalb nicht direkt aus der ersten Tabelle ableitbar. Identische Inhalte wurden pro Zeile dieser Tabelle per SHA-256 dedupliziert; keine globale Deduplizierung über alle Bereiche.

| Bereich | Vollständiger Pfad | Dateien | Physische Zeilen | Eindeutige Inhalte | Deduplizierte Zeilen |
| --- | --- | ---: | ---: | ---: | ---: |
| Welt Python/SQL | `/root/werkraum/welt` | 97 | 42266 | 97 | 42266 |
| Gateway | `/root/werkraum/app` | 5 | 160 | 5 | 160 |
| Node scripts | `/vps_root/flextrawurst/scripts` | 20 | 20863 | 20 | 20863 |
| Kernel | `/vps_root/flextrawurst/kernel` | 140 | 14036 | 140 | 14036 |
| Werkraum Python root | `/root/werkraum` | 76 | 29867 | 76 | 29867 |
| Tools candidates | `/root/werkraum/tools` | 693 | 227631 | 351 | 106721 |

Beim Wurzelbereich wurden nur direkt dort liegende Python-Dateien gezählt; Welt enthält Python und SQL; Gateway Python; Node-Skripte und Kernel TypeScript/JavaScript; Tools Python/TypeScript/JavaScript. Tests können in diesen Bereichen enthalten sein. Besonders bei Tools sind Laufzeitrelevanz, Kopien und Bibliotheken noch manuell zuzuordnen.

## Fachliche Review-Abdeckung

| Bereich | Bisherige Tiefe | Offene Arbeit |
| --- | --- | --- |
| `/root/werkraum/welt/api.py` | Routeninventur und gezielte Auth-/Profil-/Post-/Spur-/Upload-/Archivprüfungen | Keine vollständige Einzelroutenabnahme |
| `/root/werkraum/welt/auth.py` | Vollständige kleine Datei und Guard-Kette geprüft | Aktive Sessionwiderrufe/Regression nach Fix |
| `/root/werkraum/welt/groups_api.py` | Rechtehelfer, REST-Chat, WebSocket, Austritt und ausgewählte Materialpfade | Alle übrigen Gruppenoperationen/Statuswechsel |
| `/root/werkraum/welt/ws_manager.py` | Vollständige Datei; isolierter Austritts-/Broadcasttest | Mehrworker-Widerruf und Laufzeitabgleich |
| `/vps_root/flextrawurst/scripts/serve_process_camera_preview.ts` | Gezielte Auth-, Datei-, Charakter-, Wizard-, Archiv- und Proxyketten | Große Teile des Monolithen noch offen |
| `/root/werkraum/app` | Alle fünf kleinen Python-Dateien gelesen; Pfadprüfung isoliert getestet; Anmeldung live negativ geprüft | Befehlsrechte/Child-Prozess-Lebenszyklus tiefer prüfen |
| `/root/werkraum/systemweiser_web.py` | Middleware, Login, Passwortwechsel, Serviceverwaltung; Anmeldung live negativ geprüft | Restliche API-/Frontend-Datenflüsse |
| `/root/werkraum/web_chat.py` | Betriebsaktionen und Proxy-Schutz stichprobenartig geprüft | Gesamter Agent-/Prompt-/Dateidatenfluss |
| `/root/werkraum/api_bridge.py` | Token-/Pfad-/Exec-Routen gelesen | Deployment nicht zugeordnet; kein aktiver Exploit behauptet |
| `/vps_system/etc/nginx` | Haupt-vHost plus gezielte Nachbar-vHosts und Rate-Limits | Effektive Gesamt-Includes und alle öffentlichen Listener |
| `/vps_root/flextrawurst/kernel` | Eventvalidierung/-Store, Entity-Projektion, Adminrechte, Worldrun-Gate/-Handler gezielt gelesen; Payloadmutation isoliert bestätigt; 10 bestehende Eventtests grün | Übrige Module; transitive Laufzeitverwendung und Vertrauensgrenzen |
| `/root/werkraum/engine` | Grobe Inventur, keine Gesamtabnahme | Eigencode, importierte Engines, Exporte und aktive Dienste trennen |
| `/root/werkraum/tools` | Grobe Inventur, einzelne bekannte Brückenpfade | Dienstzuordnung; Recorder-Arbeit nur mit passenden Projekt-Skills |

## Arbeitsreihenfolge

1. Öffentliche und privilegierte HTTP-/WebSocket-Einstiegspunkte mit Dienst-/Proxyzuordnung.
2. Rechte-/Sichtbarkeits-/Provenienzgrenzen in Welt-API und Node-Server.
3. Gateway, Verwaltungsdienste, Datei-/Unterprozessgrenzen.
4. Verbleibende Frontends und Nebenmodule; Kontextregeln der Ausgabe.
5. Aktive Tools/Engine-Dienste, danach nicht exponierter Kerncode.
6. Abhängigkeiten und Deploymentkonfigurationen vervollständigen.
7. Separat beauftragte Reparaturen und Regression; dieser Review repariert nichts eigenmächtig.

Keine Prozentzahl „sicher“ oder „fertig“ aus diesen Zählungen ableiten. Ein Routenname, ein gelesener Abschnitt oder ein grüner isolierter Test ist keine vollständige Prüfung eines Dienstes.

## Nachtrag: weitere Prüfblöcke am 2026-09-16

- `/root/werkraum/welt/api.py`: Splitterliste/-Detail/-Story anhand derselben synthetischen Zeile verglichen; SEC-012 um zwei weitere Zugriffswege erweitert. Schatten-Löschfunktion und interne Zitatrolle isoliert geprüft, BUG-001/002. Öffentliche Antworten/Threads, Zitat-Eigentümerprüfung und Nachrichtenqueries statisch weitergelesen, Schutzmaßnahmen und offene Funktionskandidaten festgehalten.
- `/root/werkraum/welt/rag_api.py` und `/root/werkraum/welt/reibungsgewebe_api.py`: vollständig gelesen, keine dahinterliegenden Produktivoperationen aufgerufen. Retrieval-Implementierung und fachliche Öffentlichkeit des Reibungsgewebes bleiben offen.
- `/root/werkraum/welt/admin_einsicht_api.py`: nur Routeranfang gelesen; aktive Einbindung nicht belegt. Nicht als vollständig geprüft oder öffentlich exponiert werten.
- `/vps_root/flextrawurst/tests/event_core.test.ts`: zehn vorhandene Tests ausgeführt, alle grün. Eigene In-Memory-Gegenprobe zeigt trotzdem veränderbare Eventpayloads und veränderte Projektion ohne zusätzliches Event; BUG-003.

Alle Belege, Einschränkungen und Behebungsrichtungen stehen in `/root/werkraum/_codex/berichte/2026-09-07-flextrawurst-sicherheitsreview.md`. Keine Anwendungscodeänderungen in diesem Reviewblock.

Fortsetzung: `/root/werkraum/welt/erlebnis_api.py` Auth-, Reaktions- und Schreibpfad isoliert mit Fake-Dateisystem/DB geprüft (SEC-019; reale Datenbankconstraints offen). `/root/werkraum/welt/beobachtung_api.py` Guard und beide Handler geprüft, kein Start ausgelöst. Fokus-/DOM-Stream-Verbindungsstellen ergänzen SEC-004; keine Streamaufzeichnung oder Browseraktion. Nicht als vollständiger Recorder-/Crawler-Review werten.
