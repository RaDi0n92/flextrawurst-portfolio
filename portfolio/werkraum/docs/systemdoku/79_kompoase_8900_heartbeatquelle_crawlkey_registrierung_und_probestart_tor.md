# Systemdokumentation 79: KompOase 8900 — Heartbeat-Quelle, Crawlkey-Registrierung und das Probestart-Tor

Datum: 2026-09-19
Betrifft: `kompoase.service`, `splitter-physik.service`, `flextrawurst-crawlkey-helper.service`,
Skill `kompoase-8900`

---

## 1. Anlass

Der Prüfer des Skills meldete zwei rote Tore:

```
K8900-VERIFY-002  FAIL   tick_nr 262, alter_sekunden 81787
K8900-VERIFY-007  FAIL   server_py_kennt_unit_pfad: false
```

Ein drittes Tor sagte gleichzeitig, dass alles in Ordnung sei:

```
K8900-VERIFY-006  PASS   tick_nr 1359, alter_sekunden 58.8
```

Derselbe Dämon, zwei Zahlen, 22,7 Stunden Abstand.

---

## 2. Fund 1 — das HUD sah eine Leiche

Der Dämon lief die ganze Zeit. Nur schrieb er woanders hin, als das HUD nachsah.

```
/root/werkraum/logs/splitter_daemon.log      Tick  262   ·  2026-09-18 13:57  ·  eingefroren
/var/log/flextrawurst/splitter-physik.log    Tick 1360   ·  2026-09-19 12:40  ·  lebendig
```

Der Grund steht in der Unit selbst:

```
ExecStart=… SPLITTER_LOG_PATH=/var/log/flextrawurst/splitter-physik.log …
```

Der Dämon **bekommt seinen Logpfad vom Dienst gesagt**. `server.py` hatte ihn dagegen fest
eingetippt, und zwar den Pfad von vor dem Umzug in die eigene Unit. Dieselbe Wahrheit stand an zwei
Orten; einer von beiden veraltete, ohne dass jemand es merkte.

Das HUD meldete deshalb seit dem 18.09. um 13:57 „steht still", während der Dämon ununterbrochen
weiterlief.

### 2.1 Was geändert wurde

Daniel hatte die Wahl zwischen dem Austausch der einen Zeile und einer Lösung, die aufhört zu
raten. Er entschied sich für die zweite.

`server.py` listet jetzt die bekannten Orte und nimmt den zuletzt beschriebenen:

```python
SPLITTER_LOG_KANDIDATEN = [
    "/var/log/flextrawurst/splitter-physik.log",   # splitter-physik.service, seit dem Umzug
    "/root/werkraum/logs/splitter_daemon.log",     # Ort davor, bleibt als Rückfallebene
]
```

Das HUD kann damit keinen toten Log mehr anzeigen, solange irgendwo ein lebender liegt. Und es
nennt seine Quelle in der eigenen Antwort, statt sie zu verschweigen:

```json
{"tick_nr": 1372, "alter_sekunden": 15.7,
 "quelle": "/var/log/flextrawurst/splitter-physik.log"}
```

Tor `K8900-VERIFY-007` prüft weiterhin mit, ob der Pfad aus der Unit überhaupt in der Liste steht.

---

## 3. Fund 2 — eine Mine, die seit einem Tag scharf lag

Der Neustart von `kompoase.service`, der für Fund 1 nötig war, brachte den Dienst nicht wieder
hoch. Er starb sofort:

```
ValueError: unbekannter Crawlkey-Store: /root/kompoase/.env_crawl_key
```

Das hatte mit der Änderung nichts zu tun.

**Was tatsächlich passiert war.** KompOase bekam seinen Crawl-Schlüssel am 2026-09-17, nach dem
Vorbild von `claudelive`, `codexlive` und `geminilive`. Am 2026-09-18 um 15:57 wurde die gesamte
Schlüsselverwaltung in einen isolierten Helfer mit Unix-Socket umgebaut. Sechs Systeme wurden dabei
übernommen:

```
claudelive · codexlive · geminilive · toolbox · crawlschluessel · archkey
```

KompOase nicht.

**Warum es trotzdem weiterlief.** Der Prozess von `kompoase.service` hatte seinen Code lange vor
dem Umbau geladen und hielt ihn im Speicher. Solange niemand neu startete, merkte niemand etwas.
Beim nächsten Start wäre er in jedem Fall gefallen — bei einem Reboot, einem Absturz, einem
Update. Der Neustart am 19.09. war nur der, der zufällig zuerst kam.

