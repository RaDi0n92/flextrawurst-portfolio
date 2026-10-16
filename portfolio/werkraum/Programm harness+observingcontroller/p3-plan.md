Dann ist `flextrawurst.de/os` nicht mehr nur ein Dashboard. Es wird ein vollständiges **Agent Operating System und Agent Studio**:

- Agenten beobachten
- Agenten steuern
- Agenten miteinander diskutieren lassen
- Profile und Rollen erstellen
- eigene Programmier-Harnesses bauen
- Regeln und Funktionen visuell ändern
- laufende Prozesse pausieren oder beenden
- Lernschleifen kontrollieren
- Versionen speichern
- Änderungen testen
- Systeme aktivieren, deaktivieren und zurückrollen

Der wichtigste Architekturgrundsatz lautet:

> Alles darf bearbeitbar sein – aber nichts darf unversioniert, unkontrolliert oder unwiederbringlich verändert werden.

## Die vier Ebenen deines Systems

### Profil

Ein Profil beschreibt, für welche Art von Tätigkeit ein Agent eingesetzt wird.

Beispiele:

- Programmieren
- Debugging
- Code-Review
- Architekturplanung
- Recherche
- Betrieb und Monitoring
- Sicherheitsprüfung
- Dokumentation
- Datenbankpflege
- kreative Weltentwicklung
- Selbstreflexion
- Koordination anderer Agenten

Ein Profil enthält:

- Name und Zweck
- Rolle des Agenten
- bevorzugte Modelle
- erlaubte Projekte
- erlaubte Tools
- erlaubte Verzeichnisse
- zugehörige Erinnerungen
- Reminding-RAG-Regeln
- Selbstlernmodus
- Kommunikationspartner
- erlaubte Eingriffe
- Budget- und Zeitlimits
- Erfolgskriterien
- Driftregeln
- Sicherheitsstufe

Ein Profil ist also die Identität und der Rahmen.

### Harness

Ein Harness beschreibt, wie die Tätigkeit ausgeführt wird.

Ein Programmier-Harness könnte zum Beispiel aus diesen Stationen bestehen:

- Auftrag verstehen
- Anforderungen klären
- Bestand analysieren
- Plan erstellen
- Änderung vorbereiten
- Umsetzung durchführen
- Tests ausführen
- Ergebnis prüfen
- zweiter Agent reviewt
- Fehler beheben
- Ergebnis dokumentieren
- Übergabe oder Abschluss

Jede Station kann konfigurierbar sein:

- welches Modell verwendet wird
- welche Tools verfügbar sind
- welche Erinnerungen abgerufen werden
- wann ein Checkpoint entsteht
- wie oft ein Schritt wiederholt werden darf
- wann ein anderer Agent gefragt wird
- wann ein Mensch freigeben muss
- wann der Lauf abgebrochen wird

Der Harness ist der Ablaufplan.

### Sitzung

Eine Sitzung ist eine konkrete laufende Instanz eines Profils und eines Harnesses.

Sie hat:

- eigene Sitzungs-ID
- aktuellen LangGraph-Zustand
- eigene Checkpoints
- eigenes Arbeitsverzeichnis
- aktuellen Branch
- aktuelle Erinnerungen
- Tool-Historie
- Änderungen
- Fehler
- Driftstatus
- Kommunikationskanäle
- aktuelle Harness-Version

Eine laufende Sitzung muss immer wissen, mit welcher Profil- und Harness-Version sie gestartet wurde.

### Raum oder Arbeitsgruppe

Mehrere Agenten können in einem gemeinsamen Raum arbeiten.

Ein Raum kann zum Beispiel heißen:

- Authentifizierungs-Reparatur
- Release-Vorbereitung
- Architekturentscheidung
- Datenbankmigration
- Welt-Engine
- Harness-Entwicklung
- Sicherheitsreview

In diesem Raum sehen die Agenten:

- die gemeinsame Aufgabe
- die anderen Beteiligten
- deren Status
- relevante Ergebnisse
- offene Fragen
- Entscheidungen
- Dateien oder Aufgaben, die bereits vergeben sind

Sie sehen aber nicht automatisch alle privaten Erinnerungen der anderen Agenten.

## Profile können mehrere Harnesses enthalten

Ein Profil sollte nicht auf genau einen Ablauf begrenzt sein.

Beispielprofil „Senior Backend Engineer“:

- Harness „neue Funktion“
- Harness „Bug untersuchen“
- Harness „Datenbankmigration“
- Harness „Performanceproblem“
- Harness „Code-Review“
- Harness „Release vorbereiten“

Jeder Harness kann gespeichert, dupliziert, deaktiviert, verändert und separat aktiviert werden.

