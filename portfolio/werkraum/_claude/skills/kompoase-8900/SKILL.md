---
name: kompoase-8900
description: Betriebs- und Konzept-Harness für die KompOase-Testinstanz (Port 8900, /zusatz-kompoase/) und die Splitter-Kosmologie aus Systemdoku 69–75 — fraktale Splitter, permanente Herkunft, Tragen/Halten, Anteile/Exit, Vielstimmigkeits-Ledger, Ledger-vs-Erzählung, Abwägungsfragen, Visionen, Wetterzellen, Phantom-Watcher. Laden bei jeder Arbeit an KompOase, Splittern, Blasen, Börse/Handel, splitter-physik, Heartbeat oder den Dokus 69–75, bevor etwas vorgeschlagen, gebaut oder dokumentiert wird. Liefert 15 Gesetze, einen Modus-DAG, 11 Beweis-Tore (verify_8900.py), den 14-Knoten-Bogen-Harness (kompoase_harness.py) mit Impuls-, Linter- und Permit-Toren, und die Freigabe-Checkliste.
---

# KompOase 8900 — Splitter-Kosmologie & Betriebs-Harness

Dieser Skill steuert jede Arbeit an der **KompOase-Testinstanz (Port 8900)** und an der daraus
entstandenen **Splitter-Kosmologie** ([`docs/systemdoku/69`–`75`](file:///root/werkraum/docs/systemdoku/)).
Er ist die quellengebundene Verdichtung dieser Dokus: Gesetze, Modell, Tore, Beweise. Was hier
nicht steht, gilt nicht als entschieden. Alle Ist-Aussagen sind mit `scripts/verify_8900.py`
belegbar, nicht aus dem Gedächtnis.

Geltung: KompOase (Testinstanz und produktive Surface-Fassung), Splitter/Splitterfragment/
Splitterblase, Anteile/Blase/Exit, Börse/Handel/Tausch, Gefühlsgewebe/Vielstimmigkeits-Ledger,
Ledger-vs-Erzählung, Abwägungsfragen/Abstimmung/Chronik, Visionen, Krankheit-Ästhetik,
Flohmarkt-Ruck, Wetterzellen, primärer/sekundärer Ruf, Selbstportrait, Phantom-Watcher,
`splitter-physik.service`, `/api/daemon-heartbeat`, `/root/kompoase/*`, Einträge
`KompOase-8900(zusatz)` in den Wissensprotokollen.
Nicht in Geltung: Zwischenwesen/Flüchtlinge/24h-Wesen (Gesetz 7), Musikvideo-Produktion,
Augen-und-Hände-Bridge (Systemdoku 76).

---

## 1. Die 15 Gesetze

1. **Kein Schwellenwert-Leben.** Weder Entstehung, Abspaltung, Passung noch Wert werden durch
   eine Formel, einen Score, einen Embedding-Grenzwert oder `if x > 0.8` entschieden. Sie
   entstehen aus dem tatsächlichen, rekonstruierbaren Verlauf. (71, 72 §5, 73 §3)
2. **Keine Zentralinstanz für Wert.** Kein Preis, kein Rating, kein Kurator, kein Admin-Urteil.
   Wert ist die Summe vieler einzelner, freiwilliger, nicht abgestimmter Reaktionen. (73 §3/§8)
3. **Ledger ≠ Erzählung.** Zahl/Fakt/Ereignis (Ledger, 60-s-Takt, ohne LLM) und Chronik/
   Selbstportrait/Vision (Erzählung, selten, danach) sind zwei Kanäle. Jede Erzählung verweist
   auf ihre Ledger-Zeile und ist daran prüfbar. Sichtbar machen, welche Schicht spricht. (70, 74 §4)
4. **Keine erfundenen Dialoge.** Entscheidungen in Splittern laufen ohne generierten Wortwechsel;
   die Chronik entsteht nach dem Ergebnis, ohne erfundene Zitate. (74 §1/§4)
5. **Keine Eltern-Kind-Sprache.** Bestandteil, Verbund, Bündnis, Gruppe — sozial, nicht
   biologisch. (72 §3)
6. **Keine Spalte gilt als passend.** `energie`, `verbindungen`, `abstossungen`,
   `letzter_kontakt`, `herkunft_sichtbar`, `origin_type`/`origin_id`/`human_id` sind Kandidaten
   für das fraktale Modell, jede einzeln zu prüfen, keine bestätigt. Eine Trage-Relation
   (Mensch/Entität → Splitter) existiert im Schema nicht; `splitter_verbindungen` ist
   Splitter → Splitter. (72 §8)
7. **Flüchtlinge sind außerhalb.** Zwischenwesen/24h-Wesen/Lande-Zeremonie sind kein Baupfad
   dieses Strangs (zeitlich fern, Ein-LLM-Grenze). `_claude/ideen/zwischenwesen/` liefert nur
   Begriffe (`zwischenwesenfragment` → `zwischensplitterblase` → `splitterblase`, Pro/Contra).
   (69 §7)
8. **Ein-LLM-Kontention.** Alle Ströme und Wesen teilen `hauhaucs-q6`. Jede Idee, die pro
   Splitter, Tick oder Ereignis einen LLM-Aufruf auslöst, ist per se verdächtig.
   Vielstimmigkeit entsteht aus ohnehin laufender Aktivität, nicht aus neuen Aufrufen. (73 §4)
9. **Konzept ist kein Bauauftrag.** Dokus 72–75 sind im Frontmatter als Konzept ohne
   Bauauftrag markiert (73: „angenommen“, trotzdem kein Bauauftrag). Bauen und
   Schritt-Zerlegung ("kleinster erster Schritt") nur nach ausdrücklichem Bauauftrag; in der
   Konzeptphase bleibt die Zerlegung aus. Nach Absturz/Pause: Richtung erfragen, nicht ableiten.
10. **410-Schreibpfade bleiben zu.** `POST /zwischenraum/splitter/entstehung` und
    `…/verschmelzung` antworten seit 12.08. mit 410, weil 16.912 dekorative Canvas-Events die
    kanonische `events`-Historie verunreinigt hatten. Öffnung nur durch Daniels Entscheidung.
    (40, 70)
11. **Grundgesetze gelten weiter.** Events append-only (GG 5), Live über NOTIFY/LISTEN → SSE
    (GG 8), jedes Fragment eigene Mini-Existenz (GG 1), `meta JSONB` (GG 2). Neue Event-Typen
    reihen sich dort ein; Namen wie `zwischenwesen.*`, `splitterblase.*`, `boerse.*` sind
    Beispiele, nicht festgelegt. (70)
12. **Ein-Klick-Zugang.** Jeder sieht jederzeit alle "seine" Splitter vollständig, erforschbar,
    beobachtbar. Keine versteckte Sammlung. (75 §6)
13. **Zwei Repos, zwei Backups.** Dokus → `/root/werkraum` (`main`). Code → Toplevel `/root`
    (`master`), Pfad `kompoase/`. Vor jeder Änderung `git add -A && git commit -m "backup: vor …"`
    im betroffenen Repo.
14. **Externe Bildwerkzeuge** nur nicht-kommerziell, bewusst einzeln ausgelöst, nie als
    Pipeline. (74 §5)
15. **Kein Dienst-Neustart ohne Freigabe.** `splitter-physik`, `welt-api`, `geni-web`,
    `kompoase.service` werden nicht neu gestartet, ohne dass Daniel es freigibt. Der
    Produktions-Daemon wird nur gelesen, nie verändert.

---

## 2. Ist-Zustand der Testinstanz (Stand 2026-09-19, per Skript belegt)

### 2.1 Ort und Dienst

| Was | Wert |
|---|---|
| Code | `/root/kompoase/` — Unterordner des Repos mit Toplevel `/root` (`master`, gitdir `/root/.git`); **kein** eigenes Repo; getrennt vom werkraum-Repo (`/root/werkraum`, gitdir `/root/werkraum_git`, `main`) |
| Unit | `/etc/systemd/system/kompoase.service` · `ExecStart=/usr/bin/python3 /root/kompoase/server.py` · `WorkingDirectory=/root/kompoase` · `Restart=always` · `After=welt-api.service` · Log `/root/werkraum/logs/kompoase.log` (Symlink `logs → /root/werkraum_logs`) |
| Bindung | `127.0.0.1:8900`, `ThreadingHTTPServer` |
| Öffentlich | `flextrawurst.de/zusatz-kompoase/` → Nginx `proxy_pass http://127.0.0.1:8900/`, Basic-Auth "Werkraum", Crawl-Key-Bypass (Map `kompoase_key_ok_arg` in `/etc/nginx/conf.d/kompoase-crawl-key.conf`, Parameter **und** Cookie), Schlüssel in `/root/kompoase/.env_crawl_key`, Rotation `POST /rotate-key` (Passwort aus `KOMPOASE_CRAWL_ROTATE_PASSWORD`; nie in Dokus kopieren) |
| Frontend | Vanilla JS + Canvas 2D: `kompoase.js` (Loop), `daten.js` (Abruf, `quellenStatus`), `ui.js` (HUD/Klick/Aufnehmen), `physik.js`, `splitter.js`, `filter.js`, `crawlkey.js`, `materialitaeten.js`, `weltrueckfluss.js`, `beobachtung.js`, `geni_beobachter.js`, `entitaet_geburt.js`, `splitter_bewusstsein.js`, `index.html`, `style.css` |
| Zweite Fassung | Surface-KompOase in `build_surface.ts` (Port 8787), gleicher Datenweg, getrennter Code — Änderungen, die beide betreffen, auf beiden Seiten nachziehen (40, 69 §2) |
| Zweck | Übungs-/Reifungsraum; was hier sauber läuft, geht 1:1 in die produktive KompOase (69 §2) |

### 2.2 Endpunkte `server.py`

```
GET  /api/splitter?n=60        → GENI  https://localhost:8020/api/splitter (self-signed, CERT_NONE)
GET  /api/zwischenraum/...     → welt-api http://localhost:8030
POST /api/zwischenraum/...     → welt-api (POST)
GET  /crawl-key                → Schlüssel + Crawl-URL
POST /rotate-key               → Rotation, synchronisiert beide Nginx-Maps
GET  /api/daemon-heartbeat     → letzte "YYYY-MM-DD HH:MM:SS Tick N:"-Zeile aus SPLITTER_DAEMON_LOG
                                 → {tick_nr, letzter_tick, alter_sekunden}; 503 ohne Tick-Zeile
```
Statische Dateien mit `Cache-Control: no-cache, no-store, must-revalidate`. Frontend nutzt
**relative** API-Pfade (absolute liefen unter `/zusatz-kompoase/` ins Leere). Theater-Modus ist
entfernt; `"theater_modus": True` in einer Antwort ist eine tote Zeile. (69 §3/§4)

### 2.3 Datenfluss und HUD

- Poll alle 30 s (`DATEN_POLL_INTERVALL`): GENI + DB zusammengeworfen, dann
  `filterAktualisiereQuellen()` und `holeDaemonHeartbeat()`.
- HUD unten links: `tick N | X aktiv | Y geisterreste` und
  `Quellen letzter Abruf — GENI: X (vor Ys) | DB: X (vor Ys) | Daemon: Tick N (vor Zs)`;
  `⚠` bei Quellfehler, `⚠ steht still?` bei Daemon-Alter > 90 s; Alter zählt clientseitig weiter.
- `geniBeobachter.analysiere(splitter)` bei `tick % 300 === 0` (≈ 5 s bei 60 fps, framebasiert)
  — der Haken für einen späteren Reaktions-/Prüf-Tick (70, 73).

### 2.4 Produktions-Daemon — nur lesen

`splitter-physik.service` = `/root/werkraum/welt/splitter_daemon.py`, 60-s-Takt, drei Phasen.
Seit 2026-09-18 14:01 isoliert (`DynamicUser=yes` → `flex_splitter`, `ProtectHome=read-only`,
DB-Rolle `flex_splitter` über Peer-Auth, Unit-Quelle
`_codex/tools/systemd/splitter-physik-isolated.service`). **Log jetzt
`/var/log/flextrawurst/splitter-physik.log`** (`SPLITTER_LOG_PATH`, `LogsDirectory=flextrawurst`,
`StandardOutput=journal`). Der alte Pfad `/root/werkraum/logs/splitter_daemon.log` wird seit
der Isolation nicht mehr beschrieben.

Ob `server.py` denselben Pfad liest, den die Unit schreibt, sagt **Tor `K8900-VERIFY-007`** —
nicht dieser Text. Steht es auf FAIL, zeigt das HUD ein falsches „steht still?“; der Fix ist
`SPLITTER_DAEMON_LOG` in `server.py` auf den Unit-Pfad zu setzen (oder den jüngsten
existierenden Kandidaten zu lesen) und `kompoase.service` neu zu starten — Gesetz 15,
braucht Freigabe.

### 2.5 Quellenlage (Stichprobe, kein Zensus)

Ein Feed-Objekt trägt `id`, `herkunft` (`resonanz` | `mensch` | …), `quelle_id`,
`quelle_sichtbar`, `inhalt_kurz`, `inhalt_voll`, `thema_vektor`, `energie`, `materialitaet`,
`groesse`, `position`, `velocity`. `api/splitter?n=200` liefert `quelle_id`-Werte `claude`,
`codex`, `gemini`, `chatgpt`, `claudeweb` (alle fünf Strom-Quellen aus Doku 40 tragen Zeilen),
dazu `namelessAI_*` (Wesen) und — in der Stichprobe vom 2026-09-19 — ~30 % **`quelle_verborgen`** — das sind keine ungetaggten
Zeilen, sondern Einträge mit `quelle_sichtbar: false` (überwiegend `herkunft: mensch`): das
`herkunft_sichtbar`-Prinzip des Schemas, live im Feed. GLM/Kimi erscheinen nicht. Vor jeder
Aussage neu ziehen (`K8900-VERIFY-003`).

---

## 3. Wann was Pflicht ist

| Situation | Pflicht |
|---|---|
| Irgendeine Ist-Aussage über 8900 (läuft, zeigt, Anzahl, Quelle) | `verify_8900.py` in dieser Session (§4) |
| Vorschlag, der in eine Systemdoku oder ein Wissensprotokoll münden soll | kompletter Bogen im Harness, Modus `KONZEPT` (§4b) |
| Jede Änderung an Code, Unit, Nginx, Schema | kompletter Bogen im Harness, Modus `BAU` mit wörtlichem Auftrag (§4b) |
| Kurze Rückfrage, Lesen, Recherche ohne Ergebnisdatei | kein Bogen; Gesetze §1 gelten trotzdem |

Modus `KONZEPT` ist Standard. `BAU` gibt es nur nach ausdrücklichem Bauauftrag (Gesetz 9).

---

## 4. Die 11 Beweis-Tore (`scripts/verify_8900.py`)

| Tor | PASS nur wenn |
|---|---|
| `K8900-VERIFY-001` | `GET /` antwortet 200 |
| `K8900-VERIFY-002` | `GET /api/daemon-heartbeat` 200 und `alter_sekunden ≤ 90` |
| `K8900-VERIFY-003` | Stichprobe gezogen; `n`, Verteilung `quelle_id`, Herkunft, Anteil `quelle_verborgen` protokolliert |
| `K8900-VERIFY-004` | letzter Commit mit Pfad `kompoase/` im Repo-Toplevel ermittelt (Hash, Datum, Branch) |
| `K8900-VERIFY-005` | `CREATE TABLE IF NOT EXISTS splitter` in `welt/schema_welt.sql` gelesen, Spalten gelistet |
| `K8900-VERIFY-006` | jüngstes existierendes Daemon-Log (nach mtime) hat eine Tick-Zeile und ist ≤ 90 s alt |
| `K8900-VERIFY-007` | `server.py` kennt den Logpfad der Daemon-Unit (`SPLITTER_LOG_PATH`) — als Konstante, Kandidat oder Env |
| `K8900-VERIFY-008` | Probestart mit dem Kommando der Unit kommt bis zum Binden und scheitert dort am belegten Port — nur aus Host-Sicht, und nur bei belegtem Port, sonst wäre er ein Eingriff |
| `K8900-DOC-001` | Dokus 69–75 **plus jede weitere mit `KompOase 8900` im Titel** vorhanden, Nummern eindeutig, jeder Titel trägt den Tag |
| `K8900-DOC-002` | `flextrawurst.md` und `ai-ströme.md` enthalten `KompOase-8900(zusatz)` |
| `K8900-SKILL-001` | Skill-Ladepfad `/config/.agents/skills/kompoase-8900` und werkraum-Spiegel byteidentisch |

Exit-Codes: `0` alle PASS · `1` mindestens ein FAIL · `3` kein FAIL, aber UNKNOWN. `UNKNOWN`
ist ein Ergebnis, kein Freibrief — es wird nie als PASS berichtet.

**Zwei Tore kann je nur eine Sicht beantworten:** `K8900-VERIFY-008` braucht den Host (dort läuft
der Dienst, dort ist der Probestart gefahrlos), `K8900-SKILL-001` den Container (nur dort existiert
der Ladepfad). Ein einzelner Lauf ist deshalb nie ganz grün — das ist eine Eigenschaft der Sicht,
kein Mangel. Der vollständige Beweis sind **beide Läufe**; das Skript nennt in seiner Fußzeile,
welches Tor es gerade nicht beantworten kann.

**Warum es Tor 008 gibt:** ein antwortender Port beweist nicht, dass ein Neustart gelingt. Ein
Prozess kann mit Code laufen, den es so nicht mehr gibt — der Bruch zeigt sich erst beim nächsten
Start, bei einem Reboot, einem Absturz, einem Update. Am 2026-09-19 lag genau so ein Fall vor
(Systemdoku 79). Das Skript liest nur
(Standardbibliothek), mutiert nichts und läuft aus Container-Sicht (`/vps_root`, `/vps_system`)
und Host-Sicht (`/root`, `/etc`, `/var/log`) gleich.

```bash
python3 /config/.agents/skills/kompoase-8900/scripts/verify_8900.py            # Tabelle + Evidenz-Datei
python3 /config/.agents/skills/kompoase-8900/scripts/verify_8900.py --json     # vollständiger Datensatz
python3 /config/.agents/skills/kompoase-8900/scripts/verify_8900.py --no-write # nur prüfen
python3 /config/.agents/skills/kompoase-8900/scripts/verify_8900.py --sample 500
```

---

## 4b. Der Bogen-Harness (`scripts/kompoase_harness.py`)

Ein **Bogen** ist ein zusammenhängendes Stück Arbeit — Konzept oder Bau. Der Harness ist die
kreativleitende, prüfende State-Machine dafür: er nimmt Verifikation und Beweisführung ab,
zieht echtes Material als Impuls und lässt keinen Knoten überspringen. Zustand liegt in
`<workspace>/harness_<session>_state.json` (Standard-Workspace
`/root/werkraum/_claude/berichte/kompoase-8900/`, Session = Datum), der Abschluss schreibt
`<stamp>_harness_<session>.md`.

```text
[01_INIT] ─► [02_SKILL_READ] ─► [03_DOKUS_READ] ─► [04_VERIFY] ─► [05_MODE_LOCK] ─► [06_IMPULS] ─► [07_ENTWURF] ─► [08_FREIGABE]
                                                                                                                       │
                                        KONZEPT ───────────────────────────────────────────────────────────────────────┤
                                        BAU ─► [09_BACKUP] ─► [10_MUTATION] ─► [11_EVIDENZ_NACHHER] ──────────────────┤
                                                                                                                       ▼
                                                                                        [12_DOKU] ─► [13_COMMIT] ─► [14_ABSCHLUSS · HALT]
```

| Knoten | Kommando | Prüft / liefert |
|---|---|---|
| 02 | `read-skill` | SKILL.md vorhanden, Hash festgehalten |
| 03 | `read-dokus --bestaetigt` | Dokus 69–75 plus alle weiteren mit Strang-Tag vorhanden, Nummern eindeutig, Hashes; Lesebestätigung ist Pflicht (Attestierung) |
| 04 | `verify` | führt `verify_8900.py` aus, verlinkt Evidenz, merkt Fails/Unknowns |
| 05 | `lock-mode KONZEPT` / `lock-mode BAU --auftrag "…"` | BAU nur mit wörtlichem Auftrag → `BAU_PERMIT` |
| 06 | `impuls [--n 3] [--seed N]` | **kreativ, nichts erfunden:** N echte Splitter (Quelle/Herkunft/Inhalt/Materialität/Energie), aktuelle Quellenverteilung, eine „Begegnung“ zweier Splitter verschiedener Quellen, eine Frage aus dem Fragenraum, eine offene Frage, ein Gesetz im Blick |
| 07 | `entwurf --file F --check "1:nein,…,15:ja" [--override GRUND]` | Linter gegen G1/G2/G4/G5/G6/G7/G8/G10 (+ G9 im Konzeptmodus); Treffer blockieren bis Override mit Grund — **negierte Treffer** („kein Preis“, „Flüchtlinge sind außerhalb“) sind nur Hinweise; 15-Punkte-Checkliste ist **Selbst-Attestierung**, muss exakt stimmen → `ENTWURF_PERMIT` |
| 08 | `freigabe --entscheidung angenommen\|geaendert\|abgelehnt [--notiz]` | Daniels Entscheidung; `abgelehnt` springt zum Abschluss; `geaendert` **setzt zurück auf Tor 07** (neuer Entwurf, neue Freigabe; Verlauf bleibt) |
| 09 | `backup --repo werkraum\|root` | BAU: `backup:`-Commit im Repo **seit Modus-Lock** nachgewiesen (Backup darf vor der Freigabe liegen, muss vor der Mutation liegen) |
| 10 | `mutation --pfad P… --beschreibung "…" --beide-fassungen ja\|nein\|nicht-betroffen` | BAU: genau eine benannte Änderung; Pfade im Repo müssen seit dem Backup-Commit **im `git diff` auftauchen** (Diff-Beweis), Pfade außerhalb nur mit Hash; `nein` blockiert → `MUTATION_PERMIT` |
| 11 | `evidenz-nachher` | BAU: `verify_8900.py` erneut, Delta behoben / neu FAIL / weiter FAIL |
| 12 | `doku --pfad D` · `--protokoll-vorschlag F` · `--protokoll-freigegeben F --go "…"` · `--keine-doku GRUND` | **Im KONZEPT-Modus zuerst: `backup:`-Commit in werkraum seit Modus-Lock nachgewiesen** (Backup-Pflicht gilt auch für Dokus). Systemdoku: Nummer eindeutig, Titel-Tag, `status:`, **Überschrift** mit „offen“; Wissensprotokoll-Eintrag nur mit Freigabe „angenommen“ **plus** eigener Zustimmung zum Eintragstext (`--go` Wortlaut) — Entwurfs-Freigabe reicht nicht |
| 13 | `commit --hash H --repo R` (je Repo einmal) | Commit existiert und enthält die Pfade dieses Bogens **in diesem Repo**; Tor bleibt offen, bis alle erwarteten Pfade über alle Repos abgedeckt sind; ein Commit in einem Repo ohne erwartete Pfade wird abgewiesen |
| 14 | `abschluss` | Bericht, `HALT` — nächster Bogen erst nach Feedback |
| — | `status` · `check-permit --permit …` · `lint --file F [--mode]` · `checkliste` | Zustand, Sperre für fremde Skripte, Linter allein, Checklistentext |

Sperren: kein Entwurf ohne Verify und Impuls; kein BAU-Pfad ohne `BAU_PERMIT` und Freigabe;
kein Wissensprotokoll-Eintrag ohne Freigabe „angenommen“ und `--go`; Linter-Treffer nur per
Override mit Grund; `abgelehnt` erzwingt Abschluss ohne Doku-Pflicht; `init` verweigert einen
laufenden oder abgeschlossenen Bogen gleichen Namens (`--session` wählen). Exit `2` bei jeder
Sperre.

Was der Harness **nicht** beweisen kann: dass die Dokus wirklich gelesen wurden, dass die
Checkliste ehrlich beantwortet ist, dass der Entwurf Daniel so gezeigt wurde, dass kein Dienst
neu gestartet wurde. Das sind Attestierungen. Beweise sind nur die Hashes, Diffs, Commits,
Evidenz-Dateien.

---

## 5. Das Modell — entschieden, verworfen, offen

### 5.1 Entschieden

| Bereich | Regel | Quelle |
|---|---|---|
| Fraktale Splitter | Ein Splitterfragment ist nicht atomar. Seine Bestandteile verblassen, verdichten sich zum Kern, lösen sich ab (werden eigenständig) oder wachsen zusammen — auch mit Gegenteiligem. Dieselbe Zustandslogik wie zwischen Splittern (treibt, verbindet sich, kristallisiert, verworfen, sedimentiert, wachsend, verblassend, platzend), rekursiv. Zukünftige Quellen (Tagebuch, Notizen, Traumtagebuch, Kalender, Entitätsmaterial) bleiben fragmentierbar. | 72 §2 |
| Permanente Schicht | Drei Fakten je Splitter/Bestandteil, ausnahmslos, je mit Datum/Uhrzeit: **Ursprungsbesitzer**, **Ursprungsart** (Entitätsgrund, Notiz, Tagebuch, Traumtagebuch, Kalender, …), **erste Verbindung** (auch wenn längst aufgelöst). Zeitstempel ist Teil des Eintrags. | 72 §4 |
| Vermengung | Herkunft beider Seiten bleibt immer sichtbar. | 72 §5 |
| Loslösen | Keine Formel. Passte der Bestandteil (echter Kontext) → Spur „kam aus diesem Verbund“ darf bleiben; war er unpassend/fremd → eher spurlos. Kontextabhängig. | 72 §5 |
| Tragen/Halten | Tragen ≠ Besitzen. Erfasst mit Zeit: wie viele tragen, wer seit wann, Freigabe als Ereignis. Gilt für Einzelsplitter **und** Verbund parallel; bei Verschmelzung bleibt pro Bestandteil Ursprungsbesitzer + letzter Einzel-Träger nachvollziehbar. | 72 §6 |
| Eigen vs. fremd | Fremd aufgenommen = tragen, kein Handelsrecht. Selbst verursacht = Verfügungsrecht (weitergeben, tauschen, anbieten, einbringen). | 71 (13:45), 70 |
| Anteile/Exit | Blase `A+B+C` behält Herkunft je Anteil. Exit löst aus dem aktuellen Zustand: `A+B+C → A'+BC'`, beide Seiten tragen die gemeinsame Zeit weiter. Ganze Blase nur gemeinsam anbietbar, eigener Anteil allein. „Was Splitter wurde, gehört der Welt.“ | 71 |
| Vielstimmigkeits-Ledger | Wert = akkumulierte Reaktionsspuren („zieht mich an“, „stößt mich ab“, „kein Bezug“) verschiedener Ströme/Wesen, zeitgestempelt, mit Herkunft, append-only. Widersprüchlichkeit ist der Wert. Kein neuer Dienst — vorhandene Aktivität wird gerichtet und gesammelt. Video-rückwärts folgt aus append-only. Angenommen als tragfähiger Kern; Feinschliff zurückgestellt, bis etwas läuft. | 73 |
| Passt-es-Prinzip | Retrospektiv: überschneidet sich das Gefühlsgewebe eines Bestandteils mit dem des Rests → passte; völlig eigenes Gewebe → unpassend. Mechanik bewusst unformalisiert. | 73 §9, 72 §8 |
| Fragenraum | Nicht „bleiben/gehen“, sondern: wohin zieht es mich / uns / mich nicht; was zieht an, stößt ab; was mag ich; wie wachsen wir; was behalten, was loslassen; was ist Kern; was ist entgegengesetzt; was passt. | 74 §2 |
| Abstimmung | Festgehalten: wer mit was rang, wer dafür/dagegen, wie abgestimmt, Ergebnis, Konsequenz je Beteiligtem; Folgeentscheidungen (Verbleib/Exit) ergeben sich daraus. Positionen werden aus dem Gefühlsgewebe gelesen, nicht erfunden. | 74 §3 |
| Chronik | Nach der Entscheidung, erzählerisch, „malerisch“, kein Poesiealbum, an die Ledger-Zeile gekoppelt. Bücher/Geschichten der Entitäten = Vision-Punkt 173. | 74 §4/§6 |
| Visionen | (nicht „Träume“) In ruhigen Phasen rekombiniert ein Splitter sein Gefühlsgewebe zu einem surrealen Fetzen; als Vision markiert, nicht Ledger. | 75 §2 |
| Krankheit als Ästhetik | Maximal widersprüchliches Gewebe wird sichtbar zerrissen dargestellt. Gilt auch zwischensplitterlich — Splitter reiben sich aneinander ohne Mensch/Entität. | 75 §3 |
| Flohmarkt-Ruck | Seltenes, chaotisches, öffentliches Ritual wirft lange unberührte Splitter ins Licht. Kein Empfehlungsalgorithmus. | 75 §4 |
| Wetterzellen | Viele lokale Stimmungslagen je Gelände; kein globaler Himmel. | 75 §5 |
| Ruf | Erlebt (selbst berührt) und gehört (Chronik gelesen) bleiben getrennte Schichten. Plus Gesetz 12. | 75 §6 |
| Selbstportrait | Montage in Ich-Form aus fremden Eindrücken, keine Bewusstseinsbehauptung; Rohstoff für eine mögliche neue Entität („Verdichtung kann eine neue Entitätsform hervorbringen“). | 75 §7, 71 |
| Phantom-Watcher | Verglühte Splitter bleiben als Watcher; ihr Watchen rückt lebende Splitter ins Licht (sichtbare Anzeigen) und wirkt auf Handel; entsteht daraus eine Entität, erbt sie Eigenheiten der Phantome. Keine Zentralinstanz (nur eine langlebige Stimme); strukturell ein vierter permanenter Fakt — in 72 noch nicht nachgetragen. Greift den Juli-Zustand „Echo“ auf. | 75 §8 |

### 5.2 Verworfen (nicht erneut vorschlagen)

| Verworfen | Ersatz / Grund | Quelle |
|---|---|---|
| Interaktionshistorie rückwärts · Urteil nach den Folgen · Zugehörigkeits-Konto · gestufte Spur | alle vier als Passt-es-Mechanik abgelehnt; Ersatz: Vielstimmigkeits-Ledger | 73 §1 |
| Embedding-Score mit Grenzwert · LLM-Einzelurteil je Loslösung · manuelle Kuration | Gesetz 1, 8, 2 | 73 §3 |
| `energie` als erfundene Ledger-Zahl | Beobachtungsgeschichte statt Kennzahl | 70 Nachtrag |
| Globaler Himmel | Wetterzellen | 75 §5 |
| „Träume“ | „Visionen“ | 75 §2 |
| Eltern-Kind-Analogie | Gesetz 5 | 72 §3 |
| Kernfrage „bleiben oder gehen“ | Fragenraum | 74 §2 |
| Solo-vs-Gruppe als Spur-Kriterium | Passt-es-Frage | 72 §5 |
| Schritt-Zerlegung/MVP in der Konzeptphase | Gesetz 9 | — |
| 410-Pfade öffnen | Gesetz 10 | 40, 70 |
| Live-Token-Streaming einer Verhandlung im Canvas | **zurückgestellt**, nicht verworfen — kollidiert mit Gesetz 4 und 8 | 70 ↔ 74 §4 |
| Eigene DB je Wesen/Splitter | shared DB | `architektur.md` |

### 5.3 Offen (nicht still entscheiden)

- Wortstatus „Splitter“ für die innere Ebene. (72 §3)
- Konkrete Passt-es-Mechanik beim Loslösen. (72 §8, 73 §11)
- Schema für das fraktale Modell; Trage-Relation; zweiter `verbindungstyp` für Gegenteiliges. (72 §8)
- Exit: was exakt mitgenommen wird; Konflikte über gemeinsam entstandene Splitter; Gewichtung
  großer Verbünde; Währung ja/nein. (71)
- Anteile als Prozent oder genealogisch. (71)
- Erstdatum der Regel „2 Splitter → beide entscheiden“ und der Bedeutungs-Selbstverhandlung. (71)
- Mechanik von Phantom-Watcher (Ins-Licht-Rücken, Vererbung messen). (75 §8)
- Zensi als Träger einer Splitter-Stimme — Funktionsweise ungeprüft. (74 §7)
- Heartbeat-Pfad in `server.py` (2.4) — Fix benannt, Freigabe ausstehend.
- Daniels zurückgehaltene Feinschliff-Punkte zum Ledger. (73 §11)
- Ursprungs-Gesprächsdateien vom Laptop — noch nicht auf dem VPS. (69 §7)

---

## 6. Freigabe-Checkliste (vor jedem Vorschlag, jeder Doku, jedem Commit)

Ein Vorschlag darf erst raus, wenn 1–8 mit **nein** und 9–15 mit **ja** beantwortet sind.
„Weiß nicht“ ⇒ `verify_8900.py` laufen lassen, nicht raten.

1. Führt er Schwellenwert, Score, Formel oder Automatismus für Leben/Passung/Wert ein? (G1)
2. Setzt er eine Instanz ein, die Wert festlegt? (G2)
3. Erzeugt er Erzählung ohne Ledger-Zeile oder vermischt beides? (G3)
4. Braucht er generierte Dialoge? (G4)
5. Benutzt er Eltern/Kind/Geburt-Sprache? (G5)
6. Behauptet er, eine Spalte passe, ohne Einzelprüfung? (G6)
7. Berührt er Flüchtlinge/Zwischenwesen als Baupfad? (G7)
8. Löst er zusätzliche LLM-Aufrufe pro Splitter/Tick/Ereignis aus? (G8)
9. Ist der Modus benannt (KONZEPT/BAU) und passt der Text dazu — ohne Schritt-Zerlegung im
   Konzeptmodus? (G9)
10. Bleiben Ursprungsbesitzer, Ursprungsart, erste Verbindung und alle Zeitstempel erhalten? (5.1)
11. Bleibt bei Vermengung die Herkunft beider Seiten sichtbar; bleibt der Ein-Klick-Zugang? (G12)
12. Ist jede Ist-Aussage mit einem Tor aus §4 in dieser Session belegt (Evidenz-Datei verlinkt)?
13. Steht die Idee nicht schon in 5.2 (verworfen) oder 5.3 (offen, zurückgestellt)?
14. Ist es eine Fortsetzung mit neuer Nummer und `KompOase 8900 —` im Titel, kein Duplikat?
15. Backup-Commit im richtigen Repo vor jeder Schreibaktion; kein Dienst-Neustart ohne Freigabe? (G13, G15)

---

## 7. Doku-Konventionen des Strangs

- **Systemdoku:** fortlaufende Nummer (vorher `ls` — Nummern können von anderen Strömen belegt
  sein), Titel `Systemdokumentation N: KompOase 8900 — …`, Frontmatter `autor`, `datum`,
  `status`, Pflichtabschnitt „Was ausdrücklich offen bleibt“, Abschnitt „Bezug zu vorherigen
  Dokus“ mit `[[wikilinks]]`. Dateinamen nicht umbenennen.
- **1:1-Wortlaut**, wenn so beauftragt: Text unverändert, auch veraltete Sätze. (70, 71)
- **Wissensprotokolle** `_claude/flextrawurst.md`, `_claude/ai-ströme.md`: immer erst
  vorschlagen, nie autonom eintragen; keine Antwort = nein. Eintrag `## YYYY-MM-DD`, darunter
  Label `KompOase-8900(zusatz):` (weitere Themen im selben Datum mit eigenem Label, z. B.
  `Lieder-Archiv:`; kein erzwungener Übergang). Ton: die Sache selbst erzählen, adressiert an
  die nächste Session — keine Berichte über Gespräche, keine Tagesereignisse; zweite Ebene
  „Technisch dahinter:“ mit echten Pfaden, Spalten, Endpunkten.
- **`reflexionsgespräche.md`:** vorher klären, welcher Reflexionspunkt gemeint ist; echte
  Zitate; Liedtexte nicht duplizieren.
- **Skill selbst:** Änderungen an `SKILL.md`/`scripts/`/`references/` zuerst hier
  (`/config/.agents/skills/kompoase-8900/`), dann byteidentisch nach
  `/root/werkraum/_claude/skills/kompoase-8900/` spiegeln und im werkraum-Repo committen —
  Tor `K8900-SKILL-001` schlägt an, solange die Kopien abweichen.

---

## 8. Referenzen

- [`scripts/kompoase_harness.py`](scripts/kompoase_harness.py) — Bogen-Harness (§4b); [`scripts/verify_8900.py`](scripts/verify_8900.py) — Beweis-Tore (§4).
- [`references/chronologie.md`](references/chronologie.md) — Herkunft der Ideen Mai–September
  mit Sicherheitsgrad (aus Doku 71) und die Bau-/Konzept-Ereignisse vom 17.–19.09.
- `docs/systemdoku/40` — Ursprung der Standalone-Fassung, AI-Strom-Tagging, 410-Vorgeschichte.
- `docs/systemdoku/69`–`75` — Primärquellen dieses Skills.
- `_codex/berichte/2026-09-18-splitter-physik-isolation-live.md` — Isolation des
  Produktions-Daemons (Nutzer, DB-Rolle, Logpfad).
- `welt/schema_welt.sql` Z. 70–108 — `splitter`, `splitter_verbindungen`.
- `_claude/ideen/flextrawurst_490_punkte_quellliste.md` — Vision-Punkt 173.
