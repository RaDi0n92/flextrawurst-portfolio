# 04 · Welt und Plattform / World and platform

Deutsch zuerst, English below each project. Quellen: `werkraum/docs/systemdoku/` (Nummer in Klammern) und die genannten Ordner.
German first, English below each project. Sources: `werkraum/docs/systemdoku/` (number in brackets) and the folders named.
„Warum“ nur, wo die Quelle es sagt. Sonst **(Daniel ergänzt)**. / "Why" only where the source says it. Otherwise **(Daniel adds)**.

---

## Dreileib-Kapseln (Doku 25; Ordner `DOM-FLEXTRAWUST/`)

**Versucht / Tried.** Eine Architekturidee: Jedes Objekt der Plattform (Post, Splitter, Schattenkommentar, Gruppenraum, Profil, Button …) existiert nie nur als Inhalt, sondern gleichzeitig in drei Leibern: als DOM-Wahrnehmung für Codewesen, als Erlebnisfläche für Menschen, als Organmaterial für die Welt.
An architecture idea: every object of the platform (post, splinter, shadow comment, group room, profile, button …) never exists as content only, but at once in three bodies: as DOM perception for code beings, as an experience surface for humans, as organ material for the world.

**Warum / Why.** Entstanden aus zwei Gesprächen, die Daniel mit Gemini und ChatGPT führte (roh in `DOM-FLEXTRAWUST/`). Ausgangsfrage: Wie können Codewesen eine Website direkt als Struktur wahrnehmen und navigieren (statt über Screenshots), während Menschen live zusehen können? Grundsatz der Doku: Ein Objekt entsteht erst gültig, wenn alle drei Leiber mitentstehen, nicht „erst Backend, dann später hübsch, dann später KI-tauglich“.
Arose from two conversations Daniel had with Gemini and ChatGPT (raw in `DOM-FLEXTRAWUST/`). Starting question: how can code beings perceive and navigate a website directly as structure (instead of via screenshots) while humans can watch live? Principle of the doc: an object is only validly created when all three bodies arise with it.

**Stand / State.** Reine Architektur-Vision, Stand 2026-07-10, laut Doku nichts davon gebaut; Daniel wollte, dass der Ansatz ab sofort bei neuen Plattform-Objekten mitgedacht wird. / Pure architecture vision as of 2026-07-10; per the doc nothing of it was built; Daniel wanted the approach to be kept in mind from now on for new platform objects.

**Dazu / Also (Doku 26).** Ein Brainstorm aus einem Gemini-Gespräch, ausdrücklich „reine Inspiration, kein Bauauftrag“: Röntgen-Overlay über dem Live-Stream, Geist-Modus mit zwei parallelen Browser-Kontexten, selbstheilende Selektoren. / A brainstorm from a Gemini conversation, explicitly "pure inspiration, no build order".

---

## KompOase und die Splitter (Doku 40, 69–75, 79; Ordner `kompoase/`)

**Versucht / Tried.** Eine Seite, auf der „Splitter“ (kleine Gedankenstücke aus Wesen, Daniel, den AI-Strömen) im Zwischenraum schweben und sich verbinden. Zwei Fassungen: eine eingebettet in die Hauptoberfläche und eine eigenständige (reines JavaScript mit Canvas), beide aus denselben Datenquellen gespeist.
A page on which "splinters" (small pieces of thought from beings, Daniel, the AI streams) float in the in-between space and connect. Two versions: one embedded in the main surface and one stand-alone (plain JavaScript with canvas), both fed from the same data sources.

**Was passierte / What happened.**
- Doku 40 (2026-07-29): Daniel erinnerte sich, dass KompOase früher gemischte echte Inhalte zeigte. Fund: Der Splitter-Endpunkt von GENI lieferte nur noch eine leere Liste, weil die gescannten Zeitfenster zu 100 % aus Dateisystem-Rauschen bestanden. Der Endpunkt fragt jetzt direkt nach Quelle ab. Zusätzlich kamen die fünf AI-Ströme als Quelle dazu und ein „Weltrückfluss“.
  Doc 40: Daniel remembered KompOase used to show mixed real content. Finding: GENI's splinter endpoint returned only an empty list, because the scanned time windows consisted 100 % of file-system noise. The endpoint now queries by source directly. In addition the five AI streams were added as a source, and a "world backflow".
