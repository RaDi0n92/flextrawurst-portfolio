# Umdekorieren Schritt 2: Objektliste gruppiert, mit echtem Browser-Absturz

Objektliste (.object-list, 51 Eintraege) nach Typ gruppiert (Idee/Dokument/Ablauf/Automation/...), Zaehler pro Gruppe, gleiche Datei server/human_redesign.js wie beim Toolbar-Schritt.

Dabei zwei ernste, echte Bugs live gefunden - der zweite hat den Browser-Tab tatsaechlich zum Einfrieren gebracht, nicht nur die App:

1. Erster Versuch verschachtelte Zeilen in Wrapper-Divs (wie beim Toolbar). Anders als die Toolbar-Buttons wird .object-list aber von React dynamisch gefiltert/geloescht (Suche, Objekt entfernen). Beim Tippen ins Suchfeld wollte React eine Zeile ueber ihre urspruengliche Elternreferenz entfernen - die stimmte nach dem Verschachteln nicht mehr, React warf eine Exception und der komplette App-Baum wurde leer (schwarzer Bildschirm, #root leer). Fix: Zeilen bleiben direkte Kinder von .object-list, nur umsortiert per appendChild; Gruppenlabel sind eigenstaendige Geschwister-Elemente statt Wrapper.

2. Die umsortierende Funktion hat bei jedem Aufruf bedingungslos ALLES neu angehaengt, auch wenn schon an der richtigen Stelle. Jedes appendChild feuert den MutationObserver, der wieder die Funktion aufruft, die wieder alles neu anhaengt - Endlosschleife. Diesmal ist nicht nur React abgestuerzt, sondern der ganze Chrome-Tab eingefroren (Page.captureScreenshot und Runtime.evaluate haben nicht mehr geantwortet, ueber die HTTP-Liste war die URL leer = Renderer-Crash). Der alte Tab musste per CDP geschlossen und neu geoeffnet werden. Fix: vor jedem DOM-Eingriff wird verglichen, ob der gewuenschte Zustand vom aktuellen abweicht - nur bei echter Abweichung wird etwas angefasst.

Lehre fuer alle kuenftigen DOM-Restrukturierungen an dieser App (festgehalten direkt im Code als Kommentar in human_redesign.js):
- Container, die React dynamisch per Hinzufuegen/Entfernen veraendert (Suche, Objekt-Erstellung/-Loeschung), duerfen NIEMALS durch Verschachteln in neue Wrapper-Elemente umstrukturiert werden - nur durch Umsortieren als direkte Kinder plus eigenstaendige Geschwister-Label.
- Jede DOM-Restrukturierung, die auf einen MutationObserver reagiert, MUSS pruefen ob der Zielzustand schon erreicht ist, bevor sie etwas anfasst - sonst droht eine Endlosschleife.

Nach dem Fix mehrfach live getestet (Suchbegriff eintippen, Ergebnis pruefen, Suchfeld leeren) - stabil, kein Absturz mehr, Gruppierung bleibt korrekt.
