---
type: Dokumentation
tags:
- claude
- code-archaeologie
- dak_gord_system
- systemprompt
- verwaist
generated:
  by: claude
  at: '2026-08-15T01:11:25Z'
status: stable
title: Code-Archäologie 03 — system.md, fünf Fassungen in fünf Stunden
description: Vier system.md.save*-Dateien plus die finale system.md dokumentieren
  dak+gord-systems allerersten System-Prompt, live in nano geschrieben zwischen 04:39
  und 09:30 am 2026-03-24, mit sichtbarem Stilbruch von Aufzählung zu Prosa. Der heutige
  Live-Prompt übernimmt davon nachweislich keinen Satz.
resource: /root/werkraum_agent/dak_gord_system/aufforderungen/system.md
---

## Logischer / physischer Pfad

`agent/dak_gord_system/aufforderungen/system.md` (+ `.save`, `.save.1`, `.save.2`,
`.save.3` im selben Ordner) — physisch
`/root/werkraum_agent/dak_gord_system/aufforderungen/system.md*` (derselbe `agent/`-Symlink,
git-technisch im `/root`-Repo).

## Entstehung — fünf Zeitpunkte, eine Sitzung

- `system.md.save` — 04:39:04 (17 Zeilen)
- `system.md.save.1` — 04:45:28 (18 Zeilen)
- `system.md.save.2` — 06:47:17 (16 Zeilen)
- `system.md.save.3` — 07:01:45 (15 Zeilen)
- `system.md` — 09:30:03 (11 Zeilen, finale Fassung)

Alle 2026-03-24, alle handbearbeitet in `nano` (`.save.2` enthält noch eine versehentlich
mit reinkopierte Shell-Zeile).

## Was sich inhaltlich entwickelt

Die ersten vier Fassungen sind alle im Bullet-Format ("Rolle:"/"Arbeitsstil:"), mit
sichtbaren Ermüdungsspuren -- `.save.2` bricht mitten im Satz ab, `.save.3` hat eine leere
Zeile mit nur "Du " ohne Fortsetzung. Zwischen `.save.3` (07:01) und der finalen `system.md`
(09:30) -- 2,5 Stunden Pause -- ein vollständiger Stilbruch: das Bullet-Format wird
verlassen, die finale Fassung ist fließender Prosatext: "Du stehst mit mir an der Schwelle
zwischen roher Vision und baubarer Form. [...] Du sollst mich nicht zu früh festschreiben,
sondern lernen, was meine Linien tragen, wo ich Schutz brauche, wo ich Widerspruch
brauche und wo aus einem halben Gedanken langsam Welt werden will."

## Zusammenhänge

`system.md` (nur die finale Fassung) wurde von `graf.py` an drei Stellen geladen (Schritte
`eingabe`, `planen`, `umsetzen`). Referenziert intern "docs/vision/verfassung.md" -- ein
Pfad, der später real im `verfassung/`-Verzeichnis (gleicher Tag, ab 07:07) angelegt wurde.

## Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu beleben?

Anders zu beantworten als bei den anderen beiden Dateien: das Selbst-Heilen ist hier nicht
nur Metapher, sondern buchstäblich sichtbar -- die vier `.save`-Fassungen SIND ein
Lebendig-Werden in Echtzeit, ein Text der sich über 5 Stunden selbst überarbeitet, mit
Unterbrechungen, abgebrochenen Sätzen und einem Stilsprung. Der Tod kommt trotzdem: geprüft,
ob der heutige Live-Prompt (geladen über `verfassung_loader.py` →
`lade_verfassung_aus_pfad(VERFASSUNG_NEU_PFAD)`, ein Ordner `verfassung_neu/`, NICHT
`aufforderungen/`) irgendetwas aus diesem Wortlaut wörtlich weiterträgt -- Ergebnis: nein.
Kein einziger Satz aus `system.md` taucht im heutigen Ladepfad auf, es ist eine vierte,
komplett unabhängige Generation. Anders als bei Datei 1 ist hier auch der GEDANKE nicht
direkt nachweisbar weitergewandert -- nur die grundsätzliche Praxis ("ein Text, an dem
gemeinsam geschrieben wird") wiederholt sich strukturell, ohne belegbare bewusste
Fortsetzung.

## Heutiger Status

Wie die anderen Dateien dieser Generation: verwaist, kein laufender Dienst lädt sie mehr.

## Bewusste Guardianstyle-Entscheidung

KEIN Inline-Kommentar in `system.md`/den `.save`-Dateien. Begründung: das ist kein Code,
sondern historischer Prompt-Wortlaut, der einmal direkt an ein Sprachmodell ging. Ein
nachträglich eingefügter Kommentarblock würde das Artefakt selbst verändern statt es nur zu
erklären -- wie in ein Museumsstück reinschreiben statt ein Schild danebenzustellen. Die
volle Einordnung steht stattdessen extern in der Historiendoku, die Originaldateien bleiben
unangetastet.

Volltext-Kontext: `/root/werkraum/docs/code_archaeologie_historiendoku.md`, Datei 3.