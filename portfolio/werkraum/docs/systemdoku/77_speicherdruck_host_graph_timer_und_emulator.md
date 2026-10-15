# Systemdokumentation 77: Speicherdruck auf dem Host — Graph-Timer, Android-Emulator, Modell-Pinning

---
autor: claude-code bei Daniels VPS
datum: 2026-09-19
status: zwei Ursachen behoben und live verifiziert, eine bewusst unangetastet, ein Absturz unaufgeklärt
---

## 1. Anlass

Am 2026-09-18 stürzte der virtuelle Desktop zweimal ab (gegen 02:50 und gegen 09:50), beide Male
mit dem Verlust aller offenen Terminals und Prozesse. In der Nacht darauf brach Claude Code einen
eigenen Hintergrundbefehl ab mit der Begründung, das System sei kritisch knapp an Speicher. Daraus
wurde Daniels Frage: **was frisst den RAM?** Diese Doku hält die Messung, die Funde und die
Eingriffe fest.

## 2. Wie gemessen wurde — und warum `ps` täuscht

`ps`/RSS zeigte für die beiden `llama-server`-Prozesse 29,6 GB und 29,2 GB, zusammen also mehr als
der gesamte Arbeitsspeicher. Das ist Doppelzählung: beide Instanzen mappen **dieselbe** 29-GB-Modelldatei
per `mmap`. Erst `PSS` aus `/proc/<pid>/smaps` trennt das sauber:

```
PID 2237173  llama-hauhaucs-hintergrund   PSS 14,7 GB   Private 0,4 GB
PID 2237325  llama-hauhaucs (Chat)        PSS 14,3 GB   Private 0,0 GB
Modelldatei  Qwen3.6-35B-A3B-…-Q6_K_P.gguf                     29 GB
```

Merksatz für künftige Messungen an diesem Host: **RSS lügt bei mmap-geteilten Modellen, PSS nicht.**

Ausgangslage am 2026-09-19 gegen 04:33: `0,4 GB frei · 3,2 GB verfügbar · 21 GB Swap belegt`.

## 3. Fund 1 — ein Timer, der seit Monaten scheitert und dabei 5 GB greift

`werkraum-graph-update.service` (Timer: alle 10 Minuten) baut aus `/root/werkraum` eine
Übersichtskarte: jede Datei ein Knoten, Kanten für Imports, absolute Pfadnennungen,
Ordnernachbarschaft, JSON-Bezüge. Ergebnis sind
`out/process_camera/werkraum_graph.json` und `…/werkraum_explorer.html` im Repo `/root/flextrawurst`.

Tatsächlicher Zustand vor dem Eingriff:

```
Läufe seit 2026-09-05 (Journal-Grenze):  1589 Fehlschläge, 0 Erfolge
Fehlerbild:   FATAL ERROR: Reached heap limit — JavaScript heap out of memory
Abbruch nach: ~26 s CPU, ~4,3 GB RSS
Ausgabedatei: werkraum_graph.json, Stand 2026-07-23 20:48 (890 KB)
```

Die Ausgabe ist also **zwei Monate alt**, während der Dienst alle zehn Minuten rund um die Uhr
5 GB anforderte und starb. Das Journal reicht nur bis zum 05.09. zurück; der Defekt ist nach
Dateidatum deutlich älter.

### 3.1 Warum es scheiterte — zwei unabhängige Ursachen

**Ursache A, die Knotenschleife.** Für jede gefundene Datei lief

```ts
let content = "";
try { content = readFileSync(full, "utf-8"); } catch { /* skip */ }
...
  lines:   content ? content.split("\n").length : 0,
  excerpt: redactSecrets(content.slice(0, EXCERPT_LIMIT)),   // EXCERPT_LIMIT = 500
```

