# Bauauftrag: Mein Gesamtkonstrukt-Planer

## Lies das zuerst

Dies ist der verbindliche Einstieg für Menschen, LLMs und Agenten, die am Gesamtkonstrukt-Planer arbeiten. Er beschreibt keine Wunsch-UI und keine neue Theorieebene. Er beschreibt, was real gebaut, geprüft, gespeichert und nachvollziehbar weiterentwickelt werden muss.

Der Planer ist ein Arbeitsraum für echte Materialien und echte Entscheidungen: Dateien, Ideen, Konzepte, Dokumentationen, Systeme, Dienste, Wesen, Menschen, LLM-Ströme, Agenten, Werkzeuge, Workflows, Automationen, Prompts, Fragen, Feedbacks und deren Verbindungen.

Nach dem Öffnen der URL oder Einlesen einer einzelnen Datei muss ohne Gesprächsvorgeschichte klar sein — für Mensch, LLM und Agent:

1. Was ist gerade real vorhanden, und wo liegt es?
2. Was ist nur Idee, Vorschlag, Entwurf, Test, aktiv oder belegt?
3. Was kann ich hier konkret tun – am einzelnen Objekt und am Gesamtplan?
4. Welche Verbindung wurde bewusst gesetzt, welche stammt aus einer Datei, und welche ist nur ein Vorschlag?
5. Was wurde von wem verändert, mit welchem Grund und welchem Beleg?
6. Was ist der nächste offene Arbeitsschritt?

Der Einstieg muss in der URL-Oberfläche auffindbar sein, nicht nur in Chatverlauf oder implizitem Wissen. Der Button **Start hier** öffnet die VPS-Datei `00_Start/README.md`; von dort führen Bauauftrag, Arbeitskörper, reale Abläufe, gemeinsame Prüfungen, Replica-Recherche und Redteam-Status weiter.

Nicht behaupten, eine Funktion existiere, wenn sie nur dekorativ aussieht. Nicht einen Punkt als erledigt markieren, wenn er nicht im echten Browser geprüft wurde.

## Reale Orte und die eine Wahrheit

| Zweck | Reale Stelle |
|---|---|
| Öffentliche Planer-URL | `https://flextrawurst.de/Mein-Gesamtkonstrukt-planer/` |
| VPS-Arbeitswurzel | `/root/werkraum/Mein-Gesamtkonstrukt-planer/` |
| Kanonischer Planerzustand | `data/current.json` |
| Menschlich sichtbare Dateien und Ordner | `data/tree/` |
| AI-/Agenten-Spuren | `data/ai_spuren.json` und `data/tree/07_AI-Spuren/` |
| Ereignis- und Versionsspuren | `history/` und `data/events/`, soweit vorhanden |
| Browser-UI | `app/index.html` plus zugehörige JavaScript-Module |
| Server-API | `server/planner_api.py`, `server/workspace.js`, `server/streams.js`, `server/sync.js` |

Der Server ist die gemeinsame Wahrheit. Browserzustand ist nur Arbeitsoberfläche und Cache, niemals eine zweite dauerhafte Wahrheit. Eine Änderung gilt erst als gemeinsam gespeichert, wenn die API sie bestätigt und sie nach einem Browser-Neustart wieder sichtbar ist.

Dateien im Baum sind echte Dateien. Sie dürfen nicht durch bloße UI-Karten ersetzt werden. Löschen ist standardmäßig rückholbar (Papierkorb), und Verschieben/Umbenennen muss Quellenpfade und Ereignisse konsistent nachziehen.

## Was bereits real ist – und was nicht behauptet werden darf

Es gibt bereits einen servergestützten Planer mit kanonischem Zustand, Ordner-/Dateibaum, editierbaren Dateien, Arbeitsobjekten, Kanten, Feedbacksystem und einem ersten Spurenraum für Menschen und AI-Ströme. Diese Teile sind Ausgangsmaterial, nicht die Abnahme des Gesamtprojekts.

Noch nicht behaupten darf man insbesondere:

- dass alle 17 Replica-Dialekte bereits ihre eigene echte Arbeitskraft besitzen;
- dass Mobilbedienung unter realen Touch-Bedingungen vollständig gelöst ist;
- dass die Feedbackkette vollständig abgearbeitet ist;
- dass ein AI-Strom automatisch berechtigt, sicher oder konfliktfrei arbeiten kann;
- dass eine sichtbare Linie im Graphen automatisch eine belegte Beziehung ist;
- dass ein Textprompt bereits eine ausgeführte Automation ist.

