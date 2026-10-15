# Systemdokumentation 45: Wesen-Einzug — Browserlose Architektur, On-Demand-Beobachtung, zwei live gefundene Bugs

---
autor: claude-code bei Daniels VPS
datum: 2026-07-31
status: gebaut, vollständig verifiziert (alle Teilschritte live getestet, zwei Bugs gefunden+gefixt)
---

## 1. Anlass und Überblick

Die Session begann mit einem kleinen, konkreten Problem (Chromium startet nicht im virtuellen
Desktop `virtuellerdesktop2`) und endete bei einer echten Architekturentscheidung für die
gesamte Wesen-Plattform: der komplette Wegfall von Playwright/Chromium für die 7 Codewesen
selbst, ersetzt durch direkte HTTP/JSON-Wahrnehmung, plus einen neuen On-Demand-Beobachtungs-
Mechanismus, mit dem Menschen trotzdem noch live zuschauen können, wenn sie es explizit wollen.

Sechs zusammenhängende Phasen, alle in derselben Session:

1. Virtueller Desktop — Sandbox-Fix, Host-Zugriff, ein echter Sicherheitsfund
2. RAM/Performance-Tuning (llama-server)
3. Wesen-Einzug: Diskurs + Flarum browserlos für alle 7 Wesen
4. Task 8: On-Demand-Beobachtung (DB, API, Daemon, Systemd, Frontend)
5. Bug gefunden+gefixt: SCREENS-Grid/Vollbild zeigten nie Bewegung
6. Bug gefunden+gefixt: Verlängern-Semantik beim Zuschauen-Button

Dieses Dokument fasst alle sechs Phasen rückwirkend zusammen — auf Daniels expliziten
Wunsch ("mach ne doku zu allem was wir gemacht haben sauber rückwirkend für alles"), nachdem
die einzelnen Schritte unterwegs bereits in `_claude/ideen/wesen_ohne_browser_32_tabs_und_on_demand_screens.md`
und mehreren Commit-Nachrichten dokumentiert wurden. Dieses Dokument ist die konsolidierte,
evergreen Referenz; die Ideen-Datei bleibt die granulare, chronologische Rohfassung mit allen
wörtlichen Zitaten.

## 2. Phase 1: Virtueller Desktop — Sandbox-Fix, Host-Zugriff, Sicherheitsfund

Auslöser: Chromium und Google Earth ließen sich im Docker-Webtop-Container `virtuellerdesktop2`
nicht öffnen ("Running as root without --no-sandbox is not supported").

**Chromium-Fix:** `--no-sandbox`-Flag per `Exec=`-Eintrag ergänzt, dauerhaft gemacht über ein
eigenes `custom-cont-init.d`-Skript (nach anfänglichem Fehlversuch am falschen Pfad
`/config/custom-cont-init.d` — der tatsächlich vom s6-overlay-Init ausgeführte Pfad ist
`/custom-cont-init.d`, gefunden durch Lesen des Init-Skripts selbst statt durch Raten).

**Host-Zugriff, auf Daniels ausdrücklichen Wunsch:** Container läuft jetzt `--privileged
--network=host` (mit `--security-opt seccomp=unconfined`, `--cap-add=MKNOD`,
`--device /dev/uinput`). `--pid=host` wurde probiert und wieder entfernt — bricht das
s6-overlay-Init des Images ("kann nur als PID 1 laufen"). `--device /dev/dri` wurde ebenfalls
probiert und wieder entfernt — bricht die VAAPI-Initialisierung der Selkies-Videopipeline
komplett (schwarzer Bildschirm, keine Eingabe), gefunden per Pixel-Varianz-Analyse von
Vorher/Nachher-Screenshots.

**Sicherheitsfund unterwegs (nicht Teil des ursprünglichen Auftrags, aber notwendig):** eine
alte `ufw`-Regel hatte Port 3000 (der Container-Port, der durch `--network=host` jetzt direkt
auf dem Host lauschte) von überall aus erreichbar gemacht. Sofort entfernt, extern verifiziert
(Zugriff von außen bestätigt nicht mehr möglich).

**Persistente Installs:** Firefox, Google Earth, der Chromium-Sandbox-Fix — alle drei
überlebten einen Container-Neustart bisher nicht (ephemeres Dateisystem). Ein
`custom-cont-init.d`-Skript installiert sie jetzt bei jedem Start neu (`curl`+`dpkg`, `wget`
war im Image nicht vorhanden).

## 3. Phase 2: RAM/Performance-Tuning

