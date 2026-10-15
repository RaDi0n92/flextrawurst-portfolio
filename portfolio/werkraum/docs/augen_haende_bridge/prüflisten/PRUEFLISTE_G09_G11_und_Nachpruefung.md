# Prüfliste G09 bis G11 und Ergebnisse der Nachrecherche (nativ, von Daniel)

Zustand: Stand 2026-10-02, noch **kein** Paket 0.10.0 gebaut. Alles hier ist auf dem VPS (Xvfb/Wine) belegt und nativ **offen**. Abhaken nur nach echtem Versuch.

## Neue Bauschritte aus der Nachrecherche (noch zu bauen)
- [ ] **R2 Windows.Graphics.Capture** für Spiele und DirectX-Fenster, wo `PrintWindow` schwarz bleibt. Nur auf Daniels Windows prüfbar.
- [ ] **R4 XInput2** für die Übernahme-Erkennung unter X11 (statt Zählung). Danach Wiederholungsläufe wie bisher.
- [ ] **Wayland-Körper** (libei/Portal + PipeWire), nur falls ein Linux-Gerät mit Wayland dazukommt. Die KDE-Desktops der Bridge sind Xvfb/X11.

## Nativ zu prüfen: bereits gebaut
- [ ] R3: Tippen und Hotkey in ein Fenster, das nicht vorn steht (Windows verweigert den Vordergrundwechsel oft). Klappt es, steht der Text im Fenster?
- [ ] G10 Hände unter Windows: Klick, Doppelklick, Ziehen, Tippen mit Umlauten, Strg+S, Mausrad in einem echten Programm (Notepad, Browser). Zeigerposition stimmt bei 125 % und 150 % Skalierung?
- [ ] G10 Not-Aus: F12 mitten im Ziehen; danach nichts gedrückt (Strg, Umschalt, linke Maustaste).
- [ ] G10 Übernahme: eigene Maus bewegen, während ein Agent zieht; die Hände halten an. Menüpunkt „Meine Eingabe unterbricht die Hände nicht“ an: sie laufen weiter, F12 stoppt trotzdem.
- [ ] G10 Steuerprofil im Raute-Menü wechseln (hintergrund, geteilte_maus, controller, hybrid); „hintergrund“ lehnt Klicks ab.
- [ ] G09 Menü „pausieren/fortsetzen“: Agent hält an, Anzeige „pausiert“, Fortsetzen arbeitet Eingaben ab; Beenden eines pausierten Agenten.
- [ ] G09 `bridge_cli agenten/gruppe/sende/auftrag` zwischen zwei echten Agenten (Codex, Claude) in vd1.
- [ ] G11 `bridge_cli weltdom` auf einem echten Chromium (mit `--remote-debugging-port=9222`): Knoten, Rücklese bei `knoten … klick`.
- [ ] G11 Zeigen (`zeige X Y`) zeigt ein Zeichen auf dem Bildschirm; `--einfuegen` klickt wirklich; nach Fenstergrößenänderung warnt die Geste.
- [ ] Docker-Orte (vd1/vd2): Pause/Fortsetzen eines Agenten im Container.
- [ ] Claude hinter dem Ordner-Vertrauensdialog: kommt getippter Text an? Kimi und GLM auf dem Host starten und tippen.

## Bewusst nicht in dieser Liste
- Virtuelle Controller (Treiber nur nach Daniels Wort), ChatGPT-Slice (G06.5) und Mikrofon (zurückgestellt).
