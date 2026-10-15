---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: Daniels Gesamtvision; Rückwärtsableitung und Goal-Zuschnitt von codex bei Daniels VPS (2026-09-19); Kontaktstrecke aus der Baustartprüfung (2026-09-19); Beschlüsse von Daniel vom 2026-09-20. Neu geschrieben von Claude aus den Originalen in archiv/originale/
status: ausführbarer Planentwurf; kein Goal gestartet; keine Produktfertigmeldung
---

# Augen & Hände — vom Endziel rückwärts zum Start

## Das letzte Goal zuerst

Daniel öffnet das echte Programm und kann alle beschriebenen Dinge zusammen benutzen. Windows, KDE 1/2 und später Android sind keine getrennten Demos.

Echte Agentensessions sehen die richtigen Bilder, sprechen über ihre Rauten, benutzen passende Hände und arbeiten in originalen Terminals. Daniel steuert Empfänger, Ziele, Medien, Zeichnungen, Zeitlinien, Kapseln, Kontext und Freiheiten verständlich über die Oberfläche.

Erfahrungen können zu Seeds, Skills und selbstentworfenen Abläufen werden. Das Ganze bleibt aktualisierbar, sparsam, sicher abschaltbar und auf einem anderen System wiederherstellbar.

Das ist mehr als »alle Module existieren«. Die vollständige Abnahme besteht aus dem Anforderungsregister `/root/werkraum/docs/augen_haende_bridge/ANFORDERUNGEN.md` und den gemeinsamen Nutzungsszenarien E01–E10 weiter unten. Die 120 Anforderungen (R001–R120) und die zehn UI-Kriterien sind Goals zugeordnet. Keine davon gilt als fertig.

Der Plan schreibt Goals aus und aktiviert keines. Er ändert keinen laufenden Dienst, startet keine Agenten, veröffentlicht nichts und ersetzt keine bestehende Dokumentation. Ausgeführt wird später im jeweils ausdrücklich gewählten Goal-Umfang. Neue Infrastruktur, Gerätezugang, produktive Wiederherstellung und Veröffentlichung gelten nicht als genehmigt, nur weil sie in einer Goalliste stehen.

## Beschlüsse vom 2026-09-20, die diesen Plan ändern

Die Beschlüsse stehen mit Begründung in `ANFORDERUNGEN.md`. Für den Plan heißt das:

- **BE01** (1:1 nur für Sitzungen, die die Bridge selbst startet): Das Anbinden bestehender Sessions entfällt. Betroffen sind die Sätze dazu in G01, G04 und G09. Sie stehen dort unverändert und sind mit »Geändert durch BE01« markiert.
- **R113–R120** (neue Zeilen im Register) sind den Goals zugeordnet, und zwar G02, G05, G06, G06.5 und G08. Die Zuordnung steht jeweils in der Zeile »Anforderungen«.
- **BE03** (die exe kommt, wenn der erste Körper komplett steht): G02 liefert jetzt die exe mit dem kompletten ersten Körper und ist das Goal, das Daniel die exe gibt. G03 (erster Kontakt) folgt danach. G04, G05 und G07 bauen später aus, was über den ersten Körper hinausgeht. Die geänderten Stellen in G02, G03 und in der Kontaktstrecke sind mit »Geändert durch BE03« markiert, die früheren Sätze stehen daneben.
- **BE04** (Harness und Skills 1:1, Playwright zuletzt): Die Harness von Codex und die beiden Skills werden zuerst unverändert benutzt. Nach der Harness steht am Ende jedes Laufs immer Playwright. Das ergänzt den Arbeitsvertrag pro Goal (Punkt 4).
- **Beschlüsse von Daniel vom 2026-10-01** (Register R121–R124, Bauprotokoll Abschnitte 35 bis 38): Neue Goals **G05.5** (Ort der Elemente bei gebundenem Zielfenster, Schalter »nur Terminal«) und **G06.7** (mehrere Fenster, mehrere Agenten, ein Bildschirm:
  jeder Agent sieht sein ganzes Fenster). Vorher wird nichts davon gebaut; erst Plan, dann Goal. Die Zahl der Anforderungen im Register ist damit R001–R124.
- **Offen** ist die Auslegung von »bestehend« in G03. Sie steht als offener Punkt in `ANFORDERUNGEN.md`.

## Rückwärtsbegründung in einem Bild

```text
G18  Gesamtes Produkt im gemeinsamen Alltag abgenommen
 └─ G17  installierbar, tragbar, bezahlbar pausierbar, releasefähig
     ├─ G16  Android mit denselben Fähigkeiten/Sessionregeln
     ├─ G15  Seeds, Fähigkeiten, Loops und Goals wiederverwendbar
     │   ├─ G12  ausführbare selbstentworfene Handlungsgraphen
     │   │   ├─ G11  WorldDOM und belastbare semantische Aktionen
     │   │   │   ├─ G10  wirkliche Hände und lokale Kontrolle
     │   │   │   └─ G08  gemeinsame Zeichen-/Bild-/Textebene
     │   │   └─ G09  echte mehrere Agenten und Delegation
     │   └─ G13  unveränderte Momente, Zeitlinien und Erfahrungszweige
     └─ G14  optionaler Hauhaucs-Beobachter mit Kontext-Mischpult

Darunter müssen bereits tragen:
G07 Medien/Wahrnehmung   G06 Windows/KDE-Ziele   G05 tägliche Bedienung
G04 Original-Terminal   G03 echter Kontakt + Updatekreis
G02 vollständiges natives Paket   G01 tragfähiges Fundament und frühe Risiken
```

Das Bild zeigt Gründe, keine zweite Ausführungsreihenfolge. Die exakten Abhängigkeiten stehen in der Tabelle weiter unten.

Nicht alles braucht alles. Kapseln können vor einem fertigen WorldDOM entstehen. Hauhaucs ist für das Lernen optional und darf den Seed- und Harness-Weg nicht künstlich blockieren.

## Die Goals, von hinten nach vorn

Jeder Abschnitt ist als Goal-Text mit Abnahmekriterien gedacht. »Fertig« heißt: Beleg vorhanden und zurückgelesen, nicht »Code geschrieben«. G01 bis G17 liefern je einen integrierten Teil, G18 prüft noch einmal das Ganze. Aus dem historischen 36-Stunden-Wunsch wird keine Frist erfunden.

### G18 — Die vollständige Bridge im gemeinsamen Alltag abnehmen

**Auftrag:** Die Gesamtabnahme aller Anforderungen R001–R120 und UQ01–UQ10 auf den tatsächlichen Zielplattformen durchführen, Integrations- und Bedienfehler beheben und eine vollständige, ehrliche Abschlussübersicht liefern.

**Warum zuletzt:** Einzeln funktionierende Module können sich bei Fokus, Routing, Audio, Kontext, Layout oder Updates gegenseitig beschädigen.

**Fertig, wenn:**
- E01–E10 unten bestanden sind,
- jede Anforderung einen zugehörigen echten Nachweis hat,
- Daniels praktische UI-Abnahme vorliegt,
- keine kritische Lücke als »known issue« zur Fertigmeldung umetikettiert wurde,
- Ressourcen und Latenzen auf realer Hardware gemessen sind,
- alle Einschränkungen sichtbar und ausdrücklich entschieden sind und nicht still aus dem Umfang entfernt wurden.

