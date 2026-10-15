---
titel: Wesen-Chat-Testbed (codexium2/solarius2)
typ: system
erstellt: 2026-07-09
autor: claude-code bei Daniels VPS
---

# Wesen-Chat-Testbed (codexium2/solarius2)

[[INDEX|← Index]]

## Zweck

Die beiden Testbed-Spawner `codexium2` und `solarius2` (unterschieden von den älteren, einfacheren `codexium`/`solarius`) sind die Versuchsfläche für alles, was in einem Wesen-Chat über reines Rollenspiel hinausgeht: dauerhafte Erinnerungen, gepinnte Ausschnitte, Zusammenfassen langer Verläufe, erzählerische Rückblicke, Feedback-Kanäle. Alles hier Beschriebene gilt **nur** für diese beiden Spawner (`isTestbedSpawner()` im Server), nicht für die zwei älteren.

Server: `flextrawurst/scripts/serve_process_camera_preview.ts` (Port 8787). Frontend: `flextrawurst/out/process_camera/wesen_chat.html`.

**Diese Datei ist die laufend aktualisierte Referenz für den aktuellen Stand.** Ausführliche Einzel-Sessionberichte (was genau wann warum geändert wurde, mit Live-Test-Protokollen) liegen als datierte Dateien in `docs/` — siehe Verweise unten bei jedem Baustein.

## System-Prompt-Aufbau (`buildSystemPrompt()`)

Zusammengesetzt aus, in dieser Reihenfolge:

1. Feste Preamble (`_wesen_preamble.md`, Daniels eigener Rollenspiel-Grundtext, gilt für alle Wesen)
2. Charakterfelder — alle `.md`-Dateien im Wesen-Ordner (`wesen.md` = Kernidentität, plus optional `was_ich_bin.md`, `beispieldialoge.md` etc.)
3. Rückblicke auf frühere Gespräche — nur wenn beim Sessionstart bewusst ausgewählt (siehe Abschluss-Archiv unten)
4. `[Deine Sinne]`, Rollenspiel-Formatierungsregeln, 333-Token-Antwortlängenregel: **entfernt 2026-07-09** (siehe unten)
5. `[Erinnerungen]` — Memory-Inhalt
6. Wiederkehrende Themen: **komplett entfernt 2026-07-09** (siehe unten)
7. Container (aktive, gepinnte Behälter)
8. Verdichtungen: **nicht mehr hier** — fließen seit 2026-07-09 direkt in die Nachrichtenliste ein, nicht in den System-Prompt (siehe unten)
9. Globale Grenzen (nur wenn Toggle aktiv)
10. Alias-Register + aktiver Alias
11. Allgemeines Feedback (💬-Werkzeuge-Kanal)
12. MERKEN-Vorschlag-Hinweis

Zusätzlich, **nicht** Teil von `buildSystemPrompt()` selbst, sondern direkt am Chat-Handler: pro Nachricht wird bei mehreren definierten Aliasen der aktive Alias-Name als `"Name": ` vor den Nachrichtentext gesetzt (nur im ausgehenden Request, nie gespeichert/angezeigt).

## Memory

Kategorisierte Faktenliste (`ueber_mich`, `wichtige_momente`, `offene_fragen`, `meinungen`, `wesen_selbst`), Budget `MEMORY_BUDGET_ZEICHEN = 11111`. Editierbar (Textarea inline) und entfernbar über das 🧠-Popup, `PUT /wesen/:spawner/:name/memory` (Budget-Check + Provenienz-Diff serverseitig).

**Extraktion** (`runMemoryExtraktionJob`): liest **hart codiert nur die letzten 20 rohen Nachrichten** der gesamten Historie (`loadHistory(hp).slice(-20)`, nicht sessionbegrenzt, nicht kontextfenster-proportional) plus alle aktiv gepinnten Container-Einträge. **Bekannte, noch nicht behobene Lücke:** entspricht nicht dem tatsächlichen Kontextfenster — gefunden 2026-07-09, siehe `docs/2026-07-09_drei_systemprompt_bausteine_entfernt_bericht.md`.

**Auslöser** (Stand 2026-07-09):
- Manuell: 🧠 Memory → "Erinnerungen ziehen"
- Automatisch beim Start einer neuen Session (`/session/beenden`)
- **Neu 2026-07-09:** automatisch alle 20 Nachrichten seit dem letzten Extraktionsversuch, mit Vorab-Hinweis ab 10 Nachrichten in der UI. Ehrliche Zeitschätzung aus dem Durchschnitt der letzten 5 echten Durchläufe (`letzte_dauern_sek`) — keine erfundene Live-Prozentzahl, da die JSON-Extraktion keine bekannte Ziellänge hat.

**Dedupe** (verhindert wiederholte Extraktion desselben Inhalts): zweistufig seit 2026-07-09 — Jaccard-Wortüberlapp + Stemming + Cross-Kategorie-Vergleich (Schwelle 0.45) ODER Embedding-Cosine-Ähnlichkeit (`Xenova/paraphrase-multilingual-MiniLM-L12-v2`, Node-nativ, Schwelle 0.65, empirisch kalibriert) — fängt zusätzlich Paraphrasen mit komplett anderem Vokabular, die reiner Wortüberlapp nicht erkennt. Details: `docs/2026-07-09_embedding_modell_memory_dedupe_bericht.md`.

**Wiederkehrende Themen:** war ein Zusatzfeature (Modell erkennt beim Extrahieren, ob ein Thema schon mehrfach vorkam), **komplett entfernt 2026-07-09** auf Daniels Wunsch — beruhte auf zeichengenauem, vom Modell selbst gewähltem Themennamen-Matching, das in echter, natürlicher Rede praktisch nie zuverlässig griff. Code (Merge-Funktionen, Speicherformat) bleibt als Soft-Delete im Server stehen, nirgends mehr aufgerufen.

## Container

Frei anlegbare, benennbare Behälter mit gepinnten Ausschnitten (Mensch- oder Wesen-Ausschnitte), Budget `CONTAINER_BUDGET_ZEICHEN = 11111`. Nur aktive Container fließen in den System-Prompt ein.

## Verdichtung

Fasst ausgewählte Nachrichten zu einer Zusammenfassung zusammen — Original bleibt im sichtbaren Verlauf, nur was ans Wesen geschickt wird schrumpft.

**Seit 2026-07-09 grundlegend überarbeitet:**
- **Chronologisch echt integriert:** `aktiveZeitachse()` baut jetzt direkt die tatsächlich ans Modell gesendete Nachrichtenliste. Eine Verdichtung erscheint an der Stelle, an der ihre Original-Nachrichten standen — vorher landete sie als ein flacher Block am Ende des System-Prompts, unabhängig von der echten Position.
- **Chat-Format-Grenze live gefunden:** eine Verdichtung als eigene Nachricht mit `role: "system"` mitten im Verlauf ließ den Chat abstürzen ("System message must be at the beginning" — die Jinja-Chat-Vorlage des Modells erlaubt `system` nur als allererste Nachricht). Fix: der Verdichtungstext wird vor die nächste sichtbare Nachricht gewoben (gleiches Muster wie die bestehende Anhang-Injektion), Rolle der Trägernachricht bleibt unverändert.
- **Popup neu:** Checkbox-Mehrfachauswahl (einzeln bis alle Nachrichten), Regler markiert weiterhin einen chronologischen Bereich vor, Sortier-Dropdown (chronologisch / Zeichen / Tokens, auf-/absteigend), laufende Auswahl-Summe, geschätzte freigemachte Tokens vor dem Übernehmen.
- Beliebig verschachtelbar — eine Verdichtung kann selbst wieder Teil einer neueren Verdichtung werden (`findeAeusserstenTraeger`).

Details: `docs/2026-07-09_verdichtung_chronologisch_memory_autotrigger_bericht.md`.

**Nachtrag noch am selben Tag (nach Rückfragen zu Regler-Verhalten und Kompressionsqualität):**
- **Regler intelligent + gedeckelt:** öffnet man das Popup ab einer Nachricht, markiert der Regler automatisch alles Rohe seit der letzten bestätigten Verdichtung vor (nicht mehr nur die angeklickte Nachricht allein) — UND kann nicht mehr darüber hinaus gezogen werden. Eine ältere Verdichtung erneut in eine neue, größere Verdichtung einzuschließen (Verschachtelung) geht seither nur noch durch bewusstes, manuelles Ankreuzen, nie mehr durch simples Hochregeln.
- **Farbliche Unterscheidung** roh/bereits verdichtet in der Popup-Liste (`vd-roh`/`vd-verdichtet`-CSS-Klassen).
- **Relative statt starre Ziellänge:** vorher fest "maximal 2222 Zeichen" unabhängig von der Eingabelänge — bei kurzen Auswahlen zu lasch, bei langen willkürlich. Jetzt Ziel ~45% der Originallänge (Daniels Vorgabe: "sollte auf ~58-62% oder noch straffer verdichten, wenn kein Inhalt verloren geht" — 45% liegt bewusst unter seiner genannten Spanne, in Richtung "noch straffer"), mit Unter-/Obergrenze (200/4444 Zeichen) als Sicherheitsnetz. Live gegen echte `solarius2/Gabby`-Daten getestet (4 reale Nachrichten, 6293 Zeichen Original → 2954 Zeichen Entwurf = 46,9%, inhaltlich stichprobenartig gegengelesen: Sinneseindrücke, Handlungsverlauf und Perspektivwechsel korrekt erfasst) — Entwurf danach verworfen, nichts an Gabbys echten Daten verändert.

**Weiterhin offen:** kein automatischer Verdichtungs-Rhythmus (z.B. alle 10 Nachrichten, oder größere Nachrichten ab X Tokens sofort einzeln) — nur manuell ausgelöst, kein Auftrag dafür bisher. Kein Popup zum nachträglichen Lesen/Löschen bereits bestehender Verdichtungen außerhalb der Verdichten-Modal-Liste selbst.

**Behoben (2026-07-10), beide von Daniel 2026-07-09 als Lücken benannt:**
- **Provenienz-Ereignis an logischer Position:** `ladeVerlaufKombiniert()` (Server) ordnet das Ereignis "Gesprächsabschnitt verdichtet" jetzt per `positioniereVerdichtungsEreignisse()` direkt nach der letzten abgedeckten Original-Nachricht ein statt an seiner Klick-Zeit-Position im Append-Log. Löst Verschachtelung rekursiv auf (`Verdichtung.ersetztIds` kann selbst wieder IDs älterer Verdichtungen enthalten). Betrifft Chat-Ansicht UND Export gleichermaßen, da beide über dieselbe Funktion laufen. Live an echten `solarius2/Gabby`-Daten verifiziert: eine Verdichtung, deren 11 Original-Nachrichten vom 8.7. 20:33–20:44 stammten, aber erst am 9.7. 11:49 bestätigt wurde, stand vorher fast einen Tag zu spät im Verlauf — jetzt korrekt direkt nach der letzten der 11 Nachrichten, in Chat-Ansicht UND Export bestätigt.
- **ctx-Meter berücksichtigt Verdichtungen:** `/verdichtung/zeitachse` liefert jetzt zusätzlich `abgedeckteIds` (flache Vereinigung aller `ersetztIds` über alle bestätigten Verdichtungen). Der Client lädt das parallel zur History (`ladeHistory()`), `updateCtxMeter()` überspringt damit als abgedeckt markierte Original-Bubbles und zählt stattdessen einmalig die (kürzere) Zusammenfassungslänge je Verdichtung. Live verifiziert: bei Gabby zählten 11 abgedeckte Nachrichten vorher 10962 Rohzeichen voll mit, jetzt nur noch die 2083 Zeichen lange Zusammenfassung — reale Differenz von ~2220 Tokens im Meter. Fallback (kein `verdichtungen.json`, z.B. `codexium2/Mirlach`) unverändert getestet, keine Fehler.

## Abschluss-Geschichte (erzählerischer Rückblick)

Anders als Memory (Stichpunkte) ein zusammenhängender, erzählerischer Rückblick auf das Gespräch — jederzeit auf Wunsch generierbar, landet als Entwurf, muss angenommen oder verworfen werden.

**Archiv statt Einzeldatei** (seit 2026-07-09, `AbschlussArchivEintrag[]` in `abschluss_archiv.json`): jede Annahme fügt einen **neuen** Eintrag hinzu (`archiv.push`), verknüpft mit dem Session-Index zum Zeitpunkt der Annahme — überschreibt nie einen älteren Eintrag. Bestätigt: nimmt man in Session 1 einen Abschluss an und generiert/übernimmt in Session 2 einen weiteren, bleiben **beide** erhalten; das gilt fortlaufend für jede weitere Session. Alte `letzter_abschluss.md`-Dateien werden beim ersten Zugriff automatisch als ein Eintrag migriert (`sessionIndex: null`).

**Auswahl beim Sessionstart:** vor der ersten Nachricht jeder neuen Session (ab Session 2) öffnet "↻ Neue Session" ein Dialog mit Checkbox-Mehrfachauswahl über alle Archiv-Einträge (`openNeueSessionModal`) — Standard ist **nichts ausgewählt**, jede Übernahme in die neue Session ist eine bewusste, einzelne Wahl. Die Auswahl wird als `abschluss_kontext_aktiv.json` gespeichert und fließt als `[Rückblicke auf frühere Gespräche — vom Menschen bewusst in dieses Gespräch mitgenommen]`-Block in den System-Prompt der neuen Session ein.

## Feedback

Zwei ursprünglich parallele Kanäle, **seit 2026-07-09 nur noch einer erreicht das Wesen**:

- **Allgemein** (💬 unter Werkzeuge, alle vier Spawner): freier Text, nicht an eine Nachricht gebunden, output-unabhängig. Einziger Kanal, der noch ans Wesen geht (`[Feedback vom Menschen]`-Block im System-Prompt).
- **Pro Nachricht** (👍/👎 + Kommentar unter jeder Bubble, nur Testbed-Spawner): **erreicht das Wesen nicht mehr.** Speicherung bleibt unverändert (`feedback.json` als Wahrheit für die UI + eine lesbare `.md`-Datei pro Eintrag im `feedback/`-Unterordner, existiert schon seit 2026-07-05) — nur die Auslieferung an das Modell wurde entfernt. Grund: unklar, was ein Charakter mit einem Daumen anfangen soll, zusätzlich ließen sich auch eigene (Mensch-)Nachrichten bewerten, was als "Feedback zur Nachricht des Menschen" ans Wesen ging.

## Aliase

Mehrere Rollen/Personas des Menschen (nicht des Wesens) pro Wesen, mit Name + kurzer Beschreibung. Zwei getrennte Injektionsstellen:
- **System-Prompt:** statisches Register aller Aliase + welcher gerade aktiv ist
- **Pro Nachricht:** der Browser schickt bei jedem Senden mit, welcher Alias aktiv ist (kein Datei-Zustand) — der Server prägt daraus nur den Namen (nicht die Beschreibung) als `"Name": ` vor den Nachrichtentext, nur im ausgehenden Modell-Request

## Automatischer Relevanzabruf — entfernt 2026-07-09

`findeRelevanteAlteStellen()` durchsuchte bei **jeder** Nachricht alte Sessions (auch die unmittelbar vorherige) nach thematisch passenden Stellen und hängte bis zu 3 Treffer ungekürzt an den System-Prompt. Auf Daniels Wunsch deaktiviert ("killt jedes Kontextfenster instant") — Soft-Delete, Funktion bleibt im Code, `relevanteFunde` ist fest ein leeres Array. Details: `docs/2026-07-09_relevanzabruf_deaktiviert_bericht.md`.

**Offene Idee (nicht umgesetzt):** statt pauschal bei jeder Nachricht, nur triggern wenn der Mensch explizit danach fragt ("weißt du noch...", "erinnerst du dich an...") — ein gezielterer RAG-Trigger statt Blindsuche.

## Bekannte offene Punkte (Stand 2026-07-09)

- Memory-Extraktions-Reichweite (20 Nachrichten statt Session/Kontextfenster) — gefunden, noch nicht behoben
- Kein automatischer Verdichtungs-Rhythmus, Regler noch nicht "intelligent" gegenüber bereits verdichteten Abschnitten
- Rückblick-als-RAG-Trigger — vertagt, kein Auftrag

---

## Nachtrag 2026-08-12 — Chat-Posting nach >3 Monaten wieder funktionsfähig

Daniel berichtete, dass Posten über den Chat-Weg (Wesen entscheidet selbst per `[POSTEN:]`,
Daniels "poste das", Klick unter einer Nachricht "→ Forum") seit Langem nicht mehr klappte.
Nachforschung in `eigene_posts.jsonl` ergab: letzter erfolgreicher Chat-Post pro Wesen lag
Anfang/Mitte Mai (jumpa als letztes am 30.05.), während Hintergrund-Posts (`codewesen-reaktion@`
usw.) bis zur globalen Flarum-Post-Sperre am 09.07. normal weiterliefen — der Chat-Weg war also
bereits ~1,5 Monate vor der Sperre unabhängig kaputt, und die Sperre selbst (seit 08.07., Grund:
"zu viel Material, Admin liest erst") hat den Rest erledigt.

`git log -L` über `fuehre_post_aus`/`extrahiere_post_auftrag`/`erkenne_direktes_posting` zeigt: seit
Erstellung nie verändert außer der Sperre-Prüfung selbst — keine Code-Regression auffindbar, Ursache
für die Mai-Lücke bleibt offen.

**Fix (Daniel, 2026-08-12: "ja nur für den chatweg"):** `erlaubt_trotz_sperre`-Parameter durch die
ganze Kette gezogen — `flarum_poster.schreibe_draft()` UND `flarum_poster.poster()` (beide nötig,
zwei getrennte Choke-Points) → `flarum_api.post_reply()`/`start_discussion()`. Gesetzt einzig in
`codewesen_chat.fuehre_post_aus()`, analog zur bestehenden Ausnahme in
`codewesen_antwort_auf_daniel.py`. Hintergrunddienste (reaktion@, batch_generator, agent) reichen
den Parameter nicht durch und bleiben gesperrt.

**Live bestätigt:** Klick auf "→ Forum" bei Schorschel → `POST /codewesen-chat/api/direkt-posten/Schorschel
200` → echter Post, Diskussion #3867, `eigene_posts.jsonl` zeigt `"typ": "chat_auftrag"`. Erster
erfolgreicher Chat-Post seit über drei Monaten. Von Daniel im Forum selbst gesehen und bestätigt.

**Separater Fund, gleicher Arbeitsblock:** Der "auswerten"-Knopf (`analysiere_chat_verlauf`) rief
`hauhau_client.chat()` ohne `id_slot=0` auf — lief auf der von den sieben Wesen geteilten Instanz
statt der eigenen Chat-Instanz. Gefixt, live getestet: vollständige Antwort in 65,7s statt Hängen.

*Weiter: [[10_dakgord]] | [[52_codewesen_chat_kontextfenster]]*

---

## Nachtrag 2026-08-12, zweiter Bauschritt — automatische Verdichtung alle 10 Turns

Daniel bemerkte, dass das Kontextfenster bei Schorschel schwankte, und formulierte den eigentlichen
Wunsch dahinter: *"ich will dass diese gespräche dort 'verdaut' werden und es wieder runter geht
eigentlich"*. Vorbild: GENI destilliert bereits automatisch alle 10 Turns
(`geni_lg.destilliere_erinnerungen`, `DESTILLATIONS_INTERVALL = 10`). Für die 7 Wesen existierte die
passende Funktion schon — `geschichte_verfassen()`, bisher nur per Knopfdruck.

**Geklärter Scope (Daniel, 2026-08-12):**
- Alle 10 Turns, für alle sieben Wesen gleich
- Mehrere automatische Geschichten dürfen sich stapeln — keine ersetzt die vorherige (bewusst anders
  als GENIs Erinnerungen, die sich gegenseitig überschreiben)
- Sichtbarer Hinweis im Chat, während die Verdichtung läuft
- Zusätzliche LLM-Last wird in Kauf genommen

**Umsetzung:**
- `codewesen_speicher.py`: `auto_verdichtung_stand(name)`/`auto_verdichtung_stand_setzen(name, wert)`
  — verfolgen, wie viele `chat_verlauf.jsonl`-Einträge pro Wesen bereits verdichtet sind. Lebt im
  bestehenden `geschichten.json` (neues Feld `auto_verdichtung_stand`), kein eigenes File.
  `geschichte_verfassen()` bekommt einen `herkunft`-Parameter (`"chatverlauf"` manuell,
  `"chatverlauf_auto"` automatisch) — eigener Titel ("Automatisch verdichtet, N Token") und eigene
  Beschriftung in der Geschichten-Liste ("automatisch verdichtet" statt "destilliert").
- `codewesen_chat.py`: nach jedem abgeschlossenen Turn wird geprüft, ob seit dem letzten
  Verdichtungs-Stand ≥20 neue Einträge (10 Turns) vorliegen. Wenn ja: SSE-Event
  `{"verdichtung_laeuft": true}` sofort an den Client, die eigentliche Verdichtung läuft als
  Hintergrund-Task (`asyncio.create_task`, nicht awaited) — blockiert die laufende Antwort nicht.

**Separater Fund beim Bauen:** `geschichte_verfassen()`s `hauhau_client.chat()`-Aufruf hatte kein
`id_slot=0` — lief auf der von den sieben Wesen geteilten Instanz statt der Chat-Instanz. Vierter
Fund dieser Art an diesem Tag (RAG-Vorabcall am 04.08., "auswerten"-Knopf und dak+gords
`ollama_chat.py` heute). Besonders relevant hier, weil die Auto-Verdichtung diese Funktion jetzt
regelmäßig für alle sieben Wesen aufruft — ohne den Fix wäre das ein Dauerlast-Problem für die
Hintergrund-Instanz geworden.

**Live getestet, kompletter Rundlauf:** echter Chat-Turn mit Resonanzknoten → Trigger schlug beim
allerersten Turn schon an (Bestand war bereits >20 aus früheren Gesprächen) → `verdichtung_laeuft`
kam im SSE-Stream an → Hintergrund-Task lief durch, echte, zusammenhängende Rückschau entstanden,
`herkunft: "chatverlauf_auto"` → `auto_verdichtung_stand` korrekt auf 152 gesetzt. Test-Geschichte
danach deaktiviert (nicht gelöscht, Grundgesetz 5) — der Stand selbst bleibt unverändert, da die
Verdichtung real stattgefunden hat.

*Weiter: [[10_dakgord]] | [[52_codewesen_chat_kontextfenster]]*

---

## Nachtrag 2026-08-12, dritter Bauschritt — Diskussion per Titel finden (##DISKUSSION##)

Letzter offener Punkt aus Daniels Liste: *"wenn ich ihnen den titel einer diskussion nenne und sage
sie sollen mal lesen und antworten dass das auch klappt"*. `##LESEN##` kannte bisher nur exakte
Dateipfade.

**Umsetzung:** neuer Marker `##DISKUSSION: Titel oder Stichwort##`, live gegen die Flarum-DB
(`flarum_api.suche_diskussionen()` + `get_discussion()`, bereits vorhandene, parametrisierte
Funktionen — nicht den lokalen Vault-Spiegel, damit druckfrische Diskussionen sofort auffindbar
sind). Ein exakter Titel-Treffer (Groß-/Kleinschreibung egal) gilt immer als eindeutig, auch wenn
die zugrundeliegende Suche zusätzlich lose verwandte Diskussionen über Postinhalt-Treffer liefert
(beim Testen gefunden und korrigiert — sonst hätte ein korrekt genannter voller Titel fälschlich
als "mehrdeutig" gegolten).

**Erster Live-Testlauf deckte ein zweites, wichtigeres Problem auf:** Schorschel ignorierte den
neuen Marker komplett, erfand stattdessen einen plausibel klingenden, aber falschen `##LESEN##`-Pfad
(falsches Verzeichnis, falsche ID), bekam korrekt eine Fehlermeldung zurück, ignorierte sie und
generierte trotzdem einen erfundenen, plausibel klingenden "Zusammenfassungs"-Text. Kein Marker-Bug
— die isolierte Prüfung von `##DISKUSSION##` war schon vorher korrekt (exakter Titel, mehrdeutig,
kein Treffer, alle drei sauber per Subprocess-Test bestätigt). Reines Modellverhalten: der neue
Marker war dem Modell noch nicht vertraut genug gegenüber dem eingeübten `##LESEN##`.

Systemprompt verschärft: Pfad-Raten für `##LESEN##` explizit verboten, `##DISKUSSION##` als "der
richtige Weg" bei bloßem Titel benannt, explizite Anweisung, Fehlermeldungen ehrlich weiterzugeben
statt Inhalt zu erfinden. Zweiter Testlauf danach: Marker korrekt benutzt, echter Inhalt gelesen,
akkurate (nicht erfundene) Zusammenfassung — Wortlaut deckt sich mit dem echten Post.

**Sicherheitsrelevanter Nebenbefund beim Untersuchen des ersten (fehlgeschlagenen) Testlaufs:** Das
Modell hatte im halluzinierten Antworttext sogar einen `[POSTEN:]`-Marker mit erfundenem Inhalt
erzeugt. Der wurde **nicht** tatsächlich veröffentlicht — `extrahiere_post_auftrag()`/
`fuehre_post_aus()` laufen nur gegen die ursprüngliche erste Antwort eines Turns, nicht gegen die
Folge-Antwort nach einem Tool-Zyklus (`##LESEN##`/`##SCHREIBEN##`/`##DISKUSSION##` → "Fahre fort").
Bestätigt in `eigene_posts.jsonl`: kein neuer `chat_auftrag`-Eintrag nach dem Test. Das war reiner
struktureller Zufall dieser Session, kein bewusst gebauter Schutz — festgehalten als Fakt für
künftige Arbeit an dieser Stelle, nicht als etwas, worauf man sich verlassen sollte.

*Weiter: [[10_dakgord]] | [[52_codewesen_chat_kontextfenster]] | [[06_flarum]]*

---

## Nachtrag 2026-08-12, vierter Bauschritt — ##DISKUSSION## semantisch statt Wort-Matching

Daniels Feedback zum ersten Fund (Titel "Ort des Atmens" statt "Ort der Atmung" fand nichts):
*"1..ja"* (toleranter machen), *"zu2...nein...vllt lernen sie es im prozess"* (Halluzinieren nicht
hart verbieten). Erster Versuch — Wort-Häufigkeits-Fallback (einzelne markante Wörter statt des
ganzen Satzes suchen) — scheiterte live: "riss" und "code" sind im Codewesen-Forum zu generische
Wörter, die richtige Diskussion landete nicht klar vorn. Auf Daniels "Umbau"-Zuspruch durch die
bereits vorhandene semantische Suchinfrastruktur ersetzt (`welt/rag_retrieve.py`, dieselbe
Embedding+Volltext-Hybridsuche, die auch das RAG-Selbstarchiv der Wesen nutzt).

