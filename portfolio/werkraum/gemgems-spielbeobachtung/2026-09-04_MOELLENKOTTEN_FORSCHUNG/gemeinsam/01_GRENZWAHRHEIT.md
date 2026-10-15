# GRENZWAHRHEIT — MÖLLENKOTTEN

## /goal
Die Nachbarschaftsgrenze von Königreich Möllenkotten soll aus einem originalen oder institutionell autorisierten Grenzartefakt übernommen werden. Die Linie wird nicht von uns erfunden, geglättet oder aus einem ähnlich klingenden Stadtteil abgeleitet.

## Arbeitsweise und eigener Spielraum
Wähle die sinnvollsten Such- und Prüfwege selbst. Wenn ein vorgeschlagener Weg nicht funktioniert oder eine bessere Originalquelle auftaucht, dokumentiere kurz den Wechsel. Ziel und Beweisanforderung bleiben gleich.

## Begriffe getrennt halten
Die traditionellen dreizehn Nachbarschaften und die in aktuellen Planungsunterlagen verwendeten acht Stadtteile sind nicht automatisch dieselbe Gliederung. Eine Stadtteilgrenze wird nur dann als Nachbarschaftsgrenze verwendet, wenn eine Quelle genau diese Gleichsetzung trägt.

## Bevorzugte Herkunft
1. Originalmaterial der Dachorganisation der Schwelmer Nachbarschaften oder der Nachbarschaft Königreich Möllenkotten.
2. Originalmaterial der Stadt Schwelm oder des Stadtarchivs, das die Nachbarschaftsgrenze ausdrücklich benennt.
3. Historische Originalkarte, Katasterdarstellung oder amtliche Quelle mit eindeutigem Grenzbezug.
4. Sekundärmaterial dient zum Auffinden eines Originals, nicht als Ersatz für eine behauptete exakte Linie.

## Was zum Grenzbeweis gehört
Wenn ein Grenzartefakt gefunden wird, sichere soweit technisch und rechtlich möglich:
- `source_id`
- Originaladresse
- Titel und Herausgeber
- `source_date`
- `retrieved_at`
- unveränderte lokale Referenz oder Snapshot
- SHA256-Prüfabdruck des Snapshots
- Beschreibung, was die Linie laut Quelle tatsächlich bedeutet
- maschinenlesbare Geometrie mit Koordinatenreferenzsystem und Genauigkeitsangabe
- dokumentierte Kontrollpunkte der Übertragung

## Grenzstatus ist ein Sachstatus
Erlaubte Werte sind `IN_PRUEFUNG`, `ORIGINALVERIFIZIERT` und `ORIGINALGRENZE_NOCH_NICHT_GEFUNDEN`.

Der aktuelle und historische Grenzstatus wird append-only in `../zustand/grenzstatus.jsonl` geführt. Nur Gravity schreibt dort. Eine maschinenlesbare Linie erhält `ORIGINALVERIFIZIERT` erst nach der Kontrolle gegen das Original.

Wenn kein exaktes Original auffindbar ist, bleibt der Sachstatus `ORIGINALGRENZE_NOCH_NICHT_GEFUNDEN`. Forschung im sicheren Kernbereich kann weitergehen; vollständige Flächenabdeckung wird dann nicht behauptet.

## Bekannte Startquellen zum Auffinden des Originals
- Stadt Schwelm, Geodaten und Karten: https://www.schwelm.de/bauen-wohnen/stadtentwicklung/geodaten-und-karten
- Stadt Schwelm, Planungsunterlagen mit Stadtteilgliederung: https://www.schwelm.de/fileadmin/user_upload/bauen/200660_PMK_Schwelm_25-10-2023.pdf
- Dachorganisation der Schwelmer Nachbarschaften, Übersicht der dreizehn Nachbarschaften: https://schwelmer-nachbarschaften.de/nachbarschaften/
- Königreich Möllenkotten: https://schwelmer-nachbarschaften.de/nachbarschaften/koenigreich-moellenkotten/
- Nachbarschaft Königreich Möllenkotten: https://moellenkotten.de/

## So prüfst du die Goal-Stufe
Prüfe jedes Kriterium als **Kriterium → Beleg → Ergebnis**. `SELBSTPRUEFUNG_BESTANDEN` bedeutet hier nur, dass die vorgeschriebene Grenzsuche und Dokumentation für diese Goal-Stufe vollständig durchgeführt wurde. Es bedeutet ausdrücklich nicht automatisch, dass die Grenze bekannt ist.

## /goal-check
`SELBSTPRUEFUNG_BESTANDEN` ist möglich, wenn entweder eine originalverifizierte Linie vorliegt oder nachvollziehbar dokumentiert ist, welche relevanten Originalstellen geprüft wurden und weshalb die exakte Grenze weiterhin offen bleibt. Der Sachstatus wird separat in `../zustand/grenzstatus.jsonl` geführt. Eine selbst gezeichnete Ersatzlinie erfüllt dieses Goal nicht.
