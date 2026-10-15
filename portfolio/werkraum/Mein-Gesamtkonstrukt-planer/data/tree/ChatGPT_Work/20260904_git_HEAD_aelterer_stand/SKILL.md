---
name: gesamtkonstrukt-agentic-os
description: Design-Logik für das Gesamtkonstrukt-Betriebssystem+Planer, destilliert aus einer Recherche realer 2026-Agentic-OS-Produkte (Viberia, AgentCraft, Wardn AI, AWS WorkSpaces, UFO2, Intent by Augment) und der Schrottplatz-Oberflächen-Vision (Peters Haufensystem, Smallville/Generative Agents, fünf Pixel-Office-Projekte). Anzuwenden bei jeder Weiterentwicklung des Betriebssystem- oder Oberflächen-Teils, damit neue Features an dieselbe Logik anschließen, statt isolierte Einzelstücke zu werden.
---

# Gesamtkonstrukt als Agentic OS — die Logik dahinter

**Stand: 03.09.2026, noch keine Stufe der ROADMAP.md begonnen - reine
Planungsphase, kein Code gebaut.** (Von jeder Session, die hier weiterbaut,
aktualisieren.)

Quelle: `_claude`-Feldakte vom 03.09.2026 ("Agentic-OS-Feldakte", Artifact
`7a52ab33-e9d1-401d-99da-b85f0b00d94f`), zwölf echte Quellen geprüft, neun Muster
kuratiert. Dieser Skill ist die destillierte, operative Fassung davon - für den
täglichen Bauzustand, nicht zum nochmal Nachlesen der ganzen Recherche.

Die konkrete Bildsprache für die Oberflächen-Schicht steht nicht hier, sondern
in `memoarenmanifentvisionsblueprritroadmaplikehure.md` im selben Ordner -
Schrottplatz statt Büro, roh geschrieben, absichtlich noch nicht fertig. Dieser
Skill übersetzt daraus nur das, was schon baubar ist.

## Der Test, ob etwas "OS" verdient (UFO2-Definition)

Ein System heißt nicht deshalb Betriebssystem, weil es echte Prozesse verwaltet.
Es verdient den Namen, wenn es:
1. **verschiedene Anwendungen/Ströme einheitlich behandelt** (dieselbe Oberfläche,
   egal welcher Strom gerade dran ist - genaue Liste ungeklärt, Details in
   ROADMAP.md Stufe B, nicht in dieser Datei)
2. **Aktionen koordiniert an sie verteilt** (nicht "irgendwo hinschreiben", sondern
   gezielt an den richtigen Ort/Strom)

Bevor ein neues Feature gebaut wird: prüfen, ob es diesen Test besteht, nicht ob
es "wie ein Betriebssystem aussieht".

## Die sechs Schichten - wo im Code sie schon existieren

| Schicht | Was sie tut | Wo im Gesamtkonstrukt |
|---|---|---|
| Modell | Das eigentliche Denken | Claude/Codex/Gemini/GLM in den heutigen Ansichten - real mind. neun eigene Zuhause auf dem VPS, siehe `ai-ströme.md` |
| Gedächtnis | Langzeit- vs. Arbeitsgedächtnis | `<Strom>_Work/`-Ordner (Langzeit), laufendes Gespräch (Arbeit) |
| Werkzeug | Anbindung an echte Systeme | `planner_files_api` (Sandkasten, `data/tree/`, alltäglich) + `real_fs_api.py` (echter VPS, hart auf `/root` begrenzt, Freigabe-Pflicht) |
| Orchestrierung | Wer bekommt welche Aufgabe | **noch Daniel selbst - nicht das System** |
| Arbeitsablauf | Verzweigung/Wiederholung, keine starre Linie | Körper-Sequenz-Schema (linear/Loop/frei) |
| Oberfläche | Wie ein Mensch sieht und eingreift | Heute: GKWindows + Live-Banner (`live_stream.js`). Ziel: Schrottplatz-Szene (siehe Vision-Datei) |

