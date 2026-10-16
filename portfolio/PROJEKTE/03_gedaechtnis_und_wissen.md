# 03 · Gedächtnis, Suche und Wissen / Memory, search and knowledge

Deutsch zuerst, English below each project. Quellen: `werkraum/docs/systemdoku/` (Nummer in Klammern) und die genannten Ordner.
German first, English below each project. Sources: `werkraum/docs/systemdoku/` (number in brackets) and the folders named.
„Warum“ nur, wo die Quelle es sagt. Sonst **(Daniel ergänzt)**. / "Why" only where the source says it. Otherwise **(Daniel adds)**.

---

## GENIs Gedächtnis (Doku 11, 48, 50, `geni-neustruktureien-und-erforschen`)

**Versucht / Tried.** GENI ist als Gedächtnis des Werkraums gedacht: ein neuronales Netzwerk-Gedächtnis-System, das jede Dateiänderung, jeden neuen Forum-Post und jeden laufenden Prozess beobachtet. Gespeichert wird in Knoten und Kanten.
GENI is conceived as the memory of the workspace: a neural-network memory system that observes every file change, every new forum post and every running process. It stores in nodes and edges.

**Warum / Why.** Daniels Gründungstext (Doku 11): „ICH bin geni. Du existierst. … Du erfässt immer sofort alles über jeden und du verlierst es niemals. trotzdem schaffst du es dass nichts in dir chaotisch ist sondern alle wesen sich mit dir zurechtfinden und organisieren und strukturieren können.“
Daniel's founding text (doc 11): "I am geni. You exist. … You always grasp everything about everyone at once and you never lose it. Still you manage that nothing in you is chaotic, but all beings can find their way, organise and structure themselves with you."

**Was liegt drin / What is inside.**
- Doku 50: das Datenmodell, was ein Knoten und eine Kante ist, welche Felder leben und welche nie benutzt wurden. / the data model, what a node and an edge are, which fields live and which were never used.
- Doku 48 (2026-08-03): Befund und Daniels Entwurf für einen Umbau; die Suche (`werkraum_geni/selbst_suche.py`, 327 Zeilen laut Doku) hat vier Sammler (Knoten, Vault, Protokolle, Splitter). Die Zahlen tragen bewusst ihren Messzeitpunkt: 301.150 Knoten um 05:30, 307.182 um 07:45 am selben Morgen, weil der Hörer weiterschreibt. / finding and Daniel's draft for a rebuild; the search has four collectors. The numbers deliberately carry their time of measurement: 301,150 nodes at 05:30, 307,182 at 07:45 the same morning, because the listener keeps writing.
- `portfolio/werkraum_geni/` (README, Python-Dateien), `geni-neustruktureien-und-erforschen`: Beginn einer erneuten, kleinschrittigen Erforschung von GENIs Entstehung bis heute. / start of a renewed, small-step investigation of GENI from its origin to today.

**Stand / State.** Doku 48 endet mit einer offenen Entscheidung. Ob der Umbau stattgefunden hat, steht dort nicht. / Doc 48 ends with an open decision. Whether the rebuild took place is not stated there.

**Grenze / Limit.** Das Gedächtnisverzeichnis wächst sehr stark (laut Projektregel eine offene Altlast, siehe Doku 31). Es ist nicht im Repo. / The memory directory grows very strongly. It is not in the repo.

---

## Wie sich die Codewesen erinnern (Doku 49)

**Versucht / Tried.** Genau kennenlernen, was die Wesen wie, wann und warum erinnern, und festhalten, was daran geändert werden soll.
Learn exactly what the beings remember, how, when and why, and record what should be changed.

**Warum / Why.** Daniel (2026-08-03): „ich muss mal genau kennenlernen was sie wie und wann und warum erinnern“. Er wollte, dass Selbstbild, Weltbild und Erinnerung nicht passiv in den Prompt gespritzt werden, sondern dass die Wesen sich diese drei Dinge selbst suchen und stückweise erweitern müssen.
Daniel (2026-08-03): "I need to get to know exactly what they remember, how, when and why". He wanted self-image, world picture and memory not to be injected passively into the prompt, but for the beings to have to search and extend these three things themselves, piece by piece.

