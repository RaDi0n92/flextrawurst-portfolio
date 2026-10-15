<!-- KANONISCHE_VORLAGE: vorlagen/01_GOAL_START_UND_QUELLEN.md -->
# GOAL 01 — EIGENEXPLORATION, QUELLENBASIS UND ERSTER SKRIPTVERGLEICH

## /goal
Verankere dein Fachgebiet am gemeinsamen Startpunkt. Baue zuerst ein eigenes, neugieriges Ausgangsbild auf, **ohne die relevanten Skriptoutputs als Suchagenda zu verwenden**. Halte diesen Eigenstand fest und öffne erst danach den Skriptkörper zum kritischen Vergleich.

## Phase A — unabhängig explorieren
- Lies die gemeinsamen Forschungsregeln, aber öffne noch keine fachlich relevanten Skriptoutputs.
- Beginne bei Hauptstraße 151 und dem unmittelbar angrenzenden Raum.
- Suche selbst geeignete Original- und Sekundärquellen.
- Folge fachlich plausiblen **und unerwarteten** Spuren.
- Registriere eigene Quellen in `ausgabe/quellen.jsonl`.
- Schreibe atomare Funde nach `ausgabe/funde.jsonl`.
- Vermerke offen, was du nicht weißt und welche Hypothesen erst geprüft werden müssen.

Die Phase ist kein Vollscan. Ein kleiner Mindestkern reicht: mindestens ein eigener Such-/Quellenweg ohne Skriptagenda, mindestens eine selbst erkannte Lücke/Unsicherheit oder unerwartete Beobachtung und genug eigener Stoff, um im anschließenden Vergleich Unterschiede erkennen zu können. Es gibt keine Pflichtzahl an Quellen, Suchläufen, Minuten oder Funden.

## Phase B — Eigenstand einfrieren
Bevor du den fachlichen Skriptstatus öffnest, schreibe in `ERGEBNIS_01.md` einen Abschnitt `EIGENEXPLORATION_VOR_SKRIPTVERGLEICH` mit eigenen Funden, Quellen, Lücken, Hypothesen, überraschenden Beobachtungen und ausdrücklich unbekannten Punkten.

Ab dem ersten Öffnen des fachlichen Skriptstatus oder eines relevanten Skriptoutputs ist dieser Abschnitt historisch eingefroren. Er wird nicht rückwirkend geglättet, ergänzt, umsortiert oder gelöscht. Spätere Korrekturen stehen darunter als `NACHVERMERK_NACH_SKRIPTVERGLEICH` mit kurzer Begründung; der ursprüngliche Eigenstand bleibt sichtbar.

## Phase C — Skripte aufdecken und gegeneinander prüfen
Erst jetzt führe den in deinem Sessionkern genannten `skriptkoerper_status.py --session <SESSION-ID> --comparison-snapshot`-Aufruf aus. Der dabei unter deinem Session-`snapshots/` abgelegte `SKRIPTVERGLEICH_BASIS_*.json`-Stand hält genau fest, welche relevanten Skript-/Outputstände du beim ersten Phase-C-Blick gesehen hast; spätere Änderungen bleiben erlaubt und werden als späterer Vergleichsstand behandelt.
Vergleiche eigen gefunden / Skript nicht, Skript gefunden / eigen nicht, echte Konvergenz, gemeinsame Ursprungsquelle, Widerspruch, semantisch unklare oder nur technisch frische Skriptoutputs und Dinge, nach denen kein Skript überhaupt gefragt hat.
`NOCH_OHNE_OUTPUT` bedeutet ohne separaten Laufnachweis nur `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`, nicht automatisch `SKRIPT_IN_FLIGHT`.

## Phase D — gezielte erste Vertiefung
Leite aus dem Vergleich wenige konkrete Vertiefungen ab. Doppelarbeit ist jetzt erlaubt, wenn sie Gegenprobe, Qualitätssteigerung oder Lückenschluss ist. Ist eine Frage bereits belastbar genug abgedeckt und fehlt ein konkreter Gegenprüfgrund, wird die Doppelarbeit beendet und nur die Restlücke verfolgt.

## So prüfst du die Goal-Stufe
Prüfe jedes Kriterium einzeln als **Kriterium → Beleg → Ergebnis**. Prüfe unmittelbar davor den aktuellen Skriptstatus deiner Session. Dieser späte Statuscheck darf den bereits festgehaltenen unabhängigen Eigenstand nicht rückwirkend umschreiben. Danach hältst du an; die nächste Goal-Stufe braucht Daniels ausdrückliche Freigabe.

## Klare Prüflinie
`SELBSTPRUEFUNG_BESTANDEN` setzt unabhängige Eigenexploration vor Skriptblick, festgehaltenen Eigenstand, kritischen Vergleich beider Seiten und mindestens eine begründete Vertiefungs-/Verwerfungs-/Offenhaltungsentscheidung voraus. Die Eigenexploration muss vergleichsfähig, nicht maximal sein.

## Ergebnisdatei
Schreibe `ERGEBNIS_01.md` mit dem unveränderten Eigenexplorationsabschnitt und danach dem Vergleich. Nutze Arbeitsmarken wie `EIGEN_GEFUNDEN_SKRIPT_NICHT`, `SKRIPT_GEFUNDEN_EIGEN_NICHT`, `BEIDE_KONVERGIEREN`, `WIDERSPRUCH`, `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`, `SKRIPT_TECHNISCH_AKTUELL_SEMANTISCH_UNGEPRUEFT`, `GEZIELT_VERTIEFT` und `NOCH_OFFEN`. Halte danach an.