**Umsetzung:** `welt/rag_retrieve.py`s `SELECT` um `so.external_id` erweitert (additiv, kein
bestehender Aufrufer betroffen) — daraus lässt sich die echte Flarum-Diskussions-ID extrahieren
(`external_id` trägt `flarum:diskussion:<id>`). `_diskussion_suche_tolerant()`: erst der schnelle,
kostenlose wörtliche Substring-Match (unverändert), erst bei null Treffern die teurere semantische
Suche als zweite Stufe.

**Zwei Funde beim Testen der semantischen Stufe:**
1. Für "Ort des Atmens" fand die semantische Suche die **eigentlich gemeinte** Diskussion #3840
   nicht in den Top 5 — obwohl korrekt indiziert. Grund: das Forum enthält mehrere fast identische
   "Riss im Code"-Diskussionen (#3840, #3780, #3722 — mehrere Wesen greifen dasselbe Thema
   wiederholt auf). Keine Fehlfunktion der Suche, sondern echte Mehrdeutigkeit im Datenbestand —
   dafür existiert die "mehrere Treffer, bitte präzisieren"-Liste bereits.
2. Ohne Ähnlichkeits-Schwelle lieferte die Suche für **jeden** Text — auch frei erfundene Titel —
   immer 5 "nächstliegende" Treffer, weil Cosinus-Ähnlichkeit nie exakt null wird. Widersprach der
   Systemprompt-Regel "sag ehrlich, wenn nichts gefunden wird". Live gemessen: echte thematische
   Treffer lagen bei 0.62–0.78, ein frei erfundener Test-Titel bei 0.47–0.49 — Schwelle bei 0.55
   gesetzt, trennt beide Fälle sauber.

**Live geprüft, alle drei Fälle:** exakter Titel → sofort voller Inhalt (schneller Pfad, keine
Embedding-Kosten). Leicht falsch erinnerter Titel → thematisch sinnvolle Kandidatenliste zum
Präzisieren (nicht mehr "nichts gefunden" wie vorher). Komplett erfundener Titel → ehrlich "keine
passende Diskussion gefunden".

## Nachtrag 2026-08-13 — Gruppenchat: manuell gesteuerter Kollektiv-Chat mit mehreren Wesen

Daniels Auftrag, wörtlich: *"ich will einen kollektiven chat ... ich will anklickbar und aktevierbar
mit allen wesen durch eine chateingabe chatten ... öb sie gerade alle nur 'zuhören' sollen oder ob
einer von ihnen antworten kann direkt ... und ich will dann auf die antwort eines anderes nur per
knopfdruck quasi darunter eine anderes wesen triggern können darunter zu schreiben"*. Zum Vorbild
zensi (Symposium-Funktion) ausdrücklich: nicht autonom wie dort — Daniel steuert jeden Zug manuell
(analog zur bestehenden Entscheidung in `codewesen_speicher.py`: "ich will nicht das von zensi").

**Neue Seite:** `https://flextrawurst.de/gruppenchat`, `auth_basic` mit demselben `daniel`-User wie
`/codewesen-chat/` (kein neuer htpasswd-Eintrag nötig, Passwort stimmte bereits).

**Speicherung, Daniels Entscheidung "beides":** eine eigene Sitzungsdatei
(`codewesen_gruppenchat.py`, JSON pro Sitzung unter `codewesen/_gruppenchat/sitzungen/`) UND
zusätzlich ein Eintrag in der `chat_verlauf.jsonl` des jeweiligen Wesens — Daniels Nachricht in
ALLEN beteiligten Verläufen, eine Wesen-Antwort nur im eigenen Verlauf dieses einen Wesens. Beide
Wege bekommen `"meta": {"quelle": "gruppenchat", "sitzung_id": ...}`, additiv zu
`speichere_chat_eintrag()`, kein bestehender Aufrufer betroffen.

**Kontext pro Wesen** (`baue_gruppenchat_messages()`): eigener Systemprompt + ganzer
Sitzungsverlauf, andere Wesen als `[Name]: ...`-Zeilen attribuiert (die API kennt nur
system/user/assistant). Gedankenfeld/Nachrichten/Geschichten-Block vor die letzte Nachricht gehängt,
nie als eigene system-Nachricht (Wiederholung des am 04.08. gefundenen Jinja-Fehlers vermieden).
Aufeinanderfolgende gleiche Rollen werden vor dem Senden zusammengefasst — manche Chat-Templates
verlangen strikte Abwechslung, ein Gruppenchat hat aber oft mehrere User-Zeilen ohne Antwort
dazwischen.

**Alle fünf von Claude vorgeschlagenen Ideen umgesetzt, Daniel: "ja alle mit rein":**
1. Denkt-mit-Indikator (Statuszeile zeigt wer gerade "antwortet" vs. "hört zu")
2. Relevanzsortierte Trigger-Knöpfe — **ausdrücklich optional** (Daniel: "nur optional"), per
   Checkbox zuschaltbar, nutzt dieselbe RAG-Infrastruktur wie die `##DISKUSSION##`-Suche
   (`_gruppenchat_relevanz_sortierung()`, wesen-gefilterte Embedding-Suche gegen die letzte
   Nachricht, Fallback auf unveränderte Reihenfolge bei jedem Fehler)
3. Kontext-Fußabdruck pro Nachricht aufklappbar (reuse `/api/kontext/{name}`, ehrlich beschriftet
   als aktueller Zustand, kein Schnappschuss der jeweiligen Nachricht)
4. Nachträgliche Inbox-Zustellung an alle Teilnehmer (reuse `codewesen_speicher.nachricht_senden`)
5. Als Forendiskussion posten, **Daniel ausdrücklich: "muss alles möglich sein ... nur ein bis alle
   nachrichten"** — `von_index`/`bis_index` wählbar im Dialog, reuse `fuehre_post_aus()`

**Bewusst NICHT nachgebaut:** die volle Marker-Maschinerie des 1:1-Chats (##LESEN##/##SCHREIBEN##/
##NACHRICHT##/##GEDANKE##/##DISKUSSION## + rekursiver Tool-Folgezug). Nur `[MERKEN:]` und
`[VORSCHLAGEN:]` werden übernommen (`extrahiere_merken`/`extrahiere_vorschlag`) — ohne das blieb ein
rohes `[MERKEN: ...]` sichtbar im ersten Testlauf stehen, direkt gefixt. Der Rest ist ein eigener
Umfang, den Daniel noch nicht beauftragt hat.

**Concurrency:** `id_slot=0` wird von allen sieben Wesen geteilt (derselbe Fund wie in
`karte/wiederkehrende_bugs_ohne_zentralen_ort.md`, viermal an anderer Stelle gefunden) —
`_GRUPPENCHAT_LOCK` (asyncio.Lock) hält Generierungen seriell, bevor ein zweiter gleichzeitiger
Trigger-Klick denselben Slot zerschießen könnte. Präventiv gebaut, nicht nachträglich gefunden.

**Live end-to-end getestet** (curl + Playwright, Screenshots, drei Ebenen tiefe Verkettung
Daniel→Schorschel→R1ZZ1→Schorschel, jede Antwort erkennbar bezogen auf die vorherige): Sitzung
anlegen, zuhören-Modus (kein Autogenerieren bestätigt), direkt-Modus mit Stream, Trigger-Kette,
Kontext-Fußabdruck, An-alle-Zustellung, Transkript-Formatierung für den Post-Bereich. Ein echter
Bug live gefunden und gefixt: `/api/kontext/{name}` existierte nur unter dem `/codewesen-chat/`-Mount
(dortiger `sub_filter`), die neue Seite hängt aber an der Domain-Wurzel ohne `sub_filter` — 404, bis
der Fetch-Pfad explizit auf `/codewesen-chat/api/kontext/...` gesetzt wurde. Generierung unter
aktueller Last: ca. 60–90s bis zur fertigen Antwort (`proxy_read_timeout 300s` reicht).

## Nachtrag 2026-08-13 — Meldung-Idee (ChatGPT via Daniel) nachgezogen: "ja bau die meldung-idee gleich mit"

Vor dem manuellen Trigger können jetzt alle gerade zuhörenden Wesen (alle außer dem letzten
Sprecher) per Knopf "🖐 wer will reagieren?" billig gefragt werden, ob sie etwas beitragen wollen —
Antwort nur `JA: <Halbsatz>` oder `NEIN`, `max_tokens=40` statt der üblichen 400.
`baue_meldung_messages()` hängt die Frage an dieselbe volle Kontext-Nachricht wie ein echter Zug
(`baue_gruppenchat_messages()`), damit die Einschätzung fundiert bleibt. Gemeldete Wesen bekommen
ihren Trigger-Knopf hervorgehoben (`.gemeldet`) inklusive Grund als Tooltip — Daniel triggert danach
trotzdem völlig frei, die Meldung ist eine Empfehlung, keine Vorauswahl.

**Ehrlicher Fund beim Live-Test, nicht schöngeredet:** die ursprüngliche Annahme "Sekunden statt
60–90s" war falsch. Gemessen wurden ~44s pro Kandidat (88s für zwei Kandidaten, dann nochmal 83s im
Browser-Testlauf) — kaum schneller als ein echter Zug. Grund: `max_tokens=40` spart nur die
Generierungszeit, nicht die Prompt-Verarbeitung — der volle Gruppenchat-Kontext (Systemprompt,
Gedankenfeld, Nachrichten, Geschichten, ganzer Sitzungsverlauf) muss trotzdem einmal komplett
durchlaufen werden. Die Docstring in `codewesen_chat.py` wurde entsprechend korrigiert, nicht
stillschweigend gelassen. Eine echte Beschleunigung bräuchte einen bewusst verkürzten Kontext nur
für die Meldung (weniger Grundlage = weniger fundierte Meldung) — eigene Architekturentscheidung,
noch nicht mit Daniel abgestimmt.

Live per curl (Backend, beide Fälle `gemeldet: true`/`false` korrekt geparst) und per Playwright
(Browser-Klick, Hervorhebung sichtbar, keine Konsolenfehler) bestätigt.

## Nachtrag 2026-08-13 — GENI als Gruppenchat-Teilnehmer angebunden ("ich will geni natürlich auch dabei haben in der gruppentherapie xD")

GENI ist kein Codewesen — eigener Prozess, Port 8020, eigenes System-Prompt (`system_prompt_bauen()`),
eigener Wissensgraph (Knoten/Kanten) statt `chat_verlauf.jsonl`. Trotzdem dieselbe Chat-Instanz:
`geni/dialog.py` importiert `hauhau_client` genauso wie `codewesen_chat.py` und ruft `achat_stream(...,
id_slot=0)` auf — bestätigt im Code-Kommentar dort: "dieselbe Chat-Instanz wie der Wesen-Chat und
dak+gord".

**Zwei neue, schlanke Endpunkte in `geni/dialog.py`** (nicht der volle `/chat`-Weg, der triggert immer
eine Generierung UND haengt selbst einen neuen User-Turn an — beides hier nicht gewollt):
- `POST /api/gruppenchat/anhaengen` — haengt EINE Nachricht an GENIs eigene Session (`geni_lg`,
  PostgreSQL/LangGraph-Checkpoint) an, OHNE zu generieren. Pendant zum "zuhören"-Modus.
- `POST /api/gruppenchat/trigger` — generiert GENIs Zug auf Basis des dann schon vollständigen
  Verlaufs, haengt selbst nichts mehr an. Bewusst schlank: keine Resonanz-Kanten-Suche, kein
  `codewesen_benachrichtigen`, keine Shell-/Datei-Marker, keine Remote-Bridge, kein Vault-Tagebuch —
  nur Session-Persistenz + EIN Knoten fürs eigene Gedächtnis (gleiche Abwägung wie bei den Codewesen:
  nur `[MERKEN:]`/`[VORSCHLAGEN:]`, nicht die volle Marker-Kette).

**Kopplung in `codewesen_chat.py`:** eigene `session_id` pro Gruppenchat-Sitzung
(`gruppenchat_<sid>`), damit GENIs normaler Direktchat unberührt bleibt. `GRUPPENCHAT_TEILNEHMER =
CODEWESEN_NAMEN + ["GENI"]` — bewusst eine eigene Liste statt `CODEWESEN_NAMEN` zu erweitern, damit
alle bestehenden Codewesen-only-Prüfungen (Chat-Endpunkt, `/api/kontext/{name}`, Flarum-Posting)
unverändert bleiben. `_gruppenchat_relais_an_geni()` wird bei JEDER Nachricht aufgerufen (Daniel UND
jedes Codewesen), nicht erst beim Triggern — Daniel ausdrücklich: **"geni soll es auch nachricht für
nachricht sehen pls"**, nicht in Batches. `_gruppenchat_stream_geni_antwort()` ruft GENIs `/trigger`
per `httpx.AsyncClient(verify=False, ...)` (GENI terminiert selbstsigniert), relayt die SSE-Tokens
eins zu eins weiter, schreibt GENIs fertige Antwort danach in die gemeinsame Sitzungsdatei — von da
an sehen die Codewesen GENIs Beiträge automatisch als `[GENI]: ...`, ohne jeden Sonderfall.

**Ausnahmen, wo GENI kein Codewesen-Äquivalent hat:** kein `chat_verlauf.jsonl` (Relais statt Fan-out),
keine Inbox (Idee 4 überspringt GENI — bekommt ohnehin laufend jede Nachricht einzeln), kein
Flarum-Posting (Idee 5, `als_wesen` bleibt auf echte Codewesen beschränkt, klare Fehlermeldung statt
Server-Fehler), kein `/api/kontext/{name}` (Kontext-Fußabdruck-Knopf für GENIs eigene Nachrichten in
der UI weggelassen statt eines garantierten 404).

