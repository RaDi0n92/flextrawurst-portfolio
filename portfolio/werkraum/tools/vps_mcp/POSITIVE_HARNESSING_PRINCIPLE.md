# Positive Harnessing im VPS-MCP

## Grundidee

Harnessing soll künftig nicht pauschal als Zwangssystem verstanden oder vermieden werden.

Die frühere Erfahrung mit zu breiten Startgates, Hooks und globalen Regeln bleibt eine Warnung. Daraus folgt aber nicht, dass Harnessing grundsätzlich schlecht ist.

Stattdessen soll der MCP häufiger kleine, klar begrenzte, projekt- oder zweckgebundene Harnesses aufnehmen, wenn sie wiederkehrende Zusammenarbeit robuster machen.

## Gute Einsatzfälle

Ein Harness ist besonders sinnvoll, wenn er:
- einen langen Arbeitsprozess gegen Kontextdrift absichert,
- einen aktuellen Projektzustand kompakt wieder einliest,
- Regeln oder Arbeitsverfassungen mit Hashes bindet,
- Provenienz oder Chronologie sichtbar hält,
- verlustfreie Transformationen technisch prüft,
- einen klaren Export- oder Sicherheitsvertrag kontrolliert,
- wiederkehrende Vor-/Nachprüfungen automatisiert,
- mehreren Modellen oder Sessions denselben verifizierten Arbeitskontext bereitstellt.

## Bevorzugtes Muster

1. projektgebunden statt global
2. explizit oder kontextbezogen aktiviert statt heimlich immer aktiv
3. read-only Kontext zuerst
4. Warnen vor Blockieren
5. Fail-closed nur bei klaren, irreversiblen Vertragsverletzungen
6. bestehende Werkzeuge nicht automatisch umhüllen
7. keine unsichtbare Bedeutungs- oder Entscheidungslogik
8. Harness selbst testbar, versionierbar und rückbaubar halten

## Leitfrage

Nicht:
"Wie zwingen wir das Modell, sich richtig zu verhalten?"

Sondern:
"Welche wiederkehrende Kontext-, Prüf- oder Provenienzarbeit können wir dem System zuverlässig abnehmen, ohne sein Lesen, Denken und Erkunden unnötig einzuschränken?"

## Referenzimplementierung

Erster positiver Pilot:
`portfolio.archaeology_context`

Eigenschaften:
- opt-in
- read-only
- projektlokale Konfiguration
- Verfassungs-/State-Hashes
- kein Startup-Hook
- keine automatische Tool-Umhüllung
- ordinary reading/searching bleibt frei

Diese Datei ist ein Gestaltungsprinzip, kein globaler Zwangsvertrag.

## Freiheit, Drift und situatives Arbeiten

Die Harness soll den Agenten tragen, nicht beaufsichtigen.

Leitidee:
**Struktur, die Freiheit tragfähig macht.**

Daraus folgt:
- Knoten, States und mögliche Wege sind bevorzugt sichtbare Arbeitsräume, nicht automatisch Pflichtreihenfolgen.
- Ein neuer Fund darf die nächste sinnvolle Frage verändern.
- Nicht jede Abweichung vom ursprünglich gedachten Weg ist Drift.
- Drift liegt eher vor, wenn das eigentliche Goal still ersetzt, vergessen oder durch lokale Optimierung verdrängt wird.
- Gute Leitplanken sind besser als Schienen.
- Große Arbeitsbögen dürfen autonom bleiben; innerhalb davon sollen Belege, Unsicherheiten und reale Zustände mikroskopisch sauber geprüft werden.
- Erst einen relativ nackten Agenten im realen Arbeitsprozess beobachten und konkrete Schwächen feststellen.
- Unterstützung gezielt gegen beobachtete Schwächen ergänzen, nicht vorsorglich gegen hypothetische Probleme.
- Vermeiden, dass die Harness selbst so komplex wird, dass sie wiederum eine eigene Harness braucht.

Für Daniels Arbeitsweise besonders wichtig:
Viele Aufgaben an CLI-AI-Ströme sind situativ und einzigartig. Wiederholung und Automatisierung passen häufiger zu Entitäten oder klar wiederkehrenden Prozessen als zu jedem menschlich-agentischen Arbeitsbogen.

Ein Harness soll daher Kontext, Nachvollziehbarkeit, Beweisbarkeit und Bewegungsräume stabilisieren, nicht einen universellen Loop wie EXPLORE → PLAN → BUILD → VERIFY zur Systemreligion machen.

## Herkunft dieser Erweiterung

Diese Präzisierung entstand aus einer parallelen ChatGPT-Session und wurde am 2026-10-01 über folgende Inbox-Datei in diesen Arbeitsstrang übergeben:

/root/werkraum/in_gpt/job-portfolio-try/INBOX_FROM_PARALLEL_CHATGPT_2026-10-01_HARNESS_PHILOSOPHY.md

Die Inbox-Datei bleibt unverändert als eigene Quelle erhalten.

## Beobachtete Navigationsdrift als positiver Harness-Fall

Beim Portfolio zeigte sich eine konkrete, nicht hypothetische Schwäche:

Während der Kuratierung entstanden immer mehr Begleitdateien, längere Archivnamen und zusätzliche Meta-Navigation. Technisch wurde das Archiv korrekter, für Menschen aber zunehmend schwerer natürlich zu betreten.

Daraus folgt als gezielte Unterstützung:

- sichtbare Packs sollen wie natürlich zusammengestellte Uploadordner wirken,
- Quellen tragen möglichst viel Orientierung selbst,
- pro Pack ist höchstens eine kleine `LESEN.md` das Ziel,
- alte Meta-Navigation wird als Migrationsschuld gezählt,
- diese Schuld wird nur gewarnt, niemals als Arbeitsblocker behandelt,
- logische Forschungswege mit selbsterklärenden Ober-/Unterordnern ergänzen die kanonische Chronologie,
- Namensqualität bleibt weiche Gestaltung und wird nicht mit starren Zeichenlimits erzwungen.

Das ist ein Musterbeispiel für Positive Harnessing:
Erst reale Arbeit beobachten, dann eine tatsächlich aufgetretene Drift mit einer kleinen read-only Leitplanke sichtbar halten.

