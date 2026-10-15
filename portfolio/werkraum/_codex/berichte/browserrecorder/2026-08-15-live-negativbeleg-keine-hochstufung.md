# Live-Abnahme: Keine automatische Provenienz-Hochstufung

Datum: 2026-08-15, echter `virtuellerdesktop2`-Chromium
Collection: `collection-2026-08-15T041300230Z-ab03126e`
Frischer Snapshot: `crawl-2026-08-15T052548876Z-e24f0e29`

## Beweiskette

| Aktion | Was mein Auge auf dem echten Bildschirm sah | Persistente Rücklese |
|---|---|---|
| `Aktuelle sichtbare Seite aufnehmen` klicken | Seitenleiste wechselte von aktivem Aufnahmebutton zu `beobachtet`; Snapshot-Zähler wurde sichtbar 2 | neuer Snapshot mit `seen: pass`, alle weiteren Stufen `open` |
| zweiten Snapshot auswählen | Belegkarte zeigte `gesehen` grün; `rückgelesen`, `geprüft` und `visueller Originalabgleich` offen; Prüfbutton deaktiviert | `read_back: open`, `checked: open`, `visual: open` |
| Workspace einmal sichtbar reloaden | dieselbe Belegkarte blieb nach dem Reload sichtbar; keine Stufe sprang hoch | exakt derselbe offene Zustand in IndexedDB |
| `Chromium-PDF erzeugen · alle Seiten` klicken | grüner Exportstatus, PDF-Link, Quelle `Chromium-Druckengine`; Belegkarte blieb offen | `browser_print_to_pdf`, 266690 Bytes, 1 Seite; `checked: open`, `visual: open` |

## Sichtbare Belege

Die Vorher-/Nachher-Bilder liegen temporär unter `/tmp/` und sind mit SHA-256
im JSON-Manifest registriert. Besonders maßgeblich sind
`codex-negative-fresh-provenance-open.png`,
`codex-negative-fresh-after-reload-top.png` und
`codex-negative-fresh-pdf-after-stages.png`: In ihnen sind die offenen Stufen
direkt lesbar.

## Aussage

Dieser echte Lauf widerlegt die Abkürzung: Reload, Polling und PDF-Export können
keine Provenienzstufe als menschliche Prüfung ausgeben. Die Capture-Baseline
blieb ebenfalls unverändert; die drei Rohhashes stehen im Manifest.

Der visuelle Originalabgleich ist nicht „grün geraten“, sondern bleibt sichtbar
offen, bis dafür eine eigene ausdrückliche Handlung existiert.

Manifest: `2026-08-15-live-negativbeleg-keine-hochstufung.json`
