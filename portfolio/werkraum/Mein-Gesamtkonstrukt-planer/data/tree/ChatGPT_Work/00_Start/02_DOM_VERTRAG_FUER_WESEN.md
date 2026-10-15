# DOM-Vertrag für Wesen

## Wozu

Die Oberfläche ist kein zweites Gedächtnis und keine Kulisse. Sie ist eine **lesbare DOM-Projektion** der realen VPS-Dateien, Objekt-IDs, Kanten, Ereignisse und Arbeitszustände.

Dateien und der kanonische Serverstand bleiben dauerhaft. DOM-Knoten machen diesen Bestand für Menschen, LLMs und Agenten auffindbar, bedienbar und überprüfbar.

## Grundsatz

Ein Inhalt gilt erst als DOM-fähig, wenn er zugleich:

1. einen stabilen Ursprung besitzt: Datei, Objekt-ID, Kante, Ereignis oder Entwurf;
2. einen eindeutigen Typ und Zustand trägt;
3. einen sichtbaren Namen und eine menschliche Erklärung besitzt;
4. über stabile DOM-Attribute adressierbar ist;
5. wieder zur Quelle, zum Ereignis und zum nächsten Arbeitsschritt zurückführt.

DOM allein speichert nichts dauerhaft. Jede Änderung läuft: **Nutzerhandlung → Server-Commit → Datei/Objekt/Kante/Ereignis → DOM-Refresh → Reload-Gegenbeweis**.

## DOM-Identitäten

Für jeden gerenderten Arbeitsbestand werden diese Bedeutungen benutzt:

- `data-gk-kind`: `file`, `folder`, `object`, `edge`, `event`, `feedback`, `tool`, `draft`.
- `data-gk-id`: stabile Objekt-, Kanten-, Ereignis- oder Feedback-ID.
- `data-gk-path`: relativer VPS-Pfad einer Datei oder eines Ordners.
- `data-gk-source`: Herkunft, etwa `werkraum://…`, `manual://…` oder `imported://…`.
- `data-gk-state`: Realitäts-, Beleg- und Arbeitsstatus; nie als ein vermischtes Wort.
- `data-gk-context`: aktuell gewählte Wurzel/Pfad/Objekt.
- `data-gk-action`: erlaubte bewusste Handlung, z. B. `open`, `edit`, `adopt`, `link`, `run`, `review`.

Ein visueller Pfeil ist keine Kante, solange kein `data-gk-id` mit Typ, Grund und Herkunft auf eine reale Kante verweist.

## Arbeitsweg für Wesen

1. Lies `00_Start/00_MEIN_GESAMTKONSTRUKT_PLANER_BAUAUFTRAG.md` und prüfe den sichtbaren `ARBEITSKONTEXT`.
2. Suche zuerst DOM-Knoten über Typ, ID, Pfad und Zustand – nicht über geratenen Text.
3. Öffne die Quelle, bevor du ihre Bedeutung veränderst.
4. Nimm nur eine erlaubte Handlung vor. Ein Entwurf bleibt Entwurf, bis er bewusst übernommen wird.
5. Nach einer Änderung prüfe den sichtbaren DOM-Zustand und einen Reload.
6. Hinterlasse eine Spur mit Ursprung, Änderung, Test, Grenze und nächster Verbindung.
7. Bei Konflikt, fehlender Herkunft oder unklarer Freigabe: nicht überschreiben; als Frage oder Vorschlag ablegen.

## Werkzeugregel

Start, Canvas, Netz, Plan, Zeitspur und jede Replica arbeiten auf `data-gk-context`. Sie dürfen den gewählten Bestand anders bearbeiten, aber nicht still auf den globalen Standard zurückfallen.

Eine Replica ist nur echt, wenn sie eigene Kernhandlungen, Eingänge, Ergebnisse und Übergaben als DOM-Knoten sichtbar macht und das Ergebnis wieder in Dateien/Objekten/Ereignissen verankert.

## Prüffragen

- Kann ein Mensch sehen, was dieser Knoten ist, woher er kommt und was er ändern darf?
- Kann ein Wesen die Quelle öffnen, ohne den Pfad zu raten?
- Überlebt der Zusammenhang einen Reload?
- Kann ein anderer Arbeitsraum das Ergebnis benutzen?
- Ist ein Fehlerweg, Konflikt oder Entwurf als Zustand sichtbar statt verschwunden?

## Belegter Stand · 2026-08-23

Umgesetzt und im VPS-Desktop mit Reload geprüft:

- Der Ordnerbaum ist als `Arbeitsraum` markiert. Das Dokument `00_Start/00_MEIN_GESAMTKONSTRUKT.md` bleibt ein eigener oberster Arbeitskörper; es ist nicht der Name des Containers.
- Werkzeugschalter tragen `data-gk-kind="tool"` und ihren aktuellen Kontext.
- Datei- und Ordnerknoten tragen `data-gk-kind="workspace-file"`, `data-gk-source="werkraum://…"` und `data-gk-context`.
- Eindeutig auflösbare Canvas-/Objektknoten erhalten `data-gk-id` und `data-gk-source`. Mehrdeutige Titel werden ausdrücklich als nicht aufgelöst markiert, statt eine ID zu erfinden.
- `Notiz hier` erzeugt aus dem sichtbaren Kontext eine echte Markdown-Datei, einen Dokument-Knoten und eine begründete Kante. Der Server kann das Ziel über `targetSourcePath` auflösen, nicht nur über einen angezeigten Titel.
- `Arbeitsobjekt aktualisieren` zieht eine bewusst bearbeitete Quelle wieder in ihren bestehenden Dokument-Knoten. Damit werden Datei und übernommenes Objekt nicht still zwei widersprüchliche Texte.
- Wird eine übernommene Datei im Arbeitsraum gewählt, aktiviert der Browser ihr Objekt über die stabile `werkraum://`-Quelle. Start, Canvas, Netz, Plan, Zeitspur und Replicas erhalten damit dieselbe aktuelle Auswahl, statt still zum Projektstandard zurückzuspringen.

Noch nicht behauptet: Alle Renderflächen, alle Kanten, alle Feedbackmarkierungen und jede Replica besitzen bereits vollständige stabile DOM-Identitäten. Der nächste Baupunkt ist die echte Kontextbindung von Canvas und Kanten über diese IDs/Quellen.
