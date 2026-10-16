# 01 · Betrieb und Überwachung / Operations and monitoring

Deutsch zuerst, English below each project. Quellen sind die Systemdokus unter `werkraum/docs/systemdoku/` (Nummer in Klammern).
German first, English below each project. Sources are the system docs under `werkraum/docs/systemdoku/` (number in brackets).
Feld „Warum“: nur, was in der Quelle steht. Sonst: **(Daniel ergänzt)**. / Field "Why": only what the source says. Otherwise: **(Daniel adds)**.

---

## flarumstyler – das Meldesystem (Doku 18, 80)

**Versucht / Tried.** Eine Seite, die zeigt, was im System nicht so ist, wie es sein soll, erklärt, was das bedeutet, und was eine Empfehlung bringen würde oder nicht.
A page that shows what in the system is not as it should be, explains what it means, and what a recommendation would or would not achieve.

**Warum / Why.** Entstanden in der Nacht 2026-07-06/07, nachdem mehrere Fehler wochenlang unbemerkt geblieben waren: ein seit über einem Monat deaktivierter Flarum-Monitor, eine fehlende Antwortpflicht bei dak+gord, eine veraltete Watchdog-Regel. Zuerst nur beobachtend geplant („kein Auto-Fix“), noch in derselben Nacht auf Daniels Wunsch um Start/Stopp/Neustart mit Bestätigung erweitert.
Arose in the night of 2026-07-06/07 after several errors had gone unnoticed for weeks: a Flarum monitor disabled for over a month, a missing reply duty for dak+gord, an outdated watchdog rule. First planned as observation only ("no auto-fix"), extended the same night at Daniel's wish with start/stop/restart after confirmation.

**Was liegt drin / What is inside.**
- `werkraum/welt/weltkern_watchdog.py` – Datenquelle, läuft alle 10 Minuten, schreibt einen JSON-Bericht / data source, runs every 10 minutes, writes a JSON report
- Fehlermuster-Katalog mit „was ist los / Empfehlung / bringt das / bringt das nicht“ je Muster / error pattern catalogue with "what is wrong / recommendation / what it brings / what it does not bring" per pattern
- Ampel-Kacheln, Klartext-Beschreibung für 31 Dienste, Verlauf der letzten ca. 30 Tage / traffic-light tiles, plain-language description for 31 services, history of about 30 days
- Tabelle `dienst_konfiguration` (Takt und Verhalten je Dienst überschreibbar) / table `dienst_konfiguration` (rhythm and behaviour overridable per service)
- Die Steuerung ist für vier Dienste gesperrt (u. a. Welt-API, LLM-Server), „Blast-Radius für alle Wesen gleichzeitig“ / control is locked for four services (incl. world API, LLM server), "blast radius for all beings at once"

**Stand / State.** In Betrieb (Doku Juli 2026). Doku 80: Die Admin-Absicherung dieser Seite hatte einen Fehler (doppeltes „Bearer“), der die Prüfung für alle unbrauchbar machte. / In operation (docs July 2026). Doc 80: the admin guard for this page had a bug (doubled "Bearer") that made the check unusable for everyone.

**Grenze / Limit.** Eigene Seite, nicht Teil der Hauptoberfläche. Einzelne Ideen aus der Nacht (Verknüpfung mit einem Baustein 2) wurden zurückgestellt. / Separate page, not part of the main surface. Some ideas from that night (link to a "building block 2") were put on hold.

---

## Admin-Absicherung der Routen (Doku 80)

**Versucht / Tried.** Ein Wächter-Modul, das alle ändernden Anfragen unter fünf Pfad-Präfixen (Wesen, Dienst-Wizard, Meldesystem, Mischpult, Aufgabenchats) auf Anmeldung und Herkunft prüft.
A guard module that checks all state-changing requests under five path prefixes (beings, service wizard, reporting system, mixing desk, task chats) for login and origin.

**Warum / Why.** Aus dem Codex-Sicherheitsreview (Funde SEC-005/007). Davor konnte laut Review ein anonymer Besucher bestehende Wesen überschreiben oder löschen und Container-Aktionen auslösen. / From the Codex security review (findings SEC-005/007). Before it, according to the review, an anonymous visitor could overwrite or delete existing beings and trigger container actions.

