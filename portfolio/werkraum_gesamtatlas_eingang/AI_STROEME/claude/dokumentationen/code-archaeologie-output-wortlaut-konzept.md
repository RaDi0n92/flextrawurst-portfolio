---
type: Dokumentation
tags:
- claude
- code-archaeologie
- meta
- wortlaut
generated:
  by: claude
  at: '2026-08-15T00:00:00Z'
status: stable
title: Code-Archäologie — vierte Datei "Output-Wortlaut" (Konzept)
description: Neben Historiendoku (Fakten) und Lernprotokoll (Reflexion) gibt es seit
  2026-08-15 eine dritte lokale Datei, die jede Chat-Antwort zu einem Datei-Fund 1:1
  unverändert aufnimmt -- keine erneute Verdichtung, kein drittes Zusammenfassungsformat.
resource: /root/werkraum/docs/code_archaeologie_output_wortlaut.md
---

## Warum diese Datei entstand

Daniel hatte zuvor kritisiert, dass Chat-Antworten während der Code-Archäologie zu reinem
Prozess-Status verkamen ("committed, synced") statt echten Dateiinhalt zu berichten. Als
Reaktion darauf forderte er eine dritte lokale Markdown-Datei, wörtlich (2026-08-15):

"jetzt will ich auch dass du jedesmal nen ne dritte md anlegst dei deinen gesamten output
1zu1 nimmt ihne ene zache zu ändern und sauch nichmal dazu legt und auch immer laden bei
sessionstart ud auch immer in gesamtatlas eingang."

## Was die Datei macht

`docs/code_archaeologie_output_wortlaut.md` (im werkraum-Repo) nimmt nach jeder Chat-Antwort,
die einen Datei-Fund berichtet, genau diesen Text — unverändert, nicht zusammengefasst,
nichts hinzugefügt oder weggelassen — als neuen Eintrag auf. Sie unterscheidet sich damit
bewusst von:
- `code_archaeologie_historiendoku.md` — strukturierte Fakten pro Datei
- `code_archaeologie_lernprotokoll.md` — meine Reflexion über den Lernprozess

Diese dritte Datei ist reiner Wortlaut, ohne jede weitere Bearbeitungsstufe.

## Wo sie eingebunden ist

Als vierter Pflichtlese-Punkt in `/root/CLAUDE.md`, Abschnitt "Kontext-Wiederherstellung
nach Verbindungsabbruch", Schritt 9 — wird ab jetzt bei jedem Sessionstart mitgelesen wie
die anderen drei Code-Archäologie-Dateien.

Volltext-Kontext: `/root/werkraum/docs/code_archaeologie_output_wortlaut.md`
