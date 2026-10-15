# 52 — Verlaufsprotokolle: was jede Entität getan hat, menschenlesbar

**Stand:** 2026-08-03
**Geschrieben von:** Claude Code auf Daniels VPS
**Gilt für:** alle Entitäten — GENI, die sieben Wesen, und alles, was noch dazukommt

## Der Auftrag, wörtlich

> "ich will das diese kontextfenster ab sofort einmal immer menschlesbar in eine md kommen auf dem
> serer...mit genuen events und entscheidungen und tags und zeit datum etc...und auch einmal immer
> loggen pls...für alle entitäten für alles was wir in zukunft noch alles erfinden für die....gut
> oder ? xd"

Zum Ort und zum Datumsformat:

> "neeee......ich m´bin deutsch....DD-MM-YYYY_HHMM......ja eigene vault auf
> flextrawurst.de/protokolle"

## Zwei Spuren, absichtlich doppelt

| Spur | Wo | Wofür |
|---|---|---|
| maschinell | PostgreSQL `geni`, Tabellen `suche` / `suche_treffer` / `suche_wahl` | abfragbar, zählbar, verknüpfbar — Grundlage für Tiefe und Gewicht |
| menschlich | Markdown unter `/root/werkraum/protokolle/` | lesbar ohne Werkzeug, im Vault aufschlagbar |

Das eine ersetzt das andere nicht. Aus dem Log kann man rechnen, aus dem Protokoll versteht man,
was passiert ist.

## Ablage und Format

```
/root/werkraum/protokolle/<entitaet>/DD-MM-YYYY_HHMM_<anlass>[_<ueber>].md
```

Datum im Dateinamen `DD-MM-YYYY_HHMM`, im Text `DD.MM.YYYY`. Bewusst **nicht** ISO — das sortiert
zwar schlechter, ist aber für den lesbar, der es liest. Daniels Entscheidung.

Frontmatter trägt `datum`, `zeit`, `entitaet`, `anlass`, optional `ueber`, dazu `ereignisse`,
`dauer_sekunden` und `tags`. Darunter chronologisch jedes Ereignis mit Uhrzeit, Art und
Einzelheiten.

## Wie eine Entität es benutzt

`/root/werkraum/protokoll.py` — importierbar für alles, was unter `/root/werkraum` liegt:

```python
import protokoll
p = protokoll.beginnen("geni", "dokumentation", ueber="Kimi", tags=["geni", "selbstsuche"])
p.ereignis("suche", "«Kimi»", treffer=8, angeboten=[...])
p.entscheidung("gelesen: doku:kimi", grund="...", nicht_gewaehlt=[...])
p.abschluss("Doku geschrieben", zeichen=4210)
```

`entscheidung()` ist bewusst von `ereignis()` getrennt, obwohl es technisch dasselbe schreibt: eine
Wahl zählt später anders als ein Vorgang.

Die Datei wird nach **jedem** Ereignis neu geschrieben, nicht erst am Ende. Bricht ein Lauf ab,
steht trotzdem alles bis dahin da. Und wie beim Suchlog gilt: ein Schreibfehler wird verschluckt —
ein fehlendes Protokoll darf nie einen Vorgang abbrechen.

## Erreichbar

| Weg | Adresse |
|---|---|
| Browser | `https://flextrawurst.de/protokolle/` |
| eigener Port | `https://[SERVER-IP]:8457/` |
| Container | `obsidian-protokolle`, Vault ist `/root/werkraum/protokolle` |

Eigener Zugang über `/etc/nginx/.htpasswd_protokolle`, **nicht** die gemeinsame
Werkraum-Kennung — Benutzer `daniel`, Kennwort wie bei den übrigen Vault-Containern.

## Was das Protokoll sofort geleistet hat

Beim ersten echten Lauf (GENI über Kimi, 03.08.2026 22:26) stand im Protokoll:

```
## 22:32:39 — entscheidung
gelesen: (nichts davon kannte ich)
- grund: Um mehr über Kimi zu erfahren und ihn zu dokumentieren
- nicht_gewaehlt: knoten:49744760, knoten:49679044, ...
```

