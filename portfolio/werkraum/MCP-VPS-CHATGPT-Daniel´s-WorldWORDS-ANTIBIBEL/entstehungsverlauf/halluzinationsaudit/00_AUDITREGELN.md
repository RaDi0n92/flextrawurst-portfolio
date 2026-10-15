# Regeln des Halluzinationsaudits

## Zweck

Dieser Audit prüft Aussagen, die während der Metamonster-Wortsuche entstanden sind. Er trennt reale Messwerte, Fundstellen, Sprecherrollen, Urheberschaft und Interpretation.

## Verbindliche Klassen

- `BESTAETIGT`: direkt rückgelesene Datei, Datenbankzeile, Werkzeugmessung oder aktuelles Daniel-Zitat.
- `BESTAETIGT_MIT_SCOPE`: Messung stimmt nur innerhalb eines ausdrücklich genannten Filters.
- `WAHRSCHEINLICH`: starke Indizien, aber kein vollständiger Ursprungskörper.
- `UNKLAR`: Fundstelle vorhanden, Urheber oder Entstehungsweg nicht belegt.
- `HERABGESTUFT`: frühere Formulierung war stärker als die Belege.
- `VERWORFEN`: Aussage ist falsch oder durch spätere Prüfung widerlegt.

## Schutzregeln

1. Fundstelle ist nicht Urheberschaft.
2. `role=user`, `type=user`, `mensch` oder `Angelegt von` sind Datenfelder, keine notarielle Wahrheit.
3. Ein Dateiname mit einer Seitenzahl beweist keine nachgezählte Seitenzahl.
4. Null Scanner-Ausnahmen bedeuten nicht semantische Richtigkeit, Vollständigkeit oder unabhängige Quellen.
5. Wiederholte, generierte oder gespiegelte Dateien werden nicht als ebenso viele eigenständige Sprachursprünge gezählt.
6. Ein von Daniel eingefügter Text ist eine von Daniel übermittelte Quelle, aber nicht automatisch vollständig von Daniel verfasst.
7. AI-Antworten in alten Gesprächsexporten dürfen eigene Halluzinationen enthalten und werden nicht als Sachquelle benutzt.
8. ChatGPT-Suche bedeutet hier nur erreichbare aktuelle Gesprächs-, Bibliotheks- und VPS-Körper. Keine vollständige Kontoweitsuche wird behauptet.
