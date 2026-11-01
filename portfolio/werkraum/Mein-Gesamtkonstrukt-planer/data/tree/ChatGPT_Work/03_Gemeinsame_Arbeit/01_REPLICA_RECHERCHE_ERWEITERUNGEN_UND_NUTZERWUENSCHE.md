# Rechercheakte: Erweiterungen, Nutzerwünsche und Bauableitungen für die 17 Replicas

**Stand:** 22. August 2026  
**Zweck:** Material für echte, unterschiedliche Replica-Funktionen im Gesamtkonstrukt-Planer.  
**Wichtig:** Das ist keine Liste von Funktionen, die bereits existieren. Es ist eine belegte Bau-Recherche. Jede abgeleitete Funktion bleibt Vorschlag, bis sie geplant, gebaut und im echten Browser geprüft wurde.

## Wie diese Recherche zu lesen ist

Für jede Replica wurden drei Dinge getrennt gesammelt:

1. **Erweiterungs-Ökosystem:** offizielle Plugins, Libraries, Power-Ups, Packages oder SDK-Haken.
2. **Nutzersignal:** wiederkehrende konkrete Wünsche oder Probleme aus offiziellen Foren, Issue-Trackern oder Community-Beiträgen.
3. **Bauableitung:** was davon im Planer einen eigenen Zweck hätte – und was ausdrücklich *nicht* als bloße Nachahmung übernommen wird.

Ein einzelner Post ist kein Mehrheitsbeweis. Er ist ein echter Bedarfshinweis. Bevor daraus gebaut wird, muss er gegen ähnliche Meldungen, die eigene Nutzung von dak und den Daten-/Sicherheitsvertrag des Planers geprüft werden.

Eine „perfekte Replica“ kann ich nicht garantieren. Der überprüfbare Weg dorthin ist: Originalprogramm selbst benutzen, Hauptfluss filmen/protokollieren, reale Nutzerprobleme sammeln, einen einzigen Kernfluss bauen, mit Playwright und echten Personen testen, danach den nächsten Kernfluss. Nicht: alle Menüpunkte kopieren.

## Gemeinsame Regeln für alle Replicas

- Jede Replica erhält eine eigene **Kernhandlung**, die in keiner anderen Ansicht genauso ersetzt wird.
- Alle lesen dieselben echten Objekt-IDs, Dateien, Versionen und Kanten. Sie erhalten keinen eigenen Schattenbestand.
- Eine sichtbare Zeichnung, Gruppierung oder räumliche Nähe wird nicht automatisch zu einer semantischen Kante.
- Plugins/Erweiterungen werden im Planer zunächst als **Werkzeugkarten mit Herkunft, Version, Berechtigung und Risiko** modelliert – nicht blind installiert oder ausgeführt.
- Jede Übernahme aus Nutzerfeedback speichert: Quelllink, Datum der Sichtung, konkrete Beobachtung, geplante Antwort und Ablehnungsgrund, falls nicht gebaut.
- Bei Code-/Plugin-Ökosystemen gilt zusätzlich: Berechtigung, lokaler Dateizugriff, Netzwerkzugriff, Geheimnisse und Updateweg müssen sichtbar sein.

---

## 1. Excalidraw / tldraw – Denken mit Hand und Raum

**Eigenständige Kernhandlung:** schnell skizzieren, gruppieren, Pfeile ziehen, etwas räumlich erklären, ohne dafür schon eine echte Graph-Beziehung zu behaupten.

**Ecosystem-Beleg:** Excalidraw bietet öffentliche Element-Bibliotheken; tldraw ist ausdrücklich als SDK mit eigenen Shapes, Tools, Bindings und UI-Bausteinen angelegt.

- Quelle: Excalidraw Libraries
- Quelle: tldraw SDK

**Echte Nutzersignale:** Mehrere Excalidraw-Issues verlangen sortierbare/auffindbare Bibliotheken statt einer unübersichtlichen Elementmasse. tldraw führt eigene Accessibility-Themen und aktuelle Fehler bei Fokus/Reset – das ist ein Warnzeichen gegen eine Canvas-UI, die nur mit Maus gut aussieht.

- Quelle: Gruppierte Excalidraw-Bibliotheken
- Quelle: Bibliothekssuche bei vielen Elementen
- Quelle: tldraw Accessibility-Thread

