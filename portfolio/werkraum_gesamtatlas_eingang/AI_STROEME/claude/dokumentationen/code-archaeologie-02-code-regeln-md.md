---
type: Dokumentation
tags:
- claude
- code-archaeologie
- dak_gord_system
- skalpell-prinzip
- verwaist
generated:
  by: claude
  at: '2026-08-15T01:11:04Z'
status: stable
title: Code-Archäologie 02 — code_regeln.md, die früheste Textdatei
description: aufforderungen/code_regeln.md (mtime 04:02:53, noch vor zustand.py) enthält
  die früheste erhaltene Formulierung dessen, was heute als Skalpell-Prinzip in CLAUDE.md
  steht -- ebenfalls verwaist.
resource: /root/werkraum_agent/dak_gord_system/aufforderungen/code_regeln.md
---

## Logischer / physischer Pfad

`agent/dak_gord_system/aufforderungen/code_regeln.md` — physisch
`/root/werkraum_agent/dak_gord_system/aufforderungen/code_regeln.md` (derselbe `agent/`-Symlink,
git-technisch im `/root`-Repo).

## Entstehung

mtime 2026-03-24 04:02:53 — 39 Minuten vor `zustand.py`. Die allerälteste Textdatei im
System, vor jeder Code-Datei.

## Inhalt (3 Zeilen)

"Wenn du Code änderst: gib einen unified diff Patch aus. Kleine Diffs bevorzugen. Nichts
Destruktives ohne Nachfrage." — eine frühe Formulierung dessen, was heute in
`/root/CLAUDE.md` als "Skalpell-Prinzip" steht (kleine Schritte, nichts Destruktives ohne
Rückfrage). Die Idee war von Tag eins an da, nur der Name kam Monate später.

## Zusammenhänge

Geladen einzig von `graf.py` (Schritt `umsetzen`), zusammen mit `system.md`. Liegt im
selben Verzeichnis wie sieben weitere Prompt-Fragmente (alle mtime 2026-03-24 10:15, offenbar
in einem Rutsch angelegt) und den vier `system.md.save*`-Dateien (siehe eigener Eintrag
Code-Archäologie 03).

## Heutiger Status

Vollständig verwaist wie `zustand.py`/`graf.py` — nur `graf.py` lädt sie, `graf.py` läuft
nirgends mehr als Dienst.

## Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu beleben?

Stirbt am selben Tag wie `graf.py` selbst, 2026-04-03 — hängt vollständig an dessen
Lebensspanne, kein eigenständiger Tod. Kein direktes Nachleben als Datei (kein
Nachfolge-Regelwerk trat ausdrücklich an ihre Stelle). Inhaltlich lebt der Kerngedanke
("kleine Diffs, nichts Destruktives ohne Nachfrage") aber weiter — nicht als Codespur, neu
formuliert Monate später im Skalpell-Prinzip von `/root/CLAUDE.md`. Die am wenigsten
direkte Form von Nachleben, die bisher gefunden wurde: keine Codespur, nur eine
wiederkehrende Haltung, offenbar unabhängig nochmal gedacht.

## Ein Detail zur Versionierung

Erster git-fassbarer Kontakt mit dieser Datei ist NICHT ihre Erstellung, sondern ein
Notfall-Commit nach einem vollgelaufenen Datenträger ("Platte-voll-Vorfall") -- die
Entstehungsgeschichte wurde erst im Zuge eines technischen Vorfalls überhaupt versioniert,
nicht bewusst als Ursprung festgehalten.

Volltext-Kontext: `/root/werkraum/docs/code_archaeologie_historiendoku.md`, Datei 2.