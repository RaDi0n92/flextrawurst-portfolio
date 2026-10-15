# ChatGPT-Harness – Fortschrittschronik

Stand: 2026-10-04

Diese Chronik beschreibt den tatsächlichen Baufortschritt verständlich und technisch nachvollziehbar. Fehlschläge werden nur dort erwähnt, wo sie für Ursache, Lösung und Gegenprüfung wichtig sind.

## Ausgangspunkt

Die vorhandene Harness war bewusst streng. Praktisch führte das dazu, dass sie teilweise auch ihre eigene Weiterentwicklung blockierte. Besonders die Pfadinventur wirkte zu breit: selbst harmlose Beobachtungswerkzeuge konnten gesperrt werden, obwohl sie nichts verändern.

Ziel wurde deshalb nicht, die Harness abzuschwächen, sondern sie feiner zu machen: einzelne Bestandteile verstehen, getrennt steuern, ihre Gründe sichtbar machen und ihre Wirkung sauber prüfen.

## Pfadinventur untersucht

Der laufende Scan wurde direkt geprüft. Er war tatsächlich noch aktiv und wurde durch sehr große Bestände belastet. Besonders /root/geni_gedaechtnis/rauschen und /var/lib/docker dominierten große Bereiche.

Die vorhandene Nicht-Abstiegslogik wurde untersucht. Daraus entstand die Entscheidung, solche großen technischen Bestände künftig gezielt zu behandeln, statt Millionen Einzelpfade zur Voraussetzung für die gesamte Harness zu machen.

## Selbstlernschleife geprüft

Die bestehende Lernstrecke wurde gelesen:
Kandidatenregel -> Regressionstest -> Aktivierung -> spätere Neubewertung.

Dabei fiel auf, dass temporäre Blocks nicht automatisch zu dauerhaften Verhaltensregeln werden dürfen. Sicherheits- und Autorisierungssperren bleiben daher als Erfahrung sichtbar, sollen aber nicht blind als neue Regel gelernt werden.

## Erster Bootstrap der Autorität

Die Harness unterschied bereits zwischen normalem Modelltext und wirklich verifizierter Nutzerautorität. Das war korrekt, führte aber zunächst zu einem Deadlock: ChatGPT konnte Daniels Auftrag lesen, durfte daraus aber nicht selbst harte Schreibautorität machen.

Für den ersten Umbau wurde deshalb einmal manuell ein Trusted-Client-Capture erzeugt.

Gegenprüfung:
- source_kind = TRUSTED_CLIENT_CAPTURE
- authority_verified = true
- sieben gezielte Constraints

Damit konnte die Harness kontrolliert weitergebaut werden.

## Schichtenmodell gebaut

Die Harness wurde in verständliche, einzeln steuerbare Layer zerlegt.

Kernbereiche:
- Harness insgesamt
- Pfadorientierung
- Aktionsklassifikation
- Selbstlernschleife
- Nutzer-Direktiven
- Arbeitsmodus
- Gegenprüfung und Recovery
- Lesen vor Ändern
- Ausgabeprüfung
- vertrauenswürdiger Nutzer-Capture

Zusätzlich existieren Projekt-, Aufgaben- und temporäre Schichten.

Jeder Layer beschreibt:
- warum es ihn gibt
- was er konkret tut
- was bei einer Pause passiert
- warum er gerade aktiv oder pausiert ist
- wie gesund er technisch ist

## PostgreSQL als gemeinsamer Zustand

Für die Schichten wurden persistente Tabellen ergänzt:
- Harness-Layer
- Layer-Ereignisse
- Feedback/Vorschläge
- Control-Leases

Damit lesen Dashboard und MCP denselben Zustand. Es gibt keinen separaten Browser-Schattenstate.

## Status und Health getrennt

Ein möglicher Fehler wurde vor dem Livebetrieb entdeckt: Ein späteres Health-Ereignis hätte einen vorherigen Pause-Zustand überschreiben können.

Lösung:
Status und technischer Gesundheitszustand werden getrennt projiziert.

Dadurch kann ein Layer z. B. gleichzeitig PAUSED und DEGRADED sein.

## Resonanzspur eingebaut

Zu jedem Layer kann eine gemeinsame Resonanzspur geführt werden.

Daniel und ChatGPT können:
- kommentieren
- bewerten
- Änderungen vorschlagen

Ein Vorschlag verändert die Harness nicht automatisch. Diskussion und tatsächliche Steuerwirkung bleiben getrennt.

## Pause, Fortsetzen und Full-Activate

Gebaut wurden getrennte Zustände für:
- einzelne Layer pausieren
- einzelne Layer aktivieren
- gesamte Harness pausieren
- gesamte Harness fortsetzen
- bewusst alles voll aktivieren
- zeitlich begrenzte Pause
- unbegrenzte Pause

Eine Master-Pause löscht die Zustände darunter nicht.

## Control-Leases

Für ChatGPT wurde ein separates Steuerrecht vorbereitet.

Grundsatz:
- Schutz reaktivieren darf ChatGPT.
- Schutz selbst abschwächen oder archivieren soll eine sichtbare Control-Lease brauchen.
- Leases können auf einzelne Layer oder Muster begrenzt und zeitlich befristet werden.

