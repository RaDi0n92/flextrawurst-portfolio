# Zweiter Fund nach dem Header-Fix: Werkzeugleiste ueberlappte den Header

Nach dem Header-Fix (max. 2 Zeilen) systematisch weitergemessen ueber acht Breiten, um zu pruefen ob noch andere Bereiche dieselbe "Luecke zwischen Breakpoints" haben wie der Header.

Fund: .stage-buttons (Kante setzen / Ablauf vorschlagen / Marker / Malen & markieren / Begriffe & Farben, im Canvas/Werkstatt-Bereich) hat exakt dieselbe Luecke wie der Header hatte - zwischen der breiten Desktop-Regel und der nativen <760px-Mobil-Regel (die bereits eine eigene nowrap+scroll-Behandlung hat) wrappt die Buttonreihe bei ca. 800-950px auf mehrere Zeilen und ragt dabei SICHTBAR ueber ihre eigene .stage-actions-Zelle hinaus - bis in den Header hinein. Live per Screenshot bestaetigt: die "+ Idee"/"+ Frage"-Buttons schwebten sichtbar ueber der Schnellerfassungsleiste, ein echter, verwirrender visueller Bug, nicht nur eine Flaechen-Ineffizienz.

Gleicher Fix wie beim Header/top-actions: .stage-buttons bekommt dauerhaft flex-wrap:nowrap + overflow-x:auto statt nur unterhalb 760px, branch-control (das "ARBEITSVARIANTE"-Eingabefeld) bekommt min-width:0 zum Schrumpfen, .stage-actions selbst min-width:0 als Flex-Kind.

Live verifiziert bei 900px: stage-buttons vorher bei y:123-246 (Ueberlauf von ueber 30px in beide Richtungen ueber die Zellengrenzen y:156-214 hinaus), jetzt vollstaendig innerhalb der eigenen Zelle, Scrollbalken statt Umbruch, kein Overlap mehr. Bei 375px unveraendert korrekt (native Mobil-Regel griff dort schon vorher). Bei 1297px unveraendert korrekt.

Committet.
