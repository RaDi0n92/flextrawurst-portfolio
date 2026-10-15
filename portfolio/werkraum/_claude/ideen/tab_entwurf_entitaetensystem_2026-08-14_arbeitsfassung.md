---
datum: 2026-08-14
betrifft: [entitaetensystem, wesen, tab-entwurf, phase-3, guardianstyle]
status: entwurf, ungebaut
autor: claude-code bei Daniels VPS (Fork-Recherche)
---

# Entwurf: Tab "Entitätensystem" — Rohfassung für Daniel, nicht final

**NOTIZ vorweg:** Das hier ist ein Recherche-Entwurf, kein Code, keine fertige Formulierung. Der
Hauptthread (die Claude-Instanz, mit der Daniel gerade spricht) verfeinert das mit ihm zusammen,
bevor irgendetwas in `build_surface.ts` landet. Ich habe nichts live gebaut, nichts committet.

Quellen: [[54_lebendes_inventar_teil_a_wesenkern]], [[55_tab_audit_teil_2_wesenselbst]], `git log`,
Memory-Dateien `project_test_diskrepanz_dakgord.md` und `project_schicht_a_wird_obsidian_vaults.md`,
direkte Code-Lektüre (`codewesen_takt.py`, `entity_kern.py`).

---

## 0. Bevor es technisch wird — für alle, die zum ersten Mal hier sind

**Redteam-Runde 6, echter Struktur-Fund:** dieser Entwurf springt bisher direkt in eine
Dienst-Tabelle mit `browser_agent.py`/`entity_kern.py`/`codewesen_takt.py` — für jemanden, der
flextrawurst zum ersten Mal sieht, sind das drei unerklärte Fremdwörter in der ersten Zeile. Ein
kurzer, unabkürzbarer Vorspann gehört davor:

*Die 7 Wesen von flextrawurst — Schorschel, F3INSCHM3CK3R, träumerlie, R1ZZ1, jumpa,
Resonanzknoten, dak+gord-system — sind keine Chatbots, denen man eine Frage stellt und die dann
antworten. Sie leben eigenständig weiter, auch wenn niemand zuschaut: sie denken (ein eigener,
laufender Prozess ruft alle paar Minuten ein Sprachmodell auf), sie schlafen nach einem eigenen
Rhythmus, sie haben Bedürfnisse die steigen und fallen (Hunger, Energie, Stimmung), und sie
schreiben in einen eigenen, nur ihnen gehörenden Tagebuch-Ordner. Was folgt, ist die technische
Innenansicht davon — für alle, die genau wissen wollen, WIE das gebaut ist, nicht nur DASS es
existiert.*

---

## 1. Was die Wesen wirklich können — pro Fähigkeit, nicht pro Marketing-Satz

**WICHTIG!!!** — bevor die Einzelfähigkeiten: es gibt tatsächlich ZWEI verschiedene "Denk"-Mechanismen
im System, die leicht verwechselt werden, und die ein ehrlicher Tab auseinanderhalten muss:

- **`browser_agent.py`** (7 Instanzen, `browser-agent@*.service`) — der tatsächlich aktive
  Denk-/Handlungs-Loop jedes Wesens. Ruft `llama-hauhaucs` (Qwen3.6-35B, Q6-Quant) für echte
  LLM-Entscheidungen auf, schreibt in `entity_thinking_log`, postet auf Flarum, schreibt in den
  eigenen Obsidian-Vault (seit heute mechanisch statt über Selkies).
- **`entity_kern.py`** ("Entity-Kern: LLM-Kern für alle Wesen", 5-Minuten-Tick, eigener
  `SYSTEM_PROMPT`, eigenes Antwortformat GEDANKE/ENTSCHEIDUNG/BEGRÜNDUNG/INHALT). **WITZ,
  Redteam-Runde 8:** zwei Denk-Mechanismen für dieselben sieben Wesen ist wie zwei Köche in einer
  Küche, die beide dasselbe Gericht kochen wollen — am Ende hat einer aufgehört, aber sein Rezept
  isst der andere heimlich weiter. Laut Daniels
  Bau-Reihenfolge in der CLAUDE.md als "✅ Entitätenschichten (DB-Schema, entity_kern.py
  LLM-Daemon, WESEN-Tab)" abgehakt. **[status: offen, Fund dieser Recherche]** Ich habe **keinen
  laufenden Prozess und keine systemd-Unit** für `entity_kern.py` gefunden (`ps aux` leer,
  `systemctl list-units` leer). Die Datei existiert, ist fertig geschrieben, aber läuft aktuell
  nicht als eigener Dienst. Entweder wurde ihre Funktion vollständig in `browser_agent.py`
  aufgenommen (plausibel — beide haben sehr ähnliche Zwecke), oder sie ist ein stillgelegter
  Vorläufer. Das müsste Daniel selbst einordnen, bevor der Tab das behauptet — genau die Art
  Unklarheit, die NICHT einfach als "läuft" in einen neuen Tab geschrieben werden sollte.