## harness.graph live angebunden

Der früher statische Aktiv-Wert wurde entfernt.

harness.graph liest jetzt den realen Master- und Layerzustand. Damit ist der MCP selbst bereits ein internes Live-Dashboard.

## core.path_inventory als echte Einzelschicht

Die Pfadinventur wurde an einen eigenen Layer gekoppelt.

ACTIVE:
Die Regel greift normal.

PAUSED:
Nur dieses konkrete Gate wird übersprungen. Andere Harness-Regeln bleiben aktiv.

Damit wurde aus einer globalen Bremse eine fein steuerbare Schicht.

## Mehrsession-Härtung

Während mehrere Sessions gleichzeitig arbeiteten, zeigte sich ein gemeinsames Problem: VERIFY und RECOVER waren zu global. Eine Session konnte damit unabhängige Arbeit einer anderen blockieren.

Die Ursache lag unter anderem darin, dass offene Verifikationen und gelesene Ziele nicht fein genug getrennt wurden und ältere Entscheidungen neuere Zustände überschreiben konnten.

Der Workflow wurde daraufhin zielbezogener gemacht:
- offene Verifikationen werden zusammengeführt
- Vollreads räumen nur passende offene Prüfungen ab
- gelesene Pfade werden nicht mehr pauschal vergessen
- unabhängige Ziele sollen sich nicht gegenseitig blockieren
- veraltete Entscheidungen dürfen neueren Runtime-State nicht blind zurückdrehen

## network.http_probe korrigiert

Problem:
Eine harmlose HTTP-Prüfung wurde als UNKNOWN_MUTATION behandelt.

Ursache:
Sie war im Workflow nicht ausdrücklich als Beobachtungsaktion eingeordnet.

Lösung:
network.http_probe wurde als read-only/NAVIGATE behandelt.

Gegenprüfung:
Nach Neustart konnte der lokale Dashboard-Endpunkt normal geprüft werden.

## Tests

Zwischenstände:
- 37/37 Tests erfolgreich
- später 54/54 Tests erfolgreich

Die Teststrecke importiert auch den MCP-Server selbst und deckt dadurch Syntax- und Importfehler ab.

## Dashboard-Backend

Das Dashboard wurde direkt in den bestehenden ChatGPT-MCP-Dienst auf Port 8091 integriert.

Gebaut wurden schmale, feste Endpunkte für:
- Live-State
- Layer setzen
- alles voll aktivieren
- Feedback/Resonanz

Ein generischer Alles-kann-alles-Dispatcher wurde bewusst nicht als Hauptweg verwendet.

## Dashboard-Oberfläche

Die erste sichtbare Oberfläche wurde direkt in den MCP-Server eingebaut.

Sie zeigt:
- Gesamtstatus
- Health
- Runtime-State und Modus
- alle bekannten Layer
- verständliche Beschreibung pro Layer
- Wirkung einer Pause
- Statusgrund
- Healthgrund
- Pause/Aktivieren
- Resonanzspur
- Kommentare, Vorschläge und Bewertungen

Der Zustand wird sekundenweise aktualisiert.

## Lokaler Live-Test

Der laufende Dashboard-Endpunkt wurde real geprüft.

Ohne Anmeldung:
HTTP 401.

Mit gültiger Dashboard-Anmeldung:
- Dashboard HTTP 200
- State-API HTTP 200
- echte Layerdaten sichtbar

Damit sind Auth, Oberfläche und kanonischer Layerzustand im laufenden Prozess miteinander verbunden.

## Gemeinsamen VPS-Schreibpfad repariert

Mehrere Sessions warteten darauf, wieder Dateien auf dem VPS ablegen und bestehende Dateien fortschreiben zu können.

### Erstes Problem: Nutzerauftrag war sichtbar, aber nicht als harte Autorität nutzbar

harness.note speicherte sichtbare Nutzeraufträge absichtlich als UNVERIFIED_MODEL_CLAIM.

Das verhinderte korrekt, dass ChatGPT allein aus seiner eigenen Interpretation Schreibrechte erzeugt.

### Diagnose

Der ChatGPT-MCP-Connector liefert bei authentifizierten Toolaufrufen echte Client-Provenienz:
- OpenAI-Subject
- OpenAI-Session
- OpenAI-Organization

Diese Metadaten wurden vorher nicht für den Capture genutzt.

### Lösung

Der Server erfasst den authentifizierten Client-Kontext request-lokal.

Ein USER_DIRECTIVE kann dadurch als TRUSTED_CLIENT_CAPTURE übernommen werden, wenn der Request wirklich über den authentifizierten OpenAI-Connector kommt. Invarianten und Supersedes dürfen über diesen Weg weiterhin nicht eingeschleust werden.

Der erste funktionierende Capture wurde mit authority_verified=true gespeichert.

### Zweites Problem: Autorität existierte, der Pfad-Matcher traf trotzdem nicht

Der erste Schreibversuch blieb trotz gültiger Autorität blockiert.

