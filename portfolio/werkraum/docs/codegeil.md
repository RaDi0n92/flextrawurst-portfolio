# CodeGeil

Nicht chronologisch, nicht ältestes-zuerst wie die Code-Archäologie — CodeGeil sammelt
Fundstellen, während aktiv gebastelt/gebaut wird, egal welches Alter die Datei hat.
Neuestes steht ganz oben. Selbes Format wie Code-Archäologie (Blöcke, getrennt durch
`\n---\n`, Titel = erste Markdown-Überschrift im Block), damit derselbe Parser beide
Dateiformen lesen kann.

Entstanden 2026-08-16, Daniel: "codegeil is einfach beim aktiven basteln wird code
berührt und nicht chronologisch [...] nur nich sortiert aber sammelt ja und macht
doku und wird ich dich injeziert ab start."

Neu angesetzt 2026-08-20, Daniel, 1:1: Einträge sammeln Funde, Entscheidungen und
Kuriositäten, die beim aktiven Bauen sichtbar werden — Design-Entscheidungen, echte
Zusammenhänge zwischen Dateien, überraschende Details, gewachsene Strukturen. Kein
Bug-/Fehlerprotokoll.

---

## tts_service.py — vier Live-Spiegel-Systeme jetzt einheitlich aus einem Admin-Tab heraus rotierbar

`/toolbox`, `/claudelive`, `/codexlive`, `/geminilive` sperren ihren Lesezugriff jeweils
über einen eigenen Query-Schlüssel (`?key=...`), unabhängig vom normalen Login-Passwort.
`claudelive`/`codexlive`/`geminilive` teilen sich dafür `live_crawlkey.py`s `CrawlKey`-
Klasse (Map-Datei + Nginx-Reload in einem Rutsch). `/toolbox` hat seit heute dieselbe
Eigenschaft über eine eigene Helper-Funktion in `tts_service.py`
(`_sync_nginx_crawl_key`), die den literalen Schlüsseltausch in der Nginx-Config macht —
robust gegenüber den vielen Kommentarzeilen dort, wo ein Regex-Ansatz brechen würde.

Neu in `welt/api.py`: `GET/POST /api/livecrawl/{system}/aktuell|rotieren` (die drei
CrawlKey-Systeme) und `/api/toolboxcrawl/aktuell|rotieren` (proxied lokal an Port 8035),
beide admin-JWT-geschützt. Im `flextrawurst.de`-Admin-Tab (SCHLÜSSEL-Sub-Tab, Abschnitt
"LIVE-SPIEGEL-CRAWLSCHLÜSSEL") gibt es dafür ein generisches Popup
(`ftwLivecrawlPopupOeffnen(system, titel)`) statt vier fast identischer Kopien.

---

## tts_ui.html — Toolbox-Tab-Leiste: neun Buttons in einer Zeile statt acht plus einem isolierten

`.crawl-key-btn { margin-left: auto }` schob den "🔑 Crawler-Zugang"-Button in `tts_ui.html`
in `.tabs` (`display:flex; flex-wrap:wrap`) an den rechten Rand seiner eigenen Zeile.
Entfernt, plus horizontales Tab-Padding leicht verringert (`.72rem` → `.58rem`) — bei
1440px passen jetzt alle neun Buttons in eine Zeile, bei 390px bleibt Umbruch bestehen
(neun Buttons passen dort bei keiner sinnvollen Schriftgröße in eine Zeile), aber der
Button sitzt linksbündig statt isoliert am rechten Rand.

---

## welt/api.py — vier neue Endpunkte für die Live-Spiegel-Rotation aus dem Admin-Tab

`GET/POST /api/livecrawl/{system}/aktuell|rotieren` für `claudelive`/`codexlive`/
`geminilive` — greift direkt auf `live_crawlkey.py`s `CrawlKey`-Klasse zu (drei
Instanzen, ein Dict `_LIVECRAWL_SYSTEME`), keine eigene Rotationslogik dupliziert.
`GET/POST /api/toolboxcrawl/aktuell|rotieren` liest die Anzeige-Datei direkt bzw.
proxied lokal an `tts_service.py` (Port 8035), weil `/toolbox` eine eigene, separate
Rotationslogik hat statt der `CrawlKey`-Klasse. Alle vier admin-JWT-geschützt über
`_require_admin(authorization)`, gleiches Muster wie die bestehenden
`/crawlschluessel/*`- und `/archkey/*`-Endpunkte.

---

## build_surface.ts + serve_process_camera_preview.ts — ARCHGATE: echte serverseitige Sperre für CodeGeil/Guardianstyle

Die vier Archäologie-Tabs (Code-Archäologie, CodeGeil, Guardianstyle, Systemweite
Archäologie) waren nur per CSS (`display:none`) versteckt — ein roher `curl`/Fetch
ohne Browser bekam trotzdem den vollen SSR-Text, weil CSS für einen reinen Text-Client