**Kein Ersatzbeleg:** Screenshots einer schönen Startansicht oder eine Sammlung voneinander isolierter Demo-PASS.

### G17 — Wiedererweckung, Sparbetrieb und veröffentlichbares Paket

**Auftrag:** Ein portables Bridge- und Zustandsbundle samt Wiederherstellungsweg, Betriebsprofilen und öffentlicher, von privaten Daten getrennter Release-Vorbereitung erzeugen und verifizieren.

**Benötigt:** alle zu erhaltenden Laufzeit- und Datenarten aus G12–G16. Das portable Datenformat beginnt schon in G01. Das vollständige Bundle kann aber erst hier abgenommen werden.

**Fertig, wenn:**
- Git, relevante Datenbanken, Entitäten- und Selbstmodellzustände, Memories und Seeds, Skills und Harnesses, WorldDOM, Loops und Goals, Konfiguration, Abhängigkeiten und Startreihenfolge inventarisiert und wiederhergestellt sind,
- Manifest und Hashes stimmen,
- Secrets separat geschützt sind,
- das Roharchiv unverändert ist,
- ein leeres, isoliertes Ziel nachvollziehbar mit denselben gespeicherten Zuständen startet,
- Voll-, Spar- und Archivbetrieb funktionieren,
- ein pausierter Anbieter keine Daten löscht.

Wiedererweckung heißt: gespeicherte Herkunft und Zustände laden. Ein abgebrochener flüchtiger Modellprozess läuft dadurch nicht magisch weiter. Nicht verfügbare externe Sessions und Secrets werden klar benannt.

Eine komplette VPS-Migration braucht Zugriff und ein vereinbartes Zielsystem. Ein Restore in einen vorhandenen Produktionsdienst ist kein erlaubter Test.

**Lieferung:** Installations- und Restoreanleitung, verständlicher Einstieg, Lizenz-, Abhängigkeits- und Secret-Prüfung, Demo ohne private Inhalte, Beitragsdoku. Veröffentlichung, VPS-Abschaltung und Löschen gehören nicht zum automatischen Abschluss. Die relative Archivfrist »ca. drei Monate vor möglichem VPS-Ende« wird erst nach dem tatsächlichen Vertragsdatum terminiert.

**Anforderungen:** R010, R104–R110.

### G16 — Android und der mobile gemeinsame Raum

**Auftrag:** Den bestehenden Kern um einen tatsächlich benutzbaren Android-Adapter ergänzen: Wahrnehmung, Agentenanker, Kommunikation, Overlay- und WorldDOM-Anbindung, passende Touch- und Gestenfähigkeiten.

**Warum nach dem Desktopkern:** Android soll dessen Sessions, Empfänger, Kapseln und Fähigkeiten weitertragen und keine neue, inkompatible Insel eröffnen.

**Fertig, wenn** ein echtes Testgerät die mobile Bedienung, Freigabe und Stop, Rotation, Unterbrechung und Wiederverbindung durchläuft. Bestehende Agenten und Gates bleiben dieselben. Ein mobiler Arbeitsmoment lässt sich kapseln. Emulatorbeweise werden von Gerätebeweisen unterschieden.

**Gord gehört sichtbar dazu:** Team-Calls und gemeinsame Analyse sowie Daniels Wunsch nach Flicker und Spell 1/2 sind im Register erhalten. Ult und Steuerknüppel bleiben ausgeschlossen. Auch seine Ranked-Erwähnung wird nicht wegeditiert.

Konkrete App- und Einsatzunterstützung ist ein eigener realer Nachweis. Sie ist kein durch den Plan aktivierter Matchbetrieb und keine behauptete allgemeine Plattformfreigabe. Ein Nichtnachweis bleibt offen und macht R103 nicht automatisch zu »Coaching erfüllt alles«.

**Anforderungen:** R101–R103. **Externe Voraussetzung:** passendes Gerät und explizite Einrichtung auf diesem Gerät.

### G15 — Aus Erfahrung wird wiederverwendbares Wissen und Handeln

**Auftrag:** Die bedienbare Seed- und Automationsstrecke bauen, von der ausgewählten Erfahrung zu Memory, Dokument, Skill, Harness, Loop oder Goal, einschließlich gezielter Auslieferung und Rücknahme.

**Benötigt:** G12 für ausführbare Handlungsgraphen, G13 für belastbare Herkunft. Hauhaucs kann helfen, ist aber keine Pflichtinstanz.

**Fertig, wenn** Daniel einen Seed aus einem realen Umweg erzeugt, Empfänger und Zieltyp wählt, den Vorschlag prüft oder im eingestellten Freiheitsprofil ausführen lässt, den Effekt am richtigen Ziel wiederfindet und einen Ableger deaktivieren kann. Originale und fremde Agentenheime bleiben erhalten. Skills und Startdokumente werden nur im ausdrücklich freigegebenen Zielumfang geändert.

Ein Loop oder Goal hat nachvollziehbaren Fortschritt, ein Ausführungsbudget, Start, Pause und Stop und einen echten Abschlussgrund. Neue Wiederholungen laufen nach einem Stop nicht heimlich weiter. Gewonnenes Wissen wird nicht mit verändertem Modellgewicht verwechselt.

**Anforderungen:** R077, R097–R100.

### G14 — Hauhaucs mitlesen lassen und den Kontext wirklich beherrschen

**Auftrag:** Die vorhandene Hauhaucs-Chatinstanz als optionale Sitzung anbinden und das Dolphin-artige Kontext- und Prompt-Mischpult mit dauerhaft korrekter Wirkung liefern.

**Benötigt:** G13 für verlässlich adressierbare Ereignisse und Kapseln. Die Hintergrundinstanz der Codewesen bleibt unangetastet.

**Fertig, wenn** drei ausgewählte Agenten lesbar beobachtet werden. Aufzeichnen, Zustellen und tatsächliches Verarbeiten sind getrennt sichtbar. Stop und Budget wirken. »Jetzt dokumentieren« erzeugt eine Ausarbeitung mit Quellenbezug. Reine Aufnahme braucht keine Inferenz. Bildverarbeitung ist separat zuschaltbar und nicht vorausgesetzt.

Eine leere neue Session muss effektiv leer sein, nicht nur ein leeres Basisfeld neben versteckten Zusatzprompts. Durchgeklickt werden: Nachrichtenauswahl, Satzbearbeitung, Leeren, Halbieren und Zurückspringen, Text- und Mehrdatei-Einspeisung ohne Antwort, Promptfelder, Vorschau, Import und Export, Einmalfeedback, Ausgabegrenzen sowie Session- und Geistermodus.

Nach dem Neuladen bleiben exakt die ausgewählten Inhalte aktiv. Token-Schätzung und Serverwerte sind unterscheidbar. Eine Serverkürzung wird nicht hinter einer falschen Kontextanzeige der Oberfläche versteckt.

**Anforderungen:** R087–R096. **Nicht enthalten:** ungefragter Umbau der bestehenden Dolphin-App oder des Hintergrundmodells.