also ein vollständiges Einlesen **jeder** Datei als UTF-8-String — nur um Zeilen zu zählen und
500 Zeichen Auszug zu nehmen. Der Extensionsfilter (`.pyc .pyo .png .jpg .jpeg .pdf .tar .gz .sql
.xwd .pem .lock`) lässt dabei durch, was im Werkraum inzwischen gewachsen ist:

```
356.396 Dateien · 291 GB passieren den Filter, darunter
  9046 MB  _gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite
  2635 MB  engine/godot-vertical-slice/…/bibliotheksatlas.sqlite
  1553 MB  …/AUSSENRAUM_ROHKANDIDATEN.jsonl
   906 MB  _gpt/terminal_capture/codex/…/terminal.log
   526 MB  _gemini/musikvideoprojekt/…/verbrannte_erde_FULL_MASTER_1080p60.mp4
   512 MB  _gpt/…/mcp_ram_snapshot_all/039_….bin
```

Ein Heap-Limit hochzusetzen hätte hier nichts gebracht: 291 GB passen in keinen Heap.

**Ursache B, der Inhalts-Cache.** Direkt danach:

```ts
const contentCache = new Map<string, string>();
for (const node of nodes) {
  if (node.size > 200_000) continue;
  try { contentCache.set(node.id, readFileSync(full, "utf-8")); } catch {}
}
```

Ein Deckel **pro Datei** (200 KB), aber keiner für die **Summe**. Bei rund 350.000 Dateien
unterhalb dieser Grenze sind das mehrere GB gleichzeitig im Heap.

### 3.2 Der Eingriff

Commit `7d24d814729` im Repo `/root` (Toplevel `/root`, Pfad `flextrawurst/`):

- Dateien über `LARGE_FILE` (40 KB) werden nicht mehr komplett gelesen, sondern über
  `openSync`/`readSync` nur am Kopf angelesen (neue Konstante `HEAD_BYTES = 8192`). Der Auszug
  braucht 500 Zeichen; eine Zeilenzahl über hunderte MB wäre weder brauchbar noch bezahlbar und
  bleibt für solche Dateien 0 — sie tragen ohnehin bereits das Flag `large`.
- `contentCache` wird nicht mehr vorab gefüllt. Neu ist `inhalt(id)`: liest bei Bedarf und cacht
  nur bis `CACHE_BUDGET` (400 MB); darüber hinaus wird erneut von Platte gelesen. Alle fünf
  Aufrufstellen (`contentCache.get(node.id) ?? ""`) wurden umgestellt.

**Fachlich unverändert:** jede Datei bleibt als Knoten im Graphen, und wie bisher tragen nur
Dateien bis 200 KB zur Verlinkung bei.

**Verifikation:** vorher reproduzierbarer Abbruch nach 59 s bei 4,3 GB; nachher über 15 Minuten
Laufzeit ohne jeden Heap-Fehler. Der Abbruch danach war ein gesetztes Zeitlimit, kein Fehler.

### 3.3 Was dabei neu sichtbar wurde

Der Job ist **langsam** — über 15 Minuten. Das war vorher nie zu sehen, weil er nach 26 Sekunden
starb. Ursache ist Abschnitt 6 des Skripts: für jede `py`/`ts`/`md`-Datei wird über **alle**
JSON-Knoten iteriert und `content.includes(basename)` geprüft — eine Multiplikation im
Milliardenbereich bei der heutigen Werkraum-Größe.

Daniels Entscheidung dazu (2026-09-19): **Karte behalten, Geschwindigkeit so lassen, Takt auf 33
Minuten.** Damit überschneiden sich Läufe nicht mehr. Umgesetzt in
`/etc/systemd/system/werkraum-graph-update.timer`:

```
Description=Werkraum-Graph alle 33 Minuten aktualisieren
OnUnitActiveSec=33min        (vorher 10min)
OnBootSec=2min               (unverändert)
```

Sicherung der alten Fassung:
`_claude/berichte/werkraum-graph-update.timer.vor-33min-umstellung_20260919`.
Da `OnUnitActiveSec` ab der letzten Aktivierung rechnet, wurde der Dienst einmal manuell
angestoßen, damit der Takt einen Startpunkt hat.