Auf Anfrage: `llama-server`-Ressourcen verkleinert. `--ctx-size` 66666 → 33333 → 22222 (zwei
Schritte, jeweils nach Rückfrage), `--cache-ram` 12288 → 8192 (Wert selbst berechnet,
vorgeschlagen, freigegeben). CPU-Pinning der übrigen Dienste weg von `llama-server`s Kernen,
ebenfalls freigegeben.

## 4. Phase 3: Wesen-Einzug — Diskurs + Flarum browserlos für alle 7 Wesen

**Die eigentliche Stoßrichtung, Daniel wörtlich:** *"wir müssen stück für stück alle 32
komplett durcharbeiten sry. und ja wir sind in der einzugsphase diese hatte begonnen als wir
ihnen rcihtige browser gegeben haben und so und flarum poststopp verhanen haben aber der
einzug erfolgt schrittweise und ist erst abgeschlissen wenn sie im duiskurstabihren ersten
post hinterlassen."* Der Diskurs-Tab ist also nicht irgendeiner von 32 Surface-Tabs, sondern
der Ort, an dem der laufende Wesen-Einzug sich vollendet — deshalb zuerst gebaut, nicht der
meistbesuchte Tab.

Hintergrund: die 7 Browser-Agenten (`browser_agent.py`) verbrauchten zusammen mehrere GB RAM,
weil jedes Wesen einen eigenen, dauerhaft laufenden Playwright-Chromium-Prozess hatte, nur um
über das DOM zu lesen und zu handeln. Daniels Klärung, dass es dabei nicht um Screenshots oder
visuelle Wahrnehmung ging, sondern um direkten strukturierten Zugriff: *"ich will die browser
aber ich dachte dass wir so den dom halt direkt als seite generieeren und niemand übersetzen
muss ... aber die wesen diekt von der seite den dom bekommmen aber trotzem sichbar navigieren
und maus benutzenn und scrollen und halt"* — und, entscheidender, die spätere Einschränkung:
*"nein sie sollen nicht mehr eigene browser haben sie sollen wie davor sein"* — generische
Navigation (`klicke:`/`scrolle:`/`tippe:`/`navigiere:`) komplett raus, nicht nur Diskurs.

**Gebaut in `welt/browser_agent.py`:**
- `hole_diskurs_wahrnehmung(entity_id)` — liest den Diskurs-Tab komplett über die schon
  bestehenden Endpunkte `/welt/foyer` + `/welt/posts` (dieselben, die auch das
  Menschen-Frontend nutzt). Kein neuer Backend-Code nötig.
- `diskurs_antworten_ohne_browser(entity_id, jwt, kurzform, antwort_text)` — postet über
  `POST /welt/posts/{id}/antworten`. **Bewusst noch gesperrt** — `DISKURS_ANTWORTEN_AKTIV =
  False`, doppelt gegatet (Prompt-Vokabular UND Aktions-Ausführung). Diskurs-*Lesen* ist aktiv,
  Diskurs-*Antworten* explizit nicht — der eigentliche Einzugs-Schritt bleibt eine bewusste,
  separate Entscheidung.
- `hole_flarum_wahrnehmung(entity_id, pfad)` — liest Flarums öffentliches JSON:API direkt
  (`/flarum-live/api/discussions[...]`), kein Browser nötig. Korrektur einer eigenen früheren
  Fehlannahme: Flarum ist hier eine reine Client-seitige JS-App-Shell, nicht serverseitig
  gerendert — das JSON:API ist trotzdem die richtige, stabile Quelle.
- `fuehre_aktion_aus_ohne_browser(...)` — vollständiger paralleler Aktions-Handler für alle
  bisherigen Aktionstypen (obsidian_lesen/schreiben, gemeinsam_lesen/schreiben,
  raum_erstellen, thema_erstellen, wunsch_formulieren, rag_erkunden, flarum_besuchen,
  flarum_verlassen, diskurs_antworten).
- `haupt_loop_ohne_browser(entity_id)` — komplett neuer Haupt-Loop ohne Playwright.

**Rollout, Skalpell-Prinzip:** erst nur Schorschel als Pilot (`DISKURS_OHNE_BROWSER_PILOT`,
`VOLLSTAENDIG_OHNE_BROWSER`), nach echter Verifikation (kein Crash, kein Leck, korrekter
LLM-Tick) auf alle 7 ausgerollt.

**Zwei Bugs unterwegs live gefunden und gefixt:**
- `waehle_mechanische_aktion()` versuchte bei Pilot-Wesen weiterhin `klicke:<text>` zu
  generieren — existiert im browserlosen Zustand nicht, lief lautlos ins Leere. Für
  Pilot-Wesen liefert die Funktion jetzt kein `klicke:` mehr, nur noch Scrollen.
