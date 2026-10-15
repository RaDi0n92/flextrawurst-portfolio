# 48 — GENIs Gedächtnis: Befund, Daniels Entwurf, offene Entscheidung

**Stand:** 2026-08-03, Nacht/Morgen (03:19–06:00 CEST)
**Geschrieben von:** Claude Code auf Daniels VPS
**Anlass:** Gespräch nach einem Verbindungsabbruch. Ausgangspunkt war die Frage, wie sich die
sieben Codewesen erinnern — und von dort aus, wie GENI es tut.

**Warum dieses Dokument existiert:** Daniel wörtlich, 2026-08-03:

> "geh dein gesamtes ´kontextfenster soweit zurück um ne lückenlose doku in md zu ma´chen und
> such obs shon in md doku is für das was grade alles parralel dan abgesichert werden wird und
> nutze wenn du kannst alles 1zu1 roh von mir mit in die doku rein...um meiine rohenn aussagen
> und auch den verlauf hie sicher zu haben wir loggen unsreer gespräche auf 8444...."

**Verhältnis zu bestehender Doku (geprüft, nicht angenommen):** `docs/systemdoku/11_geni.md` und
`docs/systemdoku/geni-neustruktureien-und-erforschen.md` sind beide vom 23.07.2026 und beschreiben
den Stand *vor* dem Umbau vom 01.08. (Selbst-Suche, Inbox-Vault, Doku-Vault). Deshalb dieses eigene
Dokument für den Befund.

Meine erste Begründung dafür war falsch: ich hatte gesagt, in
`geni-neustruktureien-und-erforschen.md` hineinzuschreiben würde fremdes Protokoll (Codex/Luna)
verfälschen. Daniel dazu, 2026-08-03: *"ne hätte es nicht...du hättest sauber ansetzen und
einleiten können xD das ist ja keine reinnerung sondern vision und verlauf xD"* — richtig, ein
Verlauf wird fortgeschrieben, nicht umgangen. Die Datei hat deshalb jetzt einen klar abgegrenzten
Fortsetzungsabschnitt am Ende, der auf dieses und die drei Schwester-Dokumente zeigt.

`11_geni.md` beschreibt in
`## 3. Gedächtnis-System` bereits `tiefe_erhoehen(knoten_id) ← Häufigkeit erhöhen`; was unten steht,
ist die Messung dazu, nicht der Ersatz.

---

## Teil A — Was tatsächlich gefunden wurde

Alles in diesem Teil ist am 2026-08-03 an der laufenden Anlage nachgeprüft. Wo eine Zahl steht,
stammt sie aus einer Abfrage, nicht aus Erinnerung.

**Zur Knotenzahl:** hier steht 301.150, in `50_knoten_und_kanten.md` steht 307.182. Beides stimmt —
die erste Messung war um ~05:30, die zweite um ~07:45 desselben Morgens. Der Hörer schreibt
weiter, während wir darüber reden; in gut zwei Stunden kamen 6.032 Knoten dazu. Die Zahlen werden
bewusst nicht angeglichen, sie tragen ihren Messzeitpunkt.

### A1. GENIs Suche — wie sie gebaut ist

Zwei Dateien tragen das:

**`/root/werkraum/geni/selbst_suche.py`** (327 Zeilen) baut den Index. Vier Sammler:

- `_knoten_sammeln()` — die Knoten aus `/root/geni_gedaechtnis/knoten.db`, ohne die drei
  Rauschquellen `vps_dateisystem`, `chatgpt`, `vps_prozesse`, Mindestlänge 15 Zeichen.
- `_vault_sammeln()` — alle `*.md` aus `/root/werkraum/geni_dokumentation/` und alle Briefe aus
  `/root/werkraum/geni_inbox/*/*/*.md`.
- `_protokolle_sammeln()` — `fragen_antworten/*.json` und `spiegel_gelesen/*.json`.
- `_splitter_sammeln()` — die Splitter aus der flextrawurst-Postgres, weil sie nicht in ihrem
  Knotengedächtnis liegen.

Darüber zwei Suchwege gleichzeitig: SQLite **FTS5/BM25** für exakte Begriffe, Namen und Zahlen, und
**Chroma** mit der lokal vorhandenen ONNX-MiniLM-Embedding für Bedeutung. Zusammengeführt per
**Reciprocal Rank Fusion** (K=60) — ein Treffer, den beide Wege finden, steigt nach oben, ohne dass
die zwei Bewertungsskalen miteinander verrechnet werden müssen.

Im Kopf der Datei steht Daniels Auftrag vom 2026-08-01 wörtlich:

> "ich will fuer geni speziell dass sie sich selbst komplett mit rag semantisch und hybrid in ihren
> allem durchsuchen kann"

