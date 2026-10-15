# Mobil-Durchgang: Touch-Ziele korrigiert

Auftrag: "das ganze auch mobile machen, alles optimieren". Systematisch bei 375x812px getestet (per CDP Emulation.setDeviceMetricsOverride, mobile:true).

Gefunden und behoben: die gruppierten Toolbar-Knoepfe (Notiz hier, Start hier, Ordner & Dateien, Gemeinsame Arbeit, Betriebssystem, Telefon pruefen) waren durch unser kompaktes Gruppen-Padding auf 28px Hoehe geschrumpft. Zum Vergleich: alle nativen Knoepfe der App (Start/Canvas/Netz/..., Idee/Frage/Aufgabe, Stimmt so nicht/Uebergabe kopieren/Sicherung) sind durchgaengig 44px hoch - die App haelt sich selbst konsequent an die 44px-Touch-Zielgroesse, nur unsere eigene Gruppierung hat das an sechs Stellen unterschritten. Fix: ab 760px Breite (App-eigene Mobil-Schwelle) auf 44px Mindesthoehe angehoben, Desktop-Kompaktheit unveraendert.

Positiv: der Rest der mobilen Erfahrung war schon gut gebaut, nicht von uns:
- Kein horizontales Scrollen der Gesamtseite (bodyScrollWidth = window innerWidth exakt).
- Native Objektzeilen 49px hoch, bereits ueber dem Zielwert.
- Eigene Bottom-Navigation (Ort/Koerper/Werkzeuge im Betriebssystem-Overlay) mit 40px, nah genug am Zielwert.
- "Bestand/Buehne/Werkstatt"-Kacheln als eigene mobile Navigationsebene, foerdert die Objektliste sauber auf volle Breite - bereits vorher vorhanden.

Bestaetigt per direkter DOM-Messung (getBoundingClientRect, flexDirection): die Toolbar scrollt bei jeder Breite unter der Gesamtbreite ihrer Gruppen horizontal statt umzubrechen - konsistent mit flex-wrap:nowrap im Code, entspricht der beabsichtigten Loesung aus dem vorherigen Schritt.

Nach dem Fix erneut auf Absturzsicherheit geprueft (Suchfeld bei 375px) - kein Haenger.