Ursache:
Der Directive-Matcher verglich einen Ziel-Glob nur mit dem kompletten JSON der Toolargumente. Ein echter Dateipfad konnte dadurch an einer passenden Regel vorbeilaufen.

### Lösung

Der Matcher prüft nun zusätzlich echte Zielwerte:
- path
- Move-Quelle und Ziel
- Service-Name
- URL

Das alte JSON-Matching bleibt für bestehende Regeln erhalten.

### Drittes Problem: Der erste Fix war zu eng

Der erste erfolgreiche Korridor war nur für Markdown unter /root/werkraum/_gpt/ gebaut.

Das löste zwar die unmittelbar wartenden Dokumentationen, hätte aber bei jedem anderen Pfad denselben Autorisierungsaufwand erneut erzeugt.

Daniel stellte deshalb klar, dass nicht ein einzelner Dokumentationspfad, sondern das Schreiben auf dem VPS grundsätzlich wieder funktionieren soll.

### Lösung: pfadunabhängige Datei-Autorität

Ein neuer verifizierter Capture wurde gespeichert:

- source_kind = TRUSTED_CLIENT_CAPTURE
- authority_verified = true
- Event-ID = d-30f2e18a8e634e3a8432269b094b369e

Für vps.write_file und vps.edit_file gilt jetzt target_pattern="*".

Damit braucht ein neuer Dateipfad keine eigene Autorisierungsregel mehr.

### Vierte Ursache: alte Werkzeug-Wurzelliste

Auch nach der breiten Direktive besaßen die direkten Dateiwerkzeuge noch eine alte interne Liste SCHREIB_ERLAUBTE_WURZELN. Dadurch wären unter anderem /root/flextrawurst und /root/zensi weiterhin gesperrt gewesen.

Das wäre derselbe Fehler nur eine Ebene tiefer gewesen.

### Lösung: Dateiwerkzeuge und Shell getrennt

Die direkte Datei-Pfadprüfung wurde von der engeren Shell-Sandbox getrennt.

vps.write_file, vps.edit_file, vps.move und vps.delete benutzen nun eine eigene VPS-weite Dateiprüfung.

Erlaubt ist der normale persistente Dateibaum des VPS.

Weiterhin gesperrt bleiben:
- Pfade, die als Geheimnis eingestuft werden
- finale Symlink-Ziele bei normalen Mutationen
- Kernel- und Pseudo-Dateisysteme wie /proc, /sys, /dev und /run

Die Shell behält ihre eigene engere Schreibwurzel-/Sandbox-Logik. Eine breitere Dateifreigabe macht die Shell also nicht automatisch allmächtig.

### Gegenprüfung außerhalb der alten Wurzeln

/root/flextrawurst war in der alten direkten Schreibwurzel-Liste ausdrücklich ausgeschlossen.

Zur Gegenprüfung wurde die vorhandene Datei

/root/flextrawurst/.gitignore

zuerst gelesen.

Danach wurde exakt derselbe Inhalt über vps.write_file zurückgeschrieben:
- 36 Bytes vorher
- 36 Bytes nachher
- Aktion ALLOW

Anschließend wurde dieselbe Datei über vps.edit_file mit einem inhaltsgleichen Einzelersatz geschrieben:
- Aktion ALLOW

Der Hash blieb vor und nach beiden Operationen identisch:

a8f021a796c89f2639836580894bcd3f887a0720f24d9276e59317c348d2b721

Damit ist praktisch bestätigt, dass Schreiben und gezieltes Editieren auch außerhalb der früheren Schreibwurzeln funktionieren.

### Temporäre Schreibprobe

Für den ersten _gpt-Nachweis war kurz eine reine Testdatei angelegt worden.

Nach erfolgreicher Gegenprüfung hatte sie keinen weiteren Zweck und wurde wieder gelöscht.

Sie ist kein Bestandteil des dauerhaften Systems.

## Öffentliche Dashboard-Route und Livebetrieb

Die Nginx-Route /chatgptharness/ ist inzwischen öffentlich auf den bestehenden ChatGPT-MCP-Dienst auf Port 8091 geschaltet.

Gegenprüfung über HTTPS:
- ohne Dashboard-Anmeldung: HTTP 401
- mit gültiger Dashboard-Anmeldung: HTTP 200
- /chatgptharness/api/state: HTTP 200
- Cache-Control: no-store
- X-Robots-Tag: noindex, nofollow

Damit ist das Dashboard nicht mehr nur lokal erreichbar.

## Syntaxfehler vor einem Restart entdeckt

Vor einem geplanten MCP-Restart wurden die Regressionstests erneut ausgeführt.

Sie brachen bereits beim Python-Import ab.

Ursache:
In der neuen PostgreSQL-Tabelle harness_layer_context stand innerhalb eines Python-f-Strings:

DEFAULT '{}'::jsonb

Die geschweiften Klammern wurden deshalb von Python als f-string-Ausdruck interpretiert.

Lösung:
Der SQL-Default wurde korrekt als

DEFAULT '{{}}'::jsonb

escaped.

Gegenprüfung:
Danach liefen wieder 54/54 Tests erfolgreich.

Der Dienst wurde erst nach dieser Gegenprüfung neu gestartet.