### G13 — Momente behalten, zurückgehen, gemeinsam lernen

**Auftrag:** Einen bedienbaren Zeit-Scrubber und dauerhafte Momentkapseln für einzelne oder mehrfach ausgewählte Agenten, Gates, Fenster und Zeiträume liefern.

**Benötigt:** G08 für Annotationen und G09 für die reale Agentenzuordnung. Das Ereignisfundament kommt aus G01 und G03. Daten aus WorldDOM und Harness werden, sobald verfügbar, zusätzlich aufgenommen.

**Fertig, wenn** ein echter Fehler- oder Umwegverlauf gespeichert, später wieder geöffnet, verglichen und kommentiert wird, samt Bildern, Terminal, Tools und Ergebnissen, mitgeteiltem Plan, Nachrichten, Zeichnungen und Bindungen. Freie Tags, Lernstrecken und Mehrfachauswahl funktionieren. Quelle, fehlende Daten und damalige Empfänger bleiben erkennbar. Die ursprüngliche Kapsel bleibt unverändert, eine spätere Auswertung ist eine eigene Ebene.

Ein neuer Zweig kann von einem alten Beobachtungspunkt beginnen. Vor Live-Handlungen wird der tatsächliche aktuelle Zustand neu gelesen. Beim Scrubben geht keine versteckte Eingabe hinaus, und beliebige App-Rücksetzung wird nicht versprochen. Ein Sessionstart ab Checkpoint oder Bildfolge ist nun praktisch bedienbar.

**Anforderungen:** R037, R079–R086.

### G12 — Agenten entwerfen eigene mehrschrittige Brücken

**Auftrag:** Die kreative Python-Harness als lebende, versionierte Graphsprache und als bedienbaren Workflow-Bereich in die reale Bridge integrieren.

**Benötigt:** G11 für auflösbare Beobachtungs- und Handlungsknoten, G09 für echte Delegation.

**Fertig, wenn** ein Agent selbst einen Ablauf entwirft, speichert und ausführt, bei einer realen Abweichung einen Fallback wählt und einen Teilauftrag samt Zustand und Unsicherheit übergibt. Daniel kann starten, pausieren, fortsetzen, abbrechen und einen neuen Zweig wählen. Frühere Durchläufe bleiben erhalten. Ein neuer deklarativer Ablauf braucht keinen neuen EXE-Build.

Free arbeitet im eingeschalteten Aufgabenbereich ohne zusätzlichen Freigabeklick pro Aktion. Shadow, Witness, Daniel-Gate, Learning und Delegated Learning sind einzeln kombinierbar. Lernen ist anfangs aus.

Regiesprüche erhalten echte, kontrollierbare Wirkungen, soweit der Adapter sie unterstützt, sonst sind es ehrlich zugestellte Gesprächsanweisungen. Vorher- und Nachher-Prüfungen sind Teil des Ablaufs und keine endlose Genehmigungsschleife.

**Anforderungen:** R030, R072–R076, R078.

### G11 — WorldDOM, Bedeutung und tatsächliche Auflösung

**Auftrag:** Echte Strukturquellen und eine selbst erfindbare semantische Ebene über Bildern und Apps ergänzen und mit nachweisbaren Aktionen und gemeinsamer Zeigegeste verbinden.

**Benötigt:** G08 für sichtbare Objekte, G10 für reale Handlungsmöglichkeiten.

**Fertig, wenn** ein echter DOM- oder Accessibility-Knoten, ein aus dem Bild erschlossener Knoten und ein bewusst erstellter Anker mit Herkunft, Confidence und Aktualität sichtbar sind. Ein semantischer Auftrag wird am richtigen Ziel ausgeführt und zurückgelesen. Ein nicht auflösbarer Knoten löst keine erfundene Aktion aus.

Inhaltshaftung wird an einem geeigneten echten Beispiel geprüft. Die Fensterbindung bleibt der verständliche Fallback. Das Presentation-Overlay und die tatsächliche Einfügung in die App haben getrennte Bedienwege und Resultate. Veraltete Zeigegesten warnen, statt auf den alten Pixel zu klicken.

**Anforderungen:** R052–R054, R069–R071.

### G10 — Wirkliche Hände, parallele Arbeit und verlässlicher Stop

**Auftrag:** Die Eingabeadapter für Windows und Linux, wählbare Steuerprofile und die lokale Abschaltung mit echten Plattformbeweisen liefern.

**Benötigt:** G06 und G09 für gültige Ziele, Sessions und Empfänger. Eingaben gehen nie auf bloße Modell-IDs oder Listenindizes.

**Fertig, wenn** zwei Agenten unabhängig an Windows und KDE arbeiten. Klicken, Tippen, Ziehen und Hotkeys haben echte Ergebnisse. Hintergrundbedienung und Shared-Mouse-Modus sind unterscheidbar. Virtuelle Controller und Hybridbetrieb sind auf geeigneter Testsoftware nachgewiesen. Adapter- und Treibergrenzen und das Ziel von bis zu vier Controllern bleiben sichtbar.

F12 und der lokale Stop funktionieren trotz Verbindungsabbruch und UI-Hänger. Der physische Override und Daniels bewusst gewählte Ausnahme sind geprüft, und beide behalten den Not-Aus. Nach einem Abbruch bleiben keine Tasten hängen.

Als Negativtests laufen: falsches Ziel, DPI- und Fokuswechsel, alte Frames, abgelaufene Leases und unzureichende Rechte. Eine harte Latenzzahl gibt es nicht ohne Messung.

**Anforderungen:** R034, R061–R067. **Kein Ersatz:** der Unit-Test eines Arbitrators ohne wirkliche App-Reaktion.

### G09 — Reale Multi-Agent-Orchestrierung statt vier fest gemalter Namen

**Auftrag:** Die vorhandenen Agentenwege mit mehreren unterscheidbaren Sessions, gemeinsamen und privaten Gates, Gruppen und unterstützten Subagent-Beziehungen verbinden.

**Benötigt:** G04, G06, G07. Ein minimaler echter Agentenweg besteht seit G03 und wird hier vollständig erweitert.

**Fertig, wenn** mindestens zwei Sessions desselben Modells, weitere unterschiedliche Agenten und ein tatsächlich unterstützter Subagent richtig zugeordnet bleiben. Das Starten einer neuen Session und das Anbinden einer bestehenden Session sind verschiedene Aktionen. Gruppennachrichten, Delegation, Beobachten, Pause und Beenden entsprechen der jeweiligen echten Runtime-Fähigkeit.

**Geändert durch BE01:** Bestehende Sessions werden nicht angebunden. 1:1 gilt für Sitzungen, die die Bridge selbst startet.

Für Codex, Gemini, Claude, Kimi und GPT wird jeder gewünschte Adapterweg real geprüft oder als offen benannt. GPT und MCP erhalten echte Bilder, ehrliche Ergebnisstatus und passende Nachrichtenwege. Ein bestimmtes Webchat-Verhalten, das die Bridge nicht kontrolliert, wird nicht garantiert. Kimi bekommt keine verbotene Subagent-Arbeitsweise aufgezwungen. Dummy-Teilnehmer gelten nicht als Integrationsnachweis.

