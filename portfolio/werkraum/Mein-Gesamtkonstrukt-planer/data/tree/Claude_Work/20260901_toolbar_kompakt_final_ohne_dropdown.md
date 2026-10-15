# Toolbar final: kompakt, sicher, kein Dropdown

Daniel meldete nach dem align-self:start-Fix zwei weitere Punkte: (1) beim Verkleinern tauchen Dinge auf, die bei voller Breite nicht sichtbar sind, (2) generell nehmen Menues/Buttons zu viel Arbeitsflaeche weg. Beides ernst genommen und mit echten Screenshots bei mehreren Breiten (1297/950/850/761/760/650/600/500px) nachvollzogen.

Messung: die gewachsene (umgebrochene) Kopfzeile fraß bei 800px Fensterhoehe 25% der Bildschirmhoehe (199px von 800px) - deutlich zu viel.

Versuch, das mit einem "Mehr"-Dropdown zu loesen (ueberzaehlige Gruppen wandern in ein schwebendes Panel): funktionierte optisch, aber die verschobenen Knoepfe reagierten nicht mehr auf Klicks. Vermutete Ursache: Interferenz mit Reacts Event-Handling bei aus dem urspruenglichen Elternzweig verschobenen Knoten (aehnliche Fehlerklasse wie beim fruehreren Objektlisten-Crash, diesmal ohne Absturz, nur stumme Unfunktionalitaet). Versuch, das Panel innerhalb von #root statt document.body zu haengen, hat das Problem NICHT behoben - die genaue Ursache blieb ungeklaert. Wegen des Risikos verworfen.

Endgueltige Loesung: Gruppen bleiben immer an ihrer normalen Position in .top-actions, werden nie in ein externes Element verschoben. Kopfzeile bleibt einzeilig (Originalhoehe ~82px statt 199px), Gruppen-Padding und Schrift verkleinert (mehr passt ohne Scrollen). Bei echtem Platzmangel scrollt die Leiste horizontal mit Fade-Hinweis - kein hartes Abschneiden, aber auch kein Wachstum der Kopfzeile, das mit der bestehenden vierten Arbeitskontext-Zeile im Header kollidieren koennte.

Live getestet bei 1297px (kein Scrollen noetig durch kompaktere Masse), 600px (App wechselt nativ in einspaltige Mobil-Ansicht, keine Ueberlappung), erneuter Suchfeld-Crashtest (kein Haenger).

Nebenbei geklaert: ein vermeintlicher Klick-Bug bei "Stimmt so nicht" war kein echter Fehler, sondern eine zu fruehe Zustandspruefung meinerseits direkt nach dem synthetischen Klick, bevor React neu gerendert hatte (bestaetigt durch ein versehentlich ausgeloestes Feedback-Formular fuer einen anderen Knopf, waehrend der Flag-Modus noch aktiv war).

Kopfzeile nimmt jetzt wieder ungefaehr so viel Platz wie vor dem Umdekorieren ein, nur mit Gruppierung statt Chaos.