## 4. Fund 2 — ein abgeschalteter Dienst, der sich selbst wiederbelebt

`instagram-avd.service` (Android-Emulator, Google Play API 34) lief headless mit `-no-window` und
`-memory 4096`, belegte 3,2 GB PSS — obwohl er aus Daniels Sicht gar nicht eingeschaltet war.
Die Erklärung steht in der Unit:

```
is-enabled:  disabled           → startet nicht beim Boot
Restart=on-failure              → kommt nach jedem Abschuss in 3 s zurück
ActiveEnterTimestamp: 2026-09-18 02:55:07
```

Der Dienst war also für den Dauerbetrieb nie vorgesehen, wurde irgendwann von Hand gestartet —
und die Restart-Regel machte ihn faktisch **immun gegen den OOM-Killer**: `systemd-oomd` schoss ihn
am 18.09. um **02:54:56** ab, elf Sekunden später war er wieder aktiv und nahm sich seine 3,2 GB
zurück.

## 5. Die Kausalkette zum ersten Absturz

`systemd-oomd` protokollierte am 2026-09-18 zwischen **02:54:56 und 02:55:05** eine ganze Kaskade:

```
02:54:56  instagram-avd.service
02:54:56  containerd.service
02:54:56  docker-ed7626cd…scope          ← Desktop-Container
02:54:57  geni-hoerer.service
02:54:58  docker-f46fc4a8…scope
02:54:58  kimi-codex-grundriss-sync.service
02:54:58  docker-6dd51e89…scope
02:54:58  docker-84e1e639…scope
02:54:59  docker-e849d44c…scope
02:55:00  docker-34fc17e3…scope
02:55:01  docker.service
02:55:01  docker-146f7cb7…scope
02:55:02  docker-2f2d1f98…scope
02:55:02  flextrawurst-3d-truth-watchdog.service
02:55:03  llama-hauhaucs-hintergrund.service
02:55:03  ollama.service
02:55:05  llama-hauhaucs.service
```

Der Druck war nach dem ersten Abschuss nicht weg, also arbeitete `oomd` weiter — und traf dabei
die Docker-Scopes, in denen die virtuellen Desktops laufen. **Das ist der erste Absturz.**
Kein Kernel-OOM (`journalctl -k` zeigt keine `Killed process`-Zeilen), sondern `systemd-oomd`
auf Basis von Speicherdruck.

Für den **zweiten Absturz gegen 09:50** liegt kein solcher Beleg vor: keine `oomd`-Kills in dem
Fenster, nur ein geplanter `welt-api`-Stopp aus der parallelen Sicherheitsarbeit eines anderen
Stroms. Ursache bleibt offen — siehe Abschnitt 8.

## 6. Was geändert wurde

| Eingriff | Wirkung | Beleg |
|---|---|---|
| Graph-Export repariert | kein OOM mehr; 59 s/4,3 GB → über 15 min ohne Fehler | Commit `7d24d814729` in `/root` |
| Timer 10 min → 33 min | keine überlappenden Läufe mehr | `/etc/systemd/system/werkraum-graph-update.timer`, Sicherung in `_claude/berichte/` |
| verwaiste Export-Prozesse beendet | zwei parallel laufende Node-Exporte entfernt | — |
| `instagram-avd.service` gestoppt | 3,2 GB dauerhaft frei; bleibt aus (`disabled`) | `systemctl is-active` → inaktiv, kein `qemu`-Prozess |

Speicherverlauf über die Nacht:

```
04:33   0,4 GB frei ·  3,2 GB verfügbar
06:13   4,5 GB frei ·  22 GB verfügbar     (nach Timer-Stopp)
07:36  10,0 GB frei ·  26 GB verfügbar     (nach Emulator-Stopp)
08:43  13,0 GB frei ·  27 GB verfügbar
```