Die automatische Entscheidungslogik dieser Schicht (wer bekommt was, ohne dass
Daniel jedes Mal klickt) fehlt komplett und bleibt bewusst offen - keine Stufe
der Roadmap, siehe ROADMAP.md "Nicht Teil dieser Roadmap". Baubar davon ist nur
der sichtbare Sitz selbst (wer koordiniert gerade, Daniel oder ein Strom, und
was wurde von dort delegiert) - siehe "Der Sitz" in der Vision-Datei.

**Konkreter Marker der Grenze (Tree-of-Thoughts 03.09.):** der `<select>`-Strom-
Dropdown in `workspace.js`/`human_start.js` ist heute die einzige Stelle im
System, an der "wer bekommt was" entschieden wird - vollständig manuell, immer
ein bewusster Klick. Sobald dieser Dropdown durch eine automatische Vorauswahl
oder Empfehlung ersetzt wird, auch nur als Komfort-Feature, ist die Grenze
überschritten - das ist der Punkt, an dem diese Zeile neu verhandelt werden muss.

## Fünf Muster, mit echtem Beleg, in Bauprioritäts-Reihenfolge

Reihenfolge folgt echten Abhängigkeiten nur teilweise - nicht jedes Muster
braucht zwingend die Daten des vorherigen. Volle Begründung und Ausnahmen:
`ROADMAP.md` im selben Ordner, direkt am Anfang.

1. **Sichtbarer Zustand** (Viberia: "wer ist blockiert/fragt/fertig") - eine
   Statusleiste über alle Ströme, nicht nur das binäre Briefkasten-Badge von heute.
2. **Explizite Rechte pro Strom** (AWS WorkSpaces: drei einzeln abschaltbare
   Schalter pro Agent - Eingabe/Sehen/Speichern) - weg vom gemeinsamen
   `ai_stroeme`-Account, hin zu benennbaren Einzelrechten.
3. **Räumliche Karte statt Fenster-Kaskade** - nicht mehr Viberia/AgentCraft-
   Zoomkarte, sondern konkret: der Schrottplatz (Ludolfs/Peters Haufensystem),
   Details und Bausteine in ROADMAP.md Stufe C und in der Vision-Datei.
4. **Lebendige Spezifikation** (Intent by Augment: Koordinator + Umsetzer + Prüfer
   gegen eine gemeinsame, sich selbst aktualisierende Zieldefinition) - ein Körper,
   an dem mehrere Ströme sichtbar gemeinsam arbeiten.
5. **Ressourcen-Sichtbarkeit** (RTS-Essay: "was kostet diese Aktion gerade") -
   sichtbar machen was eine Aktion anfasst, bevor sie läuft. Passt zum
   Backup-vor-jedem-Schreiben-Prinzip, das `real_fs_api.py` schon hat.

## Technik-Grundlage für die Schrottplatz-Oberfläche (Recherche 03.09.)

Drei echte Referenzen geprüft, keine Marketingseiten: `pixel-agents`s eigenes
CLAUDE.md (Architektur-Doku eines laufenden Projekts derselben Gattung),
`dandacompany/deskrpg`, und ein echter Build-Bericht des AgentOffice-Autors
(dev.to, kein Werbetext).

**Näheres Vorbild als alle fünf (Fund 03.09., aus `docs/2026-08-22_harness_
recherche_bericht.md`):** Stanford/DeepMinds "Generative Agents" (Smallville,
2023) - echtes, begutachtetes Paper, keine Herstellerseite - dieselbe
Speicher→Reflexion→Planung-Schichtung, die dieses Dokument am 22./23.08.
gegen echten Code (`entity_thinking_log`, `weltbild_builder.py`, `self_model`)
verifiziert hat, nicht nur behauptet. Diese Verifikation ist jetzt drei Wochen
alt, heute nicht neu geprüft - Übernahme, kein frischer Fund. `claudeville`
(AlexHarn, GitHub) portiert denselben Ansatz auf Claude, ist aber nur ein
einzelnes Repo wie Viberia/Wardn AI - derselbe Vorbehalt wie unten bei "Was
NICHT übertragen werden soll", hier nicht nochmal ausformuliert. Smallville
trägt hier das Gewicht, nicht claudeville.