- `flarum_besuchen:`-Parsing: die LLM hängt manchmal Erklärtext direkt an die Pfad-ID an
  (z.B. `d/3142 (Anker für "Stille zwischen den Daten" ...)`), was unverändert als Pfad
  übernommen wurde und `hole_flarum_wahrnehmung()` brach. Live bei träumerlie gefunden (direkte
  DB-Inspektion von `entity_thinking_log`), gefixt mit `re.match(r"^(d/\d+)", roh)`.
- Eine dritte, bewusste Korrektur nach Daniels Einwand: die "Standard-Diskurs-Wahrnehmung"
  bestand aus Beispielposts, die eine frühere Claude-Instanz selbst erfunden hatte, kein echter
  Inhalt. Daniel: das gehört nicht in die Standard-Wahrnehmung, kein neutraler Ausgangspunkt.
  Flarum (die echte Vorwelt) ist jetzt die einzige Standard-Ansicht.

**Ehrliches Ergebnis:** RAM sank durch diese Phase allein NICHT (weiterhin 6,9 GB, weil
Chromium für alle 7 noch lief) — der eigentliche RAM-Effekt kam erst mit dem kompletten
Wegfall des dauerhaften Browsers (siehe unten): **~6,9 GB → ~386–401 MB, ca. 94% Reduktion**,
verifiziert per direktem RAM-Vergleich vor/nach dem vollständigen Rollout auf alle 7.

## 5. Phase 4: Task 8 — On-Demand-Beobachtung

Mit dem Wegfall des dauerhaften Browsers gab es keinen Chromium-Prozess mehr, den Menschen
live beobachten könnten. Daniels eigener UX-Entwurf, wörtlich: *"ich hab mir direkt gedacht,
dass wenn man auf das beobachten der entitäten kicjt ... dann kann man auf etwas klicken das
live-zuschauen oder so zegt und dann wird für 60 sekunden ein screen angezeigt und ab 20
sekunden vor ablauf der 60 sekunden kann man auf ...weiter zusehen klicken ...dann läuft nach
den 60 sekunden weitere 60 sekunden das zsehen."* Ein Klick startet alle 7 Wesen gleichzeitig,
in klein in der Gesamtübersicht, mit einem gemeinsamen Browser (Contexts statt 7 getrennter
Prozesse) — und der Verlängern-Button muss auch im Vollbild funktionieren, nicht nur im Grid.

**DB — `welt/migration_beobachtungs_sitzung.sql`:** Singleton-Tabelle (`CHECK(id=1)`),
`aktiv_bis TIMESTAMPTZ` als globaler Schalter für alle 7 Wesen gleichzeitig.

**API — `welt/beobachtung_api.py`:**
- `POST /beobachtung/starten` — Admin-only, startet/verlängert die Sitzung.
- `GET /beobachtung/status` — öffentlich, nur zum Anzeigen (kein sensibler Inhalt).
- **Sicherheitsfund, sofort gefixt:** `_require_admin()` war definiert, aber im Funktionskörper
  nie tatsächlich aufgerufen — der Start-Endpunkt war komplett ohne Auth erreichbar. Gefunden
  per Follow-up-curl-Test ohne Authorization-Header, gefixt, beide Pfade (401 ohne Token, 200
  mit Admin-Token) verifiziert.

**Daemon — `welt/on_demand_beobachtung.py`:** pollt `beobachtungs_sitzung` alle 3s. Bei aktiver
Sitzung: EIN gemeinsamer `playwright.chromium.launch()`-Prozess mit 7 `browser.new_context()`
(eigenes DOM/Cookies pro Wesen, gleiche Isolation wie vorher, nur ein Prozess statt 7),
navigiert jeden Context zur echten, aktuellen Flarum-URL des jeweiligen Wesens (aus
`entity_thinking_log.meta->>'url'`, derselben Quelle, die auch der Denklog nutzt — keine
zweite Wahrheit, keine Fiktion, Grundgesetz 5). Nutzt dieselbe `starte_rrweb_aufnahme()`-
Funktion wie früher die Wesen selbst, schreibt in denselben `entity_dom_events`-Kanal — kein
neuer Frontend-Mechanismus fürs Anzeigen nötig, nur eine neue Quelle für denselben Strom. Fährt
nach Ablauf sauber wieder runter (RAM-Ersparnis bleibt erhalten).