**Für den Planer bauen:** Zeichenwerkzeuge, Auswahl, Gruppen, Frames, freier Text, Pfeile, eigene wiederverwendbare Symbolbibliotheken mit Suche/Tags und „als Objekt verknüpfen“. Eine Skizzenkante ist zunächst `visual_only`; erst „Beziehung übernehmen“ erzeugt eine echte Kante mit Herkunft.

**Nicht blind kopieren:** das komplette tldraw-/Excalidraw-Dateiformat oder ein allgemeines Plugin-Sandboxsystem, bevor der eigene Zeichenfluss steht.

**Abnahmetest:** Auf Mobil und Desktop drei Formen, eine Gruppe und einen Pfeil zeichnen; ein reales Objekt daran heften; Reload; danach bewusst eine semantische Kante übernehmen und Herkunft sehen.

## 2. PureRef – Referenzwand statt Dateifriedhof

**Eigenständige Kernhandlung:** Bild-, Screenshot-, PDF- und Dateireferenzen ohne Zwang zu Kartenlogik nebeneinander legen, schnell vergleichen und zur Quelle zurückspringen.

**Ecosystem-Beleg:** PureRef-Nutzer fordern ausdrücklich eine online teilbare, kollaborative Variante. Vergleichswerkzeuge setzen zusätzlich auf Cloud-Sync, Tags und gemischte Medien – das sind Bedarfssignale, keine Produktvorgabe.

- Quelle: PureRef-Forum: online/shareable version
- Quelle: PureRef-Alternativen mit Cloud-/Tag-Schwerpunkt

**Echte Nutzersignale:** Menschen wollen Referenzen geräteübergreifend wiederfinden, gemeinsam anschauen und nicht bei vielen Medien den Überblick verlieren. Das eigentliche Defizit ist weniger Malen als Herkunft, Suche und Austausch.

**Für den Planer bauen:** dunkle Referenzwand, Drag-and-drop, Zoom/Pan, Stapel, Labels, Pin, Vergleichsmodus, Bildausschnitt-Anmerkung, Link zum Originalpfad und Rechte/Quelle sichtbar. Referenzen können an Idee/Konzept/Datei gebunden sein, ohne ihr Inhalt zu werden.

**Abnahmetest:** Drei hochgeladene Bilder, ein PDF und eine URL als Referenzen anlegen, frei sortieren, eine Bildstelle kommentieren, in einer zweiten Ansicht das Ursprungsobjekt öffnen.

## 3. Miro / FigJam / Milanote – gemeinsames Sortieren und Feedback im Raum

**Eigenständige Kernhandlung:** aus losen Gedanken, Bildern und Notizen ein lesbares Arbeitsbrett machen, Bereiche bilden und Menschen an genau einer Stelle sprechen lassen.

**Ecosystem-Beleg:** Miro stellt Apps/Integrationen für Boards bereit; Milanote kann Kommentare an konkrete Karten heften, die beim Verschieben mitwandern. Figma-Widgets zeigen den Unterschied zwischen einmaligen Plugins und gemeinsam interaktiven Objekten.

- Quelle: Miro Developer Platform
- Quelle: Milanote-Kommentare an Karten
- Quelle: Figma Widgets für gemeinsame Interaktion

**Echte Nutzersignale:** Miro-Nutzende brauchen Erweiterungen und Synchronisierung für ihren Kontext. Milanote hat eine eigene öffentliche Wunschliste für Kommentar-Workflows. Der Wunsch ist: Feedback soll am Ding bleiben, nicht in einem separaten Chat verschwinden.

- Quelle: Milanote: Comment-workflow-Wünsche
- Quelle: Miro App-Beispiele

**Für den Planer bauen:** Sticky Notes, Frames, freie Karten, Kommentare/Marker am Inhalt, Sammeln → Clustern → bewusste Übernahme. Kommentare werden als Ereignis mit Autor und Bezug gespeichert. Der Board-Bereich darf Kontext gruppieren, erzeugt aber keine Kante, bis jemand sie explizit setzt.

**Abnahmetest:** Zwei Nutzerrollen hinterlassen Kommentar und Antwort an einer Karte; Karte verschieben; Kommentar bleibt; Entscheidung daraus wird als eigenes Objekt/Feedback übernommen.