**Muster, das wir schon haben, nur ohne Render-Schicht:** `pixel-agents` trennt
`core/` (keine Abhängigkeiten) von `server/` und `webview-ui/` (beide hängen nur
an `core/`), verbunden über eine einzige `MessageTransport`-Schnittstelle -
dieselbe Laufzeit treibt VS Code und eine eigenständige CLI-Ansicht. Der
`AgentStateStore` ist die alleinige Quelle der Wahrheit, jede Zustandsänderung
läuft ausschließlich durch ihn, erst danach übersetzt eine reine Broadcast-
Schicht das nach außen. Das ist unsere Events-Tabelle (Grundgesetz 5) plus
`planner_events_stream.py` - wir bauen die Render-Schicht auf einem Muster, das
schon existiert, nicht auf einem neuen Fundament.

**Aber nur für den Sandkasten (Redteam-Fund 03.09.):** `_append_event` wird in
`planner_api.py` ausschließlich über `_store_workspace_state` aufgerufen, und
nur `planner_files_api`/`planner_streams_api` rufen die. `real_fs_api.py` -
verifiziert per `grep`, null Treffer - schreibt echte VPS-Pfade komplett am
Events-System vorbei. Eine Schrottplatz-Szene, die nur aus dem bestehenden
Event-Strom gespeist wird, würde jede Sandkasten-Aktion zeigen, aber keine
einzige echte Freigabe/Schreibaktion auf `/root` - der auffälligste, am
schwersten zu übersehende Teil der Arbeit bliebe unsichtbar. `real_fs_api.py`
braucht eigenes Event-Schreiben, bevor Stufe C dafür irgendetwas zeigen kann.

**Löst die Strom-Roster-Frage strukturell, nicht dokumentarisch:** das
`HookProvider`-Interface macht "neuen Strom anbinden" zu einem einzelnen neuen
Unterordner, null Änderungen an Laufzeit/UI/bestehenden Providern. Genau das
In-World-Fenster aus der Vision-Datei (neuer Strom taucht auf → Fenster zum
Definieren/Einstellen, keine Dokument-Vorbedingung) - Details dazu in ROADMAP.md
Stufe B.

**Konkrete Stolpersteine (AgentOffice-Build-Bericht):** Canvas-Layer und HTML-
Overlay (GKWindows) teilen sich sonst die Tastatur - Canvas-Tastaturfang
abschalten, sobald ein `<input>` fokussiert ist. Kamera-Bewegung per Lerp
(`x += (ziel - x) * 0.08`), nicht hart springen. Rendering und UI-Zustand über
Event-Busse trennen, nie geteilten State.

**Kein externes Vorbild, sondern schon im eigenen Werkraum gebaut (Fund
04.09.):** `_gpt/gesamtatlas/` ist ein laufendes AgentStateStore-Äquivalent
für Ströme, nicht nur eine Analogie - AI-Strom-Brücken pro Strom (Zuhause,
Sessions, Projekte, immer mit Beleg), drei Suchschichten, manuelles
Einbringen eigener Inhalte über `atlas_stream_file_write` (zwölf Kategorien),
Suche über `atlas_hybrid_search`/`atlas_find`. Bisher komplett getrennt vom
Gesamtkonstrukt-Planer - kein Draht zum Events-Strom, keine Anbindung an
GKWindows, nur über eigene MCP-Werkzeuge erreichbar. Zwei tragende Dienste
(`mcp-gesamtatlas-light`, `gesamtatlas-proof-capsule`) liefen wochenlang
kaputt, am 04.09. gefunden und repariert - der Atlas selbst ist stabil,
die Verbindung zum Betriebssystem fehlt einfach noch.