### 3.1 Was geändert wurde

Zwei Einträge, beide wortgleich nach dem Muster von `claudelive`. Kein neuer Mechanismus, kein
neuer Pfad. Schlüsseldatei und Nginx-Konfiguration lagen unverändert seit dem 17.09. an ihrem Ort
und wurden nicht angefasst.

```python
# welt/crawlkey_helper.py — KEY_STORES
"kompoase": {
    "kind": "nginx",
    "key_path":   Path("/root/kompoase/.env_crawl_key"),
    "nginx_path": Path("/etc/nginx/conf.d/kompoase-crawl-key.conf"),
},
```

```python
# .claude/live_crawlkey.py — _SYSTEM_BY_KEY_PATH
"/root/kompoase/.env_crawl_key": "kompoase",
```

Nach dem Neustart des Helfers geprüft, dass niemand sonst Schaden nahm:

```
claude-live    active
codex-live     active
gemini-live    active
kompoase       active
```

---

## 4. Fund 3 — der Prüfer hätte das nie gefunden

Das ist der eigentlich wichtige Teil.

Zehn Tore, alle grün, und darunter lag trotzdem ein Dienst, der einen Neustart nicht überlebt
hätte. Tor `K8900-VERIFY-001` fragt, ob Port 8900 antwortet. Es fragt nicht, ob das, was dort
antwortet, noch einmal starten könnte.

Ein Prozess kann lange mit Code laufen, den es so nicht mehr gibt. Hier lag die Mine von
2026-09-18 15:57 (Zeitstempel der umgebauten Fassade) bis 2026-09-19 12:42 (erster Neustart)
scharf — rund 21 Stunden. Der Bruch zeigt sich erst beim nächsten Start.

### 4.1 Tor `K8900-VERIFY-008`

Das neue Tor fährt einen **echten Probestart** mit genau dem Kommando, das in der Unit steht — ein
anderer Interpreter würde etwas anderes prüfen als das, was beim Neustart geschieht.

**Warum das gefahrlos ist.** Der Probestart läuft nur, wenn Port 8900 bereits belegt ist. Dann
scheitert sein eigenes Binden zwangsläufig mit `EADDRINUSE`, und er kann den laufenden Dienst nicht
verdrängen. Kommt er bis dorthin, ist alles davor in Ordnung: Importe, Schlüsselzugang,
Konfiguration.

Ist der Port frei, wird **nicht** gestartet. Das wäre kein Prüfen mehr, sondern ein Eingriff — das
Tor meldet dann `UNKNOWN` mit genau diesem Grund.

**Tracebacks werden gefiltert.** Gemeldet werden Fehlerart und Fundstelle, nie die auslösende
Quelltextzeile. `server.py` trägt in Zeile 68 ein voreingestelltes Rotationspasswort im Klartext;
ein ungefilterter Traceback würde es in die Evidenzdatei schreiben.

### 4.2 Gegenprobe

Ein Tor, das man nie hat fehlschlagen sehen, ist kein Tor. Die Mine aus Abschnitt 3 wurde deshalb
kurz wiederhergestellt — die `kompoase`-Zeile entfernt, der Prüfer gefahren, der Originalzustand in
einem `finally` zurückgeschrieben. Der laufende Dienst wurde dabei nicht angefasst.

```
K8900-VERIFY-001   PASS   {"http": 200}
K8900-VERIFY-008   FAIL   ValueError: unbekannter Crawlkey-Store: /root/kompoase/.env_crawl_key
                          File "/root/.claude/live_crawlkey.py", line 31, in __init__
```

Tor 001 meldete weiter grün. Genau dafür gibt es Tor 008.

Danach: Datei byteidentisch zurück, `kompoase.service` durchgehend `active`.

### 4.3 Zwei Tore, zwei Sichten

`K8900-VERIFY-008` kann nur die Host-Sicht beantworten — dort läuft der Dienst, dort ist der
Probestart gefahrlos. `K8900-SKILL-001` kann nur die Container-Sicht beantworten — nur dort
existiert der Skill-Ladepfad.

Ein einzelner Lauf ist deshalb nie ganz grün. Das ist eine Eigenschaft der Sicht, kein Mangel, und
der Prüfer sagt es jetzt selbst:

```
Aus dieser Sicht nicht beantwortbar: K8900-VERIFY-008 — vollständiger Beweis = ein Lauf je Sicht.
```