## 7. Was bewusst nicht angefasst wurde

**Das Modell-Pinning.** `llama-hauhaucs-hintergrund.service` startet mit `--mlock`; gemessen sind
**28,5 GB gepinnt** (`VmLck` in `/proc/2237173/status`). Diese Seiten sind nicht auslagerbar und
nicht reclaimable — sie sind der Grund, warum „frei" auf dieser Maschine strukturell klein bleibt,
während „verfügbar" hoch ist. Das ist kein Defekt, sondern eine Leistungsentscheidung: ohne
Pinning würde der Kernel bei Druck Modellteile auslagern und jeder Gedanke eines Wesens müsste sie
von Platte nachladen. Daniels Entscheidung am 2026-09-19: **so lassen.**

**Ollama.** 1,4 GB, wird weiterhin genutzt — im Journal der letzten sechs Stunden sieben Aufrufe
auf `/api/embed`. Nicht anfassen.

Zur Einordnung der beiden llama-Instanzen: `llama-hauhaucs.service` auf Port 11435 ist die
Chat-Instanz (`--threads 10`), `llama-hauhaucs-hintergrund.service` auf Port 11436 die
Hintergrund-Instanz für Takt/Reaktionen (`--threads 5`, `--mlock`). Beide teilen sich dieselbe
GGUF per `mmap`; ein Abschalten einer Instanz spart daher **nicht** deren PSS, sondern nur deren
KV-Cache.

## 8. Was ausdrücklich offen bleibt

- **Der zweite Desktop-Absturz vom 2026-09-18 gegen 09:50 ist nicht aufgeklärt.** Kein `oomd`-Kill
  im Zeitfenster, kein Kernel-OOM. Andere Ursache, nicht untersucht.
- **Der Erstlauf des reparierten Exports war beim Schreiben dieser Doku noch nicht beendet.** Bewiesen
  ist bislang nur, dass er nicht mehr abstürzt — nicht, dass er fertig wird. Prüfpunkt: ändern sich
  `out/process_camera/werkraum_graph.json` und `…/werkraum_explorer.html` auf ein Datum nach dem
  2026-07-23?
- **Abschnitt 6 des Export-Skripts** (jede Code-Datei gegen alle JSON-Knoten) bleibt auf Daniels
  Wunsch unoptimiert. Sollte der Werkraum weiter wachsen, wächst diese Laufzeit überproportional
  und kann die 33 Minuten irgendwann überschreiten.
- **Der Extensionsfilter des Exports** kennt keine Positivliste für Textformate. `.sqlite`, `.bin`,
  `.zip`, `.mp4` erzeugen weiterhin Knoten (nur noch ohne vollständiges Einlesen). Ob solche
  Dateien überhaupt in der Karte stehen sollen, ist nicht entschieden.
- **`geni-dokumentieren.service`** wurde am 19.09. um 03:36 per Timeout beendet, mit
  8,6 GB Speicher-Peak und 2,7 GB Swap-Peak laut eigener systemd-Bilanz. Nicht untersucht.
- **Warum `instagram-avd` ursprünglich von Hand gestartet wurde und ob das Instagram-Projekt ihn
  wieder braucht**, ist unbekannt. Rückholen jederzeit mit `systemctl start instagram-avd.service`.