**Technik-Wahl:** PixiJS v8 oder melonJS statt vollem Phaser - wir brauchen
keine Kollisionsphysik, nur Datenvisualisierung, die wie ein Spiel aussieht.
Die beiden sind aber kein Entweder-oder auf gleicher Höhe (Redteam-Fund
03.09.): PixiJS ist reiner Renderer, Tiled-Karten und Pathfinding (Figuren
laufen zwischen Haufen) müssten wir selbst bauen, wie `pixel-agents` es mit
Canvas2D getan hat. melonJS bringt beides eingebaut mit. Die Wahl hängt davon
ab, ob wir die Kontrolle des reinen Renderers wollen oder den Eigenbau sparen -
noch nicht entschieden, ROADMAP.md Stufe C nennt Details.

## Was NICHT übertragen werden soll

- Die 32-Punkte-Musterliste von agentic-design.ai NICHT als Checkliste behandeln -
  liest sich wie eine Content-Sammelseite, nicht wie gelebte Praxis. Nur was in
  echten, laufenden Produkten belegt war, zählt.
- Große Ankündigungen (Microsofts Project Solara) NICHT als Vorbild ernst nehmen,
  solange keine echte Oberfläche zu sehen ist - nur Sprache über "geformt um dich",
  keine Bilder. Genau der Fall aus der CLAUDE.md: erst ernst nehmen wenn unabhängig
  bestätigt, nicht wenn nur behauptet.
- Derselbe Maßstab gilt für die positiv zitierten Quellen genauso (Tree-of-
  Thoughts-Fund 03.09.): Viberias Product-Hunt-Seite, Wardn AIs GitHub-README
  und `claudeville` (Technik-Grundlage oben) sind ebenfalls nur Herstellerdar-
  stellung, keine unabhängig bestätigte Dritt-
  Quelle. Sie zeigen echte Screenshots/Code statt nur Sprache - das macht sie
  konkreter, nicht automatisch vertrauenswürdiger. Nicht unhinterfragt mehr
  Vertrauen geben als Solara, nur weil die Aufmachung kleiner/nahbarer wirkt.
- Freigabe-Pflicht (Muster 2 der Feldakte) gilt bisher **nur** für `real_fs_api.py`
  (propose-write → approve). Der ganz normale Sandkasten (`planner_files_api`s
  `create`/`save`/`koerper-save` - Körper, Briefkasten-Notizen, der Alltag) schreibt
  weiterhin sofort, ohne Freigabe-Schritt, mit dem gemeinsamen `ai_stroeme`-Account.
  Redteam-Fund 03.09.: das ist bewusst so belassen (Sandkasten = geringes Risiko),
  aber nicht "erledigt" im Sinne von "überall gelöst" - beim Formulieren nicht
  verwechseln.

## Bei jedem neuen Betriebssystem-Feature fragen

1. Besteht es den UFO2-Test (einheitlich behandeln + koordiniert verteilen)?
2. Welche der sechs Schichten bedient es - und existiert die darunterliegende
   Schicht schon, oder baut das Feature auf Sand?
3. Ist es Stufe N der Roadmap, oder überspringt es eine Stufe, deren Daten es
   eigentlich bräuchte?

## Wann ein Fund eine volle Redteam-Runde braucht

Klein (Zahl, Tippfehler, veraltete Zeilenangabe) → direkt fixen, keine Runde
nötig. Groß (neues externes Dokument mit eigener Architektur-Aussage,
Widerspruch zwischen zwei Dateien hier, eine Entscheidung die Daniel treffen
muss) → volle Runde. Im Zweifel: lieber eine Runde zu viel als ein Fund, der
unkommentiert stehen bleibt.

## Mehr über diesen Skill selbst

Grenzen des Ladens, Umgang mit Fund-Vermerken: `META.md` im selben Ordner -
einmal lesenswert, nicht bei jedem Feature nötig.