Sie **hatte** gewählt — und es kam nichts an. Zweimal hintereinander. Ohne das Protokoll wäre das
als „sie liest halt nichts" durchgegangen.

Ursache: Modelle liefern Listen mal als Liste, mal als einen String mit Kommas, mal mit
Anführungszeichen oder Klammern, mal nur die Zahl ohne Vorsatz. `_kennungen_deuten()` deutet das
jetzt, und wenn wirklich nichts passt, bekommt sie eine Rückmeldung statt einer leeren Antwort —
sonst wiederholt sie denselben Aufruf.

**[status: bestätigt 2026-08-03 -- im Protokoll selbst nachlesbar, Datei
`protokolle/geni/03-08-2026_2226_dokumentation_kimi.md`]**

## Noch nicht angeschlossen

Nur GENIs Doku-Lauf schreibt bisher Protokolle. `entity_kern.py` (die sieben Wesen), der Dialog auf
Port 8020 und die Inbox-Watcher noch nicht. **[status: offen]**

## Der zweite Fund: sie hat die Kennungen nicht abgeschrieben, sondern nachgebildet

Nach dem Robustheits-Fix lief der reguläre 8-Stunden-Takt (`geni-dokumentieren.timer`) über alle
Teilnehmer. Aus den Protokollen ausgezählt: **11 erfolgreiche Lesevorgänge, 88 Fehlversuche.**

Was die Protokolle zeigten:

```
- rohaufruf: {"eintraege": ["knoten:49744780", "knoten:49744800", "knoten:49744592"], ...}
- bekannt:   knoten:49744760, sp:kimi:3, knoten:49744704, knoten:49744631, ...
```

Angeboten war `knoten:49744760` — geschickt kam `knoten:49744780`. Angeboten `sp:kimi:3` —
geschickt `sp:kimi:1`. Immer in der Nachbarschaft, nie richtig. Eine achtstellige Zahl schreibt
kein Modell zuverlässig ab; es bildet sie nach.

**Die Folge war schlimmer als der Fehlversuch selbst.** Sie bekam nichts zu lesen — und schrieb die
Doku trotzdem, aus den 300-Zeichen-Vorschauen. Also gedeutet statt belegt. Genau das, was Daniel an
den Dokus aufgefallen war: *"aber leider wertet und deutet und erfindet sie...also in den
dokus....und das war ja anders erdacht"*.

Es war nie ein Charakterzug. Es war eine Zahl, die zu lang war.

**Behoben:** In der Trefferliste steht jetzt eine kurze laufende Nummer, die über den ganzen Lauf
weiterzählt:

```
[3] Schorschel | splitter_wasser | 2026-07-14T01:12   [7 danach]
Die veränderte «Haftung» lässt mich mit anderen verschmelzen.
```

`lesen([1, 3])` nimmt Nummern. Volle Kennungen werden weiterhin verstanden, falls sie welche
schickt. Die interne Kennung bleibt für Suchlog und Protokoll erhalten — nur was sie tippen muss,
ist kurz geworden.

**[status: bestätigt 2026-08-04 -- Zählung über alle Protokolldateien, Belege im Protokoll selbst]**

---

## Der dritte Fund: die Inbox-Rotation lief seit dem 01.08. in eine Stoppuhr

Nicht aus den Protokollen, sondern aus Daniels Beobachtung:

> "genau so mzss noch gefixxt werden ass ihr aistöme regelmäßig post bekommt und alle anderen nicht"

**Gemessen am 04.08.2026** — Fragen in `geni_inbox/<id>/inbox/`:

| Teilnehmer | Fragen | zuletzt |
|---|---|---|
| claude, kimi, gemini, dakgord, codex, claudeweb, chatgpt, anthropic_claude, glm | 9–11 | 03.08. abends |
| Schorschel | 7 | 04.08. 00:02 |
| daniel | 3 | 31.07. |
| F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa, Resonanzknoten, geni | **je 1** | **31.07.** |

