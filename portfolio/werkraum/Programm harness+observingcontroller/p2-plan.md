Ah, das ist kein kleines Detail – das verändert die Architektur deutlich.

Dann hast du nicht einfach drei CLI-Agenten, sondern drei eigene agentische Laufzeitsysteme:

- LangGraph als Ablauf- und Entscheidungsgraph
- PostgreSQL als dauerhaften Zustand
- Reminding-RAG als Erinnerungs- und Kontextschicht
- eine Selbstlernschleife
- zusätzlich die jeweilige Modell- und Toolschicht von Claude, Codex oder Gemini

`flextrawurst.de/os` sollte diese internen Systeme nicht ersetzen, sondern als übergeordnete Betriebs- und Kontrollschicht darüberliegen.

Ich interpretiere „Reminding-RAG“ dabei als eine Schicht, die relevante Erinnerungen, Aufgaben, Hinweise und frühere Erkenntnisse zum richtigen Zeitpunkt wieder in den Agentenkontext einbringt.

## Die aktualisierte Architektur

```text
Claude-Code-System ─┐
Codex-System        ─┼─> Flextraxtreme Controller ─> flextrawurst.de/os
Gemini-System       ─┘             │
                                   ├─ Live-Ereignisse
                                   ├─ Drift-Erkennung
                                   ├─ Interventionen
                                   ├─ gemeinsamer Status
                                   └─ Sicherheitsregeln
```

Jeder Agent besitzt intern:

```text
Modell
  ↓
LangGraph
  ↓
PostgreSQL-Zustand
  ↓
Reminding-RAG
  ↓
Selbstlern-Schleife
  ↓
Tool- und Terminalaktionen
```

Flextraxtreme sitzt darüber und beobachtet:

- welchen LangGraph-Knoten der Agent gerade ausführt
- welche Erinnerungen abgerufen wurden
- welche Daten geschrieben wurden
- welche Lernhypothesen entstanden sind
- welche Aktionen tatsächlich im Terminal stattfanden
- ob die behauptete Selbstbeschreibung zur Realität passt

## Flextraxtreme wird zur Meta-Schicht

Jeder Agent hat sein eigenes „Gehirn“. Flextraxtreme sollte kein gemeinsames Gehirn daraus machen, sondern eine übergeordnete Meta-Schicht.

Das bedeutet:

### Der Agent selbst verwaltet

- seinen internen LangGraph-Zustand
- seine lokale Erinnerung
- seine RAG-Abfragen
- seine eigenen Lernkandidaten
- seine aktuelle Aufgabe
- seine lokalen Checkpoints

### Flextraxtreme verwaltet

- Identität und Sitzung
- Berechtigungen
- Arbeitsbereich
- Fortschritt
- Ereignisse
- Risiken
- Drift
- Agentenbeziehungen
- Interventionen
- Freigaben
- gemeinsame Projektwahrheit

Das ist ein föderiertes System: Jeder Agent darf eine eigene Innenwelt haben, aber der Controller behält den Überblick über die äußere Realität.

## Die Datenbanken dürfen nicht einfach vermischt werden

Wenn alle Agenten eigene PostgreSQL-Datenbanken oder Tabellen besitzen, solltest du diese nicht ungeordnet zu einer großen gemeinsamen Datenbank machen.

Ich würde drei Ebenen unterscheiden.

### Agent-interne Datenbank

Dort liegen:

- LangGraph-Checkpoints
- lokaler Gesprächszustand
- persönliche Erinnerungen
- agentenspezifische RAG-Dokumente
- Lernkandidaten
- agentenspezifische Präferenzen
- interne Arbeitsnotizen

Diese Daten gehören grundsätzlich dem jeweiligen Agenten.

### Gemeinsame Controller-Datenbank

Dort liegen:

- Agentenregister
- Sitzungen
- Live-Status
- normalisierte Ereignisse
- Driftwarnungen
- Interventionen
- Freigaben
- Checkpoints mit Verweisen
- Datei- und Aufgabenbesitz
- Controller-Revisionen
- Infrastrukturzustand

Diese Daten gehören Flextraxtreme.