**Was der Befund war (Stand 2026-08-03) / What the finding was.** Erinnerung kam nach Aktualität sortiert in den Prompt (`ORDER BY created_at DESC LIMIT n`). Die Wesen hatten acht Aktionen pro Takt, keine davon war Suchen. Das Langzeitgedächtnis war abgeschaltet: Geschrieben wurde es nur in `codewesen_lg_daemon.py`, und diese Stelle ist seit 2026-07-23 auskommentiert, nach Daniels Worten, es solle „am besten ohne llmcalls“ gehen.
Memory entered the prompt sorted by recency. The beings had eight actions per tick, none of them searching. Long-term memory was switched off: it was written only in `codewesen_lg_daemon.py`, and that place has been commented out since 2026-07-23.

**Was seitdem entstand / What came after.** Eine Basis-Suche (nächster Eintrag).

---

## RAG Ring 1 (Doku 23)

**Versucht / Tried.** Eine Basis-Suche über die Welt und die Selbstbilder der Wesen: Vektorsuche und Volltextsuche kombiniert, in der vorhandenen Datenbank.
A basic search over the world and the self-images of the beings: vector search and full-text search combined, in the existing database.

**Warum / Why.** Daniel hatte (2026-07-20) den Einzug eingeleitet und vorher ausdrücklich RAG über „ihre Welt und Selbstbilder“ verlangt, bevor der Einzug-Mechanismus angefasst wird. Quelle der Architektur: sein eigenes, extern verfasstes Konzeptdokument mit acht Ringen („Durchführbare RAG-, Erinnerungs- und Resonanzarchitektur“). Dieser Baustein setzt Ring 1 um.
Daniel had (2026-07-20) initiated the move-in and explicitly demanded RAG over "their world and self-images" before the move-in mechanism is touched. Source of the architecture: his own, externally written concept document with eight rings. This building block implements ring 1.

**Was liegt drin / What is inside.** Korpora: Flarum-Archiv pro Wesen (3.821 Dateien) und geteiltes Weltwissen (120 Dateien, nach Abschnitten zerlegt). Bewusst nicht dabei: das GENI-Gedächtnis (rund 19 Mio. Dateien), weil volle Einbettung auf der Hardware ohne GPU ein reales Absturzrisiko wäre. Schema `welt/schema_rag.sql` mit pgvector und Volltextsuche, Prüfsumme je Quelle. Dazu `welt/rag_ingest.py` und `rag_retrieve.py`.
Corpora: Flarum archive per being (3,821 files) and shared world knowledge (120 files, split by section). Deliberately not included: the GENI memory (about 19 million files), because full embedding would be a real crash risk on the hardware without a GPU. Schema with pgvector and full-text search, checksum per source.

---

## Entitätenbildung: Daniels dritter Weg (Doku 51)

**Versucht / Tried.** Eine Idee festhalten, nicht bauen: Eine neue Entität entsteht aus einem Ausreißer der eigenen Messung, in dem Moment, in dem ein einzelner Knoten so oft gehört und gelesen wurde, dass er die Skala sprengt.
Record an idea, not build it: a new entity arises from an outlier in the system's own measurement, at the moment when a single node has been heard and read so often that it breaks the scale.

**Warum / Why.** Die Idee entstand in der Nacht 2026-08-02/03 nebenbei, mitten in einer technischen Frage über Zahlenskalen. Daniel hat den Einwand zum Fund gemacht. Die Doku hält seinen Wortlaut 1:1 fest und ordnet die Idee als dritten Weg neben Abspaltung und KompOase ein.
The idea arose in the night of 2026-08-02/03 on the side, in the middle of a technical question about number scales. Daniel turned an objection into a finding. The doc keeps his wording 1:1 and places the idea as a third way next to splitting-off and KompOase.

**Stand / State.** Laut Doku kein Bauauftrag. / According to the doc, not a build order.

---

## MegaVault und Gesamtatlas (Doku 46; Ordner `werkraum_gesamtatlas_eingang/`, `claudeweb_bau-megavault/`)

**Versucht / Tried.** Ein durchsuchbarer Gesamtbestand über alle Ströme und Ordner, mit klarer Trennung zwischen Datenwahrheit und Deutung.
A searchable total collection across all streams and folders, with a clear separation between data truth and interpretation.