**Was liegt drin / What is inside.** `portfolio/flextrawurst/scripts/admin_route_guard.ts`, Tests unter `portfolio/flextrawurst/tests/`, Reviews unter `werkraum/_codex/berichte/`.

**Stand / State.** Seit 2026-09-17 aktiv. Doku 80 beschreibt den Fehler in der ersten Fassung und seine Behebung. / Active since 2026-09-17. Doc 80 describes the error in the first version and its fix.

---

## LLM-Scheduler und Slot-Kontention (Doku 19, 31)

**Versucht / Tried.** Eine Prioritäts-Warteschlange für alle Hintergrunddienste, die auf zwei LLM-Server-Instanzen zugreifen: eilige Aufrufe (Bereitschaftsprüfung vor einem Post, Antwort an Daniel) sollen nie hinter langsamer Hintergrundarbeit festhängen.
A priority queue for all background services that use the two LLM server instances: urgent calls (readiness check before a post, reply to Daniel) should never get stuck behind slow background work.

**Warum / Why.** Daniel meldete in der Nacht 2026-07-06/07: „im flarum passiert nix mehr schon lange und ich kann auch nicht chatten“. Die Analyse fand eine strukturelle Ursache: rund 18 dauerhaft laufende Prozesse teilten sich 2 echte Slots. Am 2026-07-21 zeigte eine Abfrage etwa 15–16 Verbraucher für diese 2 Slots; fast jeder Tick der Browser-Agenten verlor die Warteschlange nach 150 s.
Daniel reported in the night of 2026-07-06/07: "nothing has happened in Flarum for a long time and I can't chat either". The analysis found a structural cause: about 18 permanently running processes shared 2 real slots. On 2026-07-21 a query showed about 15–16 consumers for those 2 slots; almost every tick of the browser agents lost the queue after 150 s.

**Was liegt drin / What is inside.** `werkraum/llm_scheduler.py`, `werkraum/hauhau_client.py`; Doku 19 und 31. Die Slot-Zahl 2 ist kein Zufallswert: `--parallel 3` verursachte am 2026-07-06 einen 37-fachen Einbruch. / Doc 19 and 31. The slot count 2 is not arbitrary: `--parallel 3` caused a 37-fold slowdown on 2026-07-06.

**Stand / State.** Scheduler in Betrieb; die Aufräumarbeit an den Diensten (Doku 31) ist beschrieben. / Scheduler in operation; the clean-up of services (doc 31) is described.

---

## Provenienz-Protokolle der Dienste (Doku 24, 27)

**Versucht / Tried.** Für jeden Hintergrunddienst nachvollziehbar festhalten: Skript, Unit, Status, Herkunft, Commit-Chronik. Stufe 1: 13 Wesen/Flarum-Dienste (16 Units). Stufe 2: Wesen-Prozess, Welt-Kern, GENI, dak+gord, Innenleben, KompOase u. a.
Record for every background service in a traceable way: script, unit, status, origin, commit chronology. Stage 1: 13 being/Flarum services (16 units). Stage 2: being process, world core, GENI, dak+gord, inner life, KompOase and others.

**Warum / Why.** Auftrag von Daniel (2026-07-11): „provenienzgetriebene, protokollierende, logartige Megadokumentation“. Wichtiger Vorbehalt der Doku: Die Git-Historie beginnt 2026-04-04, aber fast alle untersuchten Dateien erscheinen erstmals in einem einzigen Sammel-Commit vom 2026-05-12; der echte Entstehungsgrund ist daher oft nicht rekonstruierbar.
Order from Daniel (2026-07-11): "provenance-driven, logging, log-like mega documentation". Important caveat of the doc: the git history starts 2026-04-04, but almost all examined files first appear in a single bulk commit of 2026-05-12; the real reason of origin is therefore often not reconstructible.

**Was liegt drin / What is inside.** Doku 24 und 27; zusätzlich „Lebendes Inventar“ Teil A/B/C (Doku 54) vom 2026-08-14: echtes Lesen von Unit-Datei, ExecStart und Skript, Live-Status; wo eine ältere Doku widerspricht, wird das benannt. / Doc 24 and 27; additionally "Living inventory" part A/B/C (doc 54) of 2026-08-14: actually reading unit file, ExecStart and script, live status; where an older doc contradicts, that is stated.

