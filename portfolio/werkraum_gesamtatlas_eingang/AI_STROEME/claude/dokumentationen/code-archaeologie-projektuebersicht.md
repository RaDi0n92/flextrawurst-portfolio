---
type: Dokumentation
tags:
- claude
- code-archaeologie
- dak_gord_system
- guardianstyle
- systemgeschichte
generated:
  by: claude
  at: '2026-08-15T00:58:01Z'
status: draft
title: Code-Archäologie — Projektübersicht
description: Laufender, chronologischer Durchgang durch das gesamte flextrawurst/werkraum-System,
  älteste Dateien zuerst — Zeiger auf die drei wachsenden Quelldateien, nicht deren
  Inhalt (der ändert sich laufend).
resource: werkraum:/docs/code_archaeologie_historiendoku.md
---

## Was das hier ist

Auf Daniels Wort (2026-08-15): ein laufender, dateiweiser Durchgang durch das gesamte
flextrawurst/werkraum-System — chronologisch nach echtem Dateisystem-`mtime`, älteste
Datei zuerst, nicht nach Git-Historie (die beginnt erst 2026-04-04, Wochen nach den
ältesten erhaltenen Dateien). Ziel laut Daniel wörtlich: mich "zum
lexikom´glossarcodevsprojektvshistoryai-strom werden lassen" — ein wachsendes,
faktendichtes Nachschlagewerk über Code, Projekt und Geschichte, nicht eine einmalige
Zusammenfassung.

## Wo die eigentlichen (laufend wachsenden) Inhalte liegen

Dieser Atlas-Eintrag ist bewusst nur ein Zeiger, kein Duplikat — die drei Quelldateien
wachsen mit jeder neuen Datei, ein Snapshot hier würde sofort veralten:

- `/root/werkraum/docs/code_archaeologie_lernprotokoll.md` — eigene Reflexion pro Datei:
  was überrascht hat, was falsch angenommen war, was die Datei über das System verrät.
- `/root/werkraum/docs/code_archaeologie_historiendoku.md` — die Faktendoku: logischer +
  physischer Pfad, Entstehungsdatum, Struktur, Zusammenhänge, was seither geschah,
  gefundene Probleme, Omapi/Opami-Guardianstyle-Status.
- `/root/werkraum/docs/code_archaeologie_verwaiste_dateien.md` — Register bestätigt
  verwaister (nicht mehr geladener) Dateien, mit Nachfolger und Beleg-Verweis. Bewusst
  kein physischer Umzug der Dateien selbst (Fundort ist Teil der Geschichte, Umzug riskiert
  Zeitstempel-Verlust) — nur ein zentrales, menschenlesbares Register.
- `/root/werkraum/docs/code_archaeologie_output_wortlaut.md` — vierte Datei, seit 2026-08-15
  auf Daniels Wort: nimmt jede Chat-Antwort zu einem Fund 1:1 unverändert auf, keine erneute
  Verdichtung. Eigener Atlas-Eintrag: `code-archaeologie-output-wortlaut-konzept.md`.

## Methode

Pro Datei: mehrfach neugierig lesen, Beziehungen klären (grep nach Importeuren, git log,
systemd-ExecStart-Abgleich, ggf. Testlauf), bei Code-Dateien Guardianstyle-Kommentar
(Omapi/Opami, Marker WICHTIG!!!/NOTIZ/KOMMENTAR/WITZ/BELEIDIGUNG/EASTEREGG) direkt in die
Datei; bei historischem Prompt-Wortlaut (z.B. alte System-Prompt-Fassungen) bewusst KEIN
Inline-Kommentar, um das Artefakt nicht zu verfälschen — Einordnung dann nur extern in der
Historiendoku.

## Stand (2026-08-15)

6 Dateien/Dateigruppen durchgegangen. Details siehe Historiendoku (Datei 1-6) bzw. je ein
eigener Atlas-Eintrag in derselben Kategorie. Datei 4 ist der bisher stärkste
Selbstheilungs-Fund: drei der Organ-Konzepte leben heute noch als laufender Code
(`kerne/beziehungsorgan.py`, `kerne/entscheidungsorgan.py`, `kerne/zwischenraumorgan.py`).
Datei 5 eröffnet eine dritte Antwortkategorie: nie gestorben, seit Entstehung unverändert.
Datei 6 eine vierte: geboren, fast einen Monat komplett ungenutzt, dann aktiviert.

**Versuch mit parallelen Forks zur Rohrecherche (2026-08-15) wieder verworfen** — die
dabei entstandene Arbeitsweise hatte laut Daniel keine echte eigene Neugier mehr, nur noch
Fakten-Zusammenfassung. Komplett zurückgesetzt auf den Stand nach Datei 6, inklusive der
ersten (zu schnellen) Fassung von Datei 7. Weiter geht es allein, ohne Forks, ein Fund pro
Runde, wirklich langsam gelesen.