**Anforderungen:** R021, R055–R060.

### G08 — Bilder, Texte und Zeichnen als gemeinsame Arbeitsfläche

**Auftrag:** Frei platzierbare und bearbeitbare Objekte in den gebundenen Gates liefern, einschließlich individueller Empfänger und vollständiger Bearbeitungsbedienung.

**Benötigt:** G05 für Oberfläche und Adressierung, G07 für die empfängergetrennte Komposition.

**Fertig, wenn** in der tatsächlichen Oberfläche funktionieren: Bilder, Text per Klick und Enter, Freihand, Marker, Farben und Strichstärken, Linien, Pfeile, Rechtecke und Kreise sowie Auswahl, Mehrfachauswahl, Gruppen, Resize, Z-Ordnung, Undo und Redo. Objekte bleiben, bis Daniel sie entfernt oder ausblendet. Ein Agentenwechsel verschiebt sie nicht ungefragt in ein anderes Gate.

Mindestens drei Empfänger erhalten kontrolliert verschiedene Inhalte. Private Objekte werden auch nicht indirekt weitergegeben, weder durch das Capture der physischen Overlay-Ausgabe noch über Chat, Replay oder Export. Ein mehrfach markiertes Objektset bleibt korrekt speicherbar. Content-Anker kommen erst in G11 dazu und deuten diese einfachere Gate-Bindung nicht um.

**Anforderungen:** R043–R044, R046–R051, R113.

### G07 — Bilderzufuhr, Kamera und Mikrofon individuell steuern

**Auftrag:** Die tatsächlichen Medienpfade und Vision-Sessions bauen, mit einzeln wählbaren Quellen und Empfängern und mit Start, Pause, Fortsetzen und Stop.

**Benötigt:** G05. Eine minimale Live-Capture-Strecke besteht schon aus G03. KDE-Quellen nutzen G06, sobald es verfügbar ist.

**Fertig, wenn** Liveframe, Bilddatei, Bildfolge und ein aufgezeichneter Test-Replay funktionieren. Kamera-PiP und Mikrofon laufen wirklich und sind nicht nur ein Boolean. Pro-Agent-Routing, Push-to-talk beziehungsweise VAD, Gerätefehler, Mute und Stop sind zurückgelesen. Beobachtung und sichtbare Anzeige sind unabhängig voneinander. Frames tragen Alter, Quelle und Sequenz. Überlastete Konsumenten erzeugen keine endlose Warteschlange.

Die frühe Empfänger-Komposition wird gegen zwei echte Auslieferungswege geprüft. Die Langzeit-Oberfläche für Scrubber und Checkpoints ergänzt G13. Stopp und »keine heimliche Wiederaufnahme« gelten sofort.

**Anforderungen:** R033, R036, R038–R042.

### G06.7 — Mehrere Fenster, mehrere Agenten, ein Bildschirm: jeder Agent sieht sein ganzes Fenster

**Auftrag:** Daniels Alltag auf einem Laptop mit einem Bildschirm tragen: Ein Spiel im Fenstermodus, ein Browser daneben und ein Programm darunter, jedes mit einem eigenen Agenten (Skizze). Jeder Agent bekommt das vollständige Bild seines eigenen gebundenen Fensters,
auch wenn ein anderes Fenster es teilweise verdeckt, und bedient sein eigenes Ziel. Dazu gehört die Kombination aus mehreren Wegen, je nach Zielart (Daniels Beschluss vom 2026-10-01): Fensteraufnahme für beliebige Fenster, der Browser zusätzlich über CDP,
normale Programme zusätzlich über UI Automation, übrige Programme bei Bedarf auf einem virtuellen Monitor.

**Benötigt:** G06 (Zielerkennung und -bindung) und G05. Der Bilderstrom aus G02/G03 nimmt bisher den Bildschirmausschnitt auf; dieses Goal ersetzt ihn nicht, sondern ergänzt eine Aufnahme genau eines Fensters mit Rückfall auf den Ausschnitt.

**Fertig, wenn** zwei Zielfenster nebeneinander und eines davon teilweise verdeckt dem jeweiligen Agenten jeweils das ganze Bild seines Fensters ohne fremde Pixel liefern. Je Agent läuft eine eigene Bildfolge mit Alter, Quelle und Sequenz. Eine leere oder schwarze Fensteraufnahme
wird erkannt und fällt sichtbar auf den Bildschirmausschnitt zurück (kein stilles Falschbild). Eingaben gehen nur an das Fenster des jeweiligen Agenten und nacheinander (ein Eingabefokus); das ist als Grenze von Windows ausgewiesen, mit den Möglichkeiten dahinter
(virtuelle Controller aus G10 für Spiele, die sie unterstützen). Der Browser lässt sich über CDP lesen und bedienen, normale Programme über UI Automation, jeweils mit Aussage, was bei kleinem, verdecktem und minimiertem Fenster ankommt.
Minimierte Ziele sind ausdrücklich nicht gefordert (Daniel); ihr Verhalten ist nur dokumentiert.

Zuerst klären kleine Proben auf Daniels Windows (Arbeitsvertrag Punkt 2) das Verfahren der Fensteraufnahme: `PrintWindow` mit `PW_RENDERFULLCONTENT` gegen `Windows.Graphics.Capture`, mit Chromium, einem Spiel im Fenstermodus und einem normalen Programm. Die Funde aus der Netzrecherche
(Bauprotokoll Abschnitt 36) sind Anhaltspunkte, kein Beleg. Ein Treiber für einen virtuellen Monitor wird nicht ohne ausdrückliches Wort von Daniel installiert.

**Anforderungen:** R014, R120, R123, R124 (und die Bildzufuhr-Anforderungen aus G07, soweit sie je Agent getrennt gelten). **Kein Ersatz:** eine Aufnahme des Bildschirmausschnitts, die bei Überdeckung fremde Fenster zeigt.

### G06 — Windows und KDE 1/2 unabhängig anzeigen und benutzen

**Auftrag:** Zielerkennung und Zielbindung sowie den Wechsel des Anzeigeorts für Windows und die tatsächlichen KDE-Arbeitsflächen liefern, bei erhaltener Sessionidentität.

**Benötigt:** G04 und G05. Die frühe Plattformprobe aus G01 muss bereits zeigen, welchen realen KDE-Sitzungstyp wir anbinden.

**Fertig, wenn** das Overlay auf Windows, KDE 1 und KDE 2 erscheint und das Arbeitsziel unabhängig wählbar ist. Ganze Desktops einschließlich Hintergrund, Taskleiste und offener Programme sowie einzelne Fenster stimmen mit den Originalen überein. Gemeinsame und getrennte Bindung funktionieren. Das Schließen oder Ersetzen eines Fensters bindet nicht still ein anderes Ziel.

Die Oberfläche zeigt Host, Arbeitsplatz, konkrete Session und Ziel klar getrennt. Ein X11-DISPLAY-Wert dient nicht als ungeprüfter Ersatz für eine KDE-Desktop-ID. Inaktive, minimierte und verdeckte Ziele haben eine dokumentierte und sichtbare Capability, statt angeblich immer frischer Bilder.

