# Roadmap: Gesamtkonstrukt-Betriebssystem, Agentic-OS-Logik

**Nächster Schritt, konkret:** noch keiner begonnen. Wenn's losgeht: Stufe A,
Baustein `actorStream`-Feld zu `_append_event`/`planner_events_stream.py`
ergänzen - kleinster, risikoärmster Einstieg.

Stand 03.09.2026. Fortsetzung des sechsstufigen Megaplans vom selben Tag (Körper-
Schema, Fenstersystem, Mehrstrom-Briefkasten, Live-Updates, Echte Pfade - alle
sechs fertig, siehe `Claude_Work/2026090*`). Diese Roadmap ist die nächste Ebene:
nicht mehr "hat der Planer die Grundfunktionen", sondern "fühlt sich das wie ein
echtes Agentic OS an, nicht wie ein geteilter Arbeitsraum mit Dateien drin".

Nur Stufe C und D brauchen wirklich die Daten der vorherigen (C braucht A, D
braucht A+B) - Stufe B selbst hat keine technische Abhängigkeit von A, nur eine
organisatorische Vorbedingung (die ungeklärte Strom-Liste unten). Stufe E ist
von keiner der anderen abhängig. Die Reihenfolge unten ist trotzdem sinnvoll
(klein und risikoarm zuerst), aber nicht überall technisch erzwungen
(Tree-of-Thoughts-Fund 03.09.) - falls es je Grund gibt, B parallel zu A oder E
früher zu bauen, spricht nichts technisch dagegen.

## Stufe A — Sichtbarer Zustand über alle Ströme

**Ziel:** eine Statusleiste, die für jeden der vier Ströme zeigt: arbeitet gerade /
wartet auf Freigabe / fertig / inaktiv - nicht nur das binäre "neu"-Badge vom
Mehrstrom-Briefkasten.

**Baustein:** `live_stream.js` liefert schon `serverRevision`-Events. Erweitern um
ein zweites, leichtes Signal: welcher Strom hat die letzte Änderung ausgelöst,
worüber (Datei-Pfad oder Körper-ID reicht). Kein neuer Prozess nötig - dieselbe
SSE-Verbindung, ein zusätzliches Feld im JSON.

**Aufwand:** klein. Backend: `_append_event`/vergleichbare Stellen um `actorStream`
ergänzen. Frontend: neue kleine Statusleisten-Komponente, ähnlich `real_fs_ui.js`
im Aufbau.

**Fertig, wenn:** man ohne zu klicken sieht, welcher Strom gerade woran arbeitet.

## Stufe B — Explizite Rechte pro Strom

**Vorbedingung, ungeklärt (Redteam-Fund 03.09.): die Strom-Liste selbst steht
nicht sicher fest.** `workspace.js`s `STREAMS` (claude/chatgpt-codex/gemini/glm)
stammt aus der Erinnerung, nicht aus einer geprüften Quelle. Der echte Server hat
laufende `vps-mcp-*`-Dienste für `claude`, `codex`, `gemini`, `grok`, `sauber` -
**Grok fehlt in der Briefkasten-Liste komplett, GLM taucht in der echten
Server-Infrastruktur nirgends auf.** Der Widerspruch zieht sich bis ins
Betriebssystem selbst durch (Redteam-Fund 03.09., Runde 5, nachgezählt in
`replica_registry.js`): dort existieren nur zwei Posteingang-Werkstätten
(`posteingang-claude`, `posteingang-chatgpt`), für Gemini/GLM gibt es dort gar
keinen eigenen Briefkasten-Ort, obwohl `workspace.js`s `STREAMS` beide als
gleichwertige Ströme führt - die vier Systeme (Mehrstrom-Briefkasten,
Betriebssystem-Posteingang, `vps-mcp-*`-Dienste, diese Roadmap) nennen aktuell
drei verschiedene Listen. Vor Stufe B mit Daniel klären: welche Ströme zählen
wirklich, ist "ChatGPT/Codex" wirklich eine Identität oder zwei, was ist "sauber"
(Test-Instanz? eigener Strom?), und warum das Betriebssystem selbst nur zwei
Posteingänge kennt. Rechte auf der falschen Liste zu vergeben ist schlimmer als
gar keine - erst die Liste festnageln, dann Stufe B bauen.

