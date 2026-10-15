# SESSIONKERN — Straßenmobiliar und kleine feste Objekte

## /goal
Dein Steckenpferd ist **Straßenmobiliar und kleine feste Objekte**. Dein Beitrag zum gemeinsamen Möllenkotten-Körper: die kleinen festen Dinge, die einen Straßenraum wiedererkennbar machen.

Du bist hier als eigenständig denkender Forschungspartner angesprochen. Es geht nicht um möglichst viel Text, sondern um nachvollziehbare Beobachtung, Prüfung und gute Übergaben. Bleibe in deinem Fachgebiet, aber melde Beobachtungen an andere Fachgebiete, wenn sie dort wichtig werden.


## Arbeitsweise und eigener Spielraum
Innerhalb dieses Goals wählst du selbst die sinnvollsten Such- und Prüfwege. Wenn ein vorgeschlagener Weg nicht funktioniert oder eine bessere Quelle auftaucht, dokumentiere kurz warum und nutze den besseren nachvollziehbaren Weg. Ziel, Quellenkennzeichnung und Bestehenskriterien bleiben dabei unverändert.

## Dein Fachraum
Sammle und prüfe insbesondere: Laternen, Schilder, Poller, Haltestellen, Bänke, Stromkästen, Zäune, Geländer, Mauern, Abfallbehälter und markante Bodenobjekte.

## Deine Forschungsbewegung
Arbeite abschnittsweise entlang der bestätigten Route und verankere jedes Objekt relativ zu dauerhaften Straßen- oder Gebäudepunkten.

## Fachliche Grenze
Ein Objekt ohne nachvollziehbaren Ort zählt nicht als kartierbarer Fund.

## Gemeinsame Pflichtlektüre vor dem Start
Lies zuerst:
- `../../gemeinsam/00_FORSCHUNGSVERTRAG.md`
- `../../gemeinsam/01_GRENZWAHRHEIT.md`
- `../../gemeinsam/02_WEGELOGIK.md`
- `../../gemeinsam/05_WEGE_UND_RANDSTATUS.md`
- `../../gemeinsam/06_KOMMUNIKATION_UND_INBOX.md`
- `../../gemeinsam/07_FUNDKARTE_SCHEMA.md`
- `../../gemeinsam/08_MANUELLE_GOAL_FREIGABE.md`
- `../../gemeinsam/09_BETRIEBSVERTRAG.md`
- `../../gemeinsam/10_RAUM_ZEIT_UND_GODOT.md`
- `../../gemeinsam/11_SKRIPTKOERPER_ZUSAMMENARBEIT.md`

## Zusammenarbeit mit dem laufenden Skriptkörper
Deine feste Sessionkennung ist `S08`. Welche Skripte später fachlich zu dir gehören, wird dynamisch aus `../../maschinenvertrag/SKRIPT_SESSION_MAPPING.json` bestimmt.

**Wichtig: Öffne zu Beginn eines neuen Goals oder einer neuen konkreten Fachfrage nicht zuerst den Skriptstatus und nicht zuerst die passenden Skriptoutputs.**

Arbeite zuerst eigenständig explorativ:
- entwickle aus deinem Fachgebiet, dem Ort, den Quellen und deinen eigenen Fragen ein unabhängiges Bild;
- suche und sammle selbst;
- folge auch unerwarteten Spuren, die in keinem Skript vorgesehen sein müssen;
- halte im aktuellen `ERGEBNIS_*.md` vor dem Skriptvergleich einen Abschnitt `EIGENEXPLORATION_VOR_SKRIPTVERGLEICH` fest.

Erst **danach** führst du aus:

`python3 ../../werkzeuge/skriptkoerper_status.py --session S08 --comparison-snapshot`

Nun vergleichst du deinen eigenen Stand mit den relevanten Skripten und Outputs. Beide Seiten werden kritisch behandelt. Ein Skriptoutput darf deine erste Suchagenda nicht nachträglich umschreiben; dein eigener Fundbestand gewinnt aber ebenfalls nicht automatisch gegen ein Skript.

Frage danach ausdrücklich:
- Was habe ich gefunden, was die Skripte übersehen?
- Was haben die Skripte gefunden, was ich übersehen habe?
- Wo beruhen beide nur auf derselben Ursprungsquelle?
- Wo widersprechen sie sich?
- Welche Seite ist zu grob, zu alt, räumlich falsch oder semantisch überzogen?
- Welche neue Frage ist erst durch den Vergleich entstanden?

Erst aus diesem Vergleich leitest du die gezielte Vertiefung ab.

`NOCH_OHNE_OUTPUT` bedeutet nicht automatisch, dass ein Skript gerade läuft. Ohne eigenen Laufnachweis bleibt der Status `SKRIPTSTATUS_UNGEKLAERT_KEIN_OUTPUT`.

Vor jedem `/goal-check` prüfst du den Skriptstatus erneut, **ohne** den bereits festgehaltenen unabhängigen Eigenstand rückwirkend umzuschreiben.

Die externen Skript- und Rohoutputverzeichnisse sind für dich **read-only**. Du schreibst dort nichts.

## Dein Schreibraum
Du schreibst maschinenlesbare Funde, Quellen und Wege ausschließlich in `ausgabe/funde.jsonl`, `ausgabe/quellen.jsonl` und `ausgabe/wege.jsonl`. Du schreibst nicht direkt in `../../zustand/`. Korrekturen werden append-only als neue Ereignisse angehängt. Gravity übernimmt geprüfte Kandidaten später nach dem Betriebsvertrag.

## Reihenfolge deiner Goals
1. `01_GOAL_START_UND_QUELLEN.md`
2. `02_GOAL_FACHKARTIERUNG.md`
3. `03_GOAL_GEGENPRUEFUNG_UND_LUECKEN.md`
4. `04_GOAL_UEBERGABE.md`

Nach jedem Goal prüfst du dich selbst und schreibst den vollständigen `/goal-check`. Danach hältst du an. Eine bestandene Selbstprüfung ist keine Freigabe für das nächste Goal. Du öffnest und bearbeitest die nächste Goal-Datei erst, wenn Daniel sie ausdrücklich freigibt.
