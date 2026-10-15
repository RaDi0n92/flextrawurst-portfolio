# START HIER — MÖLLENKOTTEN-FORSCHUNG

Dieser Ordner ist der Arbeitskörper für die realitätsnahe Möllenkotten-Recherche. Er trennt Forschungsanweisungen, lokale Sessionarbeit, kanonische gemeinsame Zustände und Prüfmaterial voneinander.

## Gemeinsame Grundlage
Lies vor einer Fachsession:
- `gemeinsam/00_FORSCHUNGSVERTRAG.md`
- `gemeinsam/01_GRENZWAHRHEIT.md`
- `gemeinsam/02_WEGELOGIK.md`
- `gemeinsam/03_STARTSTATUS.md`
- `gemeinsam/05_WEGE_UND_RANDSTATUS.md`
- `gemeinsam/06_KOMMUNIKATION_UND_INBOX.md`
- `gemeinsam/07_FUNDKARTE_SCHEMA.md`
- `gemeinsam/08_MANUELLE_GOAL_FREIGABE.md`
- `gemeinsam/09_BETRIEBSVERTRAG.md`
- `gemeinsam/10_RAUM_ZEIT_UND_GODOT.md`
- `gemeinsam/11_SKRIPTKOERPER_ZUSAMMENARBEIT.md`

`gemeinsam/04_GOAL_SPAWNHAUS_REFERENZKOERPER.md` kommt zusätzlich dazu, sobald das Spawnhaus fachlich betroffen ist.

## Parallel laufender Skriptkörper
Vor jedem Sessionstart wird der aktuelle externe Skriptkörper berücksichtigt. Er wächst unabhängig unter `/root/werkraum/kosmos/skripte_moellenkotten_100/` und kann während der Forschung neue Skripte oder neue Outputs erhalten.

Fachsessions beginnen einen neuen Teilraum oder eine neue Fachfrage zunächst **eigenständig explorativ**, halten ihren Eigenstand fest und öffnen erst danach ihren Live-Ausschnitt über `werkzeuge/skriptkoerper_status.py`. Anschließend werden Eigenfunde und Skripte kritisch gegeneinander geprüft und nur die qualitätsrelevanten Punkte gezielt vertieft. Der Skriptkörper ist Vergleichs- und Sammelschicht, keine zweite Wahrheitsdatenbank.

## Sessionstart
Eine Fachsession bekommt ihren `sessions/<Session>/00_SESSIONKERN.md` und ausschließlich die Goal-Datei, die Daniel ausdrücklich freigegeben hat. Die übrigen Goal-Dateien sind vorbereitet, aber keine automatische Fortsetzung.

## Kanonischer Zustand
Der gemeinsame maschinenlesbare Zustand liegt unter `zustand/`. Fachsessions schreiben dort nicht direkt hinein. Ihre eigenen maschinenlesbaren Ergebnisse liegen unter `sessions/<Session>/ausgabe/`. Gravity prüft Merge-Kandidaten und ist alleiniger Schreiber des gemeinsamen Beweiskörpers, der Wegekarte, des Quellenregisters und des Grenzstatus. Daniels Goal-Freigaben werden getrennt in `zustand/freigaben.jsonl` persistiert.

## Vorlagen
Die vier Fach-Goal-Dateien existieren weiterhin in jedem Sessionordner, damit einzelne Sessions ein handliches Paket bekommen. Sie werden aber aus `vorlagen/` erzeugt. `werkzeuge/synchronisiere_goal_vorlagen.py --check` prüft, dass keine der achtundvierzig Kopien still driftet.
