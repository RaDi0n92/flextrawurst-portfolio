<!-- KANONISCHE_VORLAGE: vorlagen/04_GOAL_UEBERGABE.md -->
# GOAL 04 — ÜBERGABE AN GRAVITY NACH EIGENEXPLORATION UND GEGENSEITIGER PRÜFUNG

## /goal
Bereite nur Material für Gravity vor, das nach unabhängiger Eigenexploration, anschließendem Skriptvergleich und gezielter Gegenprüfung tragfähig genug ist.

## Vorgehen
- Prüfe unmittelbar vor der Übergabe erneut den aktuellen Skriptstatus.
- Bewahre den ursprünglichen Eigenexplorationsstand als historischen Vergleichspunkt.
- Prüfe `bestaetigungsstatus`, `sicherheitsstatus` und `weltstatus`.
- Markiere prüfreife lokale Ereignisse append-only mit `merge_status = ZUR_PRUEFUNG`.
- Verweise auf die tatsächlichen Ursprungsquellen. Ein Skriptname oder Outputpfad allein ist kein Quellenbeleg.
- Dokumentiere bei skriptgestützten Funden Skriptnummer, Skript-SHA256, Outputstand und bekannte semantische Grenzen.
- Wenn kein Output existiert, unterscheide `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT` von nachweislich laufenden Skripten.
- Liste offene Forschungsränder, echte Widersprüche und konkrete nächste Prüfungen.
- Sende Gravity eine Nachricht nach `../../kommunikation/inbox/GRAVITY/`.
- Gravity entscheidet über den kanonischen Merge.

## So prüfst du die Goal-Stufe
Prüfe jedes Kriterium einzeln als **Kriterium → Beleg → Ergebnis**. Prüfe unmittelbar davor den aktuellen Skriptstatus deiner Session. Danach hältst du an; weitere Goals brauchen Daniels ausdrückliche Freigabe.

## Klare Prüflinie
`SELBSTPRUEFUNG_BESTANDEN` setzt voraus, dass Gravity klar unterscheiden kann, was die Session selbst vor Skriptblick fand, was erst aus Skripten kam, wo beide unabhängig oder abhängig konvergieren, wo Widerspruch besteht, was gezielt vertieft wurde und was weiterhin unbekannt ist.

## Ergebnisdatei
Schreibe `ERGEBNIS_04.md`, verweise auf die prüfreifen Kennungen und dokumentiere den zuletzt gesehenen Skriptstand. Halte danach an.