### Gemeinsame Wissensschicht

Dort dürfen nur bewusst freigegebene Dinge landen:

- bestätigte technische Entscheidungen
- geprüfte Architekturregeln
- erfolgreiche Reparaturmuster
- projektweite Konventionen
- freigegebene Erkenntnisse aus einem Agentenlauf
- explizite Übergaben

Eine private Erinnerung von Claude sollte nicht automatisch zu einer Wahrheit für Codex und Gemini werden.

## Das Live-Dashboard muss LangGraph sichtbar machen

Die bisherige Terminalüberwachung wäre bei deinem System zu oberflächlich. Auf `flextrawurst.de/os` sollte man zusätzlich den LangGraph-Lauf sehen.

Für jeden Agenten brauchst du mindestens:

- aktueller Graph
- aktueller Knoten
- vorheriger Knoten
- nächster erwarteter Knoten
- Dauer im aktuellen Knoten
- Anzahl der Wiederholungen
- letzter Checkpoint
- letzter Übergang
- offene Unteraufgaben
- aktueller Zustand
- Fehler und Retries
- erwartetes Ergebnis

Beispiel:

| Bereich | Anzeige |
|---|---|
| Graph | „Analyse → Planung → Änderung → Test“ |
| Aktueller Knoten | „Test“ |
| Zustand | „Wartet auf Testresultat“ |
| Letzter Checkpoint | „Änderung an Authentifizierung abgeschlossen“ |
| RAG | „3 Erinnerungen abgerufen“ |
| Lernen | „1 neue Hypothese vorgeschlagen“ |
| Risiko | „Gelb: Test wird wiederholt“ |

So siehst du nicht nur, dass ein Terminalprozess lebt, sondern auch, wo im Denken und Handeln des Agenten er sich befindet.

## Reminding-RAG muss ebenfalls beobachtbar sein

Ein RAG-System kann selbst Drift auslösen.

Wenn ein Agent plötzlich in eine falsche Richtung läuft, kann die Ursache sein:

- eine veraltete Erinnerung
- ein widersprüchliches Dokument
- ein falsch gewichteter Treffer
- ein Erinnerungsfragment aus einem anderen Projekt
- eine Erinnerung ohne ausreichende Herkunft
- ein Hinweis, der zu oft wiederholt wird
- eine alte Aufgabe, die eigentlich abgeschlossen war

Deshalb sollte `/os` für jede wichtige Erinnerung anzeigen können:

- Quelle
- Zeitpunkt
- Projekt
- Besitzer
- Gültigkeitsbereich
- Version
- Vertrauensstatus
- Grund für den Abruf
- ob sie bestätigt, vorgeschlagen oder veraltet ist

Der Agent sollte nicht nur sehen:

> „Diese Erinnerung wurde abgerufen.“

Sondern besser:

> „Diese Erinnerung wurde abgerufen, weil sie zum aktuellen Auftrag und zur Datei passt. Sie stammt aus einem geprüften Checkpoint vom 7. Oktober.“

Damit kann der Agent seine eigene Kontextlage besser einschätzen.

## Die Selbstlernschleife braucht eine eigene Kontrollspur

Eine Selbstlernschleife darf nicht einfach stillschweigend das Verhalten eines Agenten verändern.

Ich würde fünf Stufen einführen:

### Beobachten

Der Agent sammelt:

- Fehler
- erfolgreiche Reparaturen
- wiederkehrende Muster
- neue technische Erkenntnisse
- Nutzerkorrekturen
- wiederholte Entscheidungen

Noch nichts wird dauerhaft verändert.

### Vorschlagen

Aus Beobachtungen entsteht eine Lernhypothese:

- „Bei diesem Fehlertyp zuerst die Datenbankverbindung prüfen.“
- „Dieses Projekt verwendet diese Testreihenfolge.“
- „Diese Fehlermeldung bedeutet wahrscheinlich eine veraltete Migration.“

Das ist zunächst nur ein Vorschlag.

### Bewerten

Der Vorschlag wird geprüft:

- Gibt es ausreichende Evidenz?
- Widerspricht er einer bestehenden Regel?
- Ist er projektübergreifend oder nur lokal gültig?
- Hat er tatsächlich geholfen?
- Gibt es Gegenbeispiele?
- Ist die Quelle vertrauenswürdig?
- Kann der Vorschlag zurückgenommen werden?

### Freigeben

Erst danach darf eine Erkenntnis in eine dauerhafte Wissens- oder Erinnerungsschicht übernommen werden.

Das kann automatisch für risikoarme Fakten geschehen. Für Verhalten, Berechtigungen, Systemprompts und Sicherheitsregeln sollte eine menschliche Freigabe nötig sein.

### Zurückrollen

Jede gelernte Änderung braucht:

- Version
- Herkunft
- Zeitpunkt
- zugehörige Agentensitzung
- Belege
- vorherigen Stand
- Rücknahmeoption

## Vier Speicherklassen für jeden Agenten

Ich würde Erinnerungen und Lerninhalte in vier Klassen aufteilen.

### Arbeitsgedächtnis

Kurzlebiger Kontext für den aktuellen Turn oder Graphlauf.

### Episodische Erinnerung

Was in einem konkreten Lauf passiert ist:

- Aufgabe
- Fehler
- Lösung
- Test
- Entscheidung
- Übergabe

### Geprüftes Wissen

Dauerhafte technische Erkenntnisse, die bestätigt wurden.

### Identität und Regeln

Rollen, Sicherheitsgrenzen, Arbeitsprinzipien und Systemregeln.

Die letzte Klasse darf nicht durch eine normale Selbstlernschleife überschrieben werden. Ein Agent sollte sich nicht selbst die Erlaubnis geben können, seine Grenzen zu verändern.

## Neue Drift-Arten durch Selbstlernen

Mit LangGraph, RAG und Selbstlernen kommen zusätzliche Driftformen hinzu.

### Graph-Drift

Der Agent bleibt in einer Schleife oder springt in einen nicht vorgesehenen Ablauf.

Erkennung:

- gleicher Graph-Knoten zu oft
- unerwartete Übergänge
- Wiederholungen ohne neue Evidenz
- Checkpoint wird nicht aktualisiert

Reaktion:

- Knoten pausieren
- Zwischenstatus anfordern
- letzten funktionierenden Checkpoint anzeigen
- Übergang nur nach Freigabe zulassen

### Memory-Drift

Der Agent verwendet alte oder widersprüchliche Erinnerungen.

Erkennung:

- Erinnerungen aus falschem Projekt
- widersprüchliche Versionen
- abgelaufene Hinweise
- unerklärliche Priorität eines einzelnen Dokuments

Reaktion:

- Erinnerung aus dem Kontext entfernen
- RAG-Abfrage neu durchführen
- Provenienz anzeigen
- Agent zur Begründung auffordern

### Learning-Drift

Die Selbstlernschleife verändert das Verhalten stärker als vorgesehen.

Erkennung:

- neue Regel ohne Lernvorschlag
- neue Aktion ohne Freigabe
- Änderung des Rollenverständnisses
- zunehmende Abweichung vom ursprünglichen Auftrag
- Verhalten ändert sich nach einem einzigen Erlebnis

Reaktion:

- Lernpromotion stoppen
- letzte gelernte Änderung zurückrollen
- Agent in Beobachtungsmodus versetzen
- neue Erkenntnis nur als Vorschlag weiterführen

### Controller-Drift

Der Agent behauptet einen Zustand, der nicht mit LangGraph, PostgreSQL oder dem VPS übereinstimmt.

Beispiel:

- Agent behauptet „Test erfolgreich“
- LangGraph meldet aber einen offenen Testknoten
- PostgreSQL besitzt kein aktuelles Testergebnis
- Terminalprozess ist bereits beendet

In diesem Fall gilt die externe Evidenz als Wahrheit.

## Die Selbststatuskarte muss erweitert werden

Die Statuskarte, die jeder Agent erhält, sollte nun nicht nur Aufgabe und Arbeitsverzeichnis enthalten.

Sie braucht zusätzlich:

### Graphstatus

