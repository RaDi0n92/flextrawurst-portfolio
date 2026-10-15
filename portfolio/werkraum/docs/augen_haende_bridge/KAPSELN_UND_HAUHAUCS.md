---
autor: claude bei Daniels VPS
datum: 2026-09-20
herkunft: Luna-Max-Planung von codex bei Daniels VPS (2026-09-19), abgeleitet aus dem Gesprächsexport der Codex-Session 01a0b38d-5ece-75b3-a06e-86bf715f6c36 (`/config/.codex/sessions/2026/09/18/rollout-2026-09-18T10-06-21-01a0b38d-5ece-75b3-a06e-86bf715f6c36.jsonl`). Neu geschrieben von Claude aus dem Original in archiv/originale/
status: abgeleitete Planung; der Gesprächsexport bleibt unverändert
---

# Augen & Hände — Kapseln, Hauhaucs und die Zeichenschicht

Dieses Dokument beschreibt, was aus der Luna-Max-Planung für Momentkapseln, den Beobachter Hauhaucs, die Zeichen- und Textschicht und die Agentenorchestrierung abgeleitet wurde.

Die Baufolge weiter unten ist durch die Baustartprüfung vom 2026-09-19 korrigiert (`BEFUNDE.md`, `PLAN.md`): Zuerst kommen das getestete EXE-Paket und der tatsächliche Erstkontakt, danach die erweiterten Kapseln und Hauhaucs. Zusätzliche technische Vorschläge sind nicht automatisch Daniels Festlegungen.

Der Gesprächsexport liegt unverändert unter `/root/werkraum/docs/augen_haende_bridge/archiv/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-messages.jsonl`. Eine lesbare Fassung als Markdown liegt in `archiv/originale/`.

## Was feststeht

Das Produkt ist ein echtes Windows-Programm als EXE. Sein eigenes Fenster ist ein Overlay über dem echten Windows-Desktop, einem einzelnen Fenster, Browser, Programm oder Spiel. Eine Browserseite ist nur ein Entwicklungs- und Prüfwerkzeug.

Das Programm wird auf Daniels Windows gestartet und verbindet sich danach mit der Bridge auf dem VPS. Erst dann kann Codex tatsächlich über die laufende Verbindung sehen, prüfen und weiterbauen.

Codex bleibt dabei in seiner bestehenden VPS-CLI-Session. Das Wechseln eines Arbeitsziels erzeugt keinen neuen Codex. Mehrere sichtbare Arbeitsansichten für Codex, Claude, Gemini oder Hauhaucs dürfen dieselbe oder unterschiedliche laufende Sitzungen darstellen. Identität, Session, Ziel und Empfänger bleiben dabei getrennt.

**Geändert durch BE01** (`ANFORDERUNGEN.md`): Bestehende Sessions werden nicht angebunden. Die Sitzung, in der ein Agent bleibt, ist die, die die Bridge selbst gestartet hat.

## Momentkapseln

Der Zeit-Scrubber bekommt eine zweite, dauerhafte Form: die Momentkapsel. Sie friert einen gemeinsam ausgewählten Arbeitsmoment ein, damit Daniel und mehrere Agenten ihn später wieder öffnen, besprechen, markieren, skizzieren und als Lernstrecke weiterverarbeiten können.

Eine Kapsel darf den gesamten sichtbaren und aufgezeichneten Zusammenhang enthalten:

- Screenshots oder mehrere Frames der ausgewählten Gates, Fenster, Programme, Spiele und Desktops,
- Fenster- und Programmidentität, Geometrie, Desktop, Zielbindung und Zeitpunkt,
- sichtbare Rauten, Overlay-Texte, Bilder, Zeichnungen, Formen, Farben, Transparenz, Positionen und Empfängerregeln,
- die ausgewählten Agenten mit Session-IDs, Eltern- und Subagent-Beziehungen, Aufgaben, Status und Arbeitszielen,
- Terminal-Snapshots mit sichtbarer Ausgabe, Prompt, Arbeitsrichtung, verwendeten Tools, Ergebnissen und Auditbezug,
- die gesendeten und empfangenen Nachrichten, Regiesprüche, Chattexte, Banner und an der Raute sichtbaren Mitteilungen,
- mitgeteilte Überlegungen, Zwischenbemerkungen, Fehlermeldungen, Richtungswechsel und offene Fragen,
- Markierungen und Kommentare, die Daniel oder ein Agent der Kapsel später hinzufügt.

