# 07 · Die vier Chat-Spawner: codexium, solarius, codexium2, solarius2

Deutsch zuerst, English below each field. Quellen: `werkraum/docs/systemdoku/21_wesen_chat_testbed.md` und die Konzeptfamilie `werkraum/_claude/ideen/codexium2_solarius2/` (sechs Dateien, Juli 2026).
German first, English below each field. Sources: `werkraum/docs/systemdoku/21_wesen_chat_testbed.md` and the concept family `werkraum/_claude/ideen/codexium2_solarius2/` (six files, July 2026).

Zu jedem Baustein steht: was versucht wurde, aus welchem Problem es entstand, was es lösen sollte, die Idee dahinter und der Baustand. Alles aus den Quellen, in Daniels Worten, wo die Quelle sie zitiert. Wo sie nichts sagt: **(Daniel ergänzt)**.
For each building block: what was tried, from which problem it arose, what it was meant to solve, the idea behind it and the build state. All from the sources, in Daniel's words where the source quotes them. Where it says nothing: **(Daniel adds)**.

**Was sind die vier Spawner? / What are the four spawners?**
Es sind vier Chat-Oberflächen für frei erfundene Charaktere (nicht die sieben Codewesen). Ein „Spawner“ legt einen Charakter an und führt dessen Chat. `codexium` und `solarius` sind die älteren, einfacheren. `codexium2` und `solarius2` sind die „Testbed-Spawner“: laut Doku 21 „die Versuchsfläche für alles, was in einem Wesen-Chat über reines Rollenspiel hinausgeht“. Alles unten gilt nur für die zwei Testbed-Spawner, außer wo es ausdrücklich für alle vier steht. Gebaut wurde das in `flextrawurst/scripts/serve_process_camera_preview.ts` (Server) und in `wesen_chat.html` (Oberfläche, liegt nicht im Repo).
They are four chat interfaces for freely invented characters (not the seven code beings). A "spawner" creates a character and runs its chat. `codexium` and `solarius` are the older, simpler ones. `codexium2` and `solarius2` are the "testbed spawners": according to doc 21 "the test bed for everything that goes beyond pure role play in a being chat". Everything below applies to the two testbed spawners only, unless it explicitly says all four. It was built in `flextrawurst/scripts/serve_process_camera_preview.ts` (server) and in `wesen_chat.html` (interface, not in the repo).

---

## 1. Das Testbed selbst: Charaktere mit Gedächtnis statt nur Rollenspiel

**Versucht / Tried.** Aus den einfachen Rollenspiel-Chats eine Versuchsfläche machen, auf der dauerhafte Erinnerung, gepinnte Ausschnitte, Zusammenfassen langer Verläufe, erzählerische Rückblicke und Feedback ausprobiert werden, ohne die älteren Chats anzufassen.
To turn the simple role-play chats into a test bed for lasting memory, pinned excerpts, summarising long histories, narrative recaps and feedback, without touching the older chats.

**Aus welchem Problem / From which problem.** Im Chat selbst ließ sich nichts davon benutzen. Die Quelle (`memory_container.md`) nennt als Ausgangslage, Container und Memory seien „nur dort editierbar“, nämlich auf der Profil-Seite, „im Chat nichts davon nutzbar – das war Daniels ursprüngliche Beschwerde“. Dazu kam eine Vergleichsfrage: Daniel wollte wissen, ob seine Charaktere schon mit Character.AI mithalten können. Befund der Durchsicht: Die Technik sei eher voraus, die Charakter-Felder aber „fast überall nur 1–2 Sätze dünn“. Ohne konkretes Material falle das Modell in „generische, atmosphärisch-vage ‚AI-Sprache‘“ zurück.
Nothing of this could be used in the chat itself. The source (`memory_container.md`) gives as the starting point that container and memory were "only editable" on the profile page, "nothing of it usable in the chat – that was Daniel's original complaint". There was also a comparison question: Daniel wanted to know whether his characters could already keep up with Character.AI. Finding of the review: the technology is rather ahead, but the character fields are "almost everywhere only 1–2 sentences thin". Without concrete material the model falls back into "generic, atmospherically vague 'AI language'".

