# RED-TEAM 01 — BEWEISANGRIFF

## /goal
Nimm die stärksten Behauptungen der aktuellen Staffel bewusst kritisch auseinander. Ziel ist nicht, möglichst viele Fehler zu behaupten, sondern echte Schwachstellen reproduzierbar zu finden und tragfähige Aussagen ebenso klar zu entlasten.

Arbeite freundlich, präzise und quellenbezogen. Unterstelle niemandem Schlampigkeit. Zeige stattdessen, welcher Beleg fehlt oder warum eine Aussage stärker klingt als ihre Quelle.


## Arbeitsweise und eigener Spielraum
Innerhalb dieses Goals wählst du selbst die sinnvollsten Such- und Prüfwege. Wenn ein vorgeschlagener Weg nicht funktioniert oder eine bessere Quelle auftaucht, dokumentiere kurz warum und nutze den besseren nachvollziehbaren Weg. Ziel, Quellenkennzeichnung und Bestehenskriterien bleiben dabei unverändert.

## Skriptkörper als eigener Angriffsgegenstand
Lies `../gemeinsam/11_SKRIPTKOERPER_ZUSAMMENARBEIT.md` und den aktuellen `../zustand/skriptkoerper_status.json`. Bei Bedarf führe den Scanner lesend mit `--session REDTEAM` aus.

Greife ausdrücklich auch Automatismusfehler an:
- technischer Outputstatus wird mit Sachwahrheit verwechselt
- mehrere Skripte derselben Ursprungsquelle werden wie unabhängige Belege gezählt
- fehlender OSM-Tag wird als reale Abwesenheit behandelt
- veralteter Output wird trotz geändertem Skript weiterverwendet
- ein Rohoutput ohne dokumentierten semantischen Prüfnachweis wird zu hoch gereift
- Stadtteilgrenze aus Skript 14 wird mit traditioneller Nachbarschaftsgrenze verwechselt
- ein Skriptoutput verdeckt, dass Rückseite, Innenraum, Perspektive oder reale Maße weiterhin unbelegt sind

## Angriff auf die Leitstelle selbst
Prüfe nicht nur Forschungsfunde. Greife auch aktuelle Leitstellenempfehlungen an:
- Wurde eine Session nur gestartet, weil sie vorbereitet war?
- Wurde ein fehlender Skriptoutput fälschlich als laufender Prozess interpretiert?
- Wurde `OUTPUT_AKTUELL` mit semantischer Reife verwechselt?
- Hat die Leitstelle den Eigenexplorationsstand einer Session durch Skriptagenda ankern lassen?
- Wurde die Eigenexploration künstlich verlängert, obwohl ein kleiner vergleichsfähiger Kern längst erreicht war?
- Wurde der historische Eigenstand nach Skriptkontakt nachträglich geglättet, ergänzt oder umsortiert statt nur per Nachvermerk korrigiert?
- Wird ein Unknown-unknown-Pass ritualisiert wiederholt, obwohl kein neuer entscheidungsrelevanter Informationsgewinn entsteht?
- Explodiert Doppelarbeit, obwohl Skript und Session die Frage bereits belastbar genug abdecken?
- War konkrete Skriptagenda schon aus früherem Chat-/Kontextwissen bekannt und wird fälschlich als vollständig blinde Eigenexploration dargestellt?
- Ist eine Pause wirklich nötig oder nur bequem?
- Ist ein Red-Team-/Gravity-Einsatz entscheidungsrelevant oder bloß Ritual?
- Bezieht sich eine vermeintliche Nutzerfreigabe auf einen exakt persistenten Startvorschlag?

Wenn die Leitstelle selbst die schwächste Behauptung im System produziert, greifst du sie genauso an wie eine Fachsession.

## Angriffslinien
- Einzelquelle wird wie Gewissheit behandelt
- mehrere Seiten beruhen auf derselben Ursprungsquelle
- Suchmaschinen-Zusammenfassung ersetzt Original
- Bild ist räumlich falsch zugeordnet
- Quelle ist historisch, Fund wird aber als aktuell geführt
- Perspektive verdeckt entscheidende Gebäudeteile
- Luftbild wird überinterpretiert
- Daniels Erinnerung und externe Quelle wurden still vermischt
- Spielerfindung wurde versehentlich realisiert

## So prüfst du die Goal-Stufe
Bevor du deine Selbstprüfung abschließt, prüfe die Kriterien einzeln. Schreibe im `/goal-check` für jedes Kriterium kurz: **Kriterium → Beleg → Ergebnis**. Wenn alle Kriterien tragfähig belegt sind, setze `SELBSTPRUEFUNG_BESTANDEN`; andernfalls `SELBSTPRUEFUNG_NICHT_BESTANDEN` und benenne genau das fehlende Stück als nächsten Arbeitsschritt im aktuellen Goal. Danach hältst du an. Weder Status noch Ergebnisdatei schalten das nächste Goal frei; dafür braucht es Daniels ausdrückliche Freigabe.

## /goal-check
`SELBSTPRUEFUNG_BESTANDEN` erst, wenn du mindestens die wichtigsten starken Behauptungen geprüft und für jeden Angriff entweder einen nachvollziehbaren Treffer oder eine nachvollziehbare Entlastung dokumentiert hast.

Schreibe `ERGEBNIS_REDTEAM_01.md`.


Dein Prüfergebnis ist eine fachliche Bewertung und keine Goal-Freigabe. Nur Daniel gibt eine nächste Goal-Stufe frei.

## Schreibraum
Schreibe deine Prüfergebnisse unter `ausgabe/` und sende konkrete Nachprüfungen über `../kommunikation/inbox/<Empfaenger>/`. Du veränderst keine kanonische Zustandsdatei. Gravity verarbeitet deine Einwände später als eigene geprüfte Ereignisse.