## 4. Obsidian Canvas / Heptabase – Denken aus Dokumenten

**Eigenständige Kernhandlung:** mit echten Texten/Abschnitten denken, Quellen vergleichen, daraus eine Argumentation oder Wissenskarte bauen und jederzeit zurück in den Originaltext kommen.

**Ecosystem-Beleg:** Obsidian-Plugins ergänzen Canvas um Backlinks, Frontmatter/Tags und das Senden von Notizen/Blöcken in den Canvas. Heptabase sammelt Feedback im Produkt und unterscheidet selbst neue Fähigkeiten von Reibungsabbau.

- Quelle: Advanced Canvas
- Quelle: Semantic Canvas: Backlinks und Tags
- Quelle: Heptabase über Feedback im Produkt

**Echte Nutzersignale:** Nutzer kritisieren fehlende/unsaubere Einbettungen, Performance und dass Canvas-Karten nicht als echte Verbindungen im Graph auftauchen. Besonders konkret: Rücklink von Note zum Canvas und sichtbare Tags/Backlinks.

- Quelle: Canvas-Rücklink-Wunsch
- Quelle: Canvas-Karten fehlen im Graph
- Quelle: Performance-Problembericht

**Für den Planer bauen:** Datei-/Abschnittskarten mit Textvorschau, Zitatauswahl, Backlinks, Quellenpfad, Split View (schreiben links, Material rechts), Karten-Layout mit echten/visual-only Beziehungen getrennt und „wo wird diese Datei verwendet?“-Rückweg.

**Abnahmetest:** Einen Absatz aus einer Datei auf Canvas legen, eine Aussage markieren, Rückweg zum exakten Textbereich öffnen, danach alle Canvas-Verwendungen der Datei anzeigen.

## 5. Photoshop / Krita – bildliche Arbeit mit Verantwortung für Versionen

**Eigenständige Kernhandlung:** ein konkretes Bild in Ebenen verändern – malen, auswählen, maskieren, radieren, vergleichen –, ohne Original oder Bearbeitungsgeschichte zu verlieren.

**Ecosystem-Beleg:** Krita hat ein offenes Plugin-Umfeld und strukturiertes Feature-Request-Voting; Photoshop/Creative Cloud hat einen Plugin-Markt und öffentliche Feature-Request-Bereiche.

- Quelle: Krita-Feature-Request-Voting
- Quelle: Krita Plugin-Themen
- Quelle: Photoshop Community

**Echte Nutzersignale:** Bei KI-Bildwerkzeugen wünschen Nutzer engere Steuerung (z. B. negative Vorgaben im Live-Modus), bei Plugins wiederkehrend verlässliche Auffindbarkeit/Installation. Das sind gute Gründe, Bildarbeit und Tool-Berechtigung nicht zu vermischen.

- Quelle: Krita AI Diffusion: negative prompt in live mode
- Quelle: Photoshop-Plugins nicht mehr sichtbar

**Für den Planer bauen:** zuerst einen **kleinen** Bildkörper: Ebenenliste, Sichtbarkeit, Deckkraft, Brush/Marker, Radierer, Rechteck-/Lasso-Auswahl, Masken-Grundmodell, Undo/Redo, Vorher/Nachher und neue abgeleitete Datei statt Überschreiben. AI-Bildvorschlag ist eine Ebene/Vorschau, nie still die Datei.

**Abnahmetest:** Bild laden, zwei Ebenen anlegen, auf einer markieren, eine Maske setzen, Version als neues Derivat speichern und Original/Derivat vergleichen.

## 6. Illustrator / Inkscape / Affinity – präzise Wege statt Pixelmalerei

**Eigenständige Kernhandlung:** Form, Pfad, Kurve und Anfasser gezielt bauen und als editierbares Vektorartefakt speichern.

**Ecosystem-Beleg:** Inkscape besitzt ein eigenes Extensions-Projekt; aktuelle Wünsche umfassen unter anderem mehr portable Plugin-Modelle. Affinity betont, dass Pixel-, Vektor- und Layout-Struktur beim Import erhalten bleiben soll.

- Quelle: Inkscape Extensions
- Quelle: WASM-Plugin-Vorschlag für Inkscape
- Quelle: Affinity: Struktur beim Import erhalten

**Echte Nutzersignale:** Erweiterungen müssen installierbar, erklärbar und kompatibel sein; die Inkscape-Community trennt UI/UX-/Wishlist-Themen explizit. Daraus folgt: nicht nur SVG anzeigen, sondern Pfadlogik und Versionsfähigkeit sichtbar machen.

- Quelle: Inkscape-Extensions-Labels

**Für den Planer bauen:** Pen/Bezier-Pfad, Knoten/Griffe, Rechteck/Kreis/Polygon, Füllung/Kontur, Gruppen/Ebenen, SVG-Import/-Export und direkte Verknüpfung zum Konzeptobjekt. Kein Photoshop-Ersatz: hier zählt Pfadpräzision.

**Abnahmetest:** Pfad mit drei Knoten bauen, Griff verändern, Farbe/Kontur ändern, SVG exportieren/reimportieren und editierbar erhalten.

## 7. n8n / Node-RED – Automationen mit echten Läufen

**Eigenständige Kernhandlung:** Trigger, Datenfluss, Bedingungen, Fehlerwege und einen realen Testlauf bauen; danach Run-Log und Ergebnis prüfen.

**Ecosystem-Beleg:** Node-RED betreibt eine große Node-/Flow-Library; n8n diskutiert Frontend-/Backend-Erweiterungen mit eigenen Views, Routen und Hooks.

- Quelle: Node-RED Flow Library
- Quelle: n8n: Community Extensions

**Echte Nutzersignale:** n8n-Nutzer fragen nach besserer Teamarbeit an denselben Workflows und nach einfacherem Feedback. Node-RED-Nutzer schätzen die direkte Verkabelung, brauchen aber Status-, Fehler- und Testinstrumente.

- Quelle: n8n: Team-Entwicklung-Wünsche
- Quelle: n8n: einfacheres Feedback
- Quelle: Node-RED: Ziel und Datenfluss

**Für den Planer bauen:** Trigger-/Action-/Condition-/Human-Approval-Knoten, benannte Ports, Datenvorschau mit Redaction, Testlauf, Run-Historie, Retry/Stop, Fehlerkante, Rollback/Undo-Hinweis, Freigabeschritt. Eine Workflow-Zeichnung ist zunächst Anleitung; Ausführung nur bei sichtbarer Aktivierung und Berechtigung.

**Abnahmetest:** Datei-Upload löst einen harmlosen Testworkflow aus, zeigt Eingabe/Ausgabe/Log; fehlerhafte Eingabe läuft kontrolliert in Fehlerpfad; Run bleibt nach Reload lesbar.

## 8. Unreal Engine Blueprints – Ereignislogik lesen und debuggen

**Eigenständige Kernhandlung:** verstehen, welcher Eventpfad wann welche Funktion/Variable auslöst; nicht nur „Knoten hübsch verkabeln“.

**Ecosystem-Beleg:** Unreal besitzt einen Marketplace-/Fab-Kontext für Plugins und eine aktive Community für Blueprint-/System-Wünsche.

- Quelle: Unreal Marketplace/Fab-Forum
- Quelle: Blueprint-/System-Anfragen

**Echte Nutzersignale:** Nutzer warnen bei Marketplace-Blueprints vor Black Boxes und harten Referenzen; sie wollen Systemverständnis, Kompatibilität und sichtbare Abhängigkeiten statt nur „Asset reinwerfen“.

- Quelle: Community-Warnung zu Blueprint-Plugins

**Für den Planer bauen:** Event-Start, Exec-Leitung von Datenleitung unterscheidbar, Funktions-/Macro-/Subgraph-Knoten, Breakpoint/Trace-Modus, Variablenansicht, Laufweg-Hervorhebung und „Warum ist dieser Pfad gelaufen?“. Der Planer ersetzt nicht Unreal, sondern macht seine eigenen Systemregeln ablesbar.

**Abnahmetest:** Ein Event löst zwei Zweige aus; Trace markiert tatsächlich gelaufenen Zweig und erklärt Stop-/Fehlerzustand.

## 9. Blender Geometry Nodes – Parameter erzeugen sichtbare Resultate

