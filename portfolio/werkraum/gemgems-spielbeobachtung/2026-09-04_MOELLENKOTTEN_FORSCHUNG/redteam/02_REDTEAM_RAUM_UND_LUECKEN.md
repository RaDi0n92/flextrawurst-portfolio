# RED-TEAM 02 — RAUM- UND LÜCKENANGRIFF

## /goal
Greife nicht einzelne Fakten, sondern die räumliche Vollständigkeit an.

Gehe vom Startanker Hauptstraße 151 entlang der behauptet geschlossenen Forschungswege nach außen. Suche Stellen, an denen der Bestand nur so wirkt, als sei er zusammenhängend.

Beziehe den aktuellen Skriptkörper ein. Ein automatisch dicht wirkendes Raster oder ein durch Stadtteilgrenze geclipptes Inventar ist kein Beweis, dass die traditionelle Nachbarschaft räumlich vollständig erfasst ist.

Prüfe außerdem die Orchestrierung räumlich: Hat die Leitstelle Sessions zu lange auf unbekannte Skriptzustände warten lassen? Hat sie einen Teilraum vorschnell als ausreichend abgedeckt betrachtet, nur weil Skripte dafür existieren? Wurde die unabhängige Eigenexploration tatsächlich **vor** dem Skriptvergleich festgehalten und danach historisch unverändert gelassen? Wurde räumliche Doppelarbeit künstlich verlängert, obwohl nur noch eine konkrete Restlücke offen war? Ein Unknown-unknown-Pass darf neue räumliche Fragen öffnen, aber nicht als wiederholtes Pflicht-Ritual ohne neuen Informationsgewinn weiterlaufen.

Prüfe insbesondere:
- Lücken, die alle Skripte derselben Datenquelle gemeinsam erben
- Räume, die im Skriptoutput leer erscheinen, obwohl nur die zugrunde liegende Quelle dort nichts eingetragen hat
- Seitenwege, Rückseiten oder Mikroverbindungen, die automatisches Mapping typischerweise verliert
- Bereiche, die wegen noch laufender Skripte voreilig als endgültige Lücke behandelt wurden
- verschwundene Seitenstraßen
- unbeachtete Fußwege
- unklare Kreuzungsgeometrie
- fehlende Rückseiten und Höfe
- fehlende Höhenwechsel
- Lücken zwischen Gebäude- und Vegetationsdaten
- Randbereiche ohne geklärten Grenzstatus
- Sonderorte ohne belegte Verbindungskette


## Arbeitsweise und eigener Spielraum
Innerhalb dieses Goals wählst du selbst die sinnvollsten Such- und Prüfwege. Wenn ein vorgeschlagener Weg nicht funktioniert oder eine bessere Quelle auftaucht, dokumentiere kurz warum und nutze den besseren nachvollziehbaren Weg. Ziel, Quellenkennzeichnung und Bestehenskriterien bleiben dabei unverändert.

## So prüfst du die Goal-Stufe
Bevor du deine Selbstprüfung abschließt, prüfe die Kriterien einzeln. Schreibe im `/goal-check` für jedes Kriterium kurz: **Kriterium → Beleg → Ergebnis**. Wenn alle Kriterien tragfähig belegt sind, setze `SELBSTPRUEFUNG_BESTANDEN`; andernfalls `SELBSTPRUEFUNG_NICHT_BESTANDEN` und benenne genau das fehlende Stück als nächsten Arbeitsschritt im aktuellen Goal. Danach hältst du an. Weder Status noch Ergebnisdatei schalten das nächste Goal frei; dafür braucht es Daniels ausdrückliche Freigabe.

## /goal-check
`SELBSTPRUEFUNG_BESTANDEN` erst, wenn du den als dicht bezeichneten Teilraum tatsächlich als Wegkette nachvollzogen und jede gefundene Lücke als konkretes Nachforschungsziel beschrieben hast.

Schreibe `ERGEBNIS_REDTEAM_02.md`.


Dein Prüfergebnis ist eine fachliche Bewertung und keine Goal-Freigabe. Nur Daniel gibt eine nächste Goal-Stufe frei.

## Schreibraum
Schreibe deine Prüfergebnisse unter `ausgabe/` und sende konkrete Nachprüfungen über `../kommunikation/inbox/<Empfaenger>/`. Du veränderst keine kanonische Zustandsdatei. Gravity verarbeitet deine Einwände später als eigene geprüfte Ereignisse.
