# Mobil-Durchgang, Teil 2: zwei echte Bugs im Betriebssystem-Overlay

Weiter im Mobil-Auftrag, diesmal Plan/Canvas/Sketch-Werkstatt bei 375px geprueft.

Plan- und Canvas-Ansicht (native App) sehen mobil bereits gut aus: Kanban-Spalten und Node-Graph nutzen erwartbares horizontales Scrollen/Wischen, keine Ueberlappung.

Zwei echte Bugs im eigenen Betriebssystem-Overlay (operating_shell.js) gefunden, beide seit dem urspruenglichen Bau nie aufgefallen, weil bisher nie bei echter Mobilbreite getestet:

1. Die mobilen Layout-Regeln (@media max-width:760px) zielten auf ".gkos[data-mobile=...]" - ein Klassen-Selektor. Das Shell-Element traegt aber nur id="gkos" und class="open", nie class="gkos". Die Selektoren haben dadurch NIE gegriffen - die komplette mobile Bottom-Navigation (Ort/Koerper/Werkzeuge) hat rein optisch nichts umgeschaltet, obwohl der JS-Zustand (dataset.mobile) korrekt gesetzt wurde. Fix: #gkos[data-mobile=...] statt .gkos[data-mobile=...].

2. Die Sketch-Zeichenflaeche hatte height="520" als festes Attribut, unabhaengig von der Breite. Bei 302px Breite (Handy) fuehrte das Seitenverhaeltnis 900:520 zu ueber 50% leerem Rand oben/unten. Fix: aspect-ratio:900/520 mit height:auto in CSS. svgPoint() liest die tatsaechliche gerenderte Hoehe aus, die Koordinatenumrechnung fuers Zeichnen blieb dadurch korrekt - live per simuliertem Touch-Drag verifiziert (Geometrie im gespeicherten Element proportional richtig).

Technische Randnotiz: das CDP-Screenshot-Tool selbst geriet in diesem mobilen Emulationsmodus zeitweise in einen Zustand, in dem es wiederholt denselben (alten) Frame lieferte, unabhaengig vom echten Seitenzustand (per MD5-Hash bestaetigt identisch trotz echter DOM-Aenderung). Ein kurzer Breiten-Wechsel (376px -> 375px, kurze Pause) oder ein voller Seiten-Reload hat das wieder geloest. Kein App-Bug, reine Eigenart des Test-Werkzeugs in dieser Sitzung.

Beide Fixes committet. Objektlisten-Test-Nebeneffekt (ein Sketch-Testelement aus dem Touch-Funktionstest) bewusst nicht geloescht, gleiche Behandlung wie fruehere Sketch-Testelemente.