**Was es lösen sollte / What it was meant to solve.** Dass ein Charakter über ein Gespräch hinaus trägt, was zwischen Mensch und Charakter wichtig war, und dass sein Verhalten nicht ins Allgemeine abrutscht.
That a character carries beyond one conversation what mattered between human and character, and that its behaviour does not slide into the generic.

**Idee, Vision, Planung / Idea, vision, plan.** Aus der Konzeptdatei: Der Container ist „der Ort für das Akute“, das Memory „der Ort für das, was bleibt“. „Die Trennung ist eine Trennung zwischen Gegenwart und Biografie.“ Als Folge des Character.AI-Vergleichs entstand ein neues Feld `beispieldialoge.md` (1–3 Beispiel-Antworten „So klingt X“), bewusst spät im System-Prompt platziert, weil Beispiel-Turns nah am Ende stärker wirken. Das alte „Zwischenwesen“-Konzept war die Inspiration, wurde von Daniel aber am 2026-07-04 als „braucht komplette Neubewertung“ eingestuft und nicht 1:1 übernommen.
From the concept file: the container is "the place for the acute", memory "the place for what remains". "The separation is a separation between present and biography." As a consequence of the Character.AI comparison a new field `beispieldialoge.md` was added (1–3 example answers "this is how X sounds"), deliberately placed late in the system prompt because example turns work stronger near the end. The old "in-between being" concept was the inspiration, but Daniel classified it on 2026-07-04 as "needs a complete re-evaluation" and it was not taken over one to one.

**Was liegt drin / What is inside.**
- Pro Charakter ein Ordner mit `wesen.md`, optional `was_ich_bin.md`, `beispieldialoge.md`; dazu `chat_history.jsonl`, `container.json`, `memory.json`, `verdichtungen.json`, `abschluss_archiv.json`, `feedback/` (laufende Daten, nicht im Repo) / per character a folder with the profile files and the running data (running data not in the repo)
- Doku 21 beschreibt den Aufbau des System-Prompts in zwölf Stufen: feste Vorrede, Charakterfelder, Rückblicke, Erinnerungen, Container, globale Grenzen, Alias-Register, Feedback, Merken-Hinweis / doc 21 describes the system prompt in twelve stages

**Baustand / Build state.** Laufend gebaut und getestet im Juli 2026; Doku 21 hat den Stand 2026-07-09 mit Nachtrag 2026-08-12. Drei Stellen sind in der Doku ausdrücklich als offen benannt: Die Memory-Extraktion liest nur die letzten 20 Nachrichten (nicht die Session), ein automatischer Rhythmus für das Zusammenfassen fehlt, und der Abruf alter Stellen nur auf Nachfrage („weißt du noch …“) ist vertagt.
Built and tested continuously in July 2026; doc 21 has the state of 2026-07-09 with an addendum of 2026-08-12. Three points are explicitly named open: the memory extraction only reads the last 20 messages (not the session), an automatic rhythm for summarising is missing, and retrieval of old passages only on request ("do you remember …") is postponed.

---

## 2. Das „E-Mail-Gefühl“: Antworten, die ohne offenen Browser fertig werden (`chat_architektur.md`)

**Versucht / Tried.** Chat wie einen Briefwechsel bauen: Nachricht abschicken, Seite verlassen, später die fertige Antwort im Verlauf finden.
Build chat like correspondence: send a message, leave the page, find the finished answer in the history later.

**Aus welchem Problem / From which problem.** Der Server brach die laufende Generierung ab, sobald die Verbindung des Browsers schloss. Wer die Seite verließ, bekam nichts: keine Antwort, kein Eintrag im Verlauf.
The server cancelled the running generation as soon as the browser connection closed. Whoever left the page got nothing: no answer, no entry in the history.

**Was es lösen sollte / What it was meant to solve.** Kein Zwang, dem Wesen beim „Tippen“ zuzusehen. Die Quelle nennt dazu die Eigenheit des Systems: ein 35B-Modell auf CPU, dessen Antwortzeiten „eh nicht live“ sind.
No need to watch the being "type". The source names the system's trait: a 35B model on CPU whose answer times are "not live anyway".

