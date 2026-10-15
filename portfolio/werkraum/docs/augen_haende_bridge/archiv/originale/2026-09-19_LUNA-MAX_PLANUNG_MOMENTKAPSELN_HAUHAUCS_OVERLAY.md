# Augen & Hände — Luna-Max-Planung aus dem Wortlaut

> **Korrektur durch Codex, 2026-09-19:** Die unten abgeleitete Reihenfolge wird durch `/root/werkraum/docs/augen_haende_bridge/2026-09-19_BRUECKE_BAUSTART_PRUEFUNG_UND_VEREINBARUNG.md` korrigiert: getestetes EXE-Paket und tatsächlicher Erstkontakt zuerst, erweiterte Kapseln/Hauhaucs danach. Zusätzliche technische Vorschläge sind nicht automatisch Daniels Festlegungen. Der Wortlaut-Export bleibt unverändert.

Datum: 2026-09-19  
Herkunft: `/config/.codex/sessions/2026/09/18/rollout-2026-09-18T10-06-21-01a0b38d-5ece-75b3-a06e-86bf715f6c36.jsonl`  
Wortlaut-Export: `/root/werkraum/docs/augen_haende_bridge/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-messages.md`  
Maschinenkopie: `/root/werkraum/docs/augen_haende_bridge/codex-session-01a0b38d-5ece-75b3-a06e-86bf715f6c36-messages.jsonl`  
Status: abgeleitete Planung; der Wortlaut-Export bleibt unverändert.

## Was feststeht

Das Produkt ist ein echtes Windows-Programm als EXE. Sein eigenes Fenster ist
ein Overlay über dem echten Windows-Desktop, einem einzelnen Fenster, Browser,
Programm oder Spiel. Eine Browserseite ist nur ein Entwicklungs- und
Prüfwerkzeug. Das Programm wird auf Daniels Windows gestartet und verbindet
sich danach mit der Bridge auf dem VPS. Erst dann kann Codex tatsächlich über
die laufende Verbindung sehen, prüfen und weiterbauen.

Codex bleibt dabei in seiner bestehenden VPS-CLI-Session. Das Wechseln eines
Arbeitsziels erzeugt keinen neuen Codex. Mehrere sichtbare Codex-, Claude-,
Gemini- oder Hauhaucs-Arbeitsansichten dürfen dieselbe oder unterschiedliche
laufende Sitzungen darstellen; Identität, Session, Ziel und Empfänger müssen
getrennt bleiben.

## Momentkapseln

Der Zeit-Scrubber bekommt eine zweite, dauerhafte Form: eine Momentkapsel. Sie
friert einen gemeinsam ausgewählten Arbeitsmoment ein, damit Daniel und mehrere
Agenten ihn später wieder öffnen, besprechen, markieren, skizzieren und als
Lernstrecke weiterverarbeiten können.

Eine Kapsel darf den gesamten sichtbaren und aufgezeichneten Zusammenhang
enthalten:

- Screenshots oder mehrere Frames der ausgewählten Gates, Fenster, Programme,
  Spiele und Desktops.
- Fenster-/Programmidentität, Geometrie, Desktop, Zielbindung und Zeitpunkt.
- sichtbare Rauten, Overlay-Texte, Bilder, Zeichnungen, Formen, Farben,
  Transparenz, Positionen und Empfängerregeln.
- die ausgewählten Agenten, ihre Session-IDs, Eltern-/Subagent-Beziehungen,
  Aufgaben, Status und Arbeitsziele.
- Terminal-Snapshots mit sichtbarer Ausgabe, Prompt, Arbeitsrichtung,
  verwendeten Tools, Ergebnissen und Auditbezug.
- die gesendeten und empfangenen Nachrichten, Regiesprüche, Chattexte,
  Banner und an der Raute sichtbaren Mitteilungen.
- mitgeteilte Überlegungen, Zwischenbemerkungen, Fehlermeldungen,
  Richtungswechsel und offene Fragen.
- Markierungen und Kommentare, die Daniel oder ein Agent dieser Kapsel später
  hinzufügen.

Private, nicht mitgeteilte interne Modellzustände werden nicht behauptet oder
ausgelesen. Die Kapsel speichert den tatsächlich sichtbaren und protokollierten
Arbeitsverlauf. Jede Quelle und jede Lücke bleibt gekennzeichnet.

