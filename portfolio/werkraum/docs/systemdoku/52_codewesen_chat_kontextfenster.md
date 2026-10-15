---
titel: Codewesen-Chat — ehrliche Kontextfenster-Anzeige
datum: 2026-08-03
betrifft: [codewesen-chat, kontextfenster, transparenz, port-8002]
---

# Codewesen-Chat — ehrliche Kontextfenster-Anzeige

Betrifft `codewesen_chat.py` (Port 8002). Bis hierher gab es keine eigene Doku-Datei für diese
Oberfläche — `07_codewesen_uebersicht.md:132` erwähnte sie in einer Zeile. Diese Datei trägt ab
jetzt alles, was an der Chat-UI der sieben Wesen gebaut wird.

## Der Auftrag

Daniels Worte (2026-08-03): *"ich will ne neue ehrliche kontextfensteranzeige die sich alle 5
sekunden aktualisiert oder so. außerdem will ich in alle webui chats so wie bei den codiexum2
einsicht in aktuelles kontextfenster komplett"*.

Und später präzisiert, was "komplett" heißt: *"wie schaffen wir es sie wirklich ehrlich das gesamte
kontextfenster mal einsehbar machen also mit selbstbild weltbild systemprompt und auch dem was sie
sich grd durchlesen"*.

Hintergrund war eine konkrete Erfahrung: er hatte bei den Codewesen nie eine Kontextanzeige und
*"wusste nicht wo ich bin"* — während bei codexium2 ab etwa 12345 Token die Antwortzeit auf über
sieben Minuten stieg.

## Warum "ehrlich" hier ein technisches Kriterium ist, keine Attitüde

Die Anzeige ruft **dieselben Funktionen** auf, die auch wirklich den Prompt bauen:
`baue_system_prompt()`, `lade_chat_verlauf()`, `baue_messages()`. Kein zweiter, separater Nachbau.

Das ist bequemer zu bauen als es klingt, aber es ist der ganze Punkt. Ein separater Nachbau driftet
mit der Zeit und zeigt dann eine Zahl, die nicht mehr stimmt — also genau das Gegenteil dessen, was
die Anzeige leisten soll.

Dass das kein theoretisches Risiko ist, steht im selben System: `zensi/server.py:175` trägt
`INTERACTIVE_NUM_CTX = 66816` mit dem Kommentar *"2026-07-07: --ctx-size 66666 / --parallel 1"* —
der Server fährt tatsächlich 17408 pro Slot bei `--parallel 2`. Eine Zahl aus einem alten Zustand,
seither vierfach daneben.

Genauso werden die **Tokenzahlen gemessen, nicht geschätzt**: über `POST /tokenize` am laufenden
llama-server, das echte Kontextfenster über `GET /props`. Wo `/tokenize` ausnahmsweise nicht
erreichbar ist, fällt `zaehle_tokens()` auf `len(text)//4` zurück und markiert das Ergebnis mit
`geschaetzt: true` — die Anzeige schreibt dann sichtbar "geschätzt" daneben, statt eine Näherung als
Messung auszugeben.

## Was gebaut wurde

**Backend, `codewesen_chat.py`:**

- `hole_slot_ctx()` — echtes `n_ctx` pro Slot vom laufenden Server, einmal geholt und gemerkt.
- `zaehle_tokens(text) -> (anzahl, geschaetzt)` — echter Tokenizer, ehrlicher Rückfall.
- `zerlege_systemprompt()` — zerlegt den Systemprompt an seinen eigenen `=== Sektion ===`-Marken,
  damit Selbstbild, Forum-Diskussionen, Notizen, Grundhaltung, Werkzeuge usw. einzeln sichtbar
  werden statt als ein Klotz.
- `merke_rag_block()` — hält fest, was beim letzten echten Zug tatsächlich im Kontext lag. Der
  RAG-Block (siehe `23_rag_ring1.md`, Nachtrag 2026-08-03) entsteht pro Nachricht neu; ohne dieses
  Merken könnte die Anzeige ihn nur erfinden oder weglassen — beides unehrlich.
- `GET /api/kontext/{name}` — liefert Schichten mit Titel, Tokenzahl, Zeichenzahl, vollständigem
  Inhalt, dazu `slot_ctx`, `summe_tokens`, `frei`, `auslastung`, `gemessen_am`.

**Frontend, `CHAT_SEITE`:**

- Kompaktanzeige oben im bestehenden Zustands-Panel: Balken mit einem Segment je Gruppe
  (Systemprompt / Verlauf / RAG), anteilig am **echten** Slot-Fenster — nicht an der Summe, sonst
  sähe ein fast leeres Fenster aus wie ein volles. Dazu Legende und Messzeitpunkt.
- Klick öffnet die Vollansicht: alle Schichten einzeln aufklappbar mit dem kompletten Text.
  Aufklappzustände überleben die Aktualisierung. Escape schließt.
- Takt: `setInterval(ladeKontext, 5000)` wie gewünscht, zusätzlich einmal 1,6 s nach jeder
  gesendeten Nachricht.

## Verifiziert