Private, nicht mitgeteilte interne Modellzustände werden nicht behauptet und nicht ausgelesen. Die Kapsel speichert den tatsächlich sichtbaren und protokollierten Arbeitsverlauf. Jede Quelle und jede Lücke bleibt gekennzeichnet.

Eine Kapsel kann auf sechs Arten entstehen:

1. als kompletter Moment für alle aktuell verbundenen Ziele und Agenten,
2. für ein einzelnes Fenster, Programm, Spiel oder Terminal,
3. für einen einzelnen Agenten mit seinem aktuellen Arbeitsraum,
4. für mehrere ausdrücklich markierte Bereiche und Agenten,
5. als kombinierte Kapsel aus mehreren Gates,
6. für einen kurzen Zeitbereich vor und nach einem Fehler oder einer Entscheidung.

Die Auswahl ist mehrfach markierbar. Daniel kann zum Beispiel Terminal 2, Codex, Gemini und eine bestimmte Browserfläche gemeinsam festhalten, ohne andere offene Programme in die Kapsel zu ziehen.

## Bedeutungen und Lernrichtungen

Kategorien sind Tags und keine starren Zustände. Mehrere Tags dürfen gleichzeitig gelten. Neben `Idee`, `Verwirrung`, `Fehler` und `Lösung` gehören mindestens diese Richtungen in den freien Tag-Raum:

- `Umweg` — der Weg war schmutzig, aber lehrreich.
- `Beinahe` — knapp gescheitert oder gerade gerettet.
- `Überraschung` — etwas funktionierte oder erschien anders als erwartet.
- `Widerspruch` — Agenten oder Daniel bewerten denselben Moment verschieden.
- `Offene Frage` — festhalten, ohne sofort eine Antwort zu erzwingen.
- `Vergleich` — zwei Kapseln oder Zustände nebeneinanderlegen.
- `Zufallsfund` — eine unerwartete Entdeckung.
- `Übergabe` — ein sauberer Haltepunkt für eine andere Person oder Instanz.
- `Hypothese`, `Beweis`, `Gegenbeweis`, `Blocker`, `Entscheidung`, `Rückfall`, `wiederverwendbar` und `verworfen`.

Die ursprüngliche Kapsel wird nachträglich nicht überschrieben. Spätere Interpretationen, Zeichnungen, Gegenargumente und neue Lösungen kommen als eigene Ebenen oder Folge-Kapseln dazu. So bleiben Fehler und Umwege sichtbar, statt im fertigen Ergebnis zu verschwinden.

## Hauhaucs als wählbare Beobachter-Session

Die vorhandene Dolphin- und Hauhaucs-Chatlogik ist die Referenz für den optionalen Beobachter. Hauhaucs bekommt eine eigene Session mit leerem Basis-Systemprompt. Daniel gibt ihm bei Bedarf selbst den Auftrag, zum Beispiel: »Achte ab jetzt auf Codex und Gemini. Lies mit und dokumentiere erst, wenn ich es sage.«

Die Bridge zeichnet Ereignisse zunächst skriptbasiert auf. Das ist der verlässliche Teil: Zeit, Quelle, Agent, Session, Ziel, Terminal, Tool, Ergebnis, Nachricht, Kapsel und Status werden ohne Modellaufruf gesammelt. Hauhaucs kann danach oder portionsweise lesen, Zusammenhänge erkennen und eine Dokumentation schreiben. Das reine Aufzeichnen kostet dadurch keine Modelltokens.

Die Beobachtung ist als eigene Hauhaucs-Session steuerbar:

- Beobachtung starten und stoppen.
- Zwei oder drei Agenten gleichzeitig auswählen.
- Nur Text- und Terminalereignisse lesen, den Bildzugriff separat zuschalten.
- Kontextfüllstand und tatsächlich gelesene Ereignisse anzeigen.
- Den Kontext vollständig leeren oder halbieren, einzelne Nachrichten auswählen und bearbeiten oder Sätze entfernen.
- Text und mehrere Markdown- oder Textdateien einspeisen.
- Zusatzfelder, Feedback für den nächsten Output, Zeichenlimit und Tokenlimit selbst setzen.
- Die Session speichern, benennen, archivieren, exportieren oder als flüchtige Beobachtungssession führen.
- Am Ende »jetzt dokumentieren« auslösen, wobei die Kapselverweise erhalten bleiben.