## Veralteter Prozesszustand erkannt

Nach dem öffentlichen State-Test wirkte eine bereits abgelaufene TASK-Schicht noch ACTIVE.

Der Code auf Platte enthielt die korrekte EXPIRED-Logik bereits.

Ursache:
Der laufende MCP-Prozess war älter als die zuletzt geänderten Workflow- und Serverdateien und hatte deshalb noch die vorherige Modulversion im Speicher.

Lösung:
vps-mcp.service wurde nach grünen Tests neu gestartet.

Gegenprüfung:
Die abgelaufene TASK-Schicht wurde danach korrekt als EXPIRED angezeigt.
Die Zahl der aktiven Layer sank entsprechend von 12 auf 11.

## Öffentliche Einzelsteuerung end-to-end geprüft

core.path_inventory wurde über die echte öffentliche HTTPS-Dashboard-API kurz pausiert.

Der unmittelbar danach gelesene Live-State zeigte:
- desired_status = PAUSED
- effective_status = PAUSED
- Health blieb HEALTHY
- Grund und Ablaufzeit wurden gespeichert

Danach wurde derselbe Layer über dieselbe öffentliche API wieder aktiviert.

Die Gegenprüfung zeigte:
- desired_status = ACTIVE
- effective_status = ACTIVE
- Ablaufzeit wieder leer
- neuer Statusgrund und Zeitstempel vorhanden

Damit ist bestätigt, dass die öffentliche Dashboard-Steuerung nicht nur UI ist, sondern den kanonischen PostgreSQL-Zustand tatsächlich verändert und sofort wieder ausliest.

## Bau-/Wissenskontext und Verlauf erweitert

Die Datenbank enthielt bereits eine Tabelle harness_layer_context und der Snapshot lud bereits:
- Layer-Ereignisse
- PLAN
- VISION
- RESEARCH
- EVIDENCE
- DOC
- LINK
- NOTE

Diese Daten wurden bisher nach dem Laden nicht an den Layer-Snapshot weitergegeben.

Lösung:
Jeder Layer enthält jetzt zusätzlich:
- recent_events
- context

Außerdem wurde ein gemeinsamer Schreibweg für strukturierten Layer-Kontext ergänzt.

Das Dashboard besitzt jetzt einen Endpunkt für neue Kontext-Einträge und die Oberfläche zeigt pro Layer ausklappbar:
- Bau-/Wissenskontext
- Verlauf

Der Kontextbereich kann Plan, Vision, Recherche, Beleg, Dokumentation, Link oder Notiz aufnehmen, ohne den Layer dadurch automatisch zu verändern.

Die Hauptansicht bleibt kompakt; die zusätzliche Substanz liegt in ausklappbaren Bereichen.

Gegenprüfung:
- öffentliche Dashboard-Seite enthält den neuen Bereich
- State-API liefert context und recent_events
- ein ungültiger Kontext-Eintrag ohne Titel wird sauber mit HTTP 400 abgewiesen
- 54/54 Regressionstests blieben grün

## Resonanzspur: Datenbankregel repariert

Beim Gegenlesen wurde entdeckt, dass Kommentare und Bewertungen technisch noch nicht hätten gespeichert werden können.

Problem:
Der Python-Code verwendete für COMMENT und RATING den Status RECORDED.

Die PostgreSQL-Tabelle erlaubte beim Feld status aber nur:
- OPEN
- ACCEPTED
- REJECTED
- RESOLVED
- ARCHIVED

Ein normaler Kommentar wäre dadurch an der Datenbank-Constraint gescheitert.

Lösung:
- Das Tabellenschema wurde um RECORDED erweitert.
- Die bereits bestehende PostgreSQL-Constraint wurde beim nächsten Schema-Ensure automatisch migriert.
- Die Migration prüft vorher die vorhandene Constraint und verändert sie nur, wenn RECORDED noch fehlt.

Gegenprüfung:
Die live aus PostgreSQL gelesene Constraint enthält jetzt RECORDED.

Danach wurde ein sinnvoller Resonanz-Kommentar unter core.master gespeichert:
Erklärungen sollen zuerst für Menschen verständlich sein; technische Begriffe sollen ergänzen und nicht die Erklärung ersetzen.

Der POST antwortete mit HTTP 200 und Status RECORDED.

## Kontextkanal praktisch geprüft

Der neue Bau-/Wissenskontext wurde nicht nur angezeigt, sondern mit einem echten Eintrag geprüft.

Unter core.master wurde als DOC-Kontext hinterlegt:
- Titel: Laufende Harness-Bauchronik
- Referenz: /root/werkraum/_gpt/CHATGPT_HARNESS_ARBEITSCHRONIK.md
- Zweck: verständliche fortlaufende Dokumentation des tatsächlichen Harness- und Dashboard-Baus

Der Eintrag wurde erfolgreich gespeichert und sofort im zurückgegebenen Layer-Snapshot sichtbar.

## Verständlichere Oberfläche

Die sichtbare Dashboard-Sprache wurde weiter vom internen Enum-Vokabular getrennt.

