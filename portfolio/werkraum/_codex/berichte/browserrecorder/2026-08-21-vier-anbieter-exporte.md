EVIDENCE_VERSION: 1

# Vier Anbieter — Exportformate und Provenienz

## Auftrag und sichtbare Aktion

Auf Desktop 1 wurden die direkten Chrome-Exporter nacheinander in sichtbaren, eingeloggten Chats benutzt. Für ChatGPT, Grok, Claude und Gemini wurden jeweils die sichtbaren Auswahlflächen geöffnet, alle vorhandenen Nachrichten markiert (10/10, 18/18, 192/192, 6/6) und die fünf sichtbaren Formate CSV, JSON, TEXT, MARKDOWN und PDF einzeln ausgelöst. Die UI- und Zustandsbelege liegen unter `/tmp/chatgpt-*`, `/tmp/grok-*`, `/tmp/claude-*` und `/tmp/gemini-*`.

## Rücklese

Alle 20 finalen Dateien liegen unter `/root/werkraum/analysen/provider_exports/2026-08-21/`. Bytezahl und SHA-256 wurden nach dem Speichern aus den finalen Dateien gelesen und sind in `manifest.json` wiederholt. CSV/JSON/TXT/MD wurden zusätzlich strukturell gelesen; JSON ist jeweils ein Objekt mit `metadata` und `messages`, während CSV/TXT/MD Titel- und Exportmetadaten als Projektion führen. PDF ist ein formatierter Render derselben Auswahl.

## Marker

- REC-GATE-001: PASS — `check_recorder_skill_gates.py contracts` war vor dem Lauf grün (`markers: 10`).
- REC-DOWNLOAD-001: PASS — 20 Dateien mit finaler Bytezahl und SHA-256; alle Live-Downloadpfade außer dem als vorbestehend markierten Claude-PDF lieferten ein Playwright-Downloadereignis.
- REC-FETCH-001: PASS — die Dateien wurden durch sichtbare Export-UI-Aktionen erzeugt; die Erweiterungsquellen und der Claude-PDF-URL-Klick sind als Provenienzschichten getrennt notiert.
- REC-SEC-001: PASS — keine Passwörter, 2FA, fremden Uploads oder direkten Anbieter-API-Fetches durch den Agenten; nur eingeloggte sichtbare Chats und die installierten Exporter.
- REC-DOC-001: PASS — Auswahlzahlen, Quell-URLs, Screenshots, finale Pfade, Dateigrößen, Hashes und offene Grenze stehen in diesem Bericht und `manifest.json`.

## Offene Provenienzgrenze

Der Claude-PDF-Lauf zeigte im sichtbaren Dialog „Export erfolgreich!“, aber die Erweiterung setzt den fertigen PDF-Download per erzeugtem Anchor auf eine URL; dieser spezielle Download wurde vom Playwright-Ereignis nicht zurückgeliefert. Deshalb ist der finale Claude-PDF ausdrücklich als vorbestehende Datei aus `/config/Downloads` mit Chrome-History-Beleg gekennzeichnet und nicht als neuer Byte-Claim ausgegeben. Die anderen 19 Dateien sind aktuelle Live-Downloads.

## Erste Analyse der Entstehung

Die vier Exporter verwenden denselben Grundbauplan: erst wird der sichtbare Nachrichtenkorpus in provider-spezifische `messages`-Objekte normalisiert, dann erzeugen lokale Blob-Exporter CSV/JSON/TXT/Markdown. JSON bewahrt die reichste strukturierte Hülle (`metadata` + `messages`); CSV ist eine flache Zeilenprojektion; TXT entfernt Formatierung; Markdown behält Überschriften, Rollen und einfache Formatierung. PDF ist kein Byte-Abzug der Chat-Seite, sondern ein separater, konfigurierter Render-Job mit A4/Portrait/Margins/Fonts/Metadaten. Die Dateigrößen zeigen die Provider- und Korpusunterschiede deutlich: Claude enthält 192 Nachrichten und ein 22-MB-PDF, Gemini nur sechs Nachrichten und ein 173-KB-PDF.

Die JSON-Rücklese macht die Unterschiede für eine spätere Flextrawurst-Replik direkt sichtbar: ChatGPT führt pro Nachricht `role/say/time`, Grok `sender/role/content/say/time`, Claude `role/time/say`, Gemini `id/role/time/checked/contents/text`. Alle vier Metadatenobjekte schreiben außerdem Titel, Datumsgruppe, Link und eine `powered_by`-Kennung des jeweiligen Exporters; Grok und ChatGPT ergänzen ein anonymisiertes `user`-Objekt. Das ist ein starkes Indiz für ein gemeinsames Export-Schema mit provider-spezifischem Adapter davor, nicht für vier pixelgleiche Kopierer.

OUTCOME: PASS