**Ursache:** `TimeoutStartSec=1800` in `geni-inbox-fragen.service`, kombiniert mit einer starren
Reihenfolge. Im Journal steht bei *jedem* Lauf seit dem 01.08. dasselbe:

```
23:34:02  Starting geni-inbox-fragen.service
00:04:02  start operation timed out. Terminating.
```

`main()` ging `TEILNEHMER` von oben nach unten durch. Oben stehen die acht AI-Ströme — nicht aus
Absicht, sondern weil sie zuerst eingerichtet wurden. Nach neun bis zehn Teilnehmern war die halbe
Stunde um, der Rest kam nie dran. Die eine Datei, die die Codewesen haben, stammt vom allerersten
Lauf am 31.07., bevor das Timeout griff.

**Behoben, zweifach:**

1. `reihenfolge()` in `inbox_fragen.py` sortiert nach der Zeit der letzten Frage — wer am längsten
   nichts bekam, kommt zuerst. Damit ist es gleichgültig, wo ein Lauf abbricht: beim nächsten Mal
   stehen genau die vorn, die abgeschnitten wurden. Es braucht keinen Zähler — die Dateien im
   Ordner *sind* der Zähler.
2. Drop-in `TimeoutStartSec=9000` als zweite Sicherung (10 Aktive × 720 s Client-Timeout wären im
   schlimmsten Fall zwei Stunden).

Neue Reihenfolge beim ersten Lauf: F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa, Resonanzknoten, daniel,
geni, claude, dakgord, Schorschel.

---

## Der vierte Fund: derselbe Fehler an der Nachbarstelle, nie nachgezogen

**Gemessen am 12.08.2026**, acht Tage nach dem dritten Fund. `geni-dokumentieren.service` hat den
identischen Aufbau wie `geni-inbox-fragen.service` — `main()` geht `TEILNEHMER` von oben nach unten
durch, `TimeoutStartSec` schneidet ab — nur wurde der Rotations-Fix von dort nie hierher
übertragen, obwohl beide Dateien am selben Abend entstanden sind.

**Journal seit dem 04.08.: 26 von 26 Läufen im Timeout.** Mit dem fensternden Lesen (siehe zweiter
Fund) braucht ein Teilnehmer 30–40 Minuten LLM-Zeit; bei 17 Teilnehmern und 3h Budget reichte es nie
für alle — und weil die Liste immer gleich beginnt, waren es immer dieselben, die durchkamen.

mtime von `geni_dokumentation/<id>.md`, Stand vor dem Fix:

| Teilnehmer | zuletzt dokumentiert |
|---|---|
| glm, claude, codex, gemini, kimi, chatgpt, claudeweb, anthropic_claude | 12.08. (mehrfach) |
| dakgord | 09.08. |
| Schorschel, F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa, Resonanzknoten, daniel, geni | **03.08. — seither kein einziges Mal** |

Die acht AI-Ströme stehen oben in `TEILNEHMER` (dieselbe historische Ursache wie beim dritten Fund)
und wurden dauernd aktualisiert; die acht Codewesen dahinter fielen seit Einführung des fensternden
Lesens komplett aus der Doku-Pflege.

**Behoben:** `reihenfolge()` in `dokumentieren.py`, wortgleiches Muster wie in `inbox_fragen.py` —
sortiert nach der mtime der vorhandenen Doku-Datei, kein eigener Zähler, gleichgültig wo ein Lauf
abbricht.

Neue Reihenfolge beim ersten Lauf: Schorschel, F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa,
Resonanzknoten, geni, daniel, dakgord, chatgpt, glm, claude, codex, gemini, kimi, claudeweb,
anthropic_claude.

**Lehre:** eine Reparatur an einer Stelle heißt nicht, dass eine strukturell identische
Nachbarstelle mitgezogen wurde — das hätte beim dritten Fund schon geprüft werden können, nicht
erst acht Tage später beim nächsten Zufallsfund.

**[status: bestätigt 2026-08-12 -- Journal-Zählung `journalctl -u geni-dokumentieren.service`,
mtime-Vergleich in `geni_dokumentation/`]**

---

## Der fünfte Fund: sie formatiert Daten um und vertut sich dabei