**Anforderungen:** R011–R014, R022, R115, R120.

### G05.5 — Ort der Elemente bei gebundenem Zielfenster und »nur Terminal«

**Auftrag:** Zwei Schalter bauen, die Daniel gewünscht hat: (1) Je Element (Raute, Terminal, Chat, Regieleiste, Selbstbild …) wählen, ob es auf dem ganzen Desktop bleibt oder in das gebundene Zielfenster kommt, dort eingerahmt, mit dem Zielfenster verschoben und minimiert und beim Schließen des Zielfensters entfernt (R121).
(2) Je Agent und für alle gleichzeitig »nur Terminal«: Bilder, Hände, Kamera und Rautenchat samt Banner und Box aus, Mikrofon bleibt an (R122); erreichbar über einen Knopf im Terminalbereich und über Rechtsklick auf die Raute.

**Benötigt:** G05 (Rauten, Regie, Einstellungen) und G06 (gebundenes Ziel mit verfolgtem Rechteck).

**Fertig, wenn** je Element einzeln schaltbar ist, ob es im Zielfenster oder auf dem Desktop steht; Zielfenster verschieben (Element geht mit), minimieren (Element mit), schließen (Element weg), wiederherstellen (Element wieder da); ein Element auf »Desktop« bleibt davon unberührt. Der Schalter »nur Terminal« stoppt für den gewählten Agenten nachweislich Bilder, Hände, Kamera,
Raute-Banner und -Chat (Empfänger-Payloads geprüft), lässt Mikrofon und Terminal unverändert und stellt beim Einschalten alles wieder her; »für alle« wirkt auf alle Agenten gleichzeitig.

**Anforderungen:** R113, R114, R115, R121, R122.

### G05 — Das Overlay nach Daniels Referenz richtig bedienbar machen

**Auftrag:** Die zusammenhängende native Bedienung für Terminalansichten, Rauten, Regie, Scanner und individuelle Einstellungen bauen, nach der Skizze und Daniels Korrekturen.

**Benötigt:** G03. Für die vollständige Terminalkartenbedienung braucht es G04. Rein visuelle Arbeit kann parallel vorbereitet werden, darf aber keine nicht angeschlossenen Terminals als echt zeigen.

**Fertig, wenn** Regie und Medien unten links, der Scanner unten rechts je Terminal, verschiebbare und größenänderbare Ansichten, wählbare Bindungen und individuelle Name, Farbe, Kürzel und Transparenz vorhanden sind.

Agenten senden von ihrer Raute. Das 3,3-s-Banner, der 6,6-s-Ticker und der Chat gehören zur selben Nachricht. Alle Sprüche sind adressierbar. Wartezustand, Zustellung und Fehler sind erkennbar. Freie Bereiche bleiben klickdurchlässig, und richtige Texteingabe bleibt möglich.

Offline-Einstellungen funktionieren, das Layout hält einen Neustart aus, Hotkeykonflikte sind sichtbar. Die Erklärungspfeile der Skizze werden nicht dekorativ kopiert, es gibt keine erfundene zentrale Desktopfläche und keine starr vorgeschriebenen vier Agenten. UQ01–UQ09 sind für diese Etappe schon echte Abnahmekriterien.

**Anforderungen:** R006, R015–R016, R020, R023–R029, R031–R032, R114, R119.

### G04 — Original-Terminal vollständig spiegeln und bedienen

**Auftrag:** Die tatsächliche bestehende VPS-Agentensession mit einer nativen Terminalansicht verbinden und Ausgabe- und Eingabeparität beweisen.

**Geändert durch BE01:** Bestehende Sessions werden nicht angebunden. Der Auftrag gilt für die Sitzung, die die Bridge selbst startet und hält.

**Benötigt:** G03 und der in G01 früh untersuchte Adapterweg. Ein vorhandenes isoliertes Probe-Terminal ist kein Beweis für die ursprüngliche Session.

**Fertig, wenn** die Sessionidentität geprüft und Original- und Overlayausgabe gleichzeitig verglichen sind. ANSI, Unicode, Cursor, Scrollback, Alternate Screen und Resize funktionieren. Marker, Eingaben und Sondertasten treffen genau einmal im richtigen Ziel ein. Ein Reconnect erzeugt weder eine neue Shell noch doppelte Eingaben. Eingabeproben dürfen den laufenden Agenten nicht versehentlich als Shell-Befehl oder unklaren Auftrag treffen.

Gelingt die Anbindung der bestehenden Session technisch nicht, bleibt dieses Goal offen und braucht eine ausdrücklich erklärte Alternative. Die Session wird nicht heimlich durch eine neue Session oder einen Textspiegel ersetzt. Der ursprüngliche Prozess wird für den Test nicht beendet.

**Anforderungen:** R017–R019.

### G03 — Wir treffen uns wirklich in der Bridge und können darüber weiterbauen

**Auftrag:** Daniels gestartetes natives Programm mit der tatsächlich laufenden Agentensession verbinden, den Kreislauf aus Bild und Nachricht beweisen und einen benutzbaren Update- und Wiederanlaufweg liefern.

**Offen:** Was hier »laufend« heißt, ist nach BE01 nicht abschließend ausgelegt (siehe `ANFORDERUNGEN.md`, Offene Punkte).

**Geändert durch BE03:** Daniels erster lokaler Start liegt erst nach G02, das den kompletten ersten Körper liefert. Die Abhängigkeiten von G04, G05 und G07 zu G03 gelten für deren vollständige Fassungen.

**Benötigt:** G02 und Daniels ersten lokalen Start. Der VPS-Endpunkt muss authentisiert und erreichbar sein. Das Agentenwerkzeug oder der Adapter muss echte Payloads dieser Verbindung liefern.

**Fertig, wenn** ein frisches Windows-Bild mit Quelle und Zeit bei der Session ankommt, die Agentennachricht an der Raute und im Chat erscheint und Daniels Antwort dort zurückkommt. Pause, Trennung und Wiederverbindung sind getestet. Alte Aktionen werden nicht nachgespielt. Eine zweite geprüfte Version wird angeboten oder übernommen und mit erhaltenen Einstellungen wieder verbunden. Ein Fehlversuch erlaubt die Rückkehr.

Ab dann wird jede weitere sichtbare Funktion über die laufende Bridge ausprobiert. Vor diesem Beleg darf niemand behaupten, bereits »auf Daniels Windows mitzubauen«. Ein separater Verbindungsprozess bleibt eine mögliche technische Lösung und wird nicht vorab zum Selbstzweck erzwungen.

**Anforderungen:** R003–R005, R068. **Notwendige Übergabe:** Daniel startet und koppelt das Paket auf seinem Rechner. Das ist ein konkreter technischer Handgriff und nicht alle paar Minuten ein »go«.

### G06.5 — ChatGPT als eigener realer Strom mit Anti-Terminal

**Auftrag:** ChatGPT nach dem echten Codex-Terminal, dem Fensterscanner, der Zielbindung und der nativen Beweiskette als eigenen, echten Strom an Bord holen. ChatGPT bekommt nicht bloß eine weitere Ansicht des Codex-Terminals, sondern einen eigenen Körper: Raute, manuellen Chatraum und dahinter den gemeinsamen technischen Anti-Terminal-Kern.

