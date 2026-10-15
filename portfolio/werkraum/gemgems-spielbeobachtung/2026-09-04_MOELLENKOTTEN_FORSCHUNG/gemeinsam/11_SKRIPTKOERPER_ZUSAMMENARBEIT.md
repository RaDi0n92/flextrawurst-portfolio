# SKRIPTKÖRPER-ZUSAMMENARBEIT — ERST EIGENSTÄNDIG ENTDECKEN, DANN GEGENEINANDER PRÜFEN

## /goal
Die Fachsessions arbeiten parallel zu einem externen Möllenkotten-Skriptkörper unter `/root/werkraum/kosmos/skripte_moellenkotten_100/`.

Die Skripte sind eine automatische Sammel- und Vergleichsschicht. Sie sollen die Sessions weder ersetzen noch ihre erste Wahrnehmung des Ortes vorformen.

Darum gilt nicht mehr „Skript zuerst“. Der Arbeitszyklus lautet:

**Eigenexploration → eigenen Stand festhalten → Skriptvergleich → gegenseitiger Angriff → gezielte Vertiefung und Verbesserung.**

## Phase A — Eigenexploration ohne Skriptblick
Für einen neuen Teilraum, ein neues Goal oder eine neue konkrete Fachfrage beginnt die Session zunächst eigenständig.

In dieser Phase:
- liest sie nicht den aktuellen Skriptstatus für ihr Fachgebiet;
- öffnet sie keine Skriptoutputs als Suchagenda;
- recherchiert sie neugierig aus Fachwissen, Quellenlage, Raumlogik und eigenen Beobachtungsfragen;
- darf sie unerwartete Dinge verfolgen, die in keinem Skript vorgesehen sind;
- hält sie Unsicherheit und spontane Hypothesen sichtbar.

Ziel ist **keine vollständige Doppelerhebung**. Ziel ist ein unabhängiges Ausgangsbild, damit die Skripte später nicht die gesamte Wahrnehmung ankern.

### Kleiner Mindestkern statt Forschungsritual
Die Eigenexploration ist **vergleichsbereit**, sobald ein kleiner unabhängiger Kern vorhanden ist: mindestens ein eigener Such-/Quellenweg ohne Skriptagenda, mindestens eine selbst erkannte Lücke/Unsicherheit oder unerwartete Beobachtung und genug Material, um beim späteren Vergleich überhaupt Unterschiede erkennen zu können. Es gibt **keine Pflichtzahl** an Quellen, Suchläufen, Minuten oder Funden. Sobald dieser Kern steht, darf und soll die Session zum Vergleich übergehen, statt aus Prinzip alles doppelt zu erheben.

## Phase B — Eigenen Zwischenstand einfrieren
Bevor die Session relevante Skriptoutputs öffnet, hält sie knapp fest:
- was sie selbst gefunden hat;
- welche Quellen sie selbst aufgetan hat;
- welche Lücken sie selbst wahrnimmt;
- welche Hypothesen oder überraschenden Beobachtungen entstanden sind;
- was sie ausdrücklich noch nicht weiß.

Dafür genügt ein klar markierter Abschnitt im aktuellen `ERGEBNIS_*.md` mit der Überschrift:

`EIGENEXPLORATION_VOR_SKRIPTVERGLEICH`

Es wird keine zusätzliche Pflichtdatei nur für dieses Ritual erzeugt.

Ab dem ersten Öffnen des fachlichen Skriptstatus oder eines relevanten Skriptoutputs gilt dieser Abschnitt als **historisch eingefroren**: nicht rückwirkend glätten, ergänzen, umsortieren oder löschen. Falls später ein eigener Fehler auffällt, bleibt der ursprüngliche Text stehen und die Korrektur wird darunter als `NACHVERMERK_NACH_SKRIPTVERGLEICH` mit kurzer Begründung ergänzt. So bleibt erkennbar, was wirklich vor dem Skriptkontakt vorhanden war.

## Phase C — Skriptkörper aufdecken und beide Seiten kritisch vergleichen
Erst nach dem festgehaltenen Eigenstand führt die Session den Live-Statusaufruf aus:

`python3 ../../werkzeuge/skriptkoerper_status.py --session <SESSION-ID> --comparison-snapshot`