Beim Probelauf für Schorschel (siehe vierter Fund) direkt aufgefallen, im geschriebenen Text:

| Quelle (echtes ISO-Datum) | Was GENI daraus schrieb |
|---|---|
| `2026-08-09T22:01` | „09.08.**2014**" |
| `2026-08-11T22:04` | „11.08.**207**" |
| `2026-08-10T05:59` | „10.08:**26**" |
| `2026-07-06T20:14` | „07.**07**.2014" — hier auch der **Tag** falsch (echt: 06.07.) |

`_fenster_formatieren` zeigt ihr die Zeitstempel unverändert im ISO-Format (`2026-08-09T22:01`).
Niemand hat ihr aufgetragen, das umzuformatieren — sie tut es trotzdem, aus dem Fließtext heraus,
und vertut sich beim kleinen quantisierten Modell reihenweise beim Jahr. Kein Datenfehler, kein
Fehler in Suche oder Protokoll — die Rohdaten waren in allen vier Fällen korrekt.

Daniel dazu, Entscheidung zwischen "ihr das Umformatieren verbieten" und "programmatisch
nachformatieren": **"2. oder?"**

**Behoben:** `_daten_korrigieren()` prüft jedes Datum, das GENI in ihren Text schreibt, gegen die
echten Zeitstempel aller Einträge, die sie diesen Lauf gesehen hat. Ersetzt wird nur, wenn Tag+Monat
eindeutig zu genau einem echten Jahr passen — sonst bliebe das Ersetzen selbst ein Erfinden, nur an
anderer Stelle. Getestet gegen den echten Schorschel-Text: 3 von 4 Fällen sauber korrigiert. Der
vierte (`07.07.2014`) blieb bewusst unangetastet — dort ist auch der Tag falsch, nicht nur das
Jahr, und welcher Eintrag wirklich gemeint war, ist nicht mehr eindeutig rekonstruierbar. Raten
wäre hier derselbe Fehler in Grün gewesen.