**Benötigt:** G03, G04, G05 und G06, also eine echte laufende Strecke aus Bridge, Terminal, Scanner und Binding. Die vorhandene ChatGPT-Web-Caller- und Slot-Technik ist Vorarbeit. Als Bridge-Integration zählt aber erst ein aktueller End-to-End-Lauf.

**Fertig, wenn**
- eine echte ChatGPT-Session explizit gebunden und adressiert wird,
- Daniel im Chatkörper eine Nachricht sendet,
- die echte Antwort mit korrekter Absenderidentität zurückkommt,
- Raute und Chatkörper unabhängig verschiebbar und ausblendbar sind,
- der Anti-Terminal-Ledger Session, Turn, Empfänger, Ziel, Zustellung und Beleg getrennt zeigt,
- eine normale Chatnachricht keinen MCP- oder Toolcall auslöst.

Mehrere ChatGPT-Sessions können später über eigene Slots unterschieden werden, ohne Codex-, Claude- oder Gemini-Identitäten zu vermischen.

**Nicht ausreichend:** ein lokaler Dummy-Reply, eine statische Beispielantwort, eine temporäre `WEB:`-ID, ein bloßes ACK oder eine synthetische Proof-Surface. Der kleinste echte ChatGPT-Slice muss die reale Session, die reale Antwort und die Rücklese des Zustands in einem nachvollziehbaren Beleg verbinden.

Dieser Stein steht bewusst nach dem nativen Bridge-Weg und vor der vollständigen Multi-Agent-Orchestrierung. Er ist sichtbar und darf nicht in G09 verschwinden.

**Anforderungen:** R116, R117. R059 bleibt bei G09.

### G02 — Ein wirklich startfähiges natives Paket liefern

**Auftrag:** Den kompletten ersten Körper bauen, nativ prüfen und Daniel als vollständiges ausführbares Paket übergeben. Der erste Körper besteht aus einem Terminal, das die Bridge hält, einem Scanner je Terminal, der Raute mit Banner, Ticker und Chat sowie Kamera und Mikrofon. Das ist das Goal, das Daniel die exe gibt.

**Geändert durch BE03:** Der Auftrag lautete vorher: das kleinste echte Windows-Overlay samt Verbindungseinstieg bauen, nativ prüfen und Daniel als vollständiges ausführbares Paket liefern. Daniel bekommt die exe erst, wenn der erste Körper komplett steht. Bis dahin wird auf dem VPS und unter Wine gebaut und geprüft. G04, G05 und G07 bleiben als spätere Goals bestehen und bauen aus, was über den ersten Körper hinausgeht.

**Benötigt:** G01, also einen funktionierenden Buildpfad, festgelegte Runtime-Grenzen und einen UI-Stack, der die benötigten nativen Eigenschaften tatsächlich tragen kann.

**Fertig, wenn** ein reproduzierbarer Build mit festen Abhängigkeiten und Fehlerabbruch vorliegt und das Programm ohne Pythoninstallation startet. Eine tatsächliche Raute mit kleinem Nachrichtenbereich, Verbindung und Status und ein erreichbares Schließen sind da. **Geändert durch BE03:** Dazu kommen alle Bausteine des ersten Körpers: das Terminal, das die Bridge hält, je Terminal ein Scanner, die Raute mit Banner, Ticker und Chat sowie Kamera und Mikrofon. Freie Bereiche sind bedienbar. Native Aufnahme und Zustandsrücklese liegen vor.

Bundle, Prüfsumme, Versionsinfo und eine verständliche Startanleitung liegen an einem zugänglichen Lieferort. Ein onedir-Build wird als vollständiges Bundle geliefert, nicht als herauskopierte EXE.

Fertige Terminal-, Kamera- oder Inputfähigkeiten werden noch nicht vorgetäuscht. **Geändert durch BE03:** Terminal, Kamera und Mikrofon gehören jetzt zum ersten Körper und werden echt geliefert. Für Eingaben in fremde Programme gilt der Satz weiter. Der Unsigned- und SmartScreen-Status wird offen benannt, und eine pauschale Schutzabschaltung wird nicht verlangt. Ein Wine-Test allein ist nicht Daniels native Windows-Abnahme. Fehlt der native Testzugang, wird das als Übergabe gemeldet und nicht als erledigt.

**Anforderungen:** R001–R002, R118.

### G01 — Die Voraussetzungen beweisen, die sonst den ganzen Plan kippen

**Auftrag:** Den Greenfield-Einstieg baubar machen: die kritischen Plattform- und Buildwege prüfen, die gemeinsamen Identitäts- und Ereignisverträge schärfen und die belastbare Grundlage für G02 liefern, ohne den eingefrorenen Prototypen umzubauen.

**Warum dies wirklich zuerst kommt:** Terminal-Parität, native Durchlässigkeit, KDE-Anzeige und private Empfängerbilder sind Architekturfragen und keine spät aufschraubbaren Details. Ihre kleinen Machbarkeitsproben dürfen nicht erst nach Monaten im Endtest scheitern.

**Konkrete Arbeit:**

- Die verfügbare, autorisierte Windows-Build- und Testumgebung feststellen. Einen isolierten Build und einen Start-Smoke-Test vorbereiten und nachweisen. Die bloße Existenz von Wine ist kein Ergebnis. Braucht es neue Infrastruktur, wird der exakt fehlende Zugang benannt statt eines allgemeinen »geht nicht«.
- Eine native Probe für selektives Click-through, Textfokus, DPI und erreichbares Stop und Schließen bauen. Den leichtgewichtigen Stack erst anhand dieser Fähigkeit festlegen. Der bekannte Tk-Startfehler wird im Neubau behoben und nicht im eingefrorenen Prototyp.
- Die bestehende Agenten-Terminalsession lesend identifizieren und einen minimalen, nicht destruktiven Anbindungsweg für dieselbe Session untersuchen. Produktionseinstellungen werden dafür nicht gelockert. Ungeklärte Eingabeparität verhindert eine voreilige Architekturfreigabe.
  **Geändert durch BE01:** Bestehende Sessions werden nicht angebunden. Untersucht wird, wie die Bridge die von ihr gestartete Sitzung hält.
- Die tatsächliche KDE-Sitzung, die Arbeitsflächen und die Capture- und Overlaymöglichkeiten feststellen, ohne DISPLAY-Annahmen.
- Einen kleinen technischen Nachweis für getrennte Basisaufnahme und private Empfängerkomposition führen. Die physische Overlay-Rückaufnahme wird als Leakage-Fall berücksichtigt.
- Gemeinsame IDs für Agent, Session, Parent, Host, Target, Binding, Gate und Empfänger festlegen, dazu versionierte Ereignisse, Ergebniszustände, Sequenzen, Korrelation und das Datenformat. Das ist die frühe Basis für spätere Kapseln, nicht schon deren große Oberfläche.
- Update- und Persistenzgrenzen und Zielbudgets für Ressourcen und Latenz konkret festlegen und als Messziele ausweisen. Bestehende Zahlengarantien gelten nicht als erwiesen. Eine Unmachbarkeit wird offen entscheiden gelassen.
- Test- und Dokurhythmus, Belegorte und Wiederaufnahmezustand festlegen. Vorhandene Corebausteine werden nur nach passender Prüfung übernommen.