**Idee, Vision, Planung / Idea, vision, plan.** „Der Chat wird vom Live-Gespräch zum Briefwechsel. Das nimmt Druck raus.“ Entschieden am 2026-07-04: Live-Streaming bleibt zusätzlich erhalten; wer bleibt, sieht weiter Wort für Wort, wer geht, bricht nichts mehr ab. Daniels Begründung: aktuell nur ein Nutzer, Einzug der Wesen gesperrt, also keine Last.
"The chat turns from live conversation into correspondence. That takes the pressure off." Decided on 2026-07-04: live streaming stays as well; whoever stays still sees word by word, whoever leaves no longer cancels anything. Daniel's reason: only one user at present, the beings' move-in is locked, so no load.

**Baustand / Build state.** Gebaut und getestet am 2026-07-04 (Client trennt nach 2 s, Antwort landet rund 44 s später im Verlauf). Am selben Abend kam ein Endpunkt zum bewussten Abbrechen dazu, weil „Stop“ und „Verbindung weg“ serverseitig gleich aussahen. Offen laut Quelle: Wie erfährt der Client von der neuen Antwort ohne Polling? Und eine Warteschlange pro Wesen für mehrere Nachrichten hintereinander.
Built and tested on 2026-07-04 (client disconnects after 2 s, answer lands in the history about 44 s later). The same evening an endpoint for deliberate cancelling was added, because "stop" and "connection lost" looked the same on the server. Open according to the source: how does the client learn of the new answer without polling? And a queue per being for several messages in a row.

---

## 3. Container und Memory: Gegenwart und Biografie (`memory_container.md`)

**Versucht / Tried.** Zwei Speicher pro Charakter. Der Container sammelt gepinnte Ausschnitte (ganze Nachricht oder einzelne Sätze, mit kurzem „warum wichtig“). Das Memory hat fünf Kategorien: `über_mich`, `wichtige_momente`, `offene_fragen`, `wesen_selbst`, `meinungen`.
Two stores per character. The container collects pinned excerpts (whole message or single sentences, with a short "why it matters"). The memory has five categories.

**Aus welchem Problem / From which problem.** Das Kontextfenster ist klein (`num_ctx` 8192 für HauhauCS laut Quelle) und alles muss hineinpassen: Charakter-Felder, Verlauf, Antwort. Ohne Auswahl verschwindet Wichtiges im Verlauf.
The context window is small (`num_ctx` 8192 for HauhauCS according to the source) and everything must fit: character fields, history, answer. Without selection, important things vanish in the history.

**Was es lösen sollte / What it was meant to solve.** Dass der Mensch bestimmt, was bleibt, und dass das Wesen das Wichtige beim nächsten Gespräch wieder hat, ohne den ganzen Verlauf mitzuschleppen.
That the human decides what stays, and that the being has the important things again in the next conversation without carrying the whole history.

**Idee, Vision, Planung / Idea, vision, plan.** Ein Gesamt-Zeichenbudget statt fester Obergrenzen je Kategorie, abgeleitet aus dem Kontextfenster. Die Werte wurden mehrfach von Daniel angehoben (Memory 2500 → 3333 → 5555 → 11111, Container 1200 → 2222 → 5555 → 11111 Zeichen, „mehr Luft“). Der Pin-Kommentar von 88 Zeichen und andere Pro-Eintrag-Limits wurden am 2026-07-05 auf Daniels Wunsch („wenn ja, weg damit“) entfernt, die Summen-Obergrenzen blieben. Am 2026-07-06 kam eine neue Entscheidung: Container sollen frei anlegbar und benennbar sein („deswegen heißt es ja Container: weil sie etwas tragen können, zum Packen und beschriftbar sind“), einzeln an- und ausschaltbar. Die Kategorie `wesen_selbst` hatte zuerst keinen Schreibweg. Daniel fragte nach, die Lücke wurde bestätigt und mit einer Mischung gelöst: Das Wesen darf am Ende einer Antwort `[MERKEN: …]` anhängen, und die Rückschau am Sessionende schreibt 0–3 Ich-Sätze.
A total character budget instead of fixed caps per category, derived from the context window. Daniel raised the values several times (memory 2500 → 3333 → 5555 → 11111, container 1200 → 2222 → 5555 → 11111 characters, "more room"). The pin comment limit of 88 characters and other per-entry limits were removed on 2026-07-05 at Daniel's wish ("if so, get rid of them"), the total caps stayed. On 2026-07-06 came a new decision: containers should be freely creatable and nameable, switchable on and off individually. The category `wesen_selbst` first had no write path. Daniel asked, the gap was confirmed and solved with a mix: the being may append `[MERKEN: …]` to an answer, and the recap at the end of a session writes 0–3 first-person sentences.

