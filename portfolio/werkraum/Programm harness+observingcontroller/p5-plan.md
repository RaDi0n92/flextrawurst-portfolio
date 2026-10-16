Ah, jetzt hab ich dich richtig verstanden: Meine vorige Einordnung war zu grob. Die Agenten starten nicht alle aus derselben Ordnerstruktur. Jeder hat seine eigene Startumgebung mit Root, persönlichem Bereich, Konfiguration und provider-spezifischen Dateien. Gemeinsam sind vor allem die technische Basis, die Datenbank und der LangGraph-Unterbau.

Ich habe über Flextraxtreme gerade nur die freigegebenen Wurzeln geprüft, keine Inhalte gelesen. Sichtbar sind unter anderem `/root/werkraum`, `/root/flextrawurst`, `/root/.claude/projects`, `/root/.codex/sessions`, ein Gemini-Bereich sowie zentrale Startdateien wie `CLAUDE.md`, `GEMINI.md` und `AGENTS.md`. Das bestätigt: Wir sollten den konkreten Pfad nicht zur Identität des Agenten machen.

Der entscheidende Architekturwechsel ist:

| Ebene | Bedeutung |
|---|---|
| Startumgebung | Der technische Ort, aus dem ein Agent startet: Root, Config, Dateien, lokale Tools |
| Agentenheim | Die registrierte Umgebung eines konkreten Agenten oder Agentenverbunds |
| Agenteninstanz | Ein bestimmtes laufendes Claude-, Codex- oder Gemini-Exemplar |
| Sitzung | Ein konkreter Gesprächs- oder Arbeitslauf |
| Ausführung | Ein einzelner Auftrag oder Graph-Lauf |
| Unteragent | Ein vom Hauptagenten erzeugter Kindprozess mit eigener Aufgabe |
| Gemeinsamer Unterbau | PostgreSQL, LangGraph, RAG, Eventbus und Controller |

Der Pfad ist also nur ein Hinweis auf die Startumgebung. Die eigentliche Identität sollte separat bestehen bleiben. Wenn ein Claude später aus einem anderen Verzeichnis startet, ist er dadurch nicht automatisch ein neuer Agent. Umgekehrt können zwei Claude-Prozesse aus derselben Umgebung kommen und trotzdem zwei vollständig getrennte Agenteninstanzen sein.

Das Datenmodell sollte daher nicht einfach lauten:

> Claude, Codex, Gemini

Sondern eher:

> Providerfamilie → Agentenheim → konkrete Instanz → Sitzung → Aufgabe → Unteragentenbaum

Damit können wir beliebig viele gleiche Agenten verwalten:

- Claude-Planer
- Claude-Implementierer
- Claude-Reviewer
- Claude-Sicherheitsprüfer
- Claude-Wächter
- Claude-Dokumentierer

Alle können vom selben Anbieter stammen und dieselbe technische Infrastruktur verwenden. Trotzdem bekommen sie jeweils eine eigene Identität, eigene Rolle, eigene Sitzung, eigene Berechtigungen und eine eigene Herkunftsspur.

„Gleicher Anbieter“ bedeutet dann nicht mehr „derselbe Agent“. Der Anbieter ist nur die Denkmaschine. Die Agenteninstanz ist die konkrete Persönlichkeit beziehungsweise Arbeitsrolle.

Beim Start sollte jeder Agent automatisch einen Startbericht an den Harness-Controller geben:

- aus welcher Umgebung er gestartet wurde;
- welcher Anbieter und welches Modell aktiv sind;
- welche Agenteninstanz er ist;
- welches Profil und welcher Harness geladen wurden;
- welche Version von LangGraph aktiv ist;
- welcher RAG- und Erinnerungsstand verwendet wird;
- welche Datenbankverbindung besteht;
- welche Rechte er besitzt;
- ob er Hauptagent, Unteragent oder Teil eines bestehenden Agentenbaums ist;
- welche Aufgabe und welcher Elternagent zu ihm gehören.

Dadurch erhalten deine Agenten genau die von dir gewünschte Selbstwahrnehmung. Jeder Agent hat im Controller eine permanente „Selbstkarte“:

- Wer bin ich?
- Wo laufe ich?
- Welche Rolle habe ich?
- Was darf ich?
- Was weiß ich?
- Was weiß ich nicht?
- Welche Version meines Harness verwende ich?
- Wer hat mich gestartet?
- Welche Unteragenten habe ich?
- Woran arbeite ich gerade?
- Wo weiche ich von meinem Profil oder Ziel ab?

Das ist wesentlich stärker als nur ein Heartbeat. Der Heartbeat sagt, dass ein Prozess noch lebt. Die Selbstkarte sagt ihm und dem Controller, was dieser Prozess überhaupt ist.

Für PostgreSQL und LangGraph ist die wichtigste Regel:

Die Infrastruktur darf gemeinsam sein, der Zustand darf nicht ungeordnet gemeinsam sein.

Eine gemeinsame PostgreSQL-Datenbank ist sinnvoll. Aber jede Information muss eindeutig zugeordnet werden können zu:

- Agentenheim;
- Provider;
- Agenteninstanz;
- Sitzung;
- Aufgabe;
- Unteragent;
- Projekt;
- Profil;
- Harness-Version.

