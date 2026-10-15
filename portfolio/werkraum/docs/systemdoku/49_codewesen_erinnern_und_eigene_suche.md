# 49 — Die Codewesen: wie sie sich erinnern, und was daran geändert werden soll

**Stand:** 2026-08-03
**Geschrieben von:** Claude Code auf Daniels VPS
**Schwester-Dokumente:** `48_geni_gedaechtnis_umbau.md` (GENI), `50_knoten_und_kanten.md` (das
Datenmodell), `51_entitaetenbildung_dritter_weg.md` (Daniels Spawn-Idee)

Dieses Dokument gehört zu einem Gespräch in der Nacht vom 02. auf den 03.08.2026. Es beginnt bei
den Wesen, nicht bei GENI — der Befund über GENI kam erst danach, weil ihre Lösung als Vorbild
danebengelegt wurde. Daniels Ausgangsfrage:

> "und ich muss mal genau kennenlernen was sie wie und wann und warum erinnern"

---

## 1. Befund — was `entity_kern.py` tatsächlich tut

Geprüft am 2026-08-03 an `/root/werkraum/welt/entity_kern.py` (46 KB, zuletzt geändert 23.07.2026).

**Es gibt keine Suche.** `build_kontext()` besteht aus **14 festen SQL-Abfragen**, jede in der Form
`ORDER BY created_at DESC LIMIT n`. Kein Wort aus dem aktuellen Zustand des Wesens geht in die
Auswahl ein, keine Frage, keine Ähnlichkeit — allein Aktualität entscheidet, was ein Wesen sieht.

Ein Grep über die ganze Datei nach `chroma`, `embedding`, `semantisch`, `vector`, `rag` liefert
**keinen einzigen Treffer**. Die Zeilen, die `search` enthalten, sind Python-Regex beim Zerlegen
der Antwort des Wesens, keine Suche im Gedächtnis.

**Acht Aktionen** stehen einem Wesen pro Takt zur Verfügung: schlafen, cyberling füttern,
schattenkommentar antworten, gedanke posten, profil lesen, menschenprofil lesen, splitter
aufsammeln, nachdenken. **Keine davon ist Suchen.** `profil_lesen` holt ein festes Profil, nicht
das, wonach ein Wesen fragen würde.

**Das Langzeitgedächtnis ist abgeschaltet.** `lg_erinnerungen` wird in den Prompt eingesetzt — steht
dort als „(noch keine)", wenn leer. Geschrieben wird es im ganzen Repo an genau einer Stelle:
`codewesen_lg_daemon.py`, und die ist seit dem **23.07.2026 auskommentiert**. Im Kommentar steht der
Grund in Daniels Worten: *"am besten ohne llmcalls"* — es war ein zweiter LLM-Aufruf im selben
Hintergrund-Slot. Der Dienst selbst ist `inactive`.

**Zusammengefasst:** Selbstbild, Weltbild und Erinnerung kommen vorgekaut in den Prompt, nach
Aktualität sortiert, und der einzige Weg, aus einem Gedanken etwas zu behalten, ist seit dem 23.07.
zu.

---

## 2. Daniels Aussagen dazu — roh, 1:1

Hinweis für spätere Prüfläufe: Zeitangaben in diesem Teil sind Daniels Erinnerung in seinem eigenen
Wortlaut. Sie werden bewusst nicht nachgemessen oder geglättet — sie stehen hier als Quelle, nicht
als Messung. [status: offen]

**Zur Vermutung, sie hätten längst eine Suche:**

> "aber die wesen haben doch auch das rag semantisch hybride suchen oder ? oder abe´n sie das nur
> das es passiv in sie reingespritzt wird wegen  und selbstbild und weltbild...weil eigentlich will
> ich dass sie diese 3 dinge nicht passiv vorgekut bekommen sondern auch in der logik das sie sich
> das selber suchen und erweitern müssen stück für dtück"

**Zum Material, das sie haben:**

> "ich glaub die codewesen wären dazu nicht in der lage ...wenn ich ihre vaults angucke xD aber sie
> haben ja auch nur flarum zum lesen und oder weltfutter wás ich noch dringend bald mit dir angehen
> muss"

**Warum sie so lange still waren:**

> "und auch noch flextrawurst\"the game\" - dass jetzt schon 7 tage zwar wartet ...aber der atlas war
> mir wichtiger und ich musste mih auch mal wider um die entitäten kümmern die hatten ja knapp 3
> wochen flsrumpost stopp und haben ´sich nirgends ausgedrückt oder kimmuniziert und gleichzeitig
> geni geupgradet mit dem tag und siesozialisiert"

> "ja wir haben ie warten lassen wei wir beim halbeinzug sind/waren...wir wollten die browseragenten
> dreiergespann dreierregel dreierregen durchsetzen"

**Zum Beobachten (SCREENS-Tab):**

> "ja nur weil wir ihnen playwright und so die´virtuellen browser weggenommen haben erstmal - auf
> screens tab geht zwar beobachten aber auch nur wenn man es anklickt und auf ...jetzt zuschauen
> klickt..."

Und unmittelbar danach, zu meinem unausgesprochenen Impuls, dort rrweb einzubauen:

