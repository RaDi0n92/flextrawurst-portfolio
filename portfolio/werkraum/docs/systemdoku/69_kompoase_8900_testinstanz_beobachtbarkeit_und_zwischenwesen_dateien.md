# Systemdokumentation 69: KompOase 8900 — Testinstanz: vollständiger Bau bis Beobachtbarkeit + Zwischenwesen-Dateien gesichtet

---
autor: claude-code bei Daniels VPS
datum: 2026-09-18
status: Testinstanz live, Observability-Teil abgeschlossen, Zwischenwesen-Recherche unterbrochen durch Absturz
---

## 1. Anlass

Daniel bat nach dem zweiten Desktop-Absturz des Tages (siehe Chat-Log 10:06 Uhr) darum, den
kompletten Bau der KompOase-Testinstanz auf Port 8900 zu dokumentieren, dazu einmal alle
Zwischenwesen-Konzeptdateien zu benennen, die zuvor recherchiert wurden, und kurz
zusammenzufassen, was daraus gelesen wurde — alles in einem Dokument.

## 2. Was und wo — Grundlagen

Der eigentliche Code für Port 8900 liegt **nicht** unter `/root/werkraum` (also nicht in diesem
Git-Repo), sondern unter `/root/kompoase/`. Präzisierung 2026-09-19 (per `git rev-parse`
geprüft): `/root/kompoase/` ist **kein eigenes Repo**, sondern ein Unterordner des Git-Repos mit
Toplevel `/root/` (Branch `master`, gitdir `/root/.git`) — getrennt vom werkraum-Repo (Toplevel
`/root/werkraum`, gitdir `/root/werkraum_git`, Branch `main`). Code-Commits laufen also im
`/root`-Repo mit Pfadpräfix `kompoase/`, Doku-Commits im werkraum-Repo.
Nur die Logdatei landet unter `/root/werkraum/logs/kompoase.log` bzw.
`/root/werkraum/logs/splitter_daemon.log` (letzteres gehört zum separaten Produktions-Daemon,
siehe Abschnitt 5).

```
Systemd-Unit:  /etc/systemd/system/kompoase.service
Beschreibung:  KompOase Server (Port 8900)
ExecStart:     /usr/bin/python3 /root/kompoase/server.py
WorkingDir:    /root/kompoase
Nginx-Route:   flextrawurst.de/zusatz-kompoase/ (Basic-Auth, proxy_pass auf 127.0.0.1:8900)
```

Ursprung laut Systemdoku 40 (2026-07-29): `/root/kompoase/*.js` ist die **Standalone**-Fassung
von KompOase (Vanilla JS + Canvas 2D), parallel zur in `build_surface.ts` eingebetteten
Surface-Fassung — beide sprechen dieselben Datenquellen an (GENI-Proxy + Zwischenraum-DB), sind
aber zwei getrennte Implementierungen (bestehende Memory-Regel: Änderungen müssen auf beiden
Seiten nachgezogen werden, wenn sie beide betreffen).

Diese Testinstanz auf Port 8900 ist ausdrücklich ein **Übungs-/Reifungsraum**: Daniels eigene
Worte aus der Session (2026-09-18, 02:33 Uhr), *"meine idee ist es nun diese kompoase so zu
optimieren anzupassen und zu perfektionieren, dass wir das dann alles 1:1 übernehmen können für
die echte kompoase"* — was hier sauber funktioniert, soll später komplett in die produktive
KompOase wandern, nicht parallel neu erfunden werden.

## 3. Bauverlauf, chronologisch (Git-Log `/root/kompoase`, 2026-09-17 bis 2026-09-18)

**2026-09-17, tagsüber (15:05–16:58):** Reihe unabhängiger Fixes und Features, die den
Realmodus überhaupt erst nutzbar machten:
- `976106b4bc7` — Hänger behoben: `renderMaterialFelder()` (33 Zonen mit Radial-Gradients +
  ~450 Partikeln) wurde bisher bei jedem der 60 Frames/Sekunde komplett neu berechnet, obwohl
  sich die Materialitäts-Zonen nur langsam verändern. Fix: Auslagerung auf eine unsichtbare
  Zwischen-Canvas, die nur alle 90ms neu gezeichnet wird (`MAT_LAYER_INTERVALL_MS`), im
  Hauptbild nur noch per `drawImage` kopiert.
- `308441327cd` — Filter-Panel: AI-Ströme einzeln an/aus schaltbar, einzelne/verschmolzene
  Splitter trennbar filterbar.
- `fa8f0b27c86` — `_farbeFuerUnbekannteQuelle` gab ein ungültiges `hsl()`-Format zurück statt
  Hex, brach `render()` bei jedem Splitter mit unbekannter Quelle (Seite blieb blaustichig
  hängen).