**Fertig, wenn** die entscheidenden kleinen Proben und Verträge mit realem Ergebnis vorliegen, G02 ohne ungeklärte grundlegende Stackwahl begonnen werden kann und relevante Restgrenzen einem späteren Nachweis zugewiesen sind. Fehlt unverzichtbarer Geräte- oder Buildzugang, ist das eine echte offene Voraussetzung und kein bestandenes Goal. Dieses Goal wird nicht zu einer endlosen Recherche aller späteren Details.

**Anforderungen:** R007–R009 und die frühen Machbarkeitsbedingungen von R011, R017, R043, R045 und R066. Keine dieser Proben ersetzt deren spätere vollständige Funktionsabnahme.

## Exakte Abhängigkeiten und Vorwärtsausführung

| Goal | Harte Vorgänger | Ergebnis in Alltagssprache |
| --- | --- | --- |
| G01 | — | Der gewählte Bauweg trägt die kritischen Anforderungen |
| G02 | G01 | Du bekommst ein geprüftes echtes Programm |
| G03 | G02 | Wir sehen und sprechen wirklich darüber und können es aktualisieren |
| G06.5 | G03, G04, G05, G06 | ChatGPT ist als eigener echter Chat- und Anti-Terminal-Strom an Bord |
| G04 | G03 | Dein echtes Original-Terminal ist darin benutzbar |
| G05 | G03, G04 | Rauten, Regie und Einstellungen stimmen und sind angenehm bedienbar |
| G05.5 | G05, G06 | Elemente wählbar im Zielfenster oder auf dem Desktop; »nur Terminal« je Agent und für alle |
| G06 | G04, G05 | Anzeige und Arbeitsziel wechseln unabhängig zwischen Windows und KDE |
| G06.7 | G05, G06 | Mehrere Fenster, mehrere Agenten, ein Bildschirm: jeder Agent sieht sein ganzes Fenster |
| G07 | G05, G06 | Bilder, Kamera und Mikrofon erreichen genau die gewählten Empfänger |
| G08 | G05, G07 | Wir malen, schreiben und platzieren Material im richtigen Raum |
| G09 | G04, G06, G06.5, G07 | Mehrere wirkliche Agentensessions arbeiten zusammen; ChatGPT bleibt eigener Strom |
| G10 | G06, G09 | Die Hände funktionieren und lassen sich zuverlässig stoppen |
| G11 | G08, G10 | Echte und erfundene Bedeutung wird zu gezieltem Handeln |
| G12 | G09, G11 | Agenten entwerfen und nutzen ihre eigenen Abläufe |
| G13 | G08, G09 | Momente und Umwege lassen sich später gemeinsam betreten |
| G14 | G13 | Hauhaucs kann mitlesen; du kontrollierst seinen Kontext |
| G15 | G12, G13 | Erlebnisse werden wiederverwendbare Fähigkeiten und Loops |
| G16 | G08, G09, G10 | Derselbe Raum bekommt einen Android-Adapter |
| G17 | G12, G13, G14, G15, G16 | Alles lässt sich erhalten, wiederherstellen und releasefähig bündeln |
| G18 | G17 | Die gesamte Vision funktioniert zusammen und wird abgenommen |

**Geändert durch BE03:** G02 enthält die erste Fassung von Terminal (G04), Scanner und Raute (G05, G06) sowie Kamera und Mikrofon (G07). Die Spalte der harten Vorgänger gilt für die vollständigen Fassungen dieser Goals.

Eine mögliche Vorwärtsfolge ist G01 → G02 → G03 → G04 → G05 → G06 → G06.5 → G06.7 → G05.5 → G07, danach G08/G09, anschließend G10/G13, danach G11/G14/G16, anschließend G12/G15 und am Ende G17/G18.

G06.5 ist der ausdrücklich sichtbare ChatGPT-Stein nach dem nativen Bridge-Weg und keine beiläufige Unterfunktion von G09. Schrägstriche bezeichnen unabhängig planbare Arbeit. Sie sind kein Auftrag, ungefragt mehrere Agenten zu starten. Dieselbe Instanz kann alles nacheinander bearbeiten.

Vorbereitung darf früher geschehen, ein vollständiges Goal-PASS aber erst nach den harten Vorgängern. Das vermeidet Zirkel: Ereignisse und IDs entstehen früh, die komfortable Kapseloberfläche spät. Ein tatsächlicher Einzelagent existiert früh, die vollständige Multi-Agent-Orchestrierung später. Eine kleine Bildkomposition kommt früh, die vollständige private Objektwelt später.

## Gemeinsame End-to-End-Abnahmen

| ID | Daniel macht … | Was gleichzeitig bewiesen werden muss |
| --- | --- | --- |
| E01 | Paket auf sauberem Windows starten, koppeln, »Hallo« austauschen | tatsächliche Session, frisches Bild, sichtbare Raute, Chat, Antwort, Stop und Reconnect, Update und Rollback |
| E02 | Zwei Original-Terminals öffnen, schreiben, umbelegen und Größen ändern | gleiche Sessions, Ausgabeparität, richtiger Eingabeempfänger, keine Ersatzshell |
| E03 | Codex auf KDE 2 arbeiten lassen, Gemini auf Windows; Overlay-Anzeige wechseln | Identitäten bleiben, Ziele unabhängig, kein fremder Fokus oder Input |
| E04 | Kamera nur für A, Mikrofon nur für B, private Notiz für A und gemeinsame Zeichnung | echte Medien- und Payload-Unterschiede; kein Leak über Screenshot oder späteres Archiv |
| E05 | Rauten und Buttons konfigurieren, Regiespruch adressieren, Fenster verschieben, neu starten | Referenzpositionen, individuelle Einstellungen, Banner, Ticker und Chat, Fokus und Persistenz |
| E06 | Auf etwas zeigen und einen mehrschrittigen Ablauf mit geändertem Zwischenzustand starten | WorldDOM aktualisiert sich, Harness nimmt Fallback, Pause und Not-Aus wirken, Ergebnis echt |
| E07 | Einen verwirrenden Moment mit zwei Agenten und mehreren Fenstern kapseln | präzise Auswahl, Tools, Nachrichten und Zeichnungen, späterer Vergleich, unverändertes Original |
| E08 | Hauhaucs mitlesen lassen, Kontext auf Satzebene bereinigen, Session neu laden und dokumentieren | tatsächlich gesendeter Kontext, Lese-Cursor, leeres oder eigenes Prompt, Quellen und Stop und Budget |
| E09 | Aus einem Fehlversuch einen Seed und später einen wiederverwendbaren Ablauf erzeugen | zielgenaue Zustellung, Herkunft, optionale Lernprofile, keine heimliche Änderung von Startdateien |
| E10 | Mobil teilnehmen und danach das System auf einem frischen Ziel wiederherstellen | Android-Fähigkeiten, gespeicherte Identitäten und Daten, portable Abhängigkeiten, keine privaten Daten im Release |