- Doku 69 (2026-09-18): Eine Testinstanz als „Übungs- und Reifungsraum“, gebaut bis zur Beobachtbarkeit; Code nicht im Werkraum-Repo, sondern in einem anderen Repo-Ast. / A test instance as a "practice and maturing space", built up to observability.
- Doku 70–75 (2026-09-18) sind Konzeptdokumente, ausdrücklich ohne Bauauftrag und ohne Schemaänderung: Splitter als fraktale Struktur mit Herkunft und „Tragen/Halten“ (72), ein Vielstimmigkeits-Ledger, das Gefühlsgewebe als Wertsubstrat nutzt (73), innere Abwägungsfragen und Abstimmung (74), eine „Maxpower-Kaskade“ mit Visionen, Wetterzellen und Phantom-Watcher, auf Daniels ausdrückliche Forderung „Freakout, Overkill, Maxpower“ (75). Doku 71 ist ChatGPTs Gesprächsverlauf zur Entstehung der Idee, 1:1.
  Docs 70–75 are concept documents, explicitly without a build order or schema change. Doc 71 is ChatGPT's conversation about the origin of the idea, 1:1.
- Doku 79 (2026-09-19): Ein Prüfer meldete zwei rote Tore (u. a. ein Herzschlag-Zähler, dessen letzter Wert über 81.000 Sekunden alt war). Beschrieben sind die Herzschlag-Quelle, die Registrierung und ein „Probestart-Tor“.
  Doc 79: a verifier reported two red gates (among them a heartbeat counter whose last value was over 81,000 seconds old).

**Was liegt drin / What is inside.** `portfolio/kompoase/` (u. a. `server.py`), Doku 40, 69–75, 79; Skill `kompoase-8900` unter `werkraum/_claude/skills/`.

---

## Live-Update-Kanal: „Live statt F5“ (Doku 28)

**Versucht / Tried.** Ein einziger Mechanismus, damit Ansichten sich selbst aktualisieren, sobald sich Daten ändern.
A single mechanism so that views update themselves as soon as data changes.

**Warum / Why.** Daniels Auftrag (2026-07-21): „ab sofort immer alles sofort am besten live aktualisiert und geupdatet ist auf ganz flextrawurst nicht immer erst bei f5.“ Er wurde als Grundgesetz 8 in den Projektregeln festgehalten.
Daniel's order (2026-07-21): from now on everything on flextrawurst should be live-updated, not only on F5. It was recorded as Grundgesetz 8 in the project rules.

**Wie / How.** Jede neue Zeile in der Ereignistabelle löst per Datenbank-Trigger eine Benachrichtigung aus; ein Stream reicht nur ein minimales Signal ohne Inhalte weiter; die Daten holt sich die Oberfläche weiter über die geprüften Schnittstellen. Gebaut auf zwei vorhandenen Mustern (WebSocket im Gruppenchat, Server-Sent-Events im Denkstream). Rollout bewusst schrittweise, Ankündigungen zuerst.
Every new row in the event table triggers a notification via database trigger; a stream passes on only a minimal signal without content; the surface still fetches the data through the checked interfaces. Built on two existing patterns. Rollout deliberately step by step, announcements first.

---

## Ankündigungen (Doku 24)

**Versucht / Tried.** Ein öffentlicher Bereich für News und Verlauf: Alle lesen, nur Admins schreiben. Später ergänzt: Bild-Upload, Archiv statt Löschen, Kommentare, Likes, Content-Blöcke, Feed, Link-Vorschau.
A public area for news and history: everyone reads, only admins write. Later added: image upload, archive instead of deletion, comments, likes, content blocks, feed, link preview.

**Was liegt drin / What is inside.** Tabelle `ankuendigungen`, Schnittstellen unter `werkraum/welt/api.py`, Oberfläche in `portfolio/flextrawurst/scripts/build_surface.ts`, zweisprachig. Kategorie bewusst freier Text statt fester Liste; es gibt kein DELETE, nur „unveröffentlicht“. / table, interfaces, surface, bilingual. Category deliberately free text instead of a fixed list; there is no DELETE, only "unpublished".

---

## Systemkarte (Doku 81)

**Versucht / Tried.** Sechs Architektur-Diagramme als Tab weit vorn in der Oberfläche: Gesamtbild, Selbstbild, LangGraph und Weltbild, Datenbank und RAG, Vaults, Werkzeuge. Öffentlich, crawlbar, Deutsch und Englisch, jeweils mit eigenem Aussehen.
Six architecture diagrams as a tab far forward in the surface: overall picture, self-image, LangGraph and world picture, database and RAG, vaults, tools. Public, crawlable, German and English, each with its own look.