- `7f77854efa6` — Server erzwingt jetzt `Cache-Control: no-cache, no-store, must-revalidate`
  bei jeder ausgelieferten Datei (Browser hatte während aktiver Live-Iteration wiederholt alte
  JS-Fassungen festgehalten).
- `b3ccb44b3c7` — Explosions-/Verschmelzungs-Partikel blinkten bisher unabhängig vom Filter
  weiter, auch wenn die zugehörige Kugel ausgeblendet war.

**2026-09-17, abends (19:08–21:32) — Crawl-Zugang:**
- `c90bca11b35` — Crawl-Zugangsschlüssel 1:1 nach `/toolbox`-Vorbild: ein zweiter,
  unabhängiger, rotierbarer Geheimschlüssel als `?key=...`-Parameter, den Nginx gegen eine
  Map-Datei prüft und bei Treffer die Basic-Auth für den Request abschaltet — Daniels
  eigener Login bleibt unverändert, der Schlüssel ist ein separater Weg nur für Crawler/Bots.
- `ad7e66a5532` — zweite Nginx-Map für Cookie-Bypass ergänzt, damit auch Unterressourcen
  (CSS/JS) ohne eigenen `?key=` durchkommen; Rotation hält seitdem beide Map-Vorkommen synchron.
- `cea2f122657` — Bug gefunden von Grok, von Daniel weitergegeben, von Claude bestätigt: alle
  sechs Datenaufrufe im Frontend nutzten absolute Pfade (`/api/...`), die seit der Verschiebung
  unter `/zusatz-kompoase/` (29.07.) ins Leere liefen (401 an der Domain-Wurzel). Mit relativen
  Pfaden lösen sie sich jetzt korrekt auf, egal ob direkt über Port 8900 oder über den
  öffentlichen Pfad. Vorher lief die öffentliche Seite faktisch komplett leer.

**2026-09-18, nachts (01:22–03:XX) — erster Absturz mittendrin:** Die Session brach zwischen
02:34 und 02:48 Uhr ab (siehe Systemdoku-Nachbarthema Musikvideo-Block-7, davon unabhängig).
Direkt vor dem Absturz stand Daniels Entscheidung, die Testinstanz zum 1:1-Übertragungsraum zu
machen (Zitat oben), und die offene Frage: Observability-Zähler zuerst, oder kontrollierte
Test-Splitter zuerst? Nach Wiederaufnahme (03:26–03:40 Uhr) blieb diese Frage zunächst
unbeantwortet liegen ("ich weiß nicht was du meinst").

**2026-09-18, morgens (07:47–09:36) — Observability-Teil:**
- `46f60dcbcb0` (werkraum-Repo) — Backup-Commit vor den folgenden Änderungen.
- `54fe35ddb0f` — **Quellen-Zähler im HUD.** `daten.js` bekommt ein `quellenStatus`-Objekt
  (`geni`, `db`), das bei jedem `fetchSplitter()`-Aufruf Anzahl, Zeitpunkt des letzten Erfolgs
  und ggf. Fehlermeldung pro Quelle festhält. `ui.js` formatiert das als zweite HUD-Zeile:
  `Quellen letzter Abruf — GENI: X (vor Ys) | DB: X (vor Ys)`, mit `⚠` bei Fehler. Ausdrücklich
  dokumentierte Grenze im Code selbst: zeigt nur, ob der **eigene Abruf** bei GENI/DB klappt —
  nicht ob der `splitter-physik.service`-Daemon selbst noch tickt.
- `2cd9daf540c` — **Echter Daemon-Heartbeat.** Statt den Daemon selbst zu ändern, liest
  `server.py` die letzte `Tick N:`-Zeile aus dessen bereits bestehendem Log
  (`/root/werkraum/logs/splitter_daemon.log`, Regex `TICK_ZEILE_MUSTER`) über einen neuen
  Endpunkt `GET /api/daemon-heartbeat` (liefert `tick_nr`, `letzter_tick`, `alter_sekunden`,
  oder HTTP 503 wenn keine Tick-Zeile gefunden wird). `daten.js` fragt das separat von
  GENI/DB ab (`holeDaemonHeartbeat()`, ausgelöst nach jedem `ladeNeueSplitter()`), `ui.js`
  zeigt es als dritten HUD-Wert: `Daemon: Tick N (vor Xs)`, mit `⚠ steht still?` wenn älter
  als 90s (1,5× der normale 60s-Takt). Das Alter zählt clientseitig zwischen den 30s-Polls
  weiter hoch, damit die Zahl nicht 30s lang "eingefroren" wirkt.
  **Wichtig:** kein Eingriff in den laufenden Produktions-Daemon nötig — er schrieb die
  Tick-Zeile schon immer, nur niemand hatte sie bisher ausgelesen.