Kapseln können auf mehrere Arten entstehen:

1. kompletter Moment für alle aktuell verbundenen Ziele und Agenten,
2. ein einzelnes Fenster, Programm, Spiel oder Terminal,
3. ein einzelner Agent mit seinem aktuellen Arbeitsraum,
4. mehrere ausdrücklich markierte Bereiche und Agenten,
5. eine kombinierte Kapsel aus mehreren Gates,
6. ein kurzer Zeitbereich vor und nach einem Fehler oder einer Entscheidung.

Die Auswahl ist mehrfachmarkierbar. Daniel kann also beispielsweise Terminal 2,
Codex, Gemini und eine bestimmte Browserfläche gemeinsam festhalten, ohne
andere offene Programme in die Kapsel zu ziehen.

## Bedeutungen und Lernrichtungen

Kategorien sind Tags, keine starren Zustände. Mehrere Tags dürfen gleichzeitig
gelten. Neben `Idee`, `Verwirrung`, `Fehler` und `Lösung` gehören mindestens
diese Richtungen in den freien Tag-Raum:

- `Umweg` — der Weg war schmutzig, aber lehrreich.
- `Beinahe` — knapp gescheitert oder gerade gerettet.
- `Überraschung` — etwas funktionierte oder erschien anders als erwartet.
- `Widerspruch` — Agenten oder Daniel bewerten denselben Moment verschieden.
- `Offene Frage` — festhalten, ohne sofort eine Antwort zu erzwingen.
- `Vergleich` — zwei Kapseln oder Zustände nebeneinanderlegen.
- `Zufallsfund` — eine unerwartete Entdeckung.
- `Übergabe` — ein sauberer Haltepunkt für eine andere Person oder Instanz.
- `Hypothese`, `Beweis`, `Gegenbeweis`, `Blocker`, `Entscheidung`, `Rückfall`,
  `wiederverwendbar` und `verworfen`.

Die ursprüngliche Kapsel wird nicht nachträglich überschrieben. Spätere
Interpretationen, Zeichnungen, Gegenargumente und neue Lösungen werden als
eigene Ebenen oder Folge-Kapseln angehängt. So bleiben Fehler und Umwege
sichtbar, statt im fertigen Ergebnis zu verschwinden.

## Hauhaucs als wählbare Beobachter-Session

Die vorhandene Dolphin-/Hauhaucs-Chatlogik ist die Referenz für den optionalen
Beobachter. Hauhaucs bekommt eine eigene Session mit leerem Basis-Systemprompt.
Daniel gibt ihm bei Bedarf selbst den Auftrag, etwa:

> „Achte ab jetzt auf Codex und Gemini. Lies mit und dokumentiere erst, wenn ich
> es sage.“

Die Bridge zeichnet Ereignisse zunächst skriptbasiert auf. Das ist der
verlässliche Teil: Zeit, Quelle, Agent, Session, Ziel, Terminal, Tool, Ergebnis,
Nachricht, Kapsel und Status werden ohne Modellaufruf gesammelt. Hauhaucs kann
danach oder portionsweise lesen, Zusammenhänge erkennen und eine Dokumentation
schreiben. Dadurch kostet das reine Aufzeichnen keine Modelltokens.

Die Beobachtung ist als eigene Hauhaucs-Session steuerbar:

- Beobachtung starten und stoppen.
- Zwei oder drei Agenten gleichzeitig auswählen.
- Nur Text-/Terminalereignisse lesen; Bildzugriff separat zuschalten.
- Kontextfüllstand und tatsächliche gelesene Ereignisse anzeigen.
- Kontext vollständig leeren, halbieren, einzelne Nachrichten auswählen,
  Nachrichten bearbeiten oder Sätze entfernen.
- Text und mehrere Markdown-/Textdateien einspeisen.
- Zusatzfelder, Feedback für den nächsten Output, Zeichenlimit und Tokenlimit
  selbst setzen.
- Session speichern, benennen, archivieren, exportieren oder als flüchtige
  Beobachtungssession führen.
- Am Ende „jetzt dokumentieren“ auslösen und die Kapselverweise beibehalten.

Die vorhandenen Dolphin-Bedienmöglichkeiten müssen bei einer Integration
erhalten bleiben. Insbesondere darf ein gespeicherter Kontext-Trim nicht nur
als ungenaue Anzahl am Anfang des Verlaufs abgelegt werden, wenn Daniel
einzelne Nachrichten oder Sätze ausgewählt hat. Die Bridge braucht dafür eine
explizite Ereignisliste oder Nachrichten-ID-Liste.