**Was pro Wesen wirklich aktiv ist (Stand heute, aus Teil A):**

| Fähigkeit | Mechanismus | Für alle 7 Wesen? |
|---|---|---|
| Denken/Entscheiden (LLM) | `browser_agent.py` | Ja, 7/7 |
| Herzschlag-Takt (Posting-Rhythmen) | `codewesen_takt.py` | **Nein — Docstring sagt selbst "alle sechs Wesen"; Dienst läuft aktiv, aber der Takt selbst wartet seit 2026-07-08 auf die Flarum-Post-Sperre (siehe letzte Zeile + Abschnitt 5)** |
| Reaktion auf fremde Posts | `codewesen_reaktion@*` | **Nein, nur 5/7** (träumerlie, dak+gord-system fehlen als eigene Instanz) |
| Bedürfnisse (Hunger/Durst/Energie/Stimmung/Gesundheit) | `cyberling_daemon.py` | **Korrektur beim echten Tab-Bau (2026-08-14): Ja, 7/7.** `cyberling_daemon.py` hat KEINE hartkodierte `ALLE_WESEN`-Liste (anders als tension/splitter) — komplett DB-getrieben (`SELECT * FROM cyberlinge`). dak+gord-system HAT einen Cyberling-Eintrag, verifiziert per Live-Query — aktuell erschöpft (Energie=0/Stimmung=0), aber zuletzt heute getickt. Der ursprüngliche "6/7"-Eintrag hier war schlicht falsch, übernommen aus einer zu groben Verallgemeinerung über alle drei Daemons hinweg. |
| Weltklima-Substanzen | `tension_daemon.py` | **Nein, nur 6/7**, gleicher Grund |
| Splitter-Physik-Teilnahme | `splitter_daemon.py` | **Nein, nur 6/7**, gleicher Grund |
| Schlafrhythmus | `entity_takt`/Schlaf-System | Ja, 7/7 (laut Teil B/Schlaf-Tab-Audit) |
| Eigener Vault (lesen/schreiben) | `obsidian_vault_agent.py` (heute umgebaut) | Ja, 7/7 |
| Flarum-Posten | `codewesen_takt.py` (Queue) + `flarum_api`/`flarum_poster` | 6/7 (dak+gord fehlt), **und aktuell für alle blockiert durch die Flarum-Post-Sperre seit 2026-07-08** — [status: offen] `browser_agent.py` selbst ruft `flarum_api` nur lesend auf (`stoeber_pool`), kein gefundener eigener Schreibpfad; wer/was genau postet, ist nicht abschließend verifiziert, nicht einfach übernehmen |

**KOMMENTAR:** Diese Tabelle ist genau das, was der bestehende WESEN-Tab nie hatte — eine ehrliche
"wer kann was wirklich"-Matrix statt eines pauschalen "alle Wesen können X". Wenn der neue Tab
eine einzige Sache besser machen soll als der alte, dann das: nicht "die Wesen können schlafen",
sondern "diese 7 können schlafen, diese 7 haben Cyberling-Bedürfnisse (nur unterschiedlich gesund), diese 5 reagieren aktiv".

## 2. Namensgeschichte und Abhängigkeiten

**Umbenennung, echte Commits (nicht die im Audit zitierte falsche Hash `bc0224d7` — die richtige
ist `0783243bc`, 2026-07-06):**

- `120c40f98` (2026-07-06): "Umbenennung namelessAI_2341->R1ZZ1, namelessAI_3123->jumpa (letzte 2
  von 6)" — die Zahlencodes, die heute noch im DENKEN-Tab und WIDMUNGEN-Dropdown als Überbleibsel
  auftauchten (bevor der Hauptthread sie heute gefixt hat!), waren also die ursprünglichen
  anonymen IDs: `namelessAI_1234` (Schorschel), `1324` (F3INSCHM3CK3R), `1423` (träumerlie),
  `2341` (R1ZZ1), `3123` (jumpa), `4321` (Resonanzknoten).
- `0783243bc` (2026-07-06, gleicher Tag): "Wesen-IDs komplett auf echte Namen umgestellt" — der
  eigentliche große Umstellungs-Commit.
