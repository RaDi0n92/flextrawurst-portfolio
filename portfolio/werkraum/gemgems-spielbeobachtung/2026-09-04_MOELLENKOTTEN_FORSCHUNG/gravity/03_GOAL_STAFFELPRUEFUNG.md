# GOAL 03 — STAFFELPRÜFUNG

## /goal
Entscheide nach der Staffel, was wirklich tragfähig ist und was Red-Team angreifen soll.

Erzeuge:
- Liste bestätigter Teilräume
- Liste schwacher Teilräume
- Widerspruchsliste
- Quellenlücken
- räumliche Lücken
- Bildlücken
- noch ungeprüfte Daniel-Erinnerungen
- Kandidaten für Red-Team

Keine literarische Gesamtsynthese. Der gemeinsame Beweiskörper bleibt atomar.

## Skriptkörper vor dem Merge
Aktualisiere den gemeinsamen Skriptstatus unmittelbar vor der Staffelprüfung. Ein Sessionfund darf durch Skriptmaterial vorbereitet oder gestützt sein, aber Gravity übernimmt keinen Skriptrohoutput direkt. Prüfe die darunterliegende Ursprungsquelle, den Harvester-Prüfabdruck, den räumlichen Scope und bekannte Blindstellen.

Kennzeichne in deiner Staffelprüfung besonders:
- sauber skriptgestützte und gegengeprüfte Bereiche
- manuell ergänzte Skriptlücken
- Widersprüche zwischen Skriptoutput und Fachsession
- Skriptbereiche mit maschinenlesbar belegtem Laufstatus
- Skripte ohne Output, deren Ausführungsstatus weiterhin unbekannt ist
- technisch aktuelle Outputs mit unbekannter semantischer Review-Reife
- systematische Quellenfamilien, die nicht als unabhängige Mehrfachbestätigung zählen

## Kanonischer Merge
Prüfe Ereignisse mit `merge_status = ZUR_PRUEFUNG`. Bei Annahme hängst du ein kanonisches Ereignis nach `../zustand/beweiskoerper.jsonl`, `../zustand/quellenregister.jsonl` oder `../zustand/wegekarte.jsonl` an. Bei Ablehnung bleibt das lokale Ereignis erhalten und die betreffende Session erhält eine begründete Inbox-Nachricht. Bestehende kanonische Zeilen werden nicht überschrieben.


## Arbeitsweise und eigener Spielraum
Innerhalb dieses Goals wählst du selbst die sinnvollsten Such- und Prüfwege. Wenn ein vorgeschlagener Weg nicht funktioniert oder eine bessere Quelle auftaucht, dokumentiere kurz warum und nutze den besseren nachvollziehbaren Weg. Ziel, Quellenkennzeichnung und Bestehenskriterien bleiben dabei unverändert.

## So prüfst du die Goal-Stufe
Bevor du deine Selbstprüfung abschließt, prüfe die Kriterien einzeln. Schreibe im `/goal-check` für jedes Kriterium kurz: **Kriterium → Beleg → Ergebnis**. Wenn alle Kriterien tragfähig belegt sind, setze `SELBSTPRUEFUNG_BESTANDEN`; andernfalls `SELBSTPRUEFUNG_NICHT_BESTANDEN` und benenne genau das fehlende Stück als nächsten Arbeitsschritt im aktuellen Goal. Danach hältst du an. Weder Status noch Ergebnisdatei schalten das nächste Goal frei; dafür braucht es Daniels ausdrückliche Freigabe.

## Klare Prüflinie
Ein Staffelprüfungszyklus ist abgeschlossen, wenn jeder in diesem Prüfblock als dicht bezeichnete Teilraum einen nachvollziehbaren Belegpfad besitzt, Eigenexploration und Skripteinfluss unterscheidbar bleiben und jede bekannte Lücke sichtbar geblieben ist. Spätere neue Daten dürfen einen neuen Staffelprüfungszyklus auslösen.

Schreibe `ERGEBNIS_03_STAFFELPRUEFUNG.md` mit `/goal-check`.


Nach deiner Selbstprüfung hältst du an. Die Leitstelle entscheidet mit Daniel, ob derselbe Prüfmodus für einen späteren Materialblock erneut gebraucht wird, Red-Team folgt oder eine Staffelentscheidung vorbereitet wird.
