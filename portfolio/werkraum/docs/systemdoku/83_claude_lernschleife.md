# Claude-Lernschleife (nur für Claude in Claude Code)

Stand 2026-10-04. Gilt zuerst nur für Claude. Die Bridge übernimmt es erst, wenn es hier trägt (Daniel, 2026-10-04).

## Wo es liegt

Alles unter `/config/.claude/erfahrung/` (auf dem Server: `/var/lib/docker/volumes/webtop1_config/_data/.claude/erfahrung/`).
Entwurf, Quellen und bekannte Grenzen: `ENTWURF.md` im selben Ordner.

## Bausteine

- `hook.py`: schreibt jedes Hook-Ereignis ungekürzt nach `roh_YYYY-MM.jsonl` (nur `tool_response` über 20000 Zeichen wird gekürzt und markiert).
  Bei `PostToolUseFailure` gibt er einen Halt-Block in den Kontext: bis hier gut, hier nicht mehr, Ursache.
- `lader.py`: übersetzt Session-JSONL (`projects/*/*.jsonl`) in dasselbe Ereignisformat.
- `auswerten.py`: deterministische Befunde je Turn mit Beleg. `drift.py`: Abweichungspunkte (Fehlschlag, Wiederholung).
- `pg.py`, `speicher.py`: eigener PostgreSQL-Cluster (Datenbank `erfahrung`, Socket unter `pgdata`), Import, Regelspeicher.
  Roh und Verlauf sind append-only. NUL-Zeichen fallen beim Import weg, die Zeile ist dann in `meta` markiert.
- `regeln.py`: Regeln mit Lebenszyklus CANDIDATE, TESTING, ACTIVE, WEAKENED, SUPERSEDED, RETIRED; Selbstprüfung in vier Stufen; Altern; Einspeisen; `neu` für Entscheidungen.
- `korrektur.py`: UserPromptSubmit-Hook, erkennt Korrekturen von Daniel und verlangt NOOP, UPDATE, SUPERSEDE, SPLIT, NEW oder KEINE.
- `durchsetzen.py`: Stop-Hook mit verify-retry (höchstens zweimal je Turn), blockiert nur Regeln mit `durchsetzung: blockieren`.
- `lernschleife.py`: LangGraph mit sieben Knoten (erfassen, auswerten, drift, kandidaten, testen, altern, export). Läuft im Venv `/root/bridge_speicher/venv`.
- `ansicht.py`: erzeugt `ansicht.html` (Regeln, Befunde, Driftpunkte, Verlauf) aus der Datenbank, hell, dunkel und mit Karten auf schmalen Bildschirmen.

## Schalter und Dashboard (Pausieren, Einschalten, Schichten)

Eine Hauptpause und je ein Schalter für jeden Baustein. Alle Hooks fragen vor ihrer Arbeit `schalter.aktiv(<baustein>)`; Pausieren und Einschalten braucht deshalb keine Änderung an den Settings.

- Zustand: `schalter.json` (schnell, auch ohne Datenbank); jeder Wechsel zusätzlich in `schalter_verlauf.jsonl`, nur anhängen. Jeder Eintrag nennt, wer es war (`daniel` oder `claude`), wann und warum.
- Bausteine: aufzeichnung, halt_block, korrektur_erkennung, regeln_einspeisen, stop_verifier, lernschleife. Jede Regel ist eine eigene Schicht (`regel:<ID>`).
- Schichten für kurze Momente oder ein Projekt: `schalter.py schicht neu <id> --zweck … [--projekt PFAD] [--bis 2h]`. Sie laufen von selbst ab (`bis`) oder gelten nur im Projektpfad.
  Eine beendete oder abgelaufene Schicht bleibt stehen, nichts wird gelöscht. Eine Pause mit `--bis` endet von selbst.