So ist ein Profil nicht bloß ein Prompt, sondern eine komplette Arbeitsumgebung.

## Der Lebenszyklus eines Profils oder Harnesses

Jede Änderung sollte durch einen sichtbaren Lebenszyklus laufen:

1. Entwurf
2. Prüfung
3. Simulation
4. Testlauf
5. Aktivierung
6. Nutzung
7. Überwachung
8. Pause oder Überarbeitung
9. neue Version
10. Rückkehr zu einer älteren Version
11. Deaktivierung
12. Archivierung

Ein aktiver Harness sollte nicht unbemerkt unter den Füßen des gerade laufenden Agenten verändert werden.

Wenn ein Agent seinen eigenen Harness verbessern möchte, sollte er normalerweise:

- eine neue Entwurfsversion erzeugen
- seine Änderung begründen
- die erwartete Verbesserung beschreiben
- einen Testlauf durchführen
- die alte und neue Version vergleichen
- die neue Version zur Aktivierung vorschlagen

Erst danach wird die neue Version aktiviert.

Das verhindert, dass ein Agent mitten in einem Lauf seine eigenen Regeln verändert und anschließend nicht mehr nachvollziehbar ist, warum er sich anders verhält.

## Alles editierbar – aber mit Entwurf und aktiver Version

Die Oberfläche sollte jedes Element anklickbar und bearbeitbar machen:

- Profilfelder
- Rollen
- Regeln
- LangGraph-Knoten
- Übergänge
- Tool-Berechtigungen
- RAG-Quellen
- Erinnerungsprioritäten
- Lernregeln
- Checkpoint-Verhalten
- Driftgrenzen
- Benachrichtigungen
- Agentenbeziehungen
- Pausenregeln
- Abbruchregeln

Dabei braucht jedes Objekt mindestens zwei Zustände:

### Aktive Version

Das ist die Version, die laufende Sitzungen tatsächlich verwenden.

### Entwurfsversion

Das ist die Version, die gerade bearbeitet wird.

Änderungen an der Entwurfsversion dürfen die laufende Produktion nicht automatisch verändern. Du kannst später bewusst auswählen:

- nur neue Sitzungen verwenden
- bei Checkpoints übernehmen
- laufende Sitzung sofort aktualisieren
- niemals automatisch aktualisieren

## Agenten dürfen ebenfalls editieren

Das ist möglich, aber die Rechte müssen profilbezogen sein.

Ein Agent kann zum Beispiel diese Berechtigungen haben:

| Berechtigung | Bedeutung |
|---|---|
| Lesen | Status, Regeln und Erinnerungen ansehen |
| Kommentieren | Meinung oder Kritik abgeben |
| Vorschlagen | Änderung als Entwurf erzeugen |
| Bearbeiten | Entwurf direkt verändern |
| Testen | eine Harness-Version simulieren |
| Aktivieren | eine geprüfte Version freischalten |
| Pausieren | eigene oder fremde Sitzungen pausieren |
| Fortsetzen | eine pausierte Sitzung fortsetzen |
| Beenden | eine Sitzung kontrolliert stoppen |
| Archivieren | Profil oder Harness deaktivieren |
| Löschen | innerhalb eines ausdrücklich erlaubten Bereichs entfernen |
| Systemverwaltung | globale Regeln und Berechtigungen ändern |

Die letzten Berechtigungen sollten nicht automatisch jedem Agenten gegeben werden.

Wenn du möchtest, dass Agenten Dinge löschen, pausieren oder verändern dürfen, dann definierst du das pro Profil:

- Was darf Claude im Debugging-Profil?
- Was darf Codex im Implementierungsprofil?
- Was darf Gemini im Review-Profil?
- Darf ein Agent nur seine eigenen Sitzungen ändern?
- Darf ein Reviewer andere Agenten stoppen?
- Darf ein Agent Harness-Entwürfe aktivieren?
- Darf ein Agent globale Regeln ändern?

Wichtig ist eine Trennung zwischen:

- **Bearbeiten**
- **Aktivieren**
- **Löschen**
- **Berechtigungen ändern**

Ein Agent kann zum Beispiel einen Harness-Entwurf bearbeiten, aber nicht die Sicherheitsregeln ändern, die festlegen, ob er ihn aktivieren darf.

## Löschen sollte normalerweise Archivieren bedeuten

Wenn alles editierbar und löschbar ist, brauchst du trotzdem Wiederherstellung.

Ich würde drei Aktionen unterscheiden:

### Deaktivieren

Das Objekt bleibt erhalten, kann aber nicht mehr verwendet werden.

### Archivieren

Das Objekt verschwindet aus der normalen Oberfläche, bleibt aber wiederherstellbar.

