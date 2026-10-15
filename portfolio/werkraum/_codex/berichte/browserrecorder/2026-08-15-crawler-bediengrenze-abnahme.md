EVIDENCE_VERSION: 1

# Crawler-Abnahme: sichtbarer Tab, ein Klick, ein Snapshot

Datum: 2026-08-15 15:12 +0200
Ort: isoliertes sichtbares Chromium unter `xvfb-run`; kein Anspruch auf den echten `virtuellerdesktop2`-Desktop
Test: `_codex/tools/test_crawl_universal_collection_live.js`

## Aktion

Vor dem Start wurde genau der sichtbare Fixture-Tab auf Scrollposition 300 gebracht und als Vorher-Bild gesichert. Danach wurde genau einmal `#crawlStart` geklickt. Ein bloßer Wechsel auf `/second` wurde anschließend abgewartet und erst danach durch einen zweiten ausdrücklichen Klick aufgenommen.

## Sichtbar

- Vorher-Bild des aktiven Tabs: `/tmp/dak-crawler-before-visible-capture.png` — sichtbarer Lesebereich an Position 300.
- Nachher-Bild des Workspace: `/tmp/dak-crawler-after-visible-capture.png` — `1 Snapshot`, `1 vollständig`, Status `complete`, sichtbare Position `300/1638`.
- Der Workspace zeigt die gespeicherte Snapshot-Projektion; der Link `/second` ist sichtbar als Link, aber nicht automatisch geöffnet.

Die Bilder wurden mit `view_image` tatsächlich angesehen. Der Lauf war ein isolierter sichtbarer Browser, nicht der reale Desktop-Container.

## Rücklese

- Erster Lauf: `source_mode: active_visible_tab`, `pages_count: 1`, `queued_count: 0`, `scan.snapshot: true`, `scan.chunk_count: 1`.
- Die gespeicherte Position ist `top: 300`, `max_top: 1638`; die Oberfläche meldet denselben Wert.
- `max_html_bytes` und `max_asset_bytes` sind positive endliche Werte; die Universalstrecke verwendet keine `0`-Unbegrenzung mehr.
- `owner_offline_export.status: not_requested`; der Fixture-Server sah keinen `.well-known`-Manifestrequest.
- Nach dem reinen Tabwechsel blieb die Collection bei genau einem Eintrag. Erst der zweite sichtbare Start erzeugte Snapshot zwei; die Collection enthielt anschließend genau zwei Seiten.
- Der gespeicherte Text enthält die sichtbaren Inhalte, der Link auf `/second` bleibt als Link erhalten, und es wurde keine Folgeseite aus der Linkliste erzeugt.

## Offen / unbekannt

Der isolierte Lauf beweist die Universal-Visible-Page-Strecke. Die älteren Nicht-Universal-Hilfsfunktionen für Hash-Aktivierung und vollständiges Scrollen (`activateVisibleCrawlRoute`, `captureSettledCrawlChunk`) bleiben als separate Legacy-Schicht im Code und sind in dieser Abnahme nicht als manuell sichere Bedienung freigegeben. Sie dürfen nicht als Beleg für den normalen sichtbaren Tab-Modus gelten.

Ein echter Klick im laufenden `virtuellerdesktop2`-Chromium wurde hier nicht ausgeführt. Die Originalseite ist nicht als pixelgleich bewiesen; bewiesen ist nur der sichtbare Browserzustand dieses Fixtures plus gespeicherte Rücklese.

- REC-GATE-001: PASS — Vertragsgate vor der Änderung und Evidenzgate nach der Abnahme.
- REC-CRAWL-001: PASS — Tabwechsel allein erzeugt nichts; zwei ausdrückliche Klicks erzeugen zwei Snapshots; finite Limits und kein Manifestprobe sind rückgelesen.
- REC-FETCH-001: PASS — sichtbarer Universal-Crawl fordert keinen versteckten Owner-Manifest-Fetch an; Asset-Fetch-Limits und Timeout sind im separaten Fetch-Live-Test bestanden.
- REC-EYE-001: PASS — Vorher-/Nachher-Screenshots, aktive sichtbare URL/Position, DOM-/Workspace-Rücklese und IndexedDB-/Serverstatus stimmen überein.
- REC-DOC-001: PASS — Aktion, Auge, Persistenz und Grenzen sind getrennt dokumentiert.

OUTCOME: PASS
