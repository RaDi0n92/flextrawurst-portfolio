---
type: Dokumentation
tags:
- claude
- code-archaeologie
- dak_gord_system
- langgraph
- verwaist
generated:
  by: claude
  at: '2026-08-15T01:10:47Z'
status: stable
title: Code-Archäologie 01 — zustand.py, die älteste Datei des Systems
description: agent/dak_gord_system/zustand.py (mtime 2026-03-24) ist die älteste erhaltene
  Datei im gesamten System, heute vollständig verwaist — drei Nachfolge-Generationen
  laufen stattdessen live.
resource: /root/werkraum_agent/dak_gord_system/zustand.py
---

## Logischer / physischer Pfad

`agent/dak_gord_system/zustand.py` — physisch `/root/werkraum_agent/dak_gord_system/zustand.py`.
`agent/` im werkraum-Verzeichnis ist ein Symlink (`agent -> /root/werkraum_agent`), die Datei
gehört git-technisch zum `/root`-Repo, nicht zum `werkraum`-Repo.

## Entstehung

mtime 2026-03-24 (Unix 1774321334) — zehn Tage vor dem ersten Git-Commit des werkraum-Repos
(2026-04-04). Die älteste Datei im gesamten System.

## Struktur

Zwei `@dataclass`-Definitionen, reiner Zustandscontainer für einen LangGraph-State, keine
Logik: `Auftrag` (ziel, regeln, erledigt_wenn) und `Bauzustand` (nutzer_text, auftrag, plan,
kontext, patch, verfassungs_warnungen).

## Zusammenhänge

Einzige Importstelle: `agent/dak_gord_system/graf.py` (gleicher Tag, 15 Minuten jünger),
baut daraus `StateGraph(Bauzustand)` mit Knoten `eingabe → planen → verfassung_pruefen →
kontext → umsetzen`. `graf.py` wird nur von `starte_dak_gord.py` importiert (Root-Verzeichnis,
570 Byte, CLI-Testskript).

## Heutiger Status: komplett verwaist

Kein heute laufender Dienst nutzt diese Generation mehr:
- `dak-gord-web.service` läuft `web_chat.py` → `agent/dak_gord_system/graphen/gespraechsgraf.py`
  (dritte Generation).
- `dak-neugier.service` läuft `python -m agent.dak_gord_system.graph.run_background_cycle`
  (zweite Generation, `graph/`-Verzeichnis, ab 2026-04-03).
- Der laut `docs/agent/ARCHITEKTUR_HEUTE.md` dokumentierte reale Einstiegspunkt ist
  `starte_dak_gord_system.py` (77KB) — nicht zu verwechseln mit dem gleichnamigen, aber
  winzigen `starte_dak_gord.py`, das noch auf `zustand.py`/`graf.py` zeigt.

Drei Generationen desselben Grundgedankens liegen also parallel im selben Repo:
`zustand.py`+`graf.py` (03-24, tot) → `graph/` (04-03, läuft in dak-neugier.service) →
`graphen/gespraechsgraf.py` (läuft in dak-gord-web.service).

## Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu beleben?

Tatsächlicher Sterbepunkt: 2026-04-03, als `graph/` entsteht und `dak-neugier.service`
fortan darüber läuft. Zehn Tage Lebensspanne, dann funktional tot. Er heilt sich nicht
SELBST — eine tote Datei kann das nicht. Aber die Idee darin (ein Zustandsobjekt, das
schrittweise durch einen Graphen läuft) stirbt nicht mit der Datei: sie wird zweimal neu
geboren, erst in `graph/`, dann nochmal in `graphen/gespraechsgraf.py`. Keine
Selbstheilung, eher eine Reinkarnation über menschliche/AI-Hand — der Gedanke überlebt,
das Gefäß nicht.

## Verifikation

2026-08-15 per direktem Import getestet: `Bauzustand`/`Auftrag` lassen sich weiterhin
fehlerfrei instanziieren. Kein Bug, keine Baustelle — reine, folgenlos liegen gebliebene
Prototyp-Generation.

## Guardianstyle

NOTIZ (Herkunft/Alter) + WICHTIG!!! (Verwaisungsstatus) + KOMMENTAR (Einordnung) direkt im
Modul-Docstring der Datei ergänzt.

Volltext-Kontext: `/root/werkraum/docs/code_archaeologie_historiendoku.md`, Datei 1.