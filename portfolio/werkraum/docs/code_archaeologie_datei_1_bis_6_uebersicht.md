# Code-Archäologie — Datei 1 bis 6, Übersicht

Kondensierter Auszug aus `code_archaeologie_historiendoku.md`, nur Datei 1-6. Vollständige
Fassung inkl. aller weiteren Dateien dort, nicht hier.

---

## Datei 1 — `agent/dak_gord_system/zustand.py`

mtime 2026-03-24, älteste Datei im System, zehn Tage vor dem ersten Git-Commit. Zwei
Dataclasses (`Auftrag`, `Bauzustand`) für einen LangGraph-Zustand. Einzige Importstelle:
`graf.py`, das wiederum nur von `starte_dak_gord.py` (570 Byte, reines CLI-Testskript)
genutzt wird. Weder `dak-gord-web.service` noch `dak-neugier.service` nutzen diesen Pfad
heute — zwei spätere, unabhängige Generationen (`graph/`, `graphen/gespraechsgraf.py`)
laufen stattdessen live.

## Datei 2 — `agent/dak_gord_system/aufforderungen/code_regeln.md`

mtime 2026-03-24 04:02:53, 39 Minuten vor `zustand.py` — die älteste Textdatei im System.
Drei Zeilen: unified-diff-Patches, kleine Diffs bevorzugen, nichts Destruktives ohne
Nachfrage. Nur von `graf.py` geladen (Schritt `umsetzen`).

## Datei 3 — `system.md` + vier `.save`-Vorstufen

Fünf Dateien, 2026-03-24, 04:39 bis 09:30 Uhr — der erste System-Prompt für dak+gord-system,
live in `nano` geschrieben. Vier Zwischenfassungen im Bullet-Format ("Rolle:"/"Arbeitsstil:"),
die finale Fassung (09:30) ist durchgehender Prosatext: "Du stehst mit mir an der Schwelle
zwischen roher Vision und baubarer Form." Geladen von `graf.py` an drei Stellen.

## Datei 4 — die sieben "Organ"-Fragmente

Alle sieben am 2026-03-24, 10:15:27 Uhr, 45 Minuten nach der finalen `system.md`.
Konzeptprosa für Beziehungsnähe, Codedenken, Entscheidungsmitgang, Sprachgesetz,
Verfassungsschutz, Weltformtreue, Zwischenraumhaltung.

Drei davon leben heute als Code weiter: `beziehungsnaehe.md` → `kerne/beziehungsorgan.py`,
`entscheidungsmitgang.md` → `kerne/entscheidungsorgan.py`, `zwischenraumhaltung.md` →
`kerne/zwischenraumorgan.py` — alle drei importiert von `graphen/gespraechsgraf.py`, live
hinter `dak-gord-web.service`. Feldnamen fast wörtliche Übersetzungen der Prosa
(`spannungen`, `verdeckte_kosten`, `strukturbedarf`, `widerspruchsbedarf`, `resonanzbedarf`).
`sprachgesetz.md`s "nicht wie ein Ticket-System" steht wortgleich in
`verfassung_neu/1_wesen.md`, dem heute tatsächlich geladenen Konstitutions-Ordner.

## Datei 5 — `agent/dak_gord_system/__init__.py`

mtime 2026-03-24 04:03:23, zweitälteste Datei. Eine Zeile: `# dak+gord-system (Bau-Agent)`.
Byte-identisch seit Entstehung. 48 Python-Dateien im System importieren aktuell über
`agent.dak_gord_system.*` und hängen damit an dieser einen Datei — darunter alle drei
lebenden `kerne/*organ.py`-Module aus Datei 4.

## Datei 6 — `agent/dak_gord_system/kerne/gedaechtnisspeicher.py`

mtime 2026-03-24 07:57:00. Drei generische Funktionen (JSON laden/speichern), 26 Zeilen.
Liegt heute im `kerne/`-Ordner neben den Organen aus Datei 4, aber knapp einen Monat älter
als der Ordner selbst — später dorthin verschoben, nicht dort entstanden. Erster Import
durch die neuen Organe erst 18./19.04, erster echter Schreibzugriff am 24.04
(`gespraechsverlauf.json`), erste echte Testbefüllung am 11.05.

Erste jemals gespeicherte Laufzeitdaten, wörtlich: `"was wenn der agent träumt?"`
(`erinnerungen.json`) und `"monolith vs microservices"` (`abwaegungen.json`).