Nebenbei fiel dabei auf, dass die Tabellenausgabe Detailschlüssel über eine Positivliste filtert.
Die Zeile von Tor 008 blieb leer, obwohl die Evidenzdatei alles trug. Ergänzt.

---

## 5. Stand nach der Arbeit

| Sicht | Ergebnis |
|---|---|
| Host | 10 × PASS, `SKILL-001` nicht beantwortbar |
| Container | 10 × PASS, `VERIFY-008` nicht beantwortbar |

Kein einziges FAIL in beiden Läufen zusammen.

| Commit | Repo | Inhalt |
|---|---|---|
| `fa639545f00` | `/root` | Heartbeat-Kandidaten, Fassaden-Eintrag |
| `01b004268a` | werkraum | `kompoase` im Crawlkey-Helfer |
| `ebc8a34bf2` | werkraum | Tor 008, Tabellenausgabe, Sicht-Fußzeile, SKILL.md |

---

## 6. Was offen bleibt

- **Das voreingestellte Rotationspasswort in `server.py` Zeile 68 steht im Klartext im Quelltext.**
  Es ist nur der Rückfallwert, wenn die Umgebungsvariable fehlt — aber es steht in einem Repo.
  Nicht angefasst, keine Entscheidung dazu getroffen. [status: offen]

- **Ob weitere Systeme beim Umbau vom 2026-09-18 übersehen wurden**, ist in Abschnitt 8 nachgeholt.
  [status: bestätigt 2026-09-19 -- beim Crawl-Schlüssel war KompOase der einzige; die breitere
  Suche fand dafür cyberling-daemon.service, siehe 8.3]

- **Tor 008 prüft nur `kompoase.service`.** Der Gedanke dahinter — ein antwortender Port beweist
  keinen gelingenden Neustart — gilt für jeden Dienst auf dieser Maschine. [status: offen]

---

## 7. Herkunft — wer KompOase eingehängt hat

Damit der Nächste weiß, wo der Faden anfängt.

Der Crawl-Zugang von KompOase entstand am **2026-09-17 um 18:59** auf Daniels Ansage an diesen
Strom (Claude Code, `/config`-Instanz), wörtlich aus dem Chatprotokoll:

> *„ne schau dur mal /toolbox genau an und kopiere den crawlzugang und die keyrotation 1zu1 nix
> anders machen genau so absichern"*

Umgesetzt wurde das als direkter Nachbau des Musters von `/toolbox` — mit einer eigenen
Schlüsseldatei, einer eigenen Nginx-Konfiguration und einem Aufruf in die damals gemeinsame
`live_crawlkey.py`.

Der Umbau vom **2026-09-18** stammt von einem anderen Strom: die Berichtsdatei des Commits liegt
unter `_codex/berichte/2026-09-18-welt-api-isolation-inventar.md`, die Commit-Nachrichten sind
englisch und tragen keine `Co-Authored-By`-Zeile. Im Sitzungsprotokoll dieses Stroms findet sich
zu `crawlkey_helper` kein einziger Treffer.

**Die eigentliche Lücke lag aber vor dem Umbau.** Wer sich in einen gemeinsamen Mechanismus
einhängt, muss damit rechnen, dass dieser sich bewegt. KompOase hinterließ dort nichts, was
aufgefallen wäre: keinen Eintrag in einer Liste, die jemand beim Aufräumen sieht, und keine
Prüfung, die anschlägt, wenn der Boden verschwindet. Sechs Systeme standen beim Umbau auf der
Liste; KompOase stand auf keiner.

Tor `K8900-VERIFY-008` ist genau das, was am 17.09. hätte hinterlassen werden müssen.

---

## 8. Der Abgleich danach — war KompOase der einzige Fall?

Offener Punkt 2 aus Abschnitt 6, nachgeholt am 2026-09-19. Rein lesend, kein Dienst angefasst,
kein Schlüsselwert ausgegeben.

### 8.1 Crawl-Schlüssel: vollständig

Alle Stellen, die `CrawlKey(...)` bauen, gegen die Liste des Helfers gehalten:

| Nutzer | System | Stand |
|---|---|---|
| `.claude/claude_live.py` | `claudelive` | angemeldet |
| `.claude/codex_live.py` | `codexlive` | angemeldet |
| `.claude/gemini_live.py` | `geminilive` | angemeldet |
| `kompoase/server.py` | `kompoase` | angemeldet (seit heute) |
| `welt/api.py` | `archkey`, `toolbox`, `claudelive`, `codexlive`, `geminilive` | angemeldet |
| `welt/tts_service.py` | `toolbox` | angemeldet |

