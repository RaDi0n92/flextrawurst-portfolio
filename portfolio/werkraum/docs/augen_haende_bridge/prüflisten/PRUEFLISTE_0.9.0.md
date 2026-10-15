# Prüfliste für Daniel — Version 0.9.0-g02 (G07 Rest, R020, G08 Windows)

Zusätzlich zu `PRUEFLISTE_0.8.0.md` (die gilt weiter). Alles nur auf dem VPS und unter Wine geprüft, nativ noch nicht.

## 0. Vorbereitung
- [ ] Tunnel auf, `C:\Bridge\bridge_wechseln.bat`: packt nach `C:\Bridge\v090` aus (ZIP und Datei liegen schon in `C:\Bridge`), startet die Bridge. `--version` zeigt `0.9.0-g02`.
- [ ] Selbsttest (`selbsttest.bat`): Zeile „Bridge-Fenster lassen sich aus der Aufnahme ausnehmen“ — bitte den Bericht schicken (wichtig für G08: davon hängt ab, ob der Editor Privates zeigen darf).

## 1. R020 und Bildfolge
- [ ] Zwei Agenten starten. Raute-Menü → „Terminal-Platz tauschen …“ → anderen Agenten wählen: Die Terminals tauschen Ort und Größe; Namen und Farben bleiben. Nochmal tauschen: wie vorher.
- [ ] Raute-Menü → „Bildfolge (Ordner) an den Agenten …“: ein Bild in einem Ordner mit mehreren Bildern wählen. Der Agent bekommt sie nacheinander (alle 2 s); Menü zeigt „läuft (n/m)“; Pausieren, Fortsetzen, Stoppen gehen. „Nur Terminal“ oder F12 stoppt die Folge.

## 2. G08 — Zeichnen (am besten mit einem gebundenen Browserfenster, dann nochmal mit dem ganzen Desktop)
- [ ] Browser binden (Scanner). Raute-Menü (oder Regie) → „Zeichnen im Ziel …“: Auf dem Browserfenster liegt eine leicht abgedunkelte Fläche mit farbigem Rand, darüber/daneben die Werkzeugleiste.
- [ ] **Stift, Marker, Linie, Pfeil, Rechteck, Kreis** nacheinander zeichnen (Bedientaste ist hier nicht nötig). Farbe und Stärke wechseln.
- [ ] **Text:** Werkzeug „Text“, klicken, tippen, **Enter**: Text steht da. Doppelklick auf den Text (Werkzeug „Wahl“): bearbeiten; leer machen löscht ihn.
- [ ] **Bild …:** eine Bilddatei einfügen; sie erscheint in der Mitte, auswählbar und skalierbar.
- [ ] **Wahl:** Klick wählt, Umschalt-Klick fügt hinzu, Gummiband wählt mehrere; Ziehen verschiebt; Ecke ziehen ändert die Größe; Entf löscht; Strg+D doppelt; Strg+G gruppiert, Strg+Umschalt+G trennt; Bild hoch/runter ändert die Reihenfolge.
- [ ] **Strg+Z / Strg+Y** (und „Rückg.“ / „Wied.“) gehen Schritt für Schritt zurück und wieder vor.
- [ ] **Esc:** beim Zeichnen bricht es nur den Strich ab; mehrfach gedrückt (nichts mehr zu tun) verlässt es den Zeichenmodus. „Fertig“ ebenso. Danach funktioniert das Programm darunter normal, kein Klick ist verloren gegangen.
- [ ] **Auf dem Bildschirm:** Nach „Fertig“ stehen die Objekte (Standard: auf dem Bildschirm) auf dem Browserfenster und sind durchklickbar (du kannst darunter klicken). Browserfenster verschieben/verkleinern: sie gehen mit; minimieren: weg; wiederherstellen: wieder da; schließen: weg.
- [ ] **Der Agent sieht es:** `bridge_cli see` (oder neues Bild) zeigt die Objekte im Bild des Agenten.
- [ ] **Nur für einen Agenten:** zwei Agenten am selben Ziel binden. Objekt auswählen → „Sichtbar für …“ → Haken bei „Auf meinem Bildschirm“ **weg**, „Nur im Bild von Agent A“ **an**. Das Objekt verschwindet von deinem Bildschirm (im Editor siehst du es blasser), Agent A sieht es in seinem Bild, **Agent B nicht**.
- [ ] **Neu starten:** Bridge beenden, `bridge_starten.bat`, dasselbe Programm wieder binden: die Objekte sind wieder da.
- [ ] **Ganzer Desktop:** Agent auf „Desktop“ binden, zeichnen: die Fläche liegt auf dem Desktop; Esc beendet.

## 3. Nicht gebaut (nicht prüfen)
- Zeichnen auf KDE 1/2 (gehört zu G06), Replay, Export, Mikrofon.