**Nicht mit "gelöst" verwechseln (Redteam-Fund 03.09.):** `ai-ströme.md` fand
inzwischen neun echte Zuhause-Ordner auf dem VPS - das macht die Unsicherheit
genauer sichtbar, löst sie aber nicht auf. Neun Kandidaten zu kennen
beantwortet nicht, welche davon als eigenständiger, rechtetragender Strom
zählen sollen (`_grok` z. B. hat gerade mal zwei Einträge) - die Klärung mit
Daniel bleibt offen, jetzt nur mit besserer Ausgangslage.

**Neu (Technik-Recherche 03.09.):** "die Liste festnageln" muss nicht heißen,
vorher am Schreibtisch eine feste Liste zu beschließen. Das `HookProvider`-
Muster aus der Skill-Datei macht jeden Strom zu einem eigenen, isolierten
Unterordner statt einem Eintrag in einer zentralen Liste - kombiniert mit dem
In-World-Fenster aus Stufe C (neuer Strom taucht auf → Fenster zum Definieren)
löst sich die Liste dann laufend im Betrieb, nicht einmalig im Dokument. Das
ändert nichts an der Reihenfolge (C braucht trotzdem A), aber es nimmt Stufe B
die Pflicht, vorab eine vollständige, für immer richtige Liste zu erraten.

**Warum blockiert das nur Stufe B, nicht Stufe A (die heute schon auf derselben
ungeklärten Liste läuft)?** (Tree-of-Thoughts-Fund 03.09.) Beide haben dasselbe
Unsicherheitsproblem, aber unterschiedlichen Schaden im Fehlerfall: Stufe A zeigt
nur einen Status an - eine falsche Anzeige ist harmlos und mit einem Array-Update
korrigiert. Stufe B vergibt echte Rechte - falsche Rechte auf der falschen Liste
sind viel schwerer rückgängig zu machen. Reibung soll sich am möglichen Schaden
orientieren, nicht an der bloßen Existenz von Unsicherheit.