---

## Tab-Audit der Oberfläche (Doku 55)

**Versucht / Tried.** Alle Tabs der Oberfläche daraufhin prüfen, welche Aussagen dort stehen und ob sie noch stimmen.
Check all tabs of the surface for which statements they make and whether they are still true.

**Warum / Why.** Daniel (2026-08-14): „alle tabs analysieren lassen und alles prüfen welche aussagen dort getroffen werden das ist alles veraltet und so“. Wichtiger Fund: Die live ausgelieferte Quelle liegt in einem eigenen Repo direkt unter `/root`, nicht im Werkraum; beide Kopien unterscheiden sich um etwa 830 Zeilen.
Daniel (2026-08-14): "have all tabs analysed and check which statements are made there, it's all outdated". Key finding: the live source sits in its own repo directly under `/root`, not in the workspace; the two copies differ by about 830 lines.

**Was liegt drin / What is inside.** Doku 55 in drei Teilen (Erklär-Tabs / Wesen selbst und persönlicher Bereich / restliche). Die Oberfläche selbst: `portfolio/flextrawurst/` (u. a. `scripts/build_surface.ts`, 17.092 Zeilen laut Doku).
Doc 55 in three parts (explanatory tabs / beings themselves and personal area / the rest). The surface itself: `portfolio/flextrawurst/`.

---

## Stille Ausfälle und Härtung (Doku 39, 63, 67, 77)

**Versucht / Tried.** Fehler suchen, die nicht auffallen, und sie schließen.
Find errors that do not stand out, and close them.

**Was liegt drin / What is inside.**
- Doku 39 (2026-07-29): Nachzug zum Sicherheits-Report vom Mai; Port-Härtung abgeschlossen (Priorität 5), Prioritäten 1–3 teilweise oder offen.
  Doc 39 (2026-07-29): follow-up to the May security report; port hardening done (priority 5), priorities 1–3 partly or open.
- Doku 63 (2026-09-03): `welt-api` war 13 Tage lang ausgefallen, ohne dass es auffiel; gefunden bei einem Redteam-Test an anderer Stelle.
  Doc 63 (2026-09-03): the world API had been down for 13 days without being noticed; found during a red-team test elsewhere.
- Doku 67: zwei abgeschnittene Dateien, vier Dienste seit Wochen im Absturz-Schleifenmodus; die Doku hält fest, dass die Ursache des Abschneidens nicht geklärt ist.
  Doc 67: two truncated files, four services in a crash loop for weeks; the doc notes that the cause of the truncation is not identified.
- Doku 77 (2026-09-19): Speicherdruck auf dem Host; zwei Ursachen behoben, eine bewusst nicht angefasst, ein Absturz des virtuellen Desktops unaufgeklärt.
  Doc 77 (2026-09-19): memory pressure on the host; two causes fixed, one deliberately left alone, one crash of the virtual desktop unexplained.

---

## Verlaufsprotokolle (Doku 52)

**Versucht / Tried.** Für jede Entität (GENI, die Wesen, alles Künftige) die Kontextfenster menschenlesbar in Markdown ablegen, mit Ereignissen, Entscheidungen, Tags, Zeit und Datum, und zusätzlich loggen.
For every entity (GENI, the beings, anything to come) store the context windows in human-readable Markdown, with events, decisions, tags, time and date, and log additionally.

**Warum / Why.** Auftrag von Daniel (2026-08-03), im Wortlaut in der Doku: „… menschlesbar in eine md … mit genauen events und entscheidungen und tags und zeit datum …“. / Order from Daniel (2026-08-03), verbatim in the doc.

**Stand / State.** Beschrieben in Doku 52; zur Ehrlichkeit der Kontextanzeige im Chat siehe die zweite Doku 52 (`52_codewesen_chat_kontextfenster.md`): Die Anzeige ruft dieselben Funktionen auf, die den Prompt wirklich bauen, damit die Zahl nicht von der Wirklichkeit abdriftet.
Described in doc 52; for the honesty of the context display in the chat see the second doc 52: the display calls the same functions that really build the prompt, so the number does not drift from reality.