- Nicht schaltbar von hier (stehen in `settings.json`, nur Daniel): die alten Protokolle (`log_*`) und der unlazy-Stop-Hook. Das Dashboard zeigt sie als „fest“.
- Für mich sofort sichtbar: `regeln.py einspeisen` liefert bei jedem Prompt eine Statuszeile, auch bei Pause: „Harness AN: 6 von 6 Bausteinen aktiv“ oder „HARNESS PAUSIERT: … Wieder einschalten: python3 …/schalter.py an“.
- Buttons: Dashboard `dashboard.py` (nur 127.0.0.1:8791, Schreiben nur mit Header `X-Harness: 1`), zeigt je Zeile Zustand, **Warum** und **Wozu**; Einzelschalter sind bei Hauptpause gesperrt.
  Im Claude-Fenster: der Befehl `/harness` (Skill) oder `! python3 /config/.claude/erfahrung/schalter.py pause|an|status`.

Prüfungen: `test_schalter.py` (40 Tests, die echten Hook-Skripte als Prozesse in einer isolierten Kopie) und Playwright gegen das Dashboard (Klicks, Wirkung auf die Hooks, Schreibschutz,
Skript-Einschleusung, hell, dunkel, 390 px, Live-Test).

### Ausbau 2026-10-04 (Anregung: Dashboard-Vorstellung von ChatGPT, geprüft und angepasst)

- **Gesundheit:** Das Dashboard sagt nicht nur „an“, sondern ob ein Baustein wirklich greift. Gemessen wird zweierlei: Steht der Hook in `settings.json` (`schalter.eingetragen`), und wann ist er zuletzt gelaufen
  (jeder Hook schreibt per `schalter.puls(<baustein>)` eine kleine Datei unter `puls/`, bei einem Fehler samt Fehlertext). „Gestört“ heißt: er sollte laufen, greift aber nicht
  (zum Beispiel „nicht eingetragen: läuft nie“, mit dem Weg zur Behebung). Heute zeigt es ehrlich vier gestörte Bausteine, bis `python3 /root/eh2.py` gelaufen ist.
- **Übersicht** oben: wirksam (von allen schaltbaren), pausiert, gestört, temporär.
- **Fortsetzen ist nicht „Alles voll aktivieren“:** `schalter.py an` hebt nur die Hauptpause auf, was einzeln pausiert wurde, bleibt pausiert. `schalter.py voll` schaltet alles wieder an
  (Bausteine, Regeln, pausierte Schichten; beendete Schichten bleiben beendet).
- **Schichten haben drei Zustände:** aktiv, pausiert (umkehrbar), beendet (endgültig, nie gelöscht). Dazu `schicht verlaengern <id> 30m` und im Dashboard die Restzeit bis zum Ablauf.
- **Claudes Grenzen** (`pruefe_recht` in `schalter.py`, im Dashboard als Kasten „Was Claude gerade darf“): Einschalten jederzeit; Pausieren nur zeitlich begrenzt (höchstens 30 Minuten, `--bis`); keine Regel aus Daniels Wortlaut;
  keine Schicht von Daniel beenden; keine Pause ohne Ende. Selbst vorgeschlagene Regeln und eigene Schichten darf Claude pausieren. Begründung: Eine Harness, die der Agent, den sie schützen soll, ohne Grenze selbst abschalten kann, schützt nicht.
  Das sind Spielregeln im Programm; hart sind sie erst, wenn Daniel die Dateien schützt (zum Beispiel `chattr +i`). Das steht auch auf der Seite.
- **Live:** Der Server schickt Änderungen sofort per Server-Sent Events (`/events`, Prüfung alle 0,5 s, Lebenszeichen alle 15 s); die Seite fragt nicht mehr im Takt nach (nur als Notlösung nach 8 s Stille).
  Gemessen mit Playwright: eine Änderung von außen erscheint nach 0,1 bis 0,5 s, auch durch Nginx mit Anmeldung. Alter („zuletzt vor 12 s“) und Restzeit laufen im Browser sekündlich weiter, ohne den Server zu fragen.
  Nginx braucht dafür `proxy_read_timeout 3600s`, `proxy_buffering off` und `proxy_set_header Connection ""` (steht im Block).