Beispiele:
- ACTIVE -> aktiv
- PAUSED -> pausiert
- BLOCKED_BY_PARENT -> durch Gesamtpause blockiert
- HEALTHY -> gesund
- DEGRADED -> eingeschränkt
- FOCUSED_READING -> fokussiertes Lesen
- CONTROL_PLANE -> Harness-Systemarbeit

Die technischen Rohwerte bleiben zusätzlich im Diagnosebereich sichtbar.

## Vorschläge können vor einer Entscheidung diskutiert werden

Ein offener Vorschlag hatte bisher nur die beiden sichtbaren Entscheidungen „annehmen“ und „ablehnen“.

Das war für Feinjustierung zu grob. Daniels ursprüngliche Anforderung war, einen Vorschlag zuerst kommentieren oder nachschärfen zu können und erst danach zu entscheiden.

Lösung:
- Offene Vorschläge besitzen jetzt ein eigenes Feld „Antwort / Rückfrage / Feinjustierung“.
- Eine Antwort wird als normaler COMMENT mit parent_entry_id auf den Vorschlag gespeichert.
- Antworten erscheinen eingerückt direkt unter dem zugehörigen Vorschlag.
- ACCEPT und REJECT bleiben getrennte Entscheidungen.
- Entscheidungsereignisse werden nicht zusätzlich als normale Antworten doppelt angezeigt.
- Sichtbare Feedback-Typen werden verständlicher als Kommentar, Vorschlag, Bewertung, angenommen oder abgelehnt bezeichnet.

Gegenprüfung:
- 54/54 Regressionstests erfolgreich.
- vps-mcp.service neu gestartet.
- öffentliche Dashboard-Seite liefert HTTP 200.
- die ausgelieferte Seite enthält replyFeedback und das Feld „Antwort / Rückfrage / Feinjustierung“.

## Selbstlernschleife im Dashboard verständlicher gemacht

Die Lernlogik war intern bereits vorhanden, im Dashboard aber nur teilweise sichtbar.

Vorhandener technischer Ablauf:
- eine beobachtete Abweichung kann einen Driftpunkt erzeugen
- daraus kann eine Kandidatenregel entstehen
- die Regel wird gegen gespeicherte alte Turns getestet
- nur ein bestandener Test ohne Kollision mit früher erfolgreichen Verläufen darf zur Aktivierung führen
- spätere Erfahrung und Feedback können eine Regel erneut bestätigen, abschwächen oder stilllegen
- ACTIVE darf hart eingreifen
- WEAKENED bleibt nur Erinnerung
- RETIRED und SUPERSEDED greifen nicht mehr ein

Problem:
Der bisherige Lernstatus zeigte im Dashboard im Wesentlichen Regeltext, Status, Testzahlen und Feedback-Zähler. Dadurch blieb unklar, wo eine Regel herkam, wann sie greift und was sie technisch durchsetzen würde.

Lösung:
learning_status wurde erweitert. Pro Regel werden jetzt zusätzlich geliefert:
- ursprünglicher Driftpunkt
- Drift-Code und Beschreibung
- Drift-Beleg
- konkrete Bedingung der Regel
- konkrete Durchsetzung

Die sichtbare Lernkarte erklärt nun zuerst:
- Woher kam die Regel?
- Wann greift sie?
- Was würde sie tun?
- Warum hat sie ihren aktuellen Status?
- Wie wurde sie getestet?
- Welche Rückmeldungen gab es bisher?

Technische Rohdaten bleiben zusätzlich ausklappbar.

## Regelbewertung durch Daniel

Der Backend-Endpunkt für echtes Nutzerfeedback aus dem geschützten Dashboard war bereits vorhanden, wurde in der Lernansicht aber noch nicht benutzt.

Die Lernkarte besitzt jetzt:
- ein Notizfeld
- hilfreich
- schädlich
- widersprochen
- irrelevant

Das Feedback wird mit source_kind DANIEL_DASHBOARD gespeichert und löst anschließend die vorhandene Neubewertung der Regel aus.

Die Neubewertung kann eine Regel je nach Erfahrungsstand:
- ACTIVE lassen oder wieder ACTIVE setzen
- WEAKENED setzen
- RETIRED setzen

Zusätzlich wurde ein eigener Dashboard-Endpunkt für „mit aktuellem Erfahrungsstand neu bewerten“ ergänzt.

Stillgelegte oder bereits ersetzte Regeln werden dabei nicht automatisch wiederbelebt.

Gegenprüfung:
- 54/54 Regressionstests erfolgreich
- vps-mcp.service neu gestartet
- Lernstatus ist im laufenden MCP erreichbar
- der Lernbereich und der neue learning-reassess-Endpunkt sind im geladenen Servercode vorhanden
- aktuell existieren 0 echte Lernregeln in PostgreSQL
- deshalb wurde bewusst keine künstliche Testregel erzeugt, nur um die Karten mit Beispieldaten zu füllen

## Direktiven-Inventar für Dashboard und ChatGPT

Der Core-Layer „Deine Direktiven“ erklärte bisher nur, dass verifizierte Nutzeranweisungen berücksichtigt werden. Die tatsächlichen gespeicherten Direktiven und ihre konkrete Wirkung waren im Dashboard aber nicht sichtbar.