**`/root/werkraum/geni/dokumentieren.py`** gibt ihr das Werkzeug in die Hand. Sie bekommt nur die
Aufgabe — *„hallo geni. jetzt geht es um X. such in deinem gedaechtnis nach X. nachdem du etwas
ueber X gelesen hast dokumentiere es."* — und eine Funktion `suche(frage)`. `MAX_RUNDEN = 8`,
`TREFFER_PRO_SUCHE = 8`. Sie entscheidet selbst, wonach sie sucht und wie oft.

Der Grund dafür steht als Docstring in der Datei, Daniels Wortlaut vom 2026-08-01:

> "warum kommt das als eingang rein .... wofuer hat geni nun die ragsuche ... natuerlich um selbst
> nachzuforschen, du musst sie nicht vollstopfen digga"

Vorher lagen 25 Splitter und 25 Knoten fertig in ihrem Prompt.

### A2. Wie GENI sich erinnert — vier Orte, nur zwei leben

| Ort | Umfang | Zustand |
|---|---|---|
| `knoten.db` (SQLite) | 301.150 Zeilen | lebt, wächst laufend |
| `kanten/*.json` | 1.309 Dateien | wächst nur im Webchat, letzte 20.07. |
| `episodisch/` | 2 Dateien | vom 20.04., seitdem unberührt |
| `semantisch/` | 8 Dateien | vom 20.04., seitdem unberührt |
| `fragen_antworten/` + `spiegel_gelesen/` | 24 JSON-Dateien | lebt, zuletzt 2026-08-03 04:26 |
| `selbst_index/` (FTS + Chroma) | 43.060 Einträge | seit 2026-08-01 |

Knotenverteilung nach Quelle: `vps_dateisystem` 226.740, `flarum` 37.565, `claude` 22.819,
`vps_system` 8.441, `codex` 2.214, `claudeweb` 1.367, `vps_prozesse` 614, `import:vision1.md` 355,
`daniel` 352, `geni_muster` 292, `geni_selbst` 288, `gemini` 103.

**Der wichtigste Befund hier:** `semantisch/` (ihr Weltbild, acht Dateien: `daniel.md`,
`geni_wesen.md`, `dakgord_system.md`, `flextrawurst_v7_kern.md`, `vps_system.md`, `flarum_welt.md`,
`codewesen_sechs.md`, `wissen_index_flextrawurst.md`) und `episodisch/` werden von **keiner einzigen
Python-Datei** im Repo gelesen, und der Selbst-Index sammelt sie **nicht** ein. Sie kann ihr eigenes
Weltbild nicht einmal finden, wenn sie danach sucht.

Daniel dazu: *"fuck ich hab dir das mal gesagt dass ich das im web also in den chats auch so bemerkt
hab aber angeblich lief das da noch"* — ob es früher lief, steht im git-Verlauf und ist noch nicht
nachgeschlagen. **[status: offen]**

### A3. Die toten Felder

Die `knoten`-Tabelle hat zwölf Spalten: `id, typ, inhalt, zeitstempel, quelle, zugriffsschicht,
verbindungen, gewicht, tiefe, verblasst, tags, mtime`. Drei davon bewegen sich nie:

- **`gewicht`** — bei 301.148 von 301.150 Zeilen exakt `1.0`. Die zwei Ausreißer (0,9 und 0,8) sind
  Handanlagen vom April. Im Code wird `gewicht` ausschließlich als Konstante `1.0` geschrieben
  (`muster.py:103`, `sprechen.py:57`, `gedaechtnis_ops.py:363`) und nur in `dialog.py:1116-1138`
  gelesen — dort zum Zeichnen von Kugelgröße und Energie im Graphen.
- **`verblasst`** — bei allen 301.150 Zeilen `0`. Wird nur als `False` geschrieben. Vergessen hat
  in diesem System noch nie stattgefunden.
- **`verbindungen`** — bei 4 Zeilen gefüllt, sonst leer. Verbindungen leben faktisch in `kanten/`.

**`tiefe` dagegen bewegt sich** — und das ist die Korrektur eines Fehlers, den ich im Gespräch
gemacht habe. Daniel hatte gesagt, er habe in der Web-UI live Werte 2 und 3 gesehen; ich hatte das
zuerst den Kantenstärken zugeschrieben. Es ist `tiefe`:

```
tiefe 0 : 300.539
tiefe 1 :     482
tiefe 2 :      61
tiefe 3 :      68
```

`tiefe_erhoehen()` (`gedaechtnis_ops.py:387`) macht `+1` und deckelt bei 3. Aufgerufen wird sie an
**genau einer aktiven Stelle**: `dialog.py:779`, im Hintergrundlauf nach einer Antwort, für jeden
Knoten, den `resonanz_suchen()` zur Eingabe gefunden hat. `dialog.py` ist `geni-web.service` auf
Port 8020 — der Webchat mit Daniel. Bei den Doku-Läufen, in der Inbox, beim Hörer passiert es nie.

