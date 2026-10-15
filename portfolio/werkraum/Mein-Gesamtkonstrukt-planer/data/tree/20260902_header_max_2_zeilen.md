# Header bleibt bei jeder Breite maximal 2 Zeilen

Auf Daniels Beobachtung hin (Fenster gross/klein ziehen zeigt die Arbeitsflaeche schrumpft unverhaeltnismaessig) systematisch ueber acht Breiten gemessen (1400 bis 375px), nicht nur an den zwei Extremen.

Fund: header.topbar nutzt ein natives Grid mit hart codierten Mindestbreiten (minmax(330px,1.35fr) auto minmax(450px,1.2fr)). Sobald die Fensterbreite diese Minima nicht mehr erfuellt (~900-1300px), kippt das native Grid ohne Zwischenstufe von 1 Zeile auf 3 gestapelte Zeilen; unter der 760px-Schwelle (vorherige Mobil-Fixes dieser Sitzung) auf 4. Gemessen: Header-Hoehe 82px -> 152px -> 215px, Lesefl√§chen-Anteil (Arbeitsflaeche zu Gesamthoehe) 83.7% -> 75.0% -> 67.1% - waehrend gleichzeitig die Breite schrumpft, ein doppelter Verlust.

Frage an Daniel gestellt, wie der Header sich verhalten soll: seine Wahl war "Maximal 2 Zeilen immer, Rest scrollt seitlich". Umgesetzt in human_redesign.js: Zeile 1 = brand-block + view-switch (Logo/Titel + Tab-Navigation), Zeile 2 = top-actions + #planner-context-bar (Werkzeuggruppen + Arbeitskontext-Anzeige, mit fixem Platzanteil und Ellipsis fuer den Kontext-Text, top-actions nimmt den Rest mit eigenem horizontalen Scroll). Beide sind neue Wrapper-Divs; die vier verschobenen Elemente sind wie in den Kommentaren zu object-list begruendet dauerhaft gemountete, nie von React entfernte Strukturelemente - kein dynamisch gefilterter Inhalt wie object-list, daher unkritisch fuer einmaliges Verschieben.

Beim Umsetzen erneut derselbe Grid/Flex-Fallgrube begegnet wie beim Netz- und Ordner&Dateien-Fix zuvor in dieser Sitzung, hier als Flex-Variante: die Wrapper-Zeile mit top-actions wuchs auf ihre volle Inhaltsbreite (1735px bei 375px Fensterbreite!) statt sich zu beschraenken, weil sie als Flex-Item der jetzt Column-Flex-Kopfzeile min-width:0 UND width:100% brauchte, nicht nur eins von beiden.

Live verifiziert ueber alle acht Breiten: Header-Hoehe jetzt 82px -> 108px -> 151px, Lesefl√§chen-Anteil 83.7% -> 80.5% -> 75.1% - durchgehend besser, kein Drei- oder Vierzeilen-Zustand mehr. Stabilitaet gegengeprueft: Tab-Wechsel, Sucheingabe und ein schneller Resize-Sturm ueber sechs Breiten liessen den React-Baum unveraendert intakt.

Committet (kleiner kosmetischer UTF-8-Encoding-Fehler in der Commit-Message selbst: "Lesefl√§chen" statt "Leseflaechen" durch einen Heredoc-Kodierungsfehler - nur die Commit-Message betroffen, nicht der Code, kein Amend vorgenommen).