### Dauerhaft löschen

Das wird nur für bestimmte Daten erlaubt und sollte eine zusätzliche Bestätigung oder eine besondere Rolle benötigen.

Für Profile, Harnesses, Regeln, Lerninhalte und Sitzungen sollte die Standardaktion nicht sofortiges Löschen sein, sondern Deaktivieren oder Archivieren.

## Agenten dürfen miteinander diskutieren

Das sollte nicht nur ein freier Chat sein. Es sollte ein nachvollziehbarer Arbeitsraum werden.

Agenten können:

- Meinungen abgeben
- Alternativen vorschlagen
- Einwände formulieren
- Beweise anführen
- andere Agenten korrigieren
- Aufgaben übernehmen
- Ergebnisse übergeben
- Entscheidungen vorbereiten
- Änderungen reviewen
- über Harness-Versionen abstimmen

Jede Nachricht sollte mit einem Kontext verknüpft sein:

- Profil
- Harness
- Sitzung
- Aufgabe
- Datei
- Version
- Checkpoint
- Entscheidung

So bleibt später nachvollziehbar:

> Warum wurde diese Regel geändert?

> Welcher Agent hat sie vorgeschlagen?

> Welche Evidenz wurde genannt?

> Wer hat widersprochen?

> Warum wurde die Entscheidung angenommen?

### Gute Kommunikationsformen

Neben normalen Nachrichten würde ich spezielle Nachrichtentypen vorsehen:

- Meinung
- Vorschlag
- Einwand
- Frage
- Beweis
- Übergabe
- Warnung
- Freigabeanfrage
- Entscheidung
- Rücknahme

Ein Agent kann also sagen:

> „Ich widerspreche der aktuellen Datenbankstrategie, weil der vorhandene Migrationsstand nicht zu dieser Annahme passt.“

Ein anderer Agent kann antworten:

> „Ich habe das geprüft. Die Migration ist tatsächlich veraltet. Ich schlage eine neue Reihenfolge vor.“

Der Controller kann daraus einen sichtbaren Entscheidungsprozess machen. Die Diskussion selbst darf aber nicht automatisch eine Systemänderung auslösen.

## Diskussion und Ausführung müssen getrennt bleiben

Ein Agent darf im Chat schreiben:

> „Wir sollten diesen Service neu starten.“

Das darf nicht automatisch bedeuten, dass der Service neu gestartet wird.

Stattdessen entsteht daraus:

- ein Vorschlag
- eine Prüfung
- eventuell eine Freigabe
- anschließend eine kontrollierte Aktion
- danach ein Ereignis mit Ergebnis

So können die Agenten frei argumentieren, ohne dass jede sprachliche Äußerung sofort eine gefährliche Aktion ausführt.

## Selbstverändernde Harnesses

Wenn Agenten ihre eigenen Harnesses verbessern dürfen, brauchst du eine sichere Form von Selbstmodifikation.

Der Ablauf sollte sein:

1. Agent erkennt ein wiederkehrendes Problem.
2. Agent formuliert eine Verbesserung.
3. Agent erstellt eine neue Harness-Entwurfsversion.
4. Agent beschreibt die erwartete Wirkung.
5. Andere Agenten prüfen die Änderung.
6. Eine Simulation läuft mit Beispieldaten.
7. Der Controller vergleicht alte und neue Ergebnisse.
8. Die Änderung wird freigegeben oder abgelehnt.
9. Bei Freigabe wird die neue Version aktiviert.
10. Bei Problemen wird auf die vorherige Version zurückgerollt.

Die gefährlichste Variante wäre:

> Der Agent ändert den aktiven Harness direkt und läuft anschließend mit seinen eigenen neuen Regeln weiter.

Das sollte nur als ausdrücklich aktivierbarer experimenteller Modus existieren.

## Die neue Struktur von `/os`

Ich würde die Oberfläche ungefähr so organisieren:

### Leitstand

Alle aktiven Sitzungen, Warnungen, Ressourcen und Eingriffe.

### Profile

Profile erstellen, kopieren, editieren, aktivieren, deaktivieren und archivieren.

### Harnesses

Visueller Ablauf-Editor mit:

- Knoten
- Übergängen
- Bedingungen
- Schleifen
- Retries
- Checkpoints
- Tool-Aufrufen
- Freigabepunkten
- Lernschritten
- Review-Schritten

### Agentenräume

Gemeinsame Diskussionen, Aufgaben, Übergaben und Entscheidungen.

### Graphsicht

Aktueller LangGraph-Zustand jedes Agenten.

### Memory und RAG

Erinnerungen, Quellen, Abrufe, Konflikte, Prioritäten und Gültigkeiten.