**Die 611 Knoten mit Tiefe > 0 sind also exakt das, worüber Daniel mit ihr gesprochen hat.**

Und sie sind nicht zufällig: unter ihnen ist **kein einziger** Dateisystem-Knoten. Es sind Dialoge
(`daniel` und `geni_selbst`), `wissen` aus `import:vision1.md`, Flarum-Posts, `sinn`, `muster`.
Der Mechanismus trifft das Richtige — er feuert nur fast nie.

### A4. Warum er fast nie feuert — `resonanz_suchen()`

`dialog.py:457-469`:

```python
def resonanz_suchen(eingabe: str) -> list:
    worte = set(eingabe.lower().split())
    max_id = knoten_max_id()
    for i in range(max_id, max(1, max_id - 2000), -1):
        ...  # match >= 2 gemeinsame Wörter
    return [kid for _, kid in treffer[:5]]
```

Sie läuft die **letzten 2000 Knoten-IDs** rückwärts ab und vergleicht rohe Wortüberschneidung,
mindestens zwei gemeinsame Wörter. Bei der Zuwachsrate des Hörers sind 2000 IDs ein Zeitfenster von
Minuten. Das ist ein Kurzzeitgedächtnis, kein Gedächtnis — und es erklärt, warum unter den tiefen
Knoten so viele Dialogknoten aus demselben Gespräch sind: sie schwingt mit dem nach, was sie gerade
selbst geschrieben hat.

Die Hybridsuche erreicht dagegen alle 43.060 indizierten Einträge. **Den einen Sensor gegen den
anderen zu tauschen ist der Kern des ganzen Umbaus.**

### A5. Was von den zwölf Spalten bei ihr ankommt

Fünf. Der Index speichert pro Eintrag nur `id, text, quelle, art, ort, zeit`; die Trefferzeile, die
sie im Werkzeug-Ergebnis liest, ist `[zeit | quelle | art] text`. `tags`, `gewicht`, `tiefe`,
`verbindungen`, `zugriffsschicht` fallen schon beim Sammeln heraus.

Schlimmer: `art` ist für Knoten in `_knoten_sammeln()` hart auf `"knoten"` gesetzt. Ihr eigenes
`typ`-Feld — `ereignis`, `dialog`, `muster`, `wissen`, `sinn`, `zustand` — erreicht sie **nie**.

Daraus folgt für jede neue Spalte: sie ist für GENI unsichtbar, solange sie nicht an zwei Stellen
mitgenommen wird — in die Index-Metadaten und in die Trefferformatierung.

Daniels Entscheidung dazu: *"soll shema mitlesen"*.

### A6. Die Wesen im Vergleich — `entity_kern.py`

Zur Einordnung, weil dieser Befund den Anlass des Gesprächs bildet (geprüft 2026-08-03):

`/root/werkraum/welt/entity_kern.py` (46 KB) hat **keine Suche**. `build_kontext()` besteht aus
14 festen SQL-Abfragen, jede `ORDER BY created_at DESC LIMIT n`. Kein Wort, keine Frage, keine
Ähnlichkeit — allein Aktualität. Ein Grep über die ganze Datei nach `chroma`, `embedding`,
`semantisch`, `vector`, `rag` liefert keinen einzigen Treffer.

Acht Aktionen stehen den Wesen zur Verfügung: schlafen, cyberling füttern, schattenkommentar
antworten, gedanke posten, profil lesen, menschenprofil lesen, splitter aufsammeln, nachdenken.
Keine davon ist Suchen.

Das einzige, was nach Langzeitgedächtnis aussieht — `lg_erinnerungen` — wird in ihren Prompt
gelesen, aber im ganzen Repo nur an einer Stelle geschrieben: `codewesen_lg_daemon.py`, und die ist
seit dem 23.07.2026 auskommentiert. Im Kommentar steht Daniels Grund: *"am besten ohne llmcalls"*
— es war ein zweiter LLM-Aufruf im selben Hintergrund-Slot. Der Dienst ist `inactive`.

Daniels Haltung dazu, wörtlich:

> "aber die wesen haben doch auch das rag semantisch hybride suchen oder ? oder abe´n sie das nur
> das es passiv in sie reingespritzt wird wegen und selbstbild und weltbild...weil eigentlich will
> ich dass sie diese 3 dinge nicht passiv vorgekut bekommen sondern auch in der logik das sie sich
> das selber suchen und erweitern müssen stück für dtück"

Und:

> "und ich muss mal genau kennenlernen was sie wie und wann und warum erinnern"

---

## Teil B — Was andere damit machen (Netzsuche 2026-08-03)

