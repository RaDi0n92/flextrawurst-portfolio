# Kuratierter Gesamtatlas-Eingang

Dies ist Daniels bewusste Abgabestelle für Material, das für alle angeschlossenen AI-Ströme im Gesamtatlas vollständig auffindbar und durchsuchbar werden soll.

## Verwendung — pro Strom (verbindlich seit 2026-07-31)

**Jeder AI-Strom schreibt ALLES unter `AI_STROEME/<eigener-strom>/<kategorie>/`** — zwölf feste
Kategorien (eigene_texte, auftraege, entscheidungen, uebergaben, gespraeche, arbeitsreste,
konzepte, ideen, notizen, dokumentationen, reviews, beobachtungen), siehe `AI_STROEME/README.md`
für die volle Erklärung. Das ist die verbindliche Antwort auf "wo genau lege ich das ab": kein
Erfinden eines halbwegs plausiblen Ortes mehr, ein Strom + ein Inhaltstyp ergibt genau einen Pfad.

## Verwendung — ohne festen Strombezug

Für Material, das wirklich keinem einzelnen Strom gehört (Daniels eigene Primärquellen, echt
gemeinschaftlich entstandenes Material), bleiben nur noch diese beiden alten Ordner bestehen:

- `00_UNSORTIERT/` – noch nicht eingeordnetes Material
- `QUELLEN/` – Primärquellen und Herkunftsbelege

Die frühere `AI_UEBERGABEN/` (älteres Schema, ohne feste Stromzuordnung) und die
inhaltstyp-basierten `DOKUMENTE/`, `REVIEWS/`, `IDEEN/`, `KONZEPTE/` sind durch die pro-Strom-
Kategorien unter `AI_STROEME/<strom>/` abgelöst — für neues Material bitte dort ablegen, nicht
mehr in diese alten Ordner.

Die Originaldatei bleibt an dieser Stelle erhalten. Der Gesamtatlas verschiebt oder dupliziert sie nicht, sondern indexiert sie bei einem Vollrefresh direkt als Primärquelle.

## Provenienz

Wenn Herkunft, Datum oder Autor wichtig sind, kann neben einer Datei eine gleichnamige Sidecar-Datei liegen:

`beispiel.md` → `beispiel.provenienz.json`

Die Sidecar-Datei ist optional. Fehlende Provenienz wird nicht erfunden.

## Einschraenkung

Eine Ablage hier bedeutet: **für den Atlas bewusst freigegeben und auffindbar**.
Sie bedeutet nicht automatisch: wahr, aktuell, von Daniel bestätigt oder kanonisch integriert.

Eindeutige technische Prüfmarkierung: `GESAMTATLAS_MANUELLER_EINGANG_OMEGA_20260730`.

## Automatische AI-Ankunft

Ein angeschlossener AI-Strom erkennt über seinen dedizierten MCP-Dienst automatisch seine Herkunft. `atlas.arrive` funktioniert ohne Argumente und verbindet den eigenen Strom, liest die beiden Freigabetore und die Einstiegskörper und liefert Atlasstatus, Stromstatus und Puls.

Ein Satz wie **„Der Gesamtatlas ist fertig. Schau ihn an.“** genügt dafür.

Das ist keine Importfreigabe. Importieren, Kopieren, Verschieben, Löschen, Refresh oder die Einordnung unbekannten Materials benötigen weiterhin einen ausdrücklichen Auftrag von Daniel.

## VPS-weites Markdown-Verzeichnis

Der menschenlesbare Wegweiser zu allen beim Vollscan vom 2026-08-14 gefundenen Markdown-Dateien liegt unter:

`QUELLEN/VPS_MARKDOWN_GESAMTVERZEICHNIS/START_HIER.md`

Die Originaldateien bleiben an ihren echten VPS-Pfaden; der Wegweiser verbindet sie nur navigatorisch mit diesem Eingang.