## Wahrheitsvertrag für Objekte, Kanten, Dateien und Aussagen

### Objekte

Ein Objekt ist real, wenn es bewusst angelegt, aus einer Datei importiert oder als klar markierter Agentenvorschlag erzeugt wurde. Jedes Objekt braucht mindestens eine stabile ID, Titel, Art, Bearbeitungszustand, Herkunft und Zeitspur.

Status nicht zusammenschmelzen. Mindestens getrennt halten:

- Art: Datei, Quelle, Idee, Konzept, Dienst, System, Wesen, Mensch, LLM-Strom, Agent, Werkzeug, Workflow, Automation, Prompt, Entscheidung, Frage, Ereignis.
- Realitätsstatus: roh, Idee, Inspiration, Konzept, Vorschlag, geplant, gebaut, aktiv, live, verifiziert, blockiert, historisch, archiviert.
- Belegstatus: behauptet, aus Struktur abgeleitet, Quelle vorhanden, praktisch geprüft.
- Arbeitsstatus: offen, Entwurf, in Arbeit, zur Prüfung, angenommen, abgelehnt, erledigt.

### Kanten

Eine echte Kante braucht Herkunft und Verursacher. Zulässige Herkunft: `manual`, `declared`, `contains`, `imported`, `accepted_proposal`. Ähnlichkeit, gemeinsamer Ordner, Layoutnähe oder LLM-Vermutung sind höchstens Vorschläge. Sie dürfen keine echte Kante erzeugen.

Eine strukturelle Dateioperation darf Beziehungen erzeugen oder ändern, aber nur sichtbar: `contains` für Ordner/Datei bzw. Datei/Abschnitt; dazu Ereignis, alter und neuer Pfad sowie betroffene Objekt-IDs. Ein Verschieben ist nie still nur "Optik".

### Herkunft und Ereignisse

Jede relevante Änderung braucht: Zeitpunkt, handelnde Identität, Operation, Ausgangsobjekt/-version, Quelle/Eingabe, Ergebnis und bei Freigabe/Ablehnung den Grund. Originale bleiben lesbar. Aus einem LLM erzeugte Zusammenfassung ist abgeleitetes Material, niemals Ersatz des Originals.

## Menschlicher Einstieg: Was kann ich hier aktiv tun?

Die UI darf Menschen nicht beim Klick auf ein Objekt in dieselbe enge Metadatenmaske drücken. Jede Hauptansicht braucht eine eigene produktive Handlung:

- **Gesamtplan:** Zielbild, Bereiche, Zustände, Lücken, nächste Entscheidungen und Verbindungen entwerfen.
- **Werkraum / Dateibaum:** reale Dateien lesen, schreiben, ordnen, verschieben, löschen, wiederherstellen und als Arbeitsobjekte übernehmen.
- **Objektinspektor:** Bedeutung, Herkunft, Inhalt, Varianten, Beziehungen, Entscheidungen und Arbeitsstand eines konkreten Objekts bearbeiten.
- **Graph:** Zusammenhänge sehen, filtern, setzen, prüfen und Widersprüche/isolierte Inseln finden.
- **Workflow-/Automationsebene:** konkrete Schritte, Eingaben, Ausgaben, Bedingungen, Fehlerwege, Zuständigkeiten und Belege modellieren.
- **Spurenraum:** nachvollziehen, welche Person oder AI was gedacht, geprüft, vorgeschlagen, entschieden oder geändert hat.
- **Feedback:** konkrete Lücke, Beleg, Ziel, Akzeptanztest und Folgefrage festhalten.

Vor jeder Fachansicht steht ein kurzer Satz: „Was sehe ich? Was kann ich hier tun? Was wird gespeichert? Was wird ausgeführt?“ Eine neue Funktion ohne diese Antwort ist nicht benutzbar genug.

## Arbeitsvertrag für Menschen, LLMs und Agenten

Ein neuer AI-Strom oder Mensch arbeitet in dieser Reihenfolge:

1. Diesen Auftrag lesen und den realen Stand im Planer prüfen.
2. Den Gegenstand, die betroffenen Objekt-IDs, Dateien und erlaubten Schreibbereiche nennen.
3. Im Spurenraum einen Eintrag erzeugen: Autor, Art, Titel, gedachte/ausgeführte Operation, verknüpfte Objekte und Dateien.
4. Erst dann Änderungen vornehmen – bevorzugt als kleiner, prüfbarer Schnitt.
5. Jede Änderung im echten Browser prüfen; bei Datenänderungen zusätzlich Neustart/Reload prüfen.
6. Beleg, bekannte Grenze und offenen Folgeschritt im Spurenraum bzw. Feedback notieren.

Ein Agent darf keine fremden oder menschlichen Änderungen still überschreiben. Bei Konflikt wird der Konflikt sichtbar und als Vorschlag oder getrennter Stand erhalten. Externe Ausführung ist nie die stillschweigende Folge eines Prompts: Berechtigung, Trigger, Eingabe, erwartete Ausgabe, Stopbedingung und Beleg müssen sichtbar sein.

Der Spurenraum ist dabei ein reales, menschenlesbares Protokollformat – noch keine behauptete perfekte Multi-Agenten-Orchestrierung. Rechte, Authentifizierung, Konfliktauflösung und strukturierte Change-Sets müssen weiter ausgebaut und real geprüft werden.

## Der verbindliche Feedback-Arbeitsloop

Jedes selbst erzeugte offene Feedback wird einzeln vollständig bearbeitet. Nicht fünf Punkte parallel halb bauen.

1. Feedback lesen: Problem, betroffene Ansicht, Objekt, Datei, Nutzerhandlung und gewünschtes Ergebnis konkret machen.
2. Kleinen echten Fix bauen.
3. Fix direkt mit Playwright gegen die echte URL prüfen; bei Touch/Mobile zusätzlich eine echte kleine Viewport-Prüfung. Kein Klicktest nur gegen lokalen Code.
4. Sokratisch fragen: Welche natürliche Konsequenz folgt nach diesem Fix? Welche Zusammenhänge, Zustände, Regeln, Übergänge, Bedingungen und Weiterentwicklungen fehlen genau hier noch?
5. Diese Antwort dreimal redteamen: Gegen Bedienbarkeit, falsche Sicherheit, Datenwahrheit, Konflikte, mobile Nutzung, Rückbau/Fehlerweg und Zweck der betreffenden Replica. Nach jeder Runde die Antwort verbessern.
6. Die daraus entstehende konkrete Lücke als neues eigenes Feedback direkt auf der Seite speichern – mit Ziel und prüfbarem Akzeptanztest.
7. Erst dann das bearbeitete Feedback mit Beleg als erledigt markieren und zum nächsten gehen.

„Erledigt“ bedeutet hier: Funktion gebaut, echte Nutzerhandlung durchgeführt, sichtbares Ergebnis geprüft, Persistenz geprüft wenn gespeichert wird, Grenzen notiert und Folgefeedback angelegt. Kein Statuswechsel ohne diese Kette.

## Die 17 Replica-Dialekte müssen Zähne bekommen

Die folgenden Ansichten dürfen nicht dieselben Objekte nur anders einfärben. Jede braucht ihren eigenen Grund, eine eigene produktive Handlung und eine klare Rückbindung an dieselben realen Objekt-IDs, Dateien, Kanten, Ereignisse und Versionen.