### Learning

Lernkandidaten, Bewertungen, aktivierte Regeln und Rücknahmen.

### Regeln und Berechtigungen

Wer darf was lesen, ändern, aktivieren, pausieren oder löschen?

### Versionen

Alle Änderungen an Profilen, Harnesses und Regeln mit Vergleich und Rollback.

### Sitzungen

Live-Status, Terminal, Ereignisse, Dateien, Tests und Checkpoints.

### Infrastruktur

VPS-Prozesse, PostgreSQL, Speicher, Netzwerk, Services und Agenten-Supervisoren.

## Der Controller braucht eine Capability-Schicht

Damit wirklich „alles anklickbar“ sein kann, sollte jedes Objekt seine möglichen Aktionen selbst beschreiben.

Ein Profil weiß zum Beispiel:

- welche Felder es besitzt
- welche Harnesses dazugehören
- welche Aktionen erlaubt sind
- welche Rollen es ändern dürfen
- welche Version aktiv ist
- welche Abhängigkeiten bestehen

Ein Harness weiß:

- welche Knoten es enthält
- welche Übergänge erlaubt sind
- welche Tools gebraucht werden
- welche Regeln gelten
- welche Profile es verwenden dürfen

Die Oberfläche kann daraus automatisch die passenden:

- Buttons
- Formulare
- Schalter
- Dialoge
- Graph-Editoren
- Freigaben
- Warnungen

erzeugen.

Damit musst du nicht für jede neue Funktion die gesamte Oberfläche neu bauen.

## Was jeder Agent in seinem Selbststatus sehen sollte

Der bisherige Selbststatus muss jetzt um Profil-, Harness- und Lerninformationen erweitert werden.

Jeder Agent sollte wissen:

- welches Profil aktiv ist
- welcher Harness aktiv ist
- welche Version verwendet wird
- in welchem LangGraph-Knoten er sich befindet
- welche Aufgabe er besitzt
- welche anderen Agenten beteiligt sind
- welche Erinnerungen abgerufen wurden
- welche Lernhypothese geprüft wird
- welche Rechte er besitzt
- welche Aktionen verboten sind
- welche Warnungen offen sind
- ob sein Harness geändert wurde
- ob eine neue Version zur Prüfung bereitsteht
- welchen Status der Controller als wahr betrachtet

Der Agent darf natürlich eine eigene Meinung dazu haben. Aber der Controller muss zwischen diesen beiden Dingen unterscheiden:

- „Der Agent glaubt, dass sein Zustand so ist.“
- „Der Controller kann diesen Zustand durch Ereignisse bestätigen.“

## Die wichtigste neue Designentscheidung

Dein System braucht drei Arten von Wahrheit:

### Agentenmeinung

Was ein Agent über eine Aufgabe, einen Fehler oder eine Regel denkt.

### Gemeinsame Arbeitsentscheidung

Was die beteiligten Agenten nach Diskussion als beste Vorgehensweise vorschlagen.

### Controller-Wahrheit

Was tatsächlich passiert ist:

- welcher Prozess läuft
- welche Version aktiv ist
- welcher Tool-Aufruf ausgeführt wurde
- welcher Test erfolgreich war
- welche Regel gilt
- welche Sitzung pausiert wurde
- welche Änderung freigegeben ist

Die Agenten dürfen die ersten beiden Ebenen beeinflussen. Die dritte Ebene darf nur aus überprüfbaren Systemereignissen entstehen.

## Das Gesamtbild

Damit wird dein System im Grunde:

- ein Agentenbetriebssystem
- ein visueller Harness-Builder
- ein Rollen- und Profilmanager
- ein LangGraph-Leitstand
- ein Memory- und RAG-Inspector
- ein Selbstlern-Governance-System
- ein Multi-Agenten-Arbeitsraum
- ein Versions- und Rollback-System
- ein Live-Dashboard
- eine Kontrollinstanz für den VPS

Der Kern sollte daher so aussehen:

> Profile bestimmen, wer ein Agent für eine Aufgabe ist.  
> Harnesses bestimmen, wie er arbeitet.  
> LangGraph bestimmt, wo er sich im Ablauf befindet.  
> PostgreSQL hält seinen Zustand.  
> Reminding-RAG liefert relevanten Kontext.  
> Selbstlernen schlägt Verbesserungen vor.  
> Flextraxtreme überwacht, versioniert und begrenzt alles.  
> `/os` macht den gesamten Prozess sichtbar und editierbar.

Damit wäre `flextrawurst.de/os` nicht bloß eine Verwaltungsseite, sondern die zentrale Werkstatt und Betriebszentrale für deine Agentenwelt.
