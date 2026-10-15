# Prüfliste für Daniel — Version 0.9.1-g02 (Zeichnen erweitert, Bild-Element)

Ersetzt den Zeichen-Teil (Abschnitt 2) der Liste 0.9.0; alles andere aus 0.8.0 und 0.9.0 gilt weiter. Nur auf dem VPS und unter Wine geprüft, nativ noch nicht.

## 0. Vorbereitung
- [ ] `C:\Bridge\bridge_wechseln.bat` → `C:\Bridge\v091`, `--version` zeigt `0.9.1-g02`.

## 1. Leiste und Werkzeuge
- [ ] „Zeichnen im Ziel …“: Die Leiste zeigt vor jedem Werkzeug ein kleines **Symbol** (Zeiger, T, Zickzack, gelber Balken, Linie, Pfeil, Rechteck, Kreis, Radierer).
- [ ] **Radierer:** über Gemaltes ziehen: berührte Objekte bekommen einen roten Rahmen und verschwinden **beim Loslassen**. Ein Strg+Z holt alle zurück.
- [ ] **Wahl** (Markieren): Klick, Umschalt-Klick, Gummiband; ziehen, an den Ecken größer/kleiner, Entf löscht. Die Knöpfe „Größer“ / „Kleiner“ ändern die Auswahl um ein Viertel.
- [ ] **Marker** malt einen durchscheinenden Textmarker-Strich.
- [ ] Dritte Zeile: **F K U** (fett, kursiv, unterstrichen), **A− A+** (Schriftgröße), **100 / 75 / 50 / 25 %** Deckkraft. Der aktive Zustand leuchtet.

## 2. Text
- [ ] Vor dem Schreiben F/K/U und Größe einstellen, dann Text schreiben (Klick, tippen, Enter): so steht er da.
- [ ] Schon geschriebenen Text wählen und F/K/U, A−/A+ drücken: er ändert sich sofort. Doppelklick bearbeitet den Inhalt, Strg+Z macht jede Stilwahl rückgängig.

## 3. Rechtsklick (mit Bedientaste Strg+Alt, wie bei allen Bridge-Elementen)
- [ ] Rechtsklick **ohne** Bedientaste in der Zeichenfläche tut nichts außer einem gelben Hinweis oben links. Mit gehaltener Bedientaste: Rechtsklick **auf ein Objekt** wählt es und zeigt: Löschen, Doppeln, Größer, Kleiner, Strich dicker/dünner, Deckkraft 100/75/50/25, (bei Text:) Fett, Kursiv, Unterstrichen, Schrift größer/kleiner, Farbe, Nach vorn/hinten, Ausblenden. Der aktuelle Zustand ist angehakt.
- [ ] Jeder Punkt wirkt; auch bei **gemalten** Sachen (Deckkraft, größer, Strichdicke).
- [ ] Rechtsklick auf **leere Fläche**: „Voreinstellung für neue Objekte“ (Deckkraft, Fett/Kursiv/Unterstrichen, Schrift, Farbe): gilt für alles, was danach entsteht.

## 4. Ziel wählen
- [ ] „Ziel …“ in der Leiste: Liste mit „Ganzer Desktop“ und allen offenen Fenstern. Auswahl: Der Editor springt auf dieses Fenster, auch wenn dort noch kein Agent gebunden ist. Objekte bleiben im Fenster und kommen nach Neustart zurück, wenn dasselbe Programm wieder gewählt wird.
- [ ] „Sichtbar für …“ listet auch dann alle Agenten, wenn im Ziel noch niemand sitzt.

## 5. Bild einblenden (schwebendes Element, neben „Bilddatei senden“, das bleibt)
- [ ] Raute-Menü → „Bild einblenden …“: Datei wählen. Das Bild steht **sofort als eigenes Fenster** im Ziel (kein Zeichenmodus nötig), mit schmalem Kopf oben (Name und Prozent-Knopf; ein X zum Ausblenden gibt es bewusst nicht, das steht nur im Rechtsklick-Menü).
- [ ] **Verschieben** am Kopf, **Größe** an den Kanten und Ecken (das Seitenverhältnis des Bildes rastet nach dem Loslassen wieder ein).
- [ ] **Transparenz:** Prozent-Knopf schaltet weiter, Mausrad über dem Bild in 5-%-Schritten.
- [ ] **Rechtsklick mit Bedientaste** auf das Bild: Menü mit „Auf meinem Bildschirm“, „Nur im Bild von …“ (jeden Agenten einzeln, also auch mehrere), Deckkraft 100/75/50/25, Ausblenden, Entfernen.
- [ ] Mit „Nur im Bild von Agent A“ und „Auf meinem Bildschirm“ aus: Das Bild verschwindet bei dir (oder bleibt nur, wenn Windows das Fenster aus der Aufnahme ausnimmt: der Selbsttest sagt es), Agent A sieht es in seinem Bild, ein anderer Agent nicht.
- [ ] Gate-Fenster (z. B. Browser) verschieben, verkleinern: das Bild geht mit; minimieren: weg; wiederherstellen: wieder da; schließen: weg.
- [ ] Bridge neu starten, dasselbe Programm wieder binden: das Bild steht an derselben Stelle, in derselben Größe und Deckkraft.
- [ ] Zeichenmodus öffnen: Das Bild ist dort mit sichtbar und auswählbar (Strg+Z macht auch Verschieben und Größe des Bildes rückgängig). Während der Zeichenmodus offen ist, ruht das schwebende Fenster.
- Ausgeblendete Bilder holst du über den Zeichenmodus („Alle ein“) zurück.

## Nicht gebaut
- Zeichnen auf KDE 1/2 (G06), Export, Replay, Mikrofon.