`api.py` und `tts_service.py` benutzen bereits die neue Anmeldung direkt über Systemnamen, nicht
mehr über die Fassade.

Die Nginx-Konfiguration `tts-crawl-key.conf` sah zunächst verwaist aus; sie gehört zum Eintrag
`toolbox`, dessen Name nicht zum Dateinamen passt. Kein Befund.

**KompOase war der einzige.**

### 8.2 Dieselbe Minenart, breiter gesucht

Die Frage dahinter ist allgemeiner als der Crawl-Schlüssel: **welche laufenden Dienste haben ihren
Code geladen, bevor dieser Code zuletzt geändert wurde?** Ein solcher Prozess lebt aus dem
Speicher; der Bruch zeigt sich erst beim nächsten Start.

Alle 103 laufenden Dienste geprüft. Einer fiel auf — und er hängt am selben Tag:

```
2026-09-18 15:04   security: remove Welt API DB credential fallbacks
2026-09-18 15:44   security: isolate crawlkey rotation helper
```

Seit 15:04 fällt `welt/db_runtime.py` ohne `FLEXTRAWURST_DB_URI` auf einen absichtlich
unbrauchbaren Platzhalter zurück — richtig so, der frühere Rückfallwert war ein Zugangsdatum im
Klartext.

| Dienst | gestartet | Variable | Befund |
|---|---|---|---|
| `welt-api.service` | 18.09. 16:01 | gesetzt | in Ordnung |
| `splitter-physik.service` | — | gesetzt | in Ordnung |
| `codewesen-chat.service` | 17.09. 01:08 | nicht gesetzt | **kein Befund** — liest seinen Zugang aus `/root/werkraum/.agent/flextrawurst-db.env`, braucht die Variable nicht |
| `cyberling-daemon.service` | 17.09. 02:30 | nicht gesetzt | **Mine** |

### 8.3 `cyberling-daemon.service`

Belegt, nicht gefolgert:

```
welt/cyberling_daemon.py:42    from db_runtime import DB_URI
welt/cyberling_daemon.py:119   psycopg2.connect(DB_URI, …)

ohne Variable ergibt das:      dbname=__flextrawurst_db_uri_required__
```

Die Unit setzt die Variable nicht. Der Dienst läuft seit dem 17.09. um 02:30, einen Tag vor der
Änderung — **er lebt aus dem Speicher.** Beim nächsten Neustart fände er die Datenbank nicht.

**Warum das kein Einzeiler ist.** Der frühere Zugang war
`postgresql://dak:<passwort>@localhost:5432/flextrawurst` — TCP mit Passwort, Rolle `dak`. Genau
den hat der Sicherheits-Durchgang entfernt, und er darf nicht zurück.

Das Muster, das der Umbau stattdessen eingeführt hat, sieht so aus:

| Dienst | Systembenutzer | DB-Rolle | Verbindung |
|---|---|---|---|
| `welt-api` | `flex_api` | `flex_api` | Unix-Socket, peer |
| `splitter-physik` | `flex_splitter` | `flex_splitter` | Unix-Socket, peer |
| `cyberling-daemon` | **`root`** | — | — |

`pg_hba.conf` hat `local all all peer` und keine `pg_ident`-Zuordnung. Peer bedeutet: der
Systembenutzer **muss** der DB-Rolle entsprechen. Ein als `root` laufender Dienst kann sich damit
über den Socket als gar keine dieser Rollen anmelden.

Cyberling in dieses Muster zu bringen heißt deshalb: eigener Systembenutzer, eigene DB-Rolle,
Rechte auf `cyberlinge`, `entity_profiles`, `entity_slots`, `events` — und damit auch Fragen nach
Dateieigentum und Arbeitsverzeichnis. Das ist eine Berechtigungsentscheidung, keine Unit-Zeile.

[status: bestätigt 2026-09-19 -- von Daniel beauftragt und umgesetzt, siehe Abschnitt 9] Der
Dienst hat seitdem eine eigene Rolle und einen Neustart hinter sich.

Die Eigentümer der betroffenen Tabellen zur Einordnung: `cyberlinge`, `events`, `entity_slots`
gehören `dak`, `entity_profiles` gehört `postgres`.

---

## 9. `cyberling-daemon` bekommt eine eigene Rolle