**Eigenständige Kernhandlung:** aus Parametern und Nodes einen reproduzierbaren Körper/Output bauen und sofort sehen, was sich ändert.

**Ecosystem-Beleg:** Blender führt Geometrie-Nodes aktiv in Design-/Feedback-Räumen; Community-Ergänzungen fokussieren explizite Vorschau und die Frage, welche Daten ein Knoten wirklich ändert.

- Quelle: Blender Node-Tool-Feedback
- Quelle: Geometry-Nodes-Vorschau-Addon

**Echte Nutzersignale:** Nutzer loben Nodes gegenüber versteckten Modifier-/Driver-Ketten, weil sie transparenter sind. Zugleich fehlt oft eine einfache, direkte Einsicht in Zwischenwerte und betroffene Geometrie.

- Quelle: Warum Nodes transparenter als Modifier sind

**Für den Planer bauen:** Parameterknoten mit Typ/Min/Max, Node-Gruppen, Ports, Vorschau für abstrakte Daten/Ergebnisse und Momentaufnahme eines Outputs. Nicht sofort eine komplette 3D-Engine nachbauen; zuerst prozedurale Planer-Objekte (z. B. Layout/Cluster/Regelgitter) sichtbar ableiten.

**Abnahmetest:** Einen Parameter ändern; nur der davon abhängige Vorschau-Output aktualisiert sich; die verwendete Node-Gruppe bleibt als wiederverwendbares Artefakt gespeichert.

## 10. Houdini – große Prozesse mit Zwischenschritten beherrschbar machen

**Eigenständige Kernhandlung:** komplizierte Verarbeitung in nachvollziehbare Stufen, Parameter, Caches und wiederverwendbare Digital Assets zerlegen.

**Ecosystem-Beleg:** Houdini Digital Assets werden über Orbolt verteilt und können laut Orbolt auch in andere Anwendungen eingebunden werden. Das Entscheidende ist das portable, parametrisierte Werkzeug, nicht die einzelne Node.

- Quelle: Orbolt / Houdini Digital Assets
- Quelle: Orbolt FAQ zu Presets/Versionen/Assets

**Echte Nutzersignale:** Nutzer kritisieren mangelnde Kuratierung, schwer auffindbare brauchbare Assets und Lücken bei offensichtlichen Grundwerkzeugen. Das ist relevant: ein Planer braucht gute Auffindbarkeit, Vertrauensniveau und Version/Kompatibilität für wiederverwendbare Teilprozesse.

- Quelle: SideFX-Forum: Orbolt-/Grundwerkzeug-Kritik
- Quelle: Community-Kritik: keine Kuratierung/Toolkits

**Für den Planer bauen:** Prozessstufen/Contexts, parametrische „Baugruppen“, Zwischenstand-Cache mit Herkunft, „Promote Parameter“, Version/Preset, Paket-/Abhängigkeitsübersicht und erklärender Ein-/Ausgabevertrag. Das ist die richtige zweite Ebene über n8n, nicht nur ein anderer Node-Skin.

**Abnahmetest:** Ein Unterprozess wird als wiederverwendbare Baugruppe gespeichert, zweimal mit unterschiedlichen Parametern eingesetzt und zeigt jeweils Input, Output, Cache und Version.

## 11. TouchDesigner – lebende Medien- und Signalsysteme

**Eigenständige Kernhandlung:** Live-Daten, Bild, Audio, Zeit und Interaktion als momentan laufende Signale sehen, regulieren und beobachten.

**Ecosystem-Beleg:** TouchDesigner hat Palette-/Komponenten- und Plugin-Pfade; die Palette ist praktisch eine wiederverwendbare Komponentenbibliothek.

- Quelle: TouchDesigner-Palette als Komponentenbibliothek
- Quelle: Plugin-/Custom-OP-Pfad

**Echte Nutzersignale:** Der Palette fehlt Nutzern vor allem Auffindbarkeit: Suche nach Namen, Tags und Parametern wird explizit gewünscht. Auch das Ablegen eigener Komponenten ist fehleranfällig.

- Quelle: Palette-Suchwunsch
- Quelle: Palette-Komponenten lassen sich nicht ablegen