- **Tabs und Untertabs (statt einer langen Seite):** Der Kopf mit Zustand, Zahlen und den drei Knöpfen bleibt immer oben. Darunter: Bauplan (Schritte, Entscheidungen, Frühere Bauten), Bausteine (eigene, feste),
  Regeln (von dir, von Claude vorgeschlagen, noch nicht aktiv), Schichten (laufend, pausiert oder beendet, neu anlegen), Was Claude darf, Verlauf, Hilfe. Zahlen-Badges zeigen Anzahl und Warnungen.
  Die Adresse merkt sich den Tab (`#regeln/dir`), also bleibt er nach dem Neuladen und lässt sich verlinken; Aufgeklapptes bleibt bei jedem Live-Update offen.
- **Sicherheit der Seite:** Content-Security-Policy (`default-src 'self'`), `X-Frame-Options: DENY`, `nosniff`, kein Referrer; alle Texte werden maskiert (Skript-Einschleusung getestet).

## Der Bauplan: den Kontext eines Baus halten (2026-10-04)

Das ist die Antwort auf Daniels Kernsatz: „ich will eigentlich dass du komplettes wissen besitz, den kontex hälts von begin eines baus bis zum abschluss, gezielt richtig und dauerhaft widerholend
auch gegenprufst und dich wider informierst währemd bauen … aber das ist alles wider halt nur text, also driftest du“. Text im Kontext reicht nicht; der Bauplan steht deshalb außerhalb von Claude und wird erzwungen.

- **Datei:** `/config/.claude/erfahrung/bauplan.json` (Verlauf nur anhängend in `bauplan_verlauf.jsonl`). Inhalt: Ziel mit Daniels Wortlaut, Schritte (Titel, **Warum**, Prüfbefehl, Status, Notiz), Entscheidungen, Archiv.
  Ein neues Ziel archiviert den alten Bauplan, nichts wird gelöscht.
- **Befehle:** `bauplan.py status | ziel | schritt | start | belegen | scheitert | zurueck | wieder | entscheidung | notiz` (Beschreibung im Kopf der Datei).
- **Belegt heißt belegt:** Ein Schritt wird nur durch `belegen` zu „belegt“: Der Prüfbefehl läuft, und nur Exit 0 mit passender Ausgabe zählt. Eine bloße Behauptung ändert nichts. Misslingt der Beleg, steht der Schritt auf „gescheitert“ mit der Ursache.
  „Gescheitert“ und „zurückgestellt“ verlangen einen Grund (Halt statt Wechseln); ein gescheiterter Schritt hat Vorrang als aktueller Schritt.
- **Wieder vorlegen:** `regeln.py einspeisen` legt mir bei jeder Nachricht von Daniel eine Kurzfassung vor: Ziel, Fortschritt, der aktuelle Schritt mit Grund und Beleg, was offen ist, die letzte Entscheidung. Auch nach einer Kürzung des Kontexts,
  weil sie aus der Datei kommt und nicht aus meinem Gedächtnis.
- **Zu frühes „fertig“ abfangen:** `durchsetzen.py` (Stop-Verifier) prüft meine Antwort: Meldet sie den ganzen Bau als fertig („alles ist fertig“, „nichts mehr offen“, „komplett abgeschlossen“) und es sind Schritte offen, muss ich nachbessern
  (höchstens zweimal, dann läuft nichts hängen). Teilmeldungen („Schritt 2 ist fertig“) sind erlaubt, zurückgestellte Schritte zählen nicht als offen.
  Zusammenspiel mit R3 („keine Schlussliste ‚noch offen‘“): ehrlich ist „Schritt 1 ist belegt. Als Nächstes baue ich Schritt 2“, keine Liste am Ende.