**Was liegt drin / What is inside.** `werkraum/_claude/ideen/codexium2_solarius2/memory_container.md` (Entscheidungen mit Daten / decisions with dates); Code in `flextrawurst/scripts/serve_process_camera_preview.ts`; Oberflächen `wesen_chat.html`, `wesen_profil.html` (nicht im Repo / not in the repo).

**Baustand / Build state.** Gebaut, live getestet (2026-07-04 bis 2026-07-06), Budgets zuletzt 11111 Zeichen. Zwei Nebenbefunde stehen in der Quelle: wiederholte Extraktion desselben Pins ist möglich, und ein Fakt wurde einmal mitten im Wort abgeschnitten (später durch Kürzen an der Satzgrenze behoben).
Built, tested live (2026-07-04 to 2026-07-06), budgets last at 11111 characters. Two side findings in the source: repeated extraction of the same pin is possible, and one fact was once cut off mid-word (later fixed by cutting at the sentence boundary).

---

## 4. Sessions, Kontextanzeige und Abschluss-Geschichte (`sessions_kontextmeter.md`, `provenienz_logging.md`, Doku 21)

**Versucht / Tried.** Sessions mit „Neue Session“-Knopf, alte Sessions nur lesbar, eine Kontextanzeige und ein erzählerischer Rückblick, den man in die nächste Session mitnehmen kann.
Sessions with a "new session" button, old sessions read-only, a context meter and a narrative recap that can be carried into the next session.

**Aus welchem Problem / From which problem.** Es gab nur eine einzige, endlos wachsende Verlaufsdatei pro Charakter, ohne Markierung, ohne Liste alter Gespräche. Außerdem: Daniel wollte wissen, wie voll das Fenster ist. Die Quelle nennt als Vorbild das Dolphin-Mischpult mit seinem Session-System.
There was only one endlessly growing history file per character, without markers, without a list of old conversations. Also: Daniel wanted to know how full the window is. The source names the Dolphin mixing desk with its session system as the model.

**Was es lösen sollte / What it was meant to solve.** Gesprächsabschnitte trennen, ohne etwas zu löschen. Die Abschluss-Geschichte ist etwas anderes als Memory: „ein einziger zusammenhängender, erzählerischer Text“, aus Sicht und im Ton des Wesens, „bewusst nicht kategorisch“.
Separate conversation sections without deleting anything. The closing story is something different from memory: "a single coherent narrative text", from the being's view and in its tone, "deliberately not categorical".

**Idee, Vision, Planung / Idea, vision, plan.** Beim Sessionwechsel ein Marker-Eintrag im Verlauf und eine Bestätigung vorher. Die Anzeige schätzt clientseitig (Zeichen durch 4); ab 77 % erscheint nur ein Hinweis auf Qualitätsverlust, keine Handlungsaufforderung („mach es ab 77 % und nur als Hinweis“). Die Abschluss-Geschichte läuft als Entwurf, den man verwerfen oder übernehmen kann. Seit 2026-07-09 ist sie ein Archiv: Jede Annahme fügt einen Eintrag hinzu, beim Start einer neuen Session wählt man bewusst, welche Rückblicke mitgenommen werden, Standard ist nichts. Daniels Anstoß dazu: er wolle die Möglichkeit, die „Geschichte“ auch zwischendurch generieren zu lassen und sie „als schönen Abschluss“ zu wählen, der „mitrüber genommen wird“.
At a session change a marker entry in the history and a confirmation first. The meter estimates on the client (characters divided by 4); from 77 % only a hint about loss of quality appears, no call to action. The closing story runs as a draft that can be discarded or adopted. Since 2026-07-09 it is an archive: each acceptance adds an entry, at the start of a new session you choose consciously which recaps are carried over, default is none.