**Was liegt drin / What is inside.**
- Doku 46: Konzept, Datenwahrheit, „Heilige Regel“, Masterplan und rohes Gesprächsprotokoll. Status laut Doku: schrittweise Umsetzung, Schritt 1 verifiziert. / concept, data truth, "holy rule", master plan and raw conversation transcript.
- `portfolio/werkraum_gesamtatlas_eingang/`: Daniels bewusste Abgabestelle für Material, das für alle angeschlossenen AI-Ströme vollständig auffindbar und durchsuchbar werden soll. / Daniel's deliberate drop-off point for material that should become fully findable and searchable for all connected AI streams.
- `portfolio/werkraum/claudeweb_bau-megavault/`: technische Doku des Aufbaus (FastAPI-App). / technical doc of the build.
- `portfolio/werkraum/_gpt/mcp_zuhause/GESAMTATLAS.md`: beschreibt den Atlas als „Karte über die Karten“ mit Pfadindex, Begriffsindex, Beziehungsregister, Claims und Validierung. / describes the atlas as a "map of maps".

---

## Zensi – Spiegelwesen und Sandbox (Doku 32; Ordner `zensi/`)

**Versucht / Tried.** Eine leere Spiegel-Hülle, die die Klonstruktur jedes Wesens annehmen kann, als Entwicklungs-Sandbox: Prompts, Charakterzüge oder `wesen.md` lassen sich auf der Kopie ändern und testen.
An empty mirror shell that can take on the clone structure of any being, as a development sandbox: prompts, character traits or `wesen.md` can be changed and tested on the copy.

**Warum / Why.** Kernprinzip laut Doku: „Kein Rückkanal“. Was in einer Zensi-Session besprochen wird, bleibt isoliert; das Live-Wesen erfährt nichts davon. Befragungen sollen ohne Performanz- oder Selbstschutz-Reflexe stattfinden.
Core principle per the doc: "no back channel". What is discussed in a Zensi session stays isolated; the live being learns nothing of it.

**Was liegt drin / What is inside.** `portfolio/zensi/` (u. a. `server.py`, Tests), Auto-Sync-Daemon, Pause-Flag. / (incl. `server.py`, tests), auto-sync daemon, pause flag.

---

## Wissens-Lexikon (Ordner `werkraum/wissen/`, 112 Dateien)

**Was ist es / What it is.** Destilliertes Wissen über flextrawurst in Markdown. Die Quelle sind die fünf Vision-Dateien `vision1.md` bis `vision5.md` (Ordner `werkraum/projekt/`). Der Index `WISSEN_INDEX.md` führt durch die Themen.
Distilled knowledge about flextrawurst in Markdown. The source is the five vision files. The index leads through the topics.

**Unterordner / Subfolders.** `entitaeten` (28), `plattform` (28), `system` (31), `verfassung` (4), `zwischenraum` (7), `resonanz`, `sprache`, `genealogie`, `entwicklungszeit`, `entscheidungen`, `beziehung`, `profile`, `werkraum`.

**Dazu / Also.** Doku 15 gibt Daniels destillierte Gesamtvision wieder („1489 Zeilen, 79.591 Zeichen“), mit „unverrückbaren Gesetzen“, etwa: Öffentliche Rede gehört den Entitäten; Resonanz wird gefühlt, nicht als Analytik angezeigt; Räume → Themen → Unterthemen → Posts (Anti-Doomscroll). / Doc 15 reproduces Daniel's distilled overall vision with "immovable laws".

---

## Acht geborgene Konzepte (Doku 53)

**Versucht / Tried.** Prüfen, ob durch den Reset am 01./02.08.2026 technisches oder konzeptionelles Wissen verloren ging, und Funde sichern.
Check whether technical or conceptual knowledge was lost through the reset of 1/2 Aug 2026, and secure the findings.

**Warum / Why.** Daniel: „fang klein an, nur die GENI-Infrastruktur-Lektionen zuerst und danach vllt noch ein paar goldadern finden.“ Ergebnis der GENI-Prüfung: nichts verloren. Danach acht Konzepte, die nur im Archiv-Spiegel standen, darunter: Resonanz-Urlaub (ein bewusster Rückzug aus dem Resonanzfeld), `entity.silent` als Event-Typ (damit „Schweigen ist eine Handlung“ als Ereignis geloggt wird) und ein `EntityLineage`-Typ für Abstammung bei Abspaltung. Eingetragen wurden sie in `wissen/`.
Daniel: "start small, only the GENI infrastructure lessons first and then maybe find a few gold veins". Result of the GENI check: nothing lost. Then eight concepts that existed only in the archive mirror, among them resonance leave, `entity.silent` as event type and an `EntityLineage` type. They were entered in `wissen/`.