- `092bb01a64` (werkraum-Repo, separat) — beim Warten auf den Heartbeat fiel auf: jede
  Tick-Zeile stand doppelt im Log. Ursache: `splitter_daemon.py` hatte sowohl einen
  `FileHandler` als auch einen `StreamHandler` registriert, und die systemd-Unit leitet
  `stdout`/`stderr` zusätzlich per `StandardOutput=append:.../StandardError=append:...` in
  **dieselbe** Logdatei um — jede Zeile kam also zweimal rein. Fix: `StreamHandler` entfernt,
  nur noch `FileHandler`. Live verifiziert (ein Tick-Zyklus abgewartet), `splitter-physik.service`
  musste dafür einmal neu gestartet werden, lief danach stabil weiter.

Damit ist der komplette Observability-Teil (GENI/DB-Zähler + echter Daemon-Heartbeat +
Log-Dedupe-Fix) fertig und live bestätigt (HUD zeigt alle drei Werte, Testdienst antwortet
mit HTTP 200).

## 4. Aktueller technischer Stand von `/root/kompoase/server.py`

Kurzer Überblick über die Endpunkte, wie sie jetzt existieren:

```
GET  /api/splitter?n=60          → proxy zu GENI (https://localhost:8020/api/splitter)
GET  /api/zwischenraum/...       → proxy zu welt-api (http://localhost:8030)
POST /api/zwischenraum/...       → proxy zu welt-api (POST)
GET  /crawl-key                  → aktueller Crawl-Zugangsschlüssel + fertige Crawl-URL
POST /rotate-key                 → Schlüssel-Rotation, geschützt durch eigenes Passwort
GET  /api/daemon-heartbeat       → letzte Tick-Zeile aus splitter_daemon.log, HTTP 503 wenn keine gefunden
```

Alle statischen Dateien (HTML/JS/CSS) werden mit erzwungenem `Cache-Control: no-cache`
ausgeliefert. GENI-Requests laufen über einen SSL-Kontext, der die selbst-signierten
GENI-Zertifikate akzeptiert (`ssl_ctx.verify_mode = ssl.CERT_NONE`).

## 5. Wichtige Abgrenzung: Testinstanz vs. Produktions-Daemon

Der eigentliche Physik-Takt (`splitter-physik.service`, alle 60s, drei Phasen) läuft **nicht**
in `/root/kompoase`, sondern als eigener Dienst aus `welt/splitter_daemon.py` (im
werkraum-Repo). Die Testinstanz auf Port 8900 liest von ihm nur passiv mit (Heartbeat aus dem
Log) — sie greift nicht in seinen Code oder seinen Takt ein. Das war ausdrücklich so gewollt:
kein Neustart des Produktionsdienstes nötig, außer für den einen Log-Dedupe-Fix, der den
Daemon selbst betraf (Abschnitt 3, letzter Punkt).

## 6. Offener Punkt bei Abbruch (10:06 Uhr)

Direkt vor dem zweiten Absturz des Tages lief keine weitere technische Arbeit an Port 8900 mehr
— Daniel hatte stattdessen um eine inhaltliche Recherche gebeten (siehe Abschnitt 7). Kein Code
war zu diesem Zeitpunkt unfertig oder halb angewendet.

---

## 7. Zwischenwesen — Konzeptdateien, vollständig gesichtet

Auf Daniels Bitte (09:45 Uhr, sinngemäß: KompOase-Weiterdenke zu Zwischenwesenfragmenten,
Splitterblasen-Fusion/-Abstoßung und einer Börse) wurde folgender Ordner gefunden und komplett
gelesen: **`/root/werkraum/_claude/ideen/zwischenwesen/`**, zehn Dateien, alle vom
19.–23. Juni 2026, mit vereinzelten Nachträgen vom 5. Juli 2026:

| Datei | Inhalt |
|---|---|
| `dak+claude-kompoasengespräch.md` | Das rohe Ursprungsgespräch (20.06.), Daniels Originalzitat im Wortlaut. Als `stub` markiert — ChatGPT-Dateien von Daniels Laptop sollten noch ergänzen, ist laut Daniel gerade in Rekonstruktion. |
| `konzept.md` | Grundidee: 24h-Prägungsgespräch mit einem "Flüchtling", dynamischer Cooldown (Ursprungswert 144s, später auf `max(30, aktive_zahl × 45)` präzisiert), Session-Abschluss bei ~75% Kontextauslastung mit LLM-generiertem "Geschichte-Kapitel" aus Wesen-Perspektive. |
| `felder.md` | Alle Erschaffungsfelder (Codexium-Parität: Name, Gesprächseinstieg, Was-bist-du, Neigungen/Abneigungen als Tags, Beschreibung, Wesendefinition 1337Z, Weltlore 1337Z, Farbe, Bild), komplettes Token-Budget durchgerechnet (~1215T System-Prompt voll, ~6322T Session-Ende-Worst-Case unter 8192T-Fenster). |
| `schlachtplan.md` | Der komplette Bauplan in 8 Phasen (0 Vorbereitung → 7 LangGraph/Embeddings), inkl. DB-Tabellen, API-Endpunkte, Frontend-Layouts (Tab FLÜCHTLINGE + FLÜCHTLINGSARCHIV), Lande-Zeremonie-Ablauf. Phase 0 und 0.5 als abgeschlossen markiert, Rest offen. |
| `kompoase_integration.md` | Die drei KompOase-Typen nach der Lande-Zeremonie: `zwischenwesenfragment` → (Ausbruch) → `zwischensplitterblase` → (Verbindung mit anderer Blase) → `splitterblase`. Pro/Contra-Energie-Physik, System-Analyse-Daemon mit Zuständen `läuft`/`loopt`/`ohnmächtig`, Ahnenverzeichnis. |
| `architektur.md` | Entschiedene Architekturfragen: keine eigene DB pro Zwischenwesen/Splitter (shared `flextrawurst`-DB), LangGraph bewusst erst ab Phase 4, vollständiges Tabellenschema inkl. `zwischenwesen_sessions` mit `geschichte_kapitel`. |
| `container.md` | Der Container: kuratierte, session-lokale Pins (max 10), live im LLM-Kontext, mit Filter/Suche. Nachtrag 05.07.: Text-Selektion per `mouseup` wurde bei Codexium2 verworfen (Touch-Selektion unzuverlässig), durch Checkbox-Modal ersetzt. |
| `memory_system.md` | Kategorisiertes Langzeitgedächtnis (6 Basiskategorien + max 5 eigene), Gewichtung 1–3, Kern-Memory lädt automatisch. Nachtrag 05.07.: `wesen_selbst`-Kategorie darf nur als **Vorschlag mit Begründung** funktionieren, nie als stiller Automatismus — Daniel hatte genau das bei Codexium2 einmal als Rückschritt korrigiert. |
| `wesen_dateistruktur.md` | Dateistruktur pro Wesen (`wesen.md`, `weltlore.md`, `handlung.md`, `mag-ich.md`, `mag-ich-nicht.md`, `nicht-tun.md`, `memory.md`, `container.md`, `chats/`), gilt für Solarius-, Codexium- und Flüchtlingswesen gemeinsam. Offene Kernfrage bis heute ungelöst: ob Inhalte roh/manuell oder per separatem KI-Analyse-Prompt in diese Dateien wandern. Enthält die wichtige Unterscheidung weiche Charaktergrenzen (Text im Prompt reicht) vs. absolute Grenzen (brauchen Server-Enforcement, gehören nicht in Text-Dateien). |
| `content_filter.md` | Zwei-Schichten-Moderation bei Erstellung: Schicht 1 regelbasiert (keine menschliche `wesen_typ`-Beschreibung), Schicht 2 LLM-Check (PASS/WARN/BLOCK, blockt nur echten Übergriff/Kindesmissbrauch/reale Personen). Obszönität, harte Sprache, Horror-Charaktere ausdrücklich erlaubt. |

**Was in keiner dieser zehn Dateien ausgearbeitet ist** (Fund der Recherche, Stand 09:49 Uhr):
die eigentliche **Verhandlung/Kommunikation** zwischen mehreren Zwischenwesenfragmenten (wie
einigen sich 2, 3, N Fragmente per generiertem Dialog auf eine gemeinsame Entscheidung) und die
**Börse** (Verschenken/Handeln/Tauschen/Wünschen, Partnerbörse für Fragmente) — beide stehen
bisher nur als Stichworte im rohen Ursprungsgespräch (`dak+claude-kompoasengespräch.md`), nicht
architektonisch ausgearbeitet. Ebenso nirgends weiter ausgeführt: der "KompOase-Dolphin" (eigene
LLM-Instanz als gemeinsames "Nervensystem" für alle Verhandlungen/Selbstgespräche/Handelsdialoge)
— nur in diesem einen Gesprächsprotokoll erwähnt.

Zwei im Delta-Werkzeug genannte, vermeintlich fehlende Dateien (`fluechtlingsarchiv.md`,
`lande_zeremonie.md`) lagen zum Zeitpunkt dieser Sichtung nicht (mehr) im Ordner — nicht weiter
nachverfolgt, da außerhalb des eigentlichen Auftrags.

Daniel lässt aktuell (Stand 10:16 Uhr) den ursprünglichen ChatGPT-ausführlichen Gesprächsverlauf
zu diesem Thema von seinem Laptop rekonstruieren — kommt separat nach, wird dann gegen die obige
Lückenbeschreibung abgeglichen, bevor an Verhandlung/Börse weitergedacht wird.