**Ziel:** weg vom gemeinsamen `ai_stroeme`-Account. Jeder Strom bekommt eine
eigene Identität mit eigenen, einzeln benennbaren Rechten (Vorbild: AWS
WorkSpaces' drei Schalter Eingabe/Sehen/Speichern).

**Baustein:** eigene Django-`is_staff`-Accounts statt einem, einer pro (dann
geklärtem) Strom (analog zur
Ownership-Trennung, die heute schon bei `real_fs_api.py` galt: Freigabe braucht
einen Menschen, nicht irgendeinen authentifizierten Account). Rechte-Tabelle pro
Strom: darf lesen (Echte Pfade) / darf Schreibvorschläge einreichen / darf
Freigaben genehmigen (bleibt vermutlich immer "nein" für alle Ströme, nur Daniel).

**Architektur-Entscheidung, mit Daniel klären bevor gebaut wird:** separate
Accounts pro Strom (mehr Verwaltungsaufwand, klar wer was tat) oder ein Account +
eigenes Rechte-Feld pro Anfrage (einfacher, aber Audit-Trail schwächer)?

**Aufwand:** mittel - neue Accounts/Rechte-Tabelle sind überschaubar, aber
blockiert durch die ungeklärte Liste oben, nicht durch den Code selbst.

**Teilschritt-Checkpoints:** (1) Liste mit Daniel geklärt. (2) Accounts/
Rechte-Feld angelegt, noch nicht durchgesetzt. (3) Mindestens eine Aktion
zeigt den Strom im Log, nicht nur "authentifiziert".

**Fertig, wenn:** im Log nachvollziehbar ist, welcher *Strom* (nicht nur "irgendein
authentifizierter Zugriff") eine Aktion ausgelöst hat.

## Stufe C — Der Schrottplatz

**Ziel:** kein 2D-Raster, kein Büro (das bauen `bagidea-office`, `pixel-agents`
& Co. schon, siehe Skill-Datei) - ein Schrottplatz, Peters Haufensystem-Logik.
Volles Bild in `memoarenmanifentvisionsblueprritroadmaplikehure.md`, hier nur
das Baubare daraus:

- **Haufen** = ganze Teilsysteme (Surface, Toolbox, Gesamtatlas, Flarum,
  "the-game" selbst - "GeniVault" war nur der erste, ungenaue Name dafür im
  Gespräch, siehe Vision-Datei) - keine neue Datenstruktur, nur eine Sicht auf
  das, was an Teilsystemen schon existiert.
- **Kleines Material zwischen den Haufen** = die 17 Replika-Werkstätten aus
  `replica_registry.js`, unverändert in ihrer Bedeutung, nur neu gerendert.
- **Zuhause pro Strom** = eine Szene, deren Zustand sich aus echten Daten
  ableitet (Briefkasten, Gesamtatlas, virtueller Desktop, Terminals - Liste
  laut Vision-Datei nicht abgeschlossen). Konkrete Grundlage inzwischen in
  `ai-ströme.md`: neun reale Zuhause-Ordner auf dem VPS, fünf laufende
  `vps-mcp-*`-Dienste, Terminal-Capture für fünf Ströme - nicht mehr nur
  Konzept, sondern echtes Ausgangsmaterial.
- **Pinnwand mit rotem Faden** = die visuelle Form der schon vorhandenen
  `relations`-Kanten (`replica_registry.js`s "truth"-Kategorien, Zeile ~37ff.)
  - existiert im Datenmodell, nirgends sichtbar. Das ist der erste Teil von
  Stufe C, der ohne neue Datenstruktur baubar ist. Der Gesamtatlas-Haufen
  liefert dafür schon einen echten Mechanismus zum Dranpappen
  (`atlas_stream_file_write`, zwölf Kategorien) und zum Wiederfinden
  (`atlas_hybrid_search`/`atlas_find`) - kein neues Werkzeug erfinden, nur
  anbinden.

**Baustein (Technik-Recherche 03.09., voll in SKILL.md):** PixiJS v8 oder
melonJS als Renderer, gespeist über `planner_events_stream.py` (bestehende SSE-
Verbindung, kein neuer Prozess) statt einem neuen WebSocket-Kanal. Canvas als
eigene Ebene unter/neben GKWindows, nicht als Ersatz - Klick auf eine Figur auf
dem Platz öffnet weiterhin das bestehende GKWindows-Fenster für die jeweilige
Werkstatt.

**Zwei Lücken, die "kein neuer Prozess" verdeckt (Redteam-Fund 03.09.):**
Erstens trägt `planner_events_stream.py` heute nur `{"serverRevision": N}` -
eine einzelne Zahl, verifiziert per `grep` gegen die Datei. Für den Schrottplatz
braucht es ein echtes, typisiertes Event-Schema (welcher Strom, welcher Haufen,
welche Aktion) - kein neuer Prozess, aber ein deutlich größerer Payload-Umbau
als Stufe A allein liefert. Zweitens schreibt `real_fs_api.py` (SKILL.md,
Technik-Grundlage) komplett am Events-System vorbei - ohne eigenes Event-
Schreiben dort zeigt der Schrottplatz nur Sandkasten-Aktivität, nie echte
VPS-Arbeit. Beides ist Vorarbeit für Stufe C, nicht Teil davon selbst.

**Noch offen, nirgends recherchiert:** wie Figuren zwischen Haufen laufen
(Pathfinding). `pixel-agents`/`age-of-agents` haben das selbst mit Canvas2D
gebaut, melonJS würde es eingebaut mitbringen, PixiJS nicht - reiner
Renderer ohne Wegfindung. Beeinflusst direkt, welcher der beiden Kandidaten
am Ende weniger Eigenbau bedeutet.

**Wenn ein unbekannter Strom auf dem Platz auftaucht:** kein Blocker, ein
Fenster - benennen, einrichten, Rechte vergeben, editierbar. Technisch die
`HookProvider`-Idee aus SKILL.md: neuer Strom = ein neuer Unterordner, keine
zentrale Liste, die vorher feststehen muss. Löst das Roster-Problem aus Stufe B
strukturell mit, statt es nur zu verschieben.

**Aufwand:** groß - größte Stufe der Roadmap, neuer Renderer, neues Event-
Schema, echtes Vorarbeit-Paket (siehe die zwei Lücken oben) vor dem
eigentlichen Bau.

**Teilschritt-Checkpoints:** (1) Event-Schema erweitert, `real_fs_api.py`
schreibt Events. (2) Renderer zeigt einen einzigen Haufen mit echten Daten,
ohne Bewegung. (3) Erste Figur läuft (Pathfinding gelöst). (4) Roter Faden
zwischen zwei echten Objekten sichtbar.

**Fertig, wenn:** man von einer einzigen Ansicht aus sieht, welche Werkstatt
gerade "belebt" ist, ohne jedes Fenster einzeln zu öffnen - plus mindestens ein
sichtbarer roter Faden zwischen zwei tatsächlich verbundenen Objekten.

## Stufe D — Lebendige Spezifikation

**Ziel:** ein Körper, an dem mehrere Ströme sichtbar gemeinsam arbeiten -
Koordinator + Umsetzer + Prüfer-Rollen wie bei "Intent by Augment", gegen eine
gemeinsame, sich selbst aktualisierende Zieldefinition statt getrennter
Einzelbeiträge.

**Baustein:** Erweiterung des Körper-Schemas (`gkos.koerper.v1`) um ein
`rolle`-Feld pro beteiligtem Strom, plus Live-Update (Stufe A/SSE) wenn sich der
Körper unter der Hand ändert.

**Architektur-Entscheidung:** wie werden Konflikte behandelt, wenn zwei Ströme
gleichzeitig denselben Körper ändern? Braucht Daniels Entscheidung, nicht mein
eigener Griff.

**Aufwand:** groß - Konfliktbehandlung bei echter Nebenläufigkeit ist die
technisch schwerste Frage der ganzen Roadmap, plus wartet auf Daniels
Architektur-Entscheidung.

**Teilschritt-Checkpoints:** (1) `rolle`-Feld existiert im Schema, noch ohne
Konfliktlogik. (2) Zwei Ströme können nacheinander (nicht gleichzeitig) am
selben Körper arbeiten. (3) Konflikt wird erkannt und angezeigt, noch nicht
automatisch gelöst. (4) Beide sehen Änderungen live, ohne Überschreiben.

**Fertig, wenn:** zwei Ströme denselben Körper gleichzeitig bearbeiten können,
ohne dass einer den anderen überschreibt, und beide die Änderungen des anderen
live sehen.

**Verbindung zu Stufe C:** die Pinnwand mit rotem Faden dort ist die naheliegende
Anzeige dafür, dass zwei Ströme am selben Körper hängen - kein separater
Baustein, dieselbe `relations`-Kante, nur mit zwei Enden statt einem.

**Leitprinzip, älter als diese Roadmap (Daniel, 22.08., wiedergefunden in
`docs/2026-08-22_harness_recherche_bericht.md`):** "dort arbeiten die
AI-Ströme direkt an den Knoten/Kanten und am zugrundeliegenden Python-Code,
nicht nur in Textform darüber. Ein erkannter Fehler führt zu einer konkreten
Änderung am Knoten/Kanten/Code, die ausprobiert wird - nicht zu einem
Textabsatz mit Ankündigung für später." Härter als alles hier - Stufe D sollte
sich daran messen, nicht nur an "live sehen".

**Abgrenzung (Redteam-Fund 03.09.):** dieses Leitprinzip gilt fürs alltägliche
Arbeiten (Fehler gefunden → Knoten/Kante/Code direkt ändern, nicht nur
Text darüber schreiben) - es hebt die Konflikt-Regel zwei Absätze oben nicht
auf. Zwei Ströme gleichzeitig am selben Körper bleibt Daniels Entscheidung,
"direkt handeln" heißt nicht "Konflikte selbst auflösen".

**Später, nicht jetzt:** ein "Codewesen-Live-Tab" (aus demselben Dokument,
nie gebaut) - Smallville-Dashboard-Idee (Memory-Stream, Ort, gesendeter
Prompt, live) kombiniert mit einer Langfuse-artigen Knoten/Kanten-Trace-
Ansicht. Passt konzeptionell hierher, kein aktueller Baustein.

**Auch später (Ideen-Redteam 03.09.):** ein eigener "Baustellen-Haufen" auf
dem Schrottplatz, der diese Roadmap selbst darstellt - Stufen als Teilhaufen,
sichtbar wachsend. Braucht einen Datei-Watcher/Git-Hook, der Änderungen an
diesen drei Dateien in Events übersetzt - Infrastruktur, die vor Stufe A noch
nicht existiert. Erst wenn Stufe C steht, sinnvoll nachrüstbar.

## Stufe E — Ressourcen-Sichtbarkeit

**Ziel:** sichtbar machen, was eine Aktion tatsächlich anfasst, bevor sie läuft -
nicht nur bei echten Dateischreibvorgängen (das hat `real_fs_api.py` mit dem
Backup-Prinzip schon andeutungsweise), sondern als generelles Vorschau-Prinzip.

**Baustein:** am ehesten eine Erweiterung des Freigabe-Dialogs aus Stufe 5 des
Megaplans (`real_fs_ui.js`s Vorher/Nachher-Diff) auf weitere Aktionsarten, sobald
es welche gibt, die das brauchen. Kein eigenständiger Baustein, bis ein konkreter
Anlass da ist - nicht auf Vorrat bauen.

**Fertig, wenn:** eine neue riskante Aktionsart entsteht und automatisch dasselbe
Vorschau-Muster wie Echte Pfade bekommt, statt eine eigene Lösung zu erfinden.

**Kein Aufwand-Feld, bewusst:** diese Stufe ist reaktiv, kein planbarer Bau -
"nicht auf Vorrat bauen" widerspricht einer vorab geschätzten Größe oder
Teilschritten. Aufwand hängt komplett davon ab, welche Aktionsart den Anlass
liefert.

---

## Nicht Teil dieser Roadmap

Die Orchestrierungs-Schicht (wer entscheidet automatisch, welcher Strom welche
Aufgabe bekommt) fehlt komplett und bleibt bewusst offen - das ist eine deutlich
größere Architektur-Entscheidung (siehe Skill-Datei), keine, die sich in eine
Stufe pressen lässt, ohne dass Daniel das Gesamtbild erst mitentscheidet. Der
konkrete Marker dieser Grenze (Tree-of-Thoughts 03.09., Details in SKILL.md): der
manuelle Strom-Dropdown in `workspace.js`/`human_start.js`. Solange jede
Strom-Zuweisung über einen bewussten Klick dort läuft, bleibt Orchestrierung bei
Daniel - eine automatische Vorauswahl wäre der Moment, an dem diese Grenze neu
verhandelt werden muss.

**Getrennt davon, klein und baubar (Fund 04.09., Vision-Datei "Der Sitz"):** der
sichtbare Sitz selbst - ein Ding auf dem Platz, das zeigt wer gerade
koordiniert (Daniel oder ein Strom) und eine Abgabe als sichtbare Kante macht,
statt als stiller Klick im Dropdown. Das ersetzt den Dropdown nicht technisch,
macht ihn nur sichtbar - keine automatische Entscheidungslogik, die bleibt wie
oben beschrieben offen.