- **Dashboard:** Abschnitt „Der Bauplan: wo stehen wir?“ mit Fortschrittsbalken, Symbol je Schritt, hervorgehobenem aktuellen Schritt, Beleg und Ursache; live (Änderung nach etwa 0,5 s). Der Baustein „Bauplan“ ist einzeln pausierbar und hat Gesundheit und Erklärung.
- **Selbstbelegende Schritte:** „Hooks eintragen“ und „Nginx neu laden“ haben Prüfbefehle, die erst nach Daniels Handgriffen bestehen; danach genügt `bauplan.py belegen`.
- **Geprüft:** `test_bauplan.py` (23 Tests, die echten Hooks als Prozesse in einer isolierten Kopie, inklusive Überleben einer Kontextkürzung) und Playwright (Anlegen, Beleg, Scheitern, Zurückstellen, Entscheidung, alles live).

## Der Austausch: Postfach, Feedback, Anfragen, Archiv (2026-10-04, nach Daniels Rückmeldung zum Dashboard)

Anlass: Daniel fand das Dashboard „informativ“, wollte aber ein Gespräch: Vorschläge, die er annimmt, ablehnt oder kommentiert; Feedback an jeder Stelle, das Claude zwingend bekommt; Bewertungen auch von Claude;
mehr Substanz je Schritt; und keine Aufpasser-Sperren („kein Babysitting“).

- **Postfach** (`austausch.py`, Datei `austausch.json`, Verlauf nur anhängend): Arten Kommentar, Bewertung (👍 😐 👎), Vorschlag, Anfrage. Daniels Post wird mir bei der nächsten Nachricht zugestellt und muss beantwortet werden;
  der Stop-Verifier hält mich sonst höchstens zweimal an. Meine Vorschläge und Anfragen warten im Tab „Postfach → Wartet auf dich“ auf Annehmen, Ablehnen oder Kommentar; seine Entscheidung wird mir einmal zugestellt.
- **Aktionen:** Ein angenommener Posten mit Aktion wird sofort in Daniels Namen ausgeführt (`master_pause`, `baustein`, `schicht_ende`, `regel_aktivieren`, `regel_archivieren`, `regel_zurueckholen`); scheitert sie, bleibt der Posten offen.
- **Anfragen statt Sperren:** Was ich nicht allein darf (länger als 30 Minuten pausieren, Pause ohne Ende, Regel aus Daniels Wortlaut abschalten, Schicht von Daniel beenden), wird beim normalen Befehl zu einer Anfrage an Daniel
  (`AnfrageNoetig` in `schalter.py`). Der Kasten „Was Claude darf“ nennt das mit 🙋.
- **Feedback an jeder Karte:** „Austausch mit Claude“ an Baustein, Regel, Schicht und Schritt (Kommentar oder Daumen), Claudes und Daniels Einschätzung nebeneinander. Getippter Text bleibt bei Live-Updates erhalten.
- **Regeln:** Von Claude vorgeschlagene Regeln werden nach bestandener Selbstprüfung ein Vorschlag und erst nach „Annehmen und aktivieren“ aktiv (die drei vorhandenen automatischen blieben aktiv). Nichts wird gelöscht:
  „Archivieren“ legt eine Regel ins Archiv, „Zurückholen und aktivieren“ holt sie zurück (Verlauf bleibt). Untertab „Archiv“.
- **Substanz je Schritt:** `bauplan.py details <id> "<Text>" --quelle <Pfad>`; im Dashboard „Mehr dazu“ und Dokumente zum Aufklappen. `/api/dokument` liest nur .md und .txt (höchstens 400 KB) unter `docs`, `_claude`, `plan` und dem
  Harness-Ordner; Pfade werden aufgelöst, `..` und Verweise nach draußen werden mit 400 abgewiesen (getestet).
- **Verlauf** zeigt unten „Als Nächstes“ und „Bewusst später“ aus dem Bauplan; die Hilfe erklärt den Austausch.
- **Geprüft:** `test_austausch.py` (31 Tests), `test_schalter.py`, `test_bauplan.py` (zusammen 94) und Playwright (Kommentar, Zustellung, Antwort live, Vorschlag annehmen und ablehnen, Anfrage erlauben, Archiv, Dokument, Eingabe-Erhalt, Handy).