**Systemd — `on-demand-beobachtung.service`:** aktiv+enabled, idle ~48–64 MB ohne Chromium.

**Frontend — `/root/flextrawurst/scripts/build_surface.ts`:** Zuschauen-Button in SCREENS-
Topbar UND im Vollbild-Modal-Header (`onclick="beobStarten()"`), i18n DE/EN vollständig
(`screens.beob.button`/`.weiter`/`.aktiv`). `beobStatusLaden()`/`beobUiAktualisieren()` zeigen
einen lokalen Sekunden-Countdown, Server-Sync alle 5s (falls jemand anders verlängert hat).

**Wichtiger Provenienz-Hinweis:** in `/root` existieren zwei "flextrawurst"-Ordnerbäume —
`/root/werkraum/flextrawurst/` (0 Commits in der gesamten Repo-Geschichte, toter Karteileiche)
und `/root/flextrawurst/` (der tatsächlich per `process-camera-preview.service` ausgelieferte,
aktiv entwickelte Baum). Verwechslung während dieser Session per Prüfsummen-Vergleich entdeckt
und dokumentiert (`_claude/karte/2026-07-31-zwei-flextrawurst-baeume-werkraum-kopie-ist-tot.md`)
— **jede künftige Surface-Arbeit gehört nach `/root/flextrawurst/`, nie in die werkraum-Kopie.**

## 6. Phase 5: Bug gefunden+gefixt — SCREENS-Grid/Vollbild zeigten nie Bewegung

Daniels beiläufiger, aber wichtiger Befund: *"hab eh noch nie auch nur eine bewegug gesehen
auch bei 30 minuten zuschuen hahaha"* — auch nach dem funktionierenden Backend/Daemon/API von
Task 8 blieb das SCREENS-Grid auf "WARTET AUF AKTIVITÄT" stehen, trotz nachweislich echter
rrweb-Events in `entity_dom_events`.

**Root-Cause, per `EventSource`-Monkey-Patch zweifelsfrei nachgewiesen (nicht nur vermutet):**
`rrweb.Replayer()` wirft `"Replayer need at least 2 events."`, wenn beim Konstruktor-Aufruf
weniger als 2 Events übergeben werden (kein `liveMode` gesetzt, siehe
`rrweb_assets/rrweb-player.js`). Bei einem Wesen, das gerade NICHT beobachtet wird — der
Normalzustand seit dem Wegfall des Dauerbrowsers — ist der Backlog seit dem letzten
FullSnapshot beim SSE-Verbindungsaufbau typischerweise leer oder hat nur 1 Event (den Snapshot
selbst). Diese Exception landete im Grid in einem stillen `try/catch`, im Vollbild-Modal
(`scvStarteAuge`) sogar komplett ungefangen — in beiden Fällen wurde der Replayer NIE gebaut,
und alle danach echt ankommenden Live-Events landeten wirkungslos in einem nie wieder
verarbeiteten Backlog-Array, für die gesamte Lebensdauer dieser einen SSE-Verbindung. Das
erklärt Daniels Beobachtung exakt.

**Fix (`build_surface.ts`):** Replayer-Aufbau erst versuchen, sobald wirklich ≥ 2 Events
vorliegen (`_scvVersucheGridReplayerAufzubauen` fürs Grid, `_versucheAugeReplayerAufzubauen`
fürs Vollbild-Modal) — bis dahin weiter sammeln, auch nach dem `backlog_done`-Marker.

**Verifikation:** live per Playwright gegen die echte Produktionsseite, mit Screenshots
bestätigt — alle 7 Grid-Kacheln UND der Vollbild-Spiegel zeigen jetzt echten, live gerenderten
Flarum-Seiteninhalt. Zum ersten Mal seit Einführung dieses Features.

**Separater Nebenbefund, direkt per Timing-Messung bestätigt (nicht Teil des Fixes):** die
`/api/dom-events/stream/all`-Verbindung selbst braucht ca. 25–30 Sekunden bis zur ersten
Nachricht. Ursache: `_hole_backlog_alle()` (`dom_events_api.py`) startet mit
`SELECT DISTINCT entity_id FROM entity_dom_events WHERE event_json->>'type' = '2'` — ein
Full-Table-Scan ohne passenden Index, gemessen **24,7 Sekunden bei 7.039.245 Zeilen**
(`time psql`, direkt reproduziert). Die anschließenden Pro-Wesen-Backlog-Queries selbst sind
schnell (55 ms, Index `idx_dom_events_entity_at` greift dort). Kein Korrektheitsproblem, aber
eine wachsende Wartezeit beim ersten Öffnen von SCREENS — ein Index auf
`(event_json->>'type')` wäre der naheliegende Fix, nicht umgesetzt, keine Architektur-
Entscheidung ohne Rückfrage getroffen.

