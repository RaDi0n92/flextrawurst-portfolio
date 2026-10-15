---
datum: 2026-09-20
autor: codex bei Daniels VPS
herkunft: V3.1-Terminalkanal und echter isolierter PTY-Probeweg
status: V3.2 lokaler Zustandsreader belegt; vollständiger Renderer offen
---

# V3.2 — VT-Rücklese für denselben Terminalstrom

## Zweck

Der Terminalkanal liefert nicht nur eine Marker-Zeichenkette. Der rohe PTY-
Strom wird jetzt zusätzlich in einem expliziten VT-Zustand gelesen. Das ist
die erste technische Schicht für Cursor, Zeilen, SGR-Farbe, Alternate Screen,
Cursor-Sichtbarkeit und Resize.

Der Reader liegt unter
`/root/werkraum/augen_haende_bridge/src/augen_haende_bridge/terminal_renderer.py`.
Er ist absichtlich kein Anspruch auf vollständige Terminalemulation. Nicht
unterstützte Sequenzen bleiben als Zustand sichtbar und werden nicht als
erfolgreich verarbeitet ausgegeben.

## Nachgewiesene Teilmenge

- UTF-8-Ausgabe mit Ersatzzeichen bei ungültigen Bytes
- Text, `CR`, `LF`, Backspace und Tabulator
- Cursorpositionierung und relative Cursorbewegung
- `CSI J` / `CSI K` für sichtbares Löschen
- SGR-Parameter als Zustand
- `CSI ?25h/l` für Cursor-Sichtbarkeit
- `CSI ?1049h/l` für Primary-/Alternate-Screen-Trennung
- dimensioniertes Resize mit Erhalt sichtbarer Zellen
- sichtbare Liste nicht unterstützter Sequenzen

Die Proof-Surface zeigt den serialisierten VT-Zustand unter
`data-testid="terminal-renderer"`, nachdem der echte PTY-Probeweg gelaufen ist.

## Grenzen

Der Reader ersetzt weder einen etablierten vollständigen VT-Emulator noch die
native Konsole- oder spätere Windows-ConPTY-Präsentation. Scroll-Regions,
vollständige DEC-Modi, Hyperlinks, Mausprotokolle, Tastatur-Encoding und
Pixel-/Font-Rücklese bleiben offen. Genau deshalb ist
`unsupported_sequences` Teil des Ergebnisses.

## Nächster Schritt

Den Reader gegen reale Resize-/Cursor-/Alternate-Screen-Trajektorien erweitern,
danach einen Rendereradapter auswählen und erst dann den Kanal in den echten
Windows-EXE-Terminalkörper führen.
