# Live-Abnahme: Universalmodus auf beliebiger sichtbarer Web-Seite

Datum: 2026-08-15 10:16 +0200  
Ort: echter `virtuellerdesktop2`-Chromium  
Commit: `be9f7be28`

## Auftrag

Die priorisierten Flextrawurst-Seiten sind nur Test-Fixtures. Der Universalmodus
darf keine gespeicherten URLs oder Profile als Quelle verwenden, sondern muss die
aktuell sichtbare normale Web-Seite aufnehmen.

## Klick- und Gegenprüfkette

| Schritt | Was sichtbar war | Rücklese / Beleg | Status |
|---|---|---|---|
| beliebige Seite öffnen | Chromium zeigte `Example Domain` auf `https://example.com/` | aktive sichtbare Seite war nicht Flextrawurst und nicht die bisherige Fixture | gesehen |
| Extension neu laden | reale Seitenleiste mit Universalmodus | Seitenleisten-Text: `keine gespeicherte URL`, `kein Filter`, `kein Auto-Scroll`, `keine Folgeseiten` | gesehen |
| `Aktuelle sichtbare Seite aufnehmen` klicken | Workspace öffnete sichtbar; `Example Domain · https://example.com/ · sichtbare Position 0/0` | Collection `collection-2026-08-15T081532383Z-a986421e`, ein Snapshot, Status `complete` | gesehen + gelesen |
| Snapshot rücklesen | Workspace zeigte Screenshot und Lesefläche der Example-Domain | IndexedDB-/Runtime-Rücklese: URL `https://example.com/`, `source_mode: active_visible_tab`, `seen: pass`, ein Chunk, `scroll_top: 0`, `scroll_max: 0` | bestanden |
| alte Daten kontrollieren | keine alte Flextrawurst-Seite wurde ersetzt | alte Collection `collection-2026-08-15T041300230Z-ab03126e` blieb bei zwei Flextrawurst-Snapshots | unverändert |

## Gegenprobe gegen gespeicherte Quellen

Der Live-Test übergibt absichtlich `source_mode: configured_url` und eine URL an
den Background-Runtimepfad. Der Universalmodus weist das mit
`Universalmodus braucht den aktuell sichtbaren Tab` zurück. Der Testlauf bleibt
danach mit dem echten aktiven Tab grün.

## Geltungsbereich und Grenze

Der geprüfte Universalpfad gilt für sichtbare `http(s)`-Tabs. `chrome://`,
`file://` und Extension-Seiten sind aus Browser-Sicherheitsgründen keine normalen
Web-Quellen. Die Datei `core/crawl_site_profiles.js` ist eine Test-/Fixturequelle;
der Extension-Lauf verwendet sie nicht als Auswahl- oder Fallbackliste.

Die Aussage ist damit: keine gespeicherte URL begrenzt den Universalmodus; jede
aktuell sichtbare normale Web-URL wird an diesem Pfad als eigene Quelle gelesen.
Nicht behauptet wird, dass jede Website dieselbe Zugänglichkeit oder jedes
geschützte Login-Verhalten besitzt.

## Nachprüfung: sichtbaren Tab wirklich gewechselt

Nach dem `example.com`-Klick wurde im echten Chromium sichtbar auf den bereits
offenen Tab `https://flextrawurst.de/` gewechselt. Vor dem nächsten Klick zeigte
die Seitenleiste noch die vorige Quelle; genau deshalb wurde nicht der sichtbare
Text übernommen, sondern erneut der eine Aufnahmebutton betätigt.

Danach zeigte die Seitenleiste `Quelle: https://flextrawurst.de` und der
Workspace zwei getrennte Snapshots: zuerst `Example Domain`, danach
`Was ist das? — flextrawurst`. Die Runtime-/IndexedDB-Rücklese bestätigte für
beide `source_mode: active_visible_tab`, `trigger: explicit_user_start` und
Status `complete`. Der zweite Snapshot hatte die echte sichtbare Dokumenthöhe
`7000` und `max_top: 6571`; er wurde nicht aus dem ersten Snapshot kopiert.

## Nachprüfung: Quellenanzeige bleibt nicht auf alter URL stehen

Die Aufnahme war korrekt, aber die Quellenanzeige blieb nach dem Tabwechsel bis
zum nächsten Klick auf `example.com` stehen. Sie folgt jetzt dem bestehenden
Tab-Refresh. Das liest nur den aktiven Tab und aktualisiert Status/Preview; es
startet keinen Crawl, legt keinen Snapshot an und schreibt keine Collection.

Nach Extension-Reload zeigte die Anzeige beim sichtbaren Wechsel zwischen
`example.com` und `flextrawurst.de` jeweils die passende Quelle. Die
Provenienzkarte blieb offen; ohne Aufnahme-Klick entstand kein zusätzlicher
Snapshot.

## Nachprüfung: lange beliebige Seite an manueller Scrollposition

Als weiterer unabhängiger Live-Fall wurde `https://www.rfc-editor.org/` sichtbar
geöffnet. Die Seite wurde mit einem menschlichen `Page Down` auf Position
`481/1036` bewegt. Das Vorherbild zeigte den RFC-Editor-Ausschnitt mit den
Bereichen `Learn about RFCs` und `Browse RFCs`.

Danach wurde genau einmal `Aktuelle sichtbare Seite aufnehmen` geklickt. Der
Workspace zeigte `RFC Editor · https://www.rfc-editor.org/ · sichtbare Position
481/1036` und den passenden Screenshot. Die persistente Rücklese bestätigte:
`source_mode: active_visible_tab`, `trigger: explicit_user_start`,
`snapshot: true`, `reached_end: false`, `chunk_count: 1`, `scroll_height: 1585`,
`viewport_height: 549` und `top: 481`. Es wurde also nur der sichtbare Bereich
gesichert; kein Auto-Scroll und kein heimlicher Vollseitenlauf.