| Replica | Wofür Menschen sie nutzen | Was im Planer konkret entstehen muss |
|---|---|---|
| Excalidraw / tldraw | schnell denken, skizzieren, rahmen, zeigen | Freies Zeichnen, Formen, Pfeile, Auswahl, Gruppen und Export; Skizzen können an reale Objekte angeheftet werden, ohne selbst falsche semantische Kanten zu werden. |
| PureRef | Referenzen nebeneinander sehen | Bilder, Screenshots, Dateien frei auf Referenzwand legen, zoomen, sortieren, mit Quelle/Notiz versehen und an Konzeptobjekte binden. |
| Miro / FigJam / Milanote | gemeinsam ordnen und aus Chaos Cluster machen | Sticky Notes, Frames, Bereiche, Kartenstapel, Gruppierung und Moderationsspuren; erst bewusste Übernahme erzeugt echte Objekte/Kanten. |
| Obsidian Canvas / Heptabase | aus Dokumenten Gedankenräume bauen | Lesbare Dokumentkarten, Textauszüge, Backlinks, Wissenspfade und Quellrücksprung bis zur Datei/Abschnitt. |
| Photoshop / Krita | Bildmaterial wirklich bearbeiten | Ebenen, Pinsel, Radierer, Auswahl, Masken, Deckkraft und History für ein Bildartefakt; Bearbeitung erzeugt Version/abgeleitetes Bild statt Originalverlust. |
| Illustrator / Inkscape / Affinity | präzise Vektoren bauen | Formen, Pfade, Anfasser, Füllung, Kontur, Ebenen und SVG-Export; Vektorarbeit als echtes Datei-/Artefaktobjekt. |
| n8n / Node-RED | Automationen verständlich modellieren und ausführen | Ports, Trigger, Datenfluss, Konfiguration, Testlauf, Run-Log, Fehlerpfad, Retry/Stop und explizite Aktivierung. Anleitung und Ausführung getrennt. |
| Unreal Engine Blueprints | Ereignislogik und Ablauf sichtbar machen | Event-Einstieg, Funktionsknoten, Daten-/Exec-Leitungen, Makros, Untergraphen und Laufzeitpfad pro Ereignis. |
| Blender Geometry Nodes | Regeln erzeugen statt jedes Detail manuell bauen | Geometrie-/Parametergraph, sichtbare Inputs/Outputs, Vorschau, wiederverwendbare Node-Gruppen und reproduzierbare Resultate. |
| Houdini | komplexe Prozesse in veränderbare Stufen zerlegen | Große verschachtelte Prozessnetze, Kontexte, Zwischenstände, Parameter, Caches und nachvollziehbare Stage-Übergänge. |
| TouchDesigner | lebende Signale und Medien steuern | Operatoren für Bild, Audio, Daten und Interaktion; Live-Vorschau, Signalwerte, Zeitbasis und kontrollierte Verbindungen. |
| Max/MSP / Pure Data | Klang, Daten und Logik frei patchen | Message- und Signal-Patches, Ein-/Ausgänge, Parameter, Monitor, Aufnahme und sichere Audio-/Datenwege. |
| Gephi / yEd | große Netze verstehen | Auto-Layout, Cluster, zentrale Knoten, Filter, Suche, Auswahlmengen und Layout ohne Erfindung neuer Beziehungen. |
| Trello / Notion / Airtable | denselben Bestand als Arbeitssystem sehen | Tabelle, Board, Kalender und Timeline auf denselben Feldern; Ansichten ändern Darstellung, nicht Datenmodell. |
| VS Code | Dateien effizient bearbeiten | Dateibaum, Tabs, Suche, Split-Ansicht, Diff, Markdown-/Code-Editor, Fehleranzeige und nachvollziehbare Speicherversion. |
| GitKraken | Veränderung und Verzweigung verstehen | Versionen, Branches, Unterschiede, Merge-/Konfliktansicht und Rückverweis auf konkrete Änderungen. |
| Figma | Entwürfe als wiederverwendbare Systeme bauen | Komponenten, Varianten, Eigenschaften, Ebenen, Kommentare, Prototyp-Verbindungen und Designentscheidungen mit Quelle. |

Für jedes neue Feedback ist zusätzlich zu beantworten: „Warum benutzen Menschen gerade diese Replica? Welche Handgriffe vermissen sie, wenn nur Karten und Metadaten da sind? Welche gemeinsamen Daten darf diese Ansicht lesen oder schreiben – und welche nicht?“

## Reihenfolge der offenen Bauarbeit

Die vorhandenen eigenen Feedbacks werden seriell nach dem obigen Loop abgearbeitet. Der aktuelle Vorrang ist:

1. globale mobile Bedienbarkeit und die spezifischen mobilen Fehler der Replica-Ansichten;
2. Feedbacksystem: Belege, freie Ziele/Selbstbezug und sichtbarer Bearbeitungsfortschritt;
3. Server-Wahrheit, Speichern, Konflikt- und Backup-Klarheit;
4. echte Strukturfolgen von Dateien, Ordnern, Objekten und Kanten;
5. Spurenraum als belastbare, verständliche Arbeitsgeschichte;
6. danach jede der 17 Replica-Funktionen einzeln – in der oben dokumentierten Reihenfolge und mit eigenem Zwecktest.

Wenn ein neueres Feedback eine Sicherheits-, Datenverlust- oder Bedienungsblockade offenlegt, wird es vorgezogen und die Begründung wird als Spur notiert. Sonst wird nicht umsortiert, nur weil eine neue Oberfläche attraktiver wäre.

