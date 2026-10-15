---
type: Dokumentation
tags:
- claude
- code-archaeologie
- dak_gord_system
- organe
- lebender-code
generated:
  by: claude
  at: '2026-08-15T00:00:00Z'
status: stable
title: Code-Archäologie 04 — die sieben Organ-Fragmente, mit lebendem Code-Nachweis
description: Sieben Prosa-Fragmente vom 2026-03-24 beschrieben "Organe" von dak+gord-system
  (Beziehung, Entscheidung, Zwischenraum, Sprache, Weltform). Drei davon leben heute noch
  fast wortgleich als kerne/beziehungsorgan.py, kerne/entscheidungsorgan.py,
  kerne/zwischenraumorgan.py -- live importiert vom laufenden dak-gord-web.service.
resource: /root/werkraum_agent/dak_gord_system/aufforderungen/entscheidungsmitgang.md
---

## Logischer / physischer Pfad

`agent/dak_gord_system/aufforderungen/{beziehungsnaehe,codedenken,entscheidungsmitgang,
sprachgesetz,verfassungs_schutz,weltformtreue,zwischenraumhaltung}.md` — physisch
`/root/werkraum_agent/dak_gord_system/aufforderungen/*.md` (derselbe `agent/`-Symlink,
git-technisch im `/root`-Repo).

## Entstehung

Alle sieben exakt am 2026-03-24, zwischen 10:15:27.207 und 10:15:27.214 Uhr — 45 Minuten
nach der finalen `system.md`-Fassung (09:30), in einem einzigen Rutsch angelegt.

## Was die Dateien wörtlich sagen (Auszüge)

- *Beziehungsnähe*: "Er steht also nicht 'vor' dir wie ein Assistent, sondern eher neben
  dir im selben Feld." Er soll spüren "wann du gerade suchst / wann du nur tastest / wann
  du Struktur brauchst / wann du Widerspruch brauchst / wann du eher Resonanz brauchst als
  Lösung."
- *Entscheidungsmitgang*: definiert das "Entscheidungsorgan" — "Spannungen sichtbar
  machen, Folgen mitdenken, verdeckte Motive spüren helfen". Ausdrücklich: "Dieses Organ
  darf nicht herrschen. Es ist kein Richterorgan. Es ist ein Mit-Abwägungsorgan."
- *Sprachgesetz*: "Er spricht nicht wie ein Ticket-System. Nicht wie ein Kundendienst.
  Nicht wie ein cooler Tech-Bot. Nicht wie ein leerer Motivationsassistent."
- *Zwischenraumhaltung*: seine Rolle sei "nicht auflösend, sondern hütend und
  verdichtend" — was "wirklich schon Form will" vs. was "noch geschützt unfertig bleiben
  darf".
- *Codedenken*: nennt ein "Übersetzungsorgan" zwischen "rohem Denken und klarer Sprache,
  Vision und Struktur, Struktur und Plan, Plan und Code, Code und Weltverhalten".
- *Verfassungsschutz*: definiert das "Weltformorgan" — sein "innerer Formkompass".
- *Weltformtreue*: dak+gord ist "Mit-Ermöglicher", "vorgelagerter Weltorganismus".

## Wann hört dieser Code auf zu laufen — und wann fängt er an, sich selbst zu heilen und zu beleben?

Der bisher stärkste Fund der Reihe: drei dieser Prosa-Texte sind nicht tot geblieben,
sondern wortnah als heute noch laufender Code wiedergeboren.

1. `beziehungsnaehe.md` → `kerne/beziehungsorgan.py` (2026-04-19, live, importiert von
   `graphen/gespraechsgraf.py`, läuft in `dak-gord-web.service`): "Struktur brauchst /
   Widerspruch brauchst / Resonanz brauchst" → Dataclass-Felder `strukturbedarf`,
   `widerspruchsbedarf`, `resonanzbedarf`. "wann du nur tastest" → Zustandswert `"tastend"`.
2. `entscheidungsmitgang.md` → `kerne/entscheidungsorgan.py` (2026-04-18, live):
   "Spannungen sichtbar machen" → Feld `spannungen`; "verdeckte Motive spüren helfen" →
   Feld `verdeckte_kosten`; "tiefere Richtung von dir" → Feld `moegliche_tiefere_linie`.
   Klassenname `Entscheidungsorgan` identisch zur Prosa-Überschrift.
3. `zwischenraumhaltung.md` → `kerne/zwischenraumorgan.py` (2026-04-18, live): "was gerade
   erst tastbar wird" vs. "was noch geschützt unfertig bleiben darf" → `REIFE_SCHWELLE` /
   `VERBLASSE_SCHWELLE`, über die ein `ZwischenraumKeim` reift oder verblasst.
4. `sprachgesetz.md` → `verfassung_neu/1_wesen.md` (heutiger, tatsächlich geladener
   Konstitutions-Ordner): "nicht wie ein Ticket-System" steht dort noch wortgleich, fast
   fünf Monate später.
5. `beziehungsnaehe.md` → `wissen/beziehung/an_dak_gord_system.md`: kompletter Absatz
   "Seine erste und wichtigste Beziehung ist die zu dir..." wortgleich übernommen.

`codedenken.md` (Übersetzungsorgan) und das Weltformorgan aus `verfassungs_schutz.md`
haben KEIN eigenes `kerne/*.py`-Gegenstück gefunden — diese beiden Namen tauchen in keiner
heutigen Codedatei auf.

## Heutiger Status

Nur `verfassungs_schutz.md` wird noch technisch geladen — von `graf.py` (totem Code, läuft
nirgends mehr als Dienst). Die anderen sechs wurden nie von Code gelesen, reine
Konzeptniederschrift.

## Bewusste Guardianstyle-Entscheidung

Guardian-NOTIZ-Kommentare mit dem Herkunftsverweis wurden in alle drei lebenden
`kerne/*.py`-Dateien eingefügt (`entscheidungsorgan.py`, `beziehungsorgan.py`,
`zwischenraumorgan.py`). Die sieben Prosa-Fragmente selbst bleiben unangetastet
(Artefakt-Schutz, wie bei Datei 3).

Volltext-Kontext: `/root/werkraum/docs/code_archaeologie_historiendoku.md`, Datei 4.