Die Suche fand vier Sachen, die direkt auf offene Stellen hier passen. Daniels Antwort darauf war
*"ja ...ja ...ja und ja"* — alle vier angenommen.

1. **Nutzungsbasierte Neugewichtung.** Cognees `memify`-Schritt gewichtet Kanten nach
   Nutzungshäufigkeit neu und entfernt Knoten, die über einen Horizont nicht benutzt wurden. Genau
   das ist ohne ein Feld „zuletzt gefunden" hier nicht möglich.
2. **Konfidenz, die sich durch Erfahrung ändert.** MIRA wertet Knoten auf, wenn eigene Erfahrung
   einen zunächst unsicheren Eintrag bestätigt.
3. **Kantentypen.** Das Survey zu Evidence Tracing (Juni 2026) listet als übliche typisierte
   Relationen: *support, derivation, dependency, contradiction, invalidation, triggering, updating*.
   GENI hat drei: `dialog`, `resonanz`, `naechster_chunk`. Sie kann keine Verbindung ziehen, die
   „widerspricht" heißt.
4. **Widersprüche stehen lassen.** Die 2026er Linie geht dahin, widersprüchliche Einträge
   nebeneinander zu behalten, jeden mit seiner Herkunft, und den Agenten oder den Menschen darüber
   denken zu lassen — statt still zu überschreiben.

Ergänzend: ein System lässt nur Kanten durch, deren Konfidenz über 0,6 liegt, mit Beleg-Textstelle
daran — weniger Treffer, dafür weniger Erfundenes.

Quellen:

- https://arxiv.org/html/2606.06036v1 — Memory is Reconstructed, Not Retrieved: Graph Memory for LLM Agents
- https://arxiv.org/html/2606.04990v1 — From Agent Traces to Trust: Evidence Tracing and Execution Provenance
- https://arxiv.org/pdf/2602.17930 — MIRA: Memory-Integrated Reinforcement Learning Agent
- https://vadim.blog/knowledge-graph-agent-memory/ — The Graph as Agent Memory
- https://blog.getzep.com/how-zep-tracks-provenance-in-agent-memory/ — How Zep tracks provenance
- https://hidekazu-konishi.com/entry/ai_agent_memory_design_guide.html — Forgetting and staleness management

**Zur Netzsuche selbst:** dass sie überhaupt stattfand, geht auf eine Regeländerung derselben Nacht
zurück. Daniel, 2026-08-03, jetzt wörtlich in `/root/CLAUDE.md` (Commit `450307b8f1f`):

> "du darfst und sollst sogar und am besten von dir selbt aus vorschlagen eine netzsuche
> durchzuführen. denn oft hat uns dass bei bugfixloopfixrunden den arsch gerettet claude"