## Playwright- und Redteam-Pflichten

Gegen die echte VPS-URL prüfen, nicht nur statisch lesen:

- Seite lädt ohne JavaScript-Fehler.
- Jeder sichtbare Button hat eine echte, verständliche Wirkung oder wird entfernt/deaktiviert erklärt.
- Hauptfluss der jeweiligen Ansicht: anlegen, bearbeiten, speichern, schließen, wieder öffnen.
- Daten bleiben nach Reload erhalten; bei Dateivorgängen stimmen Pfad, Inhalt und Objektverknüpfung.
- Mobile Prüfung: 390 px Breite, keine ungewollten Vollbild-Popups bei jedem Tap, keine verdeckten primären Aktionen, keine horizontale Falle.
- Tastatur-/Fokusprüfung bei Desktop-Dialogen; klare Namen statt symbolischer Rätselknöpfe.
- Fehlerweg: ungültige Eingabe, Netz-/API-Fehler, Konflikt, Abbruch, Wiederherstellung.
- Für jede Replica ihre eigene Kernhandlung testen, nicht nur Ansichtswechsel.

Redteam bedeutet nicht „viel Gemecker“. Es bedeutet konkrete Gegenfragen: Kann ein Mensch erkennen, was gerade passiert? Kann ein falscher Klick Daten verlieren? Kann eine AI mehr behaupten als belegt ist? Werden zwei Wahrheiten erzeugt? Was passiert auf Touch? Was ist der Rückweg?

## Nicht verhandelbare Grenzen

- Keine Fake-Buttons, Fake-Counts oder Erfolgsmeldungen.
- Keine parallelen LocalStorage- oder Browser-Schattenwahrheiten.
- Keine erfundenen Knoten/Kanten aus optischer Nähe oder KI-Interpretation.
- Keine stillen Hard-Deletes, Überschreibungen oder externen Ausführungen.
- Keine Erklärung, die eine Funktion ersetzt, die eigentlich gebaut werden muss.
- Kein „fertig“, solange Abnahmetest, Beleg oder Folgefrage fehlt.
- Keine neue Ansicht ohne eigene produktive Handlung und Rückbindung an reale Daten.

## Abnahmekriterien pro abgeschlossenem Feedback

Ein Punkt ist erst abgeschlossen, wenn im Spurenraum oder Feedback nachvollziehbar steht:

- Ausgangsproblem und betroffene Nutzerhandlung;
- geänderter realer Datei-/Systembereich;
- Playwright-Schritte und Ergebnis;
- Persistenz-/Reload-Ergebnis bei speichernden Funktionen;
- drei Redteam-/Sokrates-Runden in knapper, konkreter Form;
- das daraus erzeugte Folgefeedback;
- bekannte Grenze oder bewusste Nicht-Entscheidung.

## Startprompt für einen neuen ausführenden Agenten

> Lies `00_MEIN_GESAMTKONSTRUKT_PLANER_BAUAUFTRAG.md` vollständig. Prüfe zuerst den echten aktuellen Stand unter `https://flextrawurst.de/Mein-Gesamtkonstrukt-planer/` und den zugehörigen VPS-Arbeitsbaum. Wähle genau ein offenes eigenes Feedback. Baue nur dessen kleinsten vollständigen Fix. Prüfe die reale Nutzerhandlung mit Playwright, führe anschließend drei Sokrates-/Redteam-Runden aus, speichere die Folgefrage als neues Feedback und hinterlasse eine nachvollziehbare AI-Spur. Markiere erst dann den bearbeiteten Punkt als erledigt. Behaupte keine Replica-Funktion als vorhanden, wenn ihre Kernhandlung nicht existiert und geprüft wurde.

## Übergabeformat nach einem Arbeitsschritt

Am Ende eines einzelnen Arbeitsschritts nur knapp und belegbar dokumentieren:

- welcher Feedbackpunkt bearbeitet wurde;
- welche reale Nutzerhandlung jetzt möglich ist;
- welche Dateien/API-Daten geändert wurden;
- welcher Playwright-Test durchgeführt wurde;
- welche natürliche Folge als neues Feedback entstanden ist;
- was ausdrücklich noch offen bleibt.

Dieser Bauauftrag ist ein lebendes Steuerdokument. Änderungen daran sind selbst echte Änderungen: mit Spur, Grund und Version – nicht stilles Umschreiben.
