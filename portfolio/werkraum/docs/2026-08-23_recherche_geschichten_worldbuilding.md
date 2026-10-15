# Recherche: Story-/Worldbuilding-Werkzeuge — Vorbilder für den Objekttyp "Geschichten"

Auftrag: Vorbilder für den Objekttyp "Geschichten" im Gesamtkonstrukt-Planer sammeln,
mit Blick auf Daniels eigenes Projekt "flextrawurst-the-game" — ein Spiel/Erzählrahmen,
der laut Grundgesetz 1 (CLAUDE.md) auf echten flextrawurst-Daten beruht ("Spiel ist keine
Fiktion"). Reine Websuche, kein Code-Zugriff. Raw, nicht verdichtet.

## Twine — offen, textbasiert, visuelle Passage-Karte

Version 2.12.0 (10. April 2026). Kernprinzip: jede Passage ist eine Blase, jeder Link ein
Pfeil — die ganze verzweigte Struktur wird als Knoten/Kanten-Netz sichtbar, bevor man
überhaupt Code schreibt.

Mehrere austauschbare "Story-Formate" (Harlowe, SugarCube, Chapbook, Snowman) fungieren
praktisch als unterschiedliche Mini-Engines mit eigener Scripting-Handschrift innerhalb
desselben Werkzeugs.

Größte Stärke laut Quellen: kein Programmieraufwand nötig, um eine erste verzweigte
Geschichte lauffähig zu bekommen — Prosa schreiben, Links setzen, direkt als HTML
exportieren.

Größte Schwäche: Zustandsverwaltung (was hat der Spieler schon getan/gewusst) wird bei
wachsender Story schnell unübersichtlich. Professionelle interaktive-Fiction-Autoren
wandern für kommerzielle Projekte meist zu Ink weiter, weil Twine an dieser Stelle an
seine Grenzen kommt.

Quellen: [Twine offiziell](https://twinery.org/), [Best Interactive Story Software 2026 — gitnux](https://gitnux.org/best/interactive-story-software/), [What Do Professional Interactive Fiction Writers Use in 2026 — Scribeist](https://scribeist.com/blog/what-do-professional-interactive-fiction-writers-use-2026/)

## articy:draft X — der Enterprise-Standard für komplette Content-Datenbanken

Über 15 Jahre aktive Entwicklung, eingesetzt u.a. bei Hogwarts Legacy und Disco Elysium.
Geht bewusst über reine Dialogbäume hinaus: eine vollständige Content-Datenbank für
Orte, Items, Charaktere und Quests, mit Lokalisierung, flexiblen Exporten, eigener API
und fertigen Unity-/Unreal-Integrationen.

4.1-Update brachte u.a. seen/unseen-Keywords, read-only Template-Properties, .NET-8-
Migration. Neuere KI-Erweiterungen (Dialoggenerierung, Bark-Erstellung, Vorschaubilder,
Sprachsynthese) sind Add-on-Module, keine tief integrierten Kernfeatures — ein Hinweis
auf Integrationsgrenzen an genau dieser Stelle.

Preislich: ab 6,99 EUR/Monat Einzelplatz, 56 EUR/Monat für 2 Sitze; kostenlose Stufe bei
700 Objekten pro Projekt gedeckelt. War lange Windows-exklusiv, Mac-Version erst seit
April 2025.

Quellen: [articy:draft Feature-Liste](https://www.articy.com/en/articydraft/feature-list/), [Game Narrative Design Software — Update-Meldung](https://curatedtechnologynews.substack.com/p/002dcbe89bddf6764da2916c7459a5dc), [Top 10 tools for narrative design — Arcweave-Blog](https://blog.arcweave.com/top-10-tools-for-narrative-design)

## Arcweave — browserbasiert, Team-Echtzeit-Zusammenarbeit

Cloud-natives, professionelles Story-/Narrative-Design-Tool mit Echtzeit-Mehrpersonen-
Bearbeitung, direkt im Browser, gute Integration in gängige Game-Engines.

Preise: kostenlose Stufe (3 Projekte), Pro 15 USD/Mitglied/Monat, Team 25 USD/Mitglied/
Monat. Gewinnt gegenüber articy/Twine dort, wo verteilte Teams wirklich gleichzeitig am
selben Story-Graphen arbeiten müssen.

Nachteile laut Quellen: kostenpflichtig, für kleine Projekte eventuell überdimensioniert,
braucht durchgehende Internetverbindung, eingeschränkte Offline-Fähigkeit, gewisse
Lernkurve.

Quellen: [Twine vs Arcweave — SaaSHub](https://www.saashub.com/compare-twine-vs-arcweave), [Top 10 tools for narrative design](https://blog.arcweave.com/top-10-tools-for-narrative-design)

## Miro/FigJam als Story-Maps

Beide sind Whiteboard-Werkzeuge, keine dedizierten Story-Tools — werden aber verbreitet
für Story-Mapping/Quest-Flows zweckentfremdet. Miro: volles Whiteboard für alles von
Sprint-Retros bis Enterprise-Strategie. FigJam: leichtgewichtige, eng an Figma gekoppelte
Variante.

Zentrale strukturelle Schwäche für Story-Zwecke: FigJam hat "kein Map-Modell darunter" —
ohne Miros Facilitation-Tiefe oder Integrationsbreite. Sprich: beide sind freie Leinwände,
kein datenmodelliertes Story-Objekt darunter, das sich z.B. automatisch mit einem Quest-
Status oder einer Figuren-Datenbank verknüpft.

Weitere Nutzerbeschwerden zu Miro: unerwünschte Sitz-Zuweisungen, View-Links die
kostenpflichtige Lizenzen auslösen, verschleierte Rückerstattungswege — reine Abrechnungs-
probleme, kein inhaltliches Limit. Bei großen, inhaltsreichen Boards zusätzlich
Performance-Einbußen und Unübersichtlichkeit.

Quellen: [FigJam vs Miro 2026](https://startup-house.com/blog/figjam-vs-miro), [Miro Review 2026 — 15 echte Nutzerbewertungen](https://hackceleration.com/labs/review/miro), [FigJam Board-Navigation Feature-Wunsch — Figma-Forum](https://forum.figma.com/suggest-a-feature-11/figjam-enhanced-board-navigation-with-draggable-map-15778)

## Notion/Trello — Fortschritts-/Quest-Tracking statt Story-Struktur

Trello: klassisches Kanban (To-Do/Doing/Done), in Indie-Teams oft mit eigenen Spalten wie
"Art Pipeline", "Audio", "Narrative" erweitert. Leichtgewichtig, einfach, verbreitet bei
Hobby-Projekten und kleinen Teams.

Notion: kein Projektmanagement-Tool im engeren Sinn, sondern eine leere Canvas-
Workspace — eignet sich gerade deshalb für narrativlastige Projekte: Lore-Wikis,
Charakterwerte, Dialogbäume, verknüpft mit eigenen Task-Datenbanken.

Praxis bei Indie-Teams (Beispiel Ooblets-Entwickler zitiert): Kombination beider Tools —
Trello für den reinen Kanban-Fortschritt, Notion für Design-Dokumente, Lore und Notizen.
Keins der beiden deckt beides gleichzeitig gut ab.

Quellen: [Trello für Game-Projektmanagement — Guide](https://multigamedev.blogspot.com/2025/06/game-project-management-trello-indie-guide.html), [Jira vs Trello für Indie-Fortschritt — Wayline](https://www.wayline.io/blog/jira-trello-indie-game-progress)

## Obsidian-Vault-basierte Worldbuilding-Systeme

Mehrere fertige "Worldbuilding-Vaults" für Obsidian existieren als Marktplatz-Produkte,
nicht nur als DIY-Setup: eigene Dataview-Tabellen zeigen Charaktere, Fraktionen, Orte und
Zeitlinien automatisch an, jeder Charakter bekommt ein strukturiertes Profil (Stats,
Zugehörigkeiten, Beziehungen, Auftritte, Biografie).

Weitere genannte dedizierte Tools: ChronoGrapher (freies Notiz-Wiki + interaktive Karten +
Tile-Map-Editor + ausführliches Zeit-/Geschichtstracking), Fantasia Archive (offline,
Vorlagen für Charaktere/Orte/Ereignisse/Religionen/Währungen/Magie/Spezies/Sprachen,
komplexes Tagging, dokumentübergreifende Verlinkung, projektweite Suche), LoreBuilder
(CMS speziell für Autoren/Spielleiter — Charaktere, Orte, Zeitlinien-Ereignisse, eigene
Beziehungs- und Vorlagen-Definitionen).

Gemeinsamer Nenner dieser Kategorie: Verlinkung (jedes Objekt zeigt auf andere) plus
strukturierte Vorlagen pro Objekttyp — sehr nah an dem, was Obsidian Canvas selbst schon
in der vorherigen Recherchedatei als "Konzepte als verknüpfter Wissensgraph" beschrieben
wurde, nur hier spezifisch auf Charakter-/Orts-/Ereignis-Objekte zugeschnitten statt
generisch.

Zur konkreten Reddit-Diskussion über Lücken in dieser Kategorie lieferte die Suche keine
verwertbaren Treffer — offene Frage, nicht recherchiert, [status: offen].

Quellen: [Worldbuilding Starter Vault](https://prattdesign.itch.io/worldbuilding-starter-vault), [Worldbuilding Websites and Apps — AlternativeTo](https://alternativeto.net/lists/26985/worldbuilding-websites), [ChronoGrapher — AlternativeTo](https://alternativeto.net/software/chronographer)

## Einordnung für den Gesamtkonstrukt-Planer

Kein einzelnes gefundenes Tool deckt alle drei Ebenen ab, die "Geschichten" im
Gesamtkonstrukt-Planer vermutlich braucht: (1) verzweigte Struktur/Passagen wie Twine,
(2) vollständige Entitäts-Datenbank (Charaktere/Orte/Items/Quests) wie articy:draft,
(3) Fortschritts-/Status-Tracking wie Trello-Kanban. Jedes bestehende Werkzeug deckt
typischerweise nur ein bis zwei davon ab, der Rest wird über Tool-Kombination (z.B.
Notion+Trello) beziehungsweise durch Zweckentfremdung generischer Whiteboards (Miro/
FigJam) notdürftig ergänzt.

Für flextrawurst-the-game speziell relevant: da das Spielgefühl laut Grundgesetz 1 aus
echten flextrawurst-Daten (Events, Splitter, Wesen-Handlungen) entstehen soll, nicht aus
freier Erfindung, wäre die articy:draft-Idee einer durchgängigen Entitäts-Datenbank
(Charaktere/Orte/Ereignisse als eigene, verknüpfbare Objekte mit Zuständen) strukturell
näher am Bedarf als ein reines Text-Passagen-Tool wie Twine — vorausgesetzt, die
Datenquelle bleibt echte flextrawurst-DB statt frei erfundener Einträge.
