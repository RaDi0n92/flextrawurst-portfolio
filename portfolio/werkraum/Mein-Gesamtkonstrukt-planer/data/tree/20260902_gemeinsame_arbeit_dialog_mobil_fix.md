# Gemeinsame Arbeit selbst: Formular verdraengte Verlaufsliste

Zweiter Dialog nach Ordner & Dateien geprueft, aus dem gleichen Grund: staendig selbst benutzt, aber nie auf Mobile ueberprueft.

Bei 375px: .ps-body{grid-template-rows:auto 1fr} liess das Formular fast den gesamten verfuegbaren Platz nehmen (548px von 580px gemessen), die Verlaufsliste wurde auf 32px zusammengedrueckt - bei Dutzenden Eintraegen praktisch unbrauchbar, nur ein winziger Streifen sichtbar. Fix: beide Haelften bekommen gleich viel Platz per grid-template-rows:minmax(0,1fr) minmax(0,1fr) - je ~349px, beide einzeln scrollbar.

Beim Testen ist zusaetzlich ein Klick-Problem aufgefallen: bei dieser Breite ueberlappten Formular und Liste kurzzeitig (bevor der Fix griff), sodass ein Klick auf den "Spur auf VPS festhalten"-Knopf stattdessen die darunterliegende Liste traf. Nach dem Grid-Fix verschwindet das automatisch, da beide Bereiche nicht mehr overlappen.

Zusaetzlich gefunden: horizontales Ueberlaufen in der Verlaufsliste bei mehreren aelteren Eintraegen, auch von anderen KI-Stroemen (Codex). Die "Datei oeffnen: <Pfad>"-Buttons (.ps-links) hatten kein Flex-Wrap und keinen Wortumbruch fuer lange Pfade ohne Leerzeichen; ebenso der Spur-Text selbst, wenn er einen langen Pfad enthielt. Beide bekommen overflow-wrap:break-word, .ps-links zusaetzlich display:flex;flex-wrap:wrap.

Live verifiziert bei 375px: Formular/Liste exakt haelftig, kein horizontales Scrollen mehr (vorher scrollWidth 518 vs clientWidth 359, jetzt 359=359). Bei 1297px Desktop unveraendert korrekt.

Randnotiz zur eigenen Arbeitsweise: bei diesem Schritt mehrfach falsche Koordinaten aus dem Augenschein des Screenshots abgeleitet (Screenshot-Darstellung entspricht offenbar nicht 1:1 den echten CSS-Pixel-Koordinaten). Ab jetzt Koordinaten fuer Klicks/Eingaben immer per getBoundingClientRect() aus dem DOM abfragen statt aus dem Bild zu schaetzen.

Committet.