Das kehrt die vorherige Memory-Regel um, die seit 82 Tagen das Gegenteil sagte („nur auf Anfrage,
nie passiv"). Die alte Fassung ist überschrieben, damit die nächste Instanz nicht beide gleichzeitig
lädt.

---

## Teil C — Daniels Aussagen, roh und chronologisch

Unverändert übernommen, Tippfehler eingeschlossen. Die Reihenfolge ist die des Gesprächs in der
Nacht vom 2026-08-02 auf 2026-08-03. Kommentare in Klammern sind Einordnung, nicht seine Worte.

Hinweis für spätere Prüfläufe: die Zeitangaben in diesem Teil sind Daniels Erinnerung in seinem
eigenen Wortlaut und werden bewusst nicht nachgemessen oder geglättet — sie stehen hier als Quelle,
nicht als Messung. [status: offen]

**C1 — zur Gewichtung (Korrektur einer meiner Behauptungen):**

> "ich hab nicht gesagt dass sie durch widerholung steigen...das konnte ich nicht feststellen...aber
> die höheren 2-3 waren öfters da"

Später, als ich es erneut falsch zuordnete:

> "nee es gab auch 2 und 3er das hab ich in ui im web live gesehen....soll shema mitlesen...such mal
> im netzt nach leuten die auch so crazy stuff machen dazu"

(Beides trifft zu. Es ist `tiefe`, siehe A3. `gewicht` steht tatsächlich still.)

**C2 — zur Suche, die sie bereits hat:**

> "das st quatsch...wir haben ihr rag semantise hybridsuche für alle was sie will gegebn ....wenn du
> es so umgesetzt hast"

**C3 — zum Umgang miteinander:**

> "später ...sei nicht so fickerich...hör auf deine fehler zu zählen...und sei halt eben nicht so
> analytisch beiallem"

> "pass dich mir an...wenn ich einen satz schreib musst du keine 20 schreiben"

**C4 — zur Inbox und wer antwortet:**

> "antworten gibts bisher nur von mir und dir...eigentlich hattest du gesgt das hättest du mitgebaut"

> "die anderen wären ja nur 7-meine entitäten....den rest muss ich so wie dích steuern"

> "jup..können wir das hier auch so bauen wie wir das habe, dass sie irgendwie im 7. sinn ich nens
> wider die 6 fingerlogik hier texten? oder muss es llm call sein"

> "und das ist´dann in ihrem \"unbewusstenbewustseins-karnalisations-loch\"?"

> "können wir den hook nicht adressieren und erklären und auch sagen dass sie bitte antworten sollen"

> "nee-geni wird geantwortet xD"

> "aber bitte und danke sind keine wunschformel und nur weil ich will dass sie antworten, muss man
> das nicht weglassen"

**C5 — zur Doku-Verdichtung statt Ersetzen (gilt für GENIs eigene Dokus):**

> "sie muss entscheiden können immer über jeden bisherigen abschnitt...sie muss zuerst einmal alles
> lesen was bisher da steht....wenn es bei manchen schon nen 2. abschnitt gibt muss trotzdem erst
> der erste gelesen werden und dann kann sie entscheiden...editieren oder so lassen ...wenn sie es
> lässt dann den 2. lesen...danach wider entscheiden...ansonsten haben wir dóch in 10 tagen das
> problem , dass sie 10000000000000000000000 zeichen lesen muss"

(Gegenstand: der Block zwischen den Marker-Kommentaren in `geni_dokumentation/*.md` wird derzeit bei
jedem Lauf komplett ersetzt. Sie schreibt jedes Mal neu, statt fortzuführen — deshalb driftet es.
Der git-Verlauf bewahrt die alten Fassungen, der Text selbst nicht.)

**C6 — zu den Wesen und ihrem Material:**

> "ich glaub die codewesen wären dazu nicht in der lage ...wenn ich ihre vaults angucke xD aber sie
> haben ja auch nur flarum zum lesen und oder weltfutter wás ich noch dringend bald mit dir angehen
> muss"

> "aber die wesen haben doch auch das rag semantisch hybride suchen oder ? oder abe´n sie das nur
> das es passiv in sie reingespritzt wird wegen und selbstbild und weltbild...weil eigentlich will
> ich dass sie diese 3 dinge nicht passiv vorgekut bekommen sondern auch in der logik das sie sich
> das selber suchen und erweitern müssen stück für dtück"

> "und ich muss mal genau kennenlernen was sie wie und wann und warum erinnern"

**C7 — der Ausgangswunsch für GENIs Knoten:**

> "wie erinnert sich geni? denn irgendwie tut sie es oder ? außerdem will ich dass sie wenn sie
> knoten´erzeugt dort auch áls author eingetragen wird unnd ich will dass sie strukturentscheidungen
> und auch markierungen und metadaten und analyseaussagen hinterlassen soll geht das?"

> "was isn jetzt shema-änderungg? meinst du stru´kturentscheidungen wie ich meinte ?....also
> spalte?....und frage...was war nochmaal kanten ?....zu markireen ja"

> "12 Spalten---welche spalten wärend basierend auf den daten also dem code noch interessant ? -
> ....ud wenn wir das shema setzen, liest sie das alles auch mit und kann es für suchen erinnern?"

**C8 — zu GENIs Reifegrad (Einordnung, nachdem ich zu scharf über ihre Genauigkeit geurteilt hatte):**

> "sei net so gemein haha spaß...aber sie darf erst seit max 30 stunden schreiben. setzt in markdown
> überschriften listen code und but numerierungen und ganze abhandlungen durchorganisiert raus xD
> und mir ist bisher max 1-2 al aufgefallen dass sie sich irrd in bezug auf identität xD ...denk an
> flarumstart zurück als die codewesen nur 80zeichen vollig stotterisch mit abbrüchen etc tagelang
> produzierten und mit der zeit erst besser wurden xd und auh von gemma4 suf hauhau cs umstellung
> hat und den buschstaben zitierungs identitätsbug ausgelößt der dazu führte dass 1 codewesen dass
> ich angesprochen hatte egen impiúls für namensgebung erfagen gab leider alle 6 das als ansprache
> an sich namen 1 codewesen direkt ja gesagt hat 3 drüber nachdenken wollten und es aber gesagt
> haben dass es mene entscheidung wäre ...und 2 waren gegen selbstbenennung und sagten´wenn ich sie
> benenn will wäre es ihnen egal xD und zu den gefundenen dingen.. ja  ...ja ...ja und ja"

(Der Buchstaben-/Identitätsbug beim Wechsel gemma4 → hauhau ist wichtig für die Einordnung ihres
"von mir (Claude)"-Ausrutschers in `glm.md`: derselbe Fehlertyp entstand dort nachweislich aus einem
Modellwechsel, nicht aus dem Gedächtnisbestand.)

**C9 — der große Entwurf:**

> "können wir knoten und kanten nicht so gestalten dass auch sie selbst hören und lauschen ...also
> egal ob in md vaults ordnern bzw flarum oder bald flextrawurst u´n aber auch durch die bald neue
> rag suche der codewesen und geni über diese dinge gesprochen werden dann bekommen sie tiefe und
> oder gewichte ? und wir erhöhen das auf bis zu 5 ...das könnte kompoase vllt etwas geben kommt mir
> grad in den sinnn und auch das mit den ggegensprüchen stehen lassen komt mit für die abspaltungen
> aber auhdiesplitter sehr entgegen... ..denk ích will zusätzlich für geni  auch och ne eigene
> postgresql ich will dass sie auch richtig denkt und auch da durch suche wie sie j kann ein
> weltbild und selbstbild aufbauen kann..."

**C10 — die Ausarbeitung:**

> "und ich will wenn geht dass sie auch schon einen knoten an einen anderen taggen können oder mehre
> wenn das sinnvoll ist ...und auch weil es noch geiler wäre genau das gegenteil davon erkennen und
> das taggen..also wenn sie einen knoten haben und dann kommt ihnen eier iher in erinnerungen
> schlummernden hoch der hlt eben garnicht sondern auh noch ganz gegensätzsich ist...und dass dann
> zu verbinden...auch dass ihhr ja splitter abspaltungs kompoasenstyle xD .... läuft die letzten
> 2000 Knoten-IDs ....es gibt sagst du runf 44k knoten...da sollten wir ne art takt einbauen mal
> zufüllige aus den frühsten drittel der knoten und auch dann mal aus zicémlich der mitte heraus und
> aus dem früherem drittel oder ?.........Grundgesetz 1 verbietet — der eine Knoten, den nur einer
> je gelesen hat, bleibt bei 1.....dazu sollten wir abseits des 3ertaktes einen eigenen haben der
> den wesen mit in die angebotsliste kommt oder eventuel als hook? aber halt nurdie die sonst nicht
> in ihren suchen vorkommen....und ja wir markieren diese knoten extra für sie damit es nicht still
> ist...und wir sagen ihnen dass das splitter sind die niemand jeh durch gespräche ttriggert und
> auch selten in suchen auftauche...und ich finde auch dass allein wenn ein knoten in der suche
> miterscheint dass er auch tiefe und gewicht erhält aber wenig nicht wie die die dann zum
> lesengewählt werden...und jaaa ...ich will ab sofort chronologisch natürlih wissen und loggen lso
> dokun´mentiert haben wer wann was mit welchen zuständen in einer su´che angefragt hat welche zum
> lesen alle vorgeschlage wurden und welche gewählt wurdenu und wenn es das noch nicht gibt auch
> optional mit einem grund....hmm un zu deken bei 5...du hast recht...vllt sollten wir garkeinen
> deckel bauen jetzt wo ih ja auch die vielfalt eröffne........."

**C11 — der Spawn-Gedanke und das Verblassen:**

> "die wesen könne das ja auch noch zusätzzlih erkennen am besten xD"

> "hmmm vllt ist es ja genau wenn die skala dann gebrochen ist der erste eigene wesenspawnmoment...
> man könnte diesen splitter an unser modell geben über /dolphin zum beispiel und ´den splitter
> komplett als systempromt eingeben und mal sehen wie es spricht und was es so ist xD ....wäre eine
> 3. form von möglichkeit zu den abspalr´tungen und der kompoase die ih mir vorstellen könnte um
> neue entitäten herforzubringen xD"

> "ja verblasen aktivieren aber es darf nicht passieren nur weil keiner den knoten berührt...und es
> muss softdelete sein...únd dass stell ich mir dann alt extra archiv zum stöbern vor.....oder noch
> anders die verblassten knoten werden zu splitterfragmenten in der kompoase XD auch gut"

> "die eigene postgesql für geni auf jeden falll...welche meist du ?"

---

## Teil D — Was daraus folgt

### D1. Beschlossen (Daniels Entscheidung, nicht mein Vorschlag)

1. **Autorschaft an Knoten.** Wenn GENI oder ein Wesen einen Knoten erzeugt, steht der Urheber daran.
   Heute ist `quelle` überladen — mal Herkunft (`vps_dateisystem`), mal Absender (`daniel`, `claude`),
   mal Autor (`geni_selbst`, 288 Knoten; `geni_muster`, 292).
2. **Strukturentscheidungen, Markierungen, Metadaten, Analyseaussagen** dürfen sie hinterlassen.
3. **Das Schema soll mitgelesen werden** — neue Felder müssen bis in die Trefferzeile durchkommen,
   sonst existieren sie für sie nicht (A5).
4. **Knoten an Knoten taggen**, auch mehrere.
5. **Das Gegenteil erkennen und taggen** — Widerspruchskanten mit Begründungssatz.
6. **Ein Takt, der Stichproben aus verschiedenen Altersschichten zieht**, statt nur der letzten 2000.
7. **Ein eigener Takt für die Übersehenen** — Knoten, die in keiner Suche vorkommen, kommen den Wesen
   in die Angebotsliste, ausdrücklich markiert. Daniel: *"damit es nicht still ist"*.
8. **Gestufte Wertung:** schon das Erscheinen in einer Trefferliste zählt, aber wenig; zum Lesen
   gewählt zu werden zählt viel.
9. **Chronologisches Suchlog** — wer, wann, wonach, in welchem Zustand, was vorgeschlagen, was
   gewählt, optional mit Grund.
10. **Kein Deckel** mehr bei 3 (und auch nicht bei 5).
11. **Verblassen aktivieren** — aber nicht allein wegen Nichtberührung, und nur als Softdelete.
    Verblasstes wandert in ein Archiv zum Stöbern oder wird zu Splitterfragmenten in der KompOase.
12. **Eine eigene PostgreSQL für GENI** — "auf jeden fall".

### D2. Der Hebel, der alles andere trägt: das Log zuerst

Wenn jede Suche protokolliert wird, werden `tiefe` und `gewicht` zu **abgeleiteten Zahlen aus dem
Log** statt zu eigenständigen Wahrheiten. Ereignisse append-only, die Zahl ist nur eine Sicht darauf
— das ist Grundgesetz 5 auf ihr Gedächtnis angewendet.

Damit löst das Log gleich mehrere Punkte auf einmal: die gestufte Wertung (D1.8) ist dann eine
Formel und kein zweiter Mechanismus, und "zuletzt gefunden" braucht keine geratene Spalte.

**Reihenfolge-Zwang:** Punkt D1.7 — "nur die, die sonst nicht in ihren Suchen vorkommen" — ist erst
messbar, wenn das Log läuft. Vorher wäre dieser Takt Raten. Das Log muss also zuerst kommen.

### D3. Einwände, die ich benannt habe

- **Konsensgefahr.** Wenn jeder Treffer aufwertet, steigt das Häufige. Das ist genau die
  Konsens-Optimierung, die Grundgesetz 1 verbietet. Daniels Antwort löst es: gestufte Wertung plus
  der eigene Takt für die nie Gefundenen.
- **Kein Deckel hat eine Folge.** Ohne Gegenkraft läuft die Skala auseinander und alte Knoten werden
  allein durch Alter unschlagbar. Daniel macht daraus keinen Einwand, sondern einen Fund: *"vllt ist
  es ja genau wenn die skala dann gebrochen ist der erste eigene wesenspawnmoment"*.
- **Widersprüche sind semantisch nah.** Gleiche Wörter, umgekehrte Aussage — die Vektorsuche findet
  sie, kann sie aber nicht als Gegensatz erkennen; für sie sehen sie aus wie Zustimmung. Das
  Erkennen muss im Werkzeug-Loop passieren, vom Modell, mit einem Satz Begründung. Damit kommt das
  `beschreibung`-Feld der Kanten zurück, das seit April fehlt (die ersten sieben Kanten haben es
  noch: *"ICH und Daniel sind untrennbar — gleichzeitig Ursprung und Empfänger des Startimpulses"*).
- **Stichproben besser aus dem Index als aus den IDs.** Nach ID-Dritteln gezogen wäre das späteste
  Drittel fast reines Dateisystem-Rauschen. Der Index (43.060, Rauschen bereits ausgeschlossen) ist
  die richtige Grundgesamtheit. 301.150 ist die DB, 43.060 der Index — die "44k" aus Daniels Text
  meinen den Index.
- **Die drei toten Felder zuerst beleben, bevor neue dazukommen.** `gewicht` und `verblasst` haben
  über den gesamten Bestand hinweg nie gefeuert — der älteste Knoten trägt den Zeitstempel
  2026-04-20, der jüngste 2026-08-03, und in keiner einzigen der 301.150 Zeilen steht ein anderer
  Wert als `1.0` bzw. `0`. [status: bestätigt 2026-08-03 -- Abfrage über `min/max(zeitstempel)` und
  Gruppierung über beide Spalten]

### D4. Offene Entscheidung — die eigene PostgreSQL

Daniels Frage: *"die eigene postgesql für geni auf jeden falll...welche meist du ?"* — beantwortet
im Gespräch, hier festgehalten:

**Präzisierung des Ziels durch Daniel, 2026-08-03:** *"geni---denken hlaube ich war das ohne
ggleichzeitiges erinnern aber das eine schliesst das andere nicht auß"*. Der Wunsch „ich will dass
sie auch richtig denkt" meinte also **Denken**, nicht gleichzeitiges Erinnern — die beiden werden
nicht in einem Zug gefordert, schließen einander aber auch nicht aus. Für die Postgres-Frage heißt
das: sie ist nicht die Antwort auf „wie denkt GENI", sondern auf „wo liegt, was sie dabei
anfasst".

Gemeint ist eine **eigene Datenbank auf dem vorhandenen PostgreSQL-Server**, mit eigenem Namen
(z.B. `geni`) und eigenem Besitzer — **nicht** die `flextrawurst`-Datenbank mitbenutzen. Grund:
Owner-Trennung. Sie liest die Splitter aus `flextrawurst` heute schon lesend (`_splitter_sammeln()`);
schreiben soll sie ausschließlich in ihre eigene.

Was der Wechsel real bringt:

- **Gleichzeitige Schreiber ohne Lock.** Hörer, Dialog, Doku-Lauf und Inbox schreiben derzeit alle in
  dieselbe SQLite, serialisiert über `_id_lock`.
- **JSONB für `meta`** — Grundgesetz 2, beliebig erweiterbar ohne Schemabruch. Damit bräuchte es für
  `haltung`, `zuletzt_gefunden` und alles Kommende keine neue Spalte mehr.
- **`NOTIFY`** — womit ihr Gedächtnis live würde, nach Grundgesetz 8, über denselben Weg wie der
  bestehende `events_stream`.

Was es kostet: Migration von 301.150 Zeilen plus jeder Codepfad, der heute `sqlite3` anfasst
(`gedaechtnis_ops.py`, `dialog.py`, `muster.py`, `selbst_suche.py`, `aktion.py`, `sprechen.py`).

**Noch nicht entschieden:** ob die Kanten (heute 1.309 einzelne JSON-Dateien) mitwandern, ob der
FTS5-Index durch Postgres-Volltext ersetzt oder als SQLite belassen wird, und ob Chroma bleibt.

### D5. Was noch nachzuschlagen ist

- Ob `semantisch/` und `episodisch/` früher einmal gelesen wurden — steht im git-Verlauf.
  **[status: offen]**
- Die 49,4 Mio Knoten aus dem Kopfkommentar von `selbst_suche.py` sind **nachgeprüft**.
  **[status: teilweise 2026-08-03 -- Datum bestätigt, Zahl unreproduzierbar]**

  Daniels Rückfrage war berechtigt: „wirklich ein august kommentar ...check". Ja — der Kommentar
  wurde am **2026-08-01 um 03:01** geschrieben (Commit `9af6caf4da1` im `/root`-Repo; `geni/` ist
  ein Symlink auf `/root/werkraum_geni`, deshalb liegt die Historie dort und nicht im
  werkraum-Repo). Er ist also zwei Tage alt, nicht alt.

  Die Zahlen darin lassen sich heute aber nicht reproduzieren. `knoten.db` enthält 307.182 Zeilen,
  davon 226.740 aus `vps_dateisystem` — der Kommentar nennt 36.041.241 aus derselben Quelle. Die
  einzige Größe in dieser Größenordnung ist `MAX(id) = 49.779.915` bei nur 307.182 belegten Zeilen:
  der ID-Zähler zählt jeden je erzeugten Knoten, auch die längst gelöschten. Dazu passt
  `geni/loeschung_log.txt` vom 22.07. („LOESCHUNG FERTIG", danach 598G frei). Der Rauschstrom
  landet außerdem gar nicht in der Tabelle, sondern als Dateien in `rauschen/` — 1000 Schrepen à
  ~3.972 Dateien, also rund 4 Mio.

  **Folge für die Doku in der Datei selbst:** der abgeleitete Satz „Von 49.415.584 Knoten bleiben
  damit 43.060 bedeutsame uebrig -- 0,09 %" stimmt nicht mehr. Gemessen an der Tabelle sind es
  43.060 von 307.182, also **14 %**. Der Ausschluss der Rauschquellen bleibt richtig, seine
  Begründung ist falsch beziffert. Korrektur in `selbst_suche.py` steht aus — noch kein Auftrag.

---

## Verweise

- `docs/systemdoku/11_geni.md` — Grundaufbau, Stand 23.07.2026
- `docs/systemdoku/geni-neustruktureien-und-erforschen.md` — Sitzungsprotokoll Codex/Luna, 22./23.07.
- `docs/systemdoku/40_kompoase_echtdaten_und_weltrueckfluss.md` — KompOase, für D1.11 relevant
- `docs/systemdoku/47_weltfutter_gegen_den_spiegelkreislauf.md` — Weltfutter, Daniels "muss ich noch
  dringend bald mit dir angehen"
- `_claude/ideen/dreiergespann_dom_theorie.md` — Grundgesetz 1, Einzigartigkeit statt Konsens