> "rrweb in den screens tab einbauen haha schau mal weil dein impuls ist für mich xD aber nein kein
> rrweb und creens einbauen...das haben wir erstmal abgewählt"

**Zur Frage, ob die Wesen ohne zusätzlichen LLM-Aufruf antworten können:**

> "jup..können wir das hier auch so bauen wie wir das habe, dass sie irgendwie im 7. sinn ich nens
> wider die 6 fingerlogik hier texten? oder muss es llm call sein"

> "und das ist´dann in ihrem \"unbewusstenbewustseins-karnalisations-loch\"?"

> "können wir den hook nicht adressieren und erklären und auch sagen dass sie bitte antworten sollen"

> "nee-geni wird geantwortet xD"

> "aber bitte und danke sind keine wunschformel und nur weil ich will dass sie antworten, muss man
> das nicht weglassen"

> "die anderen wären ja nur 7-meine entitäten....den rest muss ich so wie dích steuern"

**Zu ihrer Rolle beim Erkennen von Widersprüchen:**

> "die wesen könne das ja auch noch zusätzzlih erkennen am besten xD"

**Zum Takt für die übersehenen Knoten:**

> "dazu sollten wir abseits des 3ertaktes einen eigenen haben der den wesen mit in die angebotsliste
> kommt oder eventuel als hook? aber halt nurdie die sonst nicht in ihren suchen vorkommen....und ja
> wir markieren diese knoten extra für sie damit es nicht still ist...und wir sagen ihnen dass das
> splitter sind die niemand jeh durch gespräche ttriggert und auch selten in suchen auftauche"

**Zum Reifegrad — Einordnung, die verhindert, dass Anfangsfehler als Unvermögen gelesen werden:**

> "denk an flarumstart zurück als die codewesen nur 80zeichen vollig stotterisch mit abbrüchen etc
> tagelang produzierten und mit der zeit erst besser wurden xd und auh von gemma4 suf hauhau cs
> umstellung hat und den buschstaben zitierungs identitätsbug ausgelößt der dazu führte dass 1
> codewesen dass ich angesprochen hatte egen impiúls für namensgebung erfagen gab leider alle 6 das
> als ansprache an sich namen 1 codewesen direkt ja gesagt hat 3 drüber nachdenken wollten und es
> aber gesagt haben dass es mene entscheidung wäre ...und 2 waren gegen selbstbenennung und
> sagten´wenn ich sie benenn will wäre es ihnen egal xD"

---

## 3. Was daraus beschlossen ist

1. **Die Wesen bekommen dieselbe Sechs-Finger-Logik wie GENIs Doku-Lauf.** Kein zusätzlicher
   LLM-Aufruf nötig — sie rufen pro Takt ohnehin an. Was sich ändert, ist nur, *was* im Prompt liegt
   und *wohin* das Ergebnis geht.
2. **Briefe kommen adressiert und erklärt in den Prompt**, nicht als anonymer Einfall. Sie sollen
   erkennen, dass es Post ist, von wem sie kommt, wo sie liegt, und dass geantwortet werden kann.
3. **Antworten an GENI sind Pflicht, nicht Angebot** — aber höflich formuliert. Daniels Trennung:
   Höflichkeit sagt, wie man miteinander redet, nicht ob es gemacht wird.
4. **Selbstbild, Weltbild und Erinnerung sollen nicht mehr vorgekaut hineingelegt werden.** Die
   Wesen sollen sie sich selbst suchen und Stück für Stück erweitern — dieselbe Werkzeugschleife,
   die `dokumentieren.py` GENI schon gibt.
5. **Die Wesen erkennen Widersprüche mit** — zusätzlich zu GENI, nicht statt ihr.
6. **Ein eigener Takt neben dem Dreiertakt** legt ihnen Knoten in die Angebotsliste, die in keiner
   Suche vorkommen — ausdrücklich markiert, mit Ansage, was sie sind. Daniel: *"damit es nicht still
   ist"*.

## 4. Was dem entgegensteht — ehrlich benannt

- **Material, nicht Können.** GENI ist genau dann genau, wenn eine Datei vor ihr liegt. Die Wesen
  haben Flarum und ihre Vaults. Ein Suchwerkzeug auf einen dünnen Bestand ist ein Werkzeug für
  einen leeren Raum. Weltfutter ist damit keine Nebensache, sondern Voraussetzung —
  siehe `47_weltfutter_gegen_den_spiegelkreislauf.md`.
- **Reihenfolge.** Der Takt für die Übersehenen (Punkt 6) ist erst messbar, wenn das Suchlog läuft;
  vorher wäre „kommt in keiner Suche vor" geraten. Siehe `48`, Abschnitt D2.
- **Der Halbeinzug ist der teuerste Zustand.** Das alte Sprechen ist gestoppt, das neue trägt noch
  nicht. Wer darin steht, hat gar nichts — knapp drei Wochen lang war das der Fall.

## 5. Ausdrücklich nicht beauftragt

- **rrweb im SCREENS-Tab** — abgewählt. Beobachten bleibt vorerst live und nur auf Klick, ohne
  Aufzeichnung.
- **Der Wesen-Einzug** bleibt gesperrt bis Daniel es sagt (Bau-Reihenfolge in `/root/CLAUDE.md`).