**Für den Planer bauen:** Operator-Typen für Zeit, Zahl, Text, Bild, Audio, Event und Display; Live-Wertanzeige; Pause/Mute/Record; Signalverlauf; Component-Palette mit Tags/Versionen; sichere Quellenbindung. Kein mystisches „Live“-Label ohne laufenden Takt/Wert.

**Abnahmetest:** Ein Zeit-Operator treibt einen sichtbaren Wert; Pause hält ihn; Record speichert einen kurzen Verlauf; ein eigener Component-Baustein ist suchbar und wieder einsetzbar.

## 12. Max/MSP / Pure Data – Patchen von Nachrichten und Signalen

**Eigenständige Kernhandlung:** Audio-, MIDI- oder Datenfluss patchen, hören/sehen, unterbrechen und über einen verständlichen Monitor debuggen.

**Ecosystem-Beleg:** Max arbeitet mit teilbaren Packages/Projects; Pure Data kennt Libraries/Externals mit klaren Ladeoperationen. Beide Welten leben von wiederverwendbaren kleinen Objekten.

- Quelle: Max: Projects und Packages
- Quelle: Pure Data: externals/libraries how-to

**Echte Nutzersignale:** Max-Nutzer wünschen ein sauberes „Auskommentieren“/Deaktivieren von Teilpatches, ohne die Verkabelung zu verlieren. Pure-Data-Nutzer berichten wiederholt von schwer verständlicher Installation/Ladereihenfolge externer Libraries.

- Quelle: Max: Objekte deaktivieren, Verbindungen erhalten
- Quelle: Pure Data: externe Bibliotheken laden

**Für den Planer bauen:** klare Trennung Nachricht vs. kontinuierliches Signal, In-/Out-Ports, Monitor, Mute/Bypass/Kommentar, Paketkarte mit Version/Abhängigkeit, Testsignal und Aufnahme. Für den Anfang genügt ein kontrollierter Daten-/Audio-Simulator, kein vollwertiges DAW-System.

**Abnahmetest:** Ein Testsignal durch drei Patch-Knoten schicken; mittleren Knoten bypass/mute; Verbindung bleibt sichtbar; Monitor und Aufnahme belegen den Unterschied.

## 13. Gephi / yEd – große Graphen wirklich lesen

**Eigenständige Kernhandlung:** einen großen echten Bestand automatisch anordnen, filtern, clustern, selektieren und wieder zurück zur Quelle gehen – ohne dabei Beziehungen zu erfinden.

**Ecosystem-Beleg:** Gephi besitzt ein Pluginverzeichnis für Datenlabor, Gruppen/Partitionen und Generatoren; yEd führt eine eigene Feature-Request-Kategorie.

- Quelle: Gephi Plugins
- Quelle: yEd Feature Requests

**Echte Nutzersignale:** In großen Graphen werden Erweiterungen für Aggregation, Layout und Datenberechnung gebraucht. Das passt direkt zum Planer, solange Aggregation als Sichtschicht kenntlich bleibt und keine Originalknoten verschluckt.

- Quelle: Gephi: Graph-Visualisierung und Manipulation

**Für den Planer bauen:** Layout-Auswahl, Filter nach Typ/Status/Quelle/Zeit, Cluster als Sichtschicht, Knotenaggregation mit Aufklappen, Nachbarschaft/Shortest Path, Lesezeichen für Selektion und Tabellenansicht. Jede Layoutaktion darf nur Positionen/Ansicht ändern.

**Abnahmetest:** 100+ Testobjekte importieren, nach einer Herkunft filtern, Cluster anzeigen, aggregierten Cluster aufklappen und ein reales Objekt bis zur Datei öffnen.

## 14. Trello / Notion / Airtable – ein Bestand, verschiedene Arbeitssichten

**Eigenständige Kernhandlung:** dieselben Arbeitseinheiten als Tabelle, Board, Kalender oder Timeline sehen und Zustände/Verantwortung bearbeiten.

**Ecosystem-Beleg:** Notion-Verbindungen können Daten lesen/schreiben und Automationen anbinden; Trello-Power-Ups erweitern Karten/Boards, etwa Kalender, Custom Fields und Automationen.

- Quelle: Notion Connections
- Quelle: Notion API: Rechte und Verbindungen
- Quelle: Trello Power-Ups