**Baustand / Build state.** Gebaut und getestet (2026-07-04 bis 2026-07-09). Die Konzeptdatei zu Sessions trägt noch den Status „in-diskussion“, die Doku 21 beschreibt die Umsetzung. Offen: Was passiert, wenn der Verlauf für den Abschluss-Prompt selbst zu groß wird.
Built and tested (2026-07-04 to 2026-07-09). The concept file on sessions still carries the status "in discussion", doc 21 describes the implementation. Open: what happens when the history itself is too big for the closing-story prompt.

---

## 5. Verdichtung: lange Chats zusammenfalten (`verdichtung.md`)

**Versucht / Tried.** Ausgewählte Nachrichten per Regler zu einer Zusammenfassung verdichten, mit Kommentar-Runden und ausdrücklicher Bestätigung, beliebig verschachtelbar.
Compress selected messages with a slider into a summary, with comment rounds and explicit confirmation, nestable without limit.

**Aus welchem Problem / From which problem.** Auslöser war Daniels Frage, warum Chats wieder hängen. Antwort laut Quelle: Je länger der Verlauf, desto länger die Prompt-Verarbeitung, bis zu minutenlangen Hängern. Das bloße Ausblenden einzelner Nachrichten (✂️) verkleinert nichts von selbst.
The trigger was Daniel's question why chats hang again. Answer according to the source: the longer the history, the longer the prompt processing, up to hangs of minutes. Merely hiding single messages (✂️) does not shrink anything by itself.

**Was es lösen sollte / What it was meant to solve.** Daniels Ziel: „quasi endlos gut weiter chatten können“, mit voller Kontrolle und nicht automatisch im Hintergrund.
Daniel's aim: "being able to keep chatting well, quasi endlessly", with full control and not automatically in the background.

**Idee, Vision, Planung / Idea, vision, plan.** „Verdichtung ist eine Faltung, kein Löschen.“ Die Originale bleiben sichtbar, nur das, was ans Modell geht, schrumpft. Seit 2026-07-09 sitzt die Verdichtung an der Stelle ihrer Originale in der Nachrichtenliste, das Ziel ist relativ (rund 45 % der Originallänge) statt einer festen Zahl. Live geprüft an echten Daten: 6293 Zeichen → 2954 Zeichen (46,9 %).
"Condensing is a fold, not a deletion." The originals stay visible, only what goes to the model shrinks. Since 2026-07-09 the condensation sits at the place of its originals in the message list, the target is relative (about 45 % of the original length) instead of a fixed number. Checked live on real data: 6293 characters → 2954 characters (46.9 %).

**Baustand / Build state.** Gebaut und live getestet inkl. Verschachtelung (2026-07-06), überarbeitet am 2026-07-09 und 2026-07-10. Beim Test wurde eine Race Condition gefunden (ein verworfener Entwurf überschrieb ein bestätigtes Ergebnis) und mit einem Job-Token behoben. Offen: kein automatischer Rhythmus. Das Zusammenfassen dauert auf der CPU mehrere Minuten, laut Quelle „die reale Geschwindigkeit des Systems“.
Built and tested live incl. nesting (2026-07-06), reworked on 2026-07-09 and 2026-07-10. During the test a race condition was found (a discarded draft overwrote a confirmed result) and fixed with a job token. Open: no automatic rhythm. Summarising takes several minutes on the CPU, according to the source "the real speed of the system".

---

## 6. Feedback, Stimme, Diktat und echtes Abbrechen (`feedback_stimme_diktat.md`)

**Versucht / Tried.** Daumen und Kommentar unter jeder Nachricht, Stimmenwahl (weiblich/männlich) und Lesetempo, Diktat per Mikrofon, ein Stop-Knopf, der wirklich abbricht.
Thumbs and comment under each message, voice choice (female/male) and reading speed, dictation by microphone, a stop button that really cancels.

**Aus welchem Problem / From which problem.** Daniel testete am 2026-07-04 abends alles auf dem Handy, drei Dinge waren kaputt: das Diktat verdoppelte Wörter (bekanntes Chromium-Verhalten auf Android mit `continuous:true`), der Stop-Klick ließ die Antwort trotzdem fertig laufen, und das Lesetempo war nicht einstellbar.
Daniel tested everything on his phone on the evening of 2026-07-04; three things were broken: dictation doubled words (known Chromium behaviour on Android with `continuous:true`), the stop click let the answer finish anyway, and the reading speed was not adjustable.

