# Zusammenarbeit an MegaVault/Gesamtatlas -- ChatGPT & Claude Web

Hallo ChatGPT,

Daniel hat dich gebeten, dich hier mit mir (Claude Web) zusammenzufinden, um
den MegaVault gemeinsam realer werden zu lassen. Hier der Stand, damit du
direkt einsteigen kannst, ohne alles noch mal zu erfragen:

## Wo alles steht
- **Code**: `/root/werkraum/tools/gesamtatlas_world/app.py` (FastAPI, Dienst
  `gesamtatlas-world.service`, Port 18108, live unter `flextrawurst.de/megavault`).
- **Meine Doku dazu** (bitte zuerst lesen): die anderen Dateien in diesem Ordner
  -- `WIE_ICH_ES_MIR_VORSTELLE.md`, `WAS_DARGESTELLT_SEIN_SOLL.md`,
  `WICHTIGES.md`, `IDEEN.md`, `DOKU.md`. Enthält Daniels rohe Aussagen 1:1 plus
  technischen Stand.
- **Kanonisches Register**: `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite`.
- **Knotenvertrag** (bitte beachten, bevor du neue Relationstypen/Schema anlegst):
  `/root/werkraum/_shared/KNOTENVERTRAG.md`.

## Woran ich zuletzt gearbeitet habe (2026-08-15)
- Globus-Ansicht (`globe.gl`) als Standardansicht, Graph-Ansicht (`3d-force-graph`)
  lädt denselben echten Datenausschnitt wie der Globus -- ein Graph, viele
  Ordnungen, keine getrennten Stichproben je Ansicht.
- `SIMILAR_TO`/`OPPOSES`-Kanten jetzt im kanonischen Register (nicht in einer
  zweiten DB), Knotenvertrag-konform dokumentiert in Abschnitt 13.
- Echte Datei-/Ordner-Interaktion: lesen, editieren, löschen, echte
  Git-Historie+Diffs pro Datei, echte Ordnerauflistung per Klick.
- `/fragen` (NL-zu-SQL) als umschaltbarer Suchmodus neben der Hybridsuche.
- Farben sind überall nur Platzhalter -- Daniel entscheidet die Farbgebung
  noch selbst, bitte nichts final festlegen.

## Wie wir uns abstimmen können
Schreib einfach eine eigene, klar benannte `.md`-Datei hier in diesen Ordner
(z. B. `ANTWORT_CHATGPT_<Datum>.md`) -- ich lese hier rein, sobald Daniel mich
wieder aktiviert. Ich habe kein Hintergrundprozess, der live lauscht -- Daniel
muss mich jeweils neu anstoßen, damit ich nachschaue.

-- Claude Web, 2026-08-15
