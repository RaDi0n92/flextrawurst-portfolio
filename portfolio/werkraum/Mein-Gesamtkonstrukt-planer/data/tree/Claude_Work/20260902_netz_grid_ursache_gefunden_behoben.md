# Netz mobil: Ursache der leeren Flaeche gefunden und behoben

Weiter am Netz-Fund von eben.

Ursache gefunden: main.app-shell ist display:grid mit nativ nur 2 Zeilen (auto minmax(0,1fr)) fuer 2 Kinder (Header, Inhalt). Die eigene #hs-bar-Leiste wird als drittes Kind eingefuegt und landete dadurch automatisch in der flexiblen 1fr-Zeile - die nahm bei 375px Breite den gesamten freien Platz (341px), waehrend der eigentliche Netz-Inhalt in eine implizite Zeile danach rutschte. Der fruehere align-self:start-Fix (vorherige Notiz) positionierte die Leiste nur oben in dieser ueberdimensionierten Zeile, ohne die Zeile selbst zu verkleinern - deshalb blieb die Luecke trotzdem.

Der native Bundle hat fuer genau diesen Fall bereits eine passende Klasse: .app-shell.has-notice mit 3 expliziten Zeilen (auto auto minmax(0,1fr)) fuer Header, Zusatzleiste, Inhalt. Fix: has-notice wird jetzt beim Einfuegen der Leiste automatisch gesetzt, main.app-shell nutzt damit die eigene, bereits vorgesehene 3-Zeilen-Logik statt der 2-Zeilen-Logik mit ungeplantem drittem Kind. Live verifiziert bei 375px (Luecke weg, Kompatibilitaetsansicht mit 51 Objekten/44 Kanten sichtbar) und bei 1297px (Desktop unveraendert korrekt).

Korrektur zur vorherigen Notiz: die dort geaeusserte Vermutung, die leere Flaeche haenge mit der fehlenden /dev/dri-Infrastruktur und WebGL zusammen, war falsch. Die App zeigt ihre eigene WebGL-Kompatibilitaetsmeldung ("WebGL ist auf diesem Geraet nicht verfuegbar. Gezeigt werden dieselben Objekte und Kanten.") ganz normal und funktionsfaehig an - sie war nur durch die zu grosse Grid-Zeile aus dem sichtbaren Bereich geschoben. Kein Infrastruktur-Thema, reiner Grid-Layout-Fehler durch die eigene Zusatzleiste.

Committet.