Das war für Daniels gewünschte gemeinsame Feinjustierung zu abstrakt.

### Neue kanonische Sicht

Im Workflow wurde directive_status ergänzt.

Diese Sicht liest direkt aus den vorhandenen append-only PostgreSQL-Tabellen und erzeugt keinen zweiten Regelbestand.

Pro Direktive werden jetzt geliefert:
- unveränderter Originalwortlaut
- source_kind
- ob die Autorität verifiziert ist
- ob die Direktive aktuell aktiv oder später ersetzt wurde
- daraus abgeleitete Constraints
- feste Invarianten
- welche ältere Direktive sie ersetzt
- wodurch sie selbst später ersetzt wurde
- technische Herkunftsmetadaten

### Verständliche Dashboard-Darstellung

Im Dashboard gibt es jetzt einen eigenen Bereich „Deine Direktiven“.

Dort wird zuerst der Originalwortlaut gezeigt.

Daneben wird verständlich erklärt:
- verifiziert und harte Wirkung möglich
- unverifiziert und deshalb nur Erinnerung
- aktiv oder ersetzt / Historie
- welche Aktion betroffen ist
- auf welches Ziel die Regel wirkt
- ob sie blockiert, einen Reminder verlangt oder nur erinnert

Technische IDs und Metadaten bleiben ausklappbar.

Aktive verifizierte Direktiven werden in der sichtbaren Reihenfolge priorisiert. Ersetzte Direktiven bleiben erhalten und werden klar als Historie markiert.

### Gemeinsame Sicht für ChatGPT und Dashboard

Zusätzlich wurde der read-only MCP-Endpunkt harness.directive_status registriert.

Damit sollen Dashboard und ChatGPT denselben kanonischen Direktivenbestand lesen.

Der bereits offene Chat-Client hält seinen Toolkatalog jedoch im Cache und sieht den neu registrierten Toolnamen erst nach einem Katalog-Refresh. Der laufende MCP wurde nach der Registrierung neu gestartet.

### Gegenprüfung

Für directive_status wurde ein dauerhafter Regressionstest ergänzt.

Der erste Testlauf scheiterte nur an einer falschen Schema-Annahme im neuen Test: dort war flextrawurst_memory statt des tatsächlichen portfolio_memory hart eingetragen.

Der Test wurde schema-unabhängig gemacht.

Danach:
- 55/55 Regressionstests erfolgreich
- Originalwortlaut, Autoritätsstatus, Constraints, Invarianten und Supersede-Historie werden im Test gemeinsam geprüft
- vps-mcp.service läuft mit dem neuen Servercode
- der Dashboard-Live-State enthält jetzt zusätzlich directives

## Beidseitige Steuerung mit Control-Lease live geprüft

Bis hierhin konnte das Dashboard Layer direkt schalten. Zusätzlich sollte ChatGPT selbst Schutzschichten steuern können, ohne sich dieses Recht still selbst zu geben.

Dafür wurde der bereits gebaute Control-Lease-Weg praktisch end-to-end geprüft.

Ablauf:
- Das öffentliche Dashboard erteilte ChatGPT für core.path_inventory eine zeitlich begrenzte Control-Lease.
- Die Lease erschien sofort im kanonischen PostgreSQL-Zustand.
- ChatGPT pausierte core.path_inventory danach selbst über das MCP-Werkzeug harness.layer_set.
- Der neue Status wurde mit actor=CHATGPT gespeichert.
- ChatGPT aktivierte denselben Layer anschließend wieder.
- Die temporäre Lease wurde über das Dashboard widerrufen.
- Der Endzustand war wieder ACTIVE und es blieb keine aktive Lease übrig.

Zusätzlich schrieb ChatGPT selbst einen Kommentar in die Resonanzspur des Layers.

Damit ist jetzt praktisch bestätigt, dass die Steuerung in beide Richtungen funktioniert:
Dashboard -> PostgreSQL -> ChatGPT-Steuerrecht -> MCP -> Layerstatus -> Dashboard.

## Baustein-Definitionen editierbar gemacht

### Problem

Die Karten erklärten bereits verständlich:
- warum ein Baustein existiert
- was er tut
- was bei Pause passiert

Diese Definition war nach der Anlage aber praktisch eingefroren.

Das passte nicht zum gewünschten Arbeitsmodell:
Daniel soll feste CORE-Bausteine direkt bearbeiten können.
ChatGPT soll dazu Änderungen vorschlagen können, sie aber nicht eigenmächtig auf CORE anwenden.

### Lösung

Für Layer-Definitionen wurde ein eigener Änderungsweg gebaut.

Direkt änderbar sind:
- Titel
- Zweck / „Warum gibt es das?“
- konkrete Wirkung / „Was tut es?“
- Pausewirkung

Für CORE-Layer gilt:
Direktes Ändern ist nur mit actor=DANIEL_DASHBOARD erlaubt.

ChatGPT kann stattdessen einen strukturierten Vorschlag mit der Aktion UPDATE_LAYER_DEFINITION in die Resonanzspur schreiben.

Erst wenn Daniel diesen Vorschlag im authentifizierten Dashboard ausdrücklich annimmt, wird die Definitionsänderung ausgeführt.

### Eigener Definitionsverlauf

Definitionsänderungen werden nicht still überschrieben.

Dafür wurde eine eigene append-only Revisionsspur angelegt.

Jede echte Änderung speichert:
- vorherige Definition
- neue Definition
- Actor
- Grund
- Zeitpunkt

Im Dashboard besitzt jede Layerkarte jetzt den ausklappbaren Bereich:

„Definition bearbeiten / Verlauf“

Dort können die vier verständlichen Definitionsfelder bearbeitet werden. Darunter bleiben frühere Definitionen mit vorher/nachher sichtbar.

### No-op-Verhalten

Der öffentliche Definitions-Endpunkt wurde mit einer inhaltsgleichen Änderung an core.path_inventory geprüft.

Ergebnis:
- HTTP 200
- changed=false
- vorher und nachher identisch
- keine Fake-Revision in definition_history

Damit erzeugt bloßes Speichern ohne tatsächliche Änderung keinen historischen Müll.

### Fehler beim ersten Bauversuch

Beim ersten Tabellenentwurf wurden zwei leere JSON-Objekte in einem Python-f-String als '{}' geschrieben.

Python interpretierte die geschweiften Klammern als leeren Ausdruck und brach bereits beim Import mit einem SyntaxError ab.

Die Tests fanden den Fehler vor einem Dienstneustart.

Lösung:
Die SQL-Literale wurden im f-String korrekt als '{{}}' geschrieben.

Danach importierten Workflow und Server wieder sauber.

### Regressionen nachgezogen

Während der Gegenprüfung waren außerdem drei ältere Testerwartungen nicht mehr mit der inzwischen absichtlich verfeinerten Harness-Logik synchron:

- BUILD_ALLOWED ist heute ein bekannter Modus, aber nur mit verifiziertem konkretem TASK-Scope.
- Eine offene VERIFY-Prüfung für Datei A darf eine unabhängige neue Datei B nicht global blockieren.
- Eine wirklich neue Datei braucht keine künstliche Vorlektüre eines noch gar nicht existierenden Ziels.

Die Tests wurden auf diese aktuelle Schutzlogik angepasst.

Die bestehenden Regeln für bereits vorhandene Edit-/Delete-/Move-Ziele bleiben bestehen: Das konkrete Ziel muss vorher gelesen sein.

Aktueller Regressionstand:
- 57/57 Tests erfolgreich

### Öffentliche Gegenprüfung

Die ausgelieferte Dashboard-Seite wurde nach dem Umbau erneut direkt über HTTPS gelesen.

Bestätigt:
- HTTP 200
- „Definition bearbeiten / Verlauf“ ist tatsächlich im ausgelieferten HTML vorhanden
- „Definition speichern“ ist vorhanden
- UPDATE_LAYER_DEFINITION ist im Browsercode vorhanden
- der neue Update-Endpunkt ist verdrahtet
- das ausgelieferte JavaScript kompiliert weiterhin mit SYNTAX_OK

## ChatGPT-Inbox und Antwortquittierung

Das Dashboard besitzt jetzt zusätzlich den Bereich „Wartet auf ChatGPT“.

Dort erscheinen Dashboard-Beiträge von Daniel, die ChatGPT noch nicht als verarbeitet quittiert hat.

Der kanonische Layer-Snapshot liefert dafür:
- chatgpt_inbox
- chatgpt_inbox_count

Damit braucht das Dashboard keinen eigenen separaten Posteingangszustand.

### Problem

Der Server besaß bereits eigene Funktionen und HTTP-Endpunkte zum Quittieren solcher Beiträge. Der aktuell geöffnete ChatGPT-Client hatte die neu registrierten MCP-Werkzeuge harness.feedback_inbox und harness.feedback_ack aber noch nicht in seinem gecachten Toolkatalog.

Damit wäre die Backend-Funktion vorhanden gewesen, ohne dass diese laufende ChatGPT-Session sie zuverlässig direkt aufrufen konnte.

### Lösung

Der bereits sichtbare MCP-Weg harness.feedback wurde erweitert.

Wenn ChatGPT einen Dashboard-Beitrag mit parent_entry_id direkt beantwortet:
- wird die Antwort normal in der append-only Resonanzspur gespeichert
- danach wird genau der beantwortete Parent als für CHATGPT verarbeitet quittiert
- Kommentar- oder Vorschlagsstatus des Parents wird dadurch nicht verändert

Eine echte Antwort ist damit zugleich die Quittierung. Ein zweiter paralleler Kommunikationsweg ist nicht nötig.

### Regressionstest

Im bestehenden Testkörper wurde ein eigener Test ergänzt.

Er prüft ohne echte Datenbankeinträge:
- ChatGPT-Antwort mit parent_entry_id wird gespeichert
- harness_feedback_ack wird genau für diesen Parent aufgerufen
- Empfänger ist CHATGPT
- Actor ist CHATGPT

