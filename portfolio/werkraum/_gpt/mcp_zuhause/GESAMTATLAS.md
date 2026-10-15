# Gesamtatlas

Der Gesamtatlas ist die Karte über die Karten. Er ersetzt weder Projektdateien noch Sitzungen, Vaults, Zuhause-Körper, Wurzelbriefe, UI-Gespräche oder technische History.

## Soforteinstiege

- Gesamtkarte: `/root/werkraum/_gpt/gesamtatlas/GESAMTKARTE.md`
- Status und globale Revision: `/root/werkraum/_gpt/gesamtatlas/ATLAS_STATUS.json`
- Pfad-/Metadatenindex: `/root/werkraum/_gpt/gesamtatlas/PFADINDEX.sqlite`
- Volltext-/Begriffsindex: `/root/werkraum/_gpt/gesamtatlas/BEGRIFFSINDEX.sqlite`
- Beziehungsgraph: `/root/werkraum/_gpt/gesamtatlas/BEZIEHUNGSREGISTER.sqlite`
- Projektrevisionen: `/root/werkraum/_gpt/gesamtatlas/PROJEKTREVISIONEN.json`
- Claims: `/root/werkraum/_gpt/gesamtatlas/CLAIMREGISTER.json`
- Validierungsartefakte: `/root/werkraum/_gpt/gesamtatlas/VALIDIERUNGSREGISTER.json`
- Sessionübergaben: `/root/werkraum/_gpt/gesamtatlas/UEBERGABEREGISTER.json`
- AI-Strom-Brücken: `/root/werkraum/_gpt/gesamtatlas/AI_STROM_BRUECKEN.json`
- Eingebungsprovenienz: `/root/werkraum/_gpt/gesamtatlas/EINGEBUNGSPROVENIENZ.jsonl`
- Konsens und Konflikte: `KONSENSREGISTER.jsonl` und `KONFLIKTREGISTER.jsonl`

## Kontext-Lease und Puls

Jede Session besitzt einen eigenen Lease-Lesestand. Er merkt nicht nur History-Offsets, sondern auch:

- Atlasrevision,
- Projektrevisionen,
- bekannte Sessionübergaben und abgeschlossene Sessions,
- offene Konflikte,
- AI-Strom-Revisionen,
- das aktuelle Projekt.

`atlas.pulse` kann vier Stufen liefern:

- `whisper`: wenige wichtigste fremde Änderungen,
- `project`: nur der aktuelle Projektkörper,
- `stream`: zusätzlich AI-Strom-Deltas,
- `full`: vollständiger Lease-Abgleich innerhalb der Ausgabelimits.

Der Puls wird beim Sessionstart und nach normalen MCP-Aufrufen gebunden. Zwei parallele Pulse derselben Sitzung dürfen dasselbe Delta nicht doppelt zustellen.

## Projektrevisionen

Projekt- und Komponentenknoten besitzen eigene Revisionen. Eine protokollierte Mutation erhöht die passende Projektrevision sofort. Der nächste Vollscan bindet den realen Dateifingerprint, ohne dasselbe Ereignis noch einmal hochzuzählen.

Die Karte unterscheidet:

- kanonische Projekte,
- Projektkomponenten,
- Systemkomponenten,
- Operationsbereiche,
- Strukturansichten,
- Speicher-/Archivbereiche,
- Backups,
- Containerwurzeln.

Nur kanonische Projekte und echte Komponenten dürfen automatisch als AI-Strom-Projektbezug erscheinen.

## Sessionübergaben

Jede technisch abgeschlossene Session erhält einen standardisierten JSON- und Markdown-Körper unter:

`/root/werkraum/_gpt/gesamtatlas/uebergaben/`

Er enthält Abschluss, Mutationen, Prüfungen, zugeordnete Projekte, Blocker, Quellereignisse und Endhash. Er ist eine Ableitung aus der append-only Action-History und ersetzt keinen vollständigen UI-Gesprächsexport.

## Beziehungsgraph

Der Graph verbindet Projekte, Komponenten, Sessions, Claims, Dienste, Vaults, Validierungsartefakte, Übergaben, Konsens, Konflikte und AI-Ströme. Jede Kante trägt eine Herkunftsklasse. Erlaubt sind nur belegte Pfad-, Struktur-, Deklarations-, History- oder exakte Volltexterwähnungen. Semantische Nähe allein erzeugt keine Kante.

Vollständige Validierungsartefakte bleiben im Validierungsregister. Die normale Projektkarte führt davon nur zusammenfassende Berichte und Maschinenergebnisse als `validation_reports`.

## AI-Ströme und Wurzelbriefe

ChatGPT, Claude, Codex, Kimi, Gemini, GLM und der begrenzte Grok-Dateinamenstatus behalten getrennte Herkunft. Die Brücken zeigen belegte Projektbezüge und Stromrevisionen, verschmelzen aber keine Erinnerungen.

Dateiname, erklärte Autorschaft und adressierter Strom bleiben getrennt. `/root/CLAUDE.md` wird nicht allein wegen seines Namens Claude zugerechnet, wenn sein Inhalt GLM-Herkunft erklärt. `/root/grok.md` erzeugt kein erfundenes Grok-Haus, wenn sein Inhalt GLM adressiert.

## Eingebungsprovenienz

Vor der Darstellung einer neuen übergreifenden Idee soll `atlas.idea_marker` aufgerufen werden. Die Klasse

`CROSS_SESSION_EINGEBUNG_MIT_NACHGELAGERTER_LOKALER_FREIGABE`

hält fest, dass ein Gedanke als Cross-Session-Einfluss in eine Sitzung gelangte und erst danach dort ausdrücklich freigegeben wurde. Explizite Quellen haben Vorrang vor bloßen Ähnlichkeitstreffern.

## Konsensgrenze

Wiederholung, semantische Nähe oder mehrere gleichlautende Sessions sind kein automatischer Konsens. Daniels explizite Setzungen, technische Validierung, Arbeitshypothesen, Vorschläge, Widersprüche und veraltete Stände bleiben getrennte Klassen.