## Veröffentlichung unter https://flextrawurst.de/claudeharness/ (2026-10-04)

Das Dashboard ist für Daniel auch über die Domain erreichbar, geschützt mit Nutzer `daniel` und einem Passwort. Gespeichert ist nur der Hash.

- **Dienst:** `dashboard.py` auf 127.0.0.1:8791 im Webtop-Container (er teilt das Netz mit dem Server). Startet sich selbst wieder, wenn er fehlt: `regeln.py einspeisen` ruft bei jeder Nachricht `schalter.dashboard_sichern()` auf.
- **Nginx** (`/etc/nginx/sites-available/flextrawurst`): Block `location ^~ /claudeharness/` mit `auth_basic`, Passwortdatei `/etc/nginx/.htpasswd-claudeharness` (`root:www-data`, 640, `$apr1$`-Hash),
  Begrenzung `limit_req zone=api_limit burst=30`, `client_max_body_size 16k`, Sicherheitsköpfe (im Block wiederholt, weil ein `add_header` im `location` die des Serverblocks ersetzt), `noindex`.
  Der Präfix wird entfernt (`proxy_pass http://127.0.0.1:8791/`); die Seite benutzt nur relative Adressen.
- **Sicherung der Konfiguration:** `flextrawurst.backup-vor-claudeharness-20261004T185954Z` neben der Konfiguration. Weg zurück: Block entfernen oder die Sicherung zurückkopieren, dann Nginx neu laden.
- **Neuladen von Nginx** braucht Rechte auf dem Server (`systemctl reload nginx`); der Container sieht den Nginx-Hauptprozess des Servers nicht. `nginx -t` per `chroot /vps_system /usr/sbin/nginx -t` war erfolgreich.
- **Passwort ändern:** `bash /root/claudeharness-passwort.sh` auf dem Server (fragt zweimal, zeigt nichts an, gilt sofort, kein Neuladen nötig).
- **Geprüft** mit einer eigenen Test-Instanz von Nginx (Port 18991/18992, derselbe Block, dieselbe Passwortdatei): ohne Anmeldung, mit falschem Passwort und mit falschem Nutzer kommt 401, auch für die API;
  mit Anmeldung laufen alle Playwright-Prüfungen (Pausieren, Einschalten, Wirkung auf die Hooks, Schreibschutz, Skript-Einschleusung, hell, dunkel, 390 px).
- **Erklärungen:** Jede Karte beantwortet „Warum gibt es das?“, „Was tut es?“ und „Was passiert, wenn es aus ist?“ in einfachem Deutsch; die Texte stehen in `schalter.py` (`KATALOG`, `warum`, `was`, `wenn_aus`).
- **Hinweis zum Passwort:** Derselbe Zugang steht laut Doku schon für das MegaVault und die drei Live-Spiegel und steht dort im Klartext in älteren Dokumenten (zum Beispiel Systemdoku 46 und 56).
  Weil diese Seite Sicherungen der Harness abschalten kann, ist ein eigenes, neues Passwort ratsam (Skript oben).

## Einschalten

Die Hooks stehen erst nach `python3 /root/eh2.py` in `/config/.claude/settings.json`. Das Skript hängt nur zusätzlich an und legt vorher ein Backup an.
Claude kann die eigenen Settings nicht ändern (Claude Code sperrt das als Self-Modification), deshalb führt Daniel es aus.

## Entscheidungen und Gründe

- Eigener Cluster statt Bridge-Speicher oder flextrawurst: getrennt von laufenden Systemen (Grundgesetz 7), gleiche Engine.
- Hook-Pfad fällt auf `regeln.json` zurück, wenn der Cluster nicht läuft. Der Graph startet den Cluster bei Bedarf.
- Blockieren nur bei Regeln aus Daniels Wortlaut mit niedrigem Fehlalarm (R3, R4). Automatische Regeln warnen nur (Warnen vor Blockieren).
- Quellen der Idee (Existenz geprüft, Inhalt nur Anregung): arXiv 2606.09498, 2606.13174, 2609.29154.

