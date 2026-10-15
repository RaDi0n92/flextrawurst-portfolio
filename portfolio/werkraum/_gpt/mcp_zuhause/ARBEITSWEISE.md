# Arbeitsweise des VPS-MCP

## Leser und Schreiber unterscheiden

Der MCP behandelt nicht mehr jeden Werkzeugaufruf gleich.

### Gemeinsame Lesesperre

Explizit klassifizierte reine Leseaktionen dürfen innerhalb derselben History-Session gleichzeitig laufen. Beispiele sind Datei-Rücklesung, Metadaten, Git-Lesen, Dienststatus, Logs, Datenbank-SELECTs und Sitzungsrecherche.

Mehrere Leser teilen sich dieselbe Session-Sperrdatei über eine gemeinsame Betriebssystem-Lesesperre.

### Exklusive Sperre

Exklusiv bleiben insbesondere:

- Schreiben, Editieren, Verschieben und Löschen,
- Shell- und erlaubte Prozessausführung,
- Dienststart, -stopp und -neustart,
- Testläufe mit möglichen Seiteneffekten,
- Import, Export oder Konvertierung mit Dateierzeugung,
- nicht eindeutig als read-only klassifizierte Werkzeuge.

Unsicherheit führt zur exklusiven Klasse, nicht zur optimistischen Parallelität.

## Warum die Session trotzdem eine Sperre behält

Die Sperre verhindert weiterhin, dass eine Session beendet wird, während noch eine ihrer Aktionen läuft. `session.end` nimmt exklusiven Zugriff und wartet damit auf alle laufenden Leser und Schreiber.

Die Hash-History bleibt separat serialisiert. Leser arbeiten parallel, aber ihre kurzen Abschlussereignisse werden weiterhin in eindeutiger Reihenfolge an die append-only Kette angehängt.

## Begrenzte rekursive Suche

Breite Suchen erhalten:

- Zeitbudget,
- maximales Scanbudget,
- deduplizierte Wurzeln,
- standardmäßiges Überspringen großer Abhängigkeits- und Cacheordner,
- ehrlichen Teilstatus bei Abbruch.

Ein Teilresultat ist kein Fehler, solange Abbruchgrund und Umfang sichtbar sind. Ein stiller 49-Minuten-Lauf ohne Zwischen- oder Budgetgrenze ist dagegen kein Tiefgang, sondern fehlende Steuerung.

## Arbeit mit Zuständigkeiten

Vor Mutationen:

1. aktive Claims lesen,
2. Zielbesitz prüfen,
3. bei Kollision einen eigenen additiven Arbeitsring wählen oder die Besitzer-Sitzung anschreiben,
4. Backup und Sicherungs-Commit setzen,
5. Änderung isoliert testen,
6. produktiv rücklesen,
7. Hash-History verifizieren.

## Skills

Installierte Skills sind verfügbarer Bestand. Ihre bloße Existenz beweist weder automatische Auswahl noch tatsächliche Anwendung. Nutzung gilt erst als belegt, wenn eine Werkzeug-, Sitzungs-, Log- oder Dateispur sie zeigt.