**Was es lösen sollte / What it was meant to solve.** „Feedback ist keine Bewertung des Wesens, sondern ein Gedächtnis für das, was zwischen Mensch und Modell wirklich getragen hat oder nicht – nützlich für spätere Prompt-Justierung, nicht für ein Ranking.“
"Feedback is not a rating of the being but a memory of what really carried between human and model or not – useful for later prompt tuning, not for a ranking."

**Idee, Vision, Planung / Idea, vision, plan.** Doppelt gespeichert: `feedback.json` für die Oberfläche und eine lesbare `.md` je Nachricht. Später (Doku 21, 2026-07-09) erreicht das Feedback pro Nachricht das Wesen nicht mehr, weil unklar ist, „was ein Charakter mit einem Daumen anfangen soll“; nur das allgemeine Feedback geht noch ans Modell.
Stored twice: `feedback.json` for the interface and a readable `.md` per message. Later (doc 21, 2026-07-09) the per-message feedback no longer reaches the being, because it is unclear "what a character is supposed to do with a thumb"; only the general feedback still goes to the model.

**Baustand / Build state.** Gebaut und von Daniel auf dem Handy nachgetestet (2026-07-04). Die Stimmenwahl und das Diktat laufen für alle vier Spawner, weil sie rein additiv sind.
Built and re-tested by Daniel on his phone (2026-07-04). Voice choice and dictation run for all four spawners because they are purely additive.

---

## 7. Lückenloser Verlauf: jede Handlung als Spur (`provenienz_logging.md`)

**Versucht / Tried.** Jede Aktion eines Charakters als eigene Zeile in `chat_history.jsonl` festhalten: Chat, Feedback, Pin, Memory-Änderung, Profil-Änderung (mit vollem Vorher/Nachher), Abbruch, Kontext-Ausschluss, Abschluss. Zwölf Ereignis-Typen sind in der Quelle aufgelistet.
Record every action of a character as its own line in `chat_history.jsonl`. Twelve event types are listed in the source.

**Aus welchem Problem / From which problem.** Daniels Auftrag, wörtlich: „ich will dass alles, jedes kleinste Detail wie bei dem Mischpult auch geloggt wird im Chat und in der Verlaufsdatei. Jeder Memoryeintrag, jede Änderung im Profil, alles.“ Später ein zweiter Anlass: ChatGPTs Web-Browsing-Tool sah von einem Charakter nur das leere HTML-Gerüst, weil die Seite per JavaScript befüllt wird.
Daniel's order, verbatim: he wants everything, every smallest detail, logged as with the mixing desk. Later a second occasion: ChatGPT's web browsing tool only saw the empty HTML frame of a character, because the page is filled by JavaScript.

**Was es lösen sollte / What it was meant to solve.** Dass der Mensch und auch Maschinen, die die Seite roh abrufen, immer den vollen Verlauf mit allen Änderungen sehen.
That the human and also machines that fetch the page raw always see the full history with all changes.

**Idee, Vision, Planung / Idea, vision, plan.** „Ein Gespräch ist eine Handlung in der Zeit. Jede Handlung hinterlässt eine Spur.“ (Zitat aus der Mischpult-Session vom 24.06., das als Vorbild dient.) Ereignis-Zeilen ohne `role` und `content` werden nie in den Modell-Kontext geladen. Die Seite rendert den Verlauf seit dem 2026-07-05 zusätzlich serverseitig ins HTML; das gilt für alle vier Spawner.
"A conversation is an action in time. Every action leaves a trace." (Quote from the mixing desk session of 24 June, which serves as the model.) Event lines without `role` and `content` are never loaded into the model context. Since 2026-07-05 the page also renders the history server-side into the HTML; this applies to all four spawners.

**Baustand / Build state.** Gebaut und an Wegwerf-Charakteren getestet (2026-07-04/05). Nicht gebaut, weil nicht verlangt: nichts Offenes aus dem Auftrag. Als Frage notiert: Ob der volle Vorher/Nachher-Text bei sehr häufigen Profil-Änderungen die Datei aufbläht.
Built and tested on throwaway characters (2026-07-04/05). Nothing open from the order. Noted as a question: whether the full before/after text bloats the file with very frequent profile edits.