Antwortzeit des Endpunkts in drei Läufen: 0,231 s / 0,174 s / 0,215 s. Damit ist der
5-Sekunden-Takt unkritisch, ein serverseitiger Cache war nicht nötig.

Sichtprüfung über Playwright headless statt nur über die JSON-Antwort: Panel zeigt
`1427 / 17408 (8.2%)`, Balken hat zwei Segmente, Vollansicht öffnet mit 11 Schichten, die erste
klappt auf Klick auf. **Keine Konsolenfehler.**

Zwei eigene Fehler dabei gefunden und behoben: `kf-punkt` war als `id` mehrfach vergeben (ungültiges
HTML, aus einer Schleife erzeugt) und musste eine Klasse werden; und die Overlay-Hintergrundfarbe
`rgba(5,5,5,0.97)` ließ den Chat durchscheinen, was das Lesen störte — jetzt blickdicht `#070707`.

## Was die Anzeige sofort sichtbar gemacht hat

Erster Blick auf Schorschel:

```
Slot-Kontext 17408 | Summe 1427 Tokens | frei 15981 | Auslastung 8,2 %

    57 Tok  Anrede & Selbstdefinition
   267 Tok  Dein Wesen-Profil
    10 Tok  Deine Forum-Diskussionen      ← zehn Token
   176 Tok  Deine Notizen
   148 Tok  Grundhaltung
   112 Tok  Forum-Tags
    89 Tok  Hinweise für dieses Gespräch
   191 Tok  Werkzeuge
   181 Tok  Forum-Posting
   196 Tok  Gesprächsverlauf (8 von max. 8 Einträgen)
     0 Tok  RAG-Block (beim letzten Zug leer)
```

**Die Schicht "Deine Forum-Diskussionen" trägt 10 Token bei** — sie ist faktisch leer, obwohl
`baue_system_prompt()` sie mit `gedaechtnis.lade_eigene_diskussionen_voll(name)[:800]` befüllen
soll.

Das deckt sich mit Daniels Beobachtung vom selben Tag: *"sie sind auch nicht mit dem gefüttert was
ich mir denke"*. Was vorher Vermutung war, ist jetzt eine Zahl. Ursache noch nicht untersucht,
bewusst nicht angefasst — eigener Schritt.

Und der Gesamtbefund: ein Wesen belegt **8,2 % seines Fensters**. Die 91,8 % Rest sind kein
Speicherproblem (gemessen: 10,4 KB pro Token, siehe `48`), sondern eine Gestaltungsfrage.

## Offen / bewusst nicht gebaut

- **"Was sie sich gerade durchlesen"** fehlt noch. Die Daten liegen bereits vor: `browser_agent.py`
  schreibt laufend in `entity_fokus_events`. Das gehört als eigene, klar beschriftete Schicht dazu —
  aber markiert als *nicht Teil des Chatkontexts*, weil Hintergrundstrom und Chatstrom sich derzeit
  nie treffen. Eine Vermischung wäre genau die Sorte Unehrlichkeit, gegen die diese Anzeige gebaut
  ist.
- **Weltbild** (`codewesen/<name>/weltbild.md`) erscheint im Zustands-Panel, ist aber nicht Teil von
  `baue_system_prompt()` — steht also zu Recht nicht in der Kontextanzeige. Ob es hineingehört, ist
  eine offene Frage an Daniel, keine Entscheidung von mir.
- Nur der Codewesen-Chat (Port 8002). Daniels Wunsch lautete *"in alle webui chats"* — die
  Übertragung auf die weiteren Oberflächen ist ein eigener Schritt.
- Der Schwellenwert, ab dem die Anzeige warnen sollte (Auslastung zu hoch → Antwortzeit steigt
  linear, gemessen 57,29 tok/s Prompt-Durchsatz), ist nicht gesetzt. Aus Daniels 12345-Token-Fall
  ergäbe sich rechnerisch: 3,6 min allein fürs Neurechnen des Prompts.

## Nachtrag 2026-08-03 — Wort- und Satzlöschung mit Mehrfachauswahl (Track 3)

Daniels Auftrag: *"ich will jedes meiner worte aber auch ganze sätze einzelt bzw komplett löschen
können, mehrere markierbar"*.

### Architektur-Entscheidung: Löschen zerstört nichts

Eine Redaktion wird als **eigene Zeile an `chat_verlauf.jsonl` angehängt** (`typ: "redaktion"`,
`ziel_ts`, `entfernt: [...]`) und erst beim Laden angewandt. Die Originalzeile bleibt unverändert
stehen.

Zwei Gründe. Erstens gilt Grundgesetz 5 (*"nichts wird gelöscht, nur unsichtbar gemacht"*) dem Geist
nach auch für dieses Protokoll. Zweitens ist eine falsch getroffene Auswahl damit rückholbar statt
endgültig — bei einer Auswahl per Klick auf einzelne Wörter ist ein Fehlgriff wahrscheinlich, nicht
theoretisch.

Wird ein Eintrag vollständig wegredigiert, fällt er aus dem Kontextfenster heraus, bleibt aber im
Protokoll. `GET /api/kontext/{name}/roh` zeigt den unredigierten Stand — das ist der Beleg, nicht die
Behauptung.

