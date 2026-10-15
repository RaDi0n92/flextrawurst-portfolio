EVIDENCE_VERSION: 1

# Download-Abnahme: Abschluss, Bytes und Rücklese

Datum: 2026-08-15 15:02 +0200
Ort: isoliertes sichtbares Chromium unter `xvfb-run`; kein Anspruch auf den echten `virtuellerdesktop2`-Desktop
Test: `_codex/tools/test_recorder_download_completion_live.js`

## Aktion

Webexport-Markdown und direkter Sidepanel-Markdown wurden jeweils genau einmal über die Chrome-Download-API ausgelöst. Der Code wartet auf `complete`, prüft `fileSize`, speichert die Prüfdaten in `chrome.storage.local` und bricht bei Unterbrechung, Timeout oder Größenabweichung ab.

Zusätzlich wurden ein fehlender Export-Identifier, eine encodierte Pfadkennung, ein 1-Sekunden-Remote-Timeout und eine 1-KiB-Antwortgrenze absichtlich geprüft.

## Sichtbar

Die Extension-Seite wurde in einem sichtbaren Chromium-Tab geladen und nach dem Download als Screenshot gelesen: `/tmp/dak-recorder-download-abnahme-sidepanel.png`. Das Bild zeigt die reale Sidepanel-Oberfläche; ein Webexportstatus wird dort nicht künstlich behauptet, weil der Test die Downloadfunktion direkt im Extension-Kontext aufruft.

Die sichtbare Abnahme ist damit der isolierte Browserlauf. Ein nativer Klick im echten `virtuellerdesktop2`-Workspace wurde in diesem Schnitt nicht durchgeführt.

## Rücklese

- Web-Markdown: 48 Bytes, `size_match: true`, real vom Datenträger gelesen, SHA-256 `fd703b46adfb977d20643b9310d57b32c44c3c3d56e80f702da26baa9d6d0f40`.
- Direkter Sidepanel-Markdown: 49 Bytes, `size_match: true`, real vom Datenträger gelesen, SHA-256 `654c6edc9e94ed0634647bfe1b8c2511c9d6752e65b5242934abab87c19fe34e`.
- Beide Quellen-SHA, erwartete Bytezahl, `chrome.downloads`-Dateigröße und Node-Dateirücklese stimmen überein.
- Beide Nachweise stehen zusätzlich in `chrome.storage.local.recorder_download_evidence`.
- Der Remote-Timeout ergab `Remote-Fetch-Timeout nach 1000ms`; die Antwortgrenze ergab `Remote-Antwort überschreitet Limit: 2059 > 1024 Bytes`.
- Fehlende Kennung wurde abgewiesen; `../probe` wurde als `%2Fprobe` encodiert und nicht als unkontrollierter Pfad ausgeführt.

## Offen / unbekannt

Die Extension selbst kann die fertige lokale Datei nicht als Datei-Hash zurücklesen; ihr Status bleibt deshalb ehrlich `hash_readback: not_available_from_extension`. Der isolierte Node-Abnahmetest hat diese Rücklese im Testumfeld übernommen und den SHA verglichen.

Dieser Lauf beweist Markdown-Webexport und den gemeinsamen direkten Downloadpfad. Format-spezifische DOCX-, ODT-, PDF- und JSON-Inhalte wurden hier nicht jeweils als eigene Datei vom Datenträger gelesen. Der native Desktop-Speicherdialog und ein echter `virtuellerdesktop2`-Klick bleiben ebenfalls außerhalb dieses Berichts.

- REC-GATE-001: PASS — `check_recorder_skill_gates.py contracts` und die Download-Evidenzprüfung werden vor Release ausgeführt.
- REC-DOWNLOAD-001: PASS — `complete`, Größenvergleich, `chrome.storage.local`-Evidenz und externe Datei-/SHA-Rücklese für Web- und Sidepanel-Download.
- REC-FETCH-001: PASS — bounded JSON-Fetch mit Abort, Content-Length-/Stream-Limit und explizitem Export-Identifier; Timeout und Größenlimit live ausgelöst.
- REC-SEC-001: PASS — fehlende Kennung abgewiesen und Pfadkennung URL-encodiert; kein SSRF- oder fremder Produktionsendpunkt aus diesem lokalen Fixture behauptet.
- REC-DOC-001: PASS — Aktion, sichtbarer Screenshot, Persistenz-/Dateirücklese und offene Grenzen sind hier getrennt dokumentiert.

OUTCOME: PASS