## Prüfungen

- Python-Teile: Testfälle mit künstlichen und echten Daten (Entscheidungen, Wiederholungsgrenze, Altern, Import idempotent).
- Ansicht: Playwright (Chromium) vergleicht Regelzeilen, Zustände und Befundzahlen mit der Datenbank, in hell, dunkel und 390 px Breite,
  prüft Konsolenfehler und horizontales Scrollen und liest die Screenshots gegen.

## Messwerte (Altdaten, 413 Turns)

Korrekturerkennung 13 % der Prompts. Fehlalarm je Regel: R1 0,78, R2 0,31, R3 0,18, R4 0,10, R5 0,96 (R1, R2, R5 warnen nur).
Der Fehlalarm-Test ist schwach: „unbeanstandet“ heißt nur, dass Daniel im nächsten Prompt nicht korrigiert hat.

## Dashboard-Neufassung (2026-10-04): Tabs, Editieren, Papierkorb

Die Oberfläche liegt in `dashboard_ui.py`, der Server in `dashboard.py`. Tabs: Überblick, Bauplan (Jetzt / Erledigt / Zurückgestellt / Entscheidungen / Archiv), Postfach, Funktionen (früher „Bausteine“), Regeln, Schichten, Wünsche, Was Claude darf, Verlauf, Hilfe.

Fast alles ist editierbar (`/api/bearbeiten`, `/api/neu`, `/api/loeschen`). Eine geänderte Entscheidung ersetzt die alte, die alte steht im Archiv. Gelöscht wird nur auf Daniels Klick; eine Kopie liegt im Papierkorb (`papierkorb.jsonl`) und lässt sich zurückholen. `belegen` läuft nie aus dem Dashboard, nur per Kommandozeile.

Offene Vorschläge und Anfragen erscheinen oben in einer Leiste und im passenden Tab. Wünsche stehen sinngemäß in `wuensche.json`. Geprüft mit `/tmp/claude-0/pw_dashboard.py` (Playwright, auch durch Nginx mit Anmeldung).

### Rückmeldung 3 (2026-10-05): Regeln in Klartext, Postfach, Wünsche, Papierkorb

Regeln haben jetzt Name, Bedeutung und Beispiel (Spalte `meta` in der Datenbank); Messwerte stehen in Klartext. Sichten: Von dir, Von Claude vorgeschlagen, Von Claude gelten, Alle. Von Claude vorgeschlagene Regeln sind erst nach Daniels Zustimmung an.

Einschätzungen von Claude (Bewertung/Kommentar) warten im Postfach auf Daniel: Antworten oder „Gelesen“. Das Postfach trennt offen und beantwortet. Wünsche haben Art (Wunsch/Korrektur/Auftrag), Bereich, Urheber und Begründung. Der Papierkorb hat Fächer je Bereich, Erledigtes im Bauplan steht neueste zuerst. Dokumente lassen sich zu Schritten hochladen (`harness_dokumente`, nur .md/.txt).

Ursache des sich schließenden Auswahlmenüs: die Seite verglich ihre Fassung mit dem HTML des Browsers und baute bei jedem Push alles neu auf. Jetzt wird die zuletzt eingesetzte Fassung verglichen.

### Rückmeldung 4 (2026-10-05): Rückgängig, Filter, Papierkorb-Tab, Verlauf

Entscheidungen im Postfach lassen sich zurücknehmen (`austausch.zurueck`): Der Vorschlag ist wieder offen, eine gerade aktivierte Regel steht wieder im Test. Nach „Annehmen“ oder „Ablehnen“ erscheint ein Hinweis, Entschiedenes steht unter Postfach → Entschieden. Das Postfach hat Filter nach Absender und Stand. Eine neue Bewertung von Claude zum selben Ziel ersetzt die alte.