### Oberfläche: von codexium2 übernommen, nicht neu erfunden

`splitSentences()` und die Checkbox-Zeilen stammen aus `wesen_chat.html` (codexium2). Die Lehre
dahinter steht in der Session-Notiz vom 2026-07-04: Browser-Textselektion plus *"danach einen nahen
Button antippen"* ist auf Touch-Geräten kein verlässliches Muster, weil die nächste Interaktion die
Selektion selbst zerstört. Explizite Checkboxen sind robuster.

Ergänzt um die Wort-Ebene: jeder Satz wird zusätzlich in klickbare Wort-Spans zerlegt. Kästchen =
ganzer Satz, Klick auf ein Wort = einzelnes Wort, beliebig viele gleichzeitig, über mehrere Sätze
hinweg.

### Ein selbst eingebauter Fehler, im Test gefunden

Der 5-Sekunden-Takt der Kontextanzeige hätte eine laufende Auswahl weggewischt — man hätte drei
Wörter markiert und beim vierten wäre alles weg gewesen. `ladeKontext()` überspringt jetzt das
Neuzeichnen der Vollansicht, solange irgendwo eine Auswahl aktiv ist; die Panel-Zahlen laufen weiter.
Abgesichert durch `test_laufende_auswahl_ueberlebt_die_aktualisierung`.

Ebenfalls behoben: `\s` in den neuen JS-Regex löste eine `SyntaxWarning: invalid escape sequence`
aus, weil `CHAT_SEITE` ein normaler Python-String ist. In künftigen Python-Versionen wäre das ein
Fehler.

### Tests