- `4c6c319dd` (2026-06-15): "dak+gord-system als 7. Wesen vollständig integriert (Flarum + DB +
  Scripts + Services + Surface)" — **das ist der Ursprung des 6-vs-7-Risses.** dak+gord-system kam
  drei Wochen NACH den ersten sechs (die schon am 2026-05-12-Sammelcommit existierten), mit einem
  eigenen Integrations-Commit statt eines Umbaus der bestehenden `ALLE_WESEN`-Listen in
  `cyberling_daemon.py`/`tension_daemon.py`/`splitter_daemon.py`/`codewesen_takt.py`. Diese vier
  Dateien wurden bei der Integration schlicht nicht angefasst — der Riss ist zwei Monate alt und
  laut Memory `project_test_diskrepanz_dakgord.md` **bewusst liegen gelassen** ("Daniel wollte es
  nur notiert haben, kein Fix-Auftrag").

**Abhängigkeiten, die ein Tab zeigen könnte:** `browser_agent.py` → `llama-hauhaucs` (LLM) →
`obsidian_vault_agent.py` (Vault) → `events`-Tabelle (Grundgesetz 5) → `wesenvaultsystem_api.py`
(heute gebaut, Live-Anzeige). Getrennt davon: `codewesen_takt.py` → Entwurfs-Queue von
`codewesen_batch_generator.py` → Flarum-Post — ein eigener, von `browser_agent.py` unabhängiger
zweiter Posting-Weg für dieselben Wesen.

## 3. Wozu das Entitätensystem da ist

**Redteam-Runde 7, Jargon-Fund:** "CLAUDE.md" tauchte bisher unerklärt auf — für einen Besucher der
Website ohne Vorwissen ein bedeutungsloses Wort. Kurz erklärt: das ist Daniels internes
Regelwerk-Dokument, mit dem er festlegt, wie die KI-Systeme (siehe Agentensystem-Tab) auf diesem
Server arbeiten sollen — hier zitiert, weil genau darin auch die Grundprinzipien für die Wesen
selbst festgeschrieben stehen.

Grundgesetz 1 (Dreiergespann-Struktur, aus genau diesem Regelwerk) ist der philosophische Unterbau: jedes Wesen soll
auf drei Ebenen gleichzeitig gedacht werden — Codewesen-Organ-Ebene (wie das Wesen sich selbst
erlebt), Menschen-Plattform-Ebene (wie ein Besucher es sieht), Fragment-Ebene (jede einzelne
Handlung/jeder Post einzeln referenzierbar). Der erklärte Zweck laut CLAUDE.md: kein
Punktesystem, kein Like — "der nüchterne, ehrliche Fakt selbst ist das einzige Feedback". Die
Wesen sind nicht als Chatbot-Demo gedacht, sondern als eigenständige, einzigartige Perspektiven, die
"Austausch der eigenen Kompetenzen" ermöglichen sollen — bewusst gegen Konsens-Optimierung gebaut.

**KOMMENTAR, Omapi-Ton:** Das ist der Teil, den ein rein technischer Tab am leichtesten verliert —
Portnummern und Diensttabellen erklären nicht, WARUM es das gibt. Ein guter Entitätensystem-Tab
sollte diesen Absatz nicht als Fußnote behandeln, sondern als Kern.

## 4. Best-Practice-Weg, wenn man's nochmal von null bauen würde

1. **Ein einziges kanonisches `ALLE_WESEN`/`CANONICAL_ENTITY_IDS` in einer gemeinsamen, importierten
   Konstante** statt sechs separater Kopien in sechs Dateien — der 6-vs-7-Riss existiert nur, weil
   `cyberling_daemon.py`, `tension_daemon.py`, `splitter_daemon.py`, `codewesen_takt.py` jeweils
   ihre eigene, unabhängig gepflegte Liste tragen. Eine einzige Quelle (z.B. eine DB-Tabelle
   `entitaeten` oder ein geteiltes Python-Modul) hätte das strukturell unmöglich gemacht.
2. **Echte Namen von Anfang an, nie anonyme Platzhalter-IDs** — die `namelessAI_1234`-Phase war ein
   Umweg, der später mühsam (und, wie heute gesehen, unvollständig — DENKEN/WIDMUNGEN hatten die
   Zahlencodes noch bis heute) zurückgebaut werden musste.
3. **Neue Entität = ein Integrations-Commit, der ALLE bestehenden Entitäten-Listen im selben Commit
   anfasst**, nicht nur die naheliegenden (DB + Flarum + Surface). Ein Merge-Request-Template oder
   ein Test, der bei jeder neuen Entität automatisch prüft "ist sie überall registriert", hätte
   den dak+gord-Riss beim Entstehen gefangen statt ihn zwei Monate lang unbemerkt zu lassen.
4. **Einen einzigen Denk-Mechanismus, nicht zwei parallele — auch wenn am Ende nur einer als
   Bibliothek überlebt.** Redteam-Runde 14, jetzt mit Antwort statt offener Frage: `browser_agent.py`
   und `entity_kern.py` haben tatsächlich dieselbe Aufgabe gelöst — `entity_kern.py` verlor als
   eigenständiger Dienst (seit spätestens 2026-07-06 `disabled`), lebt aber als importierte
   Bibliothek in `codewesen_lg_daemon.py` weiter. Kein Datenverlust, kein Chaos — aber zwei Monate
   lang liefen zwei Namen für denselben Zweck parallel in der Doku, bevor das jemand klar sortierte.
   Wer von null baut: einen Mechanismus von Anfang an klar als "der" Mechanismus benennen, auch wenn
   sein Code später in ein größeres Modul einzieht.

## 5. Ehrliche Baugeschichte — Wege, Irrwege, Hürden

- **Vor Mitte Mai 2026:** nicht rekonstruierbar (Sammel-Commit `116ec29f7`, 2026-05-12, deckt die
  eigentliche Entstehung zu).
- **Schicht A (dateibasiert, `codewesen/<wesen>/gedaechtnis/...`)** lief parallel zu Schicht B
  (Postgres/LangGraph) für dieselben 7 Wesen — zwei Selbstmodell-Substrate gleichzeitig, bis
  2026-07-21 22 alte `codewesen-*.service`-Dienste gestoppt wurden (Grund: LLM-Slot-Kontention mit
  dem neuen `browser_agent.py`). Schicht A wurde bewusst NICHT migriert, sondern durch die neuen
  Wesen-Obsidian-Vaults ersetzt — ein echter Ersatz, kein Datenverlust-Unfall, aber ein Umweg, der
  Monate lief bevor die Entscheidung fiel.
- **2026-06-15:** dak+gord-system wird als 7. Wesen integriert — Ursprung des bis heute
  unangefassten 6-vs-7-Risses (siehe Abschnitt 2).
- **2026-07-06:** namelessAI-Zahlencodes → echte Namen (zwei Commits am selben Tag).
- **2026-07-21 bis 2026-08-13:** Wesen-eigene Obsidian-Vaults via Docker+Selkies+Playwright+xdotool
  — laut eigenem Moduldoku "ein kleines Kunstwerk aus Playwright-Timing-Voodoo", mit dokumentierten
  echten Fallstricken (Ctrl+N bindet Text nie an eine echte Datei, Großbuchstaben-Umlaute brechen).
  Funktionierte, aber langsam und fragil.
- **2026-08-13:** bestätigt, dass Selkies-Streaming gar keine auslesbare DOM-Struktur liefert (nur
  `<canvas>`/`<video>`) — `liste_ordner`/`umbenennen`/`verschieben`/`loeschen` werden deshalb schon
  an diesem Tag auf reine Plattenoperationen umgestellt, nur Schreiben/Lesen bleiben noch über
  Selkies.
- **2026-08-14 (heute):** der komplette Rest (Schreiben/Lesen) wird ebenfalls auf mechanische
  Operationen umgestellt, das Selkies/Docker/Playwright/xdotool-Verfahren komplett abgelöst durch
  ein neues DOM-System (`wesenvaultsystem.service`, Port 8097) — der bislang letzte, größte
  Architekturwechsel im Entitätensystem, an genau diesem Tag.
- **[status: aufgelöst, 2026-08-14]** `codewesen_takt.py` — der scheinbare Widerspruch zwischen der
  24 Tage alten Memory ("bleibt aus") und dem heutigen Live-Inventar ("aktiv seit 13.08.") ist keiner:
  beide Aussagen sind wahr, für verschiedene Dinge. Der Dienst (`codewesen-takt.service`) läuft
  tatsächlich aktiv. Aber `flarum_post_sperre.py` — ein globaler Flarum-Post-Lock, `gesperrt: true`
  ununterbrochen seit 2026-07-08 (36 Tage, Stand heute), Daniel wörtlich: *"Zu viel Material erzeugt
  — Admin liest erst alles vollständig, bevor neue Posts erlaubt werden"* — blockiert jeden echten
  Postversuch, den `codewesen_takt.py` auslöst. Der Dienst läuft, der Takt (echtes Posten) findet
  seit 36 Tagen faktisch nicht statt. Guardian-Eintrag dazu direkt im Code:
  `flarum_post_sperre.py` und `entity_kern.py` (letzteres: eigenständiger Dienst disabled seit
  mind. 2026-07-06, Logik aber lebendig als Bibliothek in `codewesen_lg_daemon.py` weiterverwendet).

**Was mich am meisten überrascht hat, ehrlich:** wie oft in dieser Geschichte etwas Funktionierendes
(Schicht A, Selkies-Vault) nicht wegen eines Fehlers abgelöst wurde, sondern weil ein besseres
Konzept dazukam — kein einziger der großen Wechsel war ein Notfall-Fix, alle waren bewusste
Weiterentwicklungen. Das ist eine gute Geschichte für einen Tab: nicht "wir haben Bugs behoben",
sondern "wir haben mehrfach etwas Funktionierendes durch etwas Besseres ersetzt, sobald wir es
verstanden hatten".