Papierkorb ist ein eigener Tab mit Fächern. Der Verlauf liest alle `*_verlauf.jsonl` und die Regelverläufe zusammen. Listen über sieben Einträge sind eingeklappt, jeder Bereich hat eine Suche. Änderungen und Löschungen von Entscheidungen meldet `bauplan.aenderungs_text` Claude einmal (Zählung der Verlaufszeilen in `bauplan_gemeldet.txt`).

### Bridge-Ausgangsmaterial und Maschinenraum (2026-10-05)

`bridge_material.py` zerlegt die Quellen der Augen-und-Hände-Bridge (ANFORDERUNGEN R001–R125 und UQ01–UQ10, Beschlüsse BE01–BE04, Plan G01–G18 mit Abnahmen E01–E10, Audit-Stand, vier Skills, Prüfketten aus `harness.py` und `praxis/lauf.py`, 93 Dokumente) in Einträge und legt sie wörtlich in `bridge_material.json` ab; ein Test prüft, dass jedes Feld in der Quelle steht. Das Dashboard zeigt sie im Tab „Bridge“, jeder Eintrag mit Quelle, Zeile und Austausch. Ändert sich eine Quelle, steht es dort.

Der Tab „Maschinenraum“ (`maschine.py`) liest live: LangGraph der Lernschleife mit letztem Lauf, PostgreSQL-Tabellen, den Erinnerer als Vorschau (`regeln.einspeisen(vorschau=True)`, markiert nichts als zugestellt), die Hooks aus den Einstellungen und die Lage der Bridge (Relay, Ereignisspeicher, Praxis-Läufe).

Harte Sperre nach Fehlern (P14 angenommen): `halt_vor_werkzeug.py` (PreToolUse) verweigert das nächste Werkzeug, bis die drei Zeilen im Text stehen; höchstens 3 Verweigerungen, Verfall nach 10 Minuten. Eintragen in die Einstellungen: `python3 /root/eh3.py` (nur Daniel).

### Betriebssystem, Bridge-Programm und Bridge-Bauzyklus (2026-10-05)

Entscheidung von Daniel: ein Betriebssystem (`/os/`), darunter Programme mit eigenen Ordnern, Daten und eigener Form (`/os/claude/`, `/os/bridge/`, später Codex und Gemini). Das frühere Bridge-Tab in Claudes Dashboard ist wieder entfernt; der Maschinenraum bleibt dort, soweit er Claudes Harness zeigt.

Aufbau unter `/config/.claude/os/`: `os_start.py` (Startseite, Port 8790, Programme aus `programme.json`), `bridge/` (Bridge-Programm, Port 8795: `bridge_kern.py` mit eigenem Ordner `zustand/`, `bridge_server.py`, `bridge_ui.py`, `bridge_cli.py`). Das Bridge-Programm hält den Stand von R001–R125 und G01–G18 (offen, implementiert, integriert, belegt, von Daniel abgenommen; Letzteres setzt nur Daniel), die Regeln aus den Skills (wörtlich, Wirkung „Hook“ oder „Erinnerung“), Postfach, Wünsche, Verlauf und zeigt die Lage der Bridge (Agentenregister, Relay, Ereignisspeicher, Praxis-Läufe) und die RAG-Suche. Post von Daniel dort erreicht Claude über `bridge_einspeisung.py`; unbeantwortete Post hält den Stop an. Start der Programme nach einem Neustart: `schalter.os_programme_sichern`.

Nginx: `python3 /root/eh4.py` legt die Adressen an (Sicherung, `nginx -t`), danach `systemctl reload nginx`.

Bridge-Bauzyklus als harte Regeln (aus dem Skill „Greenfield-Builder“, BE04): `bridge_bau.py`, `bridge_vor_schreiben.py` (PreToolUse: Schreiben in den Bridge-Ordner erst nach Lesen beider Skills und der Harness sowie Sicherungs-Commit), Prüfung beim Beenden in `durchsetzen.py` (erneutes Lesen, Körper-Tor, Playwright als letzter Testlauf, Protokoll). Funktion `bridge_bauzyklus`. Eintragen der Hooks: `python3 /root/eh3.py` (nur Daniel).