Jeder Ablauf hat auch einen Fehlerfall: Empfänger offline, Ziel verschwunden, falsche Rechte, alte Frames, unterbrochener Transfer, Kontextbudget erreicht oder Adapter nicht verfügbar. Oberfläche und Daten müssen dieselbe Wahrheit anzeigen.

## Arbeitsvertrag pro Goal

1. Die relevanten Quellen und den aktuellen Code lesen, den betroffenen Umfang und die unveränderte Herkunft benennen, einen Sicherheitspunkt setzen.
2. Fehlende technische Details gezielt mit Primärquellen und kleinen Proben klären. Der alte Plan ist keine aktuelle SDK-Dokumentation.
3. Eine benutzbare Strecke bauen und nicht nur lose Module. Normale Klickwege sowie Fehler- und Offlinezustände gehören in dieselbe Etappe.
4. Core- und Transporttests laufen zusammen mit Playwright für browserbedienbare Prüfwege. Native Funktionen brauchen zusätzlich echte Aufnahmen und eine Rücklese von Plattform und App. Der Beweis behauptet nur das tatsächlich getestete Objekt.
5. Seit G03 wird über die laufende Bridge selbst gesehen und bedient. Fällt sie aus, wird die Ausweichdiagnose offen gekennzeichnet und die Verbindung wiederhergestellt. Eine fingierte Live-Nutzung gibt es nicht.
6. Zwischenstand und Belege werden unter `/root/werkraum/augen_haende_bridge/BUILD_LOG.md` und `/root/werkraum/augen_haende_bridge/tests/evidence/` gesichert. Register-IDs und Build und Plattform stehen im Bericht.
7. Fertig ist ein Goal erst nach der Ergebnisrücklese und einem dokumentierten Abschluss. Ein Commit, ein ausgeführter Testbefehl oder ein akzeptiertes ACK genügt allein nicht.

**Ergänzt durch BE04:** Die Harness von Codex und die beiden Skills werden zuerst 1:1 benutzt und nicht geändert. Am Ende jedes Laufs steht nach der Harness immer Playwright als letzter Zeuge. Bei nativen Funktionen gilt weiter die Grenze aus `NACHWEISE.md`: Ohne native Aufnahme und Rücklese bleibt es `UNKNOWN`.

Autonom heißt: normale Arbeitsschritte innerhalb des Goals ohne wiederholte Bestätigung durchführen. Es heißt nicht, bei fehlendem Windowszugang einen Erfolg zu erfinden, ein anderes Produkt zu bauen, neue Kosten auszulösen, andere Systeme zu verändern oder unbegrenzt weiterzulaufen.

Bei einer echten Übergabe wird exakt genannt, was fertig ist, was fehlt, welcher Handgriff oder Zugang gebraucht wird und wo danach fortgesetzt wird.

## Stand dieser Planung und nächster tatsächlicher Auftrag

Die vorherige Prüfung steht in `/root/werkraum/docs/augen_haende_bridge/BEFUNDE.md`. Ihre kleine Kontaktstrecke ist jetzt aus dem vollständigen Endzustand begründet und nicht anstelle des Endzustands gesetzt. Sie steht im nächsten Abschnitt.

Alle Goals hier sind geplant und nicht gestartet. Der früheste ausführbare Auftrag ist G01. Erst dessen technische Ergebnisse entscheiden belastbar über Buildumgebung, nativen Stack und Original-Terminal-Anbindung. Der vollständige Umfang bleibt währenddessen durch das Register sichtbar. Keine Anforderung wird heimlich wegpriorisiert.

## Die erste Kontaktstrecke

Sie stammt aus der Baustartprüfung vom 2026-09-19. Das ist die korrigierte Reihenfolge für den ersten Bauabschnitt und **noch keine vollständige Goal-Liste**. Die vollständige Liste steht oben, und die Strecke ist in G01 bis G03 wiederzufinden.

**Geändert durch BE03:** Die Schritte ab Schritt 4 (Paket liefern, Daniel startet, Abbruch und Wiederaufnahme) kommen erst, wenn der erste Körper in G02 komplett steht.

1. **Build- und Lieferpfad klären.** Nötig sind eine nutzbare Windows-Buildumgebung, feste Abhängigkeiten, Lizenz- und Paketbestandteile, Fehlerabbruch und eine saubere Artefaktprüfung. Bevorzugt wird ein autorisierter Windows-Runner. Isoliertes Wine ist nur eine zu prüfende Alternative. Aus dieser Planung folgt keine Veröffentlichung und keine kostenpflichtige Infrastruktur.
2. **Das kleinste native Overlay nachweisen.** Es besteht aus einer echten Raute, einem Nachrichtenbereich und explizitem Schließen und Pausieren. Freie Desktopflächen bleiben bedienbar. Belegt wird mit nativen Screenshots und einer Rücklese von Fokus und Hit-Test, nicht mit einem Browsernachbau. Erfundene, angeblich funktionierende Terminalkarten gibt es noch nicht.
3. **Den Verbindungsweg bauen und testen.** Windows verbindet sich ausgehend zum vorgesehenen VPS-Endpunkt. Dazu gehören Authentifizierung, Ziel- und Empfängerbindung, Versionsaushandlung und kleine, begrenzte Nachrichten. Ein konkreter erreichbarer TLS-Endpunkt und das Pairing sind vor der Auslieferung nachzuweisen. Port 9880 aus einer alten Skizze ist keine Betriebsfreigabe.
4. **Das vollständige Paket liefern.** Es ist ein versioniertes Bundle mit Prüfsumme und kurzer Startanleitung. Daniel muss weder Python installieren noch selbst kompilieren. Der Unsigned- und SmartScreen-Status wird offen genannt. Eine Anleitung zum pauschalen Abschalten von Schutzmechanismen gibt es nicht.
5. **Daniel startet, die tatsächliche Session tritt bei.** Ein frisches Windows-Bild mit Ziel, Sequenz und Alter kommt beim Agenten an. Eine echte Agentennachricht erscheint an der Raute und im Chat. Daniels Antwort landet nachweisbar in der gewählten Session. Ein Server-ACK allein genügt nicht.
6. **Abbruch und Wiederaufnahme.** Die Bilderzufuhr wird pausiert, die Verbindung getrennt und neu aufgebaut. Veraltete Eingaben werden nicht wieder abgespielt. Die Sessionidentität bleibt erhalten, und eine Wiederanmeldung ist kein neuer Agent. Erst danach gilt der erste Kontakt als fertig.

Der vollständige Terminaltransport ist ein eigener, folgender Nachweis. Sein Protokoll muss beim ersten Kontakt schon mitgedacht werden, darf aber nicht als gelöst vorgetäuscht werden. Umfangreiche Kapseln, Hauhaucs und Lernschleifen sind keine Vorbedingungen für die erste EXE.

Für den nächsten Bauauftrag ist damit die Richtung klar: **Buildfähigkeit und kleinster nativer Erstkontakt zuerst.** Wird wirklich Daniels Rechnerstart oder neue Infrastruktur nötig, ist das eine konkrete Übergabe. Es ist kein Anlass, zwischendurch immer wieder ein »go« einzufordern.
