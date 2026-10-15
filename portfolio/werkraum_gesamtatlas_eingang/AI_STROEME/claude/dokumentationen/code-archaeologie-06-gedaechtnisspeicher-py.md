---
type: Dokumentation
tags:
- claude
- code-archaeologie
- dak_gord_system
- dormanz
- persistenz
generated:
  by: claude
  at: '2026-08-15T00:00:00Z'
status: stable
title: Code-Archäologie 06 — gedaechtnisspeicher.py, eine vierte Selbstheilungs-Kategorie
description: Sechstälteste Datei im System (2026-03-24), aber fast vier Wochen komplett
  ungenutzt, bis vier neue "Organe" sie am 18./19.04. als gemeinsame Persistenzschicht
  entdeckten. Echte frühe Testdaten gefunden, u.a. der erste Testeintrag "was wenn der
  agent träumt?".
resource: /root/werkraum_agent/dak_gord_system/kerne/gedaechtnisspeicher.py
---

## Logischer / physischer Pfad

`agent/dak_gord_system/kerne/gedaechtnisspeicher.py` — physisch
`/root/werkraum_agent/dak_gord_system/kerne/gedaechtnisspeicher.py` (derselbe `agent/`-
Symlink, git-technisch im `/root`-Repo).

## Entstehung

mtime 2026-03-24 07:57:00 — 3,5 Stunden nach `graf.py`, über eine Stunde vor der finalen
`system.md`. Liegt aber schon im Verzeichnis `kerne/`, obwohl die anderen sechs Dateien
dort (siehe Datei 4) erst am 18./19.04. entstanden — ein starkes Indiz für einen späteren
`mv` in den damals neu angelegten Ordner (Verzeichnis-mtime ändert sich bei `mv`, die
Datei-mtime bleibt erhalten).

## Was die Datei tut

26 Zeilen, drei Funktionen: `_pfad()`, `lade_json()`, `speichere_json()` — ein generischer
JSON-Persistenz-Baustein unter `agent/dak_gord_system/gedaechtnis_daten/`. Kennt keine der
Fachlichkeiten, die ihn später nutzen.

## Womit sie zusammenhängt

Importiert ausschließlich von den vier `kerne/*organ.py`-Dateien aus Datei 4
(`entscheidungsorgan.py`, `zwischenraumorgan.py`, `erinnerungsgedaechtnis.py`,
`zukunftsorgan.py`). Kein Aufrufer aus der ersten Code-Generation (`zustand.py`, `graf.py`
hatten keine Persistenz).

## Die Laufzeitdaten — der eigentliche Fund

`gedaechtnis_daten/*.json` (nicht git-getrackt, reine Laufzeitdaten):
- `gespraechsverlauf.json` — erste je geschriebene Datei, 2026-04-24 08:24, Inhalt `[]`.
- `abwaegungen.json`, `erinnerungen.json`, `zukunft.json`, `zwischenraum.json` — alle
  2026-05-11 03:53, mit echtem Testinhalt. Erster `Abwaegung`-Testeintrag wörtlich:
  `"monolith vs microservices"`. Erste `erinnerung`: `"was wenn der agent träumt?"`. Erster
  Zukunfts-Keim: `"heute": "vektorsuche"` → `"spaeter": "chromadb einbauen"`.

## Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu beleben?

Eine vierte Antwortkategorie neben "tot ohne Nachleben" (Datei 1-3), "tot mit Nachleben als
neuer Code" (Datei 4) und "nie gestorben" (Datei 5): **geboren, aber fast einen Monat lang
komplett ungenutzt, dann aktiviert.** Zwischen Entstehung (03-24) und erstem Import
(18./19.04.) kannte kein einziger Code diese Datei. Erst mit den vier neuen Organen wurde
sie zum stillen gemeinsamen Fundament — und selbst dann dauerte es weitere 6 Tage bis zum
ersten echten Schreibzugriff und gut zwei Wochen bis zur ersten echten Testbefüllung.
Geschrieben, bevor jemand wusste, wofür.

## Guardianstyle

NOTIZ-Kommentar mit Herleitung direkt in die Datei ergänzt.

Volltext-Kontext: `/root/werkraum/docs/code_archaeologie_historiendoku.md`, Datei 6.