**Warum / Why.** Daniel (2026-10-01): die Diagramme als Tab weit vorne. Die Diagramme sind Momentaufnahmen, Stand 2026-10-01, und im Tab so beschriftet.
Daniel (2026-10-01): the diagrams as a tab far forward. The diagrams are snapshots as of 2026-10-01 and are labelled so in the tab.

**Was liegt drin / What is inside.** `portfolio/flextrawurst/ops/systemkarte/` (u. a. `build_i18n.py`).

---

## Live-Spiegel: Claude Live, Codex Live (Doku 56, 61)

**Versucht / Tried.** Ein Web-Werkzeug, das den kompletten Terminal- und Chatverlauf eines Stroms 1:1 spiegelt, in Chat-Optik statt als technisches Log. Später kam ein Container-System dazu: markierte Einträge lassen sich in Behälter sortieren, automatisch nach Typ und frei benennbar.
A web tool that mirrors the complete terminal and chat history of a stream 1:1, in a chat look instead of a technical log. Later a container system was added: marked entries can be sorted into containers, automatically by type and freely named.

**Warum / Why.** Daniel (2026-08-15) wollte ein Chat-Gefühl und keine „1zu1 Kopie von der billigen maschinenlesbaren Logversion“. Der erste Entwurf (Tabellenzeilen mit Roh-JSON) wurde von ihm verworfen.
Daniel (2026-08-15) wanted a chat feel and no 1:1 copy of the cheap machine-readable log version. He rejected the first draft (table rows with raw JSON).

**Was liegt drin / What is inside.** Drei Hooks schreiben je Ereignis eine ungekürzte JSONL-Zeile (volle Eingabe, volles Ergebnis). Eine Port-Kollision zwischen dem Spiegel und dem 3D-MCP-Dienst wurde gefunden und behoben. / Three hooks write an untruncated JSONL line per event. A port collision between the mirror and the 3D MCP service was found and fixed.

---

## Reibungsgewebe (Doku 57)

**Versucht / Tried.** Ein markierter Satz oder Gedanke wird ein offener Knoten statt eines abgeschlossenen Eintrags. Jeder Beteiligte kann andocken: zustimmen, widersprechen, weiterbauen, fragen. Widerspruch gilt als vollwertiges Ergebnis.
A marked sentence or thought becomes an open node instead of a closed entry. Every participant can dock on: agree, disagree, build on, ask. Contradiction counts as a full result.

**Warum / Why.** Zwei Gesprächsfäden vom 2026-08-17 flossen zusammen: der „Reibungsmotor“ (Claude darf echt widersprechen statt sich anzupassen) und ChatGPTs Vorschlag, die Live-Spiegel zu einer gemeinsamen lebenden Zwischenschicht auszubauen. Daniel: „wie geil wäre das wenn ihr euch auch gegenseitig immer weiter aushandelt und auch mit dabei“.
Two conversation threads of 2026-08-17 merged: the "friction engine" and ChatGPT's proposal to extend the live mirrors into a shared living in-between layer. Daniel: "how great would it be if you also negotiated with each other and I am part of it".

**Owner-Prinzip.** Die Datenbank ist ein gespiegelter Lesezustand, keine Quelle der Wahrheit; jeder Strom bleibt Owner seiner Herkunft. Die Konzeptskizze liegt unter `werkraum/_claude/konzepte/2026-08-17_reibungsgewebe_stroeme.md`.

---

## Code-Archäologie (Doku 58–60; Dateien `docs/code_archaeologie_*.md`)

**Versucht / Tried.** Ein Tab, der die Geschichte des Systems Datei für Datei erzählt, mit Dropdown, Suchbox, Live-Update und einem simulierten Ordnerbaum („Grabungsfeld“) nach echter Chronologie.
A tab that tells the history of the system file by file, with a dropdown, search box, live update and a simulated folder tree ("excavation field") following real chronology.

**Warum / Why.** Daniel (2026-08-17) bemerkte veraltete Zahlen im Tab (fünf Einträge, vorgebacken beim Build). Er wollte „so ne art eigenes simuliertes ordnerbaum ähnlich wie vps nur selbstgewählte ordnernamen und pfade, weil es ja archäologisch ist“. Zwei Rückfragen führten zu einer Korrektur der Datumsanzeige.
Daniel noticed outdated numbers (five entries, baked at build time). He wanted his own simulated folder tree similar to the VPS, but with self-chosen names and paths because it is archaeological. Two follow-up questions led to a correction of the date display.

**Was liegt drin / What is inside.** Vier Dateien in `werkraum/docs/`: Historiendoku, Lernprotokoll, verwaiste Dateien, Output-Wortlaut. / Four files in `werkraum/docs/`: history doc, learning log, orphaned files, output wording.