- **Die Altlast `/root/geni_gedaechtnis`** (laut CLAUDE.md ~31,5 Mio. Dateien) macht ein
  `git add -A` im Repo `/root` praktisch unbenutzbar — der Vollscan hängt. Für Commits in diesem
  Repo ist ein Pfad-Argument nötig. Die grundsätzliche Lösung steht weiterhin aus
  (Systemdoku 31, Abschnitt „Offen: geni-muster.service").

## 9. Nachtrag 2026-09-19 — der Export läuft durch, und was dabei sichtbar wurde

Der in Abschnitt 8 offene Prüfpunkt ist beantwortet: der Erstlauf des reparierten Exports wurde
**nicht** fertig. Er lief 1 h 52 min und brach dann in der Ausgabe ab.

Damit waren zwei weitere Ursachen zu lösen — eine für die Laufzeit, eine für die Ausgabe.

### 9.1 Laufzeit — die quadratischen Schleifen

Abschnitt 3 des Skripts prüfte jede `.py`/`.md`-Datei gegen **alle** langen Basenamen im Werkraum,
Abschnitt 6 jede `.py`/`.ts`/`.md`-Datei gegen **alle** JSON-Knoten. Beide per `content.includes()`.

Das ist Dateien × Namen. Jede neue Datei verlängerte also nicht nur ihren eigenen Durchlauf,
sondern den aller anderen mit.

Umgestellt auf Token-Nachschlag: der Text wird einmal in Wort-Kandidaten zerlegt (`/[\w.-]{6,}/g`),
jedes Token einmal in einer Map nachgeschlagen. Aus Dateien × Namen wird Dateien × Textlänge.

Gemessen am identischen Bestand:

```
vorher   1 h 52 min   Abbruch in der Ausgabe
nachher       78 s    Abbruch in der Ausgabe
danach        57 s    Exit 0
```

Fachlich ändert sich genau eine Sache: ein Basename zählt nur noch als Erwähnung, wenn er als
eigenständiges Wort vorkommt. Treffer mitten in einem längeren Wort entfallen.

Commit `1971bfb3df6` in `/root`.

### 9.2 Ausgabe — ein String, den V8 nicht bilden kann

Der zweite Abbruch war kein Speichermangel, sondern eine harte Grenze:

```
RangeError: Invalid string length
    at JSON.stringify (<anonymous>)
    at scripts/export_werkraum_graph.ts:374:25
```

Der Heap war zu dem Zeitpunkt bei 4,5 GB und damit nicht am Anschlag. V8 begrenzt die **Länge eines
einzelnen Strings**, und der Graph als eine Datei überschreitet sie.

Ein Ausschluss von Beständen wäre die naheliegende Antwort gewesen. Daniel hat sie verworfen:
*„ne soll bleoben finde andere löungen"*.

Die Lösung, die er stattdessen vorgegeben hat, ist eine Sichtreichweite — *„dort wo man gerade steht
und geht auf der karte hat man qiasi eine sichtreichweite und man kann aber alles durchforsten
stückweise"* — nach dem Muster von Streaming: es wird immer nur geladen, was gerade gebraucht wird.

Umgesetzt als Kachel-Export. Eine Region ist ein Ordner-Teilbaum mit höchstens 3.000 Knoten; ist ein
Teilbaum größer, bilden seine direkten Dateien eine eigene Region und jeder Unterordner wird für
sich zerlegt.

```
out/process_camera/graph/
  index.json        nur die Regionsebene: Zählwerte, Typen, verdichtete Kanten
  r/<region>.json   die Knoten dieser Region, ihre Innenkanten, ihre Randkanten
  meta.json         Gesamtzahlen, Zeitstempel, Status der alten Einzeldatei
```

Jede Region wird für sich serialisiert — es entsteht nie wieder ein großer String. Kein Knoten geht
verloren, er wandert nur in eine Kachel.

Die alte Einzeldatei wird weiterhin **versucht**, damit der bestehende Explorer nicht bricht. Gelingt
sie nicht, bleibt die vorhandene Datei unangetastet und `meta.json` hält fest, warum.

### 9.3 Erster vollständiger Durchlauf — die Zahlen

```
658.002 Knoten
1.602.814 Kanten
  1.282 Regionen
     57 s Laufzeit, 4,55 GB Max-RSS, Exit 0
```

Kantenarten:

| Art | Anzahl |
|---|---|
| `uses-json` | 1.340.764 |
| `ref` | 161.508 |
| `owns` | 50.208 |
| `folder` | 37.300 |
| `wikilink` | 12.797 |
| `import` | 237 |

Knoten nach Typ, die ersten fünf:

| Typ | Anzahl |
|---|---|
| `java` | 415.010 |
| `smali` | 162.898 |
| `md` | 63.865 |
| `json` | 5.520 |
| `jsonl` | 1.998 |

**89 % aller Knoten (585.512) liegen unter `engine/godot-vertical-slice`**, verteilt auf 1.058 der
1.282 Regionen. Das ist der dekompilierte APK-Bestand. Er bleibt auf Daniels Entscheidung drin.

### 9.4 Der Befund, der dabei auffiel — `uses-json` ist zu 84 % Rauschen

Die Kacheln sind klein, solange man nur die Knoten zählt. Die größte trägt 1.535 Knoten. Ihre Datei
ist trotzdem 185 MB groß.

Der Grund sind nicht die Knoten, sondern die Randkanten:

| Region | Knoten | Innenkanten | Randkanten |
|---|---|---|---|
| `_gpt_mcp_arbeitskoerper` | 1.535 | 3.445 | 523.624 |
| `_shared` | 1.724 | 44.981 | 477.623 |
| `obsidian_vault__shared` | 1.724 | 44.647 | 476.086 |
| `_gpt_ui_visible_conversations` | 1.077 | 1.499 | 155.382 |

Von 1,6 Mio. Kanten verlaufen nur 216.310 **innerhalb** einer Region. Alle übrigen kreuzen eine
Regionsgrenze und stehen deshalb in zwei Kacheln.

Die Ursache liegt eine Ebene tiefer, in der Regel selbst. `uses-json` verknüpft eine Code- oder
Textdatei mit einer JSON-Datei, wenn deren **Basename** im Text vorkommt. Der Werkraum enthält:

```
1205 × package.json
 913 × MANIFEST.json
 130 × messages.json
  92 × tsconfig.json
```

Wer in einer Markdown-Datei das Wort `package.json` schreibt, erzeugt damit 1.205 Kanten — zu jeder
`package.json`, die es irgendwo gibt. Bei 5.520 JSON-Knoten und 1.340.764 `uses-json`-Kanten sind das
im Schnitt 243 Kanten pro JSON-Datei.

Das ist kein Nebeneffekt der Umstellung: die alte Schleife tat dasselbe, nur langsamer. Sichtbar
wurde es erst, als die Kacheln eine Größe bekamen, die man messen kann.

[status: bestätigt 2026-09-19 -- von Daniel entschieden, siehe 9.6] Ob ein mehrdeutiger Basename
überhaupt als Referenz gelten soll, ist eine Bedeutungsfrage, keine technische. Die Regel wurde
daraufhin geändert.

### 9.5 Was danach noch aussteht

- Der Explorer (`werkraum_explorer.html`, 743 Zeilen d3) liest weiterhin die alte Einzeldatei und
  kennt die Kacheln nicht. Seit 9.6 ist diese Datei wieder schreibbar, er zeigt also eine frische
  Karte — aber über eine Brücke, die bei weiterem Wachstum erneut reißt.
- `werkraum-graph-update.timer` bleibt gestoppt, bis eine frische Karte nachweislich auf Platte
  liegt. Das Intervall steht auf 33 Minuten; der Lauf braucht davon 57 Sekunden.
- Abschnitt 8 dieser Doku nennt Abschnitt 6 des Skripts als „bleibt unoptimiert". Das ist seit
  `1971bfb3df6` überholt — beide Schleifen laufen jetzt über den Token-Nachschlag.

### 9.6 Die Entscheidung zu `uses-json` — und was sie freigelegt hat

Daniel hat die offene Frage aus 9.4 am 2026-09-19 entschieden: *„du hast recht passt nicht"*.
Der `[status: offen]`-Marker dort ist damit aufgelöst.

Die Regel lautet jetzt:

- Ein JSON-Dateiname, den es im Werkraum nur **einmal** gibt, wird weiterhin überall verbunden.
  An seiner Erwähnung ist nichts mehrdeutig.
- Ein **mehrdeutiger** Name verbindet nur die Kandidaten mit dem längsten gemeinsamen Ordnerpfad
  zur Quelldatei. Wer in `flextrawurst/README.md` von `package.json` schreibt, meint die im selben
  Baum, nicht eine von 1.204 anderen.
- Gibt es **gar keinen** gemeinsamen Pfad, entsteht keine Kante.
- Liegen **mehr als vier** Kandidaten gleich nah, trägt der Name keine Auskunft mehr, und es
  entsteht ebenfalls keine Kante.

Wirkung am identischen Bestand:

| | vorher | nachher |
|---|---|---|
| Kanten gesamt | 1.602.814 | **274.468** |
| davon `uses-json` | 1.340.764 | **12.414** |
| größte Kachel | 193,2 MB | **13,4 MB** |
| Einzeldatei | `RangeError` | **460 MB, geschrieben** |
| Laufzeit | 57 s | 63 s |
| Max-RSS | 4,55 GB | 5,08 GB |

Die Kachelgrößen liegen damit im Streaming-Bereich:

```
  >5 MB     7 Kacheln
  1-5 MB  225
0,1-1 MB  141
 <0,1 MB  909
```

Die größte ist `_claude.json` mit 13 MB — mein eigener Bereich, dicht verlinkt, das ergibt Sinn.

**Der eigentliche Fund steht in der vorletzten Zeile der Tabelle.** Die alte Einzeldatei ließ sich
plötzlich wieder schreiben. Sie war nicht an der Knotenzahl gescheitert, sondern an 1,3 Mio.
Kanten, von denen fast keine etwas aussagte.

Damit liegt zum ersten Mal seit dem 2026-07-23 wieder eine frische Karte auf Platte, und der
bestehende Explorer funktioniert ohne Umbau.

**Das ist trotzdem kein Grund, die Kacheln fallen zu lassen.** 460 MB sind rund 90 % dessen, was
V8 als Stringlänge überhaupt zulässt. Der nächste größere Zuwachs im Werkraum bringt dieselbe
Grenze zurück — nur dann ohne Vorwarnung. Die Kacheln sind der Weg, der nicht wieder an eine Wand
läuft; die Einzeldatei ist ab jetzt die Brücke, nicht das Ziel.

### 9.7 Die Karte — und warum der alte Explorer aus dem Gebrauch fiel

Daniel erinnerte sich beim Nachlesen an den Explorer: er habe anfangs gewirkt wie *„ne art obsidian
2.brain auf lowbudget"* — und irgendwann nur noch den Laptop zum Absturz gebracht.

Das ist die fehlende Hälfte der Geschichte. Der Explorer war nie kaputt. Das Gelände unter ihm ist
gewachsen.

Er lädt `werkraum_graph.json` vollständig in den Browser und übergibt **jeden** Knoten an eine
Kraftsimulation — jeder Kreis gegen jeden, dreißigmal in der Sekunde. Bei 658.000 Knoten ist das
kein Bedienfehler mehr, sondern eine Wand. Ohne diesen Zusammenhang liest sich Abschnitt 9.6
falsch: dass die Einzeldatei wieder schreibbar ist, heißt nicht, dass sie wieder benutzbar wäre.

Daneben steht jetzt `werkraum_karte.html` auf denselben Kacheln.

**Der Aufbau.** Beim Öffnen wird nur `graph/index.json` geholt — die Ordnerebene, 1.282 Regionen
als Ballons mit ihrer Dateizahl. Keine einzige Kachel. Wer eine Region betritt, bekommt ihre
Dateien aus `graph/r/<region>.json`; je nach eingestellter Reichweite auch die der Nachbarn. Alles
dahinter bleibt Ballon: man sieht immer, dass dort noch etwas liegt, ohne es zu laden.

**Nachgesehen statt behauptet.** Die Karte wurde mit Playwright geöffnet und gemessen, auf einem
Wegwerf-Port, ohne einen laufenden Dienst anzufassen. Der erste Entwurf war unbrauchbar: 4.122
Kreise, 21.505 Linien, und eine Übersicht aus 1.282 identisch grauen Kreisen, weil nur Dateiknoten
eingefärbt waren.

Vier Änderungen, alle an der Darstellung:

- **Standard-Reichweite 0 statt 1.** Reichweite 1 zog bei einer großen Region sofort zehn Kacheln
  nach und lief ins Budget — 73 Regionen blieben außen vor. Man steht erst einmal da, wo man steht.
- **Ballons nach oberstem Ordner eingefärbt.** Erst damit trägt die Übersicht Struktur statt nur
  Zahlen.
- **Kantenfilter**, Standard „nur tragende": `import`, `wikilink`, `owns`, `folder`. `ref` und
  `uses-json` sind Erwähnungen — richtig, aber sie übermalen das Bild.
- **Beschriftung auf die 150 größten Dateien gedeckelt**, Ballons immer.

Gemessen an derselben Region (`wir-muessen-claude-code-retten`):

| | erster Entwurf | danach | alter Explorer |
|---|---|---|---|
| beim Öffnen | 1,07 MB | 1,07 MB | 482 MB |
| JS-Heap (Übersicht) | 40,4 MB | **10,9 MB** | — |
| beim Betreten geladen | 21,15 MB | **4,85 MB** | — |
| Kacheln | 10 | **1** | — |
| Kreise | 4.122 | **2.510** | **658.000** |
| Linien | 21.505 | **886** | — |
| außer Budget | 73 Regionen | **keine** | — |

Keine Konsolenfehler, keine Warnungen. Die Detailtafel öffnet und zeigt echten Dateiinhalt.

**Was dabei auffiel und ein eigener Befund ist.** Die Übersicht zeigt einen weiten Sternenhimmel
aus hunderten gleich aussehenden Ballons mit „3.0k" — das sind die Teilstücke des dekompilierten
APK-Bestands. Der farbige Klumpen in der Mitte ist der gesamte übrige Werkraum. Das ist keine
Wertung, das sind die 89 % aus 9.3, zum ersten Mal als Bild.

**Zwei Restmängel**, offen und unbearbeitet: im dichten Kern überlappen die Namen weiterhin, und
ein großer Teil der Fläche besteht aus einzelnen Punkten ohne jede sichtbare Verbindung.

### 9.8 Ein Loch, das beim Freischalten entstand

Der Vorschau-Server schützt seine Werkraum-Routen mit Basic-Auth. Die Liste nennt ihren Grund im
Code selbst — *„C-002: kein oeffentliches Lesen/Schreiben des Werkraums mehr"* — und führt
`/werkraum_explorer` auf.

Die neue Karte und die Graph-Kacheln zeigen genau dasselbe: Pfade, Dateinamen und einen Auszug von
bis zu 500 Zeichen aus jedem Inhalt. Sie standen nicht auf dieser Liste und waren nach der
Freigabe der Routen ohne Anmeldung erreichbar.

Ergänzt. Geprüft nach dem Neustart:

```
ohne Anmeldung   /werkraum_karte.html      401
                 /graph/index.json         401
                 /graph/r/<region>.json    401
                 /werkraum_explorer.html   401
öffentlich       /                         200
                 /welt.html                200
```

Der Zugang von außen lief auch vorher schon über nginx auf Port 8448, das dort mit `auth_basic`
auf `location /` liegt, und 8787 lauscht nur auf 127.0.0.1. Nach außen war damit nichts offen. Die
Regel des Servers galt trotzdem für diese Routen nicht, und die Regel ist der Maßstab, nicht der
Umstand, dass eine zweite Schicht zufällig darüber lag.