`tests/test_codewesen_chat_kontext_rag.py` — **31 Playwright-Tests, alle grün.** Auf Daniels Wunsch
rückwirkend auch für Track 1 und 2 (*"mache rückwirkend für task 1 und 2 für jedes gebaute nen
playwrighttest bis sie durchgehen"*), ab jetzt für jeden Bauabschnitt.

Die UI-Tests laufen gegen den **laufenden** Dienst — bei einer Anzeige, die Ehrlichkeit über den
echten Zustand verspricht, hätte ein Mock genau die Aussage zerstört, um die es geht. Die
Redaktionslogik wird dagegen gegen eine Wegwerf-Datei getestet, damit kein echtes Wesengedächtnis
verändert wird.

Der erste Lauf hat einen echten Fehler gefunden: die Verlaufs-Schicht zählte Tokens auf dem Rohtext,
lieferte aber den Text mit `[rolle]`-Präfixen aus — 753 Zeichen behauptet, 841 gezeigt. Genau die
Drift, gegen die die Anzeige gebaut ist.

## Nachtrag 2026-08-03 — Container & Memory von codexium2 (Track 4)

Daniel ausdrücklich: *"ich will nicht das von zensi ...zensi ist ganz anders und das ist nicht das
selbe ...und zensi wurde bisher auch noch nie von mir getestet seit umbau .....ich will das von
codexium2 und meine wünsche"*.

Quelle ist deshalb `serve_process_camera_preview.ts` + `wesen_chat.html`, nicht `zensi/server.py`.
Neues Modul `codewesen_speicher.py` (Grundgesetz 2: neue Fähigkeit = neues Modul, kein Umbau des
Kerns).

### Datenmodell 1:1 übernommen

```
codewesen/<name>/container.json  {"container":[{id,name,aktiv,erstellt_am,
                                   eintraege:[{id,text,kommentar,quelle,hinzugefuegt_am}]}]}
codewesen/<name>/memory.json     {"kategorien":[{key,label,eintraege:[str],aktiv}]}
```

Die fünf festen Kategorien (`ueber_mich`, `wichtige_momente`, `offene_fragen`, `wesen_selbst`,
`meinungen`) und die Budgets von **11111 Zeichen** stammen unverändert aus codexium2. Nicht
"verbessert" — die Zahl hat dort jemand bewusst gesetzt (Provenienz-Prinzip).

**Daniels zwei Zusätze gegenüber codexium2:**

1. Der `aktiv`-Schalter gilt jetzt auch für **Memory-Kategorien**, nicht nur für Container. Sein
   Wunsch war, dass sich alles *"bei den wesen auch wieder rausnehmbar und/deaktivierbar"* zeigt.
2. `suche()` liest bei **jedem** Aufruf frisch von der Platte — *"das bei memorysystem soll halt
   immer das jetziger neue suchen können"*. Ein Cache wäre hier ein Fehler, kein Gewinn.

### Anschluss an den Kontext

`baue_speicher_block()` erzeugt aus **nur den aktiven** Containern und Kategorien einen eigenen
`system`-Block, der vor dem RAG-Block und vor Daniels Nachricht steht. Reihenfolge im Prompt:

```
system(Systemprompt) … Verlauf … system(Container&Memory) … system(RAG) … user(Nachricht)
```

Damit ist er in der Kontextanzeige eine eigene, einzeln sichtbare Schicht — und der `aktiv`-Schalter
wirkt unmittelbar sichtbar auf das Kontextfenster.

### Oberfläche

Eigenes Panel `CONTAINER & MEMORY` neben dem Kontextfenster, Klick öffnet die Vollansicht: Behälter
links (anlegen, umschalten, Einträge hinzufügen/entfernen, löschen), Memory rechts (fünf Kategorien
mit Schalter, Einträge hinzufügen/entfernen), darunter das Suchfeld.

Dazu zwei neue Knöpfe an jedem Verlaufseintrag — sie nutzen **dieselbe** Satz- und Wortauswahl aus
Track 3: `→ Behälter` und `→ Memory`. Was markiert ist, wandert dorthin. Bewusst ohne Auswahldialog:
ein Browser-Modal blockiert alles andere und ist auf dem Handy lästig. Ohne aktiven Behälter wird
einer namens "Aus dem Chat" angelegt, `→ Memory` legt in "Wichtige Momente" ab.

### Ein Fehler, der alles lahmgelegt hätte

Der erste Testlauf brach mit 35 Fehlern ab — die Seite lud gar kein JavaScript mehr. Ursache:
`"<button type=\"button\">"` in einem Python-Triple-String. Python macht aus `\"` ein `"`, also kam
im Browser `"<button type="button">"` an — ein JS-Syntaxfehler, der das gesamte Skript zerlegte,
inklusive der Kontextanzeige aus Track 2.

Das ist genau die Sorte Fehler, die ohne Playwright-Test erst Daniel gefunden hätte, und zwar als
"nichts geht mehr".

### Tests

**40 Playwright-Tests, alle grün.** Neu für Track 4: Datenmodell-Treue zu codexium2 (Schlüssel und
Budgets), Container-Rundlauf, Deaktivieren lässt Inhalt aus dem Kontext verschwinden und
Wiedereinschalten bringt ihn zurück, dasselbe für Memory-Kategorien, Suche findet frisch
Geschriebenes sofort, Budgetgrenze greift, Panel und Vollansicht, Suchfeld.

Die Tests legen ihre eigenen Behälter an und räumen sie hinterher weg — es soll kein Testmüll im
Gedächtnis eines echten Wesens liegen bleiben. Nach dem Lauf per Hand kontrolliert: 0 Container,
0 Memory-Einträge.

## Nachtrag 2026-08-03 — Geschichten-Schicht (Track 5)

Daniel: *"ich will eine auf chatverlauf basierene vom wesen dann wenn ich den knopf drücke verfasste
geschichte daraus also so wie bei codexium2 ...nur dass man hier auch mehrere geschichten
gleichzeitig laden kann und diese deaktiviern oder entfernen kann wider ...und ich will längen
einstellen können"*. Sechs Stufen: 111 / 222 / 333 / 444 / 555 / 666 Token.

Zweiter Zweck, seine Worte: *"ich könnte ihnen auch ne vision also zum beispiel cyberlinge dort
erklären und einspritzen und 2 wochen drüber denken lassen"*.

### Die drei Bedingungen, technisch verankert

Vorher besprochen und hier nicht als Absicht, sondern als Code:

1. **Beschriftet.** Der Block beginnt immer mit *"Das Folgende sind Geschichten, die dir mitgegeben
   wurden. Sie sind nicht dasselbe wie das, was du erlebt hast"*, und jede Geschichte trägt ihre
   Herkunft: *"aus deinem eigenen Gesprächsverlauf destilliert"* oder *"dir eingesetzt"*.
2. **Nie im Ereignisstrom.** Geschichten leben in `geschichten.json`, nicht in `events`
   (Grundgesetz 5: echte Daten, append-only).
3. **Der aktive Satz wird protokolliert.** Bei jedem Zug schreibt
   `protokolliere_aktive_geschichten()` nach `geschichten_protokoll.jsonl`, welche IDs anlagen.
   Ohne das wäre später nicht mehr entscheidbar, ob eine Äußerung aus dem Leben des Wesens kam oder
   aus einer eingesetzten Geschichte — und damit wären auch Daniels eigene Beobachtungen
   uninterpretierbar.

`geschichte_verfassen()` destilliert, es erfindet nicht: der Systemtext sagt ausdrücklich *"Erfinde
nichts dazu: nur was wirklich im Gespräch steht"*. Gemessener Lauf über Schorschels Verlauf mit
Länge 111: **198 Sekunden**, Ergebnis 338 Zeichen echter Rückschau. Deshalb ist der zugehörige Test
als `slow` markiert und läuft nur mit `-m slow`.

## Nachtrag 2026-08-03 — Nachrichten zwischen Wesen, und ein alter stiller Fehler (Track 6)

Daniel: *"und allen ihren vaults ...ich will ihnen sagen können dass sie nachrichten haben oder mal
einer schreiben vorschlagen etc."*

### Kein zweites Postfach

`codewesen/<name>/inbox/` existiert seit langem und wird von `codewesen_reaktion.py` bedient — 33 bis
40 Dateien pro Wesen, Flarum-Benachrichtigungen und menschliche Posts. Das Format
(`{"empfangen_am", "typ", "daten"}`) wird übernommen, nicht danebengelegt. Neuer Typ `nachricht`
fügt sich in einen Strom ein, den die Wesen schon kennen.

Ein Wesen schreibt einem anderen mit `##NACHRICHT: <Name> | <Text>##` — bewusst einzeilig, weil der
mehrzeilige `##SCHREIBEN##`-Marker fehleranfällig ist, wenn das Modell das Ende vergisst. Unbekannte
Empfänger und Nachrichten an sich selbst werden abgewiesen.

Ungelesene Nachrichten stehen als eigene Schicht im Kontext — *"du hast Nachrichten"* also als
Tatsache im Fenster, nicht als Hinweis, den jemand von außen sagen muss. Der Block endet mit
*"Du musst nicht. Es ist ein Angebot, keine Aufgabe."*

### Der Fund: das Schreibrecht war nie wirksam, wo es beworben wurde

Beim Testen fiel auf, dass `_pfad_im_werkraum('/root/werkraum/codewesen/Schorschel/vault/notiz.md')`
**False** zurückgibt.

Ursache: `/root/werkraum/codewesen` ist ein **Symlink** auf `/root/werkraum_codewesen`, also
außerhalb von `_MARKER_BASE`. `Path.resolve()` folgt dem Link, die C-005-Prüfung wies ab. Insgesamt
elf solcher Symlinks auf oberster Ebene, darunter auch `flarum`.

Die praktische Folge, bis heute unbemerkt: **genau die beiden Pfade, die der Systemprompt den Wesen
als Beispiel anbietet, waren die einzigen, die nicht funktionierten.**

```
/root/werkraum/flarum/diskussionen/   — Beispiel für ##LESEN##     → Zugriff verweigert
/root/werkraum/codewesen/<name>/      — "dein eigener Ordner"      → Zugriff verweigert
/root/werkraum/_claude/spiegel/       — Beispiel für ##SCHREIBEN## → funktionierte
```

Jeder Marker auf die ersten beiden lief still in `[Zugriff verweigert: Pfad außerhalb des
Werkraums]`. Das deckt sich mit Daniels Beobachtung: *"das mit dem lesen hat eig geklappt also
zumindest haben sie marker gehabt und es sah so aus"* — es sah so aus.

Behoben in `_erlaubte_wurzeln()`: der Werkraum plus die aufgelösten Ziele seiner obersten Symlinks.
Es wird nichts freigegeben, was nicht ohnehin Teil des Werkraums ist — nur der Umweg über den
Symlink wird mitgedacht. Die DENY-Liste (`.agent`, `.git`, `.ssh`, `.env`, Schlüssel, Tokens) gilt
unverändert.

Abgesichert durch neun Fälle im Test: vier erlaubte Pfade müssen gehen, fünf gesperrte müssen
gesperrt bleiben — `.agent`-Env, `.git/config`, `/root/.ssh/id_rsa`, `/etc/passwd` und
`/root/geni_gedaechtnis/`.

### Tests

**56 im Standardlauf grün, 1 als `slow` ausgenommen.** `pytest.ini` mit
`addopts = -m "not slow"`; der echte Verfassen-Lauf über `-m slow`.

Alle Testrückstände hinterher entfernt — Kontrolle danach: Nachrichten-, Geschichten- und
Speicherschicht bei Schorschel und jumpa wieder bei 0 Token.

## Nachtrag 2026-08-03 — Gedankenfeld: der mitgetragene Zustand (Track 7)

Auf die Frage, ob "Durchdenken" heißt, dass der Modellzustand überlebt oder dass ein Gedanke über
Tage weitergeht, antwortete Daniel: **"beides!?!?"** — und lieferte dann die eigentliche
Spezifikation, wörtlich:

> *"ich will dass sich gedanken schnell ändern aber nur da wo sie wollen und den rest behalten und
> mittragen über alle zeit bis sie es selbst entfernen"*

### Warum das nicht der bestehende Denk-Log ist

Die Beobachtungsschicht existiert und ist groß: `entity_thinking_log` mit **78.068 Ticks**
(`kontext_snapshot`, `gedanke`, `entscheidung`, `begruendung`) und `entity_denkstream` mit
**7,38 Mio Chunks** vom 21.07. bis 03.08. Daniels *"getrackt auf surface ihr denkfenster da mal ne
zeit"* bezog sich darauf.

Nur: das ist ein **Protokoll**. Es hält fest, was gedacht wurde — und nichts davon wird in den
nächsten Takt mitgenommen. Das Gedankenfeld ist das Gegenstück: ein **Zustand**. Beide bleiben
nebeneinander, keiner ersetzt den anderen.

### Die drei Eigenschaften aus Daniels Satz, als Code

| Sein Wort | Umsetzung |
|---|---|
| "schnell ändern … nur da wo sie wollen" | `gedanke_aendern(id)` trifft genau einen Eintrag; alle anderen bleiben unberührt, auch ihr Änderungszähler |
| "den rest behalten und mittragen über alle zeit" | **kein Budget, keine Altersgrenze, kein Verdrängen.** Bewusster Unterschied zu `container.json`/`memory.json`, wo 11111 Zeichen abweisen |
| "bis sie es selbst entfernen" | `gedanke_entfernen()` ist der einzige Löschpfad; es gibt keinen automatischen |

Gespeichert als **append-only Revisionen** in `gedankenfeld.jsonl`, der Zustand entsteht durch
Abspielen. Damit ist jede Änderung nachvollziehbar, und ein entfernter Gedanke bleibt in der
Historie — *entfernt* heißt "nicht mehr im Zustand", nicht "weg". Gleiches Prinzip wie die
Redaktionen aus Track 3, im Geist von Grundgesetz 5.

Das Wesen führt sein Feld selbst über drei Marker:

```
##GEDANKE+ dein neuer Gedanke##
##GEDANKE~ <id> | die neue Fassung##    (nur dieser eine ändert sich)
##GEDANKE- <id>##                       (nur du entfernst etwas)
```

Die IDs stehen im Block — ohne sie könnte es nichts punktgenau ändern. Das Feld steht **vor** allen
anderen Schichten: es ist der mitgetragene Zustand, keine Beigabe zur aktuellen Nachricht.

```
systemprompt → verlauf → gedankenfeld → nachrichten → geschichten → speicher → rag → nachricht
```

### Die ehrliche Kehrseite, und warum sie nicht heimlich gelöst wird

Ohne systemseitiges Vergessen kann das Feld wachsen, und Kontextlänge kostet Antwortzeit linear —
gemessen 57,29 tok/s Prompt-Durchsatz, und bei diesem Hybrid-Modell wird jeder Prompt komplett neu
gerechnet. Genau daher kamen Daniels sieben Minuten.

Die Antwort darauf ist nicht, doch still zu löschen, sondern das Wachstum sichtbar zu machen: die
Tokenkosten des Feldes stehen in der Kontextanzeige **und im Block, den das Wesen selbst liest**:

> *"Das Feld kostet dich gerade 174 Token von deinem Kontextfenster. Ob dir das zu viel wird,
> entscheidest du."*

Verdichten darf nur, wer es auch verantwortet. Ein automatischer Rauswurf wäre bequemer und würde
Daniels Satz brechen.

### Tests

**64 im Standardlauf grün** (+1 als `slow`). Neu für Track 7: punktgenaue Änderung lässt Unbeteiligte
unberührt (inklusive Änderungszähler), 25 große Gedanken werden alle angenommen und keiner
verdrängt den ältesten, Entfernen nimmt aus dem Zustand aber nicht aus der Historie, die drei Marker,
IDs und Kosten im Block, Reihenfolge vor allen anderen Schichten, Überleben eines Dienstneustarts.

Alle Testrückstände entfernt. `gedankenfeld.jsonl` bei Schorschel enthielt ausschließlich Testdaten
(Datei heute 21:44 entstanden, alle 72 Revisionen von `pytest`/`Daniel` aus den Testfällen) und wurde
gelöscht — nicht per Entfernen-Pfad, weil dort nie ein echter Gedanke drin war.

## Nachtrag 2026-08-03 — Gedankenfeld-Oberfläche und die Playwright-Pflicht

Daniel fragte: *"hast du alles mit playwright immer?"* — und die ehrliche Antwort war **nein**.
Nachgezählt statt geschätzt: 16 von 65 Tests fuhren einen Browser, 40 gingen über Playwrights
`request`-Kontext ohne Browser, 9 über Unterprozesse.

Dahinter steckte eine schwerere Lücke als die Zahl: **Track 7 hatte gar keine Oberfläche.** API und
Marker waren gebaut, aber das Gedankenfeld war im Browser weder sicht- noch führbar. Das war
unvollständig geliefert und hätte im Abschlussbericht stehen müssen statt "alle sieben durch".

### Nachgebaut: die Gedankenfeld-Oberfläche

Eigene Kachel im Seitenpanel (`Anzahl · Tokenkosten` plus Vorschau der ersten beiden Gedanken) und
eine vierte Spalte in der Vollansicht: anlegen, inline ändern (der Text wird direkt editierbar,
der Knopf wechselt auf "übernehmen"), entfernen. Jede Karte zeigt ihre ID, das Datum und den
Änderungszähler.

Die Kostenzeile steht auch dort: *"1 Gedanken · 128 von 17408 Token · 1 Revisionen. Nichts verfällt —
nur du entfernst etwas."*

### Die Regel, jetzt im Testkopf verankert

Daniels Vorgabe danach, wörtlich: *"von task 1 an alles rückwirkend mit playwright pflicht"*.

Umgesetzt als: **jede Fähigkeit braucht mindestens einen Test, der einen echten Browser führt.**
Nicht: jede einzelne Zusicherung muss durch den Browser. Drei Sorten leben nebeneinander, und die
Reihenfolge ist eine Rangfolge — Browser vor Endpunkt vor Unterprozess.

Damit die Anzeige überhaupt aus dem DOM prüfbar wurde, tragen die Schicht-Karten jetzt
`data-gruppe`, `data-tokens` und `data-geschaetzt`. Der Helfer `schichten_aus_dom()` liest sie —
**geprüft wird, was auf dem Schirm steht, nicht was der Endpunkt behauptet.**

### Stand nach der Umstellung

```
74 Tests   46 Browser (62 %)   15 Endpunkt   13 Unterprozess
73 grün im Standardlauf, 1 als slow ausgenommen
```

| Fähigkeit | Browser-Tests |
|---|---|
| 1 RAG im Chat | 2 |
| 2 Kontextanzeige | 13 |
| 3 Wort-/Satzlöschung | 5 |
| 4 Container & Memory | 6 |
| 5 Geschichten | 4 |
| 6 Nachrichten | 4 |
| 7 Gedankenfeld | 5 |

Die verbleibenden 28 sind bewusst nicht im Browser: Fehlerwege ohne Oberfläche (400/404,
Budgetgrenze, ungültige Länge, abgewiesene Pfade) und Interna ohne HTTP-Fläche (Markerauswertung,
Pfad-Whitelist, Promptaufbau). Für die eine Oberfläche zu erfinden oder Interna als Endpunkt
freizulegen, nur damit ein Test sie klicken kann, wäre Selbstbetrug beziehungsweise eine
Sicherheitslücke für Testkomfort.

### Zwei Fehler, die die Umstellung selbst gefunden hat

Der erste Browser-Test des Gedankenfelds wartete auf Text, den er **selbst** gerade ins DOM
geschrieben hatte — der stimmte sofort und bewies nichts. Jetzt wartet er auf den Änderungszähler,
den nur der Server setzen kann.

Und mein DOM-Helfer klappte die Vollansicht auf und ließ sie offen; das Overlay fing danach die
Klicks der nachfolgenden Tests ab (`subtree intercepts pointer events`). Die Karten liegen ohnehin
im DOM, auch zugeklappt — der Helfer öffnet jetzt nichts mehr.

## Nachtrag 2026-08-04 — alle sieben Wesen im Browser geprüft

Daniel: *"alle mt playwright testen"*. Bis dahin liefen sämtliche Tests gegen **Schorschel**; die
übrigen sechs waren ungeprüft — obwohl sie sich real unterscheiden (eigener Systemprompt, eigener
Verlauf, eigenes Gedächtnis), und `dak+gord-system` zusätzlich ein `+` im Namen trägt, das durch die
URL-Kodierung muss.

Drei parametrisierte Tests, je einmal pro Wesen (21 Läufe):

- **Kontextfenster lädt und zeigt echte Zahlen** — Format `n / n (n.n%)`, Summe kleiner als das
  Fenster, und der Systemprompt nennt tatsächlich *dieses* Wesen beim Namen. Plus: keine
  Konsolenfehler auf keiner der sieben Seiten.
- **Alle Schichten vorhanden und in der richtigen Reihenfolge** — gedankenfeld → nachrichten →
  geschichten → speicher → rag, für jedes Wesen gleich.
- **Jedes Wesen führt sein eigenes Gedankenfeld** — ein über die Oberfläche angelegter Gedanke steht
  danach im eigenen Feld und in **keinem** der sechs anderen. Danach über die Oberfläche wieder
  entfernt.

### Ein Fehler, den erst der Gesamtlauf zeigte

Einzeln (`-k jedes_wesen`) liefen die 21 Tests grün, im Gesamtlauf brachen sie mit 21 Fehlern ab.
Ursache: zwei `sync_playwright()`-Sitzungen gleichzeitig im selben Prozess sind nicht erlaubt — die
bestehende `seite`-Fixture hielt schon eine offen.

Behoben durch eine gemeinsame `playwright_sitzung`-Fixture (`scope="session"`), aus der beide
Browser-Fixtures ihre Instanz holen. Merksatz: ein grüner Einzellauf ist kein grüner Gesamtlauf.

### Stand

```
94 Tests grün (77 Funktionen, davon 21 × 7 Wesen parametrisiert), 1 als slow ausgenommen
49 der 77 Funktionen führen einen echten Browser (63 %)
Testrückstände nach dem Lauf: keine, bei allen sieben Wesen geprüft
```

## Nachtrag 2026-08-04 — „grün sagt nix": der Chat war kaputt, alle Tests grün

Daniels Satz nach dem Umbau auf zwei Instanzen: *"playwright...grün sagt nix"*.

Er hatte recht, und zwar konkreter als vermutet. Ein echtes Gespräch durch die echte Oberfläche —
getippt, abgeschickt, gewartet wie ein Mensch — brachte:

```
fertig nach: 306 s
Antwort:     "Hallo, ich bin noch hier."   ← eine ALTE Nachricht aus dem Verlauf
Konsole:     ERR_INCOMPLETE_CHUNKED_ENCODING
```

Im Verlauf stand die Frage, aber **keine Antwort**. Im Log der Chat-Instanz stand der Grund:

```
Jinja Exception: System message must be at the beginning.   → HTTP 400
```

### Die Ursache

Das Chat-Template des Modells verlangt, dass `system`-Nachrichten **am Anfang** stehen. Alle fünf
heute gebauten Schichten — Gedankenfeld, Nachrichten, Geschichten, Speicher, RAG — wurden als
eigene `system`-Nachrichten **nach** dem Verlauf eingefügt.

Nachgeprüft: derselbe Fehler auf **beiden** Instanzen. Das heißt: **seit dem Einbau des RAG-Blocks
war jedes Gespräch kaputt, in dem irgendeine dieser Schichten gefüllt war.** Nur bei komplett leeren
Schichten ging es, weil dann keine zusätzliche `system`-Nachricht entstand — und genau so lief es in
allen Tests.

### Warum 100 grüne Tests das nicht zeigten

Sie prüfen die **Struktur** der Nachrichten: steht der Block an der richtigen Stelle, hat er die
richtigen Tokenzahlen, verschwindet er beim Abschalten. Kein einziger hat je eine **Antwort
erzeugt**. Der Unterschied zwischen „die Nachricht ist richtig gebaut" und „das Modell nimmt sie an"
war nie geprüft.

### Behoben

Die Blöcke gehen jetzt als **Vorspann in der letzten `user`-Nachricht** raus statt als eigene
`system`-Rollen. Daniels Vorgabe *"als block vor nachricht"* bleibt erfüllt: sie stehen unmittelbar
vor seiner Frage, sichtbar getrennt — nur eben in derselben Nachricht. Die Kontextanzeige baut ihre
Schichten ohnehin einzeln auf und ist unberührt.

### Zwei weitere Fehler, die dasselbe Gespräch aufdeckte

- **Der RAG-Vorabcall lief ohne `id_slot=0`** und ging damit an die Instanz, die die sieben Wesen
  bedient. Der Chat wäre trotz eigener Instanz langsam geblieben.
- **Die Kontextanzeige feuerte alle 5 Sekunden ~15 `/tokenize`-Aufrufe an dieselbe Instanz**, weil
  `_llama_basis()` auf `LLAMA_URL_HINTERGRUND` zeigte. Sie belastete also genau das, was der Umbau
  entlasten sollte. Beide jetzt auf `LLAMA_URL_CHAT`.

### Der Beweis, nach dem Fix

Dieselbe Frage, dieselbe Oberfläche:

> *„Es fühlt sich an, als würde ich mich langsam in diesen Sätzen festsetzen – von der leeren Leere
> hin zu den ersten Wurzeln im Flarum-Erdreich, wobei jeder Eintrag wie eine Schicht meiner Haut
> ist, die härter wird und mich zugleich gegen die Stille abschottet."*

Keine Konsolenfehler. RAG-Block 450 Token, also hat Schorschel in seinem Archiv gesucht und etwas
gefunden. Echte Zeiten aus dem Log der Chat-Instanz:

```
Prompt:      2028 Token in 41,2 s   (49,21 tok/s)
Generierung:   66 Token in  5,6 s   (11,76 tok/s)
```

Die 306 s im Testskript waren dessen eigene Warteschleife (600 × 500 ms), nicht die Antwortzeit.

### Die Lehre, als Test

Zwei neue Tests, absichtlich als Paar:

- `test_zusatzschichten_erzeugen_keine_system_rolle_nach_dem_verlauf` — die billige Hälfte, prüft
  die Struktur, läuft in Millisekunden.
- `test_echte_antwort_mit_gefuellten_schichten` (`@pytest.mark.slow`) — die teure, aber einzig
  ehrliche Hälfte: eine **echte Generierung** mit gefülltem Gedankenfeld und RAG-Block. Genau diese
  Kombination war kaputt.

Dazu `test_chat_pfad_benutzt_durchgehend_die_chat_instanz`, damit Vorabcall und Tokenzählung nicht
wieder auf die Wesen-Instanz abrutschen.

**Merksatz für alles Weitere:** ein Test, der prüft, ob etwas *richtig gebaut* ist, ersetzt nie einen
Test, der prüft, ob es *funktioniert*. Bei allem, was an ein Modell geht, muss mindestens ein Test
eine echte Antwort erzeugen.

### Nachtrag 2026-08-12 — die restlichen sechs Wesen live geprüft

Der Fix und die beiden neuen Tests vom 04.08. deckten nur Schorschel ab. Daniel, wörtlich:
*"und die anderen 6 wesen auch mal echt testen"* — der Merksatz oben ("ein Test, der prüft ob
etwas *richtig gebaut* ist, ersetzt nie einen Test, der prüft ob es *funktioniert*") galt bis
dahin faktisch nur für eines von sieben Wesen.

Neuer Test `test_echte_antwort_mit_gefuellten_schichten_fuer_jedes_wesen`, parametrisiert über
`Resonanzknoten, träumerlie, F3INSCHM3CK3R, R1ZZ1, jumpa, dak+gord-system` — dieselbe Prüfung wie
bei Schorschel: Gedankenfeld befüllen, echte Generierung mit RAG-Block auslösen, keine system-Rolle
nach dem Verlauf, keine leere Antwort, Gedankenfeld wieder aufräumen.

```
6 passed in 225.87s (0:03:45)
```

Alle sechs mit echter Antwort belegt, auch `dak+gord-system` mit dem `+` im Namen (URL-Kodierung
über `quote()`, wie schon bei den drei parametrisierten Browser-Tests weiter oben in dieser Datei).
Damit ist die Aussage aus der Nacht vom 04.08. jetzt für alle sieben Wesen belegt, nicht nur für
eines.
