# Griffe-Inventur, Vertiefung: Detail-Controls

Weiter in die Tiefe (Daniel: "erstmal noch tiefer gehen"). Geprueft:

- Begriffe & Farben: echter Editor fuer Knotentypen/Wahrheitsgrad/Bearbeitungsstaende, funktioniert.
- Arbeitsvariante-Feld ("haupt2"): ehrlich beschriftet als "Versuchslinie, kein eigener Speicherstand" - reines Label, kein Bug.
- Filter "Alle Typen": funktioniert echt (getestet mit Typ "Idee", Liste filtert korrekt). Eigener erster Testversuch schlug fehl, weil ich den falschen Wert gesetzt hatte (Anzeigetext statt internem value) - kein App-Bug, eigener Fehler beim Testen.
- Plan-Werkstatt "Kante setzen": bewaffnet echten Zielauswahl-Modus fuer Kantenerstellung, sauber wieder deaktivierbar.
- Plan-Werkstatt "Ablauf vorschlagen": erzeugt echte, sauber getrennte Vorschlagsebene (state.proposals, 27 Stueck), ruehrt die echten Kanten nicht an - genau das Prinzip "Vorschlag ist nicht Fakt". Test-Objekt danach wieder entfernt (siehe unten).
- "+ Marker": legt lokal einen neuen Marker an. Wichtiger Fund: Objekt-Erstellung ueber Idee/Frage/Aufgabe/Marker bleibt zunaechst rein lokaler Entwurf ("Ungespeicherte Arbeit") und beruehrt den Server ueberhaupt nicht, solange nicht explizit gespeichert wird. Beim Testen geloescht, bevor gespeichert wurde - Server nie beruehrt, keine Aufraeumung noetig.

Aufgeraeumt (Testartefakte aus dem Klicken selbst, nicht Daniels Wunsch):
- Testobjekt "Ablaufvorschlag - Mein Gesamtkonstrukt" (workflow-32a2318a...) inklusive seiner 27 Vorschlaege ueber "Objekt entfernen" entfernt. Auf dem Server bestaetigt: proposals wieder bei 0, Objekt weg.

Kein weiterer kaputter Griff in dieser Tiefe gefunden. Alle bisher geprueften ca. 25+ Stellen (Haupttoolbar + Detail-Controls) funktionieren echt, bis auf den bereits behobenen "Start hier"-Fall.