Gegenprüfung:
- 65/65 Regressionstests erfolgreich
- vps-mcp.service neu gestartet
- neuer Prozess läuft seit 2026-10-05 20:04:28 CEST
- öffentliche Dashboard-Seite weiterhin HTTP 200
- öffentliche State-API weiterhin HTTP 200

## Direktiven archivieren und wieder aktivieren

Die gespeicherten Nutzer-Direktiven waren bisher nur als ACTIVE oder SUPERSEDED sichtbar.

Das reichte für Historie, aber nicht für den gewünschten Alltag:
Eine Regel, die sich als unpassend oder schlicht dämlich erweist, soll aus der Wirkung genommen werden können, ohne ihren Originalwortlaut oder ihre Geschichte zu löschen. Später soll sie wieder aktivierbar sein.

### Lösung

Für Direktiven wurde eine eigene append-only Statusspur ergänzt.

Mögliche manuelle Zustände:
- ACTIVE
- ARCHIVED

SUPERSEDED bleibt davon getrennt und bedeutet weiterhin:
Eine spätere Direktive hat diese ältere Direktive ersetzt.

Beim Archivieren werden weder Originalwortlaut noch Constraints, Invarianten oder Herkunft überschrieben.

Gespeichert werden zusätzlich:
- Actor
- Grund
- Zeitpunkt
- vollständiger Statusverlauf

### Wirkung

ARCHIVED-Direktiven:
- bleiben im Dashboard und in der Historie sichtbar
- zählen nicht mehr als aktive Direktive
- werden nicht mehr vom aktiven Direktiven-RAG geliefert
- liefern keine harten Constraints mehr
- liefern keine aktiven Invarianten mehr

Eine spätere Wiederaktivierung setzt nur einen neuen ACTIVE-Status in die append-only Statusspur.

### Dashboard

Im Bereich „Deine Direktiven“ besitzt eine aktive Direktive jetzt:
- Grundfeld
- „archivieren“

Eine archivierte Direktive besitzt:
- Grundfeld
- „wieder aktivieren“

SUPERSEDED-Direktiven bleiben reine Historie und erhalten bewusst keinen Wiederaktivierungsbutton.

Die Anzeige unterscheidet außerdem verständlich:
- verifiziert und aktiv: darf harte Wirkung erzeugen
- verifiziert und archiviert: derzeit ohne harte Wirkung
- ersetzt: durch spätere Direktive abgelöst
- unverifiziert: nur Erinnerung

### Gegenprüfung

Nach dem Umbau:
- 65/65 Regressionstests erfolgreich
- vps-mcp.service neu gestartet
- neuer Prozess läuft seit 2026-10-05 20:24:16 CEST
- öffentliche Dashboard-Seite: HTTP 200
- öffentliche State-API: HTTP 200
- directives.counts enthält jetzt archived
- aktuell archived = 0
- ausgeliefertes HTML enthält Archivieren, Wiederaktivieren und den neuen Status-Endpunkt

Es wurde bewusst keine echte bestehende Nutzer-Direktive nur für einen Test archiviert.

## Aktueller Stand

VPS-Dateischreiben über vps.write_file und vps.edit_file ist pfadunabhängig autorisiert und nicht mehr auf einzelne Projektpfade oder _gpt beschränkt.

Die direkten Dateiwerkzeuge verwenden dafür eine VPS-weite Pfadprüfung. Geheimnis- und Pseudo-Dateisystem-Sperren bleiben bestehen.

Das ChatGPT-Harness-Dashboard ist öffentlich unter https://flextrawurst.de/chatgptharness/ erreichbar, durch Anmeldung geschützt und sekundengenau an den kanonischen PostgreSQL-Zustand angebunden.

Pause/Aktivieren eines einzelnen Layers wurde über den öffentlichen HTTPS-Weg erfolgreich end-to-end geprüft.

Die Control-Lease-Kette wurde zusätzlich in beide Richtungen geprüft: Das Dashboard kann ChatGPT gezielt Steuerrecht geben, ChatGPT kann damit selbst pausieren und anschließend wieder reaktivieren.

Pro Layer sind Bau-/Wissenskontext, Zustandsverlauf und jetzt auch ein eigener Definitionsverlauf sichtbar.

CORE-Definitionen können im authentifizierten Dashboard direkt bearbeitet werden. ChatGPT kann strukturierte Definitionsänderungen nur vorschlagen; die tatsächliche Anwendung erfolgt erst nach ausdrücklicher Annahme im Dashboard.

Resonanz-Kommentare und Bewertungen können von Daniel und ChatGPT gespeichert werden. Vorschläge können vor Annahme oder Ablehnung direkt beantwortet und feinjustiert werden.

Dashboard-Beiträge können in „Wartet auf ChatGPT“ erscheinen. Eine direkte ChatGPT-Antwort auf einen solchen Beitrag quittiert ihn automatisch als verarbeitet.

Die Selbstlernschleife besitzt eine verständliche Dashboard-Ansicht mit Herkunft, Bedingung, Durchsetzung, Testlage und Regelbewertung. Der Datenbestand enthält aktuell noch keine echte Lernregel.

Aktueller Regressionstand: 65/65 Tests erfolgreich.