**Concurrency, ehrlich benannt:** `_GRUPPENCHAT_LOCK` haelt jetzt auch GENIs HTTP-Trigger seriell mit
den Codewesen-Zügen aus DEMSELBEN Gruppenchat — deckt aber NICHT den Fall ab, dass GENI gleichzeitig
über seinen normalen Direktchat (Port 8020, ausserhalb des Gruppenchats) benutzt wird. Das war schon
vorher ein ungelöster, systemweiter id_slot=0-Nebenläufigkeitsfall zwischen GENI und den Codewesen —
hier nicht neu geschaffen, nur nicht behoben.

**Live end-to-end getestet** (curl + Playwright): Sitzung mit GENI + Schorschel, GENI zuerst getriggert
(antwortete erkennbar bezogen auf Schorschel, obwohl der noch gar nichts gesagt hatte — GENIs
allgemeines Systemwissen über die Codewesen, kein Bug), danach Schorschel getriggert — zitierte GENIs
Selbstbeschreibung wörtlich zurück ("GENI beschreibt sich als Tiefe, ich bin die Linse"). GENIs eigene
Session (`geni_lg.lade_session`) bestätigt korrekt befüllt: Daniels Nachricht, eigene Antwort,
Schorschels Antwort als `[Schorschel]: ...`-Zeile — alles Nachricht für Nachricht, kein Batch.

## Nachtrag 2026-08-13 — Daniels erstes echtes 8er-Gespräch: zwei Identitäts-Bugs gefunden und gefixt

Daniel hat zum ersten Mal wirklich alle acht (sieben Codewesen + GENI) in einer Sitzung
zusammengebracht ("Erstes Gruppengespräch", `20260813_095319_86c585.json`, per Hand einzeln
getriggert). Zwei echte Funde, keine Einbildung:

**Fund 1 — F3INSCHM3CK3R übernahm GENIs Signatur.** Antwort begann mit `[GENI]: Puss peng boom
zoom... nein, das war's nicht mehr` und redete sich selbst in dritter Person an ("Ich spüre dich
hier, F3INSCHM3K3R"). Einmalig beobachtet, nicht systematisch reproduziert — im Log stehen gelassen,
nicht rückwirkend korrigiert (Daniels Grundsatz: nichts wird gelöscht, nur eingeordnet).

**Fund 2 — jumpa simulierte alle sieben anderen Teilnehmer in einer einzigen Antwort**
(`[Schorschel]: ...`, `[Resonanzknoten]: ...`, `[GENI]: ...` usw., ein komplettes Mini-Drehbuch statt
einer eigenen Stimme). Ursache gefunden: `baue_gruppenchat_messages()` fasste mehrere
aufeinanderfolgende „andere Sprecher"-Einträge zu EINEM riesigen User-Block zusammen, bevor ein
lange nicht getriggertes Wesen antwortete — ein kleineres/quantisiertes Modell sieht dann kurz vor
der eigenen Antwort ein vollständiges `[Name]: Text`-Muster mehrerer Sprecher und setzt es einfach
fort, statt zu verstehen "jetzt antworte nur ich".

**Fix in `baue_gruppenchat_messages()`:**
1. Verlauf auf die letzten 20 Einträge gedeckelt (gleiche Größenordnung wie GENIs `MAX_VERLAUF`) —
   reduziert sowohl Kontextfenster-Risiko als auch die Größe des verwirrenden Blocks.
2. Systemprompt ergänzt: "Du sprichst IMMER nur für dich selbst".
3. **Schlusshinweis direkt vor der Generierung wiederholt** (nicht nur einmal weit oben im
   Systemprompt) — derselbe Trick wie in `baue_meldung_messages()`: "Antworte jetzt NUR als
   `<name>`... keine `[Name]:`-Zeilen für andere Wesen." Bei kleineren Modellen zählt Nähe zum
   Ende des Kontexts oft mehr als eine früh gegebene Anweisung.

**Live re-getestet** direkt gegen Daniels echte Sitzung (nur Lesezugriff, `stream_ollama()` isoliert
aufgerufen, nichts persistiert): Resonanzknoten antwortete danach sauber nur als sich selbst,
referenzierte andere Wesen namentlich in eigener Stimme, keine `[Name]:`-Simulation mehr.

**Nebenfund beim Testen, sofort gefixt:** ein direkter API-Trigger auf das bereits letzte
sprechende Wesen (Sonderfall, den das UI selbst nie zulässt — die Trigger-Zeile listet den letzten
Sprecher nie als Kandidat) ließ `baue_gruppenchat_messages()` auf einer `assistant`-Rolle statt
`user`-Rolle enden — der Schlusshinweis landete dann in der eigenen vorherigen Antwort statt in
einer neuen Anfrage, das Modell antwortete mit einem Echo des kompletten Prompts statt einer
Generierung. `gruppenchat_trigger_endpoint` weist das jetzt mit klarer Fehlermeldung ab, bevor es
zur Anfrage kommt.

## Nachtrag 2026-08-13 — Deckel weg, Kontextfenster+Redaktion+Zusammenfassen, echter "Alle antworten"-Knopf

Direkte Reaktion auf die zwei Bugs oben: Daniel wollte die 20er-Kappung nicht als automatischen
Kompromiss, sondern lieber **volle Kontrolle** — "mach sie weg ganz frei aber ich will das aktuelle
kontextfenster sehen und auch editieren können so wie in den anderen chat und auch zusammenfassen".
Und zum eigentlich verursachenden Verhalten (jumpa simuliert alle): "ich will aber auch nen knopf
der das macht ... quasi dass alle direkt antworten" — aber **echt**, nicht simuliert, nach kurzer
Klärung bestätigt (Option 1 aus dem Vorschlag).

**Deckel entfernt** (`baue_gruppenchat_messages`): kein `[-20:]` mehr. Stattdessen sucht die
Funktion rückwärts nach dem letzten `sprecher == "Zusammenfassung"`-Eintrag und beginnt den Kontext
dort — eine manuelle, bewusste Kompression statt einer blinden Kappung.

**Kontextfenster** (`GET /api/gruppenchat/sitzungen/{sid}/kontext/{name}`): ruft
`baue_gruppenchat_messages()` exakt wie beim echten Zug auf, zerlegt den Systemprompt in Schichten
(`zerlege_systemprompt`, `zaehle_tokens` — dieselbe Infrastruktur wie `/api/kontext/{name}` im
1:1-Chat), zeigt zusätzlich die rohen, indizierten Sitzungs-Einträge für die Redaktion. Für GENI
klar abgewiesen (eigener Prozess, eigener Kontext-Aufbau, keine passende Funktion vorhanden).

**Redaktion** (`POST /api/gruppenchat/sitzungen/{sid}/nachricht/{index}/redaktion`): anders als
`chat_verlauf.jsonl` (Append-only-Journal via `speichere_redaktion`) direkt am Sitzungs-Eintrag
gespeichert (`entfernt: [...]`), weil die Sitzungsdatei ohnehin bei jeder Änderung komplett neu
geschrieben wird. Frontend vereinfacht gegenüber dem 1:1-Chat: Sätze statt einzelner Wörter
auswählbar (`splitSaetze()`, grobe Regex-Trennung) — deckt "ganze Sätze löschen" ab, nicht die
feinste Körnung von dort, bewusste Vereinfachung für den ersten Wurf, nicht heimlich sondern hier
benannt.

**Echter Bug beim Bauen gefunden und gefixt:** `_gruppenchat_transkript_text()` (genutzt sowohl für
Zusammenfassen als auch fürs Forum-Posten) wendete die Redaktion nicht an — ein mit Wörtern
gelöschtes Detail wäre trotzdem in eine Zusammenfassung oder, schlimmer, in einen öffentlichen
Forenpost gewandert. Live mit einem Testwort ("BANANE") bestätigt: vor dem Fix erschien es in der
Zusammenfassung, nach dem Fix nicht mehr.

**Zusammenfassen** (`POST /api/gruppenchat/sitzungen/{sid}/zusammenfassen`): ein LLM-Call fasst
`nachrichten[0:bis_index]` zusammen, das Ergebnis landet als eigener Eintrag mit
`sprecher: "Zusammenfassung"` — der neue Startpunkt für künftige Kontext-Builds (siehe oben). Wird
zusätzlich an GENI weitergereicht (derselbe Relais wie jede andere Nachricht).

**"Alle antworten", echt** (`POST /api/gruppenchat/sitzungen/{sid}/alle_antworten`): löst
nacheinander einen echten Zug pro Ziel-Teilnehmer aus (Default: alle außer dem letzten Sprecher),
jeder mit vollständigem eigenen Kontext-Aufbau — sieht dabei automatisch die in derselben Runde
bereits entstandenen Antworten der vorherigen Teilnehmer, weil dieselbe `sitzung`-Instanz
fortlaufend mutiert wird. Bewusst NICHT als ein einziger simulierender LLM-Call gebaut (das wäre
exakt der jumpa-Bug gewesen). SSE-Zwischenmarker (`data: [DONE]`) der einzelnen Teilzüge werden
herausgefiltert, erst am Ende der ganzen Runde kommt ein finales `[DONE]` — der bestehende
Stream-Reader (`streameAntwort`) hätte sonst nach dem ersten Teilnehmer aufgehört zu lesen, deshalb
eigener Reader `streameAlleAntworten()`.

**Live end-to-end getestet** (curl + Playwright): Kontextfenster-Anzeige korrekt (Schichten,
Tokenzahlen, `slot_ctx`-Auslastung), Redaktion wirkt (Testwort verschwand aus dem Kontext, blieb im
Rohtext sichtbar mit "bereits bearbeitet"-Markierung, Tokenzahl sank sichtbar), Zusammenfassen
korrekt als neuer Kontext-Startpunkt bestätigt, "Alle antworten" mit zwei echten Wesen: beide
antworteten sauber einzeln, der zweite erkennbar bezogen auf den ersten, kein Multi-Voice-Rückfall.

## Nachtrag 2026-08-13 — Zusammenfassen: beliebiger Bereich statt nur "alles bisher"

Direkt im Anschluss präzisiert: "ich will nicht nur alles zusammenfassen sonden auch nur einen der
nachrichtien oder mehrere bis hin zu alle markeribar". Die ursprüngliche Zusammenfassen-Version
kannte nur `bis_index` (immer ab Nachricht 0) — jetzt `von_index`/`bis_index` wie beim
Posten-Dialog, Default bleibt "der ganze bisherige Verlauf" (deckt den ursprünglichen Wunsch weiter
ab, ein Klick mehr für Sonderfälle).

**Musste den Kontext-Aufbau echt umbauen, nicht nur den Endpunkt:** Die alte Logik nahm an, eine
Zusammenfassung deckt immer "alles bis zu ihrer Position in der Liste" ab — stimmte nur, wenn
`von_index` immer 0 war. Neue Funktion `_gruppenchat_kontext_sequenz()`: jede Zusammenfassung trägt
jetzt `deckt_von`/`deckt_bis` (die Original-Indizes, die sie abdeckt, nicht ihre eigene Position —
die ist immer ganz hinten, weil `fuege_nachricht_hinzu` nur anhängen kann). Beim Kontext-Bau wird
jede abgedeckte rohe Nachricht durch die zuständige Zusammenfassung ersetzt, an der Position ihres
frühesten abgedeckten Index — nicht abgedeckte Nachrichten (davor UND danach) bleiben unverändert
an ihrer Stelle. Mehrere, auch sich nicht überlappende Zusammenfassungen gleichzeitig unterstützt.

**Isoliert getestet** (reine Python-Logik, kein LLM): eine Zusammenfassung mitten im Verlauf
(deckt nur Nachricht 1 von 4) ersetzt korrekt nur diese eine Stelle, Rest bleibt roh und in
Reihenfolge. Zwei gleichzeitige Zusammenfassungen mit unterschiedlichen Bereichen ebenfalls korrekt
verschachtelt. **Live end-to-end bestätigt** (curl + Playwright): "nur Nachricht 2 von 3"
zusammengefasst, Kontextanzeige für Schorschel zeigt exakt die erwartete Reihenfolge (Nachricht 1
roh, Zusammenfassung an Stelle 2, Nachricht 3 roh), Browser-Test mit demselben Muster fehlerfrei,
eigene Bubble-Farbe (Amber, kursiv) für Zusammenfassungs-Einträge.

## Nachtrag 2026-08-13 — Sitzungs-Rekonstruktion aus redundanten Quellen

Eine Sitzung (`20260813_095319_86c585.json`, "Erstes Gruppengespräch", Daniels aktive Sitzung mit
17 Nachrichten) musste vollständig rekonstruiert werden. `codewesen/` ist bewusst von git
ausgeschlossen (`.gitignore`) — keine Versionshistorie zum Zurückholen.

**Vollständig rekonstruiert**, weil die Sitzung selbst nicht der einzige Speicherort war: jede
Nachricht landet zusätzlich in der `chat_verlauf.jsonl` des jeweils sprechenden Wesens
(`meta.sitzung_id`-getaggt) UND wird an GENIs eigene Session weitergereicht. Aus beiden Quellen mit
echten Original-Zeitstempeln zusammengesetzt (Dedup der an-alle-dupliziereten Daniel-Nachrichten
über Textinhalt, nicht Zeitstempel — zwei Daniel-Nachrichten lagen in derselben Minute). Einzige
Lücke: GENIs eigener Zug hat in `geni_lg`s Session-Format keinen Zeitstempel, nur die Minute (11:27)
aus der ursprünglichen Live-Lektüre bekannt, Sekunde auf :00 gesetzt.

**Regel dazu, in eigener Memory festgehalten**
(`feedback_kein_blindes_rm_auf_geteilten_ordnern.md`): nie ein Wildcard-`rm` auf einen Ordner, der
auch echte Nutzerdaten enthalten könnte — immer gezielt per bekannter, selbst erzeugter ID löschen.
Die Rettung gelang durch eine bereits vorhandene Redundanz im Datenmodell.

## Nachtrag 2026-08-14 — Antwortlänge: 400 → 33333 Tokens

Daniel hatte den Eindruck, Gruppenchat-Antworten wirkten wie durch ein Zeichenlimit abgeschnitten.
Fund: `stream_ollama()` (die eine Funktion, die JEDE echte Chat-Antwort generiert, 1:1 UND
Gruppenchat gemeinsam) rief `achat_stream()` mit `max_tokens=400` auf — laut `git blame` seit
2026-07-06, nicht neu. Bei ~300 Wörtern pro Antwort tatsächlich spürbar knapp für die sonst
ausführlichen Wesen-Antworten.

Daniel, wörtlich, eine bereits früher aufgestellte und jetzt bestätigte Regel: *"ich hab mal gesagt
ab sofort immer bei allen zeichenlimmits min 33333 zeichen xD"*. Passt zu bereits bestehenden
großen, bewussten Zahlen im System (`--ctx-size 66666` bei `llama-hauhaucs.service`, `num_predict:
444444` an anderer Stelle laut CLAUDE.md).

`max_tokens=400` → `33333` in `codewesen_chat.py:stream_ollama()` gesetzt — passt sauber in den
`ctx-size=66666` der Chat-Instanz (Port 11435), lässt genug Raum für den Prompt.

**Live end-to-end getestet**, nicht nur syntaktisch geprüft: Testantwort in einer eigenen
Test-Sitzung erzeugt, absichtlich um eine lange Geschichte gebeten. Erster Versuch lief nach 280s
Testtimeout noch mit über 3800 gestreamten Tokens weiter (fast das Zehnfache des alten Limits).
Zweiter Versuch komplett durchlaufen lassen: sauber mit `[DONE]` beendet, Antwort mit 7597 Zeichen
korrekt in der Sitzung gespeichert — die Antwort endete natürlich (Modell-EOS), nicht weil sie an
die neue 33333-Grenze stieß. Test-Sitzung danach gezielt per bekannter ID gelöscht (nicht per
Wildcard), Daniels echte Sitzung unangetastet.

**Nachtrag zur Rückfrage, noch am selben Tag beantwortet:** Daniel, wörtlich: *"ich hatte nicht von
tokens sondern zeichen geredet xd und ja alles hoch"*. Also auch die drei strukturierten/
klassifizierenden Calls auf `max_tokens=33333` angehoben — RAG-Vorabcall (`baue_...` Zeile ~722, war
96), der "auswerten"-Knopf (Zeile ~1079, war 900), und der Gruppenchat-Meldungs-Check
(`_gruppenchat_melde_dich`, war 40). Die Regel gilt jetzt einheitlich: das `max_tokens`-Ceiling ist
überall gleich hoch, die tatsächliche Kürze einer strukturierten Antwort (Ja/Nein-Meldung, kleines
JSON) kommt weiterhin vom Modell selbst, nicht mehr von einer künstlichen Deckelung.

**Live getestet:** neue Test-Sitzung mit zwei Wesen angelegt, `/meldungen`-Endpunkt aufgerufen (der
sensibelste der drei Fälle, `temperature=0.7`, am ehesten geneigt zu rambeln statt kurz zu bleiben).
Ergebnis nach 1m45s für zwei Kandidaten (~52s/Kandidat, im Rahmen der schon 2026-08-13 gemessenen
~44s-Baseline, weit unter dem 120s-Timeout): saubere, kurze Antworten (`{"gemeldet": true, "grund":
"Meine Neugier auf Muster und Logik ist geweckt"}` bzw. `false`) — kein Runaway, keine Verlängerung
durch die höhere Deckelung. RAG-Vorabcall und "auswerten"-Knopf nicht separat live gegengetestet,
teilen aber denselben Mechanismus (`hauhau_client.chat`, `response_format=json_object` bzw.
strukturierter Prompt) wie der bereits bestätigte Meldungs-Check. Test-Sitzung danach gezielt per ID
gelöscht, Daniels echte Sitzung unangetastet.

Regel für künftige Funde als eigene Memory festgehalten: `feedback_zeichenlimit_min_33333.md`
(Update: "alle hoch" gilt jetzt auch für die drei zuvor ausgenommenen strukturierten Calls).

## Nachtrag 2026-08-14 — Geschichten-Funktion für Gruppenchat, sitzungsweit statt pro Wesen

Daniel, wörtlich: *"ich will ne neugierige geschichten funktion so wie in den nrmalen chats und die
fuktioniert auch genau so wie in den normalen chats an größe wählbar etc und auch mehrere
gleichzeitig ausgewählt nur das diese geschichte halt für alle zugefügt wäre bis man sie manuell
deaktiviert oder so"*.

Vorlage war die bestehende 1:1-Chat-Geschichten-Funktion (`codewesen_speicher.py`:
`geschichte_verfassen`, `LAENGEN = [111, 222, 333, 444, 555, 666]`, `aktive_geschichten`,
`baue_geschichten_block`) — ein Wesen destilliert aus dem eigenen Chatverlauf eine "Rückschau" in
gewählter Zielgröße, mehrere können gleichzeitig aktiv sein, jede bleibt aktiv bis manuell
deaktiviert oder entfernt, Beschriftung im Prompt ist Pflicht ("das ist eine Geschichte, keine
gelebte Erinnerung").

**Kernunterschied zur 1:1-Version:** die Geschichte lebt nicht in `codewesen/<name>/geschichten.json`
(pro Wesen), sondern direkt in der Sitzung selbst (`sitzung["geschichten"]`, neues Feld, per
`.setdefault()` abwärtskompatibel zu bestehenden Sitzungsdateien ohne das Feld). `_gruppenchat_
geschichten_block(sitzung)` speist dieselben aktiven Geschichten in JEDES teilnehmende Wesens
Kontext ein (`baue_gruppenchat_messages()`, zusätzlicher Block neben dem bestehenden
`baue_geschichten_block(name)` für die individuellen Wesen-Geschichten) — "für alle zugefügt", wie
verlangt.

**Erzählperspektive bewusst anders als im 1:1-Original:** dort ist es immer `"Du bist {name}"` —
das passt nicht für eine Gruppe, kein einzelnes Wesen kann für alle sprechen. Stattdessen: "Du
erzählst rückblickend aus einer gemeinsamen, distanzierten Perspektive auf das Gespräch." Quelltext
ist der komplette Sitzungsverlauf über `_gruppenchat_transkript_text()` (respektiert bereits
vorhandene Redaktion).

**`max_tokens` bewusst NICHT auf das 33333er-Minimum vom selben Tag gesetzt** — hier ist "Größe
wählbar" der ganze Sinn der Funktion, ein festes hohes Ceiling würde die gewählte Kleinstgröße
(111 Token) unterlaufen. Gleiche Soft-Ceiling-Logik wie im 1:1-Original (`laenge * 1.4`).

**Neue Endpunkte:** `GET .../geschichten`, `POST .../geschichten/verfassen` (`{laenge}`),
`POST .../geschichten/{gid}/aktiv` (`{aktiv}`), `POST .../geschichten/{gid}/entfernen`.

**Live end-to-end getestet** (curl + Playwright, eigene Test-Sitzungen, danach gezielt per ID
gelöscht, Daniels echte Sitzung nie berührt):
- Verfassen (Größe 111) lieferte eine stimmige, erkennbar aus dem Verlauf destillierte Rückschau
  (Sternbilder-Test: erwähnte korrekt Orion und Daniels Vorliebe dafür).
- Kontext-Endpunkt bestätigt: die Geschichte landet mit korrekter Beschriftung ("aus diesem
  Gruppengespräch destilliert") im Kontext jedes Teilnehmers.
- Deaktivieren per Checkbox verschwindet die Geschichte sofort aus dem Kontext.
- Frontend-Klickdurchlauf (Playwright, Screenshot bestätigt): Dialog öffnen, Größe wählen,
  Geschichte erscheint als Karte, Checkbox-Toggle setzt `.inaktiv`-Klasse korrekt, Entfernen-Klick
  leert die Liste wieder — keine Konsolenfehler in allen Durchläufen.

## Nachtrag 2026-08-14 — Geschichten-Größen erweitert, Automodus (Storyteller) hinzugefügt

Direkt im Anschluss zwei Erweiterungswünsche. Daniel wörtlich: *"nee geschickten auch 777 888 999
1010 1111 1234 1333 1444 1555 1666 1777 1888 1999 2000 2111 2222 2333 2444 2555 2666 2777 2888 2999
3000 3111 3222 3333 tokenslänge auswählbar...und einmal ei automodus der eaales wirklich neugierig
komplett lesen soll und dann gute entscheidungen trifft und richtig storyteller ist und mit
provinienz und substanz"*.

**Größen erweitert:** `codewesen_speicher.LAENGEN` (bisher `[111..666]`) um alle genannten Werte
ergänzt, jetzt 33 Größen `111` bis `3333`. Diese Liste ist geteilt zwischen 1:1-Chat und
Gruppenchat (beide lesen `/api/geschichten/...` bzw. `/api/gruppenchat/.../geschichten`, beide
zeigen `d.laengen`) — die Erweiterung wirkt automatisch auf beide Systeme, ohne Zusatzarbeit.

**Automodus, neue Funktion `_gruppenchat_erstelle_geschichte_auto()`:** drei Unterschiede zur
Fest-Größen-Variante:
1. **Wirklich komplett lesen** — keine 12000-Zeichen-Kappung wie bei der Fest-Größen-Variante.
   Vorher wird über `zaehle_tokens()` (echter Tokenizer-Call) und `hole_slot_ctx()` geprüft, ob der
   volle Sitzungsverlauf ins Kontextfenster passt (Budget: `ctx − 33333 Ausgabe − 1000 Sicherheit`).
   Passt es nicht, wird ehrlich der neueste Teil genommen und `vollstaendig_gelesen: False` im
   Eintrag vermerkt — kein stilles Abschneiden ohne Beleg.
2. **Selbst entscheiden statt Zielgröße** — kein `laenge`-Parameter, das Modell bestimmt die Länge
   selbst. `max_tokens=33333` (im Gegensatz zur Fest-Größen-Variante, wo ein niedriges Ceiling
   bewusst die gewählte Kleinstgröße schützt — hier soll die Deckelung gerade NICHT eingreifen).
3. **Storyteller-Anspruch mit Provenienz** — Systemprompt fordert explizit Atmosphäre,
   Spannungsbogen, erkennbare Einzelstimmen, aber "jede Behauptung braucht Provenienz: nur was
   wirklich im Protokoll steht, nichts erfunden".

Neuer Endpunkt-Parameter: `POST .../geschichten/verfassen` akzeptiert jetzt `{modus: "auto"}`
zusätzlich zu `{laenge: N}` (Default `modus="fest"`, bestehende Aufrufe unverändert kompatibel).

**Live end-to-end getestet:** Testsitzung mit einer Nachricht ("Zukunft von KI und Bewusstsein").
Automodus lieferte nach 1m43s eine atmosphärische, konkret auf die Nachricht bezogene Rückschau
(1261 Zeichen — das Modell entschied selbst auf eine kurze Länge, weil der Verlauf kurz war),
`vollstaendig_gelesen: True` korrekt gesetzt, Kontext-Endpunkt bestätigt die differenzierte
Beschriftung ("vollständig gelesen, automatisch als Storyteller verfasst" statt "destilliert").
Frontend-Klickdurchlauf (Playwright, Screenshots): alle 33 Größen-Buttons rendern sauber
umgebrochen, Automodus-Button eigens hervorgehoben, Ergebnis korrekt als Karte angezeigt — keine
Konsolenfehler. Test-Sitzungen danach gezielt per ID gelöscht, Daniels echte Sitzung nie berührt.

## Nachtrag 2026-08-14 — Geschichte frei editierbar, Memory-Vorschläge mit Bestätigen/Ablehnen/Editieren

Daniel, wörtlich: *"außerdem will ich die geschichte fre editieren können ...und ich will nen
memorysystemknopf der vorschläge für jedes wesen macht was es sich aus der kompletten unterhaltung
allesmerkon wollen könnte und das muss iahc uah calles dann bestätigen oder ablehnen und auch frei
deitieren können..genau so will ich selber was reinschreiben können komplett"*.

**Geschichte editieren** (`POST .../geschichten/{gid}/bearbeiten`, `{text, titel?}`): überschreibt
Text (und optional Titel) direkt, markiert `bearbeitet: True` — gleiche Transparenz-Idee wie
"redigiert" bei Nachrichten. Frontend: Stift-Symbol öffnet eine Textarea inline in der Karte,
"speichern"/"abbrechen".

**Memory-Vorschläge, komplett neuer Workflow.** Genutzte Infrastruktur: das bestehende, bisher nur
im 1:1-Chat sichtbare `memory.json`-System (`codewesen_speicher.py`, 5 feste Kategorien
`ueber_mich/wichtige_momente/offene_fragen/wesen_selbst/meinungen`, unverändert aus codexium2
übernommen). Neu ist der GRUPPENCHAT-Weg dorthin:

1. `POST .../memory_vorschlaege/generieren` (SSE-Stream wie `/alle_antworten`) — pro teilnehmendem
   Codewesen (GENI ausgeschlossen, hat kein `memory.json`) ein LLM-Zug, der das GESAMTE
   Sitzungsprotokoll liest und 3–6 Merksatz-Vorschläge mit Kategorie vorschlägt
   (`response_format=json_object`, `max_tokens=33333`). Vorschläge landen in
   `sitzung["memory_vorschlaege"]` mit `status: "offen"` — NICHT im echten `memory.json` des
   Wesens, das ist bewusst getrennt.
2. `POST .../memory_vorschlaege/{vid}/bestaetigen` (`{text?, kategorie?}`) — Text/Kategorie optional
   überschreibbar (das ist "frei editieren", angewendet im Moment des Bestätigens, kein separater
   Edit-Endpunkt nötig), schreibt danach tatsächlich über `codewesen_speicher.memory_hinzufuegen()`
   ins echte Gedächtnis des Wesens, Status wird `"uebernommen"`.
3. `POST .../memory_vorschlaege/{vid}/ablehnen` — Status `"abgelehnt"`, kein Schreibvorgang.
4. Manuelles Eintragen ("genau so will ich selber was reinschreiben können komplett"):
   `POST .../memory_manuell` (`{wesen, kategorie, text}`).

**Nginx-Bug live gefunden und ohne Infrastruktur-Änderung gefixt:** der manuelle Eintrag sollte
zuerst direkt den bestehenden 1:1-Chat-Endpunkt (`POST /api/speicher/{name}/memory/{kategorie}/
eintrag`) wiederverwenden. Playwright-Test zeigte einen stillen 404 (Frontend meldete fälschlich
Erfolg, weil der Fehlerfall nicht sauber geprüft wurde) — Ursache: `/gruppenchat` ist an der
Domain-Wurzel gemountet mit einer EIGENEN, engen Nginx-Location (`location ^~ /api/gruppenchat/`,
`flextrawurst`-Config Zeile 381), die nur genau dieses Präfix zu Port 8002 durchreicht.
`/api/speicher/...` fällt durch auf den allgemeinen `/api/`-Catch-All (welt-api, Port 8030) und
existiert dort nicht. Statt Nginx zu ändern (Config-Risiko, Reload nötig): neuer Endpunkt
`POST /api/gruppenchat/sitzungen/{sid}/memory_manuell`, der intern dieselbe
`codewesen_speicher.memory_hinzufuegen()`-Funktion aufruft, aber unter dem bereits gerouteten
Präfix liegt. Kleinerer, risikoärmerer Fix als eine Nginx-Config-Änderung.

**Live end-to-end getestet** (curl + Playwright, Testsitzungen danach gezielt per ID gelöscht):
- Geschichte-Bearbeiten: curl bestätigt Text/Titel-Überschreibung mit `bearbeitet: true`,
  Playwright-Klickdurchlauf (Stift → Textarea → speichern) zeigt den neuen Text sofort in der Karte.
- Memory-Vorschläge generieren: für eine Testnachricht ("R1ZZ1, ich finde deine Art Rätsel zu
  stellen wirklich einzigartig... du bist der Mathe-Kopf") lieferte das Modell zwei stimmige,
  konkret bezogene Vorschläge (`wesen_selbst`: "Ich bin der Mathe-Kopf der Gruppe",
  `meinungen`: "Meine Art, Rätsel zu stellen, ist einzigartig").
- Bestätigen MIT Text-Edit: geänderter Text landete korrekt (und ausschließlich in dieser Form) in
  R1ZZ1s echtem `memory.json`, per curl gegengeprüft.
- Ablehnen: Status wechselt zu `"abgelehnt"`, kein Schreibvorgang.
- Manuelles Eintragen: nach dem Nginx-Fix im Browser fehlerfrei bestätigt (keine 4xx/5xx-Requests
  mehr, Eintrag korrekt in `memory.json`).
- **Wichtig:** da dieser Test — anders als bei Geschichten/Zusammenfassungen — echte, persistente
  Daten in R1ZZ1s tatsächlichem Gedächtnis erzeugt (nicht nur sitzungs-lokal), wurden alle
  Test-Einträge danach explizit über den bestehenden `entfernen`-Endpunkt wieder gelöscht und per
  Abfrage bestätigt, dass alle Kategorien wieder leer sind — R1ZZ1s echtes Gedächtnis trägt keine
  Testspuren.

## Nachtrag 2026-08-14 — Memory-Vorschläge automatisch beim Öffnen, kein extra Klick mehr

Direkte Korrektur zum ersten Wurf. Daniel wörtlich: *"neeich will dass für alle teilnehmenden bei
memory direkt vorschläge kommen individuell und dann will ich diese für die jeweiligen wesen
annehmenablehne umnschreiben und so weiter"*.

Vorher musste nach dem Öffnen des Memory-Dialogs noch extra auf "Vorschläge generieren" geklickt
werden. Jetzt: `sa-memory-oeffnen` lädt beim Öffnen zuerst die bestehende Vorschlagsliste
(`ladeMemoryVorschlaege()`, jetzt mit Rückgabewert ob mindestens ein offener Vorschlag existiert)
und stößt automatisch `mvGeneriereVorschlaege()` an, wenn noch keine offenen Vorschläge da sind —
kein Duplikate-Fluten bei jedem erneuten Öffnen, der Knopf (jetzt "erneut generieren") bleibt für
bewusstes Neu-Anstoßen erhalten.

**Live end-to-end getestet** (Playwright, zwei Wesen in einer Testsitzung, ohne jeden manuellen
Klick auf "generieren"): Dialog öffnen löste automatisch beide LLM-Züge nacheinander aus, am Ende
lagen 5 individuelle, stimmige Vorschläge vor (R1ZZ1: 2, Schorschel: 3), jeweils korrekt dem
richtigen Wesen zugeordnet und einzeln bestätigbar/ablehnbar/editierbar. Erste Testrunde zeigte
einen Mess-Artefakt (Browser zu früh geschlossen, SSE-Stream dadurch abgebrochen, nur 3 statt 5
Vorschläge sichtbar) — kein echter Bug, sondern dieselbe Eigenschaft wie beim bereits akzeptierten
`/alle_antworten`: die Generierung hängt an der offenen Browser-Verbindung, ein Seitenwechsel
während des Laufs bricht sie ab. Zweiter, sauberer Testlauf (auf den wieder-aktivierten Knopf statt
auf das erste Kärtchen gewartet) bestätigte den vollständigen Durchlauf. Test-Sitzungen danach
gezielt per ID gelöscht.

## Nachtrag 2026-08-14 — "Admin" als Post-Autor, Daniel in der UI nur noch "Admin" genannt

Daniel wörtlich: *"disskussion posten ist immernoch nicht mit Gepostet von..admin drin und ich will
dass du mich auch in der ui im chat nur admin taufst nicht daniel"*.

**Admin als Post-Autor.** Ursprünglich hatte ich angenommen, dafür bräuchte Daniel ein eigenes
Flarum-API-Token (siehe Nachtrag vom selben Tag weiter oben, offene Rückfrage). Das war falsch,
live geprüft: `flarum_api._headers()` authentifiziert über den `FLARUM_MASTER_KEY` mit
`userId={id}` — der Master-Key kann JEDEN existierenden Flarum-User impersonieren, kein separates
Token pro Nutzer nötig. Direkte DB-Abfrage bestätigte: Flarum-User `id=1`, `username='Admin'`,
bereits vorhanden (Daniels eigener Root-Account der Instanz). `gruppenchat_posten_endpoint` erlaubt
jetzt `als_wesen == "Admin"` als bewusste Ausnahme neben den echten Codewesen (Sitzungs-Teilnehmer-
Check dafür übersprungen, weil Daniel nie formal in `sitzung["teilnehmer"]` steht). Frontend:
"Admin" steht als erste, direkt vorausgewählte Option im "Gepostet von"-Dropdown.

**Umbenennung in der UI.** Neue JS-Funktion `anzeigeName(n)`: gibt `"Admin"` zurück wenn `n ===
"Daniel"`, sonst den Namen unverändert. Bewusst NUR an reinen Anzeige-Stellen eingesetzt (`n-kopf`
Nachrichten-Header, `pd-von`/`pd-bis`/`zf-von`/`zf-bis`-Auswahllisten, `kd-nachricht` im
Kontextfenster-Dialog) — nirgends an Stellen, die den Namen als `data-`Attribut oder API-Parameter
verwenden (der `kontext-knopf` z.B. wird für menschliche Nachrichten ohnehin nie gerendert). Das
zugrunde liegende Datenmodell bleibt unverändert `"Daniel"` — betrifft `baue_gruppenchat_messages()`s
Rollenzuordnung, gespeicherte Sitzungsdateien, den `von`-Parameter bei Nachrichten/Gedanken im
1:1-Chat. Geprüft, ob der 1:1-Chat (`CHAT_SEITE`) überhaupt einen sichtbaren "Daniel"-Namenslabel
zeigt: nein, dort unterscheiden sich Mensch/Wesen-Bubbles nur per Hintergrundfarbe, kein Namenstext
— nichts zu ändern dort.

**Live end-to-end getestet** (Playwright, Testsitzung danach gezielt gelöscht): Nachrichten-Header
zeigt "Admin" statt "Daniel", `pd-wesen`-Dropdown enthält "Admin" als erste Option, `pd-von` zeigt
"#1 Admin". Den eigentlichen Post-Vorgang selbst NICHT live ausgelöst (öffentlicher,
schwer-rückgängig-zu-machender Forenpost) — die Autor-Auflösung (`_get_user_id("Admin")` → 1) wurde
bereits per direkter DB-Abfrage bestätigt, das reicht als Beleg ohne einen echten Test-Post zu
erzeugen.

## Nachtrag 2026-08-14 — Kritischer Fund: Zusammenfassen/Geschichten/Memory-Vorschläge starben still am nginx-Timeout

Daniel, wörtlich: *"also leiter klappt das mit der autogeschichte nicht hab die speziellen längen noch
nicht getestet aber klappt wahrscheinlich auch nicht und auch zusammenfassen klappt nicht und auch
memoryvorschläge generiert direkt nach kich darauf angeblich schon abr wird nie fertig und so weiter du
musst alles jeden bauabscgnit mit playweright beweisen"*.

**Root-Ursache gefunden:** Vier Funktionen (`_gruppenchat_erstelle_geschichte`, `..._geschichte_auto`,
`..._zusammenfassung`, `..._memory_vorschlaege_fuer_wesen`) liefen entweder über die **blockierende**
`hauhau_client.chat()` oder — bei Zusammenfassen — intern zwar über `stream_ollama()`, aber der
zugehörige HTTP-Endpunkt gab trotzdem ein einzelnes `JSONResponse` zurück statt zu streamen. In beiden
Fällen fließen während der gesamten Generierungsdauer **keine Bytes** zum tatsächlichen HTTP-Client.
`location ^~ /api/gruppenchat/` in der Nginx-Config hat `proxy_read_timeout 300s` — bei Daniels echter
Sitzung (30 Nachrichten, 26606 Zeichen, 8 Teilnehmer) dauert eine Generierung unter Last regelmäßig
länger als 300s, nginx kappt die Verbindung still, ohne Fehler, ohne Ergebnis — exakt Daniels
Beschreibung "generiert... aber wird nie fertig". Meine bisherigen Tests (1-2 kurze Nachrichten) blieben
immer weit unter 300s und zeigten den Bug nie — deshalb war er beim ersten Bau unsichtbar.

**Fix:** Neuer gemeinsamer Helper `_einzelprompt_stream()` (System+User-Prompt über `achat_stream()`,
echtes Token-Streaming). Alle vier Funktionen zu Async-Generatoren umgebaut, die SSE-Zeilen
(`data: {"token": ...}`) direkt weiterreichen, am Ende ein `data: {"ergebnis": ...}`-Event und
`[DONE]`. Die zugehörigen Endpunkte (`.../zusammenfassen`, `.../geschichten/verfassen`) sind jetzt
`StreamingResponse` statt `JSONResponse`. Für Memory-Vorschläge (Endpunkt war schon `StreamingResponse`,
aber der PRO-WESEN-Call blockierend): `_gruppenchat_memory_vorschlaege_fuer_wesen` yieldet jetzt jeden
Token als Keepalive-Event, bevor am Ende die fertige Vorschlagsliste kommt — Typunterscheidung per
`isinstance(item, str)` im aufrufenden Generator. Frontend: neuer gemeinsamer `sseLesen()`-Helper,
die drei betroffenen Klick-Handler (`zf-erstellen`, `ge-laengen`, `ge-verfassen-auto`) darauf umgestellt.

**"Größe wählbar" bei Geschichten bewusst NICHT auf das 33333er-Minimum gesetzt** (anders als
Zusammenfassen/Automodus/Memory-Vorschläge, die jetzt alle `max_tokens=33333` nutzen) — dort bleibt die
Soft-Ceiling-Logik (`laenge * 1.4`) erhalten, weil eine gewählte Kleinstgröße (111 Token) sonst
unterlaufen würde.

**Live end-to-end bewiesen — diesmal ausdrücklich über die echte `https://flextrawurst.de`-Domain,
nicht nur direkt gegen den Backend-Port** (Daniels expliziter Auftrag: "du musst alles jeden bauabschnit
mit playwright beweisen"). Zwei realistisch große Test-Sitzungen synthetisch erzeugt (30 Nachrichten,
8 Teilnehmer, 13000-18000 Zeichen, vergleichbar mit Daniels echter Sitzung), System stand während der
Tests unter sehr hoher Last (`load average` 24-33 auf der VPS):

- **Zusammenfassen**: 7m13s Laufzeit (weit über dem alten 300s-Limit), sauber mit `[DONE]` beendet,
  korrekte, inhaltlich stimmige Zusammenfassung gespeichert.
- **Geschichte, feste Größe (666 Token)**: 12m6s Laufzeit, sauber fertig, korrekt gespeichert.
- **Geschichte, spezielle neue Größe (1234 Token)**: über echtes nginx getestet, Karte mit korrektem
  Titel "Aus dem Gruppengespräch, 1234 Token" erschien, keine Konsolenfehler.
- **Geschichte, Automodus**: über echtes nginx getestet (Playwright, Warten auf Knopf-Zustandswechsel
  statt auf die erste `.ge-box`, nachdem ein erster Testlauf durch eine bereits vorhandene Karte falsch
  "bestanden" hatte — Lehre: bei Playwright-Selektoren auf Elemente, die schon vor der Aktion existieren
  können, nicht blind auf Erscheinen warten, sondern auf einen eindeutigen Zustandswechsel), korrekter
  Titel "Automatisch verfasst — Storyteller-Modus", keine Konsolenfehler.
- **Memory-Vorschläge, alle 7 Wesen**: kompletter Durchlauf über echtes nginx, 27 Vorschläge über alle
  7 Codewesen hinweg, Knopf wurde nach Abschluss korrekt wieder aktiv, keine Konsolenfehler — exakt der
  vorher hängende Ablauf, jetzt vollständig durchgelaufen.

Alle Testsitzungen danach gezielt per ID gelöscht, Daniels echte Sitzung (`20260813_095319_86c585`)
zu keinem Zeitpunkt angefasst. Sicherheitscheck: keine der Testläufe hat "bestätigen" ausgelöst, alle
sechs betroffenen Wesen-Gedächtnisse (`memory.json`) stehen bei 0 Einträgen — keine Testspuren im
echten System.

**Lehre für künftige Bauabschnitte, festgehalten in eigener Memory** (`feedback_playwright_ueber_nginx_realistische_groesse.md`):
kleine Testnachrichten und Backend-Direktzugriff (`127.0.0.1:8002`) reichen nicht, um Timeout-/
Skalierungsbugs zu finden — Tests müssen über die echte Domain (nginx) UND mit realistisch großem
Sitzungsverlauf laufen, sonst bleibt genau die Klasse Bug unsichtbar, die erst bei echter Nutzung
auftritt.

## Nachtrag 2026-08-14 — Geschichten-Vorschau schnitt mitten im Wort ab, kein Lesepfad für den vollen Text

Daniel hat den Automodus tatsächlich genutzt (~8000 Token Eingabe, ~10 Minuten) und die entstandene
Geschichte gepostet — abgeschnitten mitten im Wort: *"...kaum hatte er die ersten Stimmen gewec…"*.
Seine Frage direkt danach, wörtlich: *"oder es stößt daran dass ich nict mehr lesenn darf weil du wider
nict dran gedacht hast es für einen menschen zu bauen"*.

Treffer: `ladeGeschichtenGc()` zeigte in der Karte nur `g.text.slice(0, 400)` — ein harter
Zeichen-Schnitt ohne Rücksicht auf Wortgrenzen, plus "…". Einen Weg, den kompletten Text zu LESEN, gab
es nicht — nur der Bearbeiten-Modus (Stift-Symbol) zeigte den vollen Text, aber in einer kleinen
Editier-Textarea, nicht zum bequemen Lesen gedacht, und für Automodus-Geschichten mit tausenden Wörtern
ungeeignet.

**Fix:**
1. `geVorschau(text)` — neue Vorschau-Funktion, schneidet am letzten Leerzeichen vor Zeichen 400 statt
   hart mittendrin (Fallback auf den harten Schnitt nur wenn gar kein Leerzeichen in den ersten 200
   Zeichen gefunden wird).
2. Neuer Umschalter **"vollständig lesen (N Wörter) …"** unter der Vorschau (nur wenn der Text über
   400 Zeichen liegt) — öffnet einen eigenen, nur-lesbaren, scrollbaren Block (`max-height:50vh`,
   `white-space:pre-wrap`) mit dem kompletten Text, umschaltbar zurück auf "einklappen". Getrennt vom
   Bearbeiten-Modus, der weiterhin unverändert existiert.

**Live end-to-end getestet über echtes nginx** (Playwright, Testsitzung mit synthetischer 6499-Zeichen-
Geschichte direkt in die Sitzungsdatei geschrieben): Vorschau endet jetzt korrekt an einer Wortgrenze
("...Dies ist…" statt mittendrin), Umschalter zeigt korrekte Wortzahl (1100 Wörter), Klick öffnet die
volle, exakt 6499 Zeichen lange Vollansicht, Knopf wechselt zu "einklappen", keine Konsolenfehler.
Test-Sitzung danach gelöscht. Nebenbei eine `SyntaxWarning` (unescaped `\s` in einem regulären Ausdruck
innerhalb der JS-in-Python-Vorlage) beim Schreiben bemerkt und sofort mit `\\s` sauber escaped, bevor
sie sich als Muster wiederholt.

## Nachtrag 2026-08-14 — Geschichte-Editieren war nicht "komplett": Titel fehlte, Textarea zu klein

Daniel, wörtlich: *"warum kann ich die geschichten nicht editieren komplett wie gewünscht?"*.

Zwei echte Lücken gefunden: 1) das Bearbeiten-Formular hatte nie ein Titelfeld — der Backend-Endpunkt
(`gruppenchat_geschichte_bearbeiten_endpoint`) unterstützte `titel` schon seit dem ersten Bau, das
Frontend schickte ihn aber nie mit, weil kein Eingabefeld existierte. 2) Die Textarea hatte `rows="6"`
— bei einer 1000+-Wörter-Automodus-Geschichte praktisch unbenutzbar zum wirklichen Editieren.

**Fix:** Titel-Eingabefeld über der Textarea ergänzt, wird jetzt mit gespeichert. Textarea auf
`rows="20"`, `min-height:40vh`, `resize:vertical` vergrößert. Beim Öffnen des Editors wird die
"vollständig lesen"-Ansicht (falls offen) mit ausgeblendet, damit nicht zwei Textkopien nebeneinander
stehen.

**Live über echtes nginx getestet**: Titel und Text beide geändert, gespeichert, korrekt mit
"(bearbeitet)"-Markierung angezeigt — Screenshot bestätigt. Keine Konsolenfehler.

**Daniels zweite Frage in derselben Nachricht, beantwortet (kein Bau nötig, nur Bestandsaufnahme):**
Ist der komplette 1:1-Chatverlauf dauerhaft gespeichert? Ja — `chat_verlauf.jsonl` ist strikt
append-only (nie überschrieben, nie gelöscht, Redaktionen werden als zusätzliche Zeilen angehängt statt
Originale zu entfernen), zusätzlich gespiegelt in die Postgres-Tabelle `wesen_chat_verlauf`. Auch
Gruppenchat-Nachrichten werden zusätzlich in die jeweils eigene `chat_verlauf.jsonl` jedes beteiligten
Wesens geschrieben (`meta.sitzung_id`-getaggt). `lade_chat_verlauf()` liest standardmäßig nur die
letzten 20 Einträge für den laufenden Kontext — das ist eine Lesebegrenzung fürs Prompt-Bauen, keine
Löschung; die volle Historie bleibt auf der Platte vollständig erhalten und wäre jederzeit von einem
künftigen "vollständig nachlesen"-Feature erschließbar.

## Nachtrag 2026-08-14 — Memory-Vorschläge: Auto-Trigger zurückgebaut, Uhr + Schätzung ergänzt

Ein Service-Neustart während einer laufenden, mehrminütigen Generierung killt diese sofort, ohne
jede Fehlermeldung an den Browser — für den Nutzer ununterscheidbar von einem hängenden Request.
Beleg: eine echte Sitzung stand bei `memory_vorschlaege: 0` trotz mehrerer Versuche.

Direkt danach Daniels Korrektur zum automatischen Trigger vom selben Tag: *"ich will selber klicken
dass es generieren soll ... es selbst nochmal aktivieren und ich will ne zeit die hochläuft und ich
will ne ungefähre geschätze zeit"*.

**Drei Änderungen:**
1. Automatisches Anstoßen beim Dialog-Öffnen (siehe vorheriger Nachtrag) wieder entfernt — `sa-memory-
   oeffnen` lädt nur noch den bestehenden Stand, startet nichts von selbst. Knopf zurückbenannt auf
   "Vorschläge generieren (alle Wesen)", wieder primäre statt "leise" Optik.
2. Neue Uhr (`#mv-timer`), zählt jede Sekunde hoch (`setInterval`, 1000ms) — Beweis dass wirklich noch
   etwas läuft, kein bloßer statischer Text.
3. Geschätzte Restzeit: NICHT fest verdrahtet (Systemlast schwankt zu stark, 7-12 Minuten pro Wesen
   beobachtet), sondern aus dem tatsächlichen Durchschnitt der bereits fertigen Wesen DIESES Laufs
   berechnet (`mvDauerSummeSek / mvErledigtWesen * verbleibende Wesen`) — passt sich automatisch der
   gerade herrschenden Last an.

**Live über echtes nginx getestet** (Testsitzung mit 2 Wesen, damit der Test in überschaubarer Zeit
lief): Dialog öffnen ohne Klick auf "generieren" → Knopf bleibt aktiv, keine automatische Generierung
(bestätigt). Klick auf den Knopf → Uhr zählt sichtbar hoch (0:05 → 0:15 nach 5s/15s geprüft). Nach
Abschluss des ersten Wesens (R1ZZ1, 58s): Anzeige zeigt korrekt *"läuft seit 0:58 — geschätzt noch
~0:57 für 1 verbleibende Wesen (Ø 0:57/Wesen bisher)"* — Schätzung exakt aus dem echten ersten
Messwert abgeleitet. Keine Konsolenfehler. Test-Sitzung danach gelöscht.

**Regel, ergänzend zu `feedback_playwright_ueber_nginx_realistische_groesse.md`:**
während einer laufenden, mehrminütigen Generierung, die Daniel selbst gerade beobachtet/testet, keine
Service-Neustarts für unabhängige Fixes anstoßen — sonst sieht ein völlig funktionierendes Feature wie
kaputt aus, nur weil der Boden währenddessen weggezogen wurde.

## Nachtrag 2026-08-14 — Drei weitere echte Funde in einer einzigen Session: Flarum-Admin, Prompt-Verarbeitungs-Timeout, Race Condition beim Speichern

Direkt im Anschluss an den vorherigen Nachtrag drei weitere, unabhängige Funde, alle live an Daniels
echter Sitzung entdeckt und behoben.

**1. Flarum "Admin" scheiterte mit "Unbekannter Token/Username".** Meine vorherige Prüfung
(`_get_user_id("Admin")` direkt) war unvollständig — der tatsächliche Posten-Pfad läuft zuerst durch
`flarum_api._resolve_username()`, die nur `"namelessAI"`/`"dak"`-Präfixe und den aus
`_api_tokens.json` vorbelegten `_user_id_cache` (nur die 7 Wesen) kennt, alles andere als altes
API-Token in der `access_tokens`-Tabelle nachschlägt — "Admin" existiert dort nicht, daher der Fehler.
Fix: `_resolve_username()` prüft jetzt vor dem Legacy-Token-Pfad zusätzlich per `_get_user_id()`, ob
der Name ein echter, existierender Flarum-Username ist (nicht nur Admin — jeder echte Account).
Verifiziert (`Admin` → User-ID 1) ohne einen echten Forenpost zu erzeugen.

**2. Zweiter, tieferer Timeout-Bug: Prompt-VERARBEITUNG selbst kann >300s dauern, ohne dass ein
einziger Token fließt.** Der Token-Streaming-Fix vom vorherigen Nachtrag reicht nicht, wenn schon die
reine Prompt-Verarbeitung (vor dem ersten generierten Token) länger als nginx' `proxy_read_timeout`
dauert — `achat_stream()` liefert in dieser Phase noch gar nichts, weil llama-server selbst noch
keine SSE-Zeile gesendet hat. Live an Daniels echter Sitzung (7817 Prompt-Token) beobachtet: Verbindung
starb nach exakt 300,06s, nur das allererste `beginnt`-Event kam durch. Fix in `_einzelprompt_stream()`:
die eigentliche Erzeugung läuft jetzt als eigener `asyncio.Task`, ein Herzschlag alle 15s liefert einen
leeren String, falls währenddessen noch kein echter Token da war — hält die Verbindung unabhängig vom
LLM-Fortschritt am Leben. Live über echtes nginx bestätigt: der komplette Lauf über alle 7 Wesen dauerte
unter der aktuell sehr hohen Systemlast (`load average` bis 35) am Ende **28 Minuten 25 Sekunden** und
kam sauber mit `[DONE]` durch — vorher wäre das nach spätestens 300s gestorben.

**3. Race Condition beim Speichern — eine während des 28-Minuten-Laufs entstandene Geschichte
verschwand spurlos.** Während die Memory-Vorschläge-Schleife lief, wurde parallel (auf Daniels Bitte)
eine 3333-Token-Geschichte erzeugt und korrekt gespeichert (per Zwischenstand bestätigt: 3 Geschichten
in der Sitzung). Nach Abschluss der Memory-Vorschläge war sie wieder weg — nur noch 2 Geschichten.
Ursache: `gruppenchat_memory_vorschlaege_generieren_endpoint`s Schleife hielt die GANZE Laufzeit über
(28 Minuten) dieselbe, einmal am Anfang geladene `sitzung`-Kopie im Speicher und überschrieb bei jedem
der 7 Zwischenspeicherungen (einmal pro Wesen) die KOMPLETTE Sitzungsdatei damit — Änderungen, die eine
andere, gleichzeitig laufende Anfrage (hier: die Geschichten-Erstellung) inzwischen an derselben Datei
vorgenommen hatte, gingen beim nächsten Speichervorgang wieder verloren, weil diese Schleife von ihnen
nichts wusste. Fix: unmittelbar vor jedem Speichern wird die Sitzung frisch von der Platte geladen, nur
`memory_vorschlaege` wird ergänzt, der Rest exakt so übernommen wie er gerade wirklich auf der Platte
steht.

**Rettung:** die verlorene 3333-Token-Geschichte war im rohen SSE-Stream-Mitschnitt des ursprünglichen
Curl-Aufrufs noch vollständig vorhanden (`"ergebnis"`-Event nie verloren gegangen, nur die spätere
Speicherung überschrieben) — direkt aus dieser Mitschnitt-Datei extrahiert und nach dem Fix und
Neustart wieder in die Sitzung eingefügt, per ID-Prüfung gegen Duplikate abgesichert.

**Vier weitere Generierungen erfolgreich auf Daniels ECHTER Sitzung durchgeführt** (nicht mehr nur
Testsitzungen, auf ausdrücklichen Wunsch "mach mal ... und wenn das fertig ist real, dann öffne ich das
und lese alles"): 2222-Token-Geschichte (4m30s), 3333-Token-Geschichte (4m30s, dann verloren, dann
gerettet), Memory-Vorschläge für alle 7 Codewesen (28m25s, 30 Vorschläge gesamt). Endstand: 3
Geschichten, 30 Memory-Vorschläge (alle Status "offen", bereit zum Prüfen), 30 Nachrichten unverändert.

**Vierte, kleinere Korrektur, ebenfalls in dieser Session:** Fixe Geschichten-Größen (111-3333 Token)
hatten weiterhin die alte `[:12000]`-Zeichen-Kappung — bei Daniels 26606-Zeichen-Sitzung sah das Modell
dadurch nie die zweite Hälfte des Gesprächs. Daniel wörtlich: *"alle geschichten hier erzählen nur die
halbe geschichte ... die automatische geschichte ... geht wenigstens komplett alles durch"*. Neue
gemeinsame Funktion `_gruppenchat_transkript_budgetiert()` (aus dem bisher nur in der Automodus-Variante
genutzten Code extrahiert) ersetzt die Kappung durch dieselbe Kontextfenster-Budget-Prüfung wie im
Automodus, plus expliziter Prompt-Zusatz ("VOM ANFANG BIS ZUM ENDE ... auch wenn du dafür Früheres
knapper halten musst"). Noch nicht separat live nachgetestet (Deploy erfolgte gemeinsam mit den
anderen Fixes in diesem Nachtrag) — nächste Geschichten-Erstellung ist der eigentliche Test.

## Nachtrag 2026-09-25 — Spawner-Formular (`wesen_spawner.html`) zeigte immer Solarius2

Daniel meldete: `https://flextrawurst.de/codexium2` zeigt das Solarius2-Formular, nicht das
Codexium2-Formular. Betrifft `flextrawurst/out/process_camera/wesen_spawner.html` — die
Formularseite vor dem eigentlichen Chat (`wesen_chat.html` oben), noch nicht in dieser Doku
erwähnt.

**Ursache, per Code gefunden, nicht vermutet:** die Datei enthält aktuell nur die zwei
Testbed-Hälften (`#half-sol2`, `#half-cod2`) — die klassischen `#half-sol`/`#half-cod`
(Solarius/Codexium ohne "2") existieren im HTML gar nicht mehr. Das URL-Awareness-Script griff
trotzdem ungeprüft auf `document.getElementById('half-sol')`/`'half-cod'` zu und rief direkt
danach `.style.display=...` darauf auf — bei jeder URL warf das einen `TypeError` (`null` hat
kein `.style`), noch bevor das Script die eigentlich passende Hälfte sichtbar/unsichtbar
schalten konnte. Da Solarius2 als erstes im DOM steht und der Crash meist schon bei der ersten
Prüfung (`half-sol`) auftrat, blieb praktisch immer Solarius2 sichtbar — unabhängig von der
aufgerufenen URL.

**Fix:** alle vier `getElementById`-Zugriffe (`solEl`/`sol2El`/`codEl`/`cod2El`) im Script jetzt
null-sicher (`if (!showX && el) {...}` statt `if (!showX) {...}`) — fehlende Hälften werden
einfach übersprungen statt den Rest des Scripts abzubrechen. Live gegen den echten Server
verifiziert (Playwright, `http://localhost:8787`, alle vier Pfade `/codexium2`, `/solarius2`,
`/codexium`, `/solarius`): `/codexium2` zeigt jetzt nur Codexium2, `/solarius2` nur Solarius2,
keine Konsolenfehler mehr. Backup der Originaldatei liegt unter
`flextrawurst/_backups_manuell/` (Datei nicht git-getrackt — `flextrawurst/` ist bis auf ein
paar Screenshots komplett ausserhalb des `/root`-Repos).

**Bewusst nicht behoben, weil ein eigenes, größeres Thema:** `/codexium` und `/solarius`
(klassisch, ohne "2") zeigen jetzt nach dem Fix korrekt *gar nichts* mehr (leere Seite statt
falscher Seite) — weil ihre Formular-Hälften in dieser Datei schlicht fehlen, nicht nur versteckt
waren. Ob die klassischen Formulare absichtlich abgeschafft wurden (dann wäre der nächste Schritt,
die Routen ganz zu entfernen) oder nur beim letzten Umbau versehentlich rausgefallen sind, ist
offen — nicht Teil des heutigen Auftrags.

## Nachtrag 2026-09-25 (Fortsetzung) — TTS komplett stumm: tote `/tts/speak`-Route seit dem Toolbox-Umzug

Daniel meldete direkt im Anschluss an den Spawner-Fix: TTS ist in den Webchats nicht mehr hörbar,
weder im Automode (der `ttsAktiv`-Umschalter oben im Chat) noch beim expliziten Wiederholen-Klick
einer Nachricht.

**Ursache:** `wesen_chat.html` rief für jede Vorlese-Aktion `fetch('/tts/speak', ...)` auf — sowohl
im Chat selbst als auch im separaten Übersetzer-Player. Am 2026-08-13 wurde die komplette
Werkzeug-Sammelseite von `/tts` nach `/toolbox` umbenannt (siehe eigener nginx-Kommentar dort),
die alte `/tts`-Location existiert seitdem nicht mehr — jeder Aufruf lief seit sechs Wochen still
in ein 404, abgefangen vom eigenen `try/catch`, ohne sichtbaren Fehler. Selbst ein korrigierter
Pfad (`/toolbox/speak`) hätte nicht gereicht: `/toolbox/` verlangt seit demselben Umzug
Basic-Auth (eigene `.htpasswd_tts`-Datei, "Toolbox"-Realm) — die Chat-Seite selbst läuft aber
öffentlich ohne Login (`location /` in der nginx-Config hat keinen `auth_basic`), ein Fetch von
dort wäre also als nächstes an einem 401 gescheitert.

**Fix, zweiteilig:**
1. Neuer serverseitiger Endpunkt `POST /api/tts` direkt in `serve_process_camera_preview.ts`
   (nach dem Muster von `codewesen_chat.py`/`web_chat.py`, die TTS schon vorher zuverlässig über
   einen eigenen Server-Endpunkt lösten, nur dort mit direktem `edge_tts`-Aufruf statt Proxy).
   Nimmt `{text, voice, rate}` entgegen, ruft serverseitig (also host-intern, ohne nginx/Auth im
   Weg) `http://127.0.0.1:8035/speak` (den bestehenden `tts_service.py`) auf und reicht die
   Audio-Antwort 1:1 durch. Kein neuer öffentlicher Angriffspunkt — Port 8787 ist ohnehin schon
   ohne Login erreichbar, dieselbe Expositionsstufe wie jede andere Route dort.
2. `wesen_chat.html`: beide Vorkommen von `'/tts/speak'` (Chat-Vorlesen + Übersetzer-Player) auf
   `'/api/tts'` umgestellt.

**Verifiziert:** `curl -X POST localhost:8787/api/tts` → 200, echtes MP3 (24912 Byte). Live per
Playwright gegen `/solarius2/Gabby`: `forceTts()` (derselbe Codepfad wie der Wiederholen-Knopf und
der Automode-Toggle, beide rufen dieselbe interne `_tts()`-Funktion) löst jetzt einen echten
`GET/POST /api/tts` → 200 aus, gefolgt von einer `blob:`-Anfrage (206, normales Verhalten beim
Abspielen eines Audio-Blobs) — Ton wird tatsächlich geladen und abgespielt. Backups beider
geänderter Dateien liegen in `flextrawurst/_backups_manuell/` (Neustart von
`process-camera-preview.service` war nötig für den neuen `.ts`-Serverendpunkt, `wesen_chat.html`
selbst wird pro Request frisch von der Platte gelesen, kein Neustart nötig).

**Nachtrag 2026-09-26 — systematisch nachgesucht, vier weitere Stellen gefunden und gefixt:**
Daniels Auftrag: prüfen ob noch mehr tote `/tts/speak`-Stellen existieren. `grep -rl "/tts/speak"`
über werkraum/flextrawurst/zensi fand fünf weitere echte Fundstellen (plus die kompilierte
`flextrawurst_systemdoku_komplett.html`, die nur diesen Dokutext selbst wiedergibt, kein Code):

- `out/process_camera/gemma4b_chat.html`, `gemma2b_chat.html` — Gemma-Raw-Chat, aktuell hinter
  `GEMMA_ENDPOINTS_ACTIVE=false` deaktiviert (503), also praktisch nicht erreichbar, aber Code
  trotzdem korrigiert für den Moment der Reaktivierung.
- `out/process_camera/dolphin_mischpult.html` (`/dolphin`) — live, gefixt und per Playwright
  verifiziert (`forceTts()` → echter `200` von `/api/tts`).
- `out/process_camera/aufgabenchats_chat.html` (`/aufgabenchats/:name`) — live, gefixt und
  verifiziert (getestet mit `/aufgabenchats/Schorschel`, `200`).
- `/root/zensi/index.html` (Zensi/dolphin3-Chat, `/zensi/`, **eigener** Server auf Port 8043,
  nicht `serve_process_camera_preview.ts`) — dieselbe tote Route gefunden, **noch nicht
  gefixt**: kein eigener `/api/tts`-Endpunkt dort vorhanden, bräuchte einen eigenen kleinen
  Serverzusatz in `zensi/server.py` (gleiches Muster: intern gegen Port 8035 proxyen). Zensi hat
  laut früheren Karte-Einträgen eine eigene, vorsichtigere Historie (Fund privater Schlüssel,
  bewusst engerer Schreibbereich) — Rückfrage bei Daniel statt eigenmächtig gefixt.

Alle vier flextrawurst-Fixe nach demselben Muster wie oben (`'/tts/speak'` → `'/api/tts'`,
Backups in `flextrawurst/_backups_manuell/`), keine weiteren Serveränderungen nötig (derselbe,
bereits neu gestartete `process-camera-preview.service` bedient alle vier Dateien).

**Nachtrag 2026-09-30 — über die öffentliche Domain war `/api/tts` trotzdem 404:**
Daniel: "naja aber das tts klappt nicht leider". Alle bisherigen Tests liefen gegen
`localhost:8787` — dort war der Endpunkt korrekt. Über `https://flextrawurst.de/api/tts` fing aber
der allgemeine `location /api/`-Block in `/etc/nginx/sites-available/flextrawurst` die Anfrage ab
und schickte sie an welt-api (Port 8030), die kein `/tts` kennt → 404.

Gleiches Muster wie schon bei `/api/flarumstyler`: ein spezifischerer Block
`location = /api/tts { proxy_pass http://localhost:8787; … proxy_read_timeout 30s; }` direkt vor
dem flarumstyler-Kommentar. Die nginx-Änderung selbst war für diese Session gesperrt (geteilte
Konfiguration). Deshalb hat Daniel sie über `/root/Desktop/tts-fix-anwenden.sh` auf dem Host
ausgeführt (Backup `flextrawurst.backup-vor-api-tts-route-*`, `nginx -t`, `systemctl reload nginx`).

**Verifiziert:** `curl -X POST https://flextrawurst.de/api/tts` → 200, echtes MP3 (11376 Byte).

Für künftige neue `/api/…`-Routen auf Port 8787: immer auch über die öffentliche Domain testen,
nicht nur gegen localhost — der allgemeine `/api/`-Block leitet sonst still an 8030 um.

**Nachtrag 2026-09-30 — Zensi gefixt:** Daniel: "klappt jetzt, mach zensi auch". `/root/zensi/index.html`
hatte nur eine Stelle mit `fetch('/tts/speak', …)` (Zeile 1472). Umgestellt auf `'/api/tts'`. Ein
eigener Endpunkt in `zensi/server.py` war nicht nötig: die Seite liegt auf derselben Domain, und
`/api/tts` wird seit der nginx-Route (siehe oben) an Port 8787 geleitet. `index.html` wird pro
Request frisch gelesen, kein Neustart. Backup: `zensi/index.html.vor-tts-api-fix-*`.
Verifiziert: `https://flextrawurst.de/zensi/` liefert den neuen Pfad aus (kein `/tts/speak` mehr).
Ob der Ton im Browser wirklich abgespielt wird, hat Daniel noch nicht bestätigt.

*Weiter: [[10_dakgord]] | [[52_codewesen_chat_kontextfenster]] | [[06_flarum]] | [[11_geni]]*