Der erste Phase-C-Aufruf legt zusätzlich einen kleinen `SKRIPTVERGLEICH_BASIS_*.json`-Snapshot im eigenen Session-`snapshots/`-Ordner ab. Er enthält nur den gesehenen relevanten Status mit Skript-SHA, Outputstand sowie Review-/Run-Status; die Skriptdateien selbst werden nicht kopiert.

Dann vergleicht sie systematisch:
- Was fand die Session, was die Skripte nicht fanden?
- Was fanden die Skripte, was die Session nicht fand?
- Wo bestätigen sich beide nur scheinbar, weil dieselbe Ursprungsquelle dahintersteckt?
- Wo widersprechen sie sich?
- Wo ist ein Skript technisch aktuell, aber semantisch noch ungeprüft?
- Wo war die eigene Exploration zu eng oder voreingenommen?
- Wo war der Skriptkörper durch sein Datenmodell blind?

Weder Session noch Skript gewinnen automatisch.

## Phase D — gezielte Vertiefung
Erst nach diesem Vergleich wird entschieden, was noch einmal vertieft wird.

Mögliche Folgen:
- unabhängige Quelle nachziehen;
- räumlich genauer messen oder lokalisieren;
- Bild-/Perspektivfrage klären;
- eine eigene Annahme verwerfen;
- einen Skriptfund herabstufen;
- eine Skriptlücke manuell erforschen;
- eine neue, vorher von keiner Seite gesehene Frage verfolgen;
- Widerspruch an Gravity oder eine andere Fachsession geben.

Die Vertiefung soll **gezielt** sein. Jetzt ist Doppelarbeit erlaubt, wenn sie als Gegenprobe oder Qualitätssteigerung begründet ist. Ist eine Frage bereits belastbar genug abgedeckt und fehlt ein konkreter Gegenprüfgrund, wird die Doppelarbeit beendet und nur die Restlücke verfolgt. Die Leitstelle darf ritualisierte Doppelarbeit ausdrücklich enger führen oder beenden; bloße Arbeitslänge ist kein Qualitätsmerkmal.

## Harte Trennung der Arbeitskörper
Die Fachsessions verändern keine Dateien unter:
- `/root/werkraum/kosmos/skripte_moellenkotten_100/`
- `/root/werkraum/kosmos/moellenkotten/`

Diese Bereiche gehören zum externen Skriptkörper und dessen Rohoutputs. Die Sessions lesen sie nur.

## Kein erfundenes „läuft gerade“
`NOCH_OHNE_OUTPUT` bedeutet nur: Für das Skript wurde aktuell kein zuordenbarer Output gefunden.

Daraus darf **nicht** automatisch `SKRIPT_IN_FLIGHT` abgeleitet werden. Das Skript kann ungestartet, blockiert, fehlgeschlagen, zurückgestellt oder tatsächlich in Arbeit sein.

`SKRIPT_IN_FLIGHT` darf nur verwendet werden, wenn ein eigener Lauf-/Statusnachweis des Skriptkörpers das tatsächlich belegt. Ohne solchen Nachweis lautet der Arbeitsstatus:

`SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`

Dieser Zustand hindert die Eigenexploration nicht.

## Technische Frische ist keine semantische Reife
`OUTPUT_AKTUELL` bedeutet nur: Der Output nennt denselben Harvester-Prüfabdruck wie die aktuell sichtbare Skriptdatei.

Es bedeutet nicht:
- dass der Output sachlich richtig ist;
- dass sein räumlicher Scope stimmt;
- dass sein Ursprungsdatensatz vollständig ist;
- dass das Skript sein angekündigtes individuelles semantisches Red-Team bestanden hat.

Bis ein maschinenlesbarer, an den aktuellen Skript-SHA256 gebundener Prüfnachweis vorliegt, bleibt:

`SEMANTISCHE_SKRIPTREIFE = UNKNOWN`

## Was Skripte besonders schlecht beweisen können
Automatisierte strukturierte Quellen sind häufig stark bei vorhandenen Objekten und Tags, aber schwächer bei:
- unbekannten unbekannten Dingen, nach denen das Skript nie fragt;
- fehlenden oder falsch gepflegten Karteneinträgen;
- Rückseiten und verdeckten Bereichen;
- visuellen Materialien und Farben;
- exakten realen Breiten und Höhen ohne Messquelle;
- informellen Wegen;
- tatsächlicher Zugänglichkeit;
- privaten Innenräumen;
- lokalen Erinnerungen und Daniels Ortskenntnis;
- historischer Bedeutung;
- Blickrichtung und Bildlokalisierung;
- dem Nachweis, dass **nichts** vorhanden ist.

