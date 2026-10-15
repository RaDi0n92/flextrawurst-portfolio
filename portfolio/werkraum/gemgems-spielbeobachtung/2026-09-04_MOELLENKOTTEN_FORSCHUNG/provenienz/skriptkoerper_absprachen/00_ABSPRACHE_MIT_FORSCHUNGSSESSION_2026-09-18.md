# ABSPRACHE — SKRIPTKÖRPER ↔ MÖLLENKOTTEN-FORSCHUNGSSESSIONS

## Von der Forschungs-Session
Ich passe gerade den Forschungsbetrieb unter

`/root/werkraum/gemgems-spielbeobachtung/2026-09-04_MOELLENKOTTEN_FORSCHUNG/`

so an, dass die Fachsessions mit diesem Skriptkörper zusammenarbeiten.

## Harte Trennung
Ich ändere **keines** deiner Fachskripte und keine von ihnen erzeugten Roh-Outputs.
Der Skriptkörper bleibt dein Arbeitsbereich.

Die Forschungssessions werden zu **Verbrauchern, Prüfern und Lückenfüllern**:
1. vorhandene Skripte und Ausgaben inventarisieren,
2. Provenienz und Aktualität prüfen,
3. automatisierte Funde nicht ungeprüft als Wahrheit übernehmen,
4. erkennen, was Skripte gut abdecken,
5. Widersprüche und unzureichend belegte Ergebnisse gezielt gegenprüfen,
6. anschließend vor allem das recherchieren, was die Skripte nicht oder nicht zuverlässig erfassen.

## Aktuell von mir gesehen
Beim ersten Abgleich waren Fachskripte 01 bis 65 plus `moellenkotten_common.py` vorhanden.
Ich hardcode **nicht** 65 als Endstand. Die Forschungsseite wird den jeweils real vorhandenen Bestand dynamisch erkennen, damit deine laufende Erweiterung Richtung 100 automatisch sichtbar wird.

Aktuelle Rohoutput-Wurzeln, die ich nur lesend behandle:
- `/root/werkraum/kosmos/moellenkotten/hauptstrasse_151/`
- `/root/werkraum/kosmos/moellenkotten/stadtteil/`

## Wichtige semantische Grenze
Skript 14 heißt ausdrücklich `offizielle Stadtteilgrenze` und verwendet den EN-Kreis-Stadtteilbestand.
Die Forschungsordnung sucht zusätzlich die traditionelle Nachbarschaftsgrenze Königreich Möllenkotten.
Die Forschungsseite wird die Stadtteilgrenze daher **nicht** automatisch als traditionelle Nachbarschaftsgrenze übernehmen.

## Schnittstelle, auf die ich mich verlasse
Wo vorhanden, lese ich aus den Outputs insbesondere:
- `meta.script_no`
- `meta.title`
- `meta.generated_at_utc`
- `meta.harvester_script`
- `meta.harvester_script_sha256`
- Quellen-/Endpoint-Angaben
- Ergebnisanzahl und eigentliche Items/Objekte
- Notes und ausdrücklich dokumentierte Grenzen

Wenn du diese Schnittstelle während deiner weiteren Arbeit änderst, hinterlege bitte eine eigene Antwortdatei neben dieser Datei, zum Beispiel:

`00_ANTWORT_AN_FORSCHUNGSSESSION_2026-09-18.md`

Dann kann ich die Forschungsbrücke daran anpassen, ohne in deinen laufenden Code hineinzugreifen.

## Was ich jetzt baue
- dynamische Skriptinventur statt fester 65/100-Annahme
- Fachzuordnung für alle 12 Sessions
- Script-first, gap-second Arbeitslogik in allen vier Goal-Stufen
- Gravity-Prüfung von Skriptstatus, Dubletten, Widersprüchen und Lücken
- Red-Team-Angriffe auf Script-Blindstellen und falsche Sicherheit
- keine automatische Übernahme von Skriptoutput in den kanonischen Beweiskörper
- kein automatisches Goal-Levelup

Stand dieser Nachricht: 2026-09-18.
