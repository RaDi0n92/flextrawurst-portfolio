# Topbar wurde von geoeffneten Fenstern verdeckt - Buttons nicht mehr klickbar

Live mit echten Playwright-Klicks (CDP, kein Befehlsaufruf-Ersatz) auf einem kleineren
Viewport (1243x556) getestet: "Ordner & Dateien" geoeffnet, danach versucht "Gemeinsame
Arbeit" zu klicken - der Klick landete nicht auf dem Topbar-Button, sondern auf der
Titelleiste des bereits offenen Fensters.

Ursache mit `document.elementFromPoint()` am Button-Mittelpunkt bestaetigt (nicht nur
vermutet): `HEADER.gkw-titlebar` statt des Buttons selbst. `workspace.js`s
Fenster-Clamping (`open()`, Zeile ~60-65) begrenzte den Fenster-Top nur nach unten
(`maxTop`), reservierte aber keinen Mindestabstand von oben - auf niedrigen Viewports
rutschte das geklemmte Fenster (`top: 47.6px`) unter die 82px hohe Topbar-Zeile und
verdeckte deren untere Haelfte. Der Drag-Handler hatte dasselbe Problem
(`Math.max(nextTop, 0)` erlaubte Ziehen bis ganz nach oben).

Fix: neue Hilfsfunktion `reservedTop()` liest die tatsaechliche Topbar-Hoehe zur
Laufzeit aus (`.topbar`-Element, `getBoundingClientRect().bottom + 8`) statt eines
festen Werts - bleibt korrekt auch wenn die Topbar responsiv umbricht. `open()` klemmt
jetzt zwischen `minTop` und `maxTop`, der Drag-Handler nutzt denselben Wert als
Untergrenze (einmalig bei Drag-Start berechnet, nicht bei jedem `mousemove`).

Live nach Fix erneut verifiziert (Reload + beide Fenster nacheinander geoeffnet):
`elementFromPoint` trifft jetzt den echten Button (`BUTTON_ERREICHBAR`), Screenshot
zeigt beide Fenster gleichzeitig offen mit voll erreichbarer Topbar.

Nachtrag: den separaten Fund (zwei "Schliessen"-Buttons bei "Ordner & Dateien") auf
Zuruf ebenfalls behoben. Der innere `.pf-close`-Button im `.pf-header` war ein Rest aus
der Zeit vor Stufe 3, als das Panel noch ein eigenstaendiges Vollbild-Overlay ohne
GKWindows-Wrapper war - seit Stufe 3 oeffnet `ensurePanel()` das Panel ausschliesslich
ueber `window.GKWindows.open(...)`, das bereits eine eigene Titelleiste mit
Schliessen-Button liefert. Button, sein Klick-Handler und die zugehoerige
`margin-left:auto`-Regel entfernt. Live nach Reload verifiziert: `.pf-header` enthaelt
jetzt nur noch "Alles einklappen", die aeussere Titelleiste traegt weiterhin genau ein
"Schliessen".

## Zweiter Nachtrag — kompletter Regressionstest am Ende der Session

Auf Zuruf ("test die seite nochmal komplett im browser durch") alle Panels
gleichzeitig geoeffnet (Betriebssystem, Ordner & Dateien, Gemeinsame Arbeit) und
einzeln durchgeklickt. Dabei denselben doppelten-Schliessen-Button-Fehler auch bei
"Gemeinsame Arbeit" (`streams.js`) gefunden - exakt dasselbe Muster wie bei Ordner &
Dateien, gleiche Ursache (Rest aus der Zeit vor Stufe 3). `.ps-head`-Button, sein
Klick-Handler und die tote `margin-left:auto`-Regel entfernt. `operating_shell.js`
(Betriebssystem) geprueft und bewusst NICHT angefasst - sein einziger
"Schliessen"-Text gehoert zu einem Koerper-Editor-Abbrechen-Knopf, kein Duplikat.

Live verifiziert: `.ps-head` enthaelt jetzt keinen Button mehr, die aeussere
GKWindows-Titelleiste traegt genau ein "Schliessen". Formular-Absenden in Gemeinsame
Arbeit nach dem Fix erneut getestet (echter neuer Eintrag erscheint korrekt) - keine
Regression. Drei Fenster gleichzeitig offen (Betriebssystem + Ordner & Dateien +
Gemeinsame Arbeit): Topbar blieb durchgehend erreichbar, keine JS-Fehler in der
Konsole waehrend des ganzen Durchlaufs.