Die vorhandenen Dolphin-Bedienmöglichkeiten müssen bei einer Integration erhalten bleiben. Ein gespeicherter Kontext-Trim darf insbesondere nicht nur als ungenaue Anzahl am Anfang des Verlaufs abgelegt werden, wenn Daniel einzelne Nachrichten oder Sätze ausgewählt hat. Die Bridge braucht dafür eine explizite Ereignisliste oder eine Liste von Nachrichten-IDs.

## Zeichen- und Textschicht

Über jedem gebundenen Gate können Daniel und berechtigte Agenten dauerhaft zeichnen und schreiben:

- Freihandstift, Marker, Farben und Strichstärken.
- Linien, Pfeile, Rechtecke, Kreise und weitere schnelle geometrische Formen.
- Textmodus per Klick, wobei Textobjekte verschiebbar und bearbeitbar bleiben.
- Verschieben, Skalieren, Gruppieren, Sichtbarkeit, Reihenfolge sowie Rückgängig und Wiederholen.
- Mehrfachmarkierung und gemeinsames Speichern in einer Momentkapsel.

Die Markierung haftet an dem Raum, an den der Agent oder das Ziel gebunden ist, und bleibt darin frei verschiebbar. Zusätzlich braucht jedes Objekt eine Bindungsart: Bildschirm, Fenster, Inhalt, Agent oder Kapsel.

Ein Kreis um einen Browserbutton kann mit dem Inhalt mitwandern, eine Notiz am Fensterrand bleibt am Fenster. Ist die Inhaltserkennung nicht sicher, bleibt die Markierung an der bekannten Zielgeometrie und meldet ihre Unsicherheit.

## Agenten und Orchestrierung

Eine Codex-Instanz bleibt an ihre laufende VPS-CLI-Session gebunden. Das Overlay kann mehrere Darstellungen oder Anker derselben Session zeigen. Claude, Gemini und Hauhaucs können daneben eigene Sessions besitzen.

Subagenten werden als Kinder ihrer startenden Session geführt. Auftrag, Herkunft, Ziel, Status, Ergebnis, Sichtbarkeit und Lebensdauer sind nachvollziehbar.

Daniel kann einzelne Agenten, Gruppen oder ganze Agentenbäume beobachten, markieren, ansprechen, pausieren und, soweit die jeweilige Runtime es erlaubt, beenden. Ein Agent kann auf KDE-Desktop 2 arbeiten, während seine Raute auf Windows sichtbar ist und ein Spruch nur an einen ausgewählten Empfänger geht.

## Baufolge

Diese Reihenfolge ist durch die Baustartprüfung korrigiert (siehe oben).

1. Den Gesprächsexport sichern und die Quellen festhalten. Dieser Schritt ist mit den beiden Exportdateien erledigt.
2. Das Datenmodell für Ereignisse, Agenten-Sessions, Ziele, Bindungen, Markierungen und Momentkapseln definieren.
3. Die skriptbasierte Aufzeichnung und Kapselung bauen, zunächst ohne Hauhaucs.
4. Kapsel öffnen, Zeitlinie, Mehrfachauswahl, Annotationen und eine neue Folge-Kapsel mit sichtbarem Beleg prüfen.
5. Eine leere Hauhaucs-Chat-Session als optionalen Beobachter anschließen.
6. Kontextanzeige, Lesen, Bereinigen, Einspeisen, Promptfelder und Export anhand der Dolphin-Funktionen prüfen.
7. Die Windows-EXE bauen, auf Daniels Windows starten und über die Bridge anmelden.
8. Erst nach dem echten Handshake mit dem laufenden Programm weiterbauen: Bild hin und zurück, Text hin und zurück, Kapsel anlegen und wieder öffnen.
9. Danach Zielbindung, Rauten-Chat, Zeichenwerkzeuge, Text- und Bildobjekte, Terminal-Parität, Subagent-Orchestrierung und kontrollierte Eingabe einzeln ergänzen.

## Der erste echte Abnahmepunkt

Daniel startet die EXE auf Windows. Die EXE meldet eine eigene Session am VPS an. Codex sieht einen ausdrücklich freigegebenen Frame, und seine Nachricht erscheint im Overlay. Daniel antwortet. Beide Nachrichten, der Frame, die Zielbindung und die Ereignisse werden in einer Momentkapsel gespeichert und später gemeinsam wieder geöffnet.

Bis dieser Ablauf auf dem echten Windows-Programm funktioniert, ist die Bridge noch kein gemeinsam benutzbarer Körper. Browser-Tests und lokale Modelle können den Protokollkern vorbereiten, ersetzen diesen Abnahmepunkt aber nicht.