Die Eigenexplorationsphase existiert ausdrücklich, damit solche Dinge überhaupt eine Chance bekommen aufzutauchen.

## Skriptoutput ist keine neue unabhängige Ursprungsquelle
Ein Skript ist ein Erhebungswerkzeug. Wenn zwanzig Skripte OpenStreetMap auswerten, entstehen dadurch nicht zwanzig unabhängige Quellen.

Für Bestätigung zählt die Ursprungsquelle hinter dem Output. `harvester_script_sha256`, Output-Prüfabdruck und Generierungszeit dokumentieren die Verarbeitung, nicht zusätzliche Unabhängigkeit.

## Wichtige Grenzfalle
Skript 14 und davon abhängige Inventarskripte verwenden derzeit eine **offizielle Stadtteilgrenze** aus dem Ennepe-Ruhr-Kreis.

Die Forschungsordnung sucht für vollständige Nachbarschaftsabdeckung zusätzlich die traditionelle Grenze von **Königreich Möllenkotten**.

Darum gilt:
- Stadtteilgrenze ist nicht automatisch traditionelle Nachbarschaftsgrenze;
- ein durch die Stadtteilgrenze geclippter Skriptoutput kann räumlich nützlich sein;
- er beweist nicht, dass sein Clip exakt dem traditionellen Nachbarschaftsgebiet entspricht;
- Gravity darf daraus keinen `ORIGINALVERIFIZIERT`-Nachbarschaftsstatus ableiten.

## Nummernkonflikte
Der Scanner unterscheidet Dateianzahl, eindeutige Skriptnummern, fehlende Nummern und Doppelnummern. Bei Doppelnummern gilt der Skriptkörper weiterhin als `IN_AUFBAU`.

Bis ein Nummernkonflikt durch die Skriptkörper-Session geklärt ist, referenzieren Forschungssessions betroffene Varianten zusätzlich über vollständigen Dateipfad und SHA256 statt nur über die Nummer.

## Veränderungen während einer Session
Wenn ein Skript oder Output während Phase A entsteht, bleibt Phase A trotzdem unabhängig. Die Session schaut erst nach ihrem eigenen eingefrorenen Zwischenstand hinein.

Wenn sich Skript oder Output **nach** dem Vergleich erneut ändert:
- betroffenen Vergleich neu öffnen;
- frühere Bewertung nicht still weitertragen;
- nur den betroffenen Bereich erneut vergleichen, nicht die gesamte Eigenexploration löschen.

## Fachzuordnung
`../maschinenvertrag/SKRIPT_SESSION_MAPPING.json` ordnet Skripte den Fachsessions zu.

Diese Zuordnung ist eine **Hinweiskarte**, keine Ontologie. Ein nicht zugeordnetes Skript darf trotzdem relevant sein; eine Session darf eine unerwartete Verbindung melden.

Session 12 und Gravity dürfen den gesamten Skriptkörper überblicken.

## Goal-Ergebnisse
Jede Ergebnisdatei soll nach dem Vergleich knapp unterscheiden:
- `EIGEN_GEFUNDEN_SKRIPT_NICHT`
- `SKRIPT_GEFUNDEN_EIGEN_NICHT`
- `BEIDE_KONVERGIEREN`
- `WIDERSPRUCH`
- `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`
- `SKRIPT_TECHNISCH_AKTUELL_SEMANTISCH_UNGEPRUEFT`
- `GEZIELT_VERTIEFT`
- `NOCH_OFFEN`

Das sind Arbeitsstatus, keine neuen Wahrheitsstatus des Datenmodells.

## /goal-check
Ein Goal ist nicht sauber geprüft, wenn:
- die Session vor ihrer ersten Eigenexploration bereits die relevanten Skriptoutputs als Suchagenda benutzt hat;
- der unabhängige Eigenstand vor dem Vergleich nicht erkennbar festgehalten wurde;
- Skript- und Eigenfunde nicht kritisch gegeneinander gehalten wurden;
- oder die anschließende Vertiefung nur blind dieselbe Erhebung wiederholt, ohne Qualitätsgrund.