- aktueller LangGraph-Knoten
- letzter Übergang
- nächster erlaubter Übergang
- letzter Checkpoint
- Anzahl der Wiederholungen

### Gedächtnisstatus

- welche Erinnerungen abgerufen wurden
- aus welchem Projekt sie stammen
- ob sie bestätigt oder nur vorgeschlagen sind
- ob es Widersprüche gibt

### Lernstatus

- ob die Selbstlernschleife aktiv ist
- welche Lernhypothese gerade geprüft wird
- ob sie nur beobachtet, vorgeschlagen oder bereits freigegeben wurde
- welche Änderungen zuletzt aus Lernen entstanden sind

### Controllerstatus

- letzte Controller-Revision
- aktuelle Driftstufe
- offene Warnungen
- offene Freigaben
- Status der anderen Agenten

Ein Agent sollte regelmäßig bestätigen können:

- Ich kenne meine aktuelle Aufgabe.
- Ich kenne meine Grenzen.
- Ich kenne meinen Graphzustand.
- Ich weiß, welche Erinnerungen meinen aktuellen Kontext beeinflussen.
- Ich weiß, ob ich gerade lernen darf.
- Ich weiß, welche Handlungen eine Freigabe benötigen.

Diese Bestätigung ist aber nur ein Signal. Sie ersetzt nicht die externe Prüfung.

## Neue Bereiche für `/os`

Für dein erweitertes System würde ich die Oberfläche um drei wichtige Ansichten ergänzen:

### GRAPH

Der visuelle LangGraph-Lauf:

- aktueller Knoten
- Übergänge
- Schleifen
- Checkpoints
- Fehler
- Wartebedingungen

### MEMORY

Die Erinnerungsspur:

- RAG-Abfragen
- abgerufene Dokumente
- Erinnerungsherkunft
- Konflikte
- Gültigkeitsdauer
- verwendete Erinnerung im aktuellen Turn

### LEARNING

Die Selbstlernschleife:

- Beobachtungen
- Lernhypothesen
- Bewertungsstatus
- Evidenz
- Freigaben
- aktive gelernte Regeln
- Rollback-Möglichkeiten

Damit kannst du eine wichtige Frage beantworten:

> Warum handelt dieser Agent gerade so?

Nicht nur:

> Was hat er getan?

## Aktualisierte Rolle von `flextrawurst.de/os`

Das Interface sollte also vier Dinge gleichzeitig leisten:

1. Deine Agenten live zeigen.
2. Ihre Graph-, Gedächtnis- und Lernzustände erklären.
3. Abweichungen früh erkennen.
4. Sicher in laufende Prozesse eingreifen.

Das ist mehr als Monitoring. Es ist eine beobachtbare Betriebsumgebung für agentische Systeme.

## Meine wichtigste Empfehlung

Wenn die Selbstlernschleifen bereits aktiv sind, solltest du zuerst die Beobachtbarkeit herstellen und erst danach die Autonomie weiter erhöhen.

Nicht unbedingt die Lernschleifen abschalten – aber jede neue gelernte Regel sollte zunächst einen sichtbaren Status bekommen:

- vorgeschlagen
- in Prüfung
- freigegeben
- abgelehnt
- zurückgerollt

Der Controller sollte niemals nur anzeigen, dass ein Agent „lernt“. Er sollte zeigen:

- was gelernt wurde
- aus welcher Erfahrung
- mit welcher Sicherheit
- für welchen Bereich
- mit welchen Folgen
- ob es zurückgenommen werden kann

Für deine Architektur ist der wichtigste Satz daher:

> Jeder Agent darf eine eigene Erinnerung und eine eigene Lernentwicklung besitzen. Aber Flextraxtreme entscheidet, was als gemeinsame Wahrheit, als aktive Regel oder als gefährliche Verhaltensänderung gilt.

So wird `flextrawurst.de/os` tatsächlich zum Betriebssystem-Interface deines Harness- und Observing-Controllers – mit Agentenstatus, LangGraph, RAG, PostgreSQL, Selbstlernen, Drift und menschlicher Kontrolle an einem Ort.