## Zeichen- und Textschicht

Über jedem gebundenen Gate können Daniel und berechtigte Agenten dauerhaft
zeichnen und schreiben:

- Freihandstift, Marker, Farben und Strichstärken.
- Linien, Pfeile, Rechtecke, Kreise und weitere schnelle geometrische Formen.
- Textmodus per Klick; Textobjekte bleiben verschiebbar und bearbeitbar.
- Verschieben, Skalieren, Gruppieren, Sichtbarkeit, Reihenfolge und
  Rückgängig/Wiederholen.
- Mehrfachmarkierung und gemeinsames Speichern in einer Momentkapsel.

Die Markierung haftet an dem Raum, an den der Agent oder das Ziel gebunden ist,
und bleibt darin frei verschiebbar. Zusätzlich braucht jedes Objekt eine
Bindungsart: Bildschirm, Fenster, Inhalt, Agent oder Kapsel. Ein Kreis um einen
Browserbutton kann mit dem Inhalt mitwandern; eine Notiz am Fensterrand bleibt
am Fenster. Wenn Inhaltserkennung nicht sicher ist, bleibt die Markierung an
der bekannten Zielgeometrie und meldet ihre Unsicherheit.

## Agenten und Orchestrierung

Eine Codex-Instanz bleibt an ihre laufende VPS-CLI-Session gebunden. Das
Overlay kann mehrere Darstellungen oder Anker derselben Session zeigen. Claude,
Gemini und Hauhaucs können daneben eigene Sessions besitzen. Subagenten werden
als Kinder ihrer startenden Session geführt: Auftrag, Herkunft, Ziel, Status,
Ergebnis, Sichtbarkeit und Lebensdauer sind nachvollziehbar.

Daniel kann einzelne Agenten, Gruppen oder ganze Agentenbäume beobachten,
markieren, ansprechen, pausieren und — soweit die jeweilige Runtime es erlaubt —
beenden. Ein Agent kann auf KDE-Desktop 2 arbeiten, während seine Raute auf
Windows sichtbar ist und ein Spruch nur an einen ausgewählten Empfänger geht.

## Baufolge

1. Wortlaut sichern und Quellen festhalten. Dieser Schritt ist mit den beiden
   Exportdateien erledigt.
2. Datenmodell für Ereignisse, Agenten-Sessions, Ziele, Bindungen,
   Markierungen und Momentkapseln definieren.
3. Skriptbasierte Aufzeichnung und Kapselung bauen, zunächst ohne Hauhaucs.
4. Kapsel öffnen, Zeitlinie, Mehrfachauswahl, Annotationen und neue Folge-
   Kapsel per sichtbarem Beleg prüfen.
5. Eine leere Hauhaucs-Chat-Session als optionalen Beobachter anschließen.
6. Kontextanzeige, Lesen, Bereinigen, Einspeisen, Promptfelder und Export
   anhand der Dolphin-Funktionen prüfen.
7. Windows-EXE bauen, auf Daniels Windows starten und über die Bridge anmelden.
8. Erst nach dem echten Handshake mit dem laufenden Programm weiterbauen:
   Bild hin und zurück, Text hin und zurück, Kapsel anlegen und wieder öffnen.
9. Danach Zielbindung, Rauten-Chat, Zeichenwerkzeuge, Text-/Bildobjekte,
   Terminal-Parität, Subagent-Orchestrierung und kontrollierte Eingabe einzeln
   ergänzen.

## Erster echter Abnahmepunkt

Daniel startet die EXE auf Windows. Die EXE meldet eine eigene Session am VPS
an. Codex sieht einen ausdrücklich freigegebenen Frame und seine Nachricht
erscheint im Overlay. Daniel antwortet. Beide Nachrichten, der Frame, die
Zielbindung und die Ereignisse werden in einer Momentkapsel gespeichert und
später gemeinsam wieder geöffnet.

Bis dieser Ablauf auf dem echten Windows-Programm funktioniert, ist die Bridge
noch kein gemeinsam benutzbarer Körper. Browser-Tests und lokale Modelle können
den Protokollkern vorbereiten, ersetzen diesen Abnahmepunkt aber nicht.
