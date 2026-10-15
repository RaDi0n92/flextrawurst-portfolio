# GOAL 02 — LAUFENDE AUFSICHT

## /goal
Prüfe die aktive Staffel während ihrer Arbeit, nicht erst am Ende.

Aktualisiere zu Beginn und vor Abschluss dieser Aufsicht `../zustand/skriptkoerper_status.json` mit `python3 ../werkzeuge/skriptkoerper_status.py --write`.

Kontrolliere regelmäßig:
- ob neue oder geänderte Fachskripte während der Sessionarbeit hinzugekommen sind
- ob Sessions **vor** dem Skriptvergleich einen eigenständigen Explorationsstand festgehalten haben
- ob ein späterer Skriptfund diesen historischen Eigenstand unzulässig rückwirkend umschreibt
- ob nach dem Vergleich nur begründete Gegenproben/Vertiefungen doppelt gemacht werden, statt blind alles neu zu sammeln
- ob `NOCH_OHNE_OUTPUT` ohne maschinenlesbaren Laufnachweis korrekt als `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT` behandelt wird
- ob `OUTPUT_AKTUELL` fälschlich mit semantisch geprüft gleichgesetzt wird
- ob veraltete, unlesbare oder provenance-arme Outputs zu stark verwendet werden
- ob mehrere Skripte derselben Ursprungsquelle fälschlich wie unabhängige Belege wirken
- Quellenherkunft
- räumliche Anschlussfähigkeit
- Doppelarbeit
- scheinbare Mehrfachbestätigung
- veraltete oder falsch zugeordnete Bilder
- fehlende Gebäudeseiten
- fehlende Wege und Abzweigungen
- fehlende Höheninformationen
- unmarkierte Vermutungen
- Vermischung von Realität und Spielerfindung

Wenn du eine konkrete Lücke siehst, schreibe eine Nachricht nach `../kommunikation/inbox/<Empfaenger>/` gemäß `../gemeinsam/06_KOMMUNIKATION_UND_INBOX.md`. Nenne Fund oder Ort, Problem, vorhandene Belegkennungen, gewünschte Prüfung und weshalb die Nacharbeit wichtig ist. Keine allgemeinen Sammelparolen.


## Arbeitsweise und eigener Spielraum
Innerhalb dieses Goals wählst du selbst die sinnvollsten Such- und Prüfwege. Wenn ein vorgeschlagener Weg nicht funktioniert oder eine bessere Quelle auftaucht, dokumentiere kurz warum und nutze den besseren nachvollziehbaren Weg. Ziel, Quellenkennzeichnung und Bestehenskriterien bleiben dabei unverändert.

## So prüfst du die Goal-Stufe
Bevor du deine Selbstprüfung abschließt, prüfe die Kriterien einzeln. Schreibe im `/goal-check` für jedes Kriterium kurz: **Kriterium → Beleg → Ergebnis**. Wenn alle Kriterien tragfähig belegt sind, setze `SELBSTPRUEFUNG_BESTANDEN`; andernfalls `SELBSTPRUEFUNG_NICHT_BESTANDEN` und benenne genau das fehlende Stück als nächsten Arbeitsschritt im aktuellen Goal. Danach hältst du an. Weder Status noch Ergebnisdatei schalten das nächste Goal frei; dafür braucht es Daniels ausdrückliche Freigabe.

## Klare Prüflinie
Ein einzelner Aufsichtszyklus ist abgeschlossen, wenn jede für diesen Zyklus relevante aktive Session gegen ihren tatsächlichen Zwischenbestand geprüft wurde, Eigenexploration und Skriptvergleich getrennt erkennbar sind und offene Beanstandungen sichtbar bleiben. `SELBSTPRUEFUNG_BESTANDEN` schließt nur **diesen Aufsichtszyklus**, nicht die laufende Forschung.

Schreibe `ERGEBNIS_02_LAUFENDE_AUFSICHT.md` mit `/goal-check`.


Nach deiner Selbstprüfung hältst du an. Die Leitstelle entscheidet mit Daniel, ob derselbe Aufsichtsmodus später erneut gebraucht wird, ein anderer Gravity-Modus vorgeschlagen wird oder Gravity pausiert.