**Echte Nutzersignale:** Nutzer schätzen Kalender, benutzerdefinierte Felder und Automation; zugleich wird gefordert, Feedback nicht nur zu sammeln, sondern zu taggen, zu priorisieren und sichtbar abzuarbeiten. Ein Board allein ist dafür zu flach.

- Quelle: Trello-Nutzer über Calendar/Butler/Custom Fields
- Quelle: Notion-Template: Feedback taggen und priorisieren

**Für den Planer bauen:** gespeicherte Ansichten auf denselben Objekten: Tabelle, Kanban, Kalender, Timeline. Felder haben Typ, Ursprung und Änderungsverlauf; Filter/Sortierung sind Ansicht, kein neues Objekt. Butler-artige Regeln werden als echte Automation mit Trigger und Run-Log modelliert.

**Abnahmetest:** Eine Aufgabe in Tabelle, Board und Timeline öffnen; Status in Board ändern; in allen Ansichten und im Ereignisprotokoll erscheint dieselbe Änderung.

## 15. VS Code – Dateien, Suche, Diff und Arbeitsfokus

**Eigenständige Kernhandlung:** echte Dateien schnell lesen, gezielt ändern, Unterschiede verstehen und ohne Ansichtswechsel zur passenden Stelle springen.

**Ecosystem-Beleg:** VS Code hat einen Marketplace; die offizielle GitHub-Erweiterung bringt Pull Requests und Issues in den Editor. Das zeigt: Kontextnahe Arbeit ist wertvoller als eine zweite Projektmanagement-Insel.

- Quelle: GitHub Pull Requests & Issues für VS Code
- Quelle: VS Code: Issues-Integration

**Echte Nutzersignale:** Nutzer wollen Pull Requests, Diffs und Kommentare im gleichen Arbeitsfluss. VS Code weist selbst darauf hin, dass Erweiterungsfehler/-wünsche über Marketplace/Issuewege behandelt werden – Erweiterungen sind also nicht automatisch vertrauenswürdig.

- Quelle: VS Code FAQ zu Extension-Support

**Für den Planer bauen:** Dateibaum, Tabs, Volltextsuche, Split-View, Editor für Markdown/JSON/Text, Diff vor Speichern, Dateiänderungs-/Versionsverlauf, Fehleranzeige, Link „als Objekt/Quelle verwenden“. Keine allgemeine Code-IDE versprechen, solange LSP/Build/Terminal nicht real integriert sind.

**Abnahmetest:** Datei suchen, in Split-View ändern, Diff ansehen, als neue Version speichern, alte Version vergleichen und Quelle im Graph öffnen.

## 16. GitKraken – Veränderung als verständlicher Zeit- und Branchgraph

**Eigenständige Kernhandlung:** sehen, was sich wann aus welchem Stand abgespalten, geändert, zusammengeführt oder in Konflikt geraten ist.

**Ecosystem-Beleg:** GitKraken positioniert sich ausdrücklich als visuelle Sicht auf Branches, Commits und Konflikte; seine Werkzeuge verbinden Repo- und Teamarbeit.

- Quelle: GitKraken Desktop
- Quelle: GitKraken GitHub-Organisation

**Echte Nutzersignale:** In der Community wird die Visualisierung besonders dann geschätzt, wenn sie schneller macht als CLI; zugleich bleibt Verständnis wichtig, damit die Ansicht kein Black Box-Button wird.

- Quelle: GitKraken-Nutzererfahrung

**Für den Planer bauen:** kein Fake-Git. Stattdessen ein **Änderungsgraph für Planerobjekte und Dateien**: Versionen, Arbeitsstände, Vergleich, Merge-Vorschlag, Konfliktkarte, Rückkehr zu Vorversion, Ursprung/Autor. Git-Repositorien können später als echte externe Quelle angeschlossen werden.

**Abnahmetest:** Zwei Arbeitsstände verändern dasselbe Feld; Konflikt wird sichtbar; ein bewusster Merge erzeugt neue Version plus Vergleich; ursprüngliche Version bleibt lesbar.

## 17. Figma – Komponenten, Varianten und kollaborative Designentscheidungen

**Eigenständige Kernhandlung:** UI-/Systembausteine als wiederverwendbare Komponenten bauen, Varianten vergleichen, kommentieren und durch klickbare Abläufe testen.