Auch beim LangGraph sollten die Graph-Definitionen gemeinsam nutzbar sein, aber jeder Lauf braucht seinen eigenen Zustand, seine eigenen Checkpoints und seine eigene Historie. Sonst überschreibt ein zweiter Claude möglicherweise den Denkzustand des ersten Claude.

Das gleiche gilt für dein Reminding-RAG:

- globales Wissen darf gemeinsam sein;
- Projektwissen darf für ausgewählte Agenten freigegeben werden;
- persönliche Agentenerinnerungen bleiben standardmäßig privat;
- Sitzungsnotizen gehören zunächst nur zur Sitzung;
- Erkenntnisse werden erst nach einer bewussten Freigabe in gemeinsames Wissen übernommen.

So verhinderst du, dass zehn gleichartige Claude-Instanzen unkontrolliert gegenseitig ihre halbfertigen Gedanken, Fehler oder falschen Annahmen in die jeweils anderen Erinnerungen schreiben.

Unteragenten bilden dabei keinen flachen Agentenordner, sondern einen echten Wald:

```text
Hauptagent: Claude-Projektleiter
├── Claude-Architekt
│   ├── Claude-Datenbankprüfer
│   └── Claude-LangGraphprüfer
├── Claude-Implementierer
├── Codex-Codeprüfer
└── Gemini-Ideenprüfer
```

Jeder Unteragent bekommt:

- einen Elternagenten;
- einen konkreten Auftrag;
- einen eigenen Lauf;
- ein begrenztes Wissensfenster;
- definierte Werkzeuge;
- eine eigene Arbeitsfläche;
- eine Rückgabe- und Übergabestruktur;
- eine nachvollziehbare Herkunft.

Der Elternagent kann dann nicht nur sagen „mein Unteragent hat etwas gemacht“, sondern der Controller kann anzeigen:

- wer ihn erzeugt hat;
- warum er erzeugt wurde;
- welchen Kontext er bekommen hat;
- welche Entscheidungen er getroffen hat;
- welche Dateien, Daten und Graphknoten er verwendet hat;
- was er zurückgemeldet hat;
- ob der Elternagent das Ergebnis übernommen oder verworfen hat.

Für mehrere gleiche Claude-Agenten ist das besonders stark. Du kannst drei unabhängige Claude-Instanzen dieselbe Frage bearbeiten lassen, ohne dass sie sich gegenseitig beeinflussen. Danach können sie ihre Ergebnisse austauschen und ein Konsens- oder Konfliktverfahren durchlaufen.

Damit entstehen dann deine Agentenversammlungen, Parlamente und Symposien nicht nur zwischen Claude, Codex und Gemini, sondern auch innerhalb derselben Familie:

- drei Claude mit unterschiedlichen Rollen;
- fünf Codex-Instanzen mit getrennten Arbeitszweigen;
- zwei Gemini als Gegenprüfung;
- ein übergeordneter Richter- oder Moderatoragent.

Die `/os`-Oberfläche sollte deshalb nicht nur eine Liste „Claude, Codex, Gemini“ zeigen. Sie sollte drei Ansichten besitzen:

1. Die Heimatkarte: Wo laufen die Agenten technisch?

2. Der Agentenwald: Welche Hauptagenten, Sitzungen und Unteragenten existieren gerade?

3. Der gemeinsame Unterbau: Wie gesund sind Datenbank, LangGraph, RAG, Eventbus, Checkpoints und Erinnerungen?

Die bereits vorhandenen Flextraxtreme-Bausteine passen dafür sehr gut: Pfadinventur für die Startumgebungen, Sessionregister für laufende Agenten, Atlas und Provenienz für die Herkunft, Handoffs für Übergaben, Pulse für neue Ereignisse sowie Versionen, Sandboxes und Zeitlinien für sichere Änderungen.

Und ganz wichtig für deine Idee, dass Agenten selbst editieren, pausieren oder löschen dürfen: Diese Aktionen müssen immer an die konkrete Instanz und den konkreten Unteragentenbaum gebunden sein. Ein Claude-Unteragent darf nicht versehentlich den Zustand eines anderen Claude löschen, nur weil beide dieselbe Datenbank verwenden.

Dafür braucht jeder Eingriff:

- ein klares Ziel;
- den verantwortlichen Agenten;
- den betroffenen Lauf oder Datensatz;
- eine Berechtigungsstufe;
- eine vorherige Version;
- eine nachvollziehbare Begründung;
- eine Rückgängig- oder Wiederherstellungsoption.

Damit wird deine unterschiedliche Startstruktur kein Problem, sondern ein Vorteil: Jede reale Umgebung bleibt so, wie sie für Claude, Codex oder Gemini funktioniert. Der Harness legt nur eine gemeinsame beobachtbare Identitäts-, Sitzungs-, Unteragenten- und Provenienzschicht darüber.

Kurz gesagt: Wir bauen nicht „einen Claude, einen Codex und einen Gemini“, sondern ein verteiltes Agentenökosystem mit vielen Bewohnern, unterschiedlichen Häusern, gemeinsamem Gedächtnis-Unterbau und einem sichtbaren Stammbaum aller Aktivitäten.