Der offene Punkt aus 8.3, erledigt am 2026-09-19.

### 9.1 Warum es keine Unit-Zeile war

Der frühere Zugang stand als Rückfallwert im Quelltext:

```python
DB_URI = os.environ.get("FLEXTRAWURST_DB_URI", "postgresql://dak:<passwort>@localhost:5432/…")
```

TCP mit Passwort, Rolle `dak`. Genau das hat der Sicherheits-Durchgang am 2026-09-18 entfernt, und
es darf nicht zurück. Die Variable einfach neu zu setzen hätte bedeutet, dasselbe Zugangsdatum an
einen anderen Ort zu schreiben.

`pg_hba.conf` hat `local all all peer` und keine `pg_ident`-Zuordnung. Peer heißt: der
Systembenutzer **muss** der Datenbankrolle entsprechen. Ein als `root` laufender Dienst kann sich
über den Socket als gar keine der bestehenden Rollen anmelden. Es blieb also nur der Weg, den der
Umbau für die anderen Dienste gegangen war.

### 9.2 Was angelegt wurde

```
Systembenutzer  flex_cyberling   uid 994, kein Home, kein Login
Datenbankrolle  flex_cyberling   LOGIN, kein Passwort
```

Die Rechte sind aus dem Quelltext abgelesen, nicht großzügig geschätzt:

| Recht | Tabelle | Fundstelle |
|---|---|---|
| `SELECT` | `cyberlinge`, `entity_slots` | Tick-Schleife |
| `SELECT` | `entity_profiles` | `JOIN` in Zeile 289 und 311 |
| `UPDATE` | `cyberlinge` | Bedürfnisse, Tod, Wiedergeburt, `letzter_tick` |
| `INSERT` | `events` | `cyberling.gestorben`, `cyberling.erwacht` |

`events.event_id` ist `uuid` mit `gen_random_uuid()` — es wird keine Sequenz gebraucht.

Die Unit:

```
User=flex_cyberling
Environment=FLEXTRAWURST_DB_URI=dbname=flextrawurst user=flex_cyberling host=/var/run/postgresql
```

Damit steht Cyberling im selben Muster wie `welt-api` (`flex_api`) und `splitter-physik`
(`flex_splitter`): eigener Benutzer, eigene Rolle, Socket, kein Passwort.

### 9.3 Nachgeprüft, nicht behauptet

**Vor** dem Umstellen der Unit — sonst wäre der Neustart ein Sprung ins Dunkle gewesen:

```
Interpreter startbar als flex_cyberling   python 3.12.3
Arbeitsverzeichnis lesbar                 ja
cyberling_daemon.py lesbar                ja
db_runtime, psycopg2 importierbar         ja
Anmeldung über den Socket                 verbunden als flex_cyberling
```

Die vier Operationen des Daemons wurden real ausgeführt, in einer Transaktion, die
zurückgerollt wurde — danach standen null Prüf-Events in der Tabelle.

Und die Gegenrichtung, direkt aus dem Rechtekatalog statt durch Ausprobieren:

```
25 geprüfte Kombinationen aus 5 Tabellen × 5 Rechten
 4 × JA   ·  21 × nein
```

`events` trägt `INSERT`, aber kein `SELECT` — was zu Grundgesetz 5 passt, die Tabelle ist
append-only. Auf `splitter` hat die Rolle überhaupt keine Rechte.

### 9.4 Der Neustart

```
vorher    17.09. 02:30, User=root, lebte aus dem Speicher
nachher   19.09. 15:05, User=flex_cyberling, active, 0 Fehler
```

Der Hauptprozess läuft als `flex_cyberling`, der Daemon hat sich verbunden und seine Startzeile
geschrieben. Takt: alle 300 Sekunden.

### 9.5 Stand des Durchgangs

```
3 in Ordnung · 0 auffällig · 101 ohne DB-Bezug übersprungen
```

`codewesen-chat.service` war ein Fehlalarm des ersten Laufs — es liest seinen Zugang aus
`/root/werkraum/.agent/flextrawurst-db.env` und braucht die Umgebungsvariable nicht. Der Prüfer
erkennt diesen Weg jetzt und meldet ihn nicht mehr als Befund.

Das Werkzeug liegt dauerhaft unter
`_claude/tools/pruefe_dienste_ueberleben_neustart.py`. Es ist die allgemeine Form von Tor
`K8900-VERIFY-008`: nicht „antwortet der Dienst", sondern **„würde er nochmal starten"**.