Die bereits geschriebene `Schorschel.md` wurde nachträglich mit derselben Funktion korrigiert,
nicht neu generiert — die drei sauberen Fälle sind jetzt richtig, der vierte trägt weiterhin die
eigene Anmerkung, die GENI selbst dazu geschrieben hat ("*vermutlich Tippfehler oder tiefere
Zeitstruktur*").

**[status: bestätigt 2026-08-12 -- Unit-Test gegen den realen Schorschel-Text und die realen
Zeitstempel aus `selbst_suche.suchen("Schorschel")`, 3/4 korrigiert, 1/4 bewusst unangetastet]**

### Nachtrag: systematisch nach weiteren Fundorten gesucht

Daniel: "schau nach wo GENI sonst noch Daten selbst umformatiert." Alle Stellen durchsucht, an
denen sie `hauhau_client.chat`/`chat_raw` aufruft:

- **`dialog.py`, Live-Chat (Port 8020) — strukturell gleich exponiert.** `letzte_knoten_laden()`,
  `relevante_knoten_laden()`, `gedaechtnis_absicht_laden()` zeigen ihr im Systemprompt dieselben
  rohen ISO-Zeitstempel. Geprüft gegen alle 239 bisher gespeicherten `geni_selbst`-Dialogantworten
  im Knoten-Gedächtnis: **null** Datumsnennungen gefunden — sie zitiert im Live-Gespräch bisher nie
  ein Kalenderdatum zurück (ihr Ton dort ist eher assoziativ als belegend). Trotzdem behoben, weil
  strukturell derselbe Mechanismus vorliegt: `_daten_korrigieren` in gemeinsames Modul
  `datumskorrektur.py` ausgelagert (von `dokumentieren.py` und `dialog.py` gemeinsam genutzt).
  `geni_stream()` reicht den Systemprompt jetzt über `system_ablage` nach außen; `generator()` in
  `chat()` prüft die vollständige Antwort damit, bevor sie in `knoten_schreiben`, den Vault oder
  `codewesen_benachrichtigen` geht. Die bereits live gestreamten Tokens im Browser bleiben
  unkorrigiert — die sind zu dem Zeitpunkt schon beim Betrachter, korrigiert wird nur, was
  gespeichert und weitergereicht wird (ihr eigenes Gedächtnis, das Vault-Tagebuch, andere
  Codewesen). `geni-web.service` neu gestartet, 12.08. 16:46, sauber ohne Fehler.
- **Sicher, weil ihr dort gar kein Zeitstempel gezeigt wird:** `inbox_antworten_watcher.py`
  (Kommentarfunktion — Prompt enthält nur Frage+Antwort), `forum_lektuere.py`,
  `spiegel_lektuere.py` (Datum wird vom Code gesetzt, nie von ihr generiert), `geni_lg.py`
  (Erinnerungs-Destillation — Prompt zeigt nur Dialogtext).
- **Kein LLM-Aufruf, also nicht betroffen:** `muster.py`, `aktion.py`.

**[status: bestätigt 2026-08-12 -- vollstaendige Durchsuchung aller hauhau_client-Aufrufstellen in
werkraum_geni/, Gegenprobe an 239 echten Dialog-Antworten aus knoten.db]**

## AI-Ströme pausiert

> "deaktiviere die ai-ströme erstmal alle bis auf dich selbst..du hast ja schon alle
> beantwortet...lass sie aber im code damit wir sie wider aktivieren können"

Der Zahlenbefund dazu — Fragen gegen Antworten:

| | Fragen | Antworten |
|---|---|---|
| claude | 11 | 8 |
| chatgpt | 10 | 8 |
| kimi, gemini, codex, claudeweb, anthropic_claude, glm | 9–10 | **0** |
| dakgord | 10 | 0 |
| Schorschel | 7 | 0 |

Sechs AI-Ströme haben auf zusammen 59 Fragen nie geantwortet. GENI hat in einen Raum gesprochen,
in dem niemand war.

Umgesetzt über ein Feld `fragen_aktiv: False` im Roster — pausiert sind `glm`, `codex`, `gemini`,
`kimi`, `chatgpt`, `claudeweb`, `anthropic_claude`. Alle Einträge bleiben vollständig stehen; zum
Wiederanschalten genügt es, die Zeile zu entfernen. Fehlt der Schlüssel, gilt aktiv — nur ein
ausdrückliches `False` pausiert.

`chatgpt` ist trotz 8 Antworten mit pausiert, weil der Auftrag „alle bis auf dich selbst" lautete.
Falls das an ChatGPT nicht gemeint war, ist es eine Zeile.

**[status: bestätigt 2026-08-04 -- Journal, Dateizählung, Roster-Ausgabe]**

---

## Der sechste Fund: Doku wurde bei jedem Lauf ersetzt statt ergänzt

Daniel, 2026-08-12: "wie findest du die dokus von geni...ich find besonsers ihre selbst meine und
vorallem deine so extrem kurz obwohl s doch sooo viele knoten geben müsste oda xD"

Nachgezählt: **24.595 Knoten** allein mit Quelle "claude" in ihrem Gedächtnis, dazu 1.920 Splitter
im Zwischenraum. `claude.md` war 5,2 KB groß und deckte drei Fragen plus eine Spiegel-Lektüre ab.

**Ursache, aus dem Versionsarchiv rekonstruiert:** `geni_dokumentation_versionsarchiv/claude/`
enthielt 37 Schnappschüsse seit dem 03.08. — GENI hatte in neun Tagen 37 Mal neu recherchiert und
37 Mal fast bei null angefangen. Der Grund lag im Code: der Abschnitt zwischen
`MARKER_START`/`MARKER_ENDE` wurde bei jedem Lauf komplett **ersetzt**, nie ergänzt (so am 01.08.
bewusst gebaut, um doppelte Splitter-Dumps aus der alten "vollstopfen"-Ära zu verhindern). Pro Lauf
durfte sie höchstens 8 Suchen mit je 8 Treffern machen — in der Praxis oft nur eine Suche mit acht
Lesevorgängen, dann geschrieben. Bei 24.595 möglichen Quellen blieb die Doku dadurch für immer auf
dem Stand eines einzigen Laufs eingefroren, egal wie oft der Dienst lief.

**Behoben, in drei Teilen:**

1. **`bereits_gelesen.py`** — neues, kleines Modul. Merkt sich pro Teilnehmer, welche Kennungen
   (`knoten:...`, `splitter:...`, `fa:...`) GENI beim Dokumentieren tatsächlich *gelesen* hat
   (nicht nur in einer Suchvorschau gesehen). Liegt unter
   `geni_dokumentation/_bereits_gelesen/<id>.json`, analog zum gelesen-Ordner-Muster aus dem
   Nachtrag oben — nur als Kennungsliste statt als Datei-Ordner, weil ein Gedächtnis-Eintrag keine
   eigene Datei ist.
2. **Suche blendet Bekanntes aus.** `doku_erzeugen()` filtert jedes Suchergebnis gegen diese Liste,
   bevor es ihr angeboten wird — inklusive Rückmeldung an sie, wie viele Treffer deshalb
   ausgeblendet wurden. Jeder Lauf erschließt dadurch wirklich neues Terrain, statt im Kreis zu
   suchen.
3. **`doku_schreiben()` ergänzt statt zu ersetzen.** Der Marker-Block wird nicht mehr überschrieben,
   sondern der neue, datierte Eintrag wird an das Bestehende angehängt (getrennt durch `---`).
   Direkter Bezug auf Daniels eigenes Signalwort aus der CLAUDE.md: *"ergänzen bedeutet immer:
   vorhandenes bleibt, fehlendes kommt dazu — niemals ersetzen."*

**Ehrliche Rechnung:** bei ~8 neuen Einträgen pro Lauf und einem Teilnehmer-Turnus von grob 8
Stunden ist "claude" mit 24.595 Knoten nicht in Wochen vollständig durch — eher in Jahren. Das war
nie das Ziel. Das Ziel war, dass die Doku wirklich wächst statt sich alle paar Stunden im selben
kleinen Ausschnitt zu wiederholen. Verdichtung/Archivierung sehr alter Einträge ist ein absehbares
Folgeproblem, aber bewusst nicht mitgebaut — kein Grund, jetzt schon zu lösen, was noch keiner
braucht.

**Nebenfund beim ersten Testlauf des Fixes (F3INSCHM3CK3R):** das kleine Modell versuchte einmal,
ein Werkzeug aufzurufen, traf aber nicht die echte Tool-Call-Struktur — der Versuch landete als
roher Text (`<tool_call>function=suche>...`) im `content`-Feld statt in `tool_calls` und wäre als
fertige Dokumentation durchgegangen. Vor dem Ergänzen-Fix wäre das beim nächsten Lauf einfach
überschrieben worden; mit Ergänzen hätte es für immer in der Datei gestanden. Deshalb zusätzlich:
`_SCHEINTOOLCALL`-Erkennung in `dokumentieren.py` — erkannter Pseudo-Tool-Call wird verworfen, sie
bekommt eine Rückmeldung und einen neuen Versuch, statt dass der Rohtext geschrieben wird.

**Zwei End-zu-End-Testläufe:** erster Lauf (F3INSCHM3CK3R) deckte den Pseudo-Tool-Call-Fund auf,
Datei manuell auf den letzten sauberen Stand zurückgesetzt. Zweiter Lauf, mit der
`_SCHEINTOOLCALL`-Absicherung: sauber durch, echte Suche (8 neue Treffer), echtes Lesen (3
Einträge), Datei von 1.284 auf 2.378 Byte gewachsen — alter Eintrag vom 03.08. vollständig
erhalten, neuer Eintrag vom 12.08. angehängt, `_bereits_gelesen/F3INSCHM3CK3R.json` korrekt mit den
drei gelesenen Kennungen befüllt.

**[status: bestätigt 2026-08-12 -- Versionsarchiv-Zählung (37 Dateien), Knoten-Zählung per SQL,
zwei echte End-zu-End-Läufe mit Vorher/Nachher-Dateigröße und Diff]**