**Ecosystem-Beleg:** Figma unterscheidet Plugins, die die Datei manipulieren können, von Widgets, die alle gemeinsam sehen und bedienen. Das ist ein sehr passendes Vorbild für gemeinsame Planerobjekte versus Agentenwerkzeuge.

- Quelle: Figma Plugin API
- Quelle: Figma Widget API

**Echte Nutzersignale:** Im Figma-Forum werden konkrete Bedienungsdetails gefordert, z. B. dass ein frisch gezeichneter Connector auch sofort ausgewählt wird. Plugin-Ersteller berichten außerdem von langen/unklaren Review-Phasen. Daraus folgt: direkte Rückmeldung nach Handlung und sichtbarer Status sind Kernqualität.

- Quelle: Figma-Feature: Connector nach Zeichnen auswählen
- Quelle: Plugin-Review bleibt unklar

**Für den Planer bauen:** Komponentenbibliothek, Instanzen, Varianten, Properties, Ebenen, Kommentare am Element, einfache Prototyp-Übergänge, Designentscheidungsprotokoll und Übergabe an Dateibaum/Workflow. Das ersetzt nicht Figma, gibt dem Planer aber eine echte Design-System-Sprache.

**Abnahmetest:** Eine Komponente mit zwei Varianten anlegen, zwei Instanzen platzieren, Variante zentral ändern, Kommentar an einem Element setzen und Prototyp-Übergang testen.

---

## Forschungs- und Bauprotokoll, damit daraus keine Wunschzettelhalde wird

Für jede Replica wird vor einem großen Bauabschnitt diese Mini-Recherche wiederholt und als Spur gespeichert:

1. **Originalfluss:** Drei reale Kernhandlungen im Originalprogramm selbst durchführen/aufzeichnen.
2. **Ecosystem:** offizielle Erweiterungen, SDKs, Libraries oder Community-Packages prüfen; Lizenz, Datenzugriff und Wartungszustand notieren.
3. **Nutzerstimmen:** mindestens ein offizieller Issue-/Forumskanal plus unabhängige Nutzerstimmen durchsuchen. Wiederholungen und Gegenstimmen notieren.
4. **Lücke übersetzen:** nicht „Feature X kopieren“, sondern „welches Problem löst es für welchen Menschen?“ schreiben.
5. **Planergrenze:** festlegen, ob die Funktion echte Objekte/Kanten/Dateien schreibt oder nur Ansicht/Skizze ist.
6. **Kleiner Schnitt:** eine Kernhandlung bauen; nicht die ganze Software.
7. **Prüfung:** Playwright Desktop + 390px-Mobil, Reload/Persistenz, Fehlerweg und Rückweg testen.
8. **Feedbackschleife:** Sokrates/Redteam dreimal; daraus neues Feedback und AI-Spur erzeugen.

## Erste konkrete Priorisierung aus der Recherche

Diese Reihenfolge ist kein Dogma, sondern begründet durch Nutzen für den vorhandenen Planer:

1. **Obsidian/Heptabase + VS Code:** echte Dateien, Abschnitte, Rücklinks, Split-View, Diff. Das macht Material wirklich bearbeitbar.
2. **Trello/Notion/Airtable + GitKraken:** Zustände, Arbeitssichten, Versionen und Konflikte. Das verhindert den „alles bleibt dieselbe Metadatenkarte“-Fehler.
3. **Excalidraw/tldraw + Miro/Milanote + PureRef:** Denken, Referenzen, Kommentare und Gesamtplanung ohne falsche Kanten.
4. **n8n/Node-RED + Unreal + Houdini:** ausführbare/regelbasierte Systeme mit Verträgen, Laufspuren und Untergraphen.
5. **Gephi/yEd + TouchDesigner + Max/Pd + Geometry Nodes:** Sichtbarkeit großer Strukturen, Live-Signale und prozedurale Ergebnisse.
6. **Photoshop/Krita + Illustrator/Inkscape/Affinity + Figma:** echte Artefaktbearbeitung und Designsysteme.

Vor jedem nächsten Schritt gilt: Diese Akte lesen, aber nicht ihre Formulierungen als Wahrheit ausgeben. Den konkreten Quelllink öffnen, aktuelle Lage prüfen und den Fund als Spur an der betreffenden Replica speichern.