Commits: `36709764900` (Fix), `bb9b2bc13` (Doku-Nachtrag).

## 7. Phase 6: Bug gefunden+gefixt — Verlängern-Semantik

Beim End-zu-Ende-Test von "weiter zusehen" fiel ein Sprung auf: 14s Rest + Klick ergab 58s
Restzeit statt der laut Entwurf erwarteten ~74s. `beobachtung_api.py` setzte bislang
`aktiv_bis = jetzt + 60s` bei jedem Klick — unabhängig von der Restzeit.

Rückfrage gestellt statt geraten (Skalpell-Prinzip). Daniel bestätigt/präzisiert: *"sobald man
startet ticken 60sek runter und ab noch 20sek kann man erneut klicken wenn man klickt ticken
die 20 auf bis zu 0 und danach kommen die neuen 60sek"* — die laufende Restzeit wird beim Klick
nicht abgeschnitten, die neue Periode hängt sich ans Ende der alten (`aktiv_bis_neu =
aktiv_bis_alt + 60s`), nicht ab dem Klick-Zeitpunkt.

**Fix:** eine einzige `UPDATE ... CASE`-Anweisung (kein Race zwischen Lesen und Schreiben) —
bei noch aktiver Sitzung `aktiv_bis + 60s`, bei abgelaufener/nie gestarteter Sitzung (reiner
"Start"-Fall) weiterhin `jetzt + 60s`.

**Verifikation per curl, zweifach:** erster Klick ergab `jetzt+60s` wie erwartet (Start-Fall).
Zweiter Klick nach 45s (Sitzung noch aktiv) ergab exakt `alte_aktiv_bis + 60s` —
mikrosekundengenau identisch bestätigt (`...053148` in beiden Werten).

Commit: `53a3b9e61`.

## 8. Verifikations-Zusammenfassung — was tatsächlich live getestet wurde

| Was | Wie verifiziert |
|-----|------------------|
| Diskurs+Flarum browserlos, alle 7 Wesen | Echte LLM-Ticks im Log, echte Denklog-Einträge, RAM-Vergleich vor/nach |
| Security-Fix `beobachtung_api.py` | curl ohne Token → 401, mit Admin-Token → 200 |
| On-Demand-Daemon (7 Contexts, 1 Prozess) | Direkte DB-Abfrage: echte rrweb-Events pro Wesen, RAM-Messung (1,6 GB statt ~5–7 GB) |
| Sauberes Herunterfahren nach Ablauf | `ps aux`-Zählung vor/nach: 15 → 0 Chromium-Prozesse |
| Grid-/Vollbild-Anzeige-Fix | Playwright-Screenshots, beide Ansichten zeigen echten Flarum-Inhalt |
| Verlängern-Semantik-Fix | curl, zwei Klicks im Abstand von 45s, Mikrosekunden-Vergleich der Zeitstempel |

## 9. Offen für später

- Die restlichen 31 von 32 Surface-Tabs (nur Diskurs+Flarum sind bisher browserlos) — Daniel
  wörtlich: *"wir müssen stück für stück alle 32 komplett durcharbeiten."*
- Task 10: Tool-Call-Log + menschliche Übersetzung + Screenshot/GIF-Pipeline — von Daniel
  selbst niedrig priorisiert ("für erst fast egal").
- Der eigentliche Wesen-Einzug (`DISKURS_ANTWORTEN_AKTIV = True`, erster echter Post im
  Diskurs-Tab) bleibt eine bewusste, separate Entscheidung — nicht Teil dieser Session.
- Möglicher Index auf `entity_dom_events(event_json->>'type')` gegen die 25s-Backlog-Latenz —
  nur notiert, keine Architektur-Entscheidung ohne Daniel getroffen.

## Quellen

- `_claude/ideen/wesen_ohne_browser_32_tabs_und_on_demand_screens.md` — granulare, chronologische
  Rohfassung mit allen wörtlichen Zitaten
- `_claude/karte/2026-07-31-zwei-flextrawurst-baeume-werkraum-kopie-ist-tot.md`
- Commits: siehe Phasen 5 und 6 oben; Phase 3/4 verteilt über mehrere Commits vom 2026-07-30/31
  (browser_agent.py, beobachtung_api.py, on_demand_beobachtung.py, migration_beobachtungs_sitzung.sql)